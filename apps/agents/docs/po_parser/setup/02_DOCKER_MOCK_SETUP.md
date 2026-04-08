# Docker mock server (Phase 1.5)

**Purpose:** Run `scripts/test_e2e_mock.py` in Docker so GAS can POST to `/webhook/email` and receive a scripted callback to your GAS Web App — validating **secrets, routing, and Sheets/notifications** without OpenAI or Airtable. The real pipeline uses the **production** profile ([12_DOCKER_PRODUCTION_SETUP.md](12_DOCKER_PRODUCTION_SETUP.md)).

## Prerequisites

- Docker installed — [00_PREREQUISITES.md](00_PREREQUISITES.md)
- `.env` configured with mock variables — [01_DEVELOPMENT_SETUP.md](01_DEVELOPMENT_SETUP.md)
- GAS Web App deployed and `GAS_WEBAPP_URL` / `GAS_WEBAPP_SECRET` set — [11_GAS_WEBAPP_SETUP.md](11_GAS_WEBAPP_SETUP.md)

## 1. Configure `.env` (mock subset)

At minimum:

```env
WEBHOOK_SECRET=<same as GAS Script Property WEBHOOK_SECRET>
GAS_WEBAPP_URL=https://script.google.com/macros/s/.../exec
GAS_WEBAPP_SECRET=<same as GAS Script Property GAS_WEBAPP_SECRET>
```

OpenAI / Airtable / LangSmith are **not** required.

## 2. Build

From the repository root:

```bash
docker compose build
```

Expected: image builds without errors.

## 3. Start the mock service

```bash
docker compose --profile mock up
```

**Profile name:** `mock` — only the `mock-server` service starts (see `docker-compose.yml`).

Expected logs (similar to):

- `Uvicorn running on http://0.0.0.0:8000`
- `Application startup complete`

## 4. Verify locally

```bash
curl http://localhost:8000/health
```

Expected:

```json
{"status":"healthy","mode":"mock"}
```

## 5. Expose with ngrok

GAS runs on Google’s servers and cannot reach `http://localhost:8000`. Start a tunnel:

```bash
ngrok http 8000
```

Then set GAS Script Property **`WEBHOOK_URL`** to:

```text
https://<your-ngrok-host>/webhook/email
```

Full steps: [03_NGROK_SETUP.md](03_NGROK_SETUP.md).

## 6. Watch logs

```bash
docker compose --profile mock logs -f
```

During a test you should see:

- Incoming webhook JSON (subject, `message_id`, attachments, …).
- After ~2 seconds: `Callback sent to GAS, response: <status> <body>`.

## 7. Stop

```bash
docker compose --profile mock down
```

## Switching to production

```bash
docker compose --profile mock down
docker compose --profile production up --build
```

Only **one** of `mock` or `production` should bind port **8000** at a time.

## Troubleshooting

| Issue | What to check |
|-------|----------------|
| Build fails | Network; `requirements.txt` present; run from repo root. |
| Container exits immediately | Run `docker compose --profile mock logs` for traceback; missing `.env` or invalid `env_file` path. |
| `401` on webhook | `WEBHOOK_SECRET` in `.env` must match GAS `WEBHOOK_SECRET`. |
| Callback fails | `GAS_WEBAPP_URL` correct; `GAS_WEBAPP_SECRET` matches GAS; Web App deployment updated after `clasp push`. |
| GAS timeout | Mock must return **202** quickly (it does); ensure Docker is running and ngrok points to port 8000. |
