"use client";

import { useState, useEffect, useCallback } from "react";
import { ChevronDown, ChevronUp, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { API_BASE_URL } from "@/lib/constants";
import { formatTagLabel } from "@/lib/formatTag";
import { cn } from "@/lib/utils";

const CATEGORY_ORDER = [
  "season",
  "theme",
  "objects",
  "dominant_colors",
  "design_elements",
  "occasion",
  "mood",
  "product_type",
];

const CATEGORY_LABELS: Record<string, string> = {
  season: "Season",
  theme: "Theme",
  objects: "Objects",
  dominant_colors: "Dominant Colors",
  design_elements: "Design Elements",
  occasion: "Occasion",
  mood: "Mood",
  product_type: "Product Type",
};

const CATEGORY_BORDER_COLORS: Record<string, string> = {
  season: "border-l-amber-500",
  theme: "border-l-violet-500",
  objects: "border-l-cyan-500",
  dominant_colors: "border-l-rose-500",
  design_elements: "border-l-blue-500",
  occasion: "border-l-emerald-500",
  mood: "border-l-orange-500",
  product_type: "border-l-indigo-500",
};

const CATEGORY_CHIP_COLORS: Record<string, { border: string; bg: string }> = {
  season: { border: "border-amber-500/60", bg: "bg-amber-500" },
  theme: { border: "border-violet-500/60", bg: "bg-violet-500" },
  objects: { border: "border-cyan-500/60", bg: "bg-cyan-500" },
  dominant_colors: { border: "border-rose-500/60", bg: "bg-rose-500" },
  design_elements: { border: "border-blue-500/60", bg: "bg-blue-500" },
  occasion: { border: "border-emerald-500/60", bg: "bg-emerald-500" },
  mood: { border: "border-orange-500/60", bg: "bg-orange-500" },
  product_type: { border: "border-indigo-500/60", bg: "bg-indigo-500" },
};

type Taxonomy = Record<string, string[] | Record<string, string[]>>;

function flattenTaxonomyValues(category: string, taxonomy: Taxonomy): { value: string; parent?: string }[] {
  const val = taxonomy[category];
  if (!val) return [];
  if (Array.isArray(val)) return val.map((v) => ({ value: v }));
  const dict = val as Record<string, string[]>;
  const out: { value: string; parent?: string }[] = [];
  for (const [parent, children] of Object.entries(dict)) {
    out.push({ value: parent, parent: undefined });
    for (const c of children) out.push({ value: c, parent });
  }
  return out;
}

interface FilterSidebarProps {
  filters: Record<string, string[]>;
  setFilters: (f: Record<string, string[]>) => void;
  availableValues: Record<string, string[]>;
  /** Optional: called when filters change (e.g. for immediate fetch). Parent may also rely on useEffect. */
  onFiltersChange?: (filters: Record<string, string[]>) => void;
  className?: string;
  collapsed?: boolean;
  onToggleCollapsed?: () => void;
}

export function FilterSidebar({
  filters,
  setFilters,
  availableValues,
  onFiltersChange,
  className,
  collapsed = false,
  onToggleCollapsed,
}: FilterSidebarProps) {
  const [taxonomy, setTaxonomy] = useState<Taxonomy | null>(null);
  const [categoryExpanded, setCategoryExpanded] = useState<Record<string, boolean>>(() =>
    Object.fromEntries(CATEGORY_ORDER.map((c) => [c, true]))
  );

  useEffect(() => {
    fetch(`${API_BASE_URL}/api/taxonomy`)
      .then((r) => r.ok ? r.json() : null)
      .then(setTaxonomy)
      .catch(() => setTaxonomy(null));
  }, []);

  const toggle = useCallback(
    (category: string, value: string) => {
      const current = filters[category] ?? [];
      const next = current.includes(value)
        ? current.filter((v) => v !== value)
        : [...current, value];
      const newFilters = { ...filters, [category]: next.length ? next : [] };
      if (!newFilters[category]?.length) delete newFilters[category];
      setFilters(newFilters);
      onFiltersChange?.(newFilters);
    },
    [filters, setFilters, onFiltersChange]
  );

  const clearAll = useCallback(() => {
    setFilters({});
    onFiltersChange?.({});
  }, [setFilters, onFiltersChange]);

  const selectedList = Object.entries(filters).flatMap(([cat, vals]) =>
    (vals ?? []).map((v) => ({ category: cat, value: v }))
  );

  const toggleCategory = (key: string) => {
    setCategoryExpanded((prev) => ({ ...prev, [key]: !prev[key] }));
  };

  /** Group hierarchical values by parent for sub-headers. */
  const groupByParent = (values: { value: string; parent?: string }[]) => {
    const groups: { parent?: string; values: string[] }[] = [];
    let currentParent: string | undefined;
    let currentList: string[] = [];
    for (const { value, parent } of values) {
      if (parent !== currentParent) {
        if (currentList.length) groups.push({ parent: currentParent, values: currentList });
        currentParent = parent;
        currentList = [value];
      } else {
        currentList.push(value);
      }
    }
    if (currentList.length) groups.push({ parent: currentParent, values: currentList });
    return groups;
  };

  return (
    <aside
      className={cn(
        "flex w-full flex-col border-r border-border/60 bg-card/80 md:w-72 md:flex-shrink-0",
        className
      )}
    >
      <div className="flex items-center justify-between border-b border-border/60 p-4">
        <h2 className="text-sm font-semibold uppercase tracking-wide text-foreground">Filter by Tags</h2>
        {onToggleCollapsed && (
          <Button variant="ghost" size="icon" className="md:hidden" onClick={onToggleCollapsed}>
            {collapsed ? <ChevronDown className="h-4 w-4" /> : <ChevronUp className="h-4 w-4" />}
          </Button>
        )}
      </div>
      {!collapsed && (
        <>
          <div className="border-b border-border/60 p-3">
            {selectedList.length === 0 ? (
              <p className="text-xs text-muted-foreground">No filters selected</p>
            ) : (
              <div className="flex flex-wrap items-center gap-2">
                {selectedList.map(({ category, value }) => (
                  <span
                    key={`${category}-${value}`}
                    className={cn(
                      "inline-flex items-center gap-1 rounded-full border px-2 py-0.5 text-xs font-medium text-white",
                      CATEGORY_CHIP_COLORS[category]?.bg ?? "bg-muted"
                    )}
                  >
                    {formatTagLabel(value)}
                    <button
                      type="button"
                      aria-label={`Remove ${value}`}
                      className="hover:opacity-80"
                      onClick={() => toggle(category, value)}
                    >
                      <X className="h-3 w-3" />
                    </button>
                  </span>
                ))}
                <Button variant="ghost" size="sm" className="h-7 text-xs" onClick={clearAll}>
                  Clear All
                </Button>
              </div>
            )}
          </div>
          <div className="flex-1 overflow-y-auto p-2">
            {!taxonomy ? (
              <p className="text-xs text-muted-foreground">Loading taxonomy…</p>
            ) : (
              CATEGORY_ORDER.map((category) => {
                const values = flattenTaxonomyValues(category, taxonomy);
                const hasFilters = Object.keys(filters).some((k) => (filters[k]?.length ?? 0) > 0);
                const available = hasFilters ? new Set(availableValues[category] ?? []) : null;
                const expanded = categoryExpanded[category] ?? true;
                const borderClass = CATEGORY_BORDER_COLORS[category] ?? "border-l-muted";
                const chipStyle = CATEGORY_CHIP_COLORS[category] ?? { border: "border-border", bg: "bg-muted" };
                return (
                  <div
                    key={category}
                    className={cn("mb-2 rounded-lg border border-border/60 border-l-4", borderClass)}
                  >
                    <button
                      type="button"
                      className="flex w-full items-center justify-between px-3 py-2 text-left text-sm font-medium text-foreground"
                      onClick={() => toggleCategory(category)}
                    >
                      {CATEGORY_LABELS[category]}
                      {expanded ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
                    </button>
                    {expanded && (
                      <div className="space-y-2 px-3 pb-3">
                        {groupByParent(values).map((group) => (
                          <div key={group.parent ?? "flat"}>
                            {group.parent !== undefined && (
                              <p className="mb-1 mt-2 text-[10px] font-semibold uppercase tracking-wider text-muted-foreground">
                                {formatTagLabel(group.parent)}
                              </p>
                            )}
                            <div className="flex flex-wrap gap-1.5">
                              {group.values.map((value) => {
                                const selected = (filters[category] ?? []).includes(value);
                                const disabled = available !== null && !available.has(value);
                                return (
                                  <button
                                    key={value}
                                    type="button"
                                    className={cn(
                                      "rounded-full border px-2 py-1 text-xs transition",
                                      selected ? `${chipStyle.bg} text-white` : "bg-background/80 text-foreground " + chipStyle.border,
                                      disabled && "cursor-not-allowed opacity-50"
                                    )}
                                    onClick={() => !disabled && toggle(category, value)}
                                  >
                                    {formatTagLabel(value)}
                                  </button>
                                );
                              })}
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                );
              })
            )}
          </div>
        </>
      )}
    </aside>
  );
}
