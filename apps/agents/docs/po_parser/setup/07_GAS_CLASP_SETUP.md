# Google Apps Script + clasp

**Purpose:** Edit GAS locally under `gas/`, push with **clasp**, and run `processNewEmails` on a schedule.

## 1. Install Node.js

- Download LTS from [https://nodejs.org](https://nodejs.org) (18+).
- Verify:

```bash
node --version
npm --version
```

## 2. Install clasp globally

```bash
npm install -g @google/clasp
clasp --version
```

## 3. Log in to Google

```bash
clasp login
```

Complete the browser OAuth flow. Use the **same Google account** that owns the Gmail inbox you will monitor.

## 4. Enable the Apps Script API

1. Open [https://script.google.com/home/usersettings](https://script.google.com/home/usersettings).
2. Turn **Google Apps Script API** **ON**.

If this stays off, `clasp push` / `clasp create` can fail.

## 5. Link or create the project

This repo keeps GAS files in **`gas/`** with **`gas/.clasp.json`** (`rootDir` is `.`).

### Option A — Create a new script

The repo **does not commit** `gas/.clasp.json` (gitignored). You must run `clasp create` once so Google creates the project and clasp writes the file locally.

From the **repository root**, then into `gas/`:

```bash
cd gas
clasp create --title "PO Parsing Agent" --type standalone --rootDir .
```

This writes **`gas/.clasp.json`** with a real `scriptId`.

If clasp still says a project file already exists, ensure **`gas/.clasp.json` is missing** (delete it), then run the command again.

### Option B — Clone an existing script

```bash
cd gas
clasp clone <SCRIPT_ID> --rootDir .
```

Overwrite local files only if you intend to replace the remote project.

## 6. Push code

```bash
cd gas
clasp push
```

`.claspignore` excludes `**/*.md` so `README.md` is not pushed (optional files only).

## 7. Open in the browser

**clasp 3.x:** use `open-script` (not `open`):

```bash
clasp open-script
```

Use the editor to manage **Script properties**, **Triggers**, and **Deployments** (Web App).

### OAuth scope for time triggers

`gas/appsscript.json` includes `https://www.googleapis.com/auth/script.scriptapp` so **`installFiveMinuteTrigger()`** can create time-driven triggers. After changing scopes, run `clasp push` and complete **re-authorization** in the Apps Script editor.

## 8. Script properties (required)

**Project Settings → Script properties** — add:

| Property | Example / notes |
|----------|-----------------|
| `WEBHOOK_URL` | After ngrok: `https://xxxx.ngrok-free.app/webhook/email` |
| `WEBHOOK_SECRET` | Same as `WEBHOOK_SECRET` in Python `.env` |
| `GAS_WEBAPP_SECRET` | Same as `GAS_WEBAPP_SECRET` in Python `.env` |
| `SPREADSHEET_ID` | From Google Sheets URL — see [09_GOOGLE_SHEETS_SETUP.md](09_GOOGLE_SHEETS_SETUP.md) |
| `NOTIFICATION_RECIPIENTS` | `email1@x.com,email2@x.com` |

## 9. Time-driven trigger (every 5 minutes)

**Option A — UI**

1. In the GAS editor: **Triggers** (alarm clock) → **Add trigger**.
2. Function: `processNewEmails`
3. Event source: **Time-driven**
4. Type: **Minutes timer**
5. Interval: **Every 5 minutes**
6. Save and authorize **all requested scopes** when prompted.

**Option B — one-time install function**

1. Select function **`installFiveMinuteTrigger`** → **Run**.
2. Authorize scopes.

This deletes old `processNewEmails` triggers and adds a new 5-minute trigger.

## 10. View logs

**Easiest (no GCP):** In the Apps Script editor, open **Executions** (clock icon in the left sidebar). `Logger.log` output and errors appear there.

**`clasp logs` (CLI):** Requires the script to be **linked to a Google Cloud project** (Project Settings → Google Cloud Platform (GCP) project). If clasp asks for a **GCP `projectId`**, that is the Cloud project ID from [Google Cloud Console](https://console.cloud.google.com), not the Apps Script `scriptId`. If you skip linking GCP, use **Executions** instead of `clasp logs`.

## 11. After every `clasp push` that changes the Web App

**Deploy → Manage deployments → Edit** → select **New version** → **Deploy**.  
The Web App **URL stays the same**; the new code applies to that URL.

## Troubleshooting

| Issue | Fix |
|-------|-----|
| **`clasp create` says the project file already exists** | A `gas/.clasp.json` file is already on disk (even with empty `scriptId`). **Delete** `gas/.clasp.json`, then run `clasp create` again. This repo **gitignores** `.clasp.json` so the problem should not return after a fresh `git pull`. |
| **`clasp create` replaced `appsscript.json`** | Google’s template may reset timezone and drop Web App / `oauthScopes`. Restore the repo version of `gas/appsscript.json` (Africa/Cairo, scopes, webapp block), then run `clasp push --force`. |
| **Google shows no project / empty `scriptId`** | No remote project is linked until `clasp create` succeeds or you `clasp clone <SCRIPT_ID>`. Use the same Google account in the browser as `clasp login`. |
| “Script API not enabled” | Turn on Apps Script API (step 4). |
| “Insufficient permissions” | Re-run trigger; accept all OAuth scopes (Gmail, Sheets, external URL). |
| `clasp login` expired | `clasp login` again. |
| Push overwrites manual editor changes | Prefer local files as source of truth; `clasp pull` to sync down if needed. |
