"""Confidence filter: move tags below threshold to flagged_tags (spec 4.5)."""
from typing import Any

from ..configuration import (
    CATEGORY_CONFIDENCE_OVERRIDES,
    CONFIDENCE_THRESHOLD,
    NEEDS_REVIEW_THRESHOLD,
)
from ..schemas.models import FlaggedTag
from ..schemas.states import ImageTaggingState


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