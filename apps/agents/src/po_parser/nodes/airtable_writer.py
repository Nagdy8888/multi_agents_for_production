"""Create/update Airtable PO + line items."""

from __future__ import annotations

import base64
import json
import logging
from datetime import datetime, timezone

from src.po_parser.schemas.states import AgentState
from src.services.airtable.client import AirtableClient
from src.services.airtable.settings import AirtableSettings

logger = logging.getLogger(__name__)

_airtable: AirtableClient | None = None


def _client() -> AirtableClient:
    global _airtable
    if _airtable is None:
        _airtable = AirtableClient(AirtableSettings())
    return _airtable


def airtable_writer_node(state: AgentState) -> dict:
    po = state.get("normalized_po")
    val = state.get("validation")
    email = state["email"]
    errs = list(state["errors"])

    if not po or not val:
        return {"airtable_record_id": None, "airtable_url": None, "errors": errs}

    at = _client()
    if not at.enabled:
        errs.append("airtable_writer: Airtable not configured")
        return {"airtable_record_id": None, "airtable_url": None, "errors": errs}

    try:
        settings = AirtableSettings()

        if val.is_duplicate and not val.is_revised and val.existing_record_id:
            rid = val.existing_record_id
            url = at.record_url(settings.po_table, rid)
            return {"airtable_record_id": rid, "airtable_url": url}

        ts = datetime.now(timezone.utc).isoformat()
        conf = state.get("classification")
        confidence = conf.confidence if conf else None

        fields = {
            "PO Number": po.po_number or "",
            "Customer": po.customer or "",
            "PO Date": po.po_date or "",
            "Ship Date": po.ship_date or "",
            "Status": "Needs Review",
            "Source Type": po.source_type or "email",
            "Email Subject": email.subject,
            "Sender": email.sender,
            "Raw Extract JSON": json.dumps(po.model_dump(), default=str),
            "Validation Status": val.status.value,
            "Confidence": confidence,
            "Processing Timestamp": ts,
            "Notes": "",
        }

        if val.is_revised and val.existing_record_id:
            rid = at.update_po_record(val.existing_record_id, fields)
        else:
            rid = at.create_po_record(fields)

        item_rows: list[dict] = []
        for it in po.items or []:
            item_rows.append(
                {
                    "SKU": it.sku or "",
                    "Description": it.description or "",
                    "Quantity": it.quantity,
                    "Unit Price": it.unit_price,
                    "Total Price": it.total_price,
                    "Destination / DC": it.destination or "",
                }
            )
        if item_rows and not val.is_revised:
            at.create_po_items(rid, item_rows)

        if settings.attachments_field.strip():
            for att in email.attachments:
                try:
                    raw = base64.b64decode(att.data_base64, validate=False)
                    at.upload_file_to_field(
                        rid,
                        settings.attachments_field.strip(),
                        att.filename,
                        raw,
                        att.content_type or None,
                    )
                except Exception as ex:
                    logger.warning(
                        "Airtable attachment upload failed (%s): %s",
                        att.filename,
                        ex,
                    )
                    errs.append(f"airtable attachment {att.filename}: {ex}")

        url = at.record_url(settings.po_table, rid)
        return {"airtable_record_id": rid, "airtable_url": url, "errors": errs}
    except Exception as e:
        logger.exception("airtable_writer: %s", e)
        errs.append(f"airtable_writer: {e}")
        return {
            "airtable_record_id": None,
            "airtable_url": None,
            "errors": errs,
        }
