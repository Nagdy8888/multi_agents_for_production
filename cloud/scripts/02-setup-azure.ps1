# ==============================================================================
# Azure Resource Provisioning Script
# Multi-Agent Platform -- Backend Deployment
#
# Deploys the FastAPI backend using:
#   - Docker Hub (free) as the container registry
#   - Azure App Service (B1, free for students) as the hosting platform
#
# Read 02-setup-azure-guide.md BEFORE running this script.
#
# Prerequisites:
#   - Azure CLI installed and logged in (az login)
#   - Docker Desktop installed and running (needed to build and push images)
#   - Docker Hub account created (free at hub.docker.com)
#   - .env file at repo root with your API keys filled in
# ==============================================================================

# ---- CONFIGURATION (edit these) ----------------------------------------------

$RESOURCE_GROUP    = "multiagent-rg"
$LOCATION          = "polandcentral"
$APP_SERVICE_PLAN  = "multiagent-plan"
$APP_NAME          = "multiagent-nagdy"
$IMAGE_NAME        = "multiagent-backend"
$STORAGE_ACCOUNT   = "multiagentstorage"
$SHARE_NAME        = "uploads"

# Docker Hub settings -- CHANGE THESE to your Docker Hub username
$DOCKER_HUB_USERNAME = "nagdy8888"

# ---- VALIDATE DOCKER HUB USERNAME -------------------------------------------

if ($DOCKER_HUB_USERNAME -eq "YOUR_DOCKERHUB_USERNAME") {
    Write-Error "ERROR: You must set your Docker Hub username on line 28 of this script."
    Write-Error "Open this file, find `$DOCKER_HUB_USERNAME and replace YOUR_DOCKERHUB_USERNAME with your actual Docker Hub username."
    exit 1
}

$FULL_IMAGE = "${DOCKER_HUB_USERNAME}/${IMAGE_NAME}:latest"

# Path to the project root (where .env lives)
$PROJECT_ROOT = Split-Path -Parent (Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path))

# ---- LOAD ENVIRONMENT VARIABLES FROM .env ------------------------------------

$envFile = Join-Path $PROJECT_ROOT ".env"

if (-not (Test-Path $envFile)) {
    Write-Error "ERROR: .env file not found at $envFile"
    Write-Error "Make sure you have a .env file in the repo root with your API keys."
    exit 1
}

Write-Host "`n=== Loading environment variables from .env ===" -ForegroundColor Cyan

$envVars = @{}
Get-Content $envFile | ForEach-Object {
    $line = $_.Trim()
    if ($line -and -not $line.StartsWith("#")) {
        $parts = $line -split "=", 2
        if ($parts.Count -eq 2 -and $parts[1].Trim() -ne "") {
            $envVars[$parts[0].Trim()] = $parts[1].Trim()
        }
    }
}

Write-Host "Loaded $($envVars.Count) environment variables from .env" -ForegroundColor Green

# ---- STEP 1: BUILD AND PUSH DOCKER IMAGE TO DOCKER HUB ----------------------

Write-Host "`n=== Step 1/7: Building and pushing Docker image to Docker Hub ===" -ForegroundColor Cyan
Write-Host "Make sure Docker Desktop is running and you're logged in to Docker Hub." -ForegroundColor Yellow
Write-Host "If not logged in, run: docker login" -ForegroundColor Yellow

$dockerContext = Join-Path $PROJECT_ROOT "apps\agents"

Write-Host "Building image '$FULL_IMAGE' from $dockerContext ..." -ForegroundColor White

docker build -t $FULL_IMAGE $dockerContext

if ($LASTEXITCODE -ne 0) {
    Write-Error "Docker build failed. Make sure Docker Desktop is running and check your Dockerfile."
    exit 1
}

Write-Host "Pushing image to Docker Hub ..." -ForegroundColor White

docker push $FULL_IMAGE

if ($LASTEXITCODE -ne 0) {
    Write-Error "Docker push failed. Make sure you're logged in: run 'docker login' first."
    exit 1
}

Write-Host "Image pushed to Docker Hub: $FULL_IMAGE" -ForegroundColor Green

