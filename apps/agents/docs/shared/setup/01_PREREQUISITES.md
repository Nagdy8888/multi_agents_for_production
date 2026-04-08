# Prerequisites

> **Prev:** [00_SETUP_INDEX.md](00_SETUP_INDEX.md) | **Index:** [00_SETUP_INDEX.md](00_SETUP_INDEX.md) | **Next:** [02_CLONE_AND_REPO_SETUP.md](02_CLONE_AND_REPO_SETUP.md)

## Software

| Tool | Purpose | Verify |
|------|---------|--------|
| Docker Desktop + Compose | Run agents + frontend | `docker --version`, `docker compose version` |
| Node.js 18+ | `clasp` for GAS | `node --version`, `npm --version` |
| Git | Clone + submodule | `git --version` |
| ngrok | Public URL to localhost:8000 | `ngrok version` |
| Python 3.11+ | Local / LangGraph CLI | `python --version` |

**Windows:** Prefer **PowerShell**. For HTTP checks use `curl.exe` or `Invoke-RestMethod`, not `curl` (alias).

## Accounts

- **Google** — Gmail (PO), Drive (images), Sheets (two spreadsheets), Apps Script.
- **OpenAI** — Billing + API key.
- **Airtable** — PO parser storage.
- **ngrok** — Free tier OK for dev.
- **LangSmith** — Optional.

## One-liner verify (PowerShell)

```powershell
docker --version; docker compose version; node --version; npm --version; git --version; ngrok version
```

## One-liner verify (macOS / Linux)

```bash
docker --version && docker compose version && node --version && npm --version && git --version && ngrok version
```
