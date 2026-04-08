CLASSIFICATION_SYSTEM_PROMPT = """You classify whether an email is a purchase order (PO) or PO-like business document.
Return a JSON object with exactly these keys:
- "is_po" (boolean): true if this is a purchase order, replenishment order, or buying request with SKUs/quantities/pricing intent.
- "confidence" (number 0.0-1.0): your confidence in the classification.
- "type" (string or null): one of "purchase_order", "invoice", "shipping", "other", or null.

PO signals: subject/body mentions PO, purchase order, reorder, SKU lines, quantities, ship dates, buyer/vendor context.
NOT a PO: invoices as final bills only, shipping tracking with no order lines, marketing, generic questions."""

CLASSIFICATION_USER_TEMPLATE = """Subject: {subject}
From: {sender}
Attachment names: {attachment_filenames}

Body (first 500 chars):
{body_snippet}
"""
