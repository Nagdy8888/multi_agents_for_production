# Step 4: Configure GitHub Secrets

## Why Do You Need GitHub Secrets?

Your application needs API keys to work (OpenAI, Supabase, Airtable, etc.). These keys are in your `.env` file locally, but you should **never** commit them to GitHub -- if someone finds them, they can use your accounts and run up charges on your credit card.

**GitHub Secrets** solve this problem. They are encrypted variables stored in your GitHub repository settings. Only your GitHub Actions workflows can read them, and they're never visible in logs or to anyone browsing your code.

When GitHub Actions deploys your app, it reads these secrets and passes them to Azure as environment variables -- your app gets the keys it needs without them ever appearing in your code.

---

## How to Add a Secret (do this for each secret below)

1. Open your browser and go to your GitHub repository page
2. Click the **"Settings"** tab in the top navigation bar (the gear icon, far right after Code/Issues/Pull requests/Actions)
3. In the left sidebar, scroll down and click **"Secrets and variables"**
4. In the dropdown that appears, click **"Actions"**
5. Click the green **"New repository secret"** button
6. Fill in:
   - **Name**: The secret name (e.g., `OPENAI_API_KEY`) -- use EXACTLY the names listed below
   - **Secret**: The value (e.g., `sk-xxxxxxxxxxxx`) -- paste it from your `.env` file
7. Click **"Add secret"**

Repeat this process for every secret listed below.

---

## Secrets to Add

### Azure Credentials (from the setup script output in Step 2)

These come from the output of `02-setup-azure.ps1`. If you didn't save them, you can regenerate them (see the "Lost Your Credentials?" section at the bottom).

#### Secret 1: `AZURE_CREDENTIALS`

- **Name**: `AZURE_CREDENTIALS`
- **Value**: The entire JSON block that the setup script printed under "SERVICE PRINCIPAL CREDENTIALS"
- It looks like this (your values will be different):

```json
{
  "clientId": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "clientSecret": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
  "subscriptionId": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "tenantId": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "activeDirectoryEndpointUrl": "https://login.microsoftonline.com",
  "resourceManagerEndpointUrl": "https://management.azure.com/",
  "activeDirectoryGraphResourceId": "https://graph.windows.net/",
  "sqlManagementEndpointUrl": "https://management.core.windows.net:8443/",
  "galleryEndpointUrl": "https://gallery.azure.com/",
  "managementEndpointUrl": "https://management.core.windows.net/"
}
```

Copy and paste the **entire** JSON block as the secret value, including the curly braces.

---

### Docker Hub Credentials

You need these so GitHub Actions can push Docker images to your Docker Hub account.

#### Secret 2: `DOCKERHUB_USERNAME`

- **Name**: `DOCKERHUB_USERNAME`
- **Value**: Your Docker Hub username (the same one you put in the setup script)

#### Secret 3: `DOCKERHUB_TOKEN`

