# Database setup (image tagger, optional)

> **Prev:** [11_AIRTABLE_SETUP.md](11_AIRTABLE_SETUP.md) | **Index:** [00_SETUP_INDEX.md](00_SETUP_INDEX.md) | **Next:** [13_DOCKER_BUILD_AND_RUN.md](13_DOCKER_BUILD_AND_RUN.md)

Enables history / search endpoints (`/api/tag-images`, `/api/search-images`, …).

1. Create Supabase (or Postgres) database.
2. Run SQL from `apps/agents/src/services/supabase/migration.sql` (in repo).
3. Set in `.env`:

```env
DATABASE_URI=postgresql://...
```

If empty, image analysis still works; DB routes return **503**.
