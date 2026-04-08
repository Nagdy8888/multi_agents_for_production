# End-to-end verification

> **Prev:** [16_LANGGRAPH_STUDIO_SETUP.md](16_LANGGRAPH_STUDIO_SETUP.md) | **Index:** [00_SETUP_INDEX.md](00_SETUP_INDEX.md) | **Next:** [18_PRODUCTION_CHECKLIST.md](18_PRODUCTION_CHECKLIST.md)

## PO parser

- [ ] Docker or mock running; ngrok → `WEBHOOK_URL`
- [ ] Send unread test mail, subject contains `PO` or `Purchase Order`
- [ ] Within ~5 min: GAS execution log shows webhook POST
- [ ] Docker logs: 202 + callback to GAS
- [ ] Sheets: new rows; Airtable: new rows (if configured)
- [ ] Gmail label `PO-Processed` on success path

## Image tagger (Drive)

- [ ] Image in monitored folder; `IMAGE_WEBHOOK_URL` + `IMAGE_DRIVE_FOLDER_ID` set
- [ ] `processNewImages` runs; backend logs show `/webhook/drive-image`
- [ ] Image sheet tabs updated

## Image tagger (UI)

- [ ] http://localhost:3000 — upload works
- [ ] Tags render; no console errors