- **Name**: `DOCKERHUB_TOKEN`
- **Value**: A Docker Hub **Access Token** (NOT your password). Create one like this:
  1. Go to [hub.docker.com](https://hub.docker.com) and sign in
  2. Click your profile picture (top-right) > **"Account Settings"**
  3. In the left sidebar, click **"Personal access tokens"**
  4. Click **"Generate new token"**
  5. Give it a name like `github-actions`
  6. Set access permissions to **"Read, Write, Delete"**
  7. Click **"Generate"**
  8. **Copy the token immediately** -- you can't see it again!
  9. Paste this token as the secret value in GitHub

---

### Application Secrets (from your .env file)

Open your `.env` file in a text editor and copy the values for each of these. Only add secrets that have actual values (skip blank ones).

#### Secret 4: `WEBHOOK_SECRET`

- **Name**: `WEBHOOK_SECRET`
- **Value**: Copy the value of `WEBHOOK_SECRET` from your `.env` file
- **Purpose**: Authenticates incoming webhooks from Google Apps Script

#### Secret 5: `GAS_WEBAPP_SECRET`

- **Name**: `GAS_WEBAPP_SECRET`
- **Value**: Copy the value of `GAS_WEBAPP_SECRET` from your `.env`
- **Purpose**: Authenticates callbacks to Google Apps Script

#### Secret 6: `GAS_WEBAPP_URL`

- **Name**: `GAS_WEBAPP_URL`
- **Value**: Copy the value of `GAS_WEBAPP_URL` from your `.env`
- **Purpose**: The URL of your Google Apps Script web app

#### Secret 7: `OPENAI_API_KEY`

- **Name**: `OPENAI_API_KEY`
- **Value**: Copy the value of `OPENAI_API_KEY` from your `.env`
- **Purpose**: Authenticates with OpenAI for GPT-4o vision, classification, and extraction

#### Secret 8: `AIRTABLE_API_KEY`

- **Name**: `AIRTABLE_API_KEY`
- **Value**: Copy the value of `AIRTABLE_API_KEY` from your `.env`
- **Purpose**: Authenticates with Airtable for PO data storage

#### Secret 9: `AIRTABLE_BASE_ID`

- **Name**: `AIRTABLE_BASE_ID`
- **Value**: Copy the value of `AIRTABLE_BASE_ID` from your `.env`
- **Purpose**: Identifies which Airtable base to write PO records to

#### Secret 10: `AIRTABLE_PO_TABLE_ID`

- **Name**: `AIRTABLE_PO_TABLE_ID`
- **Value**: Copy from `.env` (skip if blank)
- **Purpose**: Table ID for PO record URLs

#### Secret 11: `AIRTABLE_PO_VIEW_ID`

- **Name**: `AIRTABLE_PO_VIEW_ID`
- **Value**: Copy from `.env` (skip if blank)
- **Purpose**: View ID for PO record URLs

#### Secret 12: `AIRTABLE_ITEMS_TABLE_ID`

- **Name**: `AIRTABLE_ITEMS_TABLE_ID`
- **Value**: Copy from `.env` (skip if blank)
- **Purpose**: Table ID for PO Items record URLs

#### Secret 13: `AIRTABLE_ITEMS_VIEW_ID`

- **Name**: `AIRTABLE_ITEMS_VIEW_ID`
- **Value**: Copy from `.env` (skip if blank)
- **Purpose**: View ID for PO Items record URLs

#### Secret 14: `DATABASE_URI`

- **Name**: `DATABASE_URI`
- **Value**: Copy the value of `DATABASE_URI` from your `.env`
- **Purpose**: PostgreSQL connection string for Supabase (used by the Image Tagging agent)

#### Secret 15 (optional): `LANGCHAIN_API_KEY`

- **Name**: `LANGCHAIN_API_KEY`
- **Value**: Copy from `.env` (only if you use LangSmith tracing)
- **Purpose**: Sends trace data to LangSmith for debugging

---

## Verify Your Secrets

After adding all secrets:

1. Go to your GitHub repository > **Settings** > **Secrets and variables** > **Actions**
2. You should see a list of all the secrets you added
3. Each secret shows its name and the date it was last updated
4. You **cannot** view the actual values (they're encrypted) -- this is by design

The minimum required secrets for CI/CD to work are:
- `AZURE_CREDENTIALS`
- `DOCKERHUB_USERNAME`
- `DOCKERHUB_TOKEN`
- `OPENAI_API_KEY`
- `DATABASE_URI`

The CI/CD pipeline will fail if these are missing.

---

## Lost Your Credentials?

### Regenerate Service Principal (AZURE_CREDENTIALS)

If you lost the Service Principal JSON from Step 2, run this in PowerShell:

```powershell
$SUBSCRIPTION_ID = az account show --query id --output tsv

az ad sp create-for-rbac `
    --name "multiagent-github-deploy" `
    --role contributor `
    --scopes "/subscriptions/$SUBSCRIPTION_ID/resourceGroups/multiagent-rg" `
    --sdk-auth
```

Copy the JSON output and update the `AZURE_CREDENTIALS` secret in GitHub.

### Regenerate Docker Hub Token

Go to [hub.docker.com](https://hub.docker.com) > Account Settings > Personal access tokens > Generate new token.

---

## Next Step

Once all secrets are added, your CI/CD pipeline is ready. To trigger a deployment now, make any small change to a file in `apps/agents/`, commit, and push:

```powershell
git add .
git commit -m "Trigger first CI/CD deployment"
git push origin main
```

Then watch the deployment:
1. Go to your GitHub repository
2. Click the **"Actions"** tab
3. You should see a workflow run in progress
4. Click on it to see the live logs

Proceed to: --> [05-deploy-vercel.md](05-deploy-vercel.md) (Deploy Frontend to Vercel)
