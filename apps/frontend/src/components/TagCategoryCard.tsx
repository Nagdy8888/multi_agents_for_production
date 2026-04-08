"use client";

import { Card, CardContent, CardHeader } from "@/components/ui/card";
import type { PartialTagResult } from "@/lib/types";
import { cn } from "@/lib/utils";

/** Color for left border by category (reference: color-coded per category). */
const CATEGORY_BORDER_COLORS: Record<string, string> = {
  season: "border-l-amber-500",
  theme: "border-l-violet-500",
  objects: "border-l-emerald-500",
  dominant_colors: "border-l-rose-500",
  design_elements: "border-l-sky-500",
  occasion: "border-l-orange-500",
  mood: "border-l-pink-500",
  product_type: "border-l-cyan-500",
};

function formatTagLabel(value: string): string {
  return value
    .split("_")
    .map((w) => w.charAt(0).toUpperCase() + w.slice(1).toLowerCase())
    .join(" ");
}

/** Chip style by confidence: green (high), yellow/orange (medium). */
function chipClass(confidence: number): string {
  if (confidence >= 0.85) return "bg-emerald-500/25 text-emerald-100 border-emerald-500/50";
  if (confidence >= 0.55) return "bg-amber-500/25 text-amber-100 border-amber-500/50";
  return "bg-muted text-muted-foreground border-border";
}

interface TagCategoryCardProps {
  result: PartialTagResult;
  className?: string;
}

export function TagCategoryCard({ result, className }: TagCategoryCardProps) {
  const { category, tags, confidence_scores } = result;
  const borderClass =
    CATEGORY_BORDER_COLORS[category] ?? "border-l-muted-foreground/50";
  const title =
    category === "dominant_colors"
      ? "Colors"
      : category === "design_elements"
        ? "Design"
        : formatTagLabel(category);

  return (
    <Card
      className={cn(
        "border-l-4 rounded-lg border border-border/60 bg-card/80",
        borderClass,
        className
      )}
    >
      <CardHeader className="pb-1.5 pt-3 px-4">
        <h3 className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">
          {title}
        </h3>
      </CardHeader>
      <CardContent className="pt-0 px-4 pb-3">
        {tags.length === 0 ? (
          <p className="text-sm text-muted-foreground">No tags</p>
        ) : (
          <ul className="flex flex-wrap gap-2">
            {tags.map((tag) => {
              const conf = confidence_scores[tag] ?? 0;
              const pct = Math.round(conf * 100);
              return (
                <li
                  key={tag}
                  className={cn(
                    "inline-flex items-center rounded-md border px-2 py-1 text-xs font-medium",
                    chipClass(conf)
                  )}
                >
                  {formatTagLabel(tag)} {pct}%
                </li>
              );
            })}
          </ul>
        )}
      </CardContent>
    </Card>
  );
}
