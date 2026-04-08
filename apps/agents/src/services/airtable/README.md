# Airtable service

- **Settings:** `AIRTABLE_API_KEY`, `AIRTABLE_BASE_ID`, `AIRTABLE_PO_TABLE`, `AIRTABLE_ITEMS_TABLE`, optional `AIRTABLE_ATTACHMENTS_FIELD`.
- **Client:** `create_po_record`, `update_po_record`, `create_po_items` (links via `Linked PO`), `find_po_by_number` (formula), `upload_file_to_field` (attachment field).

Field names must match your base (see plan: `PO Number`, `Customer`, …).
