# 01 — Project Overview

This document describes what the Image Analysis Agent does, its features, tech stack, repository structure, and points to all other documentation files.

---

## What the project does

**Image Analysis Agent** is an AI-powered image tagging system for product imagery. Users upload images (single or bulk); the system runs them through a **LangGraph** pipeline that uses **OpenAI GPT-4o** for vision analysis and category-specific tagging. Results are structured into eight tag categories (season, theme, objects, dominant colors, design elements, occasion, mood, product type), validated against a taxonomy, filtered by confidence, and optionally stored in **Supabase**. A **Next.js** web UI supports upload, result display, history, search with cascading filters, and bulk upload with progress.

---

## Features

| Feature | Description |
|--------|--------------|
| **Single image analysis** | Upload one image → preprocessor (resize, validate) → vision analyzer (GPT-4o) → 8 parallel category taggers → validator → confidence filter → aggregator → tag record; optional save to DB. |
| **Bulk upload** | Multiple images uploaded at once; processed in the background with progress bar and per-file status; results appear in history. |
| **Search** | Filter tagged images by any combination of tags; cascading filters (only show values that exist in current result set); grid results and detail modal with full tag record. |
| **History** | Browse recently tagged images; thumbnails, sample tags, status; refresh on demand. |

---

## Tech stack

| Layer | Technologies |
|-------|--------------|
| **Frontend** | Next.js 16, React 19, TypeScript, Tailwind CSS, shadcn/ui, react-dropzone, framer-motion, lucide-react, next-themes, sonner |
| **Backend** | FastAPI, LangGraph, langchain-openai (GPT-4o), Pydantic |
| **Agent** | LangGraph StateGraph, parallel taggers via Send API, custom state reducer for partial_tags |
| **Database** | Supabase (PostgreSQL), optional; JSONB + GIN indexes for tag_record and search_index |
| **Deployment** | Docker, Docker Compose |

---

## Repository structure

```
image-analysis-agent/
├── backend/
│   ├── src/
│   │   ├── server.py                 # FastAPI app, CORS, routes, static /uploads
│   │   ├── image_tagging/            # LangGraph agent package
│   │   │   ├── image_tagging.py      # Compiled graph export
│   │   │   ├── graph_builder.py      # Graph definition, nodes, edges, Send
│   │   │   ├── taxonomy.py           # Tag categories and allowed values
│   │   │   ├── configuration.py     # Thresholds, overrides, MAX_OBJECTS, etc.
│   │   │   ├── settings.py          # Env: OPENAI_API_KEY, OPENAI_MODEL, DATABASE_URI
│   │   │   ├── nodes/
│   │   │   │   ├── preprocessor.py   # Validate, resize, base64
│   │   │   │   ├── vision.py        # GPT-4o vision analyzer
│   │   │   │   ├── taggers.py       # 8 category taggers (run_tagger + wrappers)
│   │   │   │   ├── validator.py     # Taxonomy validation, flagged_tags
│   │   │   │   ├── confidence.py   # Threshold filter, needs_review
│   │   │   │   └── aggregator.py   # TagRecord from validated_tags
│   │   │   ├── prompts/
│   │   │   │   ├── system.py        # VISION_ANALYZER_PROMPT
│   │   │   │   └── tagger.py       # build_tagger_prompt
│   │   │   ├── schemas/
│   │   │   │   ├── states.py       # ImageTaggingState
│   │   │   │   └── models.py       # TagResult, ValidatedTag, FlaggedTag, TagRecord, etc.
│   │   │   └── tools/              # Placeholder
│   │   └── services/
│   │       └── supabase/            # settings, client, migration
│   │           ├── settings.py     # DATABASE_URI, SUPABASE_ENABLED
│   │           ├── client.py      # SupabaseClient, upsert, search, filters
│   │           └── migration.sql   # image_tags table, GIN indexes
│   ├── uploads/                     # Runtime: saved images
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .dockerignore
│
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── page.tsx             # Home: upload, result, bulk, history
│   │   │   ├── search/page.tsx      # Search UI
│   │   │   ├── layout.tsx
│   │   │   ├── error.tsx
│   │   │   └── globals.css
│   │   ├── components/
│   │   │   ├── ImageUploader.tsx
│   │   │   ├── BulkUploader.tsx
│   │   │   ├── DashboardResult.tsx
│   │   │   ├── FilterSidebar.tsx
│   │   │   ├── SearchResults.tsx
│   │   │   ├── DetailModal.tsx
│   │   │   ├── HistoryGrid.tsx
│   │   │   ├── TagCategories.tsx
│   │   │   ├── FlaggedTags.tsx
│   │   │   └── ui/                 # shadcn
│   │   └── lib/
│   │       ├── types.ts
│   │       ├── formatTag.ts
│   │       └── constants (API_BASE_URL, etc.)
│   ├── public/
│   ├── package.json
│   ├── Dockerfile
│   └── .dockerignore
│
├── docs/                            # Existing docs (unchanged)
│   ├── quickstart/
│   ├── architecture/
│   ├── plans/
│   ├── curriculum/
│   ├── reports/
│   └── errors/
│
├── documentation/                   # This folder: exhaustive reference
│   ├── 01-project-overview.md       # This file
│   ├── 02-architecture.md
│   ├── 03-langgraph-pipeline.md
│   ├── 04-agent-state.md
│   ├── 05-agent-data-models.md
│   ├── 06-taxonomy-complete-reference.md
│   ├── 07-configuration-and-settings.md
│   ├── 08-node-preprocessor.md
│   ├── 09-node-vision-analyzer.md
│   ├── 10-node-taggers-overview.md
│   ├── 11-node-taggers-per-category.md
│   ├── 12-node-validator.md
│   ├── 13-node-confidence-filter.md
│   ├── 14-node-aggregator.md
│   ├── 15-prompts.md
│   ├── 16-database.md
│   ├── 17-api-reference.md
│   ├── 18-frontend.md
│   ├── 19-docker-and-deployment.md
│   └── 20-development-phases.md
│
├── docker-compose.yml
├── .env                              # OPENAI_API_KEY, DATABASE_URI
├── CHANGELOG.md
├── FOLDER_STRUCTURE.md
└── README.md
```

