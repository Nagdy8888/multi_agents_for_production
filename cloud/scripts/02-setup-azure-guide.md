# Step 2: Create Azure Resources

This guide explains what the setup script does and walks you through running it. By the end, you will have a live backend running on Azure.

---

## What You're Creating

The script creates Azure resources and uses Docker Hub for image storage:

| Resource | What it is | Cost |
|---|---|---|
| **Docker Hub** | A free public/private registry that stores your Docker image. Azure pulls your image from here. | Free (1 private repo, unlimited public) |
| **Resource Group** | A container that holds all your Azure resources together. Think of it as a folder. Deleting the resource group deletes everything inside it. | Free |
| **App Service Plan** | The hosting tier that determines how much CPU/RAM your app gets. B1 is free for Azure for Students. | Free (B1 for students) |
| **Web App (App Service)** | Your actual running application -- the FastAPI backend inside a Docker container, accessible via a public URL like `https://multiagent-app.azurewebsites.net`. | Free (included in plan) |
| **Storage Account + File Share** | Persistent file storage mounted to `/app/uploads` inside the container. Uploaded images survive redeploys. Without this, images would be lost every time you deploy a new version. | Free (5 GB included) |

---

## Before You Run the Script

### 1. Make sure Azure CLI is installed and you're logged in

If you haven't done this yet, follow [01-install-azure-cli.md](01-install-azure-cli.md) first.

Verify you're logged in:

```powershell
az account show --output table
```

You should see your subscription name "Azure for Students".

### 2. Install Docker Desktop

You need Docker installed locally to build and push images to Docker Hub.

1. Go to [docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop/) and download Docker Desktop for Windows
2. Run the installer and follow the prompts (keep all defaults)
3. After installation, Docker Desktop starts automatically -- wait for it to show "Docker Desktop is running" in the system tray
4. Open PowerShell and verify:

```powershell
docker --version
```

You should see something like `Docker version 27.x.x`.

### 3. Create a Docker Hub account

1. Go to [hub.docker.com](https://hub.docker.com) in your browser
2. Click **"Sign Up"** (top right)
3. Create a free account -- remember your **username** (you'll need it)
4. In PowerShell, log in to Docker Hub:

```powershell
docker login
```

Enter your Docker Hub username and password when prompted. You should see `Login Succeeded`.

### 4. Edit the script with your Docker Hub username

Open `02-setup-azure.ps1` in any text editor. Find this line near the top:

```powershell
$DOCKER_HUB_USERNAME = "YOUR_DOCKERHUB_USERNAME"
```

Replace `YOUR_DOCKERHUB_USERNAME` with your actual Docker Hub username (e.g., `mustafanagdy`). Save the file.

### 5. (Optional) Customize other settings

```powershell
$RESOURCE_GROUP    = "multiagent-rg"       # Default is fine
$LOCATION          = "westeurope"          # Change if needed
$APP_SERVICE_PLAN  = "multiagent-plan"     # Default is fine
$APP_NAME          = "multiagent-app"      # Must be globally unique
```

**`$APP_NAME`** becomes part of your URL: `https://multiagent-app.azurewebsites.net`. If this name is already taken by someone else, the script will fail at Step 4. In that case, try adding your initials (e.g., `multiagent-app-mn`).

### 6. Make sure your `.env` file has real values

The script reads your API keys from the `.env` file at the repo root and passes them to Azure. Open `.env` and make sure these keys have actual values (not blank):

- `OPENAI_API_KEY`
- `DATABASE_URI` (your Supabase connection string)
- `AIRTABLE_API_KEY` and `AIRTABLE_BASE_ID`
- `WEBHOOK_SECRET` and `GAS_WEBAPP_SECRET`

---

## Running the Script

1. Make sure **Docker Desktop is running** (check the system tray icon)
2. Open PowerShell
3. Navigate to the project root:

```powershell
cd "c:\Nagdy\Mustafa\MIS\Real Projects\Mulit_agents_for_production"
```

4. Run the script:

```powershell
.\cloud\scripts\02-setup-azure.ps1
```

If you get an error about execution policy, run this first (only needed once):

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Then try running the script again.

---

## What the Script Does (step by step)

Here's what happens when you run the script:

**1. Builds and pushes your Docker image to Docker Hub** -- Docker reads your `apps/agents/Dockerfile`, builds the image locally on your computer, then uploads it to Docker Hub. Takes ~3-5 minutes the first time (subsequent builds are faster because Docker caches layers).

**2. Creates a Resource Group** -- A logical container for all Azure resources. Takes ~5 seconds.

**3. Creates an App Service Plan** -- Sets up the B1 hosting tier (free for Azure for Students). This determines the CPU and RAM available to your app. Takes ~30 seconds.

**4. Creates a Web App** -- Deploys your Docker image from Docker Hub to Azure App Service. Configures all your environment variables from `.env` (OpenAI keys, database connection, etc.). Sets the app to listen on port 8000 (where FastAPI runs). Takes ~1-2 minutes.

**5. Creates a Storage Account** -- An Azure Storage Account with a File Share for persistent file storage. Takes ~30 seconds.

**6. Mounts the File Share to the Web App** -- Attaches the file share to `/app/uploads` inside the container. This means uploaded images are stored on Azure's persistent storage, not inside the container. They survive redeploys, restarts, and scaling events. Takes ~10 seconds.

**7. Creates a Service Principal** -- A special Azure "identity" that lets GitHub Actions deploy updates automatically. Outputs a JSON block you'll need for GitHub Secrets. Takes ~10 seconds.

---

## After the Script Finishes

You should see output that includes:

1. **Your backend URL** -- e.g., `https://multiagent-app.azurewebsites.net`
2. **Your Docker Hub image** -- e.g., `yourusername/multiagent-backend:latest`
3. **Service Principal credentials** -- a JSON block starting with `{`

**Save all three of these.** You'll need them for:
- The backend URL goes into Vercel as `NEXT_PUBLIC_API_URL` (Step 5)
- The Docker Hub image name goes into the GitHub Actions workflow
- The Service Principal JSON goes into GitHub Secrets as `AZURE_CREDENTIALS` (Step 4)

---

## Verify Your Deployment

Open your backend URL in a browser (e.g., `https://multiagent-app.azurewebsites.net`). The first request may take 30-60 seconds because Azure needs to pull the Docker image and start the container.

You should see a JSON response from FastAPI.

To check the app logs (useful for debugging):

```powershell
az webapp log tail --name multiagent-app --resource-group multiagent-rg
```

To restart the app if it's not responding:

```powershell
az webapp restart --name multiagent-app --resource-group multiagent-rg
```

---

## Common Errors

| Error | Fix |
|---|---|
| `docker: command not found` | Docker Desktop is not installed or not running. Install it from docker.com and make sure it's running. |
| `docker push` denied / authentication required | Run `docker login` and enter your Docker Hub username and password. |
| `App name 'multiagent-app' is already taken` | Change `$APP_NAME` in the script to something unique (e.g., `multiagent-app-mn`). |
| App returns 502 or "Application Error" | The container is still starting. Wait 1-2 minutes and refresh. Check logs with `az webapp log tail`. |
| `RequestDisallowedByAzure` | Try a different region. Change `$LOCATION` in the script to `northeurope` or `centralus`. |

---

## Next Step

Once your backend is live and you've saved the three outputs, proceed to:
--> [03-push-to-github.md](03-push-to-github.md) (Push Code to GitHub)
