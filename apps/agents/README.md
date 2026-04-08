# Agents backend

Unified **FastAPI** app: `src/api/main.py` — PO webhooks, image REST API, GAS Drive webhook.

## Layout

- `src/po_parser/` — LangGraph graph `po_parser`
- `src/image_tagging/` — LangGraph graph `image_tagging`
- `src/services/` — `openai`, `supabase`, `airtable`, `gas_callback`
- `langgraph.json` — Studio config; `"env": "../../.env"`

## API (selection)

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/health` | Health |
| POST | `/webhook/email` | GAS Gmail → PO pipeline |
| POST | `/webhook/drive-image` | GAS Drive → image pipeline |
| GET | `/api/taxonomy` | Tag taxonomy |
| POST | `/api/analyze-image` | Upload + analyze |
| GET | `/api/tag-images`, `/api/search-images`, … | DB features (if `DATABASE_URI` set) |

## Run locally

From **repository root** (so `ROOT/.env` is found by `load_dotenv()`):

```powershell
cd apps/agents
pip install -r requirements.txt
cd ../..
$env:PYTHONPATH = "$(Resolve-Path apps/agents)"
python -m uvicorn src.api.main:app --app-dir apps/agents --host 0.0.0.0 --port 8000 --reload
```

## Docker

Built by root `docker-compose.yml` as service `agents`.

## Tests

`tests/unit/`, `tests/integration/`

## Docs

`docs/shared/`, `docs/po_parser/`, `docs/image_tagging/`
