# Prompts reference

Source files: `src/po_parser/prompts/`. This page follows the **Documentation Plan** in [`.cursor/plans/po_parsing_ai_agent_211da517.plan.md`](../../.cursor/plans/po_parsing_ai_agent_211da517.plan.md) (`PROMPTS_REFERENCE.md` / Phase 2.6): full prompt text, expected outputs, thresholds, and examples.

**Versioning:** prompts are **Python string constants** in repo; change control = **Git** history (no external CMS).

## Classification (`classification.py`)

### `CLASSIFICATION_SYSTEM_PROMPT`

```
You classify whether an email is a purchase order (PO) or PO-like business document.
Return a JSON object with exactly these keys:
- "is_po" (boolean): true if this is a purchase order, replenishment order, or buying request with SKUs/quantities/pricing intent.
- "confidence" (number 0.0-1.0): your confidence in the classification.
- "type" (string or null): one of "purchase_order", "invoice", "shipping", "other", or null.

PO signals: subject/body mentions PO, purchase order, reorder, SKU lines, quantities, ship dates, buyer/vendor context.
NOT a PO: invoices as final bills only, shipping tracking with no order lines, marketing, generic questions.
```

### `CLASSIFICATION_USER_TEMPLATE`

Placeholders: `{subject}`, `{sender}`, `{attachment_filenames}`, `{body_snippet}`.

```
Subject: {subject}
From: {sender}
Attachment names: {attachment_filenames}

Body (first 500 chars):
{body_snippet}
```

**Expected output shape:**

```json
{ "is_po": true, "confidence": 0.92, "type": "purchase_order" }
```

**Confidence threshold:** plan references **`CLASSIFICATION_CONFIDENCE_THRESHOLD`** env (default **0.7**). The **current code** hardcodes **`0.7`** in `src/po_parser/nodes/routing.py` — to make it env-driven, wire a setting into that module.

**Plan examples:**

- Subject **“PO 12345 from Greenbrier”** → `is_po=true`, confidence ~**0.95**.
- Subject **“Meeting tomorrow”** → `is_po=false`, confidence ~**0.05**.

## Extraction (`extraction.py`)

### `EXTRACTION_SYSTEM_PROMPT` (full text)

```
You extract structured purchase order data from messy text. Output ONE JSON object only (no markdown).
Use null for unknown fields. Do not invent SKUs or amounts.

Schema (all keys required in JSON; use null where unknown):
{
  "po_number": string|null,
  "customer": string|null,
  "po_date": string|null,
  "ship_date": string|null,
  "cancel_date": string|null,
  "items": [
    {
      "sku": string|null,
      "description": string|null,
      "quantity": number|null,
      "unit_price": number|null,
      "total_price": number|null,
      "destination": string|null
    }
  ],
  "destinations": [ { "dc_name": string|null, "address": string|null } ],
  "total_amount": number|null,
  "currency": string,
  "payment_terms": string|null,
  "ship_to": string|null,
  "bill_to": string|null,
  "source_type": "pdf"|"spreadsheet"|"email"|"mixed"|null,
  "raw_confidence": number|null
}
```

### `EXTRACTION_USER_TEMPLATE`

```
--- BEGIN DOCUMENT ---
{consolidated_text}
--- END DOCUMENT ---
```

**Behavior:** `extractor_node` calls `chat_completion` with `json_mode=True`; on **`ExtractedPO.model_validate_json`** failure, retries once with an extra user line: *“Output valid JSON only matching the schema. No markdown.”*

**Expected output:** one **`ExtractedPO`** JSON object with `po_number`, `customer`, dates, `items[]`, etc.; use **`null`** for unknown fields — do not guess SKUs or dollar amounts.

**Plan examples (samples):**

- **Greenbrier-style:** long consolidated text, **multiple SKUs**, multiple **destinations / DCs** — expect populated `items` and `destinations`.
- **Family Dollar–style:** often **PDF-originated**, sometimes **single line item** — expect `source_type` commonly `"pdf"` or `"mixed"` and a small `items` array.

Use **`tests/sample_pos/`** and any **`Description/Sample POs/`** materials in the repo for fixtures.

### Example extracted JSON (Greenbrier-style sketch)

```json
{
  "po_number": "00011830728",
  "customer": "Greenbrier International",
  "po_date": "2026-03-01",
  "ship_date": "2026-03-20",
  "cancel_date": null,
  "items": [
    { "sku": "111", "description": "Item A", "quantity": 10, "unit_price": 5.0, "total_price": 50.0, "destination": "DC1" },
    { "sku": "222", "description": "Item B", "quantity": 5, "unit_price": 8.0, "total_price": 40.0, "destination": "DC2" }
  ],
  "destinations": [
    { "dc_name": "DC1", "address": "123 Road" },
    { "dc_name": "DC2", "address": "456 Ave" }
  ],
  "total_amount": 90.0,
  "currency": "USD",
  "payment_terms": "Net 30",
  "ship_to": null,
  "bill_to": null,
  "source_type": "mixed",
  "raw_confidence": 0.9
}
```

## OCR (`ocr.py`)

### `OCR_SYSTEM_PROMPT`

```
You read document images and return plain text only.
Preserve table structure using spaces or line breaks. No commentary.
```

### `OCR_USER_PROMPT`

```
Read all text from this document image. Preserve tables and formatting.
```

**Multimodal message:** user message `content` is `[{type: text, text: ...}, {type: image_url, image_url: {url: "data:image/png;base64,..."}}]`.

**Plan quality threshold:** if vision/OCR output is **&lt; 50 characters**, treat as failed / insufficient (manual review). The PDF node uses a similar **50-character** heuristic before escalating to OCR.

**Message shape:** multimodal user content = `[{ "type": "text", "text": <prompt> }, { "type": "image_url", "image_url": { "url": "data:image/png;base64,..." } }]`.
