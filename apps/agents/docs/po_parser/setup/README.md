# Setup guides

Follow these in order for **Phase 1 + Phase 1.5** (GAS + mock Python + ngrok + end-to-end test). After that, use **OpenAI / Airtable / production Docker** guides and the technical reference in [../documentations/README.md](../documentations/README.md).

Authoritative spec: `.cursor/plans/po_parsing_ai_agent_211da517.plan.md`.

## Phase 1.5 path (do in this order)

| Step | Guide | What you get |
|------|--------|----------------|
| 1 | [00_PREREQUISITES.md](00_PREREQUISITES.md) | Docker, Node.js, Git, ngrok, Google account |
| 2 | [07_GAS_CLASP_SETUP.md](07_GAS_CLASP_SETUP.md) | clasp, GAS project, `clasp push`, trigger (or run `installFiveMinuteTrigger`) |
| 3 | [09_GOOGLE_SHEETS_SETUP.md](09_GOOGLE_SHEETS_SETUP.md) | Spreadsheet + 3 tabs + headers + `SPREADSHEET_ID` |
| 4 | [11_GAS_WEBAPP_SETUP.md](11_GAS_WEBAPP_SETUP.md) | Web App URL, `GAS_WEBAPP_SECRET`, `NOTIFICATION_RECIPIENTS`, Python `.env` |
| 5 | [08_GMAIL_SETUP.md](08_GMAIL_SETUP.md) | Labels `PO-Processed` / `PO-Processing-Failed`, search query sanity check |
| 6 | [01_DEVELOPMENT_SETUP.md](01_DEVELOPMENT_SETUP.md) | Copy `.env.example` → `.env`, mock-only variables |
| 7 | [02_DOCKER_MOCK_SETUP.md](02_DOCKER_MOCK_SETUP.md) | `docker compose --profile mock up`, health check |
| 8 | [03_NGROK_SETUP.md](03_NGROK_SETUP.md) | Public URL → set GAS `WEBHOOK_URL` = `https://…/webhook/email` |
| 9 | [14_PHASE_1_5_VERIFICATION.md](14_PHASE_1_5_VERIFICATION.md) | Send test email, run through 10 checks |

**Script Properties (GAS)** must all be set before E2E:

- `WEBHOOK_URL` — ngrok URL + `/webhook/email`
- `WEBHOOK_SECRET` — same as `WEBHOOK_SECRET` in `.env`
- `GAS_WEBAPP_SECRET` — same as `GAS_WEBAPP_SECRET` in `.env`
- `SPREADSHEET_ID` — from Sheets URL
- `NOTIFICATION_RECIPIENTS` — comma-separated emails

**Python `.env` (mock)** needs at least:

- `WEBHOOK_SECRET`
- `GAS_WEBAPP_URL` — deployed Web App URL (ends with `/exec` or similar)
- `GAS_WEBAPP_SECRET`

## Production / LangGraph path (after mock E2E)

| Guide | Purpose |
|-------|---------|
| [04_OPENAI_SETUP.md](04_OPENAI_SETUP.md) | API key and model env vars (`OPENAI_*`) |
| [05_LANGSMITH_SETUP.md](05_LANGSMITH_SETUP.md) | Optional tracing (`LANGCHAIN_*`) |
| [06_LANGGRAPH_STUDIO_SETUP.md](06_LANGGRAPH_STUDIO_SETUP.md) | Studio + root `langgraph.json` |
| [10_AIRTABLE_SETUP.md](10_AIRTABLE_SETUP.md) | Base, tables, optional `AIRTABLE_ATTACHMENTS_FIELD` |
| [12_DOCKER_PRODUCTION_SETUP.md](12_DOCKER_PRODUCTION_SETUP.md) | `po-parser` profile (`uvicorn`) |
| [13_PRODUCTION_CHECKLIST.md](13_PRODUCTION_CHECKLIST.md) | Pre-go-live checks |

### After Airtable — finish production setup

Airtable is only one piece. Do this **in order** (skip steps you already completed):

1. **OpenAI** — [04_OPENAI_SETUP.md](04_OPENAI_SETUP.md): set `OPENAI_API_KEY` and optional `OPENAI_*` models in `.env`.
2. **Merge `.env`** — Ensure **all** keys from [.env.example](../../.env.example) needed for production are filled: `WEBHOOK_SECRET`, `GAS_WEBAPP_URL`, `GAS_WEBAPP_SECRET`, `OPENAI_*`, `AIRTABLE_*`, plus optional `AIRTABLE_ATTACHMENTS_FIELD`, `LANGCHAIN_*`. See [../documentations/ENVIRONMENT_VARIABLES.md](../documentations/ENVIRONMENT_VARIABLES.md).
3. **Optional** — [05_LANGSMITH_SETUP.md](05_LANGSMITH_SETUP.md) (tracing), [06_LANGGRAPH_STUDIO_SETUP.md](06_LANGGRAPH_STUDIO_SETUP.md) (Studio + `langgraph.json`).
4. **GAS must already be done** for real email — If you have not finished the **Phase 1.5** table above (Sheets, Web App, Gmail labels, ngrok, `WEBHOOK_URL`), complete that first so GAS can POST to Python and receive callbacks. Script Properties must match `.env`.
5. **Switch Docker to production** — [12_DOCKER_PRODUCTION_SETUP.md](12_DOCKER_PRODUCTION_SETUP.md): `docker compose --profile mock down`, then `docker compose --profile production up --build`; verify `/health` has **no** `"mode":"mock"`.
6. **Expose the API** — Same ngrok pattern as mock ([03_NGROK_SETUP.md](03_NGROK_SETUP.md)). Set GAS **`WEBHOOK_URL`** to `https://<your-tunnel>/webhook/email` (update whenever the tunnel URL changes).
7. **Go-live checks** — [13_PRODUCTION_CHECKLIST.md](13_PRODUCTION_CHECKLIST.md): send a real PO email and confirm Airtable + Sheets + notification + label.

**First-time project setup** (nothing configured yet): start at **Phase 1.5** in the table above, then run the **Production / LangGraph** row (OpenAI → … → Airtable → production Docker → checklist).
