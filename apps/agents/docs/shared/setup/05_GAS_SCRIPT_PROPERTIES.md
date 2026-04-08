# GAS script properties

> **Prev:** [04_GAS_CLASP_SETUP.md](04_GAS_CLASP_SETUP.md) | **Index:** [00_SETUP_INDEX.md](00_SETUP_INDEX.md) | **Next:** [06_GOOGLE_SHEETS_SETUP.md](06_GOOGLE_SHEETS_SETUP.md)

**Apps Script** → Project Settings → **Script properties**.

| Property key | Value | When to set |
|--------------|-------|-------------|
| `WEBHOOK_SECRET` | Same as `ROOT/.env` | Immediately |
| `GAS_WEBAPP_SECRET` | Same as `ROOT/.env` | Immediately |
| `GAS_WEBAPP_URL` | *(not used here; lives in `.env` only)* | — |
| `WEBHOOK_URL` | `https://<ngrok>/webhook/email` | After [14_NGROK_SETUP.md](14_NGROK_SETUP.md) |
| `IMAGE_WEBHOOK_URL` | `https://<ngrok>/webhook/drive-image` | After ngrok |
| `SPREADSHEET_ID` | PO Google Sheet ID | After [06](06_GOOGLE_SHEETS_SETUP.md) |
| `IMAGE_SPREADSHEET_ID` | **Separate** image sheet ID | After [06](06_GOOGLE_SHEETS_SETUP.md) |
| `IMAGE_DRIVE_FOLDER_ID` | Drive folder for incoming images | After [08_GOOGLE_DRIVE_SETUP.md](08_GOOGLE_DRIVE_SETUP.md) |
| `NOTIFICATION_RECIPIENTS` | `a@x.com,b@x.com` | Before PO E2E |

`getConfig()` throws if a property is missing — add keys only when you have values, or temporarily disable triggers.

**Come back** after steps **06**, **08**, and **14** to finish URL/ID properties.
