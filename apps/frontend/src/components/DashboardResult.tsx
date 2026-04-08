"use client";

import { useMemo } from "react";
import Image from "next/image";
import { motion } from "framer-motion";
import { MoreHorizontal } from "lucide-react";
import { Button } from "@/components/ui/button";
import { TagCategories } from "@/components/TagCategories";
import { FlaggedTags } from "@/components/FlaggedTags";
import { JsonViewer } from "@/components/JsonViewer";
import { ConfidenceRing } from "@/components/ConfidenceRing";
import type { AnalyzeImageResponse } from "@/lib/types";

interface DashboardResultProps {
  data: AnalyzeImageResponse;
  onReplaceImage: () => void;
}

export function DashboardResult({ data, onReplaceImage }: DashboardResultProps) {
  const tagsByCategory = data.tags_by_category ?? {};
  const vision = data.vision_raw_tags ?? {};
  const flagged = data.flagged_tags ?? [];

  const overallConfidence = useMemo(() => {
    let sum = 0;
    let n = 0;
    Object.values(tagsByCategory).forEach((list) => {
      list.forEach((t) => {
        sum += t.confidence;
        n += 1;
      });
    });
    return n > 0 ? sum / n : 0;
  }, [tagsByCategory]);

  const dominantMood =
    vision.dominant_mood != null && String(vision.dominant_mood) !== ""
      ? String(vision.dominant_mood)
      : null;
  const visibleSubjects = Array.isArray(vision.visible_subjects)
    ? (vision.visible_subjects as string[])
    : [];
  const colorObs =
    vision.color_observations != null && String(vision.color_observations) !== ""
      ? String(vision.color_observations)
      : null;
  const seasonal =
    vision.seasonal_indicators != null && String(vision.seasonal_indicators) !== ""
      ? String(vision.seasonal_indicators)
      : null;
  const style =
    vision.style_indicators != null && String(vision.style_indicators) !== ""
      ? String(vision.style_indicators)
      : null;

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className="flex w-full flex-col gap-6"
    >
      {/* Row 1: Product Image card | AI Analysis card side by side */}
      <div className="grid w-full grid-cols-1 gap-6 md:grid-cols-2">
        <section className="rounded-lg border border-border/60 bg-card/80 p-4">
          <div className="mb-3 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <h2 className="text-sm font-semibold uppercase tracking-wide text-muted-foreground">
                Product Image
              </h2>
              {data.saved_to_db && (
                <span className="rounded-full bg-emerald-500/20 px-2 py-0.5 text-xs font-medium text-emerald-400">
                  Saved
                </span>
              )}
            </div>
            <div className="flex items-center gap-1">
              <Button
                variant="ghost"
                size="sm"
                className="text-muted-foreground hover:text-foreground"
                onClick={onReplaceImage}
              >
                Replace Image
              </Button>
              <Button variant="ghost" size="icon" className="h-8 w-8 text-muted-foreground">
                <MoreHorizontal className="h-4 w-4" />
              </Button>
            </div>
          </div>
          <div className="relative aspect-square w-full overflow-hidden rounded-lg border border-border/60 bg-muted/30">
            <Image
              src={data.image_url}
              alt="Product"
              fill
              className="object-contain"
              unoptimized
              sizes="(max-width: 768px) 100vw, 50vw"
            />
          </div>
        </section>

        <section className="rounded-lg border border-border/60 bg-card/80 p-5">
          <h2 className="mb-4 text-lg font-semibold">AI Analysis</h2>

          {data.vision_description && (
            <div className="mb-4">
              <h3 className="mb-1.5 text-xs font-semibold uppercase tracking-wide text-muted-foreground">
                Vision Analysis
              </h3>
              <p className="text-sm leading-relaxed text-foreground">
                {data.vision_description}
              </p>
            </div>
          )}

          <div className="space-y-3 text-sm">
            {dominantMood && (
              <div>
                <span className="text-muted-foreground">Dominant Mood: </span>
                <span className="text-foreground">{dominantMood}</span>
              </div>
            )}
            {visibleSubjects.length > 0 && (
              <div>
                <span className="text-muted-foreground">Visible Subjects: </span>
                <span className="text-foreground">{visibleSubjects.join(", ")}</span>
              </div>
            )}
            {colorObs && (
              <div>
                <span className="text-muted-foreground">Colors: </span>
                <span className="text-foreground">{colorObs}</span>
              </div>
            )}
            {seasonal && (
              <div>
                <span className="text-muted-foreground">Seasonal: </span>
                <span className="text-foreground">{seasonal}</span>
              </div>
            )}
            {style && (
              <div>
                <span className="text-muted-foreground">Style: </span>
                <span className="text-foreground">{style}</span>
              </div>
            )}
          </div>

          <div className="mt-6 flex justify-center">
            <ConfidenceRing
              confidence={overallConfidence}
              size={120}
              strokeWidth={8}
              showValue
              className="text-emerald-500"
            />
          </div>
        </section>
      </div>

      {/* Row 2: Tags, Flagged, Raw JSON full width */}
      <section>
        <h2 className="mb-3 text-sm font-semibold uppercase tracking-wide text-muted-foreground">
          Tags by Category
        </h2>
        {Object.keys(tagsByCategory).length > 0 ? (
          <TagCategories tagsByCategory={tagsByCategory} showTitle={false} />
        ) : (
          <p className="text-sm text-muted-foreground">No tags yet.</p>
        )}
      </section>

      <section className="rounded-lg border border-border/60 bg-card/80 p-4">
        <FlaggedTags flagged={flagged} />
      </section>

      <JsonViewer data={data.tag_record ?? data.vision_raw_tags} />
    </motion.div>
  );
}
