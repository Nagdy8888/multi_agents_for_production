"""Tag validator: check partial_tags against taxonomy, fill validated_tags and flagged_tags (spec 4.4)."""
from typing import Any

from ..schemas.models import FlaggedTag, ValidatedTag
from ..schemas.states import ImageTaggingState
from ..taxonomy import TAXONOMY, get_parent_for_child

REQUIRED_CATEGORIES = {
    "season", "theme", "objects", "dominant_colors", "design_elements",
    "occasion", "mood", "product_type",
}
HIERARCHICAL_CATEGORIES = {"objects", "dominant_colors", "product_type"}


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


async def validate_tags(state: ImageTaggingState) -> dict[str, Any]:
    """Validate every tag in partial_tags against taxonomy; output validated_tags and flagged_tags."""
    partial = state.get("partial_tags") or []
    categories_seen = {p.get("category") for p in partial if isinstance(p, dict) and p.get("category")}
    if categories_seen != REQUIRED_CATEGORIES:
        return {}

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