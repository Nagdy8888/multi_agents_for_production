# Airtable setup (PO parser)

> **Prev:** [10_OPENAI_SETUP.md](10_OPENAI_SETUP.md) | **Index:** [00_SETUP_INDEX.md](00_SETUP_INDEX.md) | **Next:** [12_DATABASE_SETUP.md](12_DATABASE_SETUP.md)

**Skip** if you only run the image agent.

1. Create base + tables **`Customer POs`** and **`PO Items`** with field names matching the code (see legacy doc `apps/agents/docs/po_parser/documentations/` or original `10_AIRTABLE_SETUP.md` content).
2. PAT at https://airtable.com/create/tokens — scopes `data.records:read` + `data.records:write`, access to your base.
3. `.env`:

```env
AIRTABLE_API_KEY=pat...
AIRTABLE_BASE_ID=app...
AIRTABLE_PO_TABLE=Customer POs
AIRTABLE_ITEMS_TABLE=PO Items
AIRTABLE_ATTACHMENTS_FIELD=   # optional Attachment field name
```
