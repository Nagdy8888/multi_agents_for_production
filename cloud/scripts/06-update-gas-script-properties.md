# Step 7: Update Google Apps Script to Use Your Azure URL

Your Google Apps Script (GAS) is what connects Gmail and Google Drive to your backend. Right now it's configured to talk to `localhost:8000`, which only works on your computer. After deploying to Azure, you need to tell GAS to use your new public Azure URL instead.

Without this step, GAS will keep trying to reach `localhost:8000` (which doesn't exist from Google's servers), and:
- New Gmail PO emails will NOT be processed
- New Google Drive images will NOT be analyzed

---

## What You Need

Your Azure backend URL from Step 2. It looks like:

```
https://multiagent-app.azurewebsites.net
```

If you forgot it, run this in PowerShell:

```powershell
az webapp show --name multiagent-app --resource-group multiagent-rg --query "defaultHostName" --output tsv
```

Your URL is `https://` followed by the output.

---

## Update Script Properties

### 7.1 Open Google Apps Script

1. Open your browser and go to [script.google.com](https://script.google.com)
2. Sign in with the same Google account that owns the GAS project
3. Find your project in the list (it might be called "PO Parser" or "Multi-Agent" or similar)
4. Click on it to open the editor

### 7.2 Go to Script Properties

1. In the left sidebar of the Apps Script editor, click the **gear icon** (Project Settings)
2. Scroll down to the **"Script Properties"** section
3. You should see a list of key-value pairs

### 7.3 Update the Webhook URLs

Find and update these properties. Click the **pencil icon** (edit) next to each one:

#### For the PO Parser agent:

| Property Name | Old Value | New Value |
|---|---|---|
| `WEBHOOK_URL` | `http://localhost:8000/webhook/email` or similar | `https://multiagent-app.azurewebsites.net/webhook/email` |

#### For the Image Tagging agent:

| Property Name | Old Value | New Value |
|---|---|---|
| `IMAGE_WEBHOOK_URL` | `http://localhost:8000/webhook/drive-image` or similar | `https://multiagent-app.azurewebsites.net/webhook/drive-image` |

Replace `multiagent-app` with your actual app name if you changed it in the setup script.

### 7.4 Verify the Secrets Match

While you're in Script Properties, also check that these secrets match your `.env` file:

| Property Name | Should Match |
|---|---|
| `WEBHOOK_SECRET` | The `WEBHOOK_SECRET` value in your `.env` |
| `GAS_WEBAPP_SECRET` | The `GAS_WEBAPP_SECRET` value in your `.env` |

If they don't match, the backend will reject requests from GAS with a 403 error.

### 7.5 Save

Click **"Save script properties"** (or the save button). Changes take effect immediately.

---

## Verify It Works

### Test the PO Parser

1. Send a test email with a PO PDF attachment to the Gmail inbox that GAS monitors
2. Wait up to 5 minutes (GAS runs on a timer)
3. Check your Azure backend logs:

```powershell
az webapp log tail --name multiagent-app --resource-group multiagent-rg
```

You should see a log entry like `POST /webhook/email` with status 202.

4. Check Airtable for the new PO record

### Test the Image Tagger (Drive flow)

1. Drop a test image into the Google Drive folder that GAS watches
2. Wait up to 5 minutes
3. Check the backend logs for `POST /webhook/drive-image`
4. Check the frontend dashboard -- the image should appear with tags

### Test the Image Tagger (Frontend upload)

1. Open your Vercel frontend URL (e.g., `https://your-project.vercel.app`)
2. Upload an image through the dashboard
3. It should be analyzed and displayed with tags immediately

---

## Common Errors

| Error | Fix |
|---|---|
| GAS shows "Exception: Request failed with 403" | `WEBHOOK_SECRET` in GAS Script Properties doesn't match the value in Azure. Update it to match your `.env`. |
| GAS shows "Exception: Request failed with 502" | Your Azure app is still starting up. Wait 1-2 minutes and try again. Or check backend logs for crashes. |
| GAS shows "Exception: Timeout" | The Azure app might be sleeping (scaled to zero). The first request wakes it up and can take 30+ seconds. GAS may timeout. Try again -- the second call should work. |
| GAS shows "Exception: DNS error" or "Address not found" | The `WEBHOOK_URL` is wrong. Double-check the URL matches your Azure App Service URL exactly. |
| PO processed but nothing in Google Sheets | Check that `GAS_WEBAPP_URL` in your Azure `.env` points to the correct Google Apps Script Web App URL, and `GAS_WEBAPP_SECRET` matches on both sides. |

---

## Previous Step

<-- [05-deploy-vercel.md](05-deploy-vercel.md) (Deploy Frontend to Vercel)

## You're Done!

After this step, your entire system is live:

- **Gmail PO emails** --> GAS (polls every 5 min) --> Azure backend --> OpenAI analysis --> Airtable + Google Sheets
- **Google Drive images** --> GAS (polls) --> Azure backend --> GPT-4o vision --> Supabase + Frontend
- **Frontend uploads** --> Vercel dashboard --> Azure backend --> GPT-4o vision --> Supabase + Frontend
- **All image files** are stored persistently on Azure Files (survive redeploys)
- **CI/CD** auto-deploys on every `git push` to main
