# Lab 13 — Search Page and Filters

**Estimated time:** 25 min  
**Difficulty:** Beginner

The **Search** page lets users filter tagged images by category (season, theme, mood, etc.). The page holds **filters** in state; when filters change, it fetches **search-images** and **available-filters** in parallel. **FilterSidebar** shows the taxonomy and lets users toggle filter values; **availableValues** (from the API) drives which options are shown so filters are cascading. This lab traces the search page and FilterSidebar.

---

## Learning objectives

- See **buildQuery** and how filters state is turned into query params.
- See **fetchSearchAndAvailable**: parallel fetch of search-images and available-filters, and how results and availableValues update state.
- See how **FilterSidebar** fetches taxonomy, uses **availableValues** for cascading options, and calls **setFilters** when the user toggles a value.

---

## Prerequisites

- [12-frontend-shows-result.md](12-frontend-shows-result.md). Search is a separate flow; no graph runs here.

---

## Step 1 — buildQuery and page state

**Snippet (lines 12–17, 20–26 in search/page.tsx)**

```tsx
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
  ...
```

**What is happening**

- **filters** — Dict like `{ season: ["christmas"], mood: ["joyful_fun"] }`. buildQuery turns it into `season=christmas&mood=joyful_fun` for the API.
- **results** — List of TagImageRow from search-images. **availableValues** — Dict category → list of values still available given current filters (from available-filters API). **loading** — True while fetch runs.

**Source:** [frontend/src/app/search/page.tsx](../../frontend/src/app/search/page.tsx) (lines 12–26)

---

## Step 2 — fetchSearchAndAvailable and useEffect

**Snippet (lines 27–57 in search/page.tsx)**

```tsx
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
```

**What is happening**

- **Promise.all** — We call search-images and available-filters with the **same** query string so both use the current filters. search-images returns matching rows; available-filters returns which values still exist in those rows (cascading).
- **useEffect** — Whenever **filters** changes (user toggles something in FilterSidebar), we run fetchSearchAndAvailable(filters). So changing a filter immediately refetches both search and available options.

**Source:** [frontend/src/app/search/page.tsx](../../frontend/src/app/search/page.tsx) (lines 27–57)

---

## Step 3 — FilterSidebar: taxonomy and availableValues

FilterSidebar fetches GET /api/taxonomy once to get the full category structure. It displays one section per category; for each category it shows **availableValues[category]** (or all taxonomy values if availableValues is empty) so options are cascading: only values that exist in the current result set are shown.

**Snippet (lines 79–98 in FilterSidebar.tsx)**

```tsx
export function FilterSidebar({
  filters,
  setFilters,
  availableValues,
  ...
}: FilterSidebarProps) {
  const [taxonomy, setTaxonomy] = useState<Taxonomy | null>(null);
  ...
  useEffect(() => {
    fetch(`${API_BASE_URL}/api/taxonomy`)
      .then((r) => r.ok ? r.json() : null)
      .then(setTaxonomy)
      .catch(() => setTaxonomy(null));
  }, []);
```

When the user clicks a value (e.g. "christmas" under Season), the sidebar calls setFilters with an updated dict (e.g. season: ["christmas"]). That triggers the page’s useEffect and thus fetchSearchAndAvailable.

**Source:** [frontend/src/components/FilterSidebar.tsx](../../frontend/src/components/FilterSidebar.tsx) (lines 79–98)

> **Next:** The backend for search-images and available-filters is in [14-search-backend-and-db.md](14-search-backend-and-db.md). The grid of results and the detail modal are in [15-search-results-and-modal.md](15-search-results-and-modal.md).

---

## Lab summary

- **buildQuery(filters)** produces the query string for both search-images and available-filters.
- **fetchSearchAndAvailable** runs both fetches in parallel and sets **results** and **availableValues**; **useEffect** runs it whenever **filters** changes.
- **FilterSidebar** loads taxonomy once, displays categories, uses **availableValues** for cascading options, and updates **filters** via **setFilters** so the page refetches.

---

## Next lab

[14-search-backend-and-db.md](14-search-backend-and-db.md) — search_images endpoint, _parse_filter_params, and search_index @> containment.
