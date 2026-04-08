# Phase 5: Search, Filters, and Bulk Upload — Setup Guide

## What This Phase Adds

- **Backend**
  - **Supabase client:** `search_images_filtered(filters, limit=50)` — WHERE search_index @> selected values (AND logic), order by created_at DESC; `get_available_filter_values(filters)` — from filtered rows, collect unique tag values per category for cascading filters.
  - **Search API:** `GET /api/search-images` — query params: season, theme, objects, dominant_colors, design_elements, occasion, mood, product_type (comma-separated); returns filtered items. `GET /api/available-filters` — same params, returns cascading available values per category.
  - **Bulk upload:** `POST /api/bulk-upload` — multiple files (form field `files`), returns `{ batch_id, total, status: "processing" }`, processes in background; `GET /api/bulk-status/{batch_id}` — returns `{ total, completed, results: [{ image_id, status, image_url?, error? }], status }`.
- **Frontend**
  - **Search page:** `/search` — sidebar (FilterSidebar) + main (SearchResults); mobile collapsible sidebar (hamburger).
  - **FilterSidebar:** Fetches taxonomy; "Filter by Tags" heading; selected chips + Clear All; 8 category cards with colored left border, expand/collapse, tag chips (pill style, toggle select). Hierarchical categories (objects, dominant_colors, product_type) show parent sub-headers and child chips. Cascading: when filters selected, chips not in available-filters are grayed out. Toggling a chip updates filters and triggers search + available-filters.
  - **SearchResults:** Grid of image cards (thumbnail, season/theme tags, status); loading skeletons; empty state with icon. Click card opens DetailModal.
  - **DetailModal:** Full image, image_id, status, processed date, TagCategories from tag_record, close button and Escape.
  - **BulkUploader:** Multi-file dropzone (react-dropzone), file list with thumbnails, "Start Bulk Analysis" → POST bulk-upload, poll bulk-status every 2s, progress bar and per-file status (pending/complete/failed), summary + "Upload more" and "View in history" on completion. Added to dashboard below single upload in a "Bulk Upload" section.

## Prerequisites

- Phase 0–4 complete
- Database configured (for search and history); bulk upload works without DB (analysis runs, save skipped if DB disabled).

## Files Changed / Added

| Path | Change |
|------|--------|
| `backend/src/services/supabase/client.py` | search_images_filtered, get_available_filter_values |
| `backend/src/server.py` | _parse_filter_params, GET search-images, GET available-filters, POST bulk-upload, GET bulk-status, BATCH_STORAGE, _process_one_file, _run_bulk_batch |
| `frontend/src/lib/formatTag.ts` | formatTagLabel |
| `frontend/src/components/FilterSidebar.tsx` | Added |
| `frontend/src/components/SearchResults.tsx` | Added |
| `frontend/src/components/DetailModal.tsx` | Added |
| `frontend/src/components/BulkUploader.tsx` | Added |
| `frontend/src/app/search/page.tsx` | Full search page with FilterSidebar, SearchResults, DetailModal |
| `frontend/src/app/page.tsx` | BulkUploader section |

## Step-by-Step Setup (Docker)

1. **Run app:** `docker compose up --build`
2. **Search:** Open http://localhost:3000/search. Select filters (e.g. Season → Christmas); results update; select more filters to cascade. Click a result to open detail modal.
3. **Bulk:** On http://localhost:3000, scroll to "Bulk Upload", add multiple images, click "Start Bulk Analysis". Polling shows progress; when complete, use "View in history" or "Upload more".

## How to Test

- **Search:** No filters → all tagged images (or 503/empty if DB off). Add season=christmas → only Christmas-tagged; add theme=modern → further narrowed. Chips not in available set are grayed out.
- **Detail modal:** Click a search card → modal with image, tags by category, metadata; Escape or overlay click closes.
- **Bulk:** Upload 3 images → 3 pending; after processing, 3 complete (or failed with error). Status endpoint returns completed count and per-file status.
