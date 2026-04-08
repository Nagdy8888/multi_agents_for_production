# 10 — Node: Taggers Overview

This document describes the generic **run_tagger** flow, how **partial_tags** is accumulated via the reducer, the **ALL_TAGGERS** and **TAGGER_NODE_NAMES** mapping, and filtering/capping logic.

---

## File and entry points

**File:** `backend/src/image_tagging/nodes/taggers.py`

- **Generic:** `async def run_tagger(state, category, instructions=None, max_tags=None) -> dict[str, Any]`
- **Concrete nodes:** `tag_season`, `tag_theme`, `tag_objects`, `tag_colors`, `tag_design`, `tag_occasion`, `tag_mood`, `tag_product` — each calls `run_tagger` with category-specific arguments. See [11-node-taggers-per-category.md](11-node-taggers-per-category.md).

---

## run_tagger — step-by-step

1. **Read vision_description from state.** `description = state.get("vision_description") or ""`.
2. **Get allowed values.** `allowed = get_flat_values(category)` from taxonomy; if category not in TAXONOMY or allowed is empty, return `{"partial_tags": [TagResult(category=category, tags=[], confidence_scores={}).model_dump()]}`.
3. **Build prompt.** `prompt = build_tagger_prompt(description, category, allowed, instructions)` — see [15-prompts.md](15-prompts.md).
4. **Create LLM.** `ChatOpenAI(model=OPENAI_MODEL, api_key=OPENAI_API_KEY)`.
5. **Call with retry.** Up to 3 attempts: `response = await llm.ainvoke([{"role": "user", "content": prompt}])`, `text = response.content`. On exception: if attempt < 2, sleep `1 * (2**attempt)`; on last attempt return `{"partial_tags": [TagResult(category=category, tags=[], confidence_scores={}).model_dump()]}`. If after loop `text is None`, same empty return.
6. **Parse.** `out = _parse_tagger_response(text)` → `TaggerOutput(tags, confidence_scores, reasoning)` or None. If None, return same empty partial_tags as above.
7. **Filter to allowed and confidence > 0.5.** `tags = [t for t in out.tags if t in allowed]`; `confidence_scores = {k: v for k, v in out.confidence_scores.items() if k in allowed and v > 0.5}`; then `tags = [t for t in tags if confidence_scores.get(t, 0) > 0.5]`.
8. **Optional cap (max_tags).** If `max_tags` is not None and `len(tags) > max_tags`: sort tags by confidence descending, take first `max_tags`, and restrict `confidence_scores` to those tags.
9. **Build result.** `result = TagResult(category=category, tags=tags, confidence_scores=confidence_scores)`.
10. **Return.** `{"partial_tags": [result.model_dump()]}`.

---

## _parse_tagger_response(text)

- Strips markdown code fence (same pattern as vision: if text starts with ```, drop first and last line if last is ```).
- `json.loads(stripped)` → expect keys `tags`, `confidence_scores`, `reasoning`; return `TaggerOutput(tags=data.get("tags", []), confidence_scores=data.get("confidence_scores", {}), reasoning=data.get("reasoning", ""))`.
- On any exception return None.

---

## How partial_tags is accumulated (reducer)

- Each tagger returns **one** dict in `partial_tags`: `[TagResult(...).model_dump()]`.
- State defines `partial_tags: Annotated[list, operator.add]`. LangGraph merges by **concatenating** the list returned by the node with the current state’s `partial_tags`.
- Because vision_analyzer fans out to all 8 taggers in parallel, each tagger runs with the same state (including `partial_tags: []` at the start of the fan-out). Each adds one element. After all 8 finish, the state has `partial_tags` = list of 8 elements (one per category). So the **reducer** is what allows all 8 outputs to be combined instead of overwriting each other.

---

## ALL_TAGGERS and TAGGER_NODE_NAMES

**TAGGER_NODE_NAMES** (order used by fan_out_to_taggers):

```python
[
    "season_tagger", "theme_tagger", "objects_tagger", "color_tagger",
    "design_tagger", "occasion_tagger", "mood_tagger", "product_tagger",
]
```

**ALL_TAGGERS** (node name → async function):

| Node name | Function |
|-----------|----------|
| season_tagger | tag_season |
| theme_tagger | tag_theme |
| objects_tagger | tag_objects |
| color_tagger | tag_colors |
| design_tagger | tag_design |
| occasion_tagger | tag_occasion |
| mood_tagger | tag_mood |
| product_tagger | tag_product |

`graph_builder.py` adds nodes with `builder.add_node(name, fn)` for each `(name, fn)` in `ALL_TAGGERS.items()`, and `fan_out_to_taggers` returns `[Send(name, state) for name in TAGGER_NODE_NAMES]`, so the names must match.

---

## Filtering and capping summary

- **Allowed only:** Tags and confidence_scores are restricted to values in `get_flat_values(category)`.
- **Confidence > 0.5:** Any tag with score ≤ 0.5 is dropped (and not included in confidence_scores).
- **max_tags:** If set (e.g. MAX_OBJECTS=10, MAX_COLORS=5, product_type=1), tags are sorted by confidence descending and only the top `max_tags` are kept; confidence_scores is then restricted to those tags.

See [11-node-taggers-per-category.md](11-node-taggers-per-category.md) for per-category instructions and max_tags, and [04-agent-state.md](04-agent-state.md) for the reducer.
