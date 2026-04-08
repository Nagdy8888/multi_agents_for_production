# Development setup (repo + `.env`)

This project runs the **mock server** and **production API** via **Docker** — no local Python venv is required for the primary workflow.

## 1. Clone and enter the repo

```bash
git clone <your-repo-url>
cd "PO Parsing AI Agent"
```

(Adjust folder name if different.)

## 2. Environment file

Copy the example env file:

**Windows (PowerShell):**

```powershell
Copy-Item .env.example .env
```

**macOS / Linux:**

```bash
cp .env.example .env
```

## 3. Fill `.env` for Phase 1.5 (mock only)

Minimum variables:

| Variable | Description |
|----------|-------------|
| `WEBHOOK_SECRET` | Same string as GAS Script Property `WEBHOOK_SECRET`. Use a long random value (e.g. `python -c "import secrets; print(secrets.token_hex(32))"`). |
| `GAS_WEBAPP_URL` | Full deployed Web App URL from Apps Script (see [11_GAS_WEBAPP_SETUP.md](11_GAS_WEBAPP_SETUP.md)). |
| `GAS_WEBAPP_SECRET` | Same string as GAS Script Property `GAS_WEBAPP_SECRET`. |

You do **not** need OpenAI, LangSmith, or Airtable keys for the mock server.

## 4. Build Docker images

From the **repository root** (where `docker-compose.yml` lives):

```bash
docker compose build
```

## 5. Run the mock server

```bash
docker compose --profile mock up
```

Expected: Uvicorn logs and `Application startup complete` / listening on `0.0.0.0:8000`.

## 6. Health check

In another terminal:

```bash
curl http://localhost:8000/health
```

**Windows PowerShell:** use **`curl.exe`** (or `Invoke-RestMethod`) — plain `curl` is an alias and behaves differently. See **Windows PowerShell** under [12_DOCKER_PRODUCTION_SETUP.md](12_DOCKER_PRODUCTION_SETUP.md).

**Mock profile** (`docker compose --profile mock`): the container runs `scripts/test_e2e_mock.py`, which returns:

```json
{"status":"healthy","mode":"mock"}
```

**Production profile** (`docker compose --profile production`): `src.api.main` returns `status` and a UTC **`timestamp`** only (no `mode` field). See [12_DOCKER_PRODUCTION_SETUP.md](12_DOCKER_PRODUCTION_SETUP.md).

## 7. Expose to the internet (GAS)

For Google Apps Script to call your machine, use ngrok — [03_NGROK_SETUP.md](03_NGROK_SETUP.md).

## 8. Production pipeline (OpenAI + Airtable)

- Copy variables from [.env.example](../../.env.example) into `.env` (`OPENAI_*`, `AIRTABLE_*`, optional `LANGCHAIN_*`, optional `AIRTABLE_ATTACHMENTS_FIELD`).
- Run: `docker compose --profile production up --build` (see [12_DOCKER_PRODUCTION_SETUP.md](12_DOCKER_PRODUCTION_SETUP.md)).
- Reference: [../documentations/ENVIRONMENT_VARIABLES.md](../documentations/ENVIRONMENT_VARIABLES.md).

## Troubleshooting

- **`env_file` / `.env` not found:** Create `.env` from `.env.example` in the repo root (same folder as `docker-compose.yml`).
- **Port 8000 in use:** Stop the other process or change the host port in `docker-compose.yml` (e.g. `8001:8000`) and use `ngrok http 8001` consistently.
