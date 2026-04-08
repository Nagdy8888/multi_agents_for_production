# Cloud Deployment Guide

This guide walks you through deploying the **Multi-Agent Platform** to the cloud:

- **Backend** (FastAPI + LangGraph) --> Azure App Service (free for students)
- **Frontend** (Next.js dashboard) --> Vercel (free Hobby plan)
- **Container Registry** --> Docker Hub (free)
- **CI/CD** --> GitHub Actions (auto-deploy on every `git push`)

If you follow every step in order, you will go from zero to a live, publicly accessible application without spending any money.

---

## Architecture

```
GitHub Repository
       |
       | git push to main
       v
GitHub Actions (CI/CD)
       |
       |-- builds Docker image
       |-- pushes to Docker Hub
       |-- deploys to Azure App Service
       |
       v
Azure App Service   <-----  Vercel (Next.js frontend)
  (FastAPI backend)           makes API calls to backend
    Port 8000                 Auto-deployed from GitHub
```

**How it works:**

1. You push code to GitHub.
2. GitHub Actions automatically builds your backend Docker image, pushes it to Docker Hub, and tells Azure App Service to use the new image.
3. Vercel automatically builds and deploys your frontend.
4. The frontend talks to the backend via the Azure URL (e.g., `https://multiagent-app.azurewebsites.net`).

---

## Why Docker Hub + App Service? (not ACR + Container Apps)

Azure for Students subscriptions have a policy that blocks Azure Container Registry (ACR). So we use:

- **Docker Hub** (free) instead of ACR -- stores your Docker images
- **Azure App Service B1** (free for students) instead of Container Apps -- runs your Docker container

The end result is the same: a production-ready Docker-based deployment with CI/CD.

---

## Prerequisites

Before you begin, make sure you have:

- [ ] An **Azure for Students** account -- you already have this
- [ ] A **GitHub account** -- sign up at [github.com](https://github.com) if you don't have one
- [ ] A **Docker Hub account** -- sign up at [hub.docker.com](https://hub.docker.com) (free)
- [ ] **Docker Desktop** installed -- download from [docker.com](https://www.docker.com/products/docker-desktop/)
- [ ] **Git** installed -- verify by running `git --version` in PowerShell
- [ ] Your `.env` file populated with your actual API keys

---

## Deployment Steps (follow in order)

### Step 1: Install the Azure CLI

The Azure CLI is a command-line tool that lets you create and manage Azure resources from your terminal.

--> Follow: [scripts/01-install-azure-cli.md](scripts/01-install-azure-cli.md)

**Time:** ~5 minutes

---

### Step 2: Create Azure Resources

This step builds your Docker image, pushes it to Docker Hub, and creates the Azure App Service to run your backend.

--> Follow the guide: [scripts/02-setup-azure-guide.md](scripts/02-setup-azure-guide.md)
--> Then run the script: [scripts/02-setup-azure.ps1](scripts/02-setup-azure.ps1)

**Time:** ~15 minutes

---

### Step 3: Push Your Code to GitHub

Your code needs to be on GitHub so that both GitHub Actions (CI/CD) and Vercel (frontend) can access it.

--> Follow: [scripts/03-push-to-github.md](scripts/03-push-to-github.md)

**Time:** ~5 minutes

---

### Step 4: Configure GitHub Secrets

GitHub Secrets are encrypted environment variables that your CI/CD pipeline uses at deploy time. This is how your API keys get to Azure without ever being committed to code.

--> Follow: [scripts/04-setup-github-secrets.md](scripts/04-setup-github-secrets.md)

**Time:** ~10 minutes

---

### Step 5: CI/CD Auto-Deploy (automatic -- nothing to do)

Once Steps 3 and 4 are complete, the GitHub Actions workflow file at `.github/workflows/deploy-backend.yml` handles everything automatically.

Every time you `git push` to the `main` branch and your backend code (`apps/agents/`) has changed, GitHub Actions will:

1. Build your Docker image
2. Push it to Docker Hub
3. Deploy the new image to Azure App Service

You can monitor deployments at: GitHub repo > "Actions" tab.

---

### Step 6: Deploy Frontend to Vercel

Vercel provides free hosting for Next.js apps. It auto-deploys from GitHub just like the backend.

--> Follow: [scripts/05-deploy-vercel.md](scripts/05-deploy-vercel.md)

**Time:** ~10 minutes

---

### Step 7: Update Google Apps Script

Your Google Apps Script (GAS) polls Gmail and Google Drive, then forwards data to your backend. After deploying, you must update GAS to point to your new Azure URL instead of `localhost`.

--> Follow: [scripts/06-update-gas-script-properties.md](scripts/06-update-gas-script-properties.md)

**Time:** ~5 minutes

---

## Cost Breakdown

| Service | Free Allowance | Notes |
|---|---|---|
| Azure App Service (B1) | Free for Azure for Students | 1 core, 1.75 GB RAM |
| Azure Storage (LRS) | 5 GB free with free account | Persistent uploads storage |
| Docker Hub | Free | 1 private repo, unlimited public |
| GitHub Actions | 2,000 min/month (private), unlimited (public) | More than enough |
| Vercel (Hobby plan) | Unlimited deployments, 100 GB bandwidth | Free forever |
| **Total** | **$0/month** | Everything is free |

---

## Tear Down (Delete Everything)

If you want to stop all Azure services, run this single command in PowerShell:

```powershell
az group delete --name multiagent-rg --yes --no-wait
```

This deletes the Resource Group and everything inside it (App Service Plan, Web App). It cannot be undone.

For Vercel: Go to your Vercel dashboard > Project > Settings > scroll to bottom > "Delete Project".

For Docker Hub: Go to hub.docker.com > Repositories > click the repo > Settings > Delete repository.

---

## Troubleshooting

### "az is not recognized as a command"

Restart your terminal (close and reopen PowerShell) after installing Azure CLI.

### Docker build fails

Make sure Docker Desktop is running (check the system tray). If you see "Cannot connect to the Docker daemon", start Docker Desktop and wait until it shows "running".

### "docker push" denied / authentication required

Run `docker login` in PowerShell and enter your Docker Hub username and password.

### App returns 502 or "Application Error"

The container is still starting up. Azure App Service can take 30-60 seconds on the first request. Wait and refresh. If it persists, check the logs:

```powershell
az webapp log tail --name multiagent-app --resource-group multiagent-rg
```

### GitHub Actions workflow doesn't trigger

The workflow only runs when files inside `apps/agents/` change. If you only changed frontend code, it won't trigger. Check the Actions tab on GitHub for error details.

### Frontend can't reach the backend

Make sure `NEXT_PUBLIC_API_URL` in Vercel is set to your Azure URL (e.g., `https://multiagent-app.azurewebsites.net`). No trailing slash.

### "RequestDisallowedByAzure" error

Try a different region. Change `$LOCATION` in `02-setup-azure.ps1` to `northeurope`, `centralus`, or `eastus2`.

### "Subscription not found" or "AuthorizationFailed"

Run `az account list --output table` to see your subscriptions. Make sure you're using the right one with `az account set --subscription <id>`.
