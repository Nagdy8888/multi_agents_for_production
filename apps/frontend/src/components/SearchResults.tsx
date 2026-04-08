"use client";

import Image from "next/image";
import { Search } from "lucide-react";
import { Skeleton } from "@/components/ui/skeleton";
import { formatTagLabel } from "@/lib/formatTag";
import type { TagImageRow } from "@/lib/types";
import { cn } from "@/lib/utils";

interface SearchResultsProps {
  items: TagImageRow[];
  loading?: boolean;
  onSelectItem: (row: TagImageRow) => void;
}

function getSeasonTags(record: Record<string, unknown>): string[] {
  const v = record.season;
  return Array.isArray(v) ? v.filter((x): x is string => typeof x === "string").slice(0, 3) : [];
}

function getThemeTags(record: Record<string, unknown>): string[] {
  const v = record.theme;
  return Array.isArray(v) ? v.filter((x): x is string => typeof x === "string").slice(0, 3) : [];
}

export function SearchResults({ items, loading, onSelectItem }: SearchResultsProps) {
  if (loading) {
    return (
      <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5">
        {[1, 2, 3, 4, 5, 6].map((i) => (
          <Skeleton key={i} className="aspect-square rounded-lg" />
        ))}
      </div>
    );
  }

  if (items.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center rounded-lg border border-dashed border-border/60 bg-muted/20 py-16 text-center">
        <Search className="h-12 w-12 text-muted-foreground/50" />
        <h3 className="mt-4 text-sm font-medium text-foreground">No results found</h3>
        <p className="mt-1 text-sm text-muted-foreground">Try adjusting your filters or add more tagged images.</p>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5">
      {items.map((row) => {
        const record = (row.tag_record ?? {}) as Record<string, unknown>;
        const season = getSeasonTags(record);
        const theme = getThemeTags(record);
        return (
          <button
            key={row.image_id}
            type="button"
            className={cn(
              "group flex flex-col overflow-hidden rounded-lg border border-border/60 bg-card/80 text-left transition hover:border-border hover:shadow-md"
            )}
            onClick={() => onSelectItem(row)}
          >
            <div className="relative aspect-square w-full overflow-hidden bg-muted/30">
              {row.image_url ? (
                <Image
                  src={row.image_url}
                  alt=""
                  fill
                  className="object-cover transition group-hover:scale-105"
                  sizes="(max-width: 640px) 50vw, 20vw"
                  unoptimized
                />
              ) : (
                <div className="flex h-full items-center justify-center text-xs text-muted-foreground">No preview</div>
              )}
            </div>
            <div className="flex flex-wrap gap-1 p-2">
              {season.map((s) => (
                <span key={s} className="rounded bg-amber-500/20 px-1.5 py-0.5 text-[10px] text-amber-200">
                  {formatTagLabel(s)}
                </span>
              ))}
              {theme.map((t) => (
                <span key={t} className="rounded bg-violet-500/20 px-1.5 py-0.5 text-[10px] text-violet-200">
                  {formatTagLabel(t)}
                </span>
              ))}
            </div>
            <div className="px-2 pb-2">
              <span
                className={cn(
                  "inline-block rounded px-1.5 py-0.5 text-[10px] font-medium",
                  row.processing_status === "complete" ? "bg-emerald-500/20 text-emerald-400" : "bg-amber-500/20 text-amber-400"
                )}
              >
                {row.processing_status}
              </span>
            </div>
          </button>
        );
      })}
    </div>
  );
}