# ---- STEP 2: CREATE RESOURCE GROUP ------------------------------------------

Write-Host "`n=== Step 2/7: Creating Resource Group '$RESOURCE_GROUP' ===" -ForegroundColor Cyan

az group create `
    --name $RESOURCE_GROUP `
    --location $LOCATION `
    --output none

if ($LASTEXITCODE -ne 0) {
    Write-Error "Failed to create resource group. Are you logged in? Run 'az login' first."
    exit 1
}

Write-Host "Resource Group created." -ForegroundColor Green

# ---- STEP 3: CREATE APP SERVICE PLAN ----------------------------------------

Write-Host "`n=== Step 3/7: Creating App Service Plan (B1 -- free for students) ===" -ForegroundColor Cyan

az appservice plan create `
    --name $APP_SERVICE_PLAN `
    --resource-group $RESOURCE_GROUP `
    --location $LOCATION `
    --is-linux `
    --sku B1 `
    --output none

if ($LASTEXITCODE -ne 0) {
    Write-Error "Failed to create App Service Plan. The B1 SKU may not be available in this region."
    Write-Error "Try changing `$LOCATION to 'northeurope' or 'eastus2'."
    exit 1
}

Write-Host "App Service Plan created (B1 Linux)." -ForegroundColor Green

# ---- STEP 4: CREATE WEB APP FROM DOCKER IMAGE -------------------------------

Write-Host "`n=== Step 4/7: Creating Web App '$APP_NAME' ===" -ForegroundColor Cyan

az webapp create `
    --name $APP_NAME `
    --resource-group $RESOURCE_GROUP `
    --plan $APP_SERVICE_PLAN `
    --container-image-name $FULL_IMAGE `
    --output none

if ($LASTEXITCODE -ne 0) {
    Write-Error "Failed to create Web App. The name '$APP_NAME' may already be taken globally."
    Write-Error "Try a different name (e.g., 'multiagent-app-mn')."
    exit 1
}

Write-Host "Web App created." -ForegroundColor Green

# Configure the app port (FastAPI listens on 8000)
Write-Host "Configuring app settings..." -ForegroundColor White

az webapp config appsettings set `
    --name $APP_NAME `
    --resource-group $RESOURCE_GROUP `
    --settings WEBSITES_PORT=8000 `
    --output none

# Set all environment variables from .env
$appSettings = @()
foreach ($key in $envVars.Keys) {
    $val = $envVars[$key]
    $appSettings += "${key}=${val}"
}

# Override the public URL to the Azure domain
$appSettings += "API_PUBLIC_BASE_URL=https://${APP_NAME}.azurewebsites.net"
$appSettings += "NEXT_PUBLIC_API_URL=https://${APP_NAME}.azurewebsites.net"

az webapp config appsettings set `
    --name $APP_NAME `
    --resource-group $RESOURCE_GROUP `
    --settings $appSettings `
    --output none

if ($LASTEXITCODE -ne 0) {
    Write-Error "Failed to set app settings."
    exit 1
}

# Enable continuous deployment from Docker Hub
az webapp config container set `
    --name $APP_NAME `
    --resource-group $RESOURCE_GROUP `
    --container-image-name $FULL_IMAGE `
    --output none

Write-Host "App configured with environment variables." -ForegroundColor Green

# ---- STEP 5: CREATE STORAGE ACCOUNT FOR PERSISTENT UPLOADS ------------------

Write-Host "`n=== Step 5/7: Creating Storage Account for persistent uploads ===" -ForegroundColor Cyan

