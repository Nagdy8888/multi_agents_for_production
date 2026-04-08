# Multi-Agent Platform

A monorepo hosting two LangGraph-based AI agents with a shared Python backend (FastAPI), a Next.js frontend, and a Google Apps Script layer (Git submodule).

## Agents

### PO Parser

Automated purchase order intake from Gmail. Emails arrive via a GAS trigger, get classified (gpt-4o-mini), then a single **GPT-4o vision** call extracts structured PO data from email body text, PDF page images, and parsed spreadsheet data in one shot. Results are written to **Airtable** and reported back to **Google Sheets** via a GAS callback.

**Pipeline:** `classify` → `extract_po` → `validate` → `write_airtable` → `callback_gas`

### Image Tagging

Product image analysis using GPT-4o vision. Images are tagged across multiple categories (season, theme, colors, objects, etc.) with confidence scores. Supports single upload, bulk upload, and a GAS Drive trigger webhook. Persists to **Supabase/PostgreSQL** with a **Next.js** dashboard for browsing and filtering.

## Repository Layout

```
Multi_agents/
├── .env.example              # Template — copy to .env at repo root
├── .env                      # All services read from this single file (gitignored)
├── docker-compose.yml        # agents (:8000) + frontend (:3000)
├── README.md                 # This file
│
├── apps/
│   ├── agents/               # Python backend (FastAPI + LangGraph)
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   ├── langgraph.json    # LangGraph Studio graph registry
│   │   ├── src/
│   │   │   ├── api/          # Unified FastAPI app (main.py, middleware.py)
│   │   │   ├── po_parser/    # PO Parser agent
│   │   │   │   ├── graph_builder.py
│   │   │   │   ├── nodes/    # classify, extract_po, validate, write_airtable, callback_gas
│   │   │   │   ├── schemas/  # AgentState, ExtractedPO, IncomingEmail, etc.
│   │   │   │   └── prompts/  # LLM prompt templates
│   │   │   ├── image_tagging/  # Image Tagging agent
│   │   │   │   ├── graph_builder.py
│   │   │   │   ├── nodes/    # preprocessor, vision_analyzer, taggers, validator
│   │   │   │   └── taxonomy.py
│   │   │   └── services/     # Shared clients
│   │   │       ├── openai/   # OpenAI chat + vision
│   │   │       ├── airtable/ # Airtable CRUD + URL builder
│   │   │       ├── supabase/ # Supabase/Postgres persistence
│   │   │       └── gas_callback/  # GAS webhook client
│   │   ├── docs/             # Agent-specific documentation
│   │   └── tests/            # Unit + integration tests
│   │
│   └── frontend/             # Next.js 16 dashboard (image tagging UI)
│       ├── Dockerfile
│       └── src/
│
├── gas-scripts/              # Git submodule — Google Apps Script
│   ├── Code.gs               # Email trigger → webhook
│   ├── WebApp.gs             # doPost() callback handler
│   ├── SheetsWriter.gs       # Google Sheets output
│   └── ...
│
├── description/              # Project briefs and sample PO files
└── scripts/                  # E2E mock test script
```

## Prerequisites

- **Docker & Docker Compose** (primary way to run)
- **Python 3.11+** (local dev / LangGraph Studio)
- **Node.js 20+** (frontend local dev)
- **clasp** (optional, for GAS deployment)

## Quick Start

```bash
git clone --recurse-submodules https://github.com/Modern-Intelligence-Solutions/multi-agents.git
cd multi-agents
cp .env.example .env        # then fill in API keys
docker compose up --build
```

| Service  | URL                           |
|----------|-------------------------------|
| API      | http://localhost:8000/health   |
| Frontend | http://localhost:3000          |
| API Docs | http://localhost:8000/docs     |

### Submodule

If you cloned without `--recurse-submodules`:

```bash
git submodule update --init --recursive
```

## Environment Variables

All configuration lives in a single `.env` file at the repo root. Both Docker services and local dev read from it. See `.env.example` for all available variables.

Key variables:

| Variable | Purpose |
|----------|---------|
| `OPENAI_API_KEY` | Required for both agents |
| `WEBHOOK_SECRET` | GAS → Python auth header |
| `GAS_WEBAPP_SECRET` | Python → GAS callback auth |
| `GAS_WEBAPP_URL` | GAS Web App URL for callbacks |
| `AIRTABLE_API_KEY` / `AIRTABLE_BASE_ID` | PO Parser writes to Airtable |
| `DATABASE_URI` | Image Tagging persists to Supabase/Postgres |
| `NEXT_PUBLIC_API_URL` | Frontend API base URL |
| `API_PUBLIC_BASE_URL` | Override for persisted image URLs (ngrok) |

## Local Development (no Docker)

**Backend** (from repo root):

```powershell
cd apps/agents
pip install -r requirements.txt
cd ../..
$env:PYTHONPATH = "$(Resolve-Path apps/agents)"
python -m uvicorn src.api.main:app --app-dir apps/agents --host 0.0.0.0 --port 8000 --reload
```

**Frontend:**

```powershell
cd apps/frontend
npm install
$env:NEXT_PUBLIC_API_URL = "http://localhost:8000"
npm run dev
```

## LangGraph Studio

The `langgraph.json` in `apps/agents/` registers both graphs:

- **`po_parser`** — 5-node pipeline (classify → extract_po → validate → write_airtable → callback_gas)
- **`image_tagging`** — preprocessor → vision_analyzer → parallel taggers → validator

To run locally:

```bash
cd apps/agents
langgraph dev
```

Studio reads `.env` from the repo root via the `"env": "../../.env"` config.

## API Endpoints

### PO Parser
| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/webhook/email` | GAS email webhook (requires `x-webhook-secret` header) |

### Image Tagging
| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/analyze-image` | Upload and tag a single image |
| `POST` | `/api/bulk-upload` | Upload and tag multiple images |
| `GET`  | `/api/tag-images` | List tagged images |
| `GET`  | `/api/tag-image/{id}` | Get single image tags |
| `GET`  | `/api/search-images` | Filter images by tag categories |
| `GET`  | `/api/available-filters` | Get available filter values |
| `GET`  | `/api/taxonomy` | Get the tag taxonomy |
| `POST` | `/webhook/drive-image` | GAS Drive trigger webhook |

### General
| Method | Path | Description |
|--------|------|-------------|
| `GET`  | `/health` | Health check |

## ngrok (for GAS webhooks)

GAS needs a public URL to reach the local backend. Use ngrok:

```bash
ngrok http 8000 --region eu
```

Set `API_PUBLIC_BASE_URL` in `.env` to the ngrok HTTPS URL, then update the GAS Script Properties with the ngrok-based webhook URLs.

See `apps/agents/docs/shared/setup/14_NGROK_SETUP.md` for detailed instructions.

## Documentation

| Location | Content |
|----------|---------|
| `apps/agents/docs/shared/setup/` | Step-by-step setup guides (01-17) |
| `apps/agents/docs/po_parser/` | PO parser architecture, data flow, LangGraph reference |
| `apps/agents/docs/image_tagging/` | Image tagging guides, architecture, curriculum |
| `gas-scripts/README.md` | GAS Script Properties and deployment |
| `description/` | Original project briefs and sample PO files |

## License

See individual packages.
