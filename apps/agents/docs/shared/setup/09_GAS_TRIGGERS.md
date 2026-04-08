# GAS triggers & callback smoke test

> **Prev:** [08_GOOGLE_DRIVE_SETUP.md](08_GOOGLE_DRIVE_SETUP.md) | **Index:** [00_SETUP_INDEX.md](00_SETUP_INDEX.md) | **Next:** [10_OPENAI_SETUP.md](10_OPENAI_SETUP.md)

## PO email trigger

Apps Script → **Triggers** → **Add trigger**

- Function: `processNewEmails`
- Event source: **Time-driven** → **Every 5 minutes**

Or run `installFiveMinuteTrigger()` once from the editor.

## Image Drive trigger

- Function: `processNewImages`
- **Time-driven** → **Every 5 minutes**

Or run `installImageTrigger()` once.

## Callback test (optional)

POST to your Web App URL with JSON body including `secret` = `GAS_WEBAPP_SECRET` and test fields. Use `curl.exe` on Windows.

```powershell
$uri = "YOUR_WEB_APP_URL"
$body = @{ secret = "YOUR_GAS_WEBAPP_SECRET"; message_id = "test"; status = "error"; errors = @("test"); type = "po_result" } | ConvertTo-Json
Invoke-RestMethod -Uri $uri -Method Post -Body $body -ContentType "application/json; charset=utf-8"
```

Redeploy Web App after `doPost` changes.
