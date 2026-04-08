# LangGraph nodes

The pipeline is defined in `backend/src/image_tagging/graph_builder.py`. Each node reads/writes the shared `ImageTaggingState`.

## Node list

| Node | File | Purpose | Main inputs | Main outputs |
|------|------|---------|-------------|--------------|
| **image_preprocessor** | `nodes/preprocessor.py` | Validate image, resize, ensure base64 | `image_base64` (raw) | `image_base64` (resized), `image_url` |
| **vision_analyzer** | `nodes/vision.py` | Single GPT-4o vision call | `image_base64` | `vision_description`, `vision_raw_tags` |
| **tag_season** … **tag_product** | `nodes/taggers.py` | One LLM call per category (8 total) | `vision_description`, taxonomy | `partial_tags` (appended) |
| **tag_validator** | `nodes/validator.py` | Validate partial_tags against taxonomy | `partial_tags` | `validated_tags`, `flagged_tags` |
| **confidence_filter** | `nodes/confidence.py` | Apply thresholds, move low-confidence to flagged | `validated_tags` | Updated `validated_tags`, `flagged_tags`, `needs_review` |
| **tag_aggregator** | `nodes/aggregator.py` | Build final TagRecord, set status | `validated_tags` | `tag_record`, `processing_status` |

## Flow

1. **Preprocessor** — Validates and resizes image; passes base64 to vision.
2. **Vision** — One vision model call; returns description and raw JSON (mood, subjects, colors, etc.).
3. **Taggers** — Fan-out from vision: eight parallel nodes (season, theme, objects, dominant_colors, design_elements, occasion, mood, product_type). Each uses `vision_description` and taxonomy to produce tags + confidence; results are appended to `partial_tags`.
4. **Validator** — Runs when all eight categories are present in `partial_tags`. Checks each value against taxonomy (flat or hierarchical); valid → `validated_tags`, invalid → `flagged_tags`.
5. **Confidence filter** — Per-category thresholds (and overrides); tags below threshold move to `flagged_tags`; sets `needs_review` if too many low-confidence.
6. **Aggregator** — Builds a single `tag_record` (season, theme, objects, dominant_colors, design_elements, occasion, mood, product_type, needs_review, processed_at) and sets `processing_status` (complete / needs_review / failed).

## State shape

See `backend/src/image_tagging/schemas/states.py`: `ImageTaggingState` is a TypedDict with `image_id`, `image_url`, `image_base64`, `vision_description`, `vision_raw_tags`, `partial_tags`, `validated_tags`, `flagged_tags`, `tag_record`, `needs_review`, `processing_status`.
