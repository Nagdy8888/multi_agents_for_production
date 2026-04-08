# Multi-Agent GAS Scripts

Google Apps Script layer for the Multi-Agent Platform. This repo contains the triggers and callback handlers that connect Google Workspace (Gmail, Drive, Sheets) to the Python backend.

## What it does

- **PO Parser trigger** (`po_parser/EmailTrigger.gs`): Scans Gmail every 5 minutes for unread PO emails, POSTs them to the Python webhook.
- **Image Tagger trigger** (`image_tagger/DriveTrigger.gs`): Scans a Google Drive folder every 5 minutes for new images, POSTs them (base64) to the Python webhook.
- **Callback handler** (`shared/WebApp.gs`): Receives results from Python via `doPost()`, routes to the correct handler based on `payload.type` (`"po_result"` or `"image_result"`), and writes data to Google Sheets.

## Folder structure

```
shared/          # Shared utilities (Config, WebApp router, LabelManager)
po_parser/       # PO-specific (email trigger, sheets writer, notifier)
image_tagger/    # Image-specific (Drive trigger, sheets writer)
```

## Prerequisites

- Node.js (for clasp CLI)
- Google account with Apps Script enabled
- **PO Parser Google Sheet** with tabs: `PO Data`, `PO Items`, `Monitoring Logs`
- **Image Tagger Google Sheet** (separate spreadsheet) with tabs: `Image Tags`, `Image Monitoring`

## Setup

```bash
npm install -g @google/clasp
clasp login
# Create a new GAS project or link to existing
clasp create --title "Multi-Agent Platform GAS" --type standalone --rootDir .
```

## Script Properties

Set in GAS editor: **Project Settings** → **Script properties**

| Key | Description | Used by |
|-----|-------------|---------|
| `WEBHOOK_URL` | Python backend URL for PO emails (e.g. `https://yourserver/webhook/email`) | PO Parser |
| `IMAGE_WEBHOOK_URL` | Python backend URL for images (e.g. `https://yourserver/webhook/drive-image`) | Image Tagger |
| `WEBHOOK_SECRET` | Shared secret sent as `x-webhook-secret` header | Both |
| `GAS_WEBAPP_SECRET` | Secret Python sends in callback JSON body | Both |
| `SPREADSHEET_ID` | Google Sheet ID for PO results | PO Parser |
| `IMAGE_SPREADSHEET_ID` | Google Sheet ID for image results (**separate sheet**) | Image Tagger |
| `NOTIFICATION_RECIPIENTS` | Comma-separated emails for PO notifications | PO Parser |
| `IMAGE_DRIVE_FOLDER_ID` | Google Drive folder ID to watch for images | Image Tagger |

## Deploy

```bash
clasp push
```

Create a **Web App** deployment: Execute as **Me**, Who has access: **Anyone**.

## Triggers

Run once from the GAS editor:

- `installFiveMinuteTrigger()` — PO email trigger (every 5 minutes)
- `installImageTrigger()` — Drive image trigger (every 5 minutes)

## Connection to agents repo

This repo is included as a **Git submodule** in the agents monorepo at `gas-scripts/`. It communicates with the Python backend via HTTP webhooks only.
