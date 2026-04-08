# Production checklist & reference

> **Prev:** [17_END_TO_END_VERIFICATION.md](17_END_TO_END_VERIFICATION.md) | **Index:** [00_SETUP_INDEX.md](00_SETUP_INDEX.md) | **Next:** —

## Checklist

- [ ] Strong random `WEBHOOK_SECRET` / `GAS_WEBAPP_SECRET` in `.env` **and** GAS
- [ ] `GAS_WEBAPP_URL` matches latest Web App deployment
- [ ] Triggers installed for `processNewEmails` and `processNewImages`
- [ ] Two separate Google Sheets with correct tab names
- [ ] `SPREADSHEET_ID` vs `IMAGE_SPREADSHEET_ID` not swapped
- [ ] Airtable schema matches code (PO)
- [ ] Stable public URL (not ephemeral ngrok) for production
- [ ] `.env` never committed

## Appendix A — Environment variables

| Variable | Where | Agent |
|----------|-------|-------|
| `WEBHOOK_SECRET` | `.env` + GAS | Both |
| `GAS_WEBAPP_SECRET` | `.env` + GAS | Both |
| `GAS_WEBAPP_URL` | `.env` | Python → GAS |
| `OPENAI_API_KEY` | `.env` | Both |
| `OPENAI_*_MODEL` etc. | `.env` | PO / image |
| `AIRTABLE_*` | `.env` | PO |
| `DATABASE_URI` | `.env` | Image (optional) |
| `NEXT_PUBLIC_API_URL` | `.env` | Frontend build |
| `WEBHOOK_URL` | GAS only | PO |
| `IMAGE_WEBHOOK_URL` | GAS only | Image |
| `SPREADSHEET_ID` | GAS only | PO |
| `IMAGE_SPREADSHEET_ID` | GAS only | Image |
| `IMAGE_DRIVE_FOLDER_ID` | GAS only | Image |
| `NOTIFICATION_RECIPIENTS` | GAS only | PO |

## Appendix B — Troubleshooting

| Symptom | Fix |
|---------|-----|
| 401/403 webhook | `WEBHOOK_SECRET` mismatch |
| GAS callback rejected | `GAS_WEBAPP_SECRET` mismatch |
| 502 via ngrok | Backend not on 8000 |
| Import errors locally | `PYTHONPATH` = `apps/agents` |
| Image agent import crash | Missing `OPENAI_API_KEY` in env |
| 503 on tag list/search | No `DATABASE_URI` |

## Appendix C — Windows PowerShell

Use `curl.exe` not `curl`. Example:

```powershell
curl.exe http://localhost:8000/health
```
