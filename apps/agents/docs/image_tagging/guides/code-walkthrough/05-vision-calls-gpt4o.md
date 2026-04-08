# Lab 05 — Vision Calls GPT-4o

**Estimated time:** 30 min  
**Difficulty:** Intermediate

After the preprocessor, the **vision_analyzer** node runs. It builds a **multimodal** message (system prompt + user message with text and image), calls the OpenAI API (GPT-4o), retries on failure, and parses the JSON response into `vision_description` and `vision_raw_tags`. This lab traces that code.

---

## Learning objectives

- See how the vision node builds a **data URI** and **messages** for the LLM.
- Understand **retry with exponential backoff** (1 s, 2 s) and failure handling.
- See how **_parse_vision_response** strips markdown code fences and extracts JSON.

---

## Prerequisites

- [04-preprocessor-runs.md](04-preprocessor-runs.md) — state now has `image_base64` (and possibly `metadata`) from the preprocessor.

---

## Step 1 — Check image_base64 and build data URI

The vision node is **async**. It reads `image_base64` from state and builds a **data URI** so the API can accept the image inline.

**Snippet (lines 35–46 in vision.py)**

```python
async def vision_analyzer(state: ImageTaggingState) -> dict[str, Any]:
    """Run GPT-4o vision on image_base64; return vision_description and vision_raw_tags."""
    image_base64 = state.get("image_base64")
    if not image_base64:
        return {
            "vision_description": "",
            "vision_raw_tags": {},
            "processing_status": "failed",
            "error": "Missing image_base64",
        }

    mime = "image/jpeg"
    data_uri = f"data:{mime};base64,{image_base64}"
```

**What is happening**

- **async def** — This node is async so we can use `await` for the LLM call. LangGraph supports both sync and async nodes.
- If `image_base64` is missing (e.g. preprocessor failed), we return empty vision fields and failed status so downstream nodes and the aggregator can handle it.
- **data_uri** — The OpenAI API accepts images as URLs. A **data URI** embeds the image as base64 in a string like `data:image/jpeg;base64,iVBORw0KGgo...`. The model receives the image without a separate upload.

**Source:** [backend/src/image_tagging/nodes/vision.py](../../backend/src/image_tagging/nodes/vision.py) (lines 35–46)

> **Glossary:** **data URI** — A URL scheme that embeds data (e.g. base64 image) inline instead of pointing to a separate resource.

---

## Step 2 — Build messages: system + human with image

The LLM is called with a list of **messages**. We use a **SystemMessage** (instructions) and a **HumanMessage** that contains both text and the image URL.

**Snippet (lines 48–56 in vision.py)**

```python
    llm = ChatOpenAI(model=OPENAI_MODEL, api_key=OPENAI_API_KEY)
    messages = [
        SystemMessage(content=VISION_ANALYZER_PROMPT),
        HumanMessage(
            content=[
                {"type": "text", "text": "Analyze this image and return the JSON object."},
                {"type": "image_url", "image_url": {"url": data_uri}},
            ]
        ),
    ]
```

**What is happening**

- **ChatOpenAI** — LangChain’s client for the OpenAI chat API. It uses `OPENAI_MODEL` (e.g. gpt-4o) and `OPENAI_API_KEY` from settings.
- **SystemMessage(content=VISION_ANALYZER_PROMPT)** — The system prompt defines the model’s role and the exact JSON shape to return (see Step 3). It is loaded from `prompts/system.py`.
- **HumanMessage(content=[...])** — For vision models, the user message can be a **list** of content blocks: one text block and one image block. The **image_url** block passes our data URI so the model “sees” the image.

> **State Tracker (input):** State has `image_base64`, `metadata` from preprocessor. No `vision_description` or `vision_raw_tags` yet.

---

## Step 3 — System prompt (what we ask for)

The system prompt tells the model to act as a visual product analyst and return **only** JSON with a fixed structure.

**Snippet (lines 3–15 in system.py)**

```python
VISION_ANALYZER_PROMPT = """You are a visual product analyst for a gift product company.
Analyze this product image and return a JSON object with the following structure.
Return ONLY valid JSON, no markdown, no explanation.

{
  "visual_description": "<2-3 sentence description>",
  "dominant_mood": "<overall feel>",
  "visible_subjects": ["<list of things you see>"],
  "color_observations": "<describe the color palette in detail>",
  "design_observations": "<describe patterns, textures, layout>",
  "seasonal_indicators": "<any holiday/seasonal cues>",
  "style_indicators": "<art style, aesthetic>",
  "text_present": "<any text or lettering visible>"
}"""
```

**What is happening**

- **visual_description** — This is the only field the **taggers** use. They get `vision_description` from state (mapped from this key in the parser). So the taggers work from text only; they do not receive the image again.
- The other fields (dominant_mood, visible_subjects, etc.) are stored in **vision_raw_tags** and can be shown in the UI or used later; they are not passed to the tagger nodes.

