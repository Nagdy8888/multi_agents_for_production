# 13 — Node: Confidence Filter

This document describes the **filter_by_confidence** node: how it uses CONFIDENCE_THRESHOLD and CATEGORY_CONFIDENCE_OVERRIDES, how it moves low-confidence tags to flagged_tags, and how it sets needs_review. It includes an example comparing season (0.60) vs product_type (0.80).

---

## File and function

**File:** `backend/src/image_tagging/nodes/confidence.py`

**Signature:** `async def filter_by_confidence(state: ImageTaggingState) -> dict[str, Any]`

---

## Configuration read

From `configuration.py` (see [07-configuration-and-settings.md](07-configuration-and-settings.md)):

- **CONFIDENCE_THRESHOLD** = 0.65 (default for categories without an override).
- **CATEGORY_CONFIDENCE_OVERRIDES** = {"product_type": 0.80, "season": 0.60}.
- **NEEDS_REVIEW_THRESHOLD** = 3.

---

## Step-by-step behavior

1. **Read state:** validated = state["validated_tags"] or {}; flagged = list(state["flagged_tags"] or []); needs_review = False; category_flag_count = {}.
2. **New validated:** new_validated = {}.
3. **For each category** in validated:
   - **Threshold:** threshold = CATEGORY_CONFIDENCE_OVERRIDES.get(category, CONFIDENCE_THRESHOLD). So product_type uses 0.80, season uses 0.60, all others use 0.65.
   - **For each tag** in that category’s list (each a dict with "value", "confidence", "parent"):
     - If confidence **>=** threshold: append to kept list for this category.
     - Else: append to flagged a FlaggedTag(category=category, value=tag["value"], confidence=tag["confidence"], reason="low_confidence"); increment category_flag_count[category].
   - new_validated[category] = kept.
4. **needs_review:** If any category has category_flag_count[category] >= NEEDS_REVIEW_THRESHOLD (3), set needs_review = True. Also if len(flagged) > 0, set needs_review = True.
5. **Return:** {"validated_tags": new_validated, "flagged_tags": flagged, "needs_review": needs_review}.

---

## Example: tag at 0.62

- **Season (threshold 0.60):** 0.62 >= 0.60 → tag **stays** in validated_tags.
- **Product_type (threshold 0.80):** 0.62 < 0.80 → tag **moved** to flagged_tags with reason "low_confidence".
- **Theme (threshold 0.65):** 0.62 < 0.65 → tag **moved** to flagged_tags with reason "low_confidence".

So the same numeric confidence can be kept or flagged depending on the category’s threshold.

---

## Output shape

```python
{
    "validated_tags": dict,  # Same structure as input but with low-confidence tags removed
    "flagged_tags": list,    # Previous flagged + new FlaggedTag dicts (reason "low_confidence")
    "needs_review": bool     # True if any flagged or any category had >= 3 flags
}
```

---

## Downstream

- **tag_aggregator** reads validated_tags (only kept tags), flagged_tags, and needs_review to build TagRecord and set processing_status ("needs_review" if needs_review else "complete"). See [14-node-aggregator.md](14-node-aggregator.md).
