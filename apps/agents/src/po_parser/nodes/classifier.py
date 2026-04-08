"""Email / PO classification."""

import json
import logging

from src.po_parser.prompts.classification import (
    CLASSIFICATION_SYSTEM_PROMPT,
    CLASSIFICATION_USER_TEMPLATE,
)
from src.po_parser.schemas.classification import ClassificationResult
from src.po_parser.schemas.states import AgentState
from src.po_parser.utils import clamp_text
from src.services.openai.client import OpenAIClient
from src.services.openai.settings import OpenAISettings

logger = logging.getLogger(__name__)

_openai: OpenAIClient | None = None


def _client() -> OpenAIClient:
    global _openai
    if _openai is None:
        _openai = OpenAIClient(OpenAISettings())
    return _openai


def _rule_fallback(state: AgentState) -> ClassificationResult:
    email = state["email"]
    subj = (email.subject or "").upper()
    names = " ".join(a.filename.lower() for a in email.attachments)
    if ("PO" in subj or "PURCHASE ORDER" in subj) and (
        ".pdf" in names or ".xlsx" in names or ".xls" in names
    ):
        return ClassificationResult(is_po=True, confidence=0.6, type="purchase_order")
    return ClassificationResult(is_po=False, confidence=0.0, type="other")


def classify_node(state: AgentState) -> dict:
    email = state["email"]
    body = email.body or ""
    snippet = clamp_text(body, 500)
    att_names = ", ".join(a.filename for a in email.attachments) or "(none)"

    user = CLASSIFICATION_USER_TEMPLATE.format(
        subject=email.subject,
        sender=email.sender,
        attachment_filenames=att_names,
        body_snippet=snippet,
    )
    messages = [
        {"role": "system", "content": CLASSIFICATION_SYSTEM_PROMPT},
        {"role": "user", "content": user},
    ]

    try:
        cli = _client()
        if not cli.enabled:
            return {"classification": _rule_fallback(state)}

        raw = cli.chat_completion(
            messages,
            model=cli.settings.classification_model,
            json_mode=True,
        )
        data = json.loads(raw)
        result = ClassificationResult(
            is_po=bool(data.get("is_po")),
            confidence=float(data.get("confidence", 0)),
            type=data.get("type"),
        )
        return {"classification": result}
    except Exception as e:
        logger.exception("Classification failed: %s", e)
        errs = state["errors"] + [f"classification: {e}"]
        return {
            "classification": _rule_fallback(state),
            "errors": errs,
        }
