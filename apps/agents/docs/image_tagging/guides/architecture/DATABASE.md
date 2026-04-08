# Database (Supabase)

When `DATABASE_URI` is set in the project root `.env`, the backend persists tag results and supports search.

## Schema

Migration: `backend/src/services/supabase/migration.sql`. Run it once in the Supabase SQL editor.

**Table: `image_tags`**

| Column | Type | Description |
|--------|------|-------------|
| image_id | TEXT | Primary key (UUID from upload) |
| tag_record | JSONB | Full tag record (season, theme, objects, …) |
| search_index | TEXT[] | Flattened tag values for containment search |
| image_url | TEXT | URL to serve the image (e.g. /uploads/…) |
| needs_review | BOOLEAN | True if confidence filter flagged |
| processing_status | TEXT | complete / needs_review / failed |
| created_at | TIMESTAMPTZ | First insert |
| updated_at | TIMESTAMPTZ | Last update |

**Indexes**

- `idx_search_index` — GIN on `search_index` for `@>` (array contains) queries.
- `idx_tag_record` — GIN on `tag_record` for JSONB queries if needed.

## Example queries

- **All recent:** `SELECT * FROM image_tags ORDER BY created_at DESC LIMIT 50;`
- **Filter by tags (AND):** `SELECT * FROM image_tags WHERE search_index @> ARRAY['christmas','modern']::text[] ORDER BY created_at DESC LIMIT 50;`

The client builds `search_index` in `build_search_index(tag_record)` (flat lists + parent/child for hierarchical fields) and uses `@>` for `search_images_filtered`.
