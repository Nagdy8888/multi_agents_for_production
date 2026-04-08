# Lab 18 — Database Deep Dive

**Estimated time:** 30 min  
**Difficulty:** Intermediate

The **image_tags** table stores one row per analyzed image: **image_id** (PK), **tag_record** (JSONB), **search_index** (TEXT[]), **image_url**, **needs_review**, **processing_status**, **created_at**, **updated_at**. The Supabase client provides **build_search_index** (flatten tag_record for search), **upsert_tag_record** (INSERT ON CONFLICT), **get_tag_record**, **list_tag_images**, **search_images_filtered** (@>), and **get_available_filter_values**. This lab summarizes the schema and client methods; see also Lab 14 for search flow.

---

## Learning objectives

- Understand the **migration.sql** schema and why we have both tag_record (JSONB) and search_index (TEXT[]).
- See **build_search_index**: flatten flat and hierarchical fields from tag_record into a sorted list of strings.
- See **upsert_tag_record**: build_search_index, then INSERT ... ON CONFLICT (image_id) DO UPDATE.
- See **_conn** with retries and **get_client** returning None when SUPABASE_ENABLED is false or connection fails.

---

## Prerequisites

- Labs 11 (upsert from server), 14 (search_images_filtered, get_available_filter_values).

---

## Schema (migration.sql)

**image_tags:** image_id (TEXT PK), tag_record (JSONB NOT NULL), search_index (TEXT[] NOT NULL DEFAULT '{}'), image_url (TEXT), needs_review (BOOLEAN DEFAULT false), processing_status (TEXT DEFAULT 'pending'), created_at, updated_at (TIMESTAMPTZ). Indexes: GIN on search_index, GIN on tag_record.

**Source:** [backend/src/services/supabase/migration.sql](../../backend/src/services/supabase/migration.sql)

---

## build_search_index (client.py)

Iterates tag_record: for flat keys (season, theme, design_elements, occasion, mood) add each list value to a set; for objects and dominant_colors add each item’s parent and child; for product_type add its parent and child. Return **sorted(list(set))** so search_index is a deterministic array for the @> query.

**Source:** [backend/src/services/supabase/client.py](../../backend/src/services/supabase/client.py) — build_search_index

---

## SupabaseClient methods

- **_conn(retries, delay):** psycopg2.connect with retry loop; raise on final failure.
- **upsert_tag_record:** build_search_index(tag_record), then INSERT ... ON CONFLICT (image_id) DO UPDATE SET tag_record, search_index, image_url, needs_review, processing_status, updated_at.
- **get_tag_record(image_id):** SELECT one row; return dict or None.
- **list_tag_images(limit, offset):** SELECT ORDER BY created_at DESC.
- **search_images_filtered(filters, limit):** Build flat_values from filters; SELECT WHERE search_index @> flat_values::text[].
- **get_available_filter_values(filters):** Call search_images_filtered(filters, 500), then aggregate unique values per category from each row’s tag_record; return { category: sorted(values) }.

**get_client()** (in supabase __init__ or client module): if not SUPABASE_ENABLED return None; else try SupabaseClient(), on exception return None.

**Source:** [backend/src/services/supabase/client.py](../../backend/src/services/supabase/client.py)

---

## Lab summary

- Schema: image_id, tag_record (JSONB), search_index (TEXT[]), plus metadata columns and GIN indexes. build_search_index flattens tag_record for @> queries. Client methods: upsert, get, list, search_filtered, get_available_filter_values; get_client can return None.

---

## Next lab

[19-taxonomy-and-config.md](19-taxonomy-and-config.md)
