# 20 — Development Phases

This document summarizes each implementation phase (0–6): what was built, key files changed, and what to verify. It also references the progress diagram and changelog.

---

## Phase 0 — Project skeleton

- **Backend:** FastAPI app, health check, folder structure (image_tagging, nodes, prompts, schemas, services/supabase), settings loader, uploads directory.
- **Frontend:** Next.js with Tailwind, shadcn/ui, Navbar (Tag Image / Search), theme toggle, placeholder pages.
- **Docs:** Folder tree (curriculum, quickstart, architecture, reports, errors, plans), PROGRESS.md diagram.

**Key files:** backend/src/server.py, frontend app layout and pages, docs structure.

**Verify:** GET /api/health returns 200; frontend loads with Navbar and theme toggle.

---

## Phase 1 — Simple image analyzer

- **Backend:** Static /uploads mount, POST /api/analyze-image (file upload, GPT-4o vision, return description + raw tags).
- **Frontend:** ImageUploader (dropzone), processing overlay, vision results display.

**Key files:** server.py (analyze-image, StaticFiles), ImageUploader, ProcessingOverlay, VisionResults.

**Verify:** Upload image → receive vision description and raw tags in response.

---

## Phase 2 — LangGraph pipeline

- **Backend:** Schemas (state, models), taxonomy, vision + tagger prompts, preprocessor + vision + season tagger nodes, linear graph, GET /api/taxonomy.
- **Frontend:** TagCategoryCard with confidence, pipeline tags on dashboard.

**Key files:** image_tagging/schemas, taxonomy.py, prompts, nodes (preprocessor, vision, taggers), graph_builder.py, image_tagging.py, server (graph.ainvoke, taxonomy route).

**Verify:** Analyze returns vision_description and at least season tags; GET /api/taxonomy returns TAXONOMY.

---

## Phase 3 — Full parallel tagging

- **Backend:** Configuration (thresholds, overrides), all 8 taggers, validator, confidence filter, aggregator, fan-out graph (Send), tag_record and flagged_tags in response.
- **Frontend:** TagCategories, TagChip, FlaggedTags, ProcessingOverlay (6 steps), DashboardResult with two-panel layout and tag_record JSON.

**Key files:** configuration.py, nodes (taggers full set, validator, confidence, aggregator), graph_builder (conditional_edges, fan_out_to_taggers), server (tags_by_category, tag_record, flagged_tags in response).

**Verify:** Analyze returns all 8 categories in tag_record; flagged_tags and needs_review appear when applicable.

---

## Phase 4 — Supabase integration

- **Backend:** migration.sql (image_tags table, GIN indexes), Supabase settings + client (upsert, get, list, build_search_index), save after analyze, GET /api/tag-image/{id}, GET /api/tag-images.
- **Frontend:** Toaster, saved_to_db toast and “Saved” badge, HistoryGrid (“Recently Tagged Images”).

**Key files:** services/supabase (settings, client, migration), server (upsert after analyze, get tag-image, tag-images), HistoryGrid, DashboardResult (saved badge), layout (Toaster).

**Verify:** With DATABASE_URI set, analyze saves to DB and “Saved” appears; GET /api/tag-images returns list; HistoryGrid shows recent images.

---

## Phase 5 — Search and bulk upload

- **Backend:** search_images_filtered, get_available_filter_values, GET /api/search-images, GET /api/available-filters, POST /api/bulk-upload, GET /api/bulk-status/{batch_id}.
- **Frontend:** Search page (FilterSidebar, SearchResults, DetailModal), BulkUploader (multi-file, progress, per-file status), “Bulk Upload” section on home.

**Key files:** client.py (search_images_filtered, get_available_filter_values), server (_parse_filter_params, search-images, available-filters, bulk-upload, bulk-status, BATCH_STORAGE, _process_one_file, _run_bulk_batch), app/search/page.tsx, FilterSidebar, SearchResults, DetailModal, BulkUploader.

**Verify:** Search by filters returns filtered results; available-filters returns cascading values; bulk upload runs in background and status poll returns completed results.

---

## Phase 6 — Polish and documentation

- **Backend:** Global exception handler (structured JSON), retry in vision and taggers (3 attempts, 1s/2s backoff), Supabase connection retry.
- **Frontend:** error.tsx (error boundary), Skeleton loading (HistoryGrid, SearchResults), empty states (HistoryGrid with icon), focus-visible for a11y.
- **Docs:** SETUP.md, DOCKER_SETUP.md, architecture (OVERVIEW, GRAPH_NODES, TAXONOMY, DATABASE, API, FRONTEND, PROMPTS), reports (PROJECT_SUMMARY, FEATURES, DECISIONS), curriculum (01–06), CHANGELOG, README update.

**Key files:** server (exception_handler), nodes/vision.py and taggers.py (retry loops), client.py (_conn retry), frontend error.tsx, Skeleton usage, globals.css (focus-visible), docs/ content.

**Verify:** Unhandled errors return 500 JSON; transient OpenAI/DB failures retry; error boundary catches client errors; loading and empty states render correctly.

---

## Progress diagram

See **docs/reports/PROGRESS.md** for the Mermaid flowchart: Backend Agent (setup → config → taxonomy → schemas → prompts → Supabase → nodes → graph → entry) → API Layer (FastAPI, Docker) → Frontend (setup → components → integration → search + bulk) → Documentation. All nodes marked [done]; “Currently working on” reflects Phase 6 complete.

---

## Changelog

See **CHANGELOG.md** at project root for the same phase list and brief feature summaries.

---

## Phase setup guides

Detailed step-by-step setup and verification for each phase are in **docs/plans/**:

- phase-0-setup.md (if present)
- phase-4-setup.md
- phase-5-setup.md
- phase-6-setup.md

Use these when bringing up a new environment or validating a phase locally.
