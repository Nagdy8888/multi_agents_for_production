"use client";

import { useEffect } from "react";
import Image from "next/image";
import { X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { TagCategories } from "@/components/TagCategories";
import { FlaggedTags } from "@/components/FlaggedTags";
import type { TagImageRow, TagRecord } from "@/lib/types";
import { cn } from "@/lib/utils";

interface DetailModalProps {
  row: TagImageRow | null;
  onClose: () => void;
}

/** Convert tag_record to tags_by_category for TagCategories. */
function tagRecordToTagsByCategory(record: TagRecord | Record<string, unknown>): Record<string, { value: string; confidence: number }[]> {
  const out: Record<string, { value: string; confidence: number }[]> = {};
  const r = record as Record<string, unknown>;
  for (const key of ["season", "theme", "design_elements", "occasion", "mood"]) {
    const val = r[key];
    if (Array.isArray(val)) {
      out[key] = val.filter((v): v is string => typeof v === "string").map((v) => ({ value: v, confidence: 1 }));
    }
  }
  for (const key of ["objects", "dominant_colors"] as const) {
    const val = r[key];
    if (Array.isArray(val)) {
      out[key] = val
        .filter((v): v is { parent?: string; child?: string } => typeof v === "object" && v !== null)
        .map((v) => ({ value: v.child ?? v.parent ?? "", confidence: 1 }));
    }
  }
  const pt = r.product_type;
  if (pt && typeof pt === "object" && "child" in pt) {
    out.product_type = [{ value: (pt as { child: string }).child, confidence: 1 }];
  }
  return out;
}

function formatDate(iso: string): string {
  try {
    return new Date(iso).toLocaleString(undefined, { dateStyle: "medium", timeStyle: "short" });
  } catch {
    return iso;
  }
}

export function DetailModal({ row, onClose }: DetailModalProps) {
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [onClose]);

  if (!row) return null;

  const tagsByCategory = tagRecordToTagsByCategory(row.tag_record ?? {});
  const flagged = Array.isArray((row.tag_record as Record<string, unknown>)?.flagged_tags)
    ? ((row.tag_record as Record<string, unknown>).flagged_tags as unknown[])
    : [];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div className="absolute inset-0 bg-black/70" aria-hidden onClick={onClose} />
      <div
        className="relative z-10 flex max-h-[90vh] w-full max-w-4xl flex-col overflow-hidden rounded-lg border border-border bg-card shadow-xl"
        role="dialog"
        aria-modal="true"
        aria-labelledby="detail-modal-title"
      >
        <div className="flex items-center justify-between border-b border-border/60 p-4">
          <h2 id="detail-modal-title" className="text-lg font-semibold">
            Image details
          </h2>
          <Button variant="ghost" size="icon" onClick={onClose} aria-label="Close">
            <X className="h-5 w-5" />
          </Button>
        </div>
        <div className="flex-1 overflow-y-auto p-4">
          <div className="grid gap-6 md:grid-cols-2">
            <div className="relative aspect-square w-full overflow-hidden rounded-lg border border-border/60 bg-muted/30">
              {row.image_url ? (
                <Image
                  src={row.image_url}
                  alt="Full size"
                  fill
                  className="object-contain"
                  unoptimized
                  sizes="50vw"
                />
              ) : (
                <div className="flex h-full items-center justify-center text-muted-foreground">No image</div>
              )}
            </div>
            <div className="space-y-4">
              <div>
                <p className="text-xs text-muted-foreground">Image ID</p>
                <p className="font-mono text-sm">{row.image_id}</p>
              </div>
              <div>
                <p className="text-xs text-muted-foreground">Status</p>
                <span
                  className={cn(
                    "inline-block rounded px-2 py-0.5 text-xs font-medium",
                    row.processing_status === "complete" ? "bg-emerald-500/20 text-emerald-400" : "bg-amber-500/20 text-amber-400"
                  )}
                >
                  {row.processing_status}
                </span>
              </div>
              {(row.updated_at || row.created_at) && (
                <div>
                  <p className="text-xs text-muted-foreground">Processed</p>
                  <p className="text-sm">{formatDate(row.updated_at || row.created_at)}</p>
                </div>
              )}
              <TagCategories tagsByCategory={tagsByCategory} showTitle={true} />
              {flagged.length > 0 && (
                <FlaggedTags flagged={flagged as { category: string; value: string; confidence: number; reason: string }[]} />
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
