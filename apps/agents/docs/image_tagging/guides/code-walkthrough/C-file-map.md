# Appendix C — File Map

Every main source file in the project with path, file type, one-line purpose, and which labs reference it.

---

## Backend

| Path | Type | Purpose | Labs |
|------|------|---------|------|
| backend/src/server.py | Python | FastAPI app: routes, CORS, static uploads, analyze_image, bulk, search, available_filters | 02, 11, 14, 16, 17 |
| backend/src/image_tagging/image_tagging.py | Python | Exports compiled graph = build_graph() | 02, 03 |
| backend/src/image_tagging/graph_builder.py | Python | StateGraph, nodes, edges, fan_out_to_taggers, compile | 03, 06 |
| backend/src/image_tagging/schemas/states.py | Python | ImageTaggingState TypedDict and reducer | 03 |
| backend/src/image_tagging/schemas/models.py | Python | TagResult, ValidatedTag, FlaggedTag, HierarchicalTag, TagRecord, TaggerOutput | 07, 08, 10 |
| backend/src/image_tagging/nodes/preprocessor.py | Python | image_preprocessor: decode, resize, encode | 04 |
| backend/src/image_tagging/nodes/vision.py | Python | vision_analyzer: multimodal message, retry, _parse_vision_response | 05 |
| backend/src/image_tagging/nodes/taggers.py | Python | run_tagger, _parse_tagger_response, 8 taggers, TAGGER_NODE_NAMES, ALL_TAGGERS | 06, 07 |
| backend/src/image_tagging/nodes/validator.py | Python | validate_tags, _validate_value, REQUIRED_CATEGORIES | 08 |
| backend/src/image_tagging/nodes/confidence.py | Python | filter_by_confidence | 09 |
| backend/src/image_tagging/nodes/aggregator.py | Python | aggregate_tags, _flat_list, _hierarchical_list, _product_type_single | 10 |
| backend/src/image_tagging/nodes/__init__.py | Python | Exports nodes and ALL_TAGGERS, TAGGER_NODE_NAMES | 03 |
| backend/src/image_tagging/taxonomy.py | Python | TAXONOMY, get_flat_values, get_parent_for_child | 07, 08, 19 |
| backend/src/image_tagging/configuration.py | Python | CONFIDENCE_THRESHOLD, overrides, MAX_COLORS, MAX_OBJECTS | 09, 19 |
| backend/src/image_tagging/settings.py | Python | OPENAI_API_KEY, OPENAI_MODEL (from env) | 05, 07, 20 |
| backend/src/image_tagging/prompts/system.py | Python | VISION_ANALYZER_PROMPT | 05, 20 |
| backend/src/image_tagging/prompts/tagger.py | Python | build_tagger_prompt | 07, 20 |
| backend/src/services/supabase/client.py | Python | SupabaseClient: build_search_index, upsert, get, list, search_filtered, get_available_filter_values | 11, 14, 18 |
| backend/src/services/supabase/migration.sql | SQL | CREATE TABLE image_tags, GIN indexes | 18 |
| backend/src/services/supabase/settings.py | Python | DATABASE_URI, SUPABASE_ENABLED | 18 |

---

## Frontend

| Path | Type | Purpose | Labs |
|------|------|---------|------|
| frontend/src/app/page.tsx | TSX | Home: handleAnalyze, ImageUploader, BulkUploader, DashboardResult, HistoryGrid | 01, 12 |
| frontend/src/app/search/page.tsx | TSX | Search: filters state, fetchSearchAndAvailable, FilterSidebar, SearchResults, DetailModal | 13 |
| frontend/src/app/layout.tsx | TSX | Root layout: ThemeProvider, Navbar, Toaster | — |
| frontend/src/app/error.tsx | TSX | Error boundary | — |
| frontend/src/components/ImageUploader.tsx | TSX | Single-file dropzone, onAnalyze, Analyze button | 01 |
| frontend/src/components/BulkUploader.tsx | TSX | Multi-file dropzone, POST bulk-upload, poll bulk-status | 16, 17 |
| frontend/src/components/DashboardResult.tsx | TSX | Result: image, vision, TagCategories, FlaggedTags, ConfidenceRing, JsonViewer | 12 |
| frontend/src/components/FilterSidebar.tsx | TSX | Taxonomy fetch, filter toggles, availableValues | 13 |
| frontend/src/components/SearchResults.tsx | TSX | Grid of search rows, onSelectItem | 15 |
| frontend/src/components/DetailModal.tsx | TSX | Modal with full tag_record for selected row | 15 |
| frontend/src/components/HistoryGrid.tsx | TSX | GET tag-images, grid of recent | — |
| frontend/src/components/TagCategories.tsx | TSX | Renders tags by category | 12 |
| frontend/src/components/FlaggedTags.tsx | TSX | Renders flagged list | 12 |
| frontend/src/components/ConfidenceRing.tsx | TSX | Confidence ring UI | 12 |
| frontend/src/components/JsonViewer.tsx | TSX | Collapsible JSON | 12 |
| frontend/src/lib/constants.ts | TS | API_BASE_URL | 01 |
| frontend/src/lib/types.ts | TS | AnalyzeImageResponse, TagImageRow, TagRecord, etc. | 01, 12 |
| frontend/src/lib/formatTag.ts | TS | formatTagLabel | — |

---

## Other

| Path | Type | Purpose | Labs |
|------|------|---------|------|
| backend/Dockerfile | Dockerfile | Python image, pip install, uvicorn | — |
| frontend/Dockerfile | Dockerfile | Multi-stage Next.js build, standalone | — |
| docker-compose.yml | YAML | backend + frontend services, ports, env | — |

Use this map to jump from a lab to the exact file and to see which labs touch each file.
