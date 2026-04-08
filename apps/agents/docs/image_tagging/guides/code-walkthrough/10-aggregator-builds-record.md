# Lab 10 — Aggregator Builds Record

**Estimated time:** 25 min  
**Difficulty:** Intermediate

The **tag_aggregator** node builds the final **TagRecord** from **validated_tags**. Flat categories become lists of strings; hierarchical categories (objects, dominant_colors) become lists of **HierarchicalTag**; product_type becomes a single **HierarchicalTag** (best by confidence). The node also sets **processing_status** (complete, needs_review, or failed). This lab traces the aggregator code.

---

## Learning objectives

- See **_flat_list** and **_hierarchical_list** and how they map validated_tags to TagRecord fields.
- See **_product_type_single**: pick the single best product_type by confidence.
- See how **processing_status** is set from needs_review and state.error.

---

## Prerequisites

- [09-confidence-filters.md](09-confidence-filters.md) — state has validated_tags (trimmed), flagged_tags, and needs_review.

---

## Step 1 — Helpers: _flat_list and _hierarchical_list

Validated_tags is a dict: category → list of {value, confidence, parent?}. We need to turn that into the shape expected by TagRecord: flat categories are list[str], hierarchical are list of {parent, child}.

**Snippet (lines 10–26 in aggregator.py)**

```python
def _flat_list(validated: dict, category: str) -> list[str]:
    items = validated.get(category) or []
    return [t.get("value") for t in items if isinstance(t, dict) and t.get("value")]


def _hierarchical_list(validated: dict, category: str) -> list[dict]:
    items = validated.get(category) or []
    out = []
    for t in items:
        if not isinstance(t, dict):
            continue
        child = t.get("value")
        parent = t.get("parent") or get_parent_for_child(category, child)
        if parent and child:
            out.append({"parent": parent, "child": child})
    return out
```

**What is happening**

- **_flat_list** — For season, theme, design_elements, occasion, mood we just collect the "value" from each validated tag into a list of strings.
- **_hierarchical_list** — For objects and dominant_colors each tag has value (child) and optionally parent (from the validator). If parent is missing we call get_parent_for_child. We append {"parent": ..., "child": ...} to the list. The TagRecord then wraps these as HierarchicalTag (parent, child).

**Source:** [backend/src/image_tagging/nodes/aggregator.py](../../backend/src/image_tagging/nodes/aggregator.py) (lines 10–26)

---

## Step 2 — _product_type_single: one best by confidence

Product_type is stored as a **single** HierarchicalTag (the best by confidence), not a list.

**Snippet (lines 29–44 in aggregator.py)**

```python
def _product_type_single(validated: dict) -> dict | None:
    items = validated.get("product_type") or []
    if not items:
        return None
    best = max(
        (t for t in items if isinstance(t, dict) and t.get("value")),
        key=lambda t: t.get("confidence", 0),
        default=None,
    )
    if not best:
        return None
    child = best.get("value")
    parent = best.get("parent") or get_parent_for_child("product_type", child)
    if parent and child:
        return {"parent": parent, "child": child}
    return None
```

**What is happening**

- We take the product_type list from validated_tags. We pick the tag with **maximum confidence**. We form one {parent, child} dict (or None if empty). TagRecord.product_type is then one HierarchicalTag or None.

**Source:** [backend/src/image_tagging/nodes/aggregator.py](../../backend/src/image_tagging/nodes/aggregator.py) (lines 29–44)

---

## Step 3 — Build TagRecord and processing_status

We read validated_tags, flagged, needs_review, image_id from state; set processed_at; build the TagRecord; then set processing_status and return.

**Snippet (lines 47–76 in aggregator.py)**

```python
async def aggregate_tags(state: ImageTaggingState) -> dict[str, Any]:
    """Build TagRecord from validated_tags; set processing_status."""
    validated = state.get("validated_tags") or {}
    flagged = state.get("flagged_tags") or []
    needs_review = bool(flagged) or state.get("needs_review", False)
    image_id = state.get("image_id", "")
    processed_at = datetime.now(timezone.utc).isoformat()

    record = TagRecord(
        image_id=image_id,
        season=_flat_list(validated, "season"),
        theme=_flat_list(validated, "theme"),
        objects=[HierarchicalTag(**o) for o in _hierarchical_list(validated, "objects")],
        dominant_colors=[HierarchicalTag(**o) for o in _hierarchical_list(validated, "dominant_colors")],
        design_elements=_flat_list(validated, "design_elements"),
        occasion=_flat_list(validated, "occasion"),
        mood=_flat_list(validated, "mood"),
        product_type=HierarchicalTag(**_product_type_single(validated)) if _product_type_single(validated) else None,
        needs_review=needs_review,
        processed_at=processed_at,
    )

    status = "needs_review" if needs_review else "complete"
    if state.get("error"):
        status = "failed"

    return {
        "tag_record": record.model_dump(),
        "processing_status": status,
    }
```

**What is happening**

- **needs_review** — True if there are any flagged tags or if the confidence filter set needs_review. We store it on the TagRecord so the API and UI can show "needs review."
- **processed_at** — UTC timestamp when the aggregator ran.
- **TagRecord** — Pydantic model with all category fields (flat lists, hierarchical lists, single product_type), needs_review, and processed_at. We call model_dump() so we return a plain dict for state and API.
- **status** — "needs_review" if needs_review else "complete". If state has an "error" (e.g. from preprocessor or vision failure), we force status to "failed".
- We return **tag_record** and **processing_status**. The graph ends here; the server will read these from the final state and use them in the response and for DB persistence (Lab 11).

> **State Tracker (after aggregator):** tag_record and processing_status are set. This is the final state returned by graph.ainvoke to the server.

> **Next:** Back in server.py (Lab 11): the server saves tag_record to the DB (if enabled) and builds the JSON response for the frontend.

---

## Lab summary

1. **_flat_list** and **_hierarchical_list** map validated_tags to TagRecord’s flat and hierarchical fields. **_product_type_single** picks the best product_type by confidence and returns one {parent, child} or None.
2. **aggregate_tags** builds TagRecord with image_id, all category fields, needs_review, processed_at; then sets **processing_status** to needs_review/complete/failed and returns tag_record and processing_status.

---

## Exercises

1. Why is product_type a single HierarchicalTag instead of a list?
2. What does the API response contain from the graph’s final state? (Hint: Lab 11.)
3. If the preprocessor set state["error"], what is processing_status?

---

## Next lab

Go to [11-server-saves-and-responds.md](11-server-saves-and-responds.md) to see how the server uses the graph result to upsert to the database and build the JSON response.