---

## Documentation index (this folder)

| # | File | Description |
|---|------|-------------|
| 01 | [01-project-overview.md](01-project-overview.md) | This file: project summary, features, stack, repo tree, doc index. |
| 02 | [02-architecture.md](02-architecture.md) | High-level system diagram, request lifecycles (single, bulk, search), sequence and component interaction. |
| 03 | [03-langgraph-pipeline.md](03-langgraph-pipeline.md) | Agent graph Mermaid, graph_builder.py walkthrough, Send API, state merge. |
| 04 | [04-agent-state.md](04-agent-state.md) | ImageTaggingState: every field, reducer (partial_tags), lifecycle table, example state. |
| 05 | [05-agent-data-models.md](05-agent-data-models.md) | Pydantic models: TagResult, ValidatedTag, FlaggedTag, HierarchicalTag, TagRecord, TaggerOutput; who creates/consumes; examples. |
| 06 | [06-taxonomy-complete-reference.md](06-taxonomy-complete-reference.md) | Every allowed value per category; flat vs hierarchical; get_flat_values, get_parent_for_child. |
| 07 | [07-configuration-and-settings.md](07-configuration-and-settings.md) | settings.py (env), configuration.py (thresholds, overrides, MAX_*). |
| 08 | [08-node-preprocessor.md](08-node-preprocessor.md) | image_preprocessor: steps, constants, errors. |
| 09 | [09-node-vision-analyzer.md](09-node-vision-analyzer.md) | vision_analyzer: messages, retry, _parse_vision_response, vision JSON shape. |
| 10 | [10-node-taggers-overview.md](10-node-taggers-overview.md) | run_tagger flow, ALL_TAGGERS, reducer, filtering, capping. |
| 11 | [11-node-taggers-per-category.md](11-node-taggers-per-category.md) | All 8 taggers: instructions, max_tags, examples. |
| 12 | [12-node-validator.md](12-node-validator.md) | validate_tags: REQUIRED_CATEGORIES, flat/hierarchical validation, _validate_value. |
| 13 | [13-node-confidence-filter.md](13-node-confidence-filter.md) | filter_by_confidence: thresholds, overrides, needs_review. |
| 14 | [14-node-aggregator.md](14-node-aggregator.md) | aggregate_tags: _flat_list, _hierarchical_list, _product_type_single, TagRecord, processing_status. |
| 15 | [15-prompts.md](15-prompts.md) | VISION_ANALYZER_PROMPT and build_tagger_prompt; example prompts; tuning tips. |
| 16 | [16-database.md](16-database.md) | migration.sql, SupabaseClient, build_search_index, search_images_filtered, get_available_filter_values. |
| 17 | [17-api-reference.md](17-api-reference.md) | Every endpoint: method, path, params, body, response, status codes. |
| 18 | [18-frontend.md](18-frontend.md) | Pages, layout, components, data flow, TypeScript types. |
| 19 | [19-docker-and-deployment.md](19-docker-and-deployment.md) | Dockerfiles, docker-compose, build/run, production env. |
| 20 | [20-development-phases.md](20-development-phases.md) | Phases 0–6 summary, key files, verification, changelog. |

---

## Quick start

From the repository root:

```bash
docker compose up --build
```

- **App:** http://localhost:3000  
- **API:** http://localhost:8000  

Create a `.env` at the project root with `OPENAI_API_KEY` (required) and optionally `DATABASE_URI` for persistence and search.

See [19-docker-and-deployment.md](19-docker-and-deployment.md) and the existing [docs/quickstart](docs/quickstart) for details.
