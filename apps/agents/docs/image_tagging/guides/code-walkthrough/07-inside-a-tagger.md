# Lab 07 — Inside a Tagger

**Estimated time:** 35 min  
**Difficulty:** Intermediate

Each of the 8 taggers is a thin wrapper around **run_tagger**. run_tagger reads `vision_description` from state, gets the allowed values for the category from the taxonomy, builds a prompt, calls the LLM (with retry), parses the JSON, filters to allowed values and confidence > 0.5, optionally caps the number of tags, and returns one TagResult in `partial_tags`. This lab walks through run_tagger step by step and lists all 8 taggers.

---

## Learning objectives

- Trace **run_tagger**: get allowed values, build prompt, call LLM, parse, filter, cap, return.
- See how **build_tagger_prompt** injects the category, allowed values, and image description.
- See how **_parse_tagger_response** and the filter/cap logic produce a single TagResult.
- Know the category, instructions, and max_tags for each of the 8 taggers.

---

## Prerequisites

- [06-taggers-fan-out.md](06-taggers-fan-out.md) — the runtime has scheduled one of the 8 taggers with state that includes `vision_description`.

---

## Step 1 — Read vision_description and get allowed values

run_tagger needs the image description (from the vision node) and the list of allowed tag values for this category (from the taxonomy).

**Snippet (lines 37–46 in taggers.py)**

```python
async def run_tagger(
    state: ImageTaggingState,
    category: str,
    instructions: str | None = None,
    max_tags: int | None = None,
) -> dict[str, Any]:
    """Generic tagger: vision_description + category → TagResult appended to partial_tags."""
    description = state.get("vision_description") or ""
    allowed = get_flat_values(category) if category in TAXONOMY else []
    if not allowed:
        return {"partial_tags": [TagResult(category=category, tags=[], confidence_scores={}).model_dump()]}
```

**What is happening**

- **description** — The 2–3 sentence description from the vision node. All taggers use **only** this text; they do not receive the image. That keeps token usage lower and the pipeline simple.
- **get_flat_values(category)** — From the taxonomy module. For flat categories (e.g. season, theme) it returns the list of allowed strings. For hierarchical categories (objects, dominant_colors, product_type) it returns a flat list of all **child** values. If the category is not in TAXONOMY or the list is empty, we return an empty TagResult for this category so the reducer still gets one element per category.

**Source:** [backend/src/image_tagging/nodes/taggers.py](../../backend/src/image_tagging/nodes/taggers.py) (lines 37–46)

> **Glossary:** **taxonomy** — The single source of truth for allowed tag values per category. Used to build the prompt and to filter the LLM output.

---

## Step 2 — Build the prompt

The prompt tells the model which category to tag, lists the allowed values, gives the image description, and specifies the JSON shape and confidence scale.

**Snippet (lines 4–29 in tagger.py)**

```python
def build_tagger_prompt(
    description: str,
    category: str,
    allowed_values: list[str],
    instructions: str | None = None,
) -> str:
    """Build system prompt for a category tagger node."""
    values_str = ", ".join(allowed_values)
    base = f"""You are a product tagging assistant. Based on the image description below,
select the most applicable tags for the "{category}" category.

Rules:
- Only use values from the provided allowed_values list
- Return tags as a JSON object with this exact structure:
  {{"tags": ["value1", "value2"], "confidence_scores": {{"value1": 0.95, "value2": 0.72}}, "reasoning": "..."}}
- Include a tag only if confidence > 0.5
- For confidence: 0.9+ = clearly visible, 0.7–0.9 = likely present, 0.5–0.7 = possibly present
- Return ONLY valid JSON, no markdown

Allowed values: {values_str}

Image description:
{description}"""
    if instructions:
        base += f"\n\nAdditional instructions: {instructions}"
    return base
```

**What is happening**

- **values_str** — Comma-separated list of allowed values so the model knows exactly what it can return.
- **base** — Role, category name, rules (only allowed values, JSON structure, confidence > 0.5, confidence scale), allowed values, and the image description. The `{{` and `}}` in the f-string are escaped braces so the output contains literal `{` and `}`.
- **Additional instructions** — Optional per-category guidance (e.g. "Select all aesthetic themes that apply" for theme, "Select the single most likely product type" for product_type).

