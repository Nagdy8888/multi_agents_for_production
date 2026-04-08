# Multi-Agent Platform — Setup guide index

Follow these guides **in order**. Paths are relative to the **monorepo root** (`Multi_agents/`) unless noted.

> **Prev:** — | **Index:** (you are here) | **Next:** [01_PREREQUISITES.md](01_PREREQUISITES.md)

## Layout

| Path | Role |
|------|------|
| `apps/agents/` | Python backend (port **8000**) |
| `apps/frontend/` | Next.js UI (port **3000**) |
| `gas-scripts/` | Apps Script (**submodule**) — Gmail + Drive triggers, Web App callbacks |
| `.env` | **Single** env file at repo root |

## Ordered guides

| # | Guide | Purpose |
|---|-------|---------|
| 01 | [Prerequisites](01_PREREQUISITES.md) | Tools & accounts |
| 02 | [Clone & repo](02_CLONE_AND_REPO_SETUP.md) | Clone, submodule, tree |
| 03 | [Environment variables](03_ENVIRONMENT_VARIABLES.md) | `.env` / `.env.example` |
| 04 | [GAS + clasp](04_GAS_CLASP_SETUP.md) | clasp, push, Web App deploy |
| 05 | [Script properties](05_GAS_SCRIPT_PROPERTIES.md) | All GAS keys + secrets |
| 06 | [Google Sheets](06_GOOGLE_SHEETS_SETUP.md) | PO sheet + **separate** image sheet |
| 07 | [Gmail](07_GMAIL_SETUP.md) | Labels & search query |
| 08 | [Google Drive](08_GOOGLE_DRIVE_SETUP.md) | Image folder ID |
| 09 | [GAS triggers](09_GAS_TRIGGERS.md) | 5‑minute triggers + callback test |
| 10 | [OpenAI](10_OPENAI_SETUP.md) | API keys in `.env` |
| 11 | [Airtable](11_AIRTABLE_SETUP.md) | PO tables & PAT |
| 12 | [Database](12_DATABASE_SETUP.md) | Optional Supabase / Postgres |
| 13 | [Docker](13_DOCKER_BUILD_AND_RUN.md) | `docker compose up` |
| 14 | [ngrok](14_NGROK_SETUP.md) | Tunnel for GAS → localhost |
| 15 | [LangSmith](15_LANGSMITH_SETUP.md) | Optional tracing |
| 16 | [LangGraph Studio](16_LANGGRAPH_STUDIO_SETUP.md) | Optional local Studio |
| 17 | [E2E verification](17_END_TO_END_VERIFICATION.md) | Checklists |
| 18 | [Production](18_PRODUCTION_CHECKLIST.md) | Final checks + troubleshooting |

## Quick ports

- **8000** — FastAPI (PO + image APIs + webhooks)
- **3000** — Next.js
- **2024** — `langgraph dev` (optional)

## Related

- Architecture: [../ARCHITECTURE_OVERVIEW.md](../ARCHITECTURE_OVERVIEW.md)
- Folder blueprint: [../FOLDER_STRUCTURE.md](../FOLDER_STRUCTURE.md)
- PO-specific setup (legacy paths): [../../po_parser/setup/](../../po_parser/setup/)
