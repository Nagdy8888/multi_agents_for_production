"use client";

import { useState } from "react";
import { ChevronDown, ChevronRight, AlertTriangle } from "lucide-react";
import type { FlaggedTag as FlaggedTagType } from "@/lib/types";

function formatLabel(s: string): string {
  return s
    .split("_")
    .map((w) => w.charAt(0).toUpperCase() + w.slice(1).toLowerCase())
    .join(" ");
}

interface FlaggedTagsProps {
  flagged: FlaggedTagType[];
  className?: string;
}

export function FlaggedTags({ flagged, className }: FlaggedTagsProps) {
  const [open, setOpen] = useState(true);

  const label =
    flagged.length === 0
      ? "None"
      : flagged.length === 1
        ? "1 low-confidence tag"
        : `${flagged.length} low-confidence tags`;

  return (
    <div className={className}>
      <h2 className="mb-3 text-sm font-semibold uppercase tracking-wide text-muted-foreground">
        Flagged Tags
      </h2>
      {flagged.length === 0 ? (
        <p className="text-sm text-muted-foreground">No flagged tags. All tags passed confidence.</p>
      ) : (
        <div className="rounded-lg border border-amber-500/50 bg-amber-500/10">
          <button
            type="button"
            onClick={() => setOpen((o) => !o)}
            className="flex w-full items-center gap-2 px-4 py-3 text-left font-medium text-amber-200"
          >
            {open ? (
              <ChevronDown className="h-4 w-4" />
            ) : (
              <ChevronRight className="h-4 w-4" />
            )}
            <AlertTriangle className="h-4 w-4 shrink-0" />
            <span>Flagged Tags ({label})</span>
          </button>
          {open && (
            <ul className="flex flex-wrap gap-2 border-t border-amber-500/20 px-4 py-3">
              {flagged.map((f, i) => (
                <li key={`${f.category}-${f.value}-${i}`}>
                  <span className="inline-flex items-center rounded-md border border-amber-500/40 bg-amber-500/20 px-2 py-1 text-xs font-medium text-amber-100">
                    {formatLabel(f.value)} {Math.round(f.confidence * 100)}%
                  </span>
                </li>
              ))}
            </ul>
          )}
        </div>
      )}
    </div>
  );
}
