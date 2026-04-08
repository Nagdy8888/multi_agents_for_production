# Supabase Service

Database client for image_tags table: upsert, get, list. Used when SUPABASE_ENABLED is true (DATABASE_URI set in project root .env).

## Contents

| File | Description |
|------|-------------|
| `migration.sql` | image_tags table and GIN indexes; run in Supabase SQL editor |
| `settings.py` | DATABASE_URI, SUPABASE_ENABLED |
| `client.py` | build_search_index, SupabaseClient (upsert_tag_record, get_tag_record, list_tag_images), get_client |
| `__init__.py` | Exports client and settings |
