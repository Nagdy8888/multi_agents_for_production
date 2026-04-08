# Lab 08 — Validator Checks Tags

**Estimated time:** 25 min  
**Difficulty:** Intermediate

After all 8 taggers have run, state contains **partial_tags** (a list of 8 TagResults). The **tag_validator** node checks every tag value against the taxonomy: flat categories use a simple list membership check; hierarchical categories use **get_parent_for_child** to validate and to attach the parent. Valid tags become **ValidatedTag** entries in **validated_tags**; invalid ones become **FlaggedTag** entries in **flagged_tags**. This lab traces the validator code.

---

## Learning objectives

- See the **REQUIRED_CATEGORIES** gate: validator runs only when all 8 categories are present.
- Understand **_validate_value**: flat vs hierarchical, ValidatedTag vs FlaggedTag, reason "invalid_taxonomy_value".
- See how validated_tags and flagged_tags are built and returned.

---

## Prerequisites

- [07-inside-a-tagger.md](07-inside-a-tagger.md) — state has partial_tags with 8 elements (one per category).

---

## Step 1 — REQUIRED_CATEGORIES gate

The validator only runs when partial_tags contains exactly the 8 expected categories. If one is missing (e.g. a tagger failed and returned empty), the validator returns an empty dict and does not overwrite state.

**Snippet (lines 8–12, 41–46 in validator.py)**

```python
REQUIRED_CATEGORIES = {
    "season", "theme", "objects", "dominant_colors", "design_elements",
    "occasion", "mood", "product_type",
}
HIERARCHICAL_CATEGORIES = {"objects", "dominant_colors", "product_type"}
# ...
    partial = state.get("partial_tags") or []
    categories_seen = {p.get("category") for p in partial if isinstance(p, dict) and p.get("category")}
    if categories_seen != REQUIRED_CATEGORIES:
        return {}
```

**What is happening**

- **categories_seen** — The set of category names that appear in partial_tags. We expect exactly the 8 categories.
- If **categories_seen != REQUIRED_CATEGORIES** (e.g. one tagger failed and we have only 7, or a category name is wrong), we **return {}**. Returning an empty dict means we do not update state; the graph continues but validated_tags and flagged_tags are not set by this node. Downstream nodes (confidence, aggregator) would then see missing validated_tags. So this gate avoids writing incomplete validation results.

**Source:** [backend/src/image_tagging/nodes/validator.py](../../backend/src/image_tagging/nodes/validator.py) (lines 8–12, 41–46)

> **Why This Way?** If we validated anyway with 7 categories, we would overwrite state with incomplete validated_tags and the aggregator might build an incomplete TagRecord. Returning {} keeps the previous state (if any) and lets the pipeline still finish; the aggregator can handle missing validated_tags.

---

## Step 2 — _validate_value: flat vs hierarchical

For each tag value we decide: is it valid? If the category is hierarchical we also need the **parent** for the aggregator. _validate_value returns either (ValidatedTag, None) or (None, FlaggedTag).

**Snippet (lines 15–38 in validator.py)**

```python
def _is_valid_flat(category: str, value: str) -> bool:
    allowed = TAXONOMY.get(category)
    if isinstance(allowed, list):
        return value in allowed
    return False


def _is_valid_hierarchical(category: str, value: str) -> bool:
    return get_parent_for_child(category, value) is not None


def _validate_value(category: str, value: str, confidence: float) -> tuple[ValidatedTag | None, FlaggedTag | None]:
    if category in HIERARCHICAL_CATEGORIES:
        parent = get_parent_for_child(category, value)
        if parent is None:
            return None, FlaggedTag(
                category=category, value=value, confidence=confidence, reason="invalid_taxonomy_value"
            )
        return ValidatedTag(value=value, confidence=confidence, parent=parent), None
    if _is_valid_flat(category, value):
        return ValidatedTag(value=value, confidence=confidence, parent=None), None
    return None, FlaggedTag(
        category=category, value=value, confidence=confidence, reason="invalid_taxonomy_value"
    )
```

