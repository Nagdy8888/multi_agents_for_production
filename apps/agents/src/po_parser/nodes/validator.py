"""Business validation and duplicate detection (Airtable)."""

from __future__ import annotations

import json
import logging
from typing import Any

from src.po_parser.schemas.states import AgentState
from src.po_parser.schemas.validation import ValidationResult, ValidationStatus
from src.services.airtable.client import AirtableClient
from src.services.airtable.settings import AirtableSettings

logger = logging.getLogger(__name__)

_airtable_client: AirtableClient | None = None


def _get_airtable() -> AirtableClient:
    global _airtable_client
    if _airtable_client is None:
        _airtable_client = AirtableClient(AirtableSettings())
    return _airtable_client


def _snapshot(po) -> dict[str, Any]:
    return {
        "po_number": po.po_number,
        "customer": po.customer,
        "items": [i.model_dump() for i in (po.items or [])],
    }


def validator_node(state: AgentState) -> dict:
    po = state.get("normalized_po")
    if po is None:
        return {
            "validation": ValidationResult(
                status=ValidationStatus.EXTRACTION_FAILED,
                issues=["No PO data extracted"],
            )
        }

    issues: list[str] = []
    if not (po.po_number or "").strip():
        issues.append("Missing PO Number")
    if not (po.customer or "").strip():
        issues.append("Missing Customer")

    for idx, it in enumerate(po.items or []):
        if it.quantity is not None and it.quantity <= 0:
            issues.append(f"Line {idx + 1}: quantity must be > 0")

    status = ValidationStatus.READY_FOR_REVIEW
    is_duplicate = False
    is_revised = False
    existing_record_id: str | None = None

    at = _get_airtable()
    if at.enabled and (po.po_number or "").strip():
        try:
            rec = at.find_po_by_number(po.po_number.strip())
            if rec:
                existing_record_id = str(rec.get("id", ""))
                fields = rec.get("fields") or {}
                raw = fields.get("Raw Extract JSON") or "{}"
                try:
                    prev = json.loads(raw) if isinstance(raw, str) else raw
                except json.JSONDecodeError:
                    prev = {}
                snap = _snapshot(po)
                if isinstance(prev, dict) and json.dumps(
                    prev, sort_keys=True, default=str
                ) == json.dumps(snap, sort_keys=True, default=str):
                    status = ValidationStatus.DUPLICATE
                    is_duplicate = True
                else:
                    status = ValidationStatus.NEEDS_REVIEW
                    is_revised = True
                    issues.append("Existing Airtable PO with same number differs from extraction")
        except Exception as e:
            logger.warning("validator Airtable lookup failed: %s", e)
            issues.append(f"Airtable duplicate check failed: {e}")
            status = ValidationStatus.NEEDS_REVIEW

    if issues and status == ValidationStatus.READY_FOR_REVIEW:
        status = ValidationStatus.NEEDS_REVIEW

    return {
        "validation": ValidationResult(
            status=status,
            issues=issues,
            is_duplicate=is_duplicate,
            is_revised=is_revised,
            existing_record_id=existing_record_id,
        )
    }
