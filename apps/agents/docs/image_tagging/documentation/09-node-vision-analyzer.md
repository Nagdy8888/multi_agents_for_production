# 09 — Node: Vision Analyzer

This document describes the **vision_analyzer** node: where it lives, how it builds the request (data URI, messages), the retry loop, `_parse_vision_response`, the expected vision JSON shape, and failure handling.

---

## File and function

**File:** `backend/src/image_tagging/nodes/vision.py`

**Signature:** `async def vision_analyzer(state: ImageTaggingState) -> dict[str, Any]`

**Type:** Async. Uses `ChatOpenAI(model, api_key).ainvoke(messages)`.

---

## Step-by-step behavior

1. **Read image_base64 from state.** If missing, return:
   - `{"vision_description": "", "vision_raw_tags": {}, "processing_status": "failed", "error": "Missing image_base64"}`.
2. **Build data URI:** `mime = "image/jpeg"`; `data_uri = f"data:{mime};base64,{image_base64}"`.
3. **Build messages:**
   - `SystemMessage(content=VISION_ANALYZER_PROMPT)` — see [15-prompts.md](15-prompts.md).
   - `HumanMessage(content=[{"type": "text", "text": "Analyze this image and return the JSON object."}, {"type": "image_url", "image_url": {"url": data_uri}}])`.
4. **Create LLM:** `ChatOpenAI(model=OPENAI_MODEL, api_key=OPENAI_API_KEY)` (from `settings`).
5. **Call with retry:** Up to 3 attempts. On each attempt call `response = await llm.ainvoke(messages)`. Extract `text = response.content` (string). On exception: if attempt < 2, sleep `1 * (2**attempt)` seconds (1s, then 2s); on last attempt return:
   - `{"vision_description": "", "vision_raw_tags": {}, "processing_status": "failed", "error": str(e)}`.
6. **Parse response:** `description, raw = _parse_vision_response(text)`.
7. **Return:** `{"vision_description": description, "vision_raw_tags": raw}`.

---

## _parse_vision_response(text)

**Signature:** `def _parse_vision_response(text: str) -> tuple[str, dict]`

**Returns:** `(visual_description: str, raw_dict: dict)`.

**Logic:**

- Strip leading/trailing whitespace from `text`.
- If `text` starts with ` ``` ` (markdown code fence), remove the first line and the last line if the last line is ` ``` `; join the middle lines to form the new `stripped` string.
- Try `json.loads(stripped)`:
  - On success: set `raw = parsed`, `description = raw.get("visual_description", "")`.
  - On JSONDecodeError: set `description = stripped`, `raw = {}`.
- Return `(description, raw)`.

So the **vision_description** is either the `visual_description` field from the parsed JSON or the whole stripped text if JSON parsing fails. **vision_raw_tags** is the full parsed object or an empty dict.

---

## Expected vision JSON shape (from prompt)

The system prompt asks the model to return a JSON object with at least:

| Field | Description |
|-------|-------------|
| visual_description | 2–3 sentence description of the image |
| dominant_mood | Overall feel |
| visible_subjects | List of things seen |
| color_observations | Color palette description |
| design_observations | Patterns, textures, layout |
| seasonal_indicators | Holiday/seasonal cues |
| style_indicators | Art style, aesthetic |
| text_present | Any text or lettering |

The node stores the **entire** parsed JSON in `vision_raw_tags`; only `visual_description` is promoted to the top-level state field `vision_description`, which is what the taggers use as input.

---

## Success return shape

```python
{
    "vision_description": str,   # From JSON or fallback to full text
    "vision_raw_tags": dict       # Full parsed JSON or {}
}
```

---

## Failure return shape

On missing image_base64 or on third retry failure:

```python
{
    "vision_description": "",
    "vision_raw_tags": {},
    "processing_status": "failed",
    "error": str
}
```

---

## Downstream

- **All 8 tagger nodes** read `state["vision_description"]` to build their prompts. They do not receive the image again; they only see the text description. So the quality of tagging depends on the quality of `vision_description` and the prompt (see [15-prompts.md](15-prompts.md)).

See [03-langgraph-pipeline.md](03-langgraph-pipeline.md) for the graph and [10-node-taggers-overview.md](10-node-taggers-overview.md) for how taggers use the description.
