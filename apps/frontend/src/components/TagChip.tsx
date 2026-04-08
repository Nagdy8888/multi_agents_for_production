"use client";

import { cn } from "@/lib/utils";
import type { TagWithConfidence } from "@/lib/types";

function formatTagLabel(value: string): string {
  return value
    .split("_")
    .map((w) => w.charAt(0).toUpperCase() + w.slice(1).toLowerCase())
    .join(" ");
}

/** Confidence-based background: green (>=0.85), blue (0.7-0.85), yellow (0.55-0.7), red (<0.55). */
function confidenceClass(confidence: number): string {
  if (confidence >= 0.85) return "bg-emerald-500/20 text-emerald-800 dark:text-emerald-200 border-emerald-500/40";
  if (confidence >= 0.7) return "bg-blue-500/20 text-blue-800 dark:text-blue-200 border-blue-500/40";
  if (confidence >= 0.55) return "bg-amber-500/20 text-amber-800 dark:text-amber-200 border-amber-500/40";
  return "bg-red-500/20 text-red-800 dark:text-red-200 border-red-500/40";
}

interface TagChipProps {
  tag: TagWithConfidence;
  className?: string;
}

export function TagChip({ tag, className }: TagChipProps) {
  const pct = Math.round(tag.confidence * 100);
  return (
    <span
      title={`Confidence: ${pct}%`}
      className={cn(
        "inline-flex items-center rounded-md border px-2 py-0.5 text-xs font-medium",
        confidenceClass(tag.confidence),
        className
      )}
    >
      {formatTagLabel(tag.value)}
    </span>
  );
}
