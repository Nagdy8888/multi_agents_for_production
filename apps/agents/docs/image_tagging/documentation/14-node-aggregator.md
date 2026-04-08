# 14 — Node: Aggregator

This document describes the **aggregate_tags** node: how it builds TagRecord from validated_tags using _flat_list, _hierarchical_list, and _product_type_single; how it sets processing_status; and a complete example from validated_tags to TagRecord JSON.

---

## File and function

**File:** `backend/src/image_tagging/nodes/aggregator.py`

**Signature:** `async def aggregate_tags(state: ImageTaggingState) -> dict[str, Any]`

---

## Helpers

### _flat_list(validated, category)

- Gets validated.get(category) or [].
- Returns list of strings: for each item that is a dict with "value", append item["value"].
- Used for: season, theme, design_elements, occasion, mood.

### _hierarchical_list(validated, category)

- Gets validated.get(category) or [].
- For each item (dict): child = item["value"], parent = item.get("parent") or get_parent_for_child(category, child). If parent and child exist, append {"parent": parent, "child": child}.
- Returns list of such dicts.
- Used for: objects, dominant_colors.

### _product_type_single(validated)

- Gets validated.get("product_type") or [].
- Picks the **one** item with highest confidence: max(..., key=lambda t: t.get("confidence", 0)).
- If none, return None. Else child = best["value"], parent = best.get("parent") or get_parent_for_child("product_type", child). If parent and child, return {"parent": parent, "child": child}; else None.
- Used for: product_type (single HierarchicalTag in TagRecord).

---

## Main logic (aggregate_tags)

1. **Read state:** validated = state["validated_tags"] or {}; flagged = state["flagged_tags"] or []; needs_review = bool(flagged) or state.get("needs_review", False); image_id = state.get("image_id", ""); processed_at = datetime.now(timezone.utc).isoformat().
2. **Build TagRecord:**
   - season = _flat_list(validated, "season")
   - theme = _flat_list(validated, "theme")
   - objects = [HierarchicalTag(**o) for o in _hierarchical_list(validated, "objects")]
   - dominant_colors = [HierarchicalTag(**o) for o in _hierarchical_list(validated, "dominant_colors")]
   - design_elements = _flat_list(validated, "design_elements")
   - occasion = _flat_list(validated, "occasion")
   - mood = _flat_list(validated, "mood")
   - product_type = HierarchicalTag(**_product_type_single(validated)) if _product_type_single(validated) else None
   - needs_review = needs_review (from state)
   - processed_at = processed_at
3. **Processing status:** status = "needs_review" if needs_review else "complete". If state.get("error") then status = "failed".
4. **Return:** {"tag_record": record.model_dump(), "processing_status": status}.

---

## Example: validated_tags → TagRecord

**Input validated_tags (abbreviated):**

```json
{
  "season": [{ "value": "christmas", "confidence": 0.92, "parent": null }],
  "theme": [{ "value": "traditional", "confidence": 0.88, "parent": null }],
  "objects": [
    { "value": "gift_box", "confidence": 0.95, "parent": "objects_items" },
    { "value": "ribbon", "confidence": 0.9, "parent": "objects_items" }
  ],
  "dominant_colors": [
    { "value": "crimson", "confidence": 0.9, "parent": "red_family" },
    { "value": "gold_metallic", "confidence": 0.85, "parent": "metallic_family" }
  ],
  "design_elements": [{ "value": "foil_metallic", "confidence": 0.88, "parent": null }],
  "occasion": [{ "value": "gifting_general", "confidence": 0.9, "parent": null }],
  "mood": [{ "value": "joyful_fun", "confidence": 0.82, "parent": null }],
  "product_type": [{ "value": "gift_bag_medium", "confidence": 0.78, "parent": "gift_bag" }]
}
```

**Output tag_record:**

```json
{
  "image_id": "a1b2c3d4-...",
  "season": ["christmas"],
  "theme": ["traditional"],
  "objects": [
    { "parent": "objects_items", "child": "gift_box" },
    { "parent": "objects_items", "child": "ribbon" }
  ],
  "dominant_colors": [
    { "parent": "red_family", "child": "crimson" },
    { "parent": "metallic_family", "child": "gold_metallic" }
  ],
  "design_elements": ["foil_metallic"],
  "occasion": ["gifting_general"],
  "mood": ["joyful_fun"],
  "product_type": { "parent": "gift_bag", "child": "gift_bag_medium" },
  "needs_review": false,
  "processed_at": "2025-03-17T12:00:00.000000+00:00"
}
```

---

## Return shape

```python
{
    "tag_record": dict,           # TagRecord.model_dump()
    "processing_status": "complete" | "needs_review" | "failed"
}
```

See [05-agent-data-models.md](05-agent-data-models.md) for the TagRecord model and [16-database.md](16-database.md) for how tag_record and search_index are stored.
