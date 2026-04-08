"""Validator output."""

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class ValidationStatus(str, Enum):
    READY_FOR_REVIEW = "Ready for Review"
    NEEDS_REVIEW = "Needs Review"
    DUPLICATE = "Duplicate"
    EXTRACTION_FAILED = "Extraction Failed"


class ValidationResult(BaseModel):
    status: ValidationStatus
    issues: list[str] = Field(default_factory=list)
    is_duplicate: bool = False
    is_revised: bool = False
    existing_record_id: Optional[str] = None
