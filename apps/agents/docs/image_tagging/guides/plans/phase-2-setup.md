# Phase 2: LangGraph Pipeline + Taxonomy + First Tagger — Setup Guide

## What This Phase Adds

- **Backend**
  - **Schemas:** `ImageTaggingState` (TypedDict with `partial_tags` reducer), Pydantic models: `TagResult`, `ValidatedTag`, `FlaggedTag`, `HierarchicalTag`, `TagRecord`, `TaggerOutput`.
  - **Taxonomy:** Single `TAXONOMY` dict (season, theme, objects, dominant_colors, design_elements, occasion, mood, product_type) and `get_flat_values(category)`.
  - **Prompts:** `VISION_ANALYZER_PROMPT` (spec 6.1), `build_tagger_prompt(description, category, allowed_values, instructions)` (spec 6.2).
  - **Nodes:** `image_preprocessor` (validate, resize max 1024, metadata, base64), `vision_analyzer` (GPT-4o → vision_description + vision_raw_tags), `tag_season` (generic `run_tagger` for season).
  - **Graph:** Linear pipeline: START → image_preprocessor → vision_analyzer → season_tagger → END; exported as `graph` from `image_tagging`.
  - **API:** `POST /api/analyze-image` builds initial state, runs `graph.ainvoke(initial_state)`, returns vision_description, vision_raw_tags, partial_tags, image_url, image_id. `GET /api/taxonomy` returns TAXONOMY.
- **Frontend**
  - Types: `PartialTagResult`, `AnalyzeImageResponse.partial_tags`.
  - `ConfidenceRing`: circular progress for 0–1 confidence.
  - `TagCategoryCard`: category name (color-coded left border), tags with confidence rings.
  - Dashboard: Pipeline tags section showing `partial_tags` (e.g. season) via TagCategoryCard.

## Prerequisites

- Phase 0 and Phase 1 complete
- `.env` with `OPENAI_API_KEY` set

## Files Changed / Added

| Path | Change |
|------|--------|
| `backend/src/image_tagging/schemas/states.py` | Added (ImageTaggingState) |
| `backend/src/image_tagging/schemas/models.py` | Added (TagResult, ValidatedTag, FlaggedTag, HierarchicalTag, TagRecord, TaggerOutput) |
| `backend/src/image_tagging/schemas/__init__.py` | Exports |
| `backend/src/image_tagging/taxonomy.py` | Added (TAXONOMY, get_flat_values) |
| `backend/src/image_tagging/prompts/system.py` | Added (VISION_ANALYZER_PROMPT) |
| `backend/src/image_tagging/prompts/tagger.py` | Added (build_tagger_prompt) |
| `backend/src/image_tagging/prompts/__init__.py` | Exports |
| `backend/src/image_tagging/nodes/preprocessor.py` | Added (image_preprocessor) |
| `backend/src/image_tagging/nodes/vision.py` | Added (vision_analyzer) |
| `backend/src/image_tagging/nodes/taggers.py` | Added (run_tagger, tag_season) |
| `backend/src/image_tagging/nodes/__init__.py` | Exports |
| `backend/src/image_tagging/graph_builder.py` | Implemented (build_graph) |
| `backend/src/image_tagging/image_tagging.py` | Export graph |
| `backend/src/server.py` | Use graph for analyze-image; add GET /api/taxonomy |
| `frontend/src/lib/types.ts` | PartialTagResult, partial_tags on response |
| `frontend/src/components/ConfidenceRing.tsx` | Added |
| `frontend/src/components/TagCategoryCard.tsx` | Added |
| `frontend/src/components/VisionResults.tsx` | Pipeline tags section with TagCategoryCard |

## Step-by-Step Setup (Docker)

From project root:

```bash
docker compose up --build
```

Open http://localhost:3000, upload an image, click Analyze. You should see the processing overlay, then the AI description, raw JSON, and a **Pipeline tags** section with at least **Season** (tags + confidence rings).

## How to Test

1. Open http://localhost:3000
2. Upload a seasonal image (e.g. Christmas gift bag)
3. Click **Analyze**
4. After completion: check **Pipeline tags** → **Season** card with tags (e.g. "Christmas") and confidence rings
5. `GET http://localhost:8000/api/taxonomy` returns the full taxonomy object

## Troubleshooting

| Issue | Fix |
|-------|-----|
| 500 Graph load error | Ensure all image_tagging imports resolve (schemas, taxonomy, prompts, nodes). |
| partial_tags empty | Check vision_analyzer output is passed to season_tagger; check tagger LLM response parsing (JSON, allowed values). |
| Preprocessor fails | Image must be valid JPG/PNG/WEBP; base64 must be in state. |
