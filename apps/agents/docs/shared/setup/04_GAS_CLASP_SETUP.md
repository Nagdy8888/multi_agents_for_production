# GAS + clasp setup

> **Prev:** [03_ENVIRONMENT_VARIABLES.md](03_ENVIRONMENT_VARIABLES.md) | **Index:** [00_SETUP_INDEX.md](00_SETUP_INDEX.md) | **Next:** [05_GAS_SCRIPT_PROPERTIES.md](05_GAS_SCRIPT_PROPERTIES.md)

Work in `gas-scripts/` (submodule).

## Install clasp

```bash
npm install -g @google/clasp
clasp --version
```

## Login

```bash
clasp login
```

Use the **same Google account** as Gmail + Drive + Sheets.

## Enable Apps Script API

Open https://script.google.com/home/usersettings — turn **Google Apps Script API** **ON**.

## Link or create project

```bash
cd gas-scripts
clasp create --title "Multi-Agent Platform GAS" --type standalone --rootDir .
```

Or `clasp clone <SCRIPT_ID> --rootDir .`

## Push

```bash
clasp push
clasp open-script
```

## Deploy Web App (callback)

1. **Deploy** → **New deployment** → type **Web app**
2. Execute as: **Me**
3. Who has access: **Anyone**
4. Copy URL → put in `.env` as `GAS_WEBAPP_URL`

After **every** push that changes `doPost`, use **Manage deployments** → **New version**.

See also: `gas-scripts/README.md`.
