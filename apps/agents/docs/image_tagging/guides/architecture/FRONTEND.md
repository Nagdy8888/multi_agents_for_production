# Frontend structure

Next.js 16 App Router, TypeScript, Tailwind v4, shadcn/ui. Entry: `frontend/src/app`.

## Pages

| Route | File | Description |
|-------|------|-------------|
| / | app/page.tsx | Tag Image: upload, analyze, result (DashboardResult), HistoryGrid, BulkUploader |
| /search | app/search/page.tsx | Search: FilterSidebar + SearchResults + DetailModal |

## Key components

- **Navbar** — Logo, “Tag Image” / “Search”, theme toggle.
- **ImageUploader** — Single-file dropzone; calls `onAnalyze(file)`.
- **BulkUploader** — Multi-file dropzone; POST bulk-upload, poll bulk-status, progress and per-file status.
- **ProcessingOverlay** — Step-based overlay during analysis.
- **DashboardResult** — Two-panel: Product Image (with “Saved” badge) + AI Analysis (vision, ConfidenceRing), then TagCategories, FlaggedTags, JsonViewer.
- **TagCategories / TagCategoryCard** — Grid of category cards with chips and confidence.
- **FlaggedTags** — Collapsible list of tags needing review.
- **HistoryGrid** — Fetches tag-images; grid of recent cards; Refresh.
- **FilterSidebar** — Taxonomy-driven filter chips (8 categories), cascading; updates search.
- **SearchResults** — Grid of search result cards; click opens DetailModal.
- **DetailModal** — Full image, tag_record as TagCategories, metadata.

## Data flow

- **Analyze:** page → POST /api/analyze-image → set result → DashboardResult; if `saved_to_db`, toast + badge.
- **History:** HistoryGrid → GET /api/tag-images → grid.
- **Search:** search page state (filters, results, availableValues) → GET /api/search-images and GET /api/available-filters when filters change; FilterSidebar toggles update state; SearchResults + DetailModal show data.

Types and API base URL: `frontend/src/lib/types.ts`, `frontend/src/lib/constants.ts`.
