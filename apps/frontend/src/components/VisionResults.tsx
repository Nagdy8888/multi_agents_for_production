"use client";

import { motion } from "framer-motion";
import Image from "next/image";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { TagCategoryCard } from "@/components/TagCategoryCard";
import type { AnalyzeImageResponse } from "@/lib/types";

interface VisionResultsProps {
  data: AnalyzeImageResponse;
}

export function VisionResults({ data }: VisionResultsProps) {
  const { image_url, vision_description, vision_raw_tags, partial_tags } = data;
  const tags = vision_raw_tags || {};
  const pipelineTags = partial_tags ?? [];

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className="grid w-full gap-6 md:grid-cols-2"
    >
      <div className="relative aspect-square max-h-[400px] w-full overflow-hidden rounded-lg border bg-muted shadow-md">
        <Image
          src={image_url}
          alt="Uploaded"
          fill
          className="object-contain"
          unoptimized
          sizes="400px"
        />
      </div>

      <Card>
        <CardHeader>
          <h2 className="text-xl font-semibold">AI Analysis</h2>
        </CardHeader>
        <CardContent className="space-y-4">
          {vision_description && (
            <div>
              <p className="text-sm text-muted-foreground">Description</p>
              <p className="mt-1 text-foreground">{vision_description}</p>
            </div>
          )}

          {tags.dominant_mood != null && String(tags.dominant_mood) !== "" ? (
            <div>
              <p className="text-sm text-muted-foreground">Dominant mood</p>
              <p className="mt-1 text-foreground">{String(tags.dominant_mood)}</p>
            </div>
          ) : null}

          {Array.isArray(tags.visible_subjects) && tags.visible_subjects.length > 0 ? (
            <div>
              <p className="text-sm text-muted-foreground">Visible subjects</p>
              <div className="mt-2 flex flex-wrap gap-2">
                {(tags.visible_subjects as string[]).map((s) => (
                  <Badge key={s} variant="secondary">
                    {s}
                  </Badge>
                ))}
              </div>
            </div>
          ) : null}

          {tags.color_observations != null && String(tags.color_observations) !== "" ? (
            <div>
              <p className="text-sm text-muted-foreground">Color observations</p>
              <p className="mt-1 text-foreground">{String(tags.color_observations)}</p>
            </div>
          ) : null}

          {tags.design_observations != null && String(tags.design_observations) !== "" ? (
            <div>
              <p className="text-sm text-muted-foreground">Design observations</p>
              <p className="mt-1 text-foreground">{String(tags.design_observations)}</p>
            </div>
          ) : null}

          {tags.seasonal_indicators != null && String(tags.seasonal_indicators) !== "" ? (
            <div>
              <p className="text-sm text-muted-foreground">Seasonal indicators</p>
              <p className="mt-1 text-foreground">{String(tags.seasonal_indicators)}</p>
            </div>
          ) : null}

          {tags.style_indicators != null && String(tags.style_indicators) !== "" ? (
            <div>
              <p className="text-sm text-muted-foreground">Style indicators</p>
              <p className="mt-1 text-foreground">{String(tags.style_indicators)}</p>
            </div>
          ) : null}

          {tags.text_present !== undefined && tags.text_present !== null ? (
            <div>
              <p className="text-sm text-muted-foreground">Text present</p>
              <p className="mt-1 text-foreground">{String(tags.text_present)}</p>
            </div>
          ) : null}
        </CardContent>
      </Card>

      {pipelineTags.length > 0 && !data.tags_by_category && (
        <div className="space-y-4 md:col-span-2">
          <h2 className="text-lg font-semibold">Pipeline tags</h2>
          <div className="grid gap-4 sm:grid-cols-2">
            {pipelineTags.map((result) => (
              <TagCategoryCard key={result.category} result={result} />
            ))}
          </div>
        </div>
      )}
    </motion.div>
  );
}
