# Phase 1.5 — E2E verification checklist

Complete [setup/README.md](README.md) **in order** before this checklist.

## Prerequisites snapshot

- [ ] `docker compose --profile mock up` — mock responds at `http://localhost:8000/health` with `"mode":"mock"`.
- [ ] `ngrok http 8000` — HTTPS URL copied.
- [ ] GAS **Script properties:** `WEBHOOK_URL`, `WEBHOOK_SECRET`, `GAS_WEBAPP_SECRET`, `SPREADSHEET_ID`, `NOTIFICATION_RECIPIENTS`.
- [ ] `.env` has `WEBHOOK_SECRET`, `GAS_WEBAPP_URL`, `GAS_WEBAPP_SECRET` aligned with GAS.
- [ ] Google Sheet has three tabs with correct row-1 headers — [09_GOOGLE_SHEETS_SETUP.md](09_GOOGLE_SHEETS_SETUP.md).
- [ ] Time-driven trigger on `processNewEmails` (every 5 min) **or** `installFiveMinuteTrigger` run once.
- [ ] Web App deployed and **new version** published after latest `clasp push`.

## Test execution

1. Send an email **to the monitored Gmail** with subject like **`Test PO 12345`** (must match search: PO or “Purchase Order”).
2. Leave it **unread**.
3. Wait up to **5 minutes** (trigger interval).

## Verification (10 checks)

| # | Check | Where | Expected |
|---|--------|-------|----------|
| 1 | GAS picked up the email | GAS **Executions** / `clasp logs` | Log contains **Processing email: Test PO 12345** (see `gas/Code.gs`). |
| 2 | Webhook reached Python | Docker logs for mock | Log line with **received webhook** / payload with subject, body, sender. |
| 3 | Payload shape | Docker logs | Fields: `subject`, `body`, `sender`, `timestamp`, `message_id`, `attachments` (array). |
| 4 | Auth OK | Docker logs | No **401**; request accepted (202). |
| 5 | Callback to GAS | Docker logs | **Callback sent to GAS, response:** … |
| 6 | PO Data row | Google Sheet **PO Data** | Row with **MOCK-001**, **Mock Test Company**, etc. |
| 7 | PO Items row | **PO Items** | **TEST-SKU-001**, quantity **100**, etc. |
| 8 | Monitoring row | **Monitoring Logs** | Timestamp, `message_id`, success path. |
| 9 | Notification | Inbox of `NOTIFICATION_RECIPIENTS` | HTML email about processed PO. |
| 10 | Gmail label | Original test message | Label **PO-Processed** on the thread. |

## Optional error scenarios (after happy path)

| Scenario | Action | Expected |
|----------|--------|----------|
| Non-PO | Send subject **Meeting tomorrow** (unread) | No webhook / no match for search — no processing. |
| Server down | Stop Docker; send PO-like mail | **PO-Processing-Failed** label after failed `UrlFetchApp`. |
| Wrong callback secret | Temporarily change `GAS_WEBAPP_SECRET` in `.env` only | GAS rejects callback; no success rows / check logs. |
| Body-only PO | Subject contains PO, no attachments | Webhook fires; `attachments: []`. |

## When everything passes

Phase 1.5 (mock E2E) is complete. Next: fill production `.env`, run [12_DOCKER_PRODUCTION_SETUP.md](12_DOCKER_PRODUCTION_SETUP.md), and use [../documentations/TESTING_GUIDE.md](../documentations/TESTING_GUIDE.md). Advance other project phases only with explicit approval per `.cursor/rules/phase-gates.mdc`.

**Reference:** `.cursor/plans/po_parsing_ai_agent_211da517.plan.md` (Phase 1.5 section).