az storage account create `
    --name $STORAGE_ACCOUNT `
    --resource-group $RESOURCE_GROUP `
    --location $LOCATION `
    --sku Standard_LRS `
    --output none

if ($LASTEXITCODE -ne 0) {
    Write-Host "WARNING: Storage Account creation failed (likely blocked by subscription policy)." -ForegroundColor Yellow
    Write-Host "Skipping persistent storage. Uploads will work but won't survive redeploys." -ForegroundColor Yellow
    Write-Host "This is fine for a demo/learning project." -ForegroundColor Yellow
} else {
    Write-Host "Storage Account created." -ForegroundColor Green

    # ---- STEP 6: CREATE FILE SHARE AND MOUNT TO WEB APP -------------------------

    Write-Host "`n=== Step 6/7: Mounting persistent file share for /app/uploads ===" -ForegroundColor Cyan

    $STORAGE_KEY = az storage account keys list `
        --account-name $STORAGE_ACCOUNT `
        --resource-group $RESOURCE_GROUP `
        --query "[0].value" `
        --output tsv

    az storage share create `
        --name $SHARE_NAME `
        --account-name $STORAGE_ACCOUNT `
        --account-key $STORAGE_KEY `
        --output none

    az webapp config storage-account add `
        --name $APP_NAME `
        --resource-group $RESOURCE_GROUP `
        --custom-id "uploads-mount" `
        --storage-type AzureFiles `
        --account-name $STORAGE_ACCOUNT `
        --share-name $SHARE_NAME `
        --access-key $STORAGE_KEY `
        --mount-path "/app/uploads" `
        --output none

    if ($LASTEXITCODE -ne 0) {
        Write-Host "WARNING: Failed to mount file share. Uploads will work but won't survive redeploys." -ForegroundColor Yellow
    } else {
        Write-Host "Persistent storage mounted at /app/uploads." -ForegroundColor Green
        Write-Host "Uploaded images will survive redeploys." -ForegroundColor Green
    }
}

# ---- STEP 7: CREATE SERVICE PRINCIPAL FOR GITHUB ACTIONS ---------------------

Write-Host "`n=== Step 7/7: Creating Service Principal for GitHub Actions ===" -ForegroundColor Cyan

$SUBSCRIPTION_ID = az account show --query id --output tsv

$spCredentials = az ad sp create-for-rbac `
    --name "multiagent-github-deploy" `
    --role contributor `
    --scopes "/subscriptions/$SUBSCRIPTION_ID/resourceGroups/$RESOURCE_GROUP" `
    --sdk-auth

if ($LASTEXITCODE -ne 0) {
    Write-Error "Failed to create Service Principal."
    Write-Error "This is needed for GitHub Actions CI/CD. You can skip this and set it up manually later."
    Write-Host "Continuing without Service Principal..." -ForegroundColor Yellow
    $spCredentials = "(Service Principal creation failed -- see 04-setup-github-secrets.md for manual steps)"
}

# ---- PRINT RESULTS ----------------------------------------------------------

$APP_URL = "https://${APP_NAME}.azurewebsites.net"

Write-Host "`n" -NoNewline
Write-Host "================================================================" -ForegroundColor Yellow
Write-Host "  DEPLOYMENT COMPLETE -- SAVE THESE VALUES                      " -ForegroundColor Yellow
Write-Host "================================================================" -ForegroundColor Yellow

Write-Host "`n1. BACKEND URL (open in browser to test):" -ForegroundColor Cyan
Write-Host "   $APP_URL" -ForegroundColor White

Write-Host "`n2. DOCKER HUB IMAGE:" -ForegroundColor Cyan
Write-Host "   $FULL_IMAGE" -ForegroundColor White

Write-Host "`n3. SERVICE PRINCIPAL CREDENTIALS (needed for GitHub Secrets):" -ForegroundColor Cyan
Write-Host "   Copy the ENTIRE JSON block below:" -ForegroundColor White
Write-Host $spCredentials

Write-Host "`n================================================================" -ForegroundColor Yellow
Write-Host "  NEXT STEPS:                                                   " -ForegroundColor Yellow
Write-Host "  1. Open $APP_URL in your browser to verify" -ForegroundColor Yellow
Write-Host "     (may take 1-2 minutes for first startup)                   " -ForegroundColor Yellow
Write-Host "  2. Follow 03-push-to-github.md to push code to GitHub        " -ForegroundColor Yellow
Write-Host "  3. Follow 04-setup-github-secrets.md to configure CI/CD      " -ForegroundColor Yellow
Write-Host "================================================================" -ForegroundColor Yellow
