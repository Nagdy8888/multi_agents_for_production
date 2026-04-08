# Step 1: Install the Azure CLI

The Azure CLI (`az`) is a command-line tool that lets you create, configure, and manage Azure resources directly from your terminal. Every Azure operation in this deployment guide uses it.

---

## Install on Windows

### Option A: Using winget (recommended)

Open **PowerShell** (regular PowerShell, not as Administrator) and run:

```powershell
winget install Microsoft.AzureCLI
```

This downloads and installs the latest version automatically. When it finishes, **close your PowerShell window completely and open a new one** -- the `az` command won't be available until you restart the terminal.

### Option B: Using the MSI installer

If `winget` doesn't work or you prefer a graphical installer:

1. Open your browser and go to: https://learn.microsoft.com/en-us/cli/azure/install-azure-cli-windows
2. Click the **"Latest release of the Azure CLI"** download link (the `.msi` file)
3. Run the downloaded `.msi` file
4. Follow the installer wizard (click Next through all screens, keep defaults)
5. When finished, **close your PowerShell window and open a new one**

---

## Verify the Installation

Open a **new** PowerShell window and run:

```powershell
az --version
```

You should see output that starts with something like `azure-cli 2.x.x`. The exact version number doesn't matter as long as the command works. If you see `az: The term 'az' is not recognized`, your terminal session is stale -- close it and open a brand new PowerShell window.

---

## Log In to Your Azure Account

Run:

```powershell
az login
```

**What happens:**

1. Your default web browser opens automatically to a Microsoft login page
2. Sign in with the Microsoft account that has your Azure free subscription
3. If prompted to pick an account or grant permissions, accept
4. After successful login, the browser shows "You have logged in" -- you can close that browser tab
5. Switch back to PowerShell -- it now shows your subscription(s) in a JSON list

If the browser doesn't open automatically, look for a line in the terminal that says something like `To sign in, use a web browser to open the page https://microsoft.com/devicelogin and enter the code XXXXXXX`. Open that URL manually and type in the code.

---

## Verify Your Subscription

Run:

```powershell
az account show --output table
```

This shows which Azure subscription is currently active. Look at the `Name` column -- it should say something like "Azure subscription 1" or "Free Trial" or "Azure for Students".

### If you have multiple subscriptions

Run this to see all of them:

```powershell
az account list --output table
```

Find the subscription you want to use (the free one), copy its `SubscriptionId`, and set it as the default:

```powershell
az account set --subscription "YOUR_SUBSCRIPTION_ID"
```

Replace `YOUR_SUBSCRIPTION_ID` with the actual ID from the table (it looks like `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`).

---

## Common Errors

| Error | Fix |
|---|---|
| `az: The term 'az' is not recognized` | Close your terminal and open a new PowerShell window. If still broken, reinstall using the MSI installer (Option B). |
| Browser doesn't open during `az login` | Use the device code flow: look for the URL and code in the terminal output, then open the URL manually in any browser. |
| `No subscriptions found` | You may not have an Azure subscription yet. Sign up for a free account at [azure.microsoft.com/free](https://azure.microsoft.com/en-us/free/). |
| `The subscription 'xxx' could not be found` | Run `az account list --output table` to see available subscriptions and use `az account set` to pick the right one. |

---

## Next Step

Once `az login` succeeds and you can see your subscription, proceed to:
--> [02-setup-azure-guide.md](02-setup-azure-guide.md) (Create Azure Resources)
