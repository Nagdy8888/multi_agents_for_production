"use client";

import { useState, useEffect, useCallback } from "react";
import { Menu } from "lucide-react";
import { Button } from "@/components/ui/button";
import { FilterSidebar } from "@/components/FilterSidebar";
import { SearchResults } from "@/components/SearchResults";
import { DetailModal } from "@/components/DetailModal";
import { API_BASE_URL } from "@/lib/constants";
import type { TagImageRow } from "@/lib/types";

function buildQuery(filters: Record<string, string[]>): string {
  const params = new URLSearchParams();
  for (const [k, vals] of Object.entries(filters)) {
    if (vals?.length) params.set(k, vals.join(","));
  }
  return params.toString();
}

export default function SearchPage() {
  const [filters, setFilters] = useState<Record<string, string[]>>({});
  const [results, setResults] = useState<TagImageRow[]>([]);
  const [availableValues, setAvailableValues] = useState<Record<string, string[]>>({});
  const [loading, setLoading] = useState(true);
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [selectedRow, setSelectedRow] = useState<TagImageRow | null>(null);

  const fetchSearchAndAvailable = useCallback(async (f: Record<string, string[]>) => {
    setLoading(true);
    const q = buildQuery(f);
    try {
      const [searchRes, availRes] = await Promise.all([
        fetch(`${API_BASE_URL}/api/search-images?${q}&limit=50`),
        fetch(`${API_BASE_URL}/api/available-filters?${q}`),
      ]);
      if (searchRes.ok) {
        const data = await searchRes.json();
        setResults(data.items ?? []);
      } else if (searchRes.status === 503) {
        setResults([]);
      }
      if (availRes.ok) {
        const avail = await availRes.json();
        setAvailableValues(avail ?? {});
      } else {
        setAvailableValues({});
      }
    } catch {
      setResults([]);
      setAvailableValues({});
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchSearchAndAvailable(filters);
  }, [filters, fetchSearchAndAvailable]);

  return (
    <main className="flex min-h-[calc(100vh-3.5rem)] flex-col md:flex-row">
      <div className={sidebarCollapsed ? "hidden md:block md:w-0" : "w-full md:w-72"}>
        <FilterSidebar
          filters={filters}
          setFilters={setFilters}
          availableValues={availableValues}
          collapsed={sidebarCollapsed}
          onToggleCollapsed={() => setSidebarCollapsed((c) => !c)}
        />
      </div>
      <div className="flex-1 p-4">
        <div className="mb-4 flex items-center gap-2">
          <Button
            variant="ghost"
            size="icon"
            className="md:hidden"
            onClick={() => setSidebarCollapsed((c) => !c)}
            aria-label="Toggle filters"
          >
            <Menu className="h-5 w-5" />
          </Button>
          <h1 className="text-xl font-semibold">Search</h1>
        </div>
        <SearchResults
          items={results}
          loading={loading}
          onSelectItem={setSelectedRow}
        />
      </div>
      <DetailModal row={selectedRow} onClose={() => setSelectedRow(null)} />
    </main>
  );
}
