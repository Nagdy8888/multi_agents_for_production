# Airtable setup

**When:** Phase 2+ (production LangGraph pipeline writing PO records). **Not** required for Phase 1.5 mock E2E ([02_DOCKER_MOCK_SETUP.md](02_DOCKER_MOCK_SETUP.md)).

**Outcome:** An Airtable **base** with two tables whose **field names match the Python writer exactly** (case-sensitive), plus a **Personal Access Token** in `.env` so `AirtableClient` can create records, look up duplicates, and optionally upload attachments.

**Authoritative field mapping:** [../documentations/DATA_FLOW.md](../documentations/DATA_FLOW.md) (section 4). **Code:** `src/services/airtable/`, `src/po_parser/nodes/airtable_writer.py`, `src/po_parser/nodes/validator.py`.

---

## Prerequisites

- An [Airtable](https://airtable.com) account (Free tier is enough to start).
- A **workspace** where you can create bases (or use “My First Workspace”).
- You will need **Owner** or **Creator** access to the base to create tables and fields.

---

## Step 1 — Create a base

1. Sign in at [https://airtable.com](https://airtable.com).
2. Click **Add a base** (or **Create**).
3. Choose **Start from scratch**.
4. Name the base something recognizable (e.g. **PO Parsing**). You can rename it anytime.

You should land in the default **Table 1** grid. You will replace this with the schema below.

---

## Step 2 — Create the **Customer POs** table

1. Rename **Table 1** to **`Customer POs`** (must match `AIRTABLE_PO_TABLE` default; or pick another name and set `AIRTABLE_PO_TABLE` in `.env` to that exact string).

2. Delete the default fields you do not need, then add fields so the **names match character-for-character** (spaces, slashes, capitalization):

| Field name (exact) | Suggested field type | Purpose |
|--------------------|----------------------|---------|
| `PO Number` | Single line text | Primary business key; used in duplicate formula `{PO Number}='…'` |
| `Customer` | Single line text | Customer name |
| `PO Date` | Single line text | Normalized date string (often `YYYY-MM-DD`) |
| `Ship Date` | Single line text | Same |
| `Status` | Single line text | Writer sets **Needs Review** on create |
| `Source Type` | Single line text | e.g. `email`, `pdf`, `mixed` |
| `Email Subject` | Single line text (or Long text) | From webhook |
| `Sender` | Single line text | From webhook |
| `Raw Extract JSON` | Long text | Full normalized `ExtractedPO` JSON for duplicate/revised comparison |
| `Validation Status` | Single line text | e.g. `Ready for Review`, `Needs Review`, `Duplicate`, `Extraction Failed` |
| `Confidence` | Number | Float 0–1 from classifier |
| `Processing Timestamp` | Single line text | UTC ISO 8601 from Python (e.g. `2026-04-05T12:34:56.789012+00:00`) |
| `Notes` | Long text | Reserved; writer sends empty string unless you extend code |

**How to add a field in Airtable:** click **+** to the right of the last column → choose type → set **Field name** exactly as in the table.

**Why text for some dates:** The normalizer outputs date **strings** from documents; the writer passes them through as strings. If you prefer Airtable **Date** fields, you may need to align formats; the current code does not send Airtable’s date-only API shape unless you change `airtable_writer.py`.

**Primary field:** Airtable requires a primary column. The first column is often **Name** by default. Either:
- Rename the default primary field to **`PO Number`** and delete a duplicate `PO Number` column, **or**
- Keep **Name** as primary for Airtable UI only and **also** have a field literally named **`PO Number`** used by the API (recommended: make **`PO Number`** the primary / first field so the grid matches the pipeline).

The duplicate check queries the PO table with an Airtable **formula** on the field whose name is **`PO Number`** (see `find_po_by_number` in `src/services/airtable/client.py`):

```text
{PO Number}='escaped_po_number'
```

Single quotes in the PO number are escaped for the formula.

If your primary field is not `PO Number`, you must still have a **separate** field named **`PO Number`** with that exact name, or change `find_po_by_number` in `src/services/airtable/client.py`.

---

## Step 3 — Create the **PO Items** table

1. Click **+** next to the table tabs → **Create empty table**.
2. Name it **`PO Items`** (or set `AIRTABLE_ITEMS_TABLE` in `.env` to your name).

3. Add fields:

| Field name (exact) | Field type | Notes |
|--------------------|------------|--------|
| `Linked PO` | Link to another record | Link **to** table **Customer POs**; allow linking **one** parent record per line item (typical). |
| `SKU` | Single line text | |
| `Description` | Long text | |
| `Quantity` | Number | Integer preferred; writer may send integers |
| `Unit Price` | Number | Currency formatting optional in Airtable UI |
| `Total Price` | Number | |
| `Destination / DC` | Single line text | Slash and spaces must match exactly |

The writer creates line items with pyairtable by sending, for each row, something like:

```text
"Linked PO": [ "<parent_record_id>" ]
```

plus `SKU`, `Description`, etc. The **link field name** must be **`Linked PO`**.

Remove or ignore Airtable’s default **Name** field if it conflicts with your workflow; linked-record tables often keep **Name** as primary auto-generated, or you can use **SKU** or a formula as primary—just ensure **`Linked PO`** and the item columns exist with the names above.

---

## Step 4 — Create a Personal Access Token (PAT)

1. Open [https://airtable.com/create/tokens](https://airtable.com/create/tokens).
2. Click **Create token**.
3. **Name** it (e.g. `po-parsing-agent-prod`).
4. **Scopes:** add at least:
   - **`data.records:read`**
   - **`data.records:write`**
5. **Access:** under **Add a base**, select the base you created (or “All current and future bases in …” if your policy allows—narrower is safer).
6. Create the token and **copy it once** (you will not see it again). It looks like `pat…`.

Store it only in `.env` or a secrets manager—never commit it.

---

## Step 5 — Copy the Base ID

1. Open your base in the browser.
2. The URL looks like:  
   `https://airtable.com/appXXXXXXXXXXXXXX/...`
3. The segment starting with **`app`** is **`AIRTABLE_BASE_ID`** (e.g. `appAbCdEfGhIjKlMnO`).

---

## Step 6 — Configure `.env`

In the repo root, copy from [.env.example](../../.env.example) if needed, then set:

```env
AIRTABLE_API_KEY=pat_xxxxxxxxxxxxxxxx
AIRTABLE_BASE_ID=appXXXXXXXXXXXXXX
AIRTABLE_PO_TABLE=Customer POs
AIRTABLE_ITEMS_TABLE=PO Items
```

- If you used **different table names**, set `AIRTABLE_PO_TABLE` / `AIRTABLE_ITEMS_TABLE` to those **exact** tab names.
- Leave optional attachment field empty until Step 7:

```env
AIRTABLE_ATTACHMENTS_FIELD=
```

**Docker:** [12_DOCKER_PRODUCTION_SETUP.md](12_DOCKER_PRODUCTION_SETUP.md) loads this `.env` for the production profile—same variables apply.

---

## Step 7 — Optional: attachment field on **Customer POs**

The pipeline can upload each email attachment to an **Attachment**-type field on the parent PO record **after** the record exists.

1. In **Customer POs**, add a field:
   - Type: **Attachment**
   - Name: e.g. **`Attachments`** or **`Email Files`** (any single name you choose).
2. Set in `.env`:

```env
AIRTABLE_ATTACHMENTS_FIELD=Attachments
```

Use the **exact** field name (case-sensitive). The writer calls pyairtable’s **`upload_attachment`** for each file; failures are logged and appended to pipeline `errors` without failing the whole run.

If you omit this variable or leave it blank, **no** uploads are attempted.

---

## Step 8 — Verify access (quick sanity check)

1. Restart your API container or process so it picks up `.env`.
2. Run the production stack ([12_DOCKER_PRODUCTION_SETUP.md](12_DOCKER_PRODUCTION_SETUP.md)).
3. POST a test webhook (or send a real PO email) and confirm:
   - A new row appears in **Customer POs** with **`PO Number`**, **`Raw Extract JSON`**, **`Validation Status`**, etc.
   - Related rows appear in **PO Items** with **`Linked PO`** populated.
4. In Airtable, open **Extensions** → **Scripting** or use the REST API docs if you want to confirm the token sees the base (optional).

---

## How the pipeline uses this base

| Component | Behavior |
|-----------|----------|
| **Validator** | `find_po_by_number`: formula `FIND` on `{PO Number}`; compares stored **`Raw Extract JSON`** to current extraction for duplicate vs revised. |
| **Writer** | Creates or updates **Customer POs**; creates **PO Items** with **`Linked PO`** for new POs; skips creating new line items when `is_revised` in validation (see [../documentations/LANGGRAPH_REFERENCE.md](../documentations/LANGGRAPH_REFERENCE.md)). |
| **Rate limits** | Airtable ~**5 requests/second** per base; sequential writes in code. No automatic 429 retry in `AirtableClient` ([../documentations/ERROR_HANDLING.md](../documentations/ERROR_HANDLING.md)). |

---

## Troubleshooting

| Symptom | Likely cause | What to do |
|---------|----------------|------------|
| **403** or **Unauthorized** from Airtable | Bad PAT, revoked token, or token missing base access | Recreate PAT with correct scopes and base; update `AIRTABLE_API_KEY`. |
| **422** / **INVALID_VALUE_FOR_COLUMN** | Field name typo or wrong type | Compare every name to the tables above; check **Single line text** vs **Number** for `Confidence` / prices. |
| **Duplicate check never finds rows** | Field not named **`PO Number`**, or primary field mismatch | Ensure a field with exact name **`PO Number`** exists; see Step 2. |
| **Linked PO** not linking | Wrong linked table or field name | Field must link to **Customer POs**; name **`Linked PO`**. |
| **Attachments fail** | Wrong `AIRTABLE_ATTACHMENTS_FIELD`, or field not Attachment type | Fix field name; ensure type is **Attachment**. |
| Writes slow or **429** | Burst of requests | Space out tests; consider throttling or batching in code if you bulk-import. |

---

## Related docs

- [../documentations/ENVIRONMENT_VARIABLES.md](../documentations/ENVIRONMENT_VARIABLES.md) — all `AIRTABLE_*` variables
- [../documentations/SERVICES_REFERENCE.md](../documentations/SERVICES_REFERENCE.md) — `AirtableClient` methods
- [12_DOCKER_PRODUCTION_SETUP.md](12_DOCKER_PRODUCTION_SETUP.md) — run the full pipeline
- [13_PRODUCTION_CHECKLIST.md](13_PRODUCTION_CHECKLIST.md) — go-live checks

Authoritative long-form spec: [`.cursor/plans/po_parsing_ai_agent_211da517.plan.md`](../../.cursor/plans/po_parsing_ai_agent_211da517.plan.md) (Airtable service section).