**Source:** [backend/src/image_tagging/prompts/system.py](../../backend/src/image_tagging/prompts/system.py) (lines 3–15)

> **Why This Way?** One vision call is expensive; we do it once and get both a description and extra structured fields. The eight taggers then run on text only (cheaper and simpler).

---

## Step 4 — Retry loop and ainvoke

We call the LLM up to 3 times. On exception we sleep 1 s, then 2 s, then give up and return failed state.

**Snippet (lines 59–74 in vision.py)**

```python
    for attempt in range(3):
        try:
            response = await llm.ainvoke(messages)
            text = response.content if isinstance(response.content, str) else str(response.content)
            break
        except Exception as e:
            if attempt < 2:
                await asyncio.sleep(1 * (2**attempt))
            else:
                return {
                    "vision_description": "",
                    "vision_raw_tags": {},
                    "processing_status": "failed",
                    "error": str(e),
                }
```

**What is happening**

- **llm.ainvoke(messages)** — Sends the messages to the OpenAI API and waits for the response. The response has a `.content` attribute (usually a string with the model’s reply). If the model returns a list (e.g. multiple parts), we coerce to string.
- On **success** we break out of the loop with `text` set.
- On **exception** (network error, API error, rate limit): if `attempt < 2` we sleep `1 * (2**attempt)` seconds (1 s, then 2 s) and retry. On the last attempt we return failed state with the error message so the graph can finish and the API can return a sensible response.

> **Error Path:** If all 3 attempts fail, we return failed state. The graph still runs the taggers (they will get empty `vision_description`), then validator, confidence, aggregator. The aggregator will see `processing_status` from state and can set the final status to failed.

> **Why This Way?** Transient network or API errors are common; a few retries with backoff often succeed without the user having to re-upload.

---

## Step 5 — Parse response and return

We pass the model’s text to **_parse_vision_response** to get a description string and a raw dict. We return those in state.

**Snippet (lines 15–32 in vision.py — _parse_vision_response)**

```python
def _parse_vision_response(text: str) -> tuple[str, dict]:
    """Extract JSON from response; return (visual_description, raw_dict)."""
    description = ""
    raw = {}
    stripped = text.strip()
    if stripped.startswith("```"):
        lines = stripped.split("\n")
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        stripped = "\n".join(lines)
    try:
        raw = json.loads(stripped)
        description = raw.get("visual_description", "")
    except json.JSONDecodeError:
        description = stripped
    return description, raw
```

**What is happening**

- **Strip code fences** — Many models wrap JSON in markdown code blocks (```json ... ```). If the text starts with ``` we remove the first and last line so we are left with the inner JSON.
- **json.loads(stripped)** — Parse the string as JSON. We put the result in `raw` and take `visual_description` from it for the taggers. If parsing fails we fall back to using the full stripped text as `description` and leave `raw` empty.
- **return description, raw** — The node then returns `vision_description=description` and `vision_raw_tags=raw`.

**Snippet (lines 76–80 in vision.py)**

```python
    description, raw = _parse_vision_response(text)
    return {
        "vision_description": description,
        "vision_raw_tags": raw,
    }
```

**Source:** [backend/src/image_tagging/nodes/vision.py](../../backend/src/image_tagging/nodes/vision.py) (lines 15–32, 76–80)

> **State Tracker (after vision):** State now has `vision_description` (2–3 sentences) and `vision_raw_tags` (dict with visual_description, dominant_mood, visible_subjects, etc.). `partial_tags` still empty; taggers will fill it.

> **I/O Snapshot:** **Input (to LLM):** SystemMessage + HumanMessage with text and image_url. **Output (from parser):** `description` = string, `raw` = dict with keys like visual_description, dominant_mood, visible_subjects, color_observations, etc.

> **Next:** The graph’s conditional edge runs **fan_out_to_taggers**; all 8 taggers are scheduled with this state. See [06-taggers-fan-out.md](06-taggers-fan-out.md).

---

## Lab summary

1. Vision node reads `image_base64`, builds a **data URI**, and creates **messages** (system prompt + user message with text and image).
2. It calls **ChatOpenAI.ainvoke** with **retry** (3 attempts, 1 s and 2 s backoff).
3. **_parse_vision_response** strips optional markdown fences and parses JSON; it returns **vision_description** (for taggers) and **vision_raw_tags** (full JSON for UI/storage).
4. The returned dict is merged into state; the next step is the **fan-out** to the 8 taggers.

---

## Exercises

1. Why do we strip markdown code fences before json.loads?
2. If the model returns valid JSON but without a key "visual_description", what is `vision_description` in state?
3. What happens to the graph if the vision node returns failed (e.g. after 3 API failures)?

---

## Next lab

Go to [06-taggers-fan-out.md](06-taggers-fan-out.md) to see how the conditional edge schedules all 8 taggers with the same state and how the reducer merges their `partial_tags`.
