"""Pydantic models for tag results and LLM structured output."""
from typing import Optional

from pydantic import BaseModel


class TagResult(BaseModel):
    """Output from a single tagger node."""
    category: str
    tags: list[str]
    confidence_scores: dict[str, float]


class ValidatedTag(BaseModel):
    """A tag that passed validation."""
    value: str
    confidence: float
    parent: Optional[str] = None


class FlaggedTag(BaseModel):
    """A tag below confidence threshold or invalid."""
    category: str
    value: str
    confidence: float
    reason: str


class HierarchicalTag(BaseModel):
    """Parent/child tag (e.g. objects, colors, product_type)."""
    parent: str
    child: str


class TagRecord(BaseModel):
    """Final assembled tag record for an image."""
    image_id: str
    season: list[str]
    theme: list[str]
    objects: list[HierarchicalTag]
    dominant_colors: list[HierarchicalTag]
    design_elements: list[str]
    occasion: list[str]
    mood: list[str]
    product_type: Optional[HierarchicalTag] = None
    needs_review: bool
    processed_at: str


class TaggerOutput(BaseModel):
    """Structured LLM output from a category tagger."""
    tags: list[str]
    confidence_scores: dict[str, float]
    reasoning: str
