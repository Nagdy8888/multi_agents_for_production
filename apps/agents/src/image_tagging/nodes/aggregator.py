"""Tag aggregator: build TagRecord from validated_tags (spec 4.6)."""
from datetime import datetime, timezone
from typing import Any

from ..schemas.models import HierarchicalTag, TagRecord
from ..schemas.states import ImageTaggingState
from ..taxonomy import get_parent_for_child


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