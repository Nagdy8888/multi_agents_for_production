"""LangGraph shared state."""

from typing import Optional, TypedDict

from src.po_parser.schemas.classification import ClassificationResult
from src.po_parser.schemas.email import IncomingEmail
from src.po_parser.schemas.po import ExtractedPO
from src.po_parser.schemas.validation import ValidationResult


class AgentState(TypedDict):
    email: IncomingEmail
    classification: Optional[ClassificationResult]
    extracted_po: Optional[ExtractedPO]
    normalized_po: Optional[ExtractedPO]
    validation: Optional[ValidationResult]
    airtable_record_id: Optional[str]
    airtable_url: Optional[str]
    gas_callback_status: Optional[str]
    errors: list[str]
    processing_start_time: float