**Source:** [backend/src/image_tagging/prompts/tagger.py](../../backend/src/image_tagging/prompts/tagger.py) (lines 4–29)

> **I/O Snapshot:** **Input:** description (string), category (e.g. "season"), allowed_values (list), instructions (optional). **Output:** A single string (the full prompt) that will be sent as the user message to the LLM.

---

## Step 3 — Call LLM with retry

We call the same ChatOpenAI model (text-only this time) with the prompt as the user message. We retry up to 3 times with the same backoff as the vision node.

**Snippet (lines 47–62 in taggers.py)**

```python
    prompt = build_tagger_prompt(description, category, allowed, instructions)
    llm = ChatOpenAI(model=OPENAI_MODEL, api_key=OPENAI_API_KEY)
    text = None
    for attempt in range(3):
        try:
            response = await llm.ainvoke([{"role": "user", "content": prompt}])
            text = response.content if isinstance(response.content, str) else str(response.content)
            break
        except Exception:
            if attempt < 2:
                await asyncio.sleep(1 * (2**attempt))
            else:
                return {"partial_tags": [TagResult(category=category, tags=[], confidence_scores={}).model_dump()]}
    if text is None:
        return {"partial_tags": [TagResult(category=category, tags=[], confidence_scores={}).model_dump()]}
```

**What is happening**

- **llm.ainvoke([{"role": "user", "content": prompt}])** — Single user message (no system message here; the prompt is self-contained). The model returns text (we expect JSON).
- On success we set `text` and break. On the last failure we return an empty TagResult for this category. If we never got a response (`text is None`), we also return empty.

**Source:** [backend/src/image_tagging/nodes/taggers.py](../../backend/src/image_tagging/nodes/taggers.py) (lines 47–62)

> **Error Path:** Parse failure or LLM failure → we return one TagResult with empty tags so the pipeline continues and the validator still sees 8 categories (one empty).

---

## Step 4 — Parse and filter to allowed and confidence > 0.5

We parse the model’s text into tags and confidence_scores, then keep only values that are in the allowed list and have confidence greater than 0.5.

**Snippet (_parse_tagger_response, lines 16–34; then filter, lines 64–71 in taggers.py)**

```python
def _parse_tagger_response(text: str) -> TaggerOutput | None:
    """Parse LLM response into TaggerOutput."""
    stripped = text.strip()
    if stripped.startswith("```"):
        lines = stripped.split("\n")
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        stripped = "\n".join(lines)
    try:
        data = json.loads(stripped)
        return TaggerOutput(
            tags=data.get("tags", []),
            confidence_scores=data.get("confidence_scores", {}),
            reasoning=data.get("reasoning", ""),
        )
    except Exception:
        return None
```

```python
    out = _parse_tagger_response(text)
    if not out:
        return {"partial_tags": [TagResult(category=category, tags=[], confidence_scores={}).model_dump()]}

    # Filter to allowed only and confidence > 0.5
    tags = [t for t in out.tags if t in allowed]
    confidence_scores = {k: v for k, v in out.confidence_scores.items() if k in allowed and v > 0.5}
    tags = [t for t in tags if confidence_scores.get(t, 0) > 0.5]
```

**What is happening**

- **_parse_tagger_response** — Same idea as vision: strip markdown fences, json.loads, build TaggerOutput(tags, confidence_scores, reasoning). On any exception return None; then we return empty partial_tags for this category.
- **Filter tags** — Keep only tags that appear in `allowed` (taxonomy). Then keep only confidence_scores for keys that are in allowed and have value > 0.5. Then restrict tags to those that still have a confidence_scores entry above 0.5. So we never pass invalid or low-confidence tags to the validator.

**Source:** [backend/src/image_tagging/nodes/taggers.py](../../backend/src/image_tagging/nodes/taggers.py) (lines 16–34, 64–71)

---

## Step 5 — Optional cap by max_tags

Some categories limit how many tags we keep (e.g. 5 colors, 10 objects, 1 product type). We sort by confidence descending and take the top max_tags.

**Snippet (lines 73–77 in taggers.py)**

```python
    # Optional cap (e.g. MAX_COLORS=5, MAX_OBJECTS=10)
    if max_tags is not None and len(tags) > max_tags:
        sorted_tags = sorted(tags, key=lambda t: confidence_scores.get(t, 0), reverse=True)
        tags = sorted_tags[:max_tags]
        confidence_scores = {k: v for k, v in confidence_scores.items() if k in tags}
