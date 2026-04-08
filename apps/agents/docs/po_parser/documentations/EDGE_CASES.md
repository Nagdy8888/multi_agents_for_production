# Edge cases

This file follows the **Documentation Plan** in [`.cursor/plans/po_parsing_ai_agent_211da517.plan.md`](../../.cursor/plans/po_parsing_ai_agent_211da517.plan.md) (`EDGE_CASES.md`). For each scenario the plan asks for: **description**, **detection**, **handling**, **which node**, **what the user sees**.

| Topic | Detection | Handling | Node(s) | User-visible outcome |
|-------|-----------|----------|---------|----------------------|
| **Multiple POs in one email** | LLM might emit multiple PO numbers in text | Plan: split into multiple `ExtractedPO`; **code:** single schema per run | `extract`, `validate`, `write_airtable` | One Airtable row unless pipeline extended; review **Needs Review** if merged wrong |
| **PDF + Excel overlap** | Same PO data in body + attachments | Consolidator **section delimiters**; LLM merges in one `ExtractedPO` | `consolidate`, `extract` | Single record; check **Raw Extract JSON** in Airtable |
| **Scanned PDF** | Text length &lt; **50** after pdfplumber + PyMuPDF | Page images → **Vision** OCR | `parse_pdf` | If OCR still poor → extraction issues / **Needs Review** |
| **Revised PO (same PO#)** | `find_po_by_number` + JSON snapshot ≠ stored **Raw Extract JSON** | `is_revised`, **update** parent, line-item rules per writer | `validate`, `write_airtable` | **Needs Review** + issues; updated row |
| **Multiple Excel tabs** | `wb.sheetnames` | Each sheet in `excel_data` | `parse_excel`, `consolidate` | All sheets in consolidated text; LLM picks PO sheet |
| **Inconsistent headers** | `_HEADER_ALIASES` + normalization | Map e.g. **P.O. #** / **PO Number** → `po_number`, **Qty** / **Quantity** → `quantity`, **Unit Cost** / **Unit Price** → `unit_price` | `parse_excel` | Better column alignment in JSON dump |
| **Mixed attachments** | Sequential parsers | **parse_body → parse_pdf → parse_excel**; skip irrelevant | all parsers | Combined context in one extraction |
| **Body + attachment partial PO** | Consolidator sections | Both body and files in `consolidated_text` | `consolidate`, `extract` | Single merged extraction |
| **Empty / corrupt attachment** | Parser exception per file | Append to `errors`, continue | `parse_pdf`, `parse_excel` | Pipeline continues; errors in callback / logs |
| **Non-English PO** | No dedicated detector | LLM may still extract; **not fully tested** | `extract` | Treat as **Needs Review** if unsure |
| **Very large PO (100+ lines)** | Token limits / huge `consolidated_text` | Plan: future chunking; **now:** retry once then fail path | `extract` | **Extraction Failed** or partial JSON errors |
| **Body-only PO** | No PDF/Excel hits | Empty `pdf_texts` / `excel_data` | `parse_*`, `consolidate` | `source_type` often **`email`** |
| **Not a PO / low confidence** | `is_po` false or **confidence &lt; 0.7** | Route to **END** after classify | `classify`, `routing` | No Airtable row from this run; GAS may still **markRead** on **202** |
| **Secrets mismatch** | 401 or invalid `secret` | GAS labels failed; Python logs callback error | `middleware` / `doPost` | **PO-Processing-Failed** / callback error |
| **GAS self-processing loop** | Notification emails (subject "PO Processed: ..." or "PO Processing FAILED: ...") match the search query | `SEARCH_QUERY` in `Config.gs` now excludes `-subject:"PO Processed:" -subject:"PO Processing FAILED:" -from:me` | `Config.gs` | GAS no longer picks up its own notifications |
| **LLM returns `null` for currency** | OpenAI returns `null` instead of `"USD"` for optional-looking fields | `ExtractedPO.currency` is `Optional[str]` with a `@field_validator` that coerces `None`/empty to `"USD"` | `extract`, `po.py` | No Pydantic crash; defaults to USD |
| **Airtable URL missing table ID** | `record_url` built as `/{base_id}/{record_id}` (two segments) → 404 in browser | `AirtableClient._resolve_table_ids()` fetches table IDs at init; `record_url` now produces `/{base_id}/{table_id}/{record_id}` | `airtable_writer`, `airtable/client.py` | Clickable links in Sheets/notifications work correctly |

## Plan narrative (verbatim themes)

- **Multiple POs:** the plan assumes multiple `ExtractedPO` objects; the **current** extractor validates **one** object per invocation — extend schema/pipeline if you need one-email → many Airtable POs.

- **OCR failure:** if vision output is trivially short (**&lt; 50 chars**), treat as failed OCR / manual review (aligns with [PROMPTS_REFERENCE.md](PROMPTS_REFERENCE.md)).

- **Gmail labels:** errors on webhook POST or error **callback** path apply **PO-Processing-Failed** (see [GAS_REFERENCE.md](GAS_REFERENCE.md)).

## Related docs

- Parser mechanics: [LANGGRAPH_REFERENCE.md](LANGGRAPH_REFERENCE.md) (plan subflow diagrams).
- Validation rules: [SCHEMAS_REFERENCE.md](SCHEMAS_REFERENCE.md), `src/po_parser/nodes/validator.py`.
