"""Classifier output."""

from typing import Optional

from pydantic import BaseModel, Field


class ClassificationResult(BaseModel):
    is_po: bool
    confidence: float = Field(ge=0.0, le=1.0)
    type: Optional[str] = None
