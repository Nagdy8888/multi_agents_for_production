# Docker build and run

> **Prev:** [12_DATABASE_SETUP.md](12_DATABASE_SETUP.md) | **Index:** [00_SETUP_INDEX.md](00_SETUP_INDEX.md) | **Next:** [14_NGROK_SETUP.md](14_NGROK_SETUP.md)

From **repo root**:

```bash
docker compose build
docker compose up
```

Detached:

```bash
docker compose up -d
```

## Health

```powershell
curl.exe http://localhost:8000/health
```

Expected JSON includes `"status":"healthy"` and `"timestamp"`.

Frontend: http://localhost:3000

## Logs

```bash
docker compose logs -f
```

## Mock profile (PO wiring test)

```bash
docker compose --profile mock up --build
```

Uses `scripts/test_e2e_mock.py` mounted at `/app/scripts`. Health shows `"mode":"mock"`.

## Stop

```bash
docker compose down
```

Do not run **mock** and **agents** on port 8000 simultaneously.
