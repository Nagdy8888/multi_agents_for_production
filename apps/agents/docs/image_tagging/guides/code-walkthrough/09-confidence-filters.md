# Lab 09 — Confidence Filters

**Estimated time:** 20 min  
**Difficulty:** Beginner

The **confidence_filter** node reads **validated_tags** from state and applies a per-category **threshold**. Tags with confidence below the threshold are moved to **flagged_tags** with reason "low_confidence". The node also sets **needs_review** when there are many flagged tags or any flags at all. This lab traces the confidence filter code and the configuration it uses.

---

## Learning objectives

- See how **CONFIDENCE_THRESHOLD** (default) and **CATEGORY_CONFIDENCE_OVERRIDES** are applied per category.
- Understand how tags below threshold are moved to flagged_tags with reason "low_confidence".
- See how **needs_review** is set (NEEDS_REVIEW_THRESHOLD and presence of any flagged tags).

---

## Prerequisites

- [08-validator-checks-tags.md](08-validator-checks-tags.md) — state has validated_tags and flagged_tags from the validator.

---

## Step 1 — Configuration: thresholds and overrides

The default confidence threshold is 0.65. Some categories use a different threshold via overrides.

**Snippet (configuration.py, lines 1–14)**

```python
"""Runtime configuration (spec section 7)."""
from .settings import OPENAI_MODEL

CONFIDENCE_THRESHOLD = 0.65
NEEDS_REVIEW_THRESHOLD = 3
MAX_COLORS = 5
MAX_OBJECTS = 10
# ...
CATEGORY_CONFIDENCE_OVERRIDES = {
    "product_type": 0.80,
    "season": 0.60,
}
```

**What is happening**

- **CONFIDENCE_THRESHOLD** — Default cutoff: tags with confidence < 0.65 are moved to flagged. Used for any category not in overrides.
- **CATEGORY_CONFIDENCE_OVERRIDES** — product_type uses 0.80 (stricter); season uses 0.60 (looser). So product_type tags must be more confident to pass; season tags can pass with slightly lower confidence.
- **NEEDS_REVIEW_THRESHOLD** — If any single category has this many (or more) tags moved to flagged, we set needs_review. Set to 3.

**Source:** [backend/src/image_tagging/configuration.py](../../backend/src/image_tagging/configuration.py) (lines 1–14)

---

## Step 2 — Loop validated_tags and apply threshold

For each category we get the threshold (override or default). For each tag we keep it in validated or append a FlaggedTag to flagged.

**Snippet (lines 14–40 in confidence.py)**

```python
async def filter_by_confidence(state: ImageTaggingState) -> dict[str, Any]:
    """Filter validated_tags by threshold; move low-confidence to flagged_tags."""
    validated = state.get("validated_tags") or {}
    flagged = list(state.get("flagged_tags") or [])
    needs_review = False
    category_flag_count: dict[str, int] = {}
    new_validated: dict[str, list[dict]] = {}

    for category, tag_list in validated.items():
        threshold = CATEGORY_CONFIDENCE_OVERRIDES.get(category, CONFIDENCE_THRESHOLD)
        kept = []
        for t in tag_list:
            if not isinstance(t, dict):
                continue
            conf = t.get("confidence", 0)
            if conf >= threshold:
                kept.append(t)
            else:
                flagged.append(
                    FlaggedTag(
                        category=category,
                        value=t.get("value", ""),
                        confidence=conf,
                        reason="low_confidence",
                    ).model_dump()
                )
                category_flag_count[category] = category_flag_count.get(category, 0) + 1
        new_validated[category] = kept
```

**What is happening**

- **validated** — Copy from state. **flagged** — Start from existing flagged (from validator). We will append more.
- **threshold** — Per category: overrides get category value, else CONFIDENCE_THRESHOLD.
- For each tag: if **conf >= threshold** we keep it in **kept**; else we append a FlaggedTag with reason "low_confidence" to **flagged** and increment **category_flag_count[category]**.
- **new_validated[category]** — The kept list (only tags that passed the threshold). We return new_validated so state’s validated_tags is **replaced** by this trimmed dict.

**Source:** [backend/src/image_tagging/nodes/confidence.py](../../backend/src/image_tagging/nodes/confidence.py) (lines 14–40)

> **State Tracker (after confidence):** validated_tags is now the trimmed dict (only tags >= threshold). flagged_tags is the previous list plus all tags moved for low_confidence. needs_review is set in the next step.

---

## Step 3 — Set needs_review and return

We set needs_review to True if any category had at least NEEDS_REVIEW_THRESHOLD flags, or if there are any flagged tags at all.

**Snippet (lines 41–53 in confidence.py)**

```python
    for count in category_flag_count.values():
        if count >= NEEDS_REVIEW_THRESHOLD:
            needs_review = True
            break
    if flagged:
        needs_review = True

    return {
        "validated_tags": new_validated,
        "flagged_tags": flagged,
        "needs_review": needs_review,
    }
```

**What is happening**

- If any category had 3 or more tags moved to flagged, **needs_review = True**.
- If **flagged** is non-empty (from validator or from this node), we also set **needs_review = True**. So any flag triggers review.
- We return the new validated_tags (replacing state’s), the full flagged list, and needs_review. The aggregator will read needs_review and put it on the TagRecord and use it for processing_status.

> **Next:** The aggregator (Lab 10) builds the final TagRecord from validated_tags and sets processing_status.

---

## Lab summary

1. **configuration.py** defines CONFIDENCE_THRESHOLD (0.65), CATEGORY_CONFIDENCE_OVERRIDES (product_type 0.80, season 0.60), and NEEDS_REVIEW_THRESHOLD (3).
2. **filter_by_confidence** loops validated_tags, keeps tags with confidence >= threshold, moves others to flagged with reason "low_confidence", and builds new_validated.
3. **needs_review** is True if any category has >= 3 flags or if there are any flagged tags. Return validated_tags, flagged_tags, needs_review.

---

## Exercises

1. Why use a higher threshold for product_type than for season?
2. If validated_tags has 2 tags in season and both are below 0.60, what happens to them and to needs_review?
3. Can needs_review be True even when category_flag_count is empty?

---

## Next lab

Go to [10-aggregator-builds-record.md](10-aggregator-builds-record.md) to see how the aggregator builds the final TagRecord from validated_tags and sets processing_status.
