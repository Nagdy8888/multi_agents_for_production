"""Graph state definition for image tagging."""
from typing import Annotated, Literal, Optional, TypedDict
import operator


class ImageTaggingState(TypedDict, total=False):
    """State passed through the LangGraph pipeline."""
    image_id: str
    image_url: str
    image_base64: Optional[str]
    metadata: dict
    vision_description: str
    vision_raw_tags: dict
    partial_tags: Annotated[list, operator.add]
    validated_tags: dict
    flagged_tags: list
    tag_record: dict
    needs_review: bool
    processing_status: Literal["pending", "complete", "needs_review", "failed"]
    error: Optional[str]
