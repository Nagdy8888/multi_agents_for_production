# 16 — Database

This document describes the database schema (migration.sql), how DATABASE_URI and SUPABASE_ENABLED are set, and the Supabase client: build_search_index, SupabaseClient (_conn with retry, upsert_tag_record, get_tag_record, list_tag_images, search_images_filtered, get_available_filter_values), and get_client. It also includes example SQL queries.

---

## Migration (schema)

**File:** `backend/src/services/supabase/migration.sql`

Run manually in the Supabase SQL editor or on first connection.

```sql
CREATE TABLE IF NOT EXISTS image_tags (
  image_id       TEXT PRIMARY KEY,
  tag_record    JSONB NOT NULL,
  search_index  TEXT[] NOT NULL DEFAULT '{}',
  image_url     TEXT,
  needs_review  BOOLEAN DEFAULT false,
  processing_status TEXT DEFAULT 'pending',
  created_at    TIMESTAMPTZ DEFAULT NOW(),
  updated_at    TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_search_index ON image_tags USING GIN (search_index);
CREATE INDEX IF NOT EXISTS idx_tag_record ON image_tags USING GIN (tag_record);
```

**Columns:**

| Column | Type | Purpose |
|--------|------|---------|
| image_id | TEXT PRIMARY KEY | Unique id (UUID from server). |
| tag_record | JSONB NOT NULL | Full TagRecord (season, theme, objects, dominant_colors, design_elements, occasion, mood, product_type, needs_review, processed_at). |
| search_index | TEXT[] NOT NULL | Flat list of tag values for containment search; built by build_search_index(tag_record). |
| image_url | TEXT | URL to serve the image (e.g. /uploads/xxx.jpg). |
| needs_review | BOOLEAN | True if any flagged or many low-confidence. |
| processing_status | TEXT | "pending" | "complete" | "needs_review" | "failed". |
| created_at | TIMESTAMPTZ | Set on insert. |
| updated_at | TIMESTAMPTZ | Set on insert and on update (upsert). |

**Indexes:** GIN on search_index for fast `@>` (array containment) queries; GIN on tag_record for JSONB queries if needed.

---

## Settings

**File:** `backend/src/services/supabase/settings.py`

- **DATABASE_URI:** `os.getenv("DATABASE_URI", "").strip()` — loaded from project root `.env`.
- **SUPABASE_ENABLED:** `bool(DATABASE_URI)` — True if URI is non-empty. When False, get_client() returns None and API routes return 503 or skip DB writes.

---

## build_search_index(tag_record)

**File:** `backend/src/services/supabase/client.py`

**Signature:** `def build_search_index(tag_record: dict) -> list[str]`

**Algorithm:**

- out = set().
- Flat keys: "season", "theme", "design_elements", "occasion", "mood". For each, if tag_record[key] is a list, add each string element to out.
- Hierarchical keys: "objects", "dominant_colors". For each, if tag_record[key] is a list, for each item (dict) add item["parent"] and item["child"] to out if present.
- product_type: if tag_record["product_type"] is a dict, add parent and child to out.
- Return sorted(out).

Used when upserting so search_index reflects all tag values for containment search.

---

## SupabaseClient

**File:** `backend/src/services/supabase/client.py`

### __init__(database_uri=None)

- self._uri = database_uri or DATABASE_URI. Raises ValueError if _uri is empty.

### _conn(retries=3, delay=1.0)

- Tries psycopg2.connect(self._uri) up to retries times; on failure sleeps delay seconds and retries. Raises last exception if all fail. Used by all methods that need a connection.

### upsert_tag_record(image_id, tag_record, image_url=None, needs_review=False, processing_status="complete")

- Builds search_index = build_search_index(tag_record); serializes tag_record to JSON.
- INSERT into image_tags (image_id, tag_record, search_index, image_url, needs_review, processing_status, updated_at) VALUES (...) ON CONFLICT (image_id) DO UPDATE SET tag_record = EXCLUDED.tag_record, search_index = EXCLUDED.search_index, image_url = EXCLUDED.image_url, needs_review = EXCLUDED.needs_review, processing_status = EXCLUDED.processing_status, updated_at = NOW().
- Commits; on exception rolls back and re-raises.

### get_tag_record(image_id)

- SELECT image_id, tag_record, search_index, image_url, needs_review, processing_status, created_at, updated_at FROM image_tags WHERE image_id = %s. Returns one row as dict or None.

### list_tag_images(limit=20, offset=0)

- SELECT same columns FROM image_tags ORDER BY created_at DESC LIMIT %s OFFSET %s. Returns list of dicts.

### search_images_filtered(filters, limit=50)

- Flattens filters dict to a list of non-empty strings (all values from all categories).
- If flat list is empty, returns list_tag_images(limit=limit, offset=0).
- Else: SELECT same columns FROM image_tags WHERE search_index @> %s::text[] ORDER BY created_at DESC LIMIT %s. The parameter is the flat list (PostgreSQL array); @> means "contains" (all those values must be in search_index). Returns list of dicts.

### get_available_filter_values(filters)

- Calls search_images_filtered(filters, limit=500) to get the result set for current filters.
- For each row, scans tag_record: for flat keys (season, theme, design_elements, occasion, mood) collects all string list elements; for objects and dominant_colors collects parent and child; for product_type collects parent and child. Builds categories dict: category -> set of values.
- Returns {k: sorted(s) for k, s in categories.items()} for cascading filter options.

---

## get_client()

- If not SUPABASE_ENABLED, return None. Else try SupabaseClient(); on exception log and return None.

---

## Example SQL queries

**All images (recent first):**
```sql
SELECT image_id, tag_record, search_index, image_url, needs_review, processing_status, created_at, updated_at
FROM image_tags ORDER BY created_at DESC LIMIT 20 OFFSET 0;
```

**Search by tags (e.g. christmas and whimsical):**
```sql
SELECT image_id, tag_record, search_index, image_url, needs_review, processing_status, created_at, updated_at
FROM image_tags
WHERE search_index @> ARRAY['christmas', 'whimsical']::text[]
ORDER BY created_at DESC LIMIT 50;
```

**Single image:**
```sql
SELECT * FROM image_tags WHERE image_id = 'a1b2c3d4-e5f6-7890-abcd-ef1234567890';
```
