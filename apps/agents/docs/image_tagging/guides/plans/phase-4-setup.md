# Phase 4: Supabase Integration and Persistence — Setup Guide

## What This Phase Adds

- **Backend**
  - **Migration:** `backend/src/services/supabase/migration.sql` — `image_tags` table (image_id PK, tag_record JSONB, search_index TEXT[], image_url, needs_review, processing_status, created_at, updated_at) and GIN indexes. Run manually in Supabase SQL editor.
  - **Settings:** `settings.py` — loads `DATABASE_URI` from project root `.env`; `SUPABASE_ENABLED` true when URI is set.
  - **Client:** `client.py` — `build_search_index(tag_record)` flattens tag values for search; `SupabaseClient.upsert_tag_record`, `get_tag_record(image_id)`, `list_tag_images(limit, offset)`; `get_client()` returns client when DB configured.
  - **Server:** After analyze, if Supabase enabled, upserts tag record; response includes `saved_to_db`. New routes: `GET /api/tag-image/{image_id}` (503 if DB disabled, 404 if not found), `GET /api/tag-images?limit=20&offset=0` (503 if DB disabled).
- **Frontend**
  - **Toaster:** Sonner `<Toaster />` in layout for save feedback.
  - **Save feedback:** On analyze response, if `saved_to_db` show success toast and “Saved” badge next to Product Image.
  - **Types:** `saved_to_db` on `AnalyzeImageResponse`; `TagImageRow`, `TagImagesListResponse` for history.
  - **HistoryGrid:** Fetches `GET /api/tag-images`, responsive grid of cards (thumbnail, truncated image_id, processing_status badge, 3–4 sample tags, date); Refresh button; shows “Database not configured” when API returns 503 or empty list.
  - **Page:** “Recently Tagged Images” section with HistoryGrid below main content (upload or result).

## Prerequisites

- Phase 0, 1, 2, 3 complete
- `.env` with `OPENAI_API_KEY`; optional `DATABASE_URI` (Supabase/PostgreSQL connection string) for persistence

## Files Changed / Added

| Path | Change |
|------|--------|
| `backend/src/services/supabase/migration.sql` | Added (Phase 4) |
| `backend/src/services/supabase/settings.py` | Added |
| `backend/src/services/supabase/client.py` | Added |
| `backend/src/services/supabase/__init__.py` | Added |
| `backend/src/services/__init__.py` | Added |
| `backend/src/server.py` | Persist after analyze, `saved_to_db`; GET tag-image, tag-images |
| `frontend/src/lib/types.ts` | saved_to_db, TagImageRow, TagImagesListResponse |
| `frontend/src/app/layout.tsx` | Toaster from sonner |
| `frontend/src/app/page.tsx` | toast on saved_to_db, HistoryGrid |
| `frontend/src/components/DashboardResult.tsx` | “Saved” badge when saved_to_db |
| `frontend/src/components/HistoryGrid.tsx` | Added |

## Step-by-Step Setup (Docker)

1. **Database (optional)**  
   In Supabase dashboard → SQL Editor, run `backend/src/services/supabase/migration.sql`.  
   In project root `.env`, set:
   ```env
   DATABASE_URI=postgresql://user:password@host:5432/postgres
   ```
   (Use your Supabase connection string.)

2. **Run app**
   ```bash
   docker compose up --build
   ```

3. **Verify**  
   Open http://localhost:3000. Upload and analyze an image. If `DATABASE_URI` is set: “Analysis saved to database” toast and “Saved” badge appear; “Recently Tagged Images” shows the new entry with Refresh. If not set: no toast/badge, history section shows “Database not configured” or empty state.

## How to Test

- **Without DB:** Leave `DATABASE_URI` unset. Analyze image → no `saved_to_db`, no toast/badge; GET /api/tag-images returns 503 or frontend shows empty/disabled message.
- **With DB:** Set `DATABASE_URI`, run migration. Analyze image → `saved_to_db: true`, toast and “Saved” badge; GET /api/tag-images returns items; GET /api/tag-image/{id} returns stored row.
- **HistoryGrid:** Refresh reloads list; cards link to image_url; sample tags and date display correctly.
