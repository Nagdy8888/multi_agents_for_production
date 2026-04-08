# Prompts

LLM prompts live under `backend/src/image_tagging/prompts/`. Used by the vision node and the tagger nodes.

## Vision (system prompt)

**File:** `prompts/system.py` — `VISION_ANALYZER_PROMPT`.

- Role: visual product analyst.
- Asks for a JSON object with: `visual_description`, `dominant_mood`, `visible_subjects`, `color_observations`, `design_observations`, `seasonal_indicators`, `style_indicators`, `text_present`.
- The vision node sends one image (base64 data URI) and asks the model to analyze and return that JSON. Output is parsed and stored as `vision_description` and `vision_raw_tags`.

## Taggers

**File:** `prompts/tagger.py` — `build_tagger_prompt(description, category, allowed_values, instructions=None)`.

- Inputs: product description (from vision), category name, allowed values from taxonomy, optional category-specific instructions (e.g. max items for colors/objects).
- Output: user message that instructs the model to return JSON with `tags` (list), `confidence_scores` (dict), and optionally `reasoning`.
- Each tagger node (season, theme, objects, etc.) calls `build_tagger_prompt` with the right category and allowed list; the model’s response is parsed in `nodes/taggers.py` via `_parse_tagger_response` and filtered to allowed values and confidence threshold.

## Tuning

- To change vision output shape, edit `VISION_ANALYZER_PROMPT` and the parser in `nodes/vision.py` (`_parse_vision_response`).
- To change tagger output or constraints, edit `build_tagger_prompt` and the tagger instructions (e.g. max_tags) in `nodes/taggers.py`. Confidence and validation thresholds are in `configuration.py` and applied in `nodes/confidence.py` and `nodes/validator.py`.
