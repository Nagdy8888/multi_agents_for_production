# Phase 6: Polish, Docker, and Documentation — Setup Guide

## What This Phase Adds

- **Docker (verified):** Existing backend and frontend Dockerfiles and docker-compose.yml confirmed; .dockerignore in both. Backend: python:3.11-slim, uvicorn. Frontend: node:20-alpine multi-stage, standalone Next.js.
- **Error handling:** Global exception handler in server.py returns structured JSON (detail, type). Vision and tagger nodes retry up to 2 times with exponential backoff (1s, 2s) on OpenAI errors. Supabase client _conn() retries 3 times with 1s delay; app continues without DB if connection fails.
- **UI polish:** app/error.tsx (Next.js error boundary) with Try again / Go home. Skeleton components for HistoryGrid and SearchResults loading. Empty state for HistoryGrid with icon and short copy. focus-visible styles in globals.css for links and buttons.
- **Documentation:** Quickstart SETUP.md and DOCKER_SETUP.md; architecture OVERVIEW, GRAPH_NODES, TAXONOMY, DATABASE, API, FRONTEND, PROMPTS; reports PROJECT_SUMMARY, FEATURES, DECISIONS; curriculum 01–06 and README; CHANGELOG.md; root README with features and architecture diagram.

## Prerequisites

- Phases 0–5 complete.

## Files Changed / Added

| Path | Change |
|------|--------|
| backend/src/server.py | JSONResponse import, global_exception_handler |
| backend/src/image_tagging/nodes/vision.py | asyncio, retry loop (3 attempts, backoff) |
| backend/src/image_tagging/nodes/taggers.py | asyncio, retry loop in run_tagger |
| backend/src/services/supabase/client.py | time import, _conn retry logic |
| frontend/src/app/error.tsx | Added (error boundary) |
| frontend/src/app/globals.css | focus-visible for a, button |
| frontend/src/components/HistoryGrid.tsx | Skeleton, ImageIcon empty state |
| frontend/src/components/SearchResults.tsx | Skeleton for loading |
| docs/quickstart/SETUP.md | Added |
| docs/quickstart/DOCKER_SETUP.md | Added |
| docs/architecture/*.md | OVERVIEW, GRAPH_NODES, TAXONOMY, DATABASE, API, FRONTEND, PROMPTS |
| docs/architecture/README.md | Updated |
| docs/reports/PROJECT_SUMMARY.md, FEATURES.md, DECISIONS.md | Added |
| docs/curriculum/01–06 + README | Added/updated |
| CHANGELOG.md | Added |
| README.md | Updated (features, diagram, doc links) |
| docs/reports/PROGRESS.md | Documentation nodes [done], Phase 6 complete |
| docs/plans/phase-6-setup.md | This file |

## Verification

1. `docker compose up --build` — both services build and run.
2. Full flow: upload image → analyze → see result and (if DB set) “Saved” and history; search with filters; bulk upload and progress.
3. Trigger an error (e.g. invalid route or throw in component) — error UI or error boundary appears instead of blank screen.
