# Environment variables

Aligned with the **Documentation Plan** in [`.cursor/plans/po_parsing_ai_agent_211da517.plan.md`](../../.cursor/plans/po_parsing_ai_agent_211da517.plan.md) (`ENVIRONMENT_VARIABLES.md`). **No Google API keys, service accounts, or GCP JSON** are used by Python.

## Python `.env` (repo root)

Loaded by Docker Compose (`env_file: .env`) and by `pydantic-settings` / `dotenv` in app code. **Never commit** `.env`. Start from **[`.env.example`](../../.env.example)** in the repo root.

| Variable | Required | Default / notes |
|----------|----------|-----------------|
| `OPENAI_API_KEY` | For real LLM path | Empty string → OpenAI clients **disabled** (rule fallback in classifier) |
| `OPENAI_CLASSIFICATION_MODEL` | No | `gpt-4o-mini` |
| `OPENAI_EXTRACTION_MODEL` | No | `gpt-4o-mini` |
| `OPENAI_OCR_MODEL` | No | `gpt-4o` (vision quality) |
| `OPENAI_MAX_TOKENS` | No | `4096` |
| `OPENAI_TEMPERATURE` | No | `0` |
| `LANGCHAIN_TRACING_V2` | No | `false` in example; set **`true`** to trace |
| `LANGCHAIN_API_KEY` | If tracing | Get from [smith.langchain.com](https://smith.langchain.com) |
| `LANGCHAIN_PROJECT` | No | `po-parsing-agent` |
| `LANGCHAIN_ENDPOINT` | No | Default `https://api.smith.langchain.com` (LangSmith SDK) |
| `AIRTABLE_API_KEY` | For Airtable writes | Personal access token |
| `AIRTABLE_BASE_ID` | For Airtable writes | Base id `app...` |
| `AIRTABLE_PO_TABLE` | No | `Customer POs` |
| `AIRTABLE_ITEMS_TABLE` | No | `PO Items` |
| `AIRTABLE_ATTACHMENTS_FIELD` | No | Optional attachment field name on PO table |
| `WEBHOOK_SECRET` | Yes for webhook | Match GAS; header `x-webhook-secret`. Generate e.g. `openssl rand -hex 32` |
| `GAS_WEBAPP_URL` | Yes for callback | Deployed Web App URL (`.../exec`) |
| `GAS_WEBAPP_SECRET` | Yes for callback | Match GAS; JSON field **`secret`** on callback |
| `LOG_LEVEL` | No | `INFO`; also **`DEBUG`**, **`WARNING`**, **`ERROR`** |
| `CLASSIFICATION_CONFIDENCE_THRESHOLD` | Plan only | **Not read by code today** — threshold **0.7** is hardcoded in `routing.py` |

## GAS Script Properties (not in `.env`)

Set in Apps Script: **Project Settings → Script properties**.

| Property | Purpose |
|----------|---------|
| `WEBHOOK_URL` | Full Python URL including **`/webhook/email`** |
| `WEBHOOK_SECRET` | Must equal Python **`WEBHOOK_SECRET`** |
| `GAS_WEBAPP_SECRET` | Must equal Python **`GAS_WEBAPP_SECRET`** |
| `SPREADSHEET_ID` | Target Google Sheet |
| `NOTIFICATION_RECIPIENTS` | Comma-separated emails for HTML alerts |

## Docker vs local

- **Docker Compose:** `.env` sits next to `docker-compose.yml`; both **`mock`** and **`production`** profiles read it.
- **Local `uvicorn`:** export vars or use `.env` in the working directory so `pydantic-settings` / `load_dotenv` can see them.

## Security

- **`.gitignore`** must exclude `.env`.
- Script Properties are stored by Google on the script project.
- Rotate **both** sides when a secret leaks.

## Timezone strategy (required by plan)

- **Python / Airtable:** processing timestamps in **UTC** (e.g. `datetime.now(timezone.utc).isoformat()`). Airtable **Processing Timestamp** = UTC ISO 8601.
- **GAS / Sheets:** `appsscript.json` uses **`Africa/Cairo`**; `Utilities.formatDate(..., "Africa/Cairo", ...)` for Sheets readability.
- **PO business dates (`po_date`, `ship_date`, `cancel_date`):** **date-only** strings from the document — **no timezone**; they are calendar dates, not instants.
- **Rationale:** UTC in Airtable avoids ambiguity across senders; Cairo in Sheets matches operator locale; PO dates stay neutral.
