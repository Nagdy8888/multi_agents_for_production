# Prerequisites

## Software (Phase 1.5)

| Tool | Purpose | Notes |
|------|---------|--------|
| **Docker Desktop** (Windows/Mac) or **Docker Engine** + Compose (Linux) | Run mock FastAPI in a container | Python 3.11 is **inside** the image — no local Python required for Docker workflow |
| **Node.js 18+** | [clasp](https://github.com/google/clasp) for GAS | `npm install -g @google/clasp` |
| **Git** | Clone / version control | |
| **ngrok** | Tunnel `localhost:8000` so GAS can reach your PC | Free tier is enough for dev; see [03_NGROK_SETUP.md](03_NGROK_SETUP.md) |

Verify:

```bash
docker --version
docker compose version
node --version
npm --version
git --version
ngrok version
```

## Accounts (Phase 1.5)

- **Google account** — Gmail (monitored inbox), Google Apps Script, Google Sheets. No GCP project, no service account, no Google Cloud API keys.

## Accounts (Phase 2+)

- OpenAI, LangSmith, Airtable, etc. — not required for Phase 1.5 mock E2E.

## Network

- Outbound **HTTPS** from Docker (mock callback to `script.google.com`).
- ngrok requires outbound HTTPS to ngrok cloud.

## OS notes

- **Windows:** Docker Desktop with WSL 2 backend recommended.
- **macOS:** Docker Desktop for Apple Silicon or Intel as appropriate.
- **Linux:** Install Docker Engine and the Compose plugin (`docker compose`).

## Troubleshooting

- **Docker won’t start:** Ensure virtualization is enabled in BIOS (Windows), or that Docker Desktop has finished starting (whale icon stable).
- **ngrok not found:** Install from [ngrok download](https://ngrok.com/download) and ensure the binary is on `PATH`.