**What is happening**

- **Flat categories** (season, theme, design_elements, occasion, mood): TAXONOMY[category] is a list. We check `value in allowed`. If valid we return ValidatedTag with parent=None. If invalid we return FlaggedTag with reason "invalid_taxonomy_value".
- **Hierarchical categories** (objects, dominant_colors, product_type): TAXONOMY[category] is a dict (parent → list of children). **get_parent_for_child(category, value)** looks up which parent (if any) has this value as a child. If parent is None the value is not in the taxonomy → FlaggedTag. If parent is set we return ValidatedTag with that parent so the aggregator can build HierarchicalTag(parent, child).

**Source:** [backend/src/image_tagging/nodes/validator.py](../../backend/src/image_tagging/nodes/validator.py) (lines 15–38)

> **Glossary:** **ValidatedTag** — A tag that passed taxonomy validation; has value, confidence, and optional parent (for hierarchical). **FlaggedTag** — A tag that failed validation or was later dropped by confidence; has category, value, confidence, and reason (e.g. invalid_taxonomy_value).

---

## Step 3 — Loop partial_tags and fill validated_tags and flagged_tags

We iterate every item in partial_tags, then every value in that item’s tags list, and call _validate_value. We append to validated[category] or to flagged.

**Snippet (lines 48–70 in validator.py)**

```python
    validated: dict[str, list[dict]] = {}
    flagged: list[dict] = list(state.get("flagged_tags") or [])

    for item in partial:
        if not isinstance(item, dict):
            continue
        category = item.get("category")
        tags = item.get("tags") or []
        scores = item.get("confidence_scores") or {}
        if category not in validated:
            validated[category] = []
        for value in tags:
            conf = scores.get(value, 0.5)
            vt, ft = _validate_value(category, value, conf)
            if vt is not None:
                validated[category].append(vt.model_dump())
            if ft is not None:
                flagged.append(ft.model_dump())

    return {
        "validated_tags": validated,
        "flagged_tags": flagged,
    }
```

**What is happening**

- **flagged** — We start from any existing flagged_tags in state (e.g. from a previous run or from the confidence filter in a different design). Here the validator is the first to write flagged_tags, so we copy state.get("flagged_tags") or [].
- For each **item** in partial (each TagResult dict), we read category, tags list, and confidence_scores. For each **value** in tags we get its confidence (default 0.5) and call _validate_value. If we get a ValidatedTag we append its model_dump() to validated[category]. If we get a FlaggedTag we append to flagged.
- We return **validated_tags** (dict category → list of ValidatedTag dicts) and **flagged_tags** (list of FlaggedTag dicts). LangGraph merges these into state.

> **State Tracker (after validator):** validated_tags = { "season": [...], "theme": [...], ... } (each value a dict with value, confidence, parent?). flagged_tags = [ ... ] (list of dicts with category, value, confidence, reason). partial_tags unchanged.

> **Next:** The confidence filter (Lab 09) will read validated_tags, apply per-category thresholds, move low-confidence tags to flagged_tags, and set needs_review.

---

## Lab summary

1. **REQUIRED_CATEGORIES** gate: if partial_tags does not contain all 8 categories, return {} and do not update state.
2. **_validate_value**: for hierarchical categories use get_parent_for_child; for flat use _is_valid_flat. Return ValidatedTag (with parent when hierarchical) or FlaggedTag with reason "invalid_taxonomy_value".
3. Loop partial_tags and each tag value; fill **validated_tags** (dict) and **flagged_tags** (list). Return both for LangGraph to merge into state.

---

## Exercises

1. Why do we need get_parent_for_child for hierarchical categories instead of just checking "value in some list"?
2. What would happen if we did not have the REQUIRED_CATEGORIES check and partial_tags had only 7 categories?
3. Can the same tag value appear in both validated_tags and flagged_tags for the same category?

---

## Next lab

Go to [09-confidence-filters.md](09-confidence-filters.md) to see how the confidence filter applies per-category thresholds, moves low-confidence tags to flagged_tags, and sets needs_review.
