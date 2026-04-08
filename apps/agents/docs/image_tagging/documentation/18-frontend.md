# 18 — Frontend

This document describes the Next.js frontend: pages and routes, layout and theme, data flow for analyze/search/bulk, TypeScript types, and a concise component list with props and API usage.

---

## Stack and structure

- **Framework:** Next.js 16 (App Router), React 19, TypeScript.
- **Styling:** Tailwind CSS, shadcn/ui (Button, Card, Badge, Skeleton, etc.), next-themes (dark/light), sonner (toast).
- **Key paths:** `frontend/src/app/` (pages, layout, error, globals.css), `frontend/src/components/`, `frontend/src/lib/` (types, formatTag, constants).

---

## Pages and routes

| Route | File | Purpose |
|-------|------|---------|
| / | app/page.tsx | Home: ImageUploader, single result (DashboardResult), BulkUploader, HistoryGrid. |
| /search | app/search/page.tsx | Search: FilterSidebar, SearchResults, DetailModal; manages filters, results, availableValues state. |
| (layout) | app/layout.tsx | Root layout: ThemeProvider, Navbar, Toaster, children. |
| (error) | app/error.tsx | Error boundary: message, retry, "Go home" link. |

---

## Layout and theme

- **layout.tsx:** Wraps app in ThemeProvider (next-themes), renders Navbar and Toaster (sonner). Children render the page.
- **globals.css:** Tailwind, CSS variables for theme; focus-visible styles for accessibility.
- **ThemeToggle** and **Navbar:** Navbar has links (Tag Image, Search) and theme toggle. Font: Inter (or project default).

---

## Data flow

- **Single analyze:** User drops file → ImageUploader sends POST /api/analyze-image with FormData (file) → response stored in state → DashboardResult shows image_url, tags_by_category, tag_record, flagged_tags, saved_to_db (toast + badge). HistoryGrid refetches GET /api/tag-images when appropriate.
- **Search:** User opens /search → page loads taxonomy and initial results (GET /api/search-images, GET /api/available-filters with current filters). FilterSidebar toggles filters; parent state filters update → useEffect refetches search-images and available-filters → SearchResults and FilterSidebar (cascading options) update. Clicking a result opens DetailModal with full row (tag_record, flagged_tags).
- **Bulk:** User selects files in BulkUploader → POST /api/bulk-upload (files) → receive batch_id → poll GET /api/bulk-status/{batch_id} on interval until status "complete" or all done → show progress and per-file status; "View in history" links to /.

---

## TypeScript types (lib/types.ts)

| Type | Purpose |
|------|---------|
| PartialTagResult | category, tags, confidence_scores (single tagger output). |
| TagWithConfidence | value, confidence (for tags_by_category). |
| HierarchicalTag | parent, child. |
| TagRecord | image_id, season, theme, objects, dominant_colors, design_elements, occasion, mood, product_type, needs_review, processed_at. |
| FlaggedTag | category, value, confidence, reason. |
| AnalyzeImageResponse | image_url, image_id, vision_description, vision_raw_tags, partial_tags?, tags_by_category?, tag_record?, flagged_tags?, processing_status?, saved_to_db?. |
| TagImageRow | image_id, tag_record, search_index?, image_url?, needs_review, processing_status, created_at, updated_at. |
| TagImagesListResponse | items: TagImageRow[], limit, offset. |

BulkUploader defines locally: BatchResultItem (image_id, status, image_url?, error?), BatchState (total, completed, results, status).

---

## API base URL

- **NEXT_PUBLIC_API_URL** is set at build time (e.g. http://localhost:8000). Used for all fetch calls to the backend. See [19-docker-and-deployment.md](19-docker-and-deployment.md) for production.

---

## Components (concise)

| Component | Purpose | API / props |
|-----------|---------|-------------|
| **ImageUploader** | Dropzone, single file; on success sets result for DashboardResult. | POST /api/analyze-image. |
| **BulkUploader** | Multi-file dropzone; "Start Bulk Analysis" → POST /api/bulk-upload; polls GET /api/bulk-status/{batch_id}. | — |
| **DashboardResult** | Two-panel: image + AI analysis (TagCategories, ConfidenceRing, FlaggedTags, tag_record); "Saved" badge if saved_to_db. | Receives AnalyzeImageResponse. |
| **TagCategories** | Renders tags_by_category as category cards (TagCategoryCard) with TagChip (value + confidence %). | tags_by_category. |
| **TagCategoryCard** | One category: title, list of TagChip. | category, tags (TagWithConfidence[]). |
| **TagChip** | Chip with value and confidence percentage; styling by confidence band. | value, confidence; formatTagLabel for display. |
| **ConfidenceRing** | Ring or indicator for overall confidence. | Receives data from result. |
| **FlaggedTags** | List of flagged tags (category, value, reason); always visible, empty state if none. | flagged_tags. |
| **JsonViewer** | Optional raw JSON display (e.g. tag_record). | data (record). |
| **FilterSidebar** | Fetches GET /api/taxonomy; renders filter categories with chips; toggles update parent filters state (cascading: chips disabled if not in availableValues). | filters, setFilters, availableValues (from parent). |
| **SearchResults** | Grid of result cards (thumbnail, sample tags, status); onSelectItem opens DetailModal. | results, loading, onSelectItem. |
| **DetailModal** | Overlay: image, image_id, processing_status, date, TagCategories (from tag_record), FlaggedTags; Escape to close. | item (row), onClose. |
| **HistoryGrid** | GET /api/tag-images; grid of thumbnails, truncated image_id, status, sample tags, date; empty state with icon; Skeleton when loading. | — |
| **Navbar** | Links (Tag Image, Search), ThemeToggle. | — |
| **ThemeProvider / ThemeToggle** | next-themes; toggle light/dark. | — |
| **ProcessingOverlay** | Shown while analyze in progress (e.g. steps). | visible, steps. |
| **ui/** | shadcn: button, card, badge, skeleton, sonner. | — |

---

## Error handling

- **error.tsx:** Catches runtime errors in the app; shows message, retry button, and link to home. No asChild on Button; Link wraps Button for navigation.

---

See [17-api-reference.md](17-api-reference.md) for backend contracts and [02-architecture.md](02-architecture.md) for end-to-end flow.
