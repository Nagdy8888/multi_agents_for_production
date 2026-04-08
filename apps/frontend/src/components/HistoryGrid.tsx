"use client";

import { useState, useEffect, useCallback } from "react";
import Image from "next/image";
import { ImageIcon, RefreshCw } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { API_BASE_URL } from "@/lib/constants";
import type { TagImagesListResponse, TagImageRow } from "@/lib/types";

const LIMIT = 20;

function sampleTags(row: TagImageRow): string[] {
  const record = row.tag_record as Record<string, unknown>;
  const out: string[] = [];
  for (const key of ["season", "theme", "occasion", "mood"]) {
    const val = record[key];
    if (Array.isArray(val) && val.length > 0) {
      const first = val[0];
      if (typeof first === "string") out.push(first);
      else if (first && typeof first === "object" && "child" in first) out.push((first as { child: string }).child);
    }
  }
  return out.slice(0, 4);
}

function formatDate(iso: string): string {
  try {
    const d = new Date(iso);
    return d.toLocaleDateString(undefined, { month: "short", day: "numeric", year: "numeric" });
  } catch {
    return "";
  }
}

export function HistoryGrid() {
  const [data, setData] = useState<TagImagesListResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchList = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${API_BASE_URL}/api/tag-images?limit=${LIMIT}&offset=0`);
      if (!res.ok) {
        if (res.status === 503) {
          setData({ items: [], limit: LIMIT, offset: 0 });
          return;
        }
        throw new Error(res.statusText);
      }
      const json: TagImagesListResponse = await res.json();
      setData(json);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load");
      setData(null);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchList();
  }, [fetchList]);

  if (loading && !data) {
    return (
      <section className="mt-10">
        <h2 className="mb-3 text-sm font-semibold uppercase tracking-wide text-muted-foreground">
          Recently Tagged Images
        </h2>
        <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 md:grid-cols-4">
          {[1, 2, 3, 4].map((i) => (
            <Skeleton key={i} className="aspect-square rounded-lg" />
          ))}
        </div>
      </section>
    );
  }

  const items = data?.items ?? [];
  const dbUnavailable = data && items.length === 0 && !error;

  return (
    <section className="mt-10">
      <div className="mb-3 flex items-center justify-between">
        <h2 className="text-sm font-semibold uppercase tracking-wide text-muted-foreground">
          Recently Tagged Images
        </h2>
        {!dbUnavailable && (
          <Button variant="ghost" size="sm" onClick={fetchList} disabled={loading}>
            <RefreshCw className={`mr-1 h-4 w-4 ${loading ? "animate-spin" : ""}`} />
            Refresh
          </Button>
        )}
      </div>
      {error && (
        <p className="text-sm text-muted-foreground">
          {error}
        </p>
      )}
      {dbUnavailable && (
        <p className="text-sm text-muted-foreground">
          Database not configured. Tag history will appear here when enabled.
        </p>
      )}
      {!error && !dbUnavailable && items.length === 0 && (
        <div className="flex flex-col items-center justify-center rounded-lg border border-dashed border-border/60 bg-muted/20 py-12 text-center">
          <ImageIcon className="h-10 w-10 text-muted-foreground/60" aria-hidden />
          <p className="mt-2 text-sm font-medium text-foreground">No tagged images yet</p>
          <p className="mt-1 text-xs text-muted-foreground">Analyze an image to see it here.</p>
        </div>
      )}
      {!error && items.length > 0 && (
        <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 md:grid-cols-4">
          {items.map((row) => (
            <a
              key={row.image_id}
              href={row.image_url || "#"}
              target="_blank"
              rel="noopener noreferrer"
              className="group rounded-lg border border-border/60 bg-card/80 p-2 transition hover:border-border"
            >
              <div className="relative aspect-square w-full overflow-hidden rounded-md bg-muted/30">
                {row.image_url ? (
                  <Image
                    src={row.image_url}
                    alt=""
                    fill
                    className="object-cover transition group-hover:scale-105"
                    sizes="(max-width: 640px) 50vw, 25vw"
                    unoptimized
                  />
                ) : (
                  <div className="flex h-full items-center justify-center text-xs text-muted-foreground">
                    No preview
                  </div>
                )}
              </div>
              <p className="mt-2 truncate text-xs text-muted-foreground" title={row.image_id}>
                {row.image_id.slice(0, 8)}…
              </p>
              <div className="mt-1 flex flex-wrap gap-1">
                <span
                  className={`rounded px-1.5 py-0.5 text-[10px] font-medium ${
                    row.processing_status === "complete"
                      ? "bg-emerald-500/20 text-emerald-400"
                      : "bg-amber-500/20 text-amber-400"
                  }`}
                >
                  {row.processing_status}
                </span>
              </div>
              <div className="mt-1 flex flex-wrap gap-1">
                {sampleTags(row).map((t) => (
                  <span
                    key={t}
                    className="truncate rounded bg-muted/60 px-1 py-0.5 text-[10px] text-foreground"
                    title={t}
                  >
                    {t}
                  </span>
                ))}
              </div>
              <p className="mt-1 text-[10px] text-muted-foreground">{formatDate(row.updated_at || row.created_at)}</p>
            </a>
          ))}
        </div>
      )}
    </section>
  );
}
