# 12 — Node: Validator

This document describes the **validate_tags** node: REQUIRED_CATEGORIES gate, flat vs hierarchical validation, `_validate_value`, and how it produces validated_tags and flagged_tags. It also includes an example walkthrough.

---

## File and function

**File:** `backend/src/image_tagging/nodes/validator.py`

**Signature:** `async def validate_tags(state: ImageTaggingState) -> dict[str, Any]`

---

## Constants

| Name | Value | Purpose |
|------|-------|---------|
| REQUIRED_CATEGORIES | {"season", "theme", "objects", "dominant_colors", "design_elements", "occasion", "mood", "product_type"} | Set of 8 categories that must appear in partial_tags for validation to run. |
| HIERARCHICAL_CATEGORIES | {"objects", "dominant_colors", "product_type"} | Categories whose values have a parent; validation uses get_parent_for_child and sets parent on ValidatedTag. |

---

## Gate logic

- **partial** = `state.get("partial_tags") or []`.
- **categories_seen** = set of `p.get("category")` for each dict in partial that has a category.
- If **categories_seen != REQUIRED_CATEGORIES** (i.e. not all 8 categories present), return **{}** (no state update). So if any tagger failed or returned empty, the validator does not run and does not overwrite validated_tags or flagged_tags.

---

## Per-tag validation: _validate_value

**Signature:** `def _validate_value(category: str, value: str, confidence: float) -> tuple[ValidatedTag | None, FlaggedTag | None]`

**Returns:** Either `(ValidatedTag, None)` for valid, or `(None, FlaggedTag)` for invalid. Never both valid and flagged for the same input.

**Logic:**

- If **category in HIERARCHICAL_CATEGORIES:**
  - `parent = get_parent_for_child(category, value)`.
  - If parent is None → value not in taxonomy → return `(None, FlaggedTag(category=category, value=value, confidence=confidence, reason="invalid_taxonomy_value"))`.
  - Else return `(ValidatedTag(value=value, confidence=confidence, parent=parent), None)`.
- Else (flat category):
  - If `_is_valid_flat(category, value)` is True → return `(ValidatedTag(value=value, confidence=confidence, parent=None), None)`.
  - Else return `(None, FlaggedTag(..., reason="invalid_taxonomy_value"))`.

**_is_valid_flat(category, value):** `TAXONOMY.get(category)` must be a list and `value in that list`.

**_is_valid_hierarchical:** Not used directly; hierarchical path uses `get_parent_for_child` only.

---

## Main loop (validate_tags)

- **validated:** dict category → list of ValidatedTag dicts (model_dump()).
- **flagged:** list of FlaggedTag dicts. Initialize from `state.get("flagged_tags") or []` so any existing flagged tags are carried forward (e.g. from a previous node; in practice only confidence_filter appends after this).
- For each **item** in partial_tags (each TagResult dict):
  - category = item["category"], tags = item["tags"], scores = item["confidence_scores"].
  - For each **value** in tags: conf = scores.get(value, 0.5). Call _validate_value(category, value, conf). If ValidatedTag, append to validated[category]. If FlaggedTag, append to flagged.
- Return `{"validated_tags": validated, "flagged_tags": flagged}`.

---

## Example walkthrough

**partial_tags** (one element): `{"category": "product_type", "tags": ["gift_bag_medium", "unknown_type"], "confidence_scores": {"gift_bag_medium": 0.78, "unknown_type": 0.6}}`.

- product_type is hierarchical. For "gift_bag_medium": get_parent_for_child("product_type", "gift_bag_medium") → "gift_bag". So ValidatedTag(value="gift_bag_medium", confidence=0.78, parent="gift_bag"), add to validated["product_type"].
- For "unknown_type": get_parent_for_child("product_type", "unknown_type") → None. So FlaggedTag(category="product_type", value="unknown_type", confidence=0.6, reason="invalid_taxonomy_value"), add to flagged.

Result: validated_tags has product_type with one ValidatedTag; flagged_tags has one FlaggedTag.

---

## Output shape

```python
{
    "validated_tags": {
        "season": [{"value": str, "confidence": float, "parent": None | str}, ...],
        "theme": [...],
        "objects": [...],
        "dominant_colors": [...],
        "design_elements": [...],
        "occasion": [...],
        "mood": [...],
        "product_type": [...]
    },
    "flagged_tags": [
        {"category": str, "value": str, "confidence": float, "reason": "invalid_taxonomy_value"},
        ...
    ]
}
```

Validator only adds reason "invalid_taxonomy_value". The confidence filter adds "low_confidence" — see [13-node-confidence-filter.md](13-node-confidence-filter.md).
