"""POST final payload to GAS Web App."""

from __future__ import annotations

import logging
import time

from src.po_parser.schemas.states import AgentState
from src.po_parser.schemas.validation import ValidationStatus
from src.services.gas_callback.client import GASCallbackClient
from src.services.gas_callback.settings import GASCallbackSettings

logger = logging.getLogger(__name__)

_gas: GASCallbackClient | None = None


def _client() -> GASCallbackClient:
    global _gas
    if _gas is None:
        _gas = GASCallbackClient(GASCallbackSettings())
    return _gas


def gas_callback_node(state: AgentState) -> dict:
    email = state["email"]
    po = state.get("normalized_po")
    val = state.get("validation")
    conf = state.get("classification")
    errs = list(state["errors"])

    success = (
        po is not None
        and val is not None
        and val.status != ValidationStatus.EXTRACTION_FAILED
    )
    status = "success" if success else "error"

    items_out: list[dict] = []
    if po:
        for it in po.items or []:
            items_out.append(
                {
                    "sku": it.sku,
                    "description": it.description,
                    "quantity": it.quantity,
                    "unit_price": it.unit_price,
                    "total_price": it.total_price,
                    "destination": it.destination,
                }
            )

    po_data = po.model_dump() if po else {}
    validation_out = (
        {"status": val.status.value, "issues": val.issues}
        if val
        else {"status": "Unknown", "issues": []}
    )

    payload = {
        "message_id": email.message_id,
        "status": status,
        "po_data": po_data,
        "items": items_out,
        "validation": validation_out,
        "confidence": conf.confidence if conf else 0.0,
        "airtable_url": state.get("airtable_url") or "",
        "processing_time_ms": int(
            (time.time() - state["processing_start_time"]) * 1000
        ),
        "errors": errs,
    }

    try:
        res = _client().send_results(payload)
        st = str(res.get("status", "")).lower()
        ok = st in ("ok", "success")
        if ok:
            return {"gas_callback_status": "ok"}
        errs.append(f"gas_callback: {res}")
        return {"gas_callback_status": "error", "errors": errs}
    except Exception as e:
        logger.exception("gas_callback: %s", e)
        errs.append(f"gas_callback: {e}")
        return {"gas_callback_status": "error", "errors": errs}
