# Environment variables

> **Prev:** [02_CLONE_AND_REPO_SETUP.md](02_CLONE_AND_REPO_SETUP.md) | **Index:** [00_SETUP_INDEX.md](00_SETUP_INDEX.md) | **Next:** [04_GAS_CLASP_SETUP.md](04_GAS_CLASP_SETUP.md)

## Single root `.env`

All backend and Compose services read **`ROOT/.env`**. Do not add a second `.env` under `apps/agents` or `apps/frontend` for production secrets.

Copy from template:

```powershell
Copy-Item .env.example .env   # PowerShell
```

## Minimum to boot Docker (recommended for first run)

| Variable | Purpose |
|----------|---------|
| `OPENAI_API_KEY` | Required for real image/PO LLM paths |
| `WEBHOOK_SECRET` | Must match GAS Script Property |
| `GAS_WEBAPP_SECRET` | Must match GAS Script Property |
| `GAS_WEBAPP_URL` | Deployed Web App `.../exec` URL |

## Full variable reference

See **Appendix A** in [18_PRODUCTION_CHECKLIST.md](18_PRODUCTION_CHECKLIST.md).

## Generate secrets

```powershell
python -c "import secrets; print(secrets.token_hex(32))"
```

Use output for `WEBHOOK_SECRET` and a **different** value for `GAS_WEBAPP_SECRET`; copy both into GAS **Script properties** with the same names.

## Loading behavior

- **Docker Compose** injects `env_file: .env` → process env (preferred).
- **`load_dotenv()`** in Python (no args) also discovers `.env` when cwd is repo root.
- **`langgraph.json`** uses `"env": "../../.env"` from `apps/agents/`.
