# Phase 3: Full Parallel Tagging Pipeline — Setup Guide

## What This Phase Adds

- **Backend**
  - **Configuration:** `configuration.py` with CONFIDENCE_THRESHOLD (0.65), NEEDS_REVIEW_THRESHOLD (3), MAX_COLORS (5), MAX_OBJECTS (10), CATEGORY_CONFIDENCE_OVERRIDES (product_type 0.80, season 0.60).
  - **Taxonomy:** `get_parent_for_child(category, child)` for aggregator hierarchical mapping.
  - **Taggers:** All 8 taggers (theme, objects, colors, design, occasion, mood, product) plus `ALL_TAGGERS` and `TAGGER_NODE_NAMES`; `run_tagger` supports `max_tags` for colors/objects/product.
  - **Validator:** `nodes/validator.py` — validates partial_tags against taxonomy, fills validated_tags and flagged_tags; runs only when all 8 categories present in partial_tags.
  - **Confidence filter:** `nodes/confidence.py` — applies per-category threshold, moves low-confidence tags to flagged_tags, sets needs_review.
  - **Aggregator:** `nodes/aggregator.py` — builds TagRecord from validated_tags (flat and hierarchical), sets processing_status and needs_review.
  - **Graph:** Fan-out from vision_analyzer via `add_conditional_edges` returning list of `Send(node_name, state)` to all 8 taggers; each tagger → tag_validator → confidence_filter → tag_aggregator → END.
  - **API:** POST /api/analyze-image response includes `tags_by_category`, `tag_record`, `flagged_tags`, `processing_status`.
- **Frontend**
  - Types: TagWithConfidence, TagRecord, FlaggedTag, tags_by_category, processing_status.
  - **TagChip:** Confidence-colored chip (green/blue/amber/red) with tooltip.
  - **TagCategories:** Grid of 8 TagCategoryCards from tags_by_category.
  - **FlaggedTags:** Collapsible section for tags needing review (reason + confidence).
  - **ProcessingOverlay:** 6 steps (Uploading, Preprocessing, Analyzing with AI, Tagging 8 categories, Validating, Complete).
  - Dashboard: VisionResults, TagCategories, FlaggedTags (if any), JsonViewer (tag_record or vision_raw_tags), Analyze New Image.

## Prerequisites

- Phase 0, 1, 2 complete
- `.env` with OPENAI_API_KEY

## Files Changed / Added

| Path | Change |
|------|--------|
| `backend/src/image_tagging/configuration.py` | Implemented (thresholds, overrides) |
| `backend/src/image_tagging/taxonomy.py` | get_parent_for_child() |
| `backend/src/image_tagging/nodes/taggers.py` | tag_theme, tag_objects, tag_colors, tag_design, tag_occasion, tag_mood, tag_product; ALL_TAGGERS, TAGGER_NODE_NAMES; run_tagger max_tags |
| `backend/src/image_tagging/nodes/validator.py` | Added |
| `backend/src/image_tagging/nodes/confidence.py` | Added |
| `backend/src/image_tagging/nodes/aggregator.py` | Added |
| `backend/src/image_tagging/nodes/__init__.py` | Exports for all nodes |
| `backend/src/image_tagging/schemas/states.py` | needs_review field |
| `backend/src/image_tagging/graph_builder.py` | Send fan-out, 8 taggers, validator, confidence_filter, aggregator |
| `backend/src/server.py` | tags_by_category, tag_record, flagged_tags, processing_status in response |
| `frontend/src/lib/types.ts` | TagWithConfidence, TagRecord, FlaggedTag, tags_by_category, processing_status |
| `frontend/src/components/TagChip.tsx` | Added |
| `frontend/src/components/TagCategories.tsx` | Added |
| `frontend/src/components/FlaggedTags.tsx` | Added |
| `frontend/src/components/ProcessingOverlay.tsx` | 6 steps |
| `frontend/src/components/VisionResults.tsx` | Hide pipeline tags when tags_by_category present |
| `frontend/src/app/page.tsx` | TagCategories, FlaggedTags, step timer, JsonViewer tag_record |

## Step-by-Step Setup (Docker)

From project root:

```bash
docker compose up --build
```

Open http://localhost:3000, upload an image, click Analyze. Overlay shows 6 steps; after completion you see vision results, an 8-category tag grid, flagged tags (if any), and raw JSON (tag_record).

## How to Test

1. Upload a gift/product image and click **Analyze**.
2. Confirm overlay steps advance (or jump to Complete when done).
3. Check **Tags by category**: all 8 categories (Season, Theme, Objects, Dominant Colors, Design Elements, Occasion, Mood, Product Type) with tags and confidence.
4. If any tag is below threshold or invalid, **Flagged tags** section appears.
5. **View Raw JSON** shows tag_record (or vision_raw_tags).

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Validator never runs / validated_tags empty | Ensure all 8 taggers are wired and partial_tags has 8 items (categories_seen == REQUIRED_CATEGORIES). |
| product_type or objects wrong shape | Aggregator uses get_parent_for_child; taxonomy must have correct parent/child. |
| Send / conditional_edges error | Use add_conditional_edges("vision_analyzer", fan_out_to_taggers) with no path_map when returning list of Send. |