```

**What is happening**

- If we have more tags than max_tags, we sort by confidence (highest first) and keep only the first max_tags. Then we restrict confidence_scores to those tags so the returned TagResult is consistent.

**Source:** [backend/src/image_tagging/nodes/taggers.py](../../backend/src/image_tagging/nodes/taggers.py) (lines 73–77)

---

## Step 6 — Build TagResult and return

We wrap the final tags and confidence_scores in a TagResult (Pydantic model), serialize it to a dict with model_dump(), and return it as the single element in partial_tags.

**Snippet (lines 79–80 in taggers.py)**

```python
    result = TagResult(category=category, tags=tags, confidence_scores=confidence_scores)
    return {"partial_tags": [result.model_dump()]}
```

**What is happening**

- **TagResult** — Pydantic model with category, tags (list of strings), confidence_scores (dict str → float). model_dump() produces a plain dict for JSON/state.
- We return a dict with one key, **partial_tags**, whose value is a **list of one** element. The reducer in the graph will append this list to the current partial_tags, so after all 8 taggers we have 8 elements.

> **Next:** The validator (Lab 08) will read partial_tags (all 8 items), validate each tag against the taxonomy, and produce validated_tags and flagged_tags.

---

## All 8 taggers: category, instructions, max_tags

| Tagger function   | Category         | Instructions (summary)                          | max_tags   |
|-------------------|------------------|-------------------------------------------------|------------|
| tag_season        | season           | (default)                                       | None       |
| tag_theme         | theme            | Select all aesthetic themes that apply          | None       |
| tag_objects       | objects          | Hierarchical; return child values               | MAX_OBJECTS (10) |
| tag_colors        | dominant_colors  | Up to 5; specific shade names                   | MAX_COLORS (5)  |
| tag_design        | design_elements  | Patterns, textures, layout, typography         | None       |
| tag_occasion      | occasion         | Occasions or use cases                          | None       |
| tag_mood          | mood             | Moods or tones                                 | None       |
| tag_product       | product_type     | Single most likely; one child value             | 1          |

**Snippet (example: tag_product, lines 134–139)**

```python
async def tag_product(state: ImageTaggingState) -> dict[str, Any]:
    return await run_tagger(
        state, "product_type",
        instructions="Select the single most likely product type. Return one specific child value (e.g. gift_bag_medium, wrapping_paper_roll).",
        max_tags=1,
    )
```

Each tagger is a thin wrapper: it just calls run_tagger with the right category, optional instructions, and optional max_tags.

---

## Lab summary

1. **run_tagger** gets vision_description and allowed values from the taxonomy; if no allowed values, returns empty TagResult.
2. **build_tagger_prompt** builds a single prompt with category, allowed values, description, and optional instructions.
3. We **call the LLM** (text-only) with retry; on failure we return empty TagResult.
4. **_parse_tagger_response** strips fences and parses JSON to TaggerOutput; we **filter** to allowed values and confidence > 0.5, then **cap** by max_tags if set.
5. We return **{"partial_tags": [TagResult.model_dump()]}**; the reducer appends this to state. All 8 taggers follow the same flow with different category/instructions/max_tags.

---

## Exercises

1. Why do we filter to allowed values again in code when the prompt already says "only use values from the list"?
2. What is the type of the single element in the list we return in partial_tags (e.g. dict keys)?
3. For product_type, why is max_tags=1?

---

## Next lab

Go to [08-validator-checks-tags.md](08-validator-checks-tags.md) to see how the validator reads partial_tags, checks every value against the taxonomy (flat vs hierarchical), and produces validated_tags and flagged_tags.
