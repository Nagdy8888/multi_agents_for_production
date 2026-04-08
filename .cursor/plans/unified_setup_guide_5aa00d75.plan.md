---
name: Unified Setup Guide
overview: Create 19 ordered Markdown files in apps/agents/docs/shared/setup/ (00_ through 18_) with exhaustive, verbatim instructions so a cheap LLM can write each file with zero guessing.
todos:
  - id: create-folder
    content: "Create folder: apps/agents/docs/shared/setup/"
    status: pending
  - id: write-00
    content: "Write 00_SETUP_INDEX.md -- table of contents linking all files in order"
    status: pending
  - id: write-01
    content: "Write 01_PREREQUISITES.md -- software, accounts, OS notes, verify commands"
    status: pending
  - id: write-02
    content: "Write 02_CLONE_AND_REPO_SETUP.md -- clone, folder tree, .env from template"
    status: pending
  - id: write-03
    content: "Write 03_ENVIRONMENT_VARIABLES.md -- full .env.example content, every variable explained"
    status: pending
  - id: write-04
    content: "Write 04_GAS_CLASP_SETUP.md -- install clasp, create project, push, deploy Web App"
    status: pending
  - id: write-05
    content: "Write 05_GAS_SCRIPT_PROPERTIES.md -- every Script Property, shared secrets generation"
    status: pending
  - id: write-06
    content: "Write 06_GOOGLE_SHEETS_SETUP.md -- PO Parser sheet (3 tabs) + Image Tagger sheet (2 tabs)"
    status: pending
  - id: write-07
    content: "Write 07_GMAIL_SETUP.md -- labels, search query, test email"
    status: pending
  - id: write-08
    content: "Write 08_GOOGLE_DRIVE_SETUP.md -- create folder, copy ID, set Script Property"
    status: pending
  - id: write-09
    content: "Write 09_GAS_TRIGGERS.md -- install both 5-min triggers, Web App callback test"
    status: pending
  - id: write-10
    content: "Write 10_OPENAI_SETUP.md -- account, API key, fill .env vars"
    status: pending
  - id: write-11
    content: "Write 11_AIRTABLE_SETUP.md -- base, tables, fields, PAT, .env vars"
    status: pending
  - id: write-12
    content: "Write 12_DATABASE_SETUP.md -- Supabase/Postgres, migration.sql, DATABASE_URI"
    status: pending
  - id: write-13
    content: "Write 13_DOCKER_BUILD_AND_RUN.md -- build, up, health checks, logs, stop"
    status: pending
  - id: write-14
    content: "Write 14_NGROK_SETUP.md -- install, tunnel, update GAS URLs, verify"
    status: pending
  - id: write-15
    content: "Write 15_LANGSMITH_SETUP.md -- account, project, API key, .env, verify traces"
    status: pending
  - id: write-16
    content: "Write 16_LANGGRAPH_STUDIO_SETUP.md -- venv, CLI, PYTHONPATH, langgraph dev"
    status: pending
  - id: write-17
    content: "Write 17_END_TO_END_VERIFICATION.md -- PO Parser E2E, Image Tagger E2E, Frontend E2E"
    status: pending
  - id: write-18
    content: "Write 18_PRODUCTION_CHECKLIST.md -- full checkbox list, troubleshooting tables, Windows notes"
    status: pending
isProject: false
---

# Unified Setup Guide -- Split into Ordered Files

## Goal

Create **19 numbered Markdown files** in `apps/agents/docs/shared/setup/` that walk the reader from zero to production. Each file is self-contained for its topic -- every command verbatim, every expected output shown, every table with exact headers. A cheap LLM should NEVER need to open another file to understand a single phase.

## File listing

```
apps/agents/docs/shared/setup/
├── 00_SETUP_INDEX.md
├── 01_PREREQUISITES.md
├── 02_CLONE_AND_REPO_SETUP.md
├── 03_ENVIRONMENT_VARIABLES.md
├── 04_GAS_CLASP_SETUP.md
├── 05_GAS_SCRIPT_PROPERTIES.md
├── 06_GOOGLE_SHEETS_SETUP.md
├── 07_GMAIL_SETUP.md
├── 08_GOOGLE_DRIVE_SETUP.md
├── 09_GAS_TRIGGERS.md
├── 10_OPENAI_SETUP.md
├── 11_AIRTABLE_SETUP.md
├── 12_DATABASE_SETUP.md
├── 13_DOCKER_BUILD_AND_RUN.md
├── 14_NGROK_SETUP.md
├── 15_LANGSMITH_SETUP.md
├── 16_LANGGRAPH_STUDIO_SETUP.md
├── 17_END_TO_END_VERIFICATION.md
└── 18_PRODUCTION_CHECKLIST.md
```

## Writing rules for the LLM that generates each file

1. **Every shell command must be inside a fenced code block** with the correct language tag (`bash`, `powershell`, or `sql`).
2. **Every expected output must follow the command** in a separate fenced code block with language tag `text` or `json`.
3. **Every table must use exact column headers** -- copy character-for-character from the specifications below.
4. **Every env var** must show: variable name, example value, which agent uses it, required vs optional.
5. **Do NOT abbreviate steps.** If a step says "click X then Y then Z", write "click X", then "click Y", then "click Z" as separate numbered sub-steps.
6. **Use blockquotes (`>`) for IMPORTANT / WARNING / NOTE callouts.**
7. **Use checkboxes (`- [ ]`)** for verification checklists so the reader can track progress.
8. **Include BOTH Windows PowerShell AND macOS/Linux commands** side by side for every shell command that differs between OSes.
9. **Every Phase must start with a "What you need before this phase" prerequisite box** listing which prior phases must be complete.

---

## Folder

`apps/agents/docs/shared/setup/` (19 files, `00_` through `18_`)

---

## Exact content specification (file by file)

Each file specification below shows what MUST appear in that file -- literal text, exact commands, exact tables, and exact expected outputs.

---

### File: `00_SETUP_INDEX.md`

This is the table of contents. It must contain:

```markdown
# Multi-Agent Platform -- Setup Guide

This guide walks you through every step to set up and run both AI agents (PO Parser and Image Tagger) from a fresh machine. Follow the guides **in order** -- each one depends on the ones before it.

**Monorepo structure:**
- `apps/agents/` -- Python backend (FastAPI + LangGraph, both agents)
- `apps/frontend/` -- Next.js frontend (image tagger UI)
- `gas-scripts/` -- Google Apps Script (Git submodule, shared by both agents)

**Ports:**
- `8000` -- Backend API (both agents share one FastAPI app)
- `3000` -- Frontend (Next.js)
- `2024` -- LangGraph Studio (optional, local dev only)

## Setup order

| # | Guide | What you do | Time estimate |
|---|-------|-------------|---------------|
| 01 | [Prerequisites](01_PREREQUISITES.md) | Install software, create accounts | 15-30 min |
| 02 | [Clone and Repo Setup](02_CLONE_AND_REPO_SETUP.md) | Clone repo, understand folder structure | 5 min |
| 03 | [Environment Variables](03_ENVIRONMENT_VARIABLES.md) | Create .env file, understand every variable | 10 min |
| 04 | [GAS + clasp Setup](04_GAS_CLASP_SETUP.md) | Install clasp, create Apps Script project, deploy Web App | 15 min |
| 05 | [GAS Script Properties](05_GAS_SCRIPT_PROPERTIES.md) | Set all Script Properties, generate shared secrets | 10 min |
| 06 | [Google Sheets Setup](06_GOOGLE_SHEETS_SETUP.md) | Create 2 spreadsheets with exact tabs and headers | 15 min |
| 07 | [Gmail Setup](07_GMAIL_SETUP.md) | Create labels, verify search query | 5 min |
| 08 | [Google Drive Setup](08_GOOGLE_DRIVE_SETUP.md) | Create image folder, copy ID | 5 min |
| 09 | [GAS Triggers](09_GAS_TRIGGERS.md) | Install time-driven triggers, test Web App callback | 10 min |
| 10 | [OpenAI Setup](10_OPENAI_SETUP.md) | Create API key, fill .env | 5 min |
| 11 | [Airtable Setup](11_AIRTABLE_SETUP.md) | Create base, tables, PAT (PO Parser only) | 20 min |
| 12 | [Database Setup](12_DATABASE_SETUP.md) | Supabase/Postgres migration (Image Tagger, optional) | 10 min |
| 13 | [Docker Build and Run](13_DOCKER_BUILD_AND_RUN.md) | Build images, start services, health checks | 10 min |
| 14 | [ngrok Setup](14_NGROK_SETUP.md) | Tunnel localhost, update GAS URLs | 10 min |
| 15 | [LangSmith Setup](15_LANGSMITH_SETUP.md) | Tracing (optional) | 10 min |
| 16 | [LangGraph Studio Setup](16_LANGGRAPH_STUDIO_SETUP.md) | Visual graph debugger (optional) | 15 min |
| 17 | [End-to-End Verification](17_END_TO_END_VERIFICATION.md) | Test both agents + frontend | 15 min |
| 18 | [Production Checklist](18_PRODUCTION_CHECKLIST.md) | Final checks, troubleshooting, Windows notes | 10 min |
```

Each file must start with a navigation header:

```markdown
> **Prev:** [XX_PREVIOUS.md](XX_PREVIOUS.md) | **Index:** [00_SETUP_INDEX.md](00_SETUP_INDEX.md) | **Next:** [XX_NEXT.md](XX_NEXT.md)
```

(First file has no Prev; last file has no Next.)

---

### File: `01_PREREQUISITES.md`

**Must include:**

1. Software table with exact install commands:

| Software | Purpose | Install (Windows) | Install (macOS) | Install (Linux) | Verify command | Expected output pattern |
|----------|---------|-------------------|-----------------|-----------------|----------------|------------------------|
| Docker Desktop | Run containers | Download from docker.com | `brew install --cask docker` | Install Docker Engine + Compose plugin | `docker --version` | `Docker version 2X.X.X` |
| Docker Compose | Orchestrate services | Included in Docker Desktop | Included | `sudo apt install docker-compose-plugin` | `docker compose version` | `Docker Compose version v2.X.X` |
| Node.js 18+ | clasp for GAS | Download from nodejs.org or `winget install OpenJS.NodeJS.LTS` | `brew install node@18` | `sudo apt install nodejs npm` | `node --version` | `v18.X.X` or higher |
| Git | Version control | Download from git-scm.com | `brew install git` | `sudo apt install git` | `git --version` | `git version 2.X.X` |
| ngrok | Tunnel localhost for GAS | Download from ngrok.com or `winget install ngrok.ngrok` | `brew install ngrok` | `snap install ngrok` | `ngrok version` | `ngrok version 3.X.X` |
| Python 3.11+ | Local dev / LangGraph Studio (optional) | Download from python.org | `brew install python@3.11` | `sudo apt install python3.11 python3.11-venv` | `python --version` | `Python 3.11.X` |

2. Accounts table:

| Account | URL | Required for | When needed |
|---------|-----|-------------|-------------|
| Google | gmail.com | Gmail (PO Parser inbox), Google Drive (Image Tagger images), Google Sheets (both agents), Apps Script (both agents) | Phase 2 |
| OpenAI | platform.openai.com | LLM calls for both agents | Phase 7 |
| Airtable | airtable.com | PO data storage (PO Parser only) | Phase 8 |
| ngrok | ngrok.com | Expose localhost to GAS | Phase 11 |
| LangSmith | smith.langchain.com | Tracing (optional) | Phase 12 |

3. OS-specific notes:
   - Windows: Docker Desktop with WSL 2 backend recommended. In PowerShell, `curl` is an alias for `Invoke-WebRequest` -- always use `curl.exe` or `Invoke-RestMethod` instead. See Appendix C.
   - macOS: Docker Desktop for Apple Silicon or Intel.
   - Linux: Install Docker Engine and the Compose plugin (`docker compose`, not `docker-compose`).

4. A "Verify all prerequisites" section with the exact multi-line command:

**Windows PowerShell:**
```powershell
docker --version; docker compose version; node --version; npm --version; git --version; ngrok version
```

**macOS / Linux:**
```bash
docker --version && docker compose version && node --version && npm --version && git --version && ngrok version
```

---

### File: `02_CLONE_AND_REPO_SETUP.md`

**Prerequisites line:** `> **Requires:** [01_PREREQUISITES.md](01_PREREQUISITES.md) complete (all software installed).`

**Must include:**

1. Clone command with submodules:
```bash
git clone --recurse-submodules <your-repo-url>
cd Multi_agents
```

2. If already cloned without submodules:
```bash
git submodule update --init --recursive
```

3. Folder tree (abbreviated, showing only key paths):
```
Multi_agents/                     <-- ROOT (all commands run from here)
├── .env                          <-- Single env file for everything
├── .env.example                  <-- Template (committed to Git)
├── docker-compose.yml
├── .gitignore
├── README.md
├── apps/
│   ├── agents/                   <-- Python backend
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   ├── langgraph.json
│   │   └── src/
│   │       ├── api/main.py       <-- Unified FastAPI (port 8000)
│   │       ├── po_parser/        <-- PO Parser agent
│   │       ├── image_tagging/    <-- Image Tagger agent
│   │       └── services/         <-- Shared (OpenAI, Supabase, Airtable, GAS callback)
│   └── frontend/                 <-- Next.js app (port 3000)
│       ├── Dockerfile
│       └── package.json
└── gas-scripts/                  <-- Git submodule (Google Apps Script)
    ├── shared/                   <-- Config.gs, WebApp.gs, Utils.gs
    ├── po_parser/                <-- GmailTrigger.gs, SheetsWriter.gs
    ├── image_tagger/             <-- DriveTrigger.gs, SheetsWriter.gs
    └── appsscript.json
```

4. Create `.env` from template:

**Windows PowerShell:**
```powershell
Copy-Item .env.example .env
```

**macOS / Linux:**
```bash
cp .env.example .env
```

5. Then the FULL `.env.example` content must be inlined (every variable, with placeholder values and comments explaining each one):

```env
# ============================================================
# Multi-Agent Platform -- Single Environment File
# Place this file at the repository root (same folder as docker-compose.yml)
# ============================================================

# --- GAS <-> Python Webhook Secrets ---
# Generate with: python -c "import secrets; print(secrets.token_hex(32))"
# Must match the GAS Script Property of the same name
WEBHOOK_SECRET=your-webhook-secret-here
GAS_WEBAPP_SECRET=your-gas-webapp-secret-here

# GAS Web App URL (from Apps Script deployment)
GAS_WEBAPP_URL=https://script.google.com/macros/s/YOUR_DEPLOYMENT_ID/exec

# --- OpenAI (required for both agents) ---
OPENAI_API_KEY=sk-your-openai-api-key
OPENAI_CLASSIFICATION_MODEL=gpt-4o-mini
OPENAI_EXTRACTION_MODEL=gpt-4o-mini
OPENAI_OCR_MODEL=gpt-4o
OPENAI_MODEL=gpt-4o
OPENAI_MAX_TOKENS=4096
OPENAI_TEMPERATURE=0

# --- LangSmith (optional -- tracing) ---
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=lsv2_pt_your-langsmith-api-key
LANGCHAIN_PROJECT=multi-agent-platform

# --- Airtable (PO Parser only) ---
AIRTABLE_API_KEY=pat_your-airtable-pat
AIRTABLE_BASE_ID=appYOUR_BASE_ID
AIRTABLE_PO_TABLE=Customer POs
AIRTABLE_ITEMS_TABLE=PO Items
AIRTABLE_ATTACHMENTS_FIELD=Attachments

# --- Supabase / PostgreSQL (Image Tagger -- optional, enables save/search) ---
DATABASE_URI=postgresql://user:password@host:5432/postgres

# --- Frontend ---
NEXT_PUBLIC_API_URL=http://localhost:8000

# --- Runtime ---
LOG_LEVEL=INFO
```

6. A table explaining every variable:

| Variable | Agent(s) | Required? | Example | Description |
|----------|----------|-----------|---------|-------------|
| `WEBHOOK_SECRET` | Both | Yes | `a1b2c3...` (64-char hex) | Shared secret: GAS sends this in webhook header; Python validates it |
| `GAS_WEBAPP_SECRET` | Both | Yes | `d4e5f6...` (64-char hex) | Shared secret: Python sends this in callback body; GAS validates it |
| `GAS_WEBAPP_URL` | Both | Yes | `https://script.google.com/macros/s/.../exec` | GAS Web App URL for Python to POST callbacks |
| `OPENAI_API_KEY` | Both | Yes | `sk-proj-...` | OpenAI API key |
| `OPENAI_CLASSIFICATION_MODEL` | PO Parser | Yes | `gpt-4o-mini` | Model for PO classification |
| `OPENAI_EXTRACTION_MODEL` | PO Parser | Yes | `gpt-4o-mini` | Model for PO data extraction |
| `OPENAI_OCR_MODEL` | PO Parser | Yes | `gpt-4o` | Model for OCR on attachments |
| `OPENAI_MODEL` | Image Tagger | Yes | `gpt-4o` | Model for image analysis |
| `OPENAI_MAX_TOKENS` | PO Parser | Yes | `4096` | Max tokens for OpenAI responses |
| `OPENAI_TEMPERATURE` | PO Parser | Yes | `0` | Temperature (0 = deterministic) |
| `LANGCHAIN_TRACING_V2` | Both | No | `true` | Enable LangSmith tracing |
| `LANGCHAIN_API_KEY` | Both | No | `lsv2_pt_...` | LangSmith API key |
| `LANGCHAIN_PROJECT` | Both | No | `multi-agent-platform` | LangSmith project name |
| `AIRTABLE_API_KEY` | PO Parser | Yes (for PO) | `pat_...` | Airtable Personal Access Token |
| `AIRTABLE_BASE_ID` | PO Parser | Yes (for PO) | `appXXX...` | Airtable base ID |
| `AIRTABLE_PO_TABLE` | PO Parser | Yes (for PO) | `Customer POs` | Exact table name |
| `AIRTABLE_ITEMS_TABLE` | PO Parser | Yes (for PO) | `PO Items` | Exact table name |
| `AIRTABLE_ATTACHMENTS_FIELD` | PO Parser | No | `Attachments` | Attachment field name (leave empty to skip) |
| `DATABASE_URI` | Image Tagger | No | `postgresql://...` | Enables save/search in image tagger |
| `NEXT_PUBLIC_API_URL` | Frontend | Yes | `http://localhost:8000` | Backend URL the browser calls |
| `LOG_LEVEL` | Both | No | `INFO` | Python logging level |

---

### File: `03_ENVIRONMENT_VARIABLES.md`

**Prerequisites line:** `> **Requires:** [02_CLONE_AND_REPO_SETUP.md](02_CLONE_AND_REPO_SETUP.md) complete (.env file created from template).`

**Must include:**

The FULL `.env.example` content (same as in the `02_CLONE_AND_REPO_SETUP.md` specification above), PLUS the full variable table. This file is the single reference for all environment variables. It must be a standalone document -- do NOT say "see 02 for the template". Inline the full template AND the full table here.

**Additionally, this file must include:**
- A "How `.env` works in this monorepo" section explaining: single `.env` at ROOT, Docker Compose `env_file: .env`, Python `load_dotenv()` picks it up, `pydantic-settings` reads from environment, frontend gets `NEXT_PUBLIC_API_URL` as Docker build arg.
- A "Generating secrets" section with the exact `python -c "import secrets; ..."` commands.
- A "Minimum .env for first boot" section showing which 3 variables are needed to at least start Docker (even if agents won't fully work): `OPENAI_API_KEY`, `WEBHOOK_SECRET`, `GAS_WEBAPP_SECRET`.

---

### File: `04_GAS_CLASP_SETUP.md`

**Prerequisites line:** `> **Requires:** [03_ENVIRONMENT_VARIABLES.md](03_ENVIRONMENT_VARIABLES.md) complete (.env file filled with secrets).`

**Must include these exact sub-steps:**

**Step 2.1 -- Install clasp:**
```bash
npm install -g @google/clasp
clasp --version
```
Expected: `3.X.X`

**Step 2.2 -- Log in to Google:**
```bash
clasp login
```
Complete the browser OAuth flow. Use the **same Google account** that owns the Gmail inbox (PO Parser) and Google Drive folder (Image Tagger).

**Step 2.3 -- Enable Apps Script API:**
1. Open https://script.google.com/home/usersettings in your browser.
2. Find the toggle for **Google Apps Script API**.
3. Turn it **ON**.

> **WARNING:** If you skip this step, `clasp push` and `clasp create` will fail with "Script API not enabled".

**Step 2.4 -- Create the GAS project:**

Navigate to the `gas-scripts` folder and create:

**Windows PowerShell:**
```powershell
cd gas-scripts
clasp create --title "Multi-Agent Platform GAS" --type standalone --rootDir .
```

**macOS / Linux:**
```bash
cd gas-scripts
clasp create --title "Multi-Agent Platform GAS" --type standalone --rootDir .
```

This creates `gas-scripts/.clasp.json` with a `scriptId`. This file is gitignored -- it lives only on your machine.

> **If clasp says "A project file already exists":** Delete `gas-scripts/.clasp.json` and run the command again.

**Step 2.5 -- Push code to Apps Script:**
```bash
clasp push
```
Expected: lists all `.gs` files pushed, no errors.

> After `clasp push`, any existing `appsscript.json` may be overwritten by Google's template. If scopes or timezone are reset, restore `gas-scripts/appsscript.json` from Git and run `clasp push --force`.

**Step 2.6 -- Open in browser:**
```bash
clasp open-script
```
This opens the Apps Script editor in your browser.

**Step 2.7 -- Set Script Properties:**

In the Apps Script editor: **Project Settings** (gear icon) -> **Script properties** -> **Add script property** for each row:

| Property Key | Value | Notes |
|-------------|-------|-------|
| `WEBHOOK_SECRET` | (paste from `ROOT/.env` `WEBHOOK_SECRET`) | Must match Python `.env` exactly |
| `GAS_WEBAPP_SECRET` | (paste from `ROOT/.env` `GAS_WEBAPP_SECRET`) | Must match Python `.env` exactly |
| `WEBHOOK_URL` | `https://YOUR-NGROK-HOST/webhook/email` | Set after ngrok (Phase 11). Leave empty for now. |
| `SPREADSHEET_ID` | (from PO Parser Google Sheet URL) | Set after Phase 3. Leave empty for now. |
| `NOTIFICATION_RECIPIENTS` | `you@company.com,team@company.com` | Comma-separated emails |
| `IMAGE_WEBHOOK_URL` | `https://YOUR-NGROK-HOST/webhook/drive-image` | Set after ngrok (Phase 11). Leave empty for now. |
| `IMAGE_FOLDER_ID` | (from Google Drive folder URL) | Set after Phase 5. Leave empty for now. |
| `IMAGE_SPREADSHEET_ID` | (from Image Tagger Google Sheet URL) | Set after Phase 3. Leave empty for now. |

> **IMPORTANT:** Properties marked "Leave empty for now" will be filled in later phases. Do NOT skip creating them -- add them now with empty values so you remember to fill them later.

**Step 2.8 -- Generate shared secrets:**

If you have not already generated secrets for `WEBHOOK_SECRET` and `GAS_WEBAPP_SECRET`:

```bash
python -c "import secrets; print('WEBHOOK_SECRET=' + secrets.token_hex(32))"
python -c "import secrets; print('GAS_WEBAPP_SECRET=' + secrets.token_hex(32))"
```

Copy each value into:
1. `ROOT/.env` (the Python side)
2. GAS Script Properties (the GAS side)

Both sides **must have the exact same value** for each secret.

**Step 2.9 -- Deploy Web App:**

1. In the Apps Script editor, click **Deploy** -> **New deployment**.
2. Click the gear icon next to "Select type" and choose **Web app**.
3. Settings:
   - **Description:** `Multi-Agent Platform Callback`
   - **Execute as:** `Me (your-email@gmail.com)`
   - **Who has access:** `Anyone`
4. Click **Deploy**.
5. Click **Authorize access** and grant all requested permissions.
6. **Copy the Web App URL** -- it looks like: `https://script.google.com/macros/s/AKfycb.../exec`
7. Paste this URL into `ROOT/.env` as the value of `GAS_WEBAPP_URL`.

> **CRITICAL:** After every future `clasp push` that changes `WebApp.gs` or `doPost`, you must create a **new version**: Deploy -> Manage deployments -> Edit -> New version -> Deploy. The URL stays the same.

---

### File: `05_GAS_SCRIPT_PROPERTIES.md`

**Prerequisites line:** `> **Requires:** [04_GAS_CLASP_SETUP.md](04_GAS_CLASP_SETUP.md) complete (GAS project created and deployed).`

**Must include:**

The complete Script Properties table (same as Step 2.7 above), plus the secret generation commands (same as Step 2.8 above). This is a standalone file -- inline the full table and commands, do NOT say "see 04".

The file must emphasize:
- Which properties to fill now vs which to fill later (after Sheets, Drive, ngrok).
- The critical rule: `WEBHOOK_SECRET` and `GAS_WEBAPP_SECRET` must match between `ROOT/.env` and GAS Script Properties **exactly**.
- A "Come back to this file" reminder: after completing files 06, 08, and 14, return here to fill in the remaining empty properties (`SPREADSHEET_ID`, `IMAGE_SPREADSHEET_ID`, `IMAGE_FOLDER_ID`, `WEBHOOK_URL`, `IMAGE_WEBHOOK_URL`).

---

### File: `06_GOOGLE_SHEETS_SETUP.md`

**Prerequisites line:** `> **Requires:** [05_GAS_SCRIPT_PROPERTIES.md](05_GAS_SCRIPT_PROPERTIES.md) complete. After this file, go back to 05 and fill `SPREADSHEET_ID` and `IMAGE_SPREADSHEET_ID`.`

**Must include two completely separate spreadsheet setups:**

**Step 3.1 -- PO Parser Google Sheet:**

1. Open https://sheets.google.com (same Google account as GAS).
2. Click **Blank spreadsheet**.
3. Name it: `PO Parsing Agent - Data & Monitoring`

4. **Tab 1: PO Data** -- Rename `Sheet1` to exactly `PO Data`. Add these headers in row 1:

| Column | Header (exact text) |
|--------|-------------------|
| A | PO Number |
| B | Customer |
| C | PO Date |
| D | Ship Date |
| E | Status |
| F | Source Type |
| G | Email Subject |
| H | Sender |
| I | Confidence |
| J | Validation Status |
| K | Processing Timestamp |
| L | Airtable Link |

5. **Tab 2: PO Items** -- Click **+** (add sheet) -> rename to exactly `PO Items`. Row 1 headers:

| Column | Header (exact text) |
|--------|-------------------|
| A | PO Number |
| B | SKU |
| C | Description |
| D | Quantity |
| E | Unit Price |
| F | Total Price |
| G | Destination/DC |
| H | Processing Timestamp |

6. **Tab 3: Monitoring Logs** -- Click **+** -> rename to exactly `Monitoring Logs`. Row 1 headers:

| Column | Header (exact text) |
|--------|-------------------|
| A | Timestamp (Cairo) |
| B | Email ID |
| C | Subject |
| D | Sender |
| E | Classification Result |
| F | Confidence |
| G | Parse Status |
| H | Processing Time (ms) |
| I | Errors |
| J | Node |

7. **Get `SPREADSHEET_ID`:** From the browser URL: `https://docs.google.com/spreadsheets/d/SPREADSHEET_ID_HERE/edit` -- copy the segment between `/d/` and `/edit`.

8. Go to GAS Script Properties and set `SPREADSHEET_ID` = the ID you just copied.

**Step 3.2 -- Image Tagger Google Sheet (SEPARATE spreadsheet):**

1. Open https://sheets.google.com.
2. Click **Blank spreadsheet**.
3. Name it: `Image Tagger Agent - Data & Monitoring`

4. **Tab 1: Image Data** -- Rename `Sheet1` to exactly `Image Data`. Row 1 headers:

| Column | Header (exact text) |
|--------|-------------------|
| A | Image ID |
| B | Filename |
| C | Tags JSON |
| D | Confidence |
| E | Needs Review |
| F | Processing Status |
| G | Source |
| H | Processing Timestamp |

5. **Tab 2: Image Monitoring** -- Click **+** -> rename to exactly `Image Monitoring`. Row 1 headers:

| Column | Header (exact text) |
|--------|-------------------|
| A | Timestamp |
| B | Image ID |
| C | Filename |
| D | Status |
| E | Processing Time (ms) |
| F | Errors |

6. **Get `IMAGE_SPREADSHEET_ID`:** Same as above -- copy from the URL.

7. Go to GAS Script Properties and set `IMAGE_SPREADSHEET_ID` = the ID you just copied.

> **IMPORTANT:** The PO Parser and Image Tagger use **different** Google Sheets. Do NOT use the same spreadsheet for both.

---

### File: `07_GMAIL_SETUP.md`

**Prerequisites line:** `> **Requires:** [06_GOOGLE_SHEETS_SETUP.md](06_GOOGLE_SHEETS_SETUP.md) complete (both Google Sheets created).`

**Must include:**

1. Use the **same Google account** as the GAS project.
2. Create two Gmail labels (Settings -> Labels -> Create new label):
   - `PO-Processed`
   - `PO-Processing-Failed`
3. The GAS trigger searches for emails matching this query (from `Config.gs`):
   ```text
   subject:(PO OR "Purchase Order") is:unread -label:PO-Processed -label:PO-Processing-Failed
   ```
4. **Test the query:** Paste it into Gmail's search bar. It should return zero results (no matching unread emails yet).

---

### File: `08_GOOGLE_DRIVE_SETUP.md`

**Prerequisites line:** `> **Requires:** [06_GOOGLE_SHEETS_SETUP.md](06_GOOGLE_SHEETS_SETUP.md) complete. After this file, go back to [05_GAS_SCRIPT_PROPERTIES.md](05_GAS_SCRIPT_PROPERTIES.md) and fill `IMAGE_FOLDER_ID`.`

**Must include:**

1. Open Google Drive (same Google account).
2. Create a new folder (e.g. `Image Tagger Input`).
3. Open the folder. The URL looks like: `https://drive.google.com/drive/folders/FOLDER_ID_HERE`
4. Copy `FOLDER_ID_HERE` from the URL.
5. Go to GAS Script Properties and set `IMAGE_FOLDER_ID` = the folder ID.

> The GAS `DriveTrigger.gs` watches this folder for new images every 5 minutes.

---

### File: `09_GAS_TRIGGERS.md`

**Prerequisites line:** `> **Requires:** Files 04-08 complete (GAS deployed, Script Properties partially filled, Sheets created, Gmail labels created, Drive folder created).`

**Must include:**

**Step 6.1 -- Install PO Parser trigger:**

1. In Apps Script editor, click **Triggers** (alarm clock icon in left sidebar).
2. Click **+ Add trigger**.
3. Settings:
   - **Choose which function to run:** `processNewEmails`
   - **Choose which deployment should run:** `Head`
   - **Select event source:** `Time-driven`
   - **Select type of time based trigger:** `Minutes timer`
   - **Select minute interval:** `Every 5 minutes`
4. Click **Save**.
5. **Authorize all requested scopes** when prompted (Gmail, Sheets, external URL).

**Step 6.2 -- Install Image Tagger trigger:**

1. Click **+ Add trigger** again.
2. Settings:
   - **Choose which function to run:** `processNewImages`
   - **Choose which deployment should run:** `Head`
   - **Select event source:** `Time-driven`
   - **Select type of time based trigger:** `Minutes timer`
   - **Select minute interval:** `Every 5 minutes`
3. Click **Save**.
4. Authorize if prompted.

**Step 6.3 -- Quick Web App callback test (optional, after filling `GAS_WEBAPP_SECRET`):**

**macOS / Linux / Git Bash:**
```bash
curl -L -X POST "YOUR_GAS_WEBAPP_URL" \
  -H "Content-Type: application/json" \
  -d '{"secret":"YOUR_GAS_WEBAPP_SECRET","message_id":"test-msg","status":"error","errors":["test"],"type":"po_result"}'
```

**Windows PowerShell:**
```powershell
$uri = "YOUR_GAS_WEBAPP_URL"
$body = @{ secret = "YOUR_GAS_WEBAPP_SECRET"; message_id = "test-msg"; status = "error"; errors = @("test"); type = "po_result" } | ConvertTo-Json
Invoke-RestMethod -Uri $uri -Method Post -Body $body -ContentType "application/json; charset=utf-8"
```

Expected: JSON response from GAS (not an HTML error page). If you get a redirect HTML page, ensure you used `-L` (curl) or that PowerShell follows redirects.

---

### File: `10_OPENAI_SETUP.md`

**Prerequisites line:** `> **Requires:** [03_ENVIRONMENT_VARIABLES.md](03_ENVIRONMENT_VARIABLES.md) complete (.env file exists).`

**Must include:**

1. Open https://platform.openai.com and sign up or log in.
2. Add a payment method under **Billing**.
3. Go to **API keys** -> **Create new secret key**.
4. Copy the key (starts with `sk-`). You will not see it again.
5. Open `ROOT/.env` and set:
```env
OPENAI_API_KEY=sk-your-actual-key-here
OPENAI_CLASSIFICATION_MODEL=gpt-4o-mini
OPENAI_EXTRACTION_MODEL=gpt-4o-mini
OPENAI_OCR_MODEL=gpt-4o
OPENAI_MODEL=gpt-4o
OPENAI_MAX_TOKENS=4096
OPENAI_TEMPERATURE=0
```

> **IMPORTANT:** Both agents require `OPENAI_API_KEY`. The PO Parser uses `OPENAI_CLASSIFICATION_MODEL`, `OPENAI_EXTRACTION_MODEL`, `OPENAI_OCR_MODEL`, `OPENAI_MAX_TOKENS`, and `OPENAI_TEMPERATURE`. The Image Tagger uses `OPENAI_MODEL`.

---

### File: `11_AIRTABLE_SETUP.md`

**Prerequisites line:** `> **Requires:** [03_ENVIRONMENT_VARIABLES.md](03_ENVIRONMENT_VARIABLES.md) complete (.env file exists). This guide is ONLY for the PO Parser agent. Skip if you only use the Image Tagger.`

**Must include the full Airtable setup with exact field schemas:**

**Step 8.1 -- Create an Airtable base:**
1. Sign in at https://airtable.com.
2. Click **Add a base** -> **Start from scratch**.
3. Name: `PO Parsing` (or any name).

**Step 8.2 -- Create the `Customer POs` table:**

Rename the default `Table 1` to exactly `Customer POs`. Add these fields (exact names, case-sensitive):

| Field name (exact) | Field type | Purpose |
|--------------------|------------|---------|
| `PO Number` | Single line text | Primary key; make this the primary field |
| `Customer` | Single line text | Customer name |
| `PO Date` | Single line text | Date string |
| `Ship Date` | Single line text | Date string |
| `Status` | Single line text | e.g. `Needs Review` |
| `Source Type` | Single line text | e.g. `email`, `pdf` |
| `Email Subject` | Single line text | From webhook |
| `Sender` | Single line text | From webhook |
| `Raw Extract JSON` | Long text | Full extraction JSON |
| `Validation Status` | Single line text | e.g. `Ready for Review` |
| `Confidence` | Number | Float 0-1 |
| `Processing Timestamp` | Single line text | UTC ISO 8601 |
| `Notes` | Long text | Reserved |

**Step 8.3 -- Create the `PO Items` table:**

Click **+** next to the table tabs -> **Create empty table** -> name it exactly `PO Items`. Fields:

| Field name (exact) | Field type | Notes |
|--------------------|------------|-------|
| `Linked PO` | Link to another record | Link to table `Customer POs` |
| `SKU` | Single line text | |
| `Description` | Long text | |
| `Quantity` | Number | Integer |
| `Unit Price` | Number | |
| `Total Price` | Number | |
| `Destination / DC` | Single line text | Slash and spaces must match exactly |

**Step 8.4 -- Create a Personal Access Token (PAT):**

1. Open https://airtable.com/create/tokens.
2. Click **Create token**.
3. Name: `po-parsing-agent`
4. Scopes: add `data.records:read` and `data.records:write`.
5. Access: select the base you created.
6. Create and **copy the token** (starts with `pat`). You will not see it again.

**Step 8.5 -- Copy the Base ID:**

Open your base in the browser. URL: `https://airtable.com/appXXXXXXXXXXXXXX/...` -- the `appXXX...` segment is the Base ID.

**Step 8.6 -- Fill `.env`:**
```env
AIRTABLE_API_KEY=pat_your_token_here
AIRTABLE_BASE_ID=appYourBaseIdHere
AIRTABLE_PO_TABLE=Customer POs
AIRTABLE_ITEMS_TABLE=PO Items
AIRTABLE_ATTACHMENTS_FIELD=Attachments
```

**Step 8.7 -- Optional attachment field:**

In `Customer POs`, add a field named `Attachments` with type **Attachment**. Set `AIRTABLE_ATTACHMENTS_FIELD=Attachments` in `.env`. If you skip this, leave it empty.

---

### File: `12_DATABASE_SETUP.md`

**Prerequisites line:** `> **Requires:** [03_ENVIRONMENT_VARIABLES.md](03_ENVIRONMENT_VARIABLES.md) complete. This guide is OPTIONAL -- skip if you do not need save/search in the Image Tagger.`

**Must include:**

**Option A -- Supabase (recommended):**
1. Sign up at https://supabase.com.
2. Create a new project.
3. Open **SQL Editor** -> **New query**.
4. Paste and run this migration:

```sql
CREATE TABLE IF NOT EXISTS image_tags (
  image_id       TEXT PRIMARY KEY,
  tag_record    JSONB NOT NULL,
  search_index  TEXT[] NOT NULL DEFAULT '{}',
  image_url     TEXT,
  needs_review  BOOLEAN DEFAULT false,
  processing_status TEXT DEFAULT 'pending',
  created_at    TIMESTAMPTZ DEFAULT NOW(),
  updated_at    TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_search_index ON image_tags USING GIN (search_index);
CREATE INDEX IF NOT EXISTS idx_tag_record ON image_tags USING GIN (tag_record);
```

5. Get your connection string from **Settings -> Database -> Connection string -> URI**.
6. Set in `ROOT/.env`:
```env
DATABASE_URI=postgresql://postgres.xxxx:password@aws-0-region.pooler.supabase.com:6543/postgres
```

**Option B -- Standalone PostgreSQL:**
1. Install PostgreSQL 15+.
2. Create a database.
3. Run the same SQL migration above.
4. Set `DATABASE_URI` in `ROOT/.env`.

> **If `DATABASE_URI` is empty or not set:** The Image Tagger still works but save/search features return 503. This is expected behavior, not a bug.

---

### File: `13_DOCKER_BUILD_AND_RUN.md`

**Prerequisites line:** `> **Requires:** [10_OPENAI_SETUP.md](10_OPENAI_SETUP.md) complete (`.env` has at least `OPENAI_API_KEY`, `WEBHOOK_SECRET`, `GAS_WEBAPP_SECRET`). For full functionality: files 04-12 also complete.`

**Must include:**

**Step 10.1 -- Build all images:**

From `ROOT/` (the folder containing `docker-compose.yml`):

```bash
docker compose build
```

Expected: Both `backend` and `frontend` images build without errors.

**Step 10.2 -- Start all services:**

```bash
docker compose up
```

Add `-d` for detached mode (background):
```bash
docker compose up -d
```

Expected output (similar to):
```text
✔ Container multi_agents-backend-1   Started
✔ Container multi_agents-frontend-1  Started
```

**Step 10.3 -- Verify backend health:**

**macOS / Linux:**
```bash
curl http://localhost:8000/health
```

**Windows PowerShell:**
```powershell
curl.exe http://localhost:8000/health
```

Expected:
```json
{"status":"healthy","timestamp":"2026-04-07T12:00:00.000000+00:00"}
```

**Step 10.4 -- Verify frontend:**

Open http://localhost:3000 in your browser. You should see the Image Tagger UI.

**Step 10.5 -- View logs:**
```bash
docker compose logs -f
```

Press `Ctrl+C` to stop following logs.

**Step 10.6 -- Stop services:**
```bash
docker compose down
```

> **If backend crashes on startup:** Check `docker compose logs backend`. The most common cause is a missing `OPENAI_API_KEY` in `.env`. The image tagging agent raises `ValueError("OPENAI_API_KEY is required")` at import time if this variable is missing.

---

### File: `14_NGROK_SETUP.md`

**Prerequisites line:** `> **Requires:** [13_DOCKER_BUILD_AND_RUN.md](13_DOCKER_BUILD_AND_RUN.md) complete (Docker running on port 8000). After this file, go back to [05_GAS_SCRIPT_PROPERTIES.md](05_GAS_SCRIPT_PROPERTIES.md) and fill `WEBHOOK_URL` and `IMAGE_WEBHOOK_URL`.`

**Must include:**

**Step 11.1 -- Create ngrok account:**
1. Go to https://ngrok.com/signup.
2. Free tier is enough.

**Step 11.2 -- Add authtoken:**
1. Open https://dashboard.ngrok.com/get-started/your-authtoken.
2. Copy the token.
3. Run:
```bash
ngrok config add-authtoken YOUR_TOKEN_HERE
```

> If you see **ERR_NGROK_108**, repeat this step.

**Step 11.3 -- Start the tunnel:**

In a **separate terminal** (Docker must be running):
```bash
ngrok http 8000
```

Copy the **Forwarding** HTTPS URL, e.g. `https://abc123.ngrok-free.app`.

**Step 11.4 -- Verify from browser:**

Open: `https://abc123.ngrok-free.app/health`

Expected:
```json
{"status":"healthy","timestamp":"..."}
```

- **502 Bad Gateway:** Docker is not running on port 8000. Start it first.
- **Tunnel not found:** ngrok stopped or wrong URL.

**Step 11.5 -- Update GAS Script Properties:**

Go to Apps Script editor -> Project Settings -> Script properties. Update:

| Property | Value |
|----------|-------|
| `WEBHOOK_URL` | `https://abc123.ngrok-free.app/webhook/email` |
| `IMAGE_WEBHOOK_URL` | `https://abc123.ngrok-free.app/webhook/drive-image` |

> **IMPORTANT:** Include the full path (`/webhook/email` and `/webhook/drive-image`), not just the host.

> **Free tier warning:** The ngrok URL changes every time you restart ngrok. Update both `WEBHOOK_URL` and `IMAGE_WEBHOOK_URL` in GAS Script Properties each time. For a stable URL, use ngrok's paid reserved domain.

**Step 11.6 -- Optional ngrok web UI:**

While ngrok is running, open http://localhost:4040 in your browser to inspect requests, status codes, and bodies.

---

### File: `15_LANGSMITH_SETUP.md`

**Prerequisites line:** `> **Requires:** [13_DOCKER_BUILD_AND_RUN.md](13_DOCKER_BUILD_AND_RUN.md) complete (Docker running). This guide is OPTIONAL -- skip if you do not want tracing.`

**Must include:**

1. Open https://smith.langchain.com and sign up or log in.
2. Create a new **Project** named `multi-agent-platform`.
3. Go to **Settings** -> **API Keys** -> Create a new API key. Copy it (starts with `lsv2_`).
4. Set in `ROOT/.env`:
```env
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=lsv2_pt_your-key-here
LANGCHAIN_PROJECT=multi-agent-platform
```
5. Restart Docker to pick up the new env vars:
```bash
docker compose down
docker compose up -d
```
6. Trigger a run (process a PO email or analyze an image).
7. Open https://smith.langchain.com -> your project -> verify new traces appear.

---

### File: `16_LANGGRAPH_STUDIO_SETUP.md`

**Prerequisites line:** `> **Requires:** [02_CLONE_AND_REPO_SETUP.md](02_CLONE_AND_REPO_SETUP.md) complete. Python 3.11+ installed. This guide is OPTIONAL -- use Studio to visually debug agent graphs.`

**Must include:**

**Step 13.1 -- Create a local Python virtual environment:**

**Windows PowerShell:**
```powershell
cd apps\agents
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -U pip
pip install -r requirements.txt
pip install "langgraph-cli[inmem]"
```

**macOS / Linux:**
```bash
cd apps/agents
python3.11 -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -r requirements.txt
pip install "langgraph-cli[inmem]"
```

**Step 13.2 -- Set PYTHONPATH:**

**Windows PowerShell:**
```powershell
$env:PYTHONPATH = (Get-Location).Path
```

**macOS / Linux:**
```bash
export PYTHONPATH="$(pwd)"
```

**Step 13.3 -- Start LangGraph dev server:**
```bash
langgraph dev
```

Default: binds to `127.0.0.1:2024`. Opens browser automatically.

Useful flags:
```bash
langgraph dev --no-browser
langgraph dev --port 2024
```

**Step 13.4 -- Use Studio:**

1. In the Studio UI, select graph: `po_parser` or `image_tagging`.
2. Verify graph visualization matches the expected node/edge layout.
3. Run or step through with test input.

> **Port note:** LangGraph Studio runs on port **2024**, NOT port 8000. Port 8000 is the Docker FastAPI API. Do not confuse them.

> **Troubleshooting:**
> - `ModuleNotFoundError: src` -- set `PYTHONPATH` (Step 13.2).
> - `langgraph: command not found` -- install `langgraph-cli[inmem]` (Step 13.1).
> - LLM nodes fail -- set `OPENAI_API_KEY` in shell or load `.env` via `langgraph.json`'s `"env"` key.

---

### File: `17_END_TO_END_VERIFICATION.md`

**Prerequisites line:** `> **Requires:** Files 01-14 complete (everything running, ngrok active, GAS triggers installed, all Script Properties filled).`

**Must include three separate E2E tests with checklists:**

**Test A -- PO Parser E2E:**

1. Send an email **to your monitored Gmail** with subject `Test PO 12345` (must contain "PO" or "Purchase Order").
2. Leave the email **unread**.
3. Wait up to **5 minutes** (trigger interval).
4. Verify:

- [ ] **GAS picked up email:** Apps Script Executions shows `processNewEmails` ran with log "Processing email: Test PO 12345"
- [ ] **Webhook reached Python:** `docker compose logs backend` shows received webhook payload
- [ ] **Auth OK:** No 401 errors in Docker logs
- [ ] **Processing completed:** Docker logs show pipeline finished
- [ ] **Callback to GAS:** Docker logs show "Callback sent to GAS, response: ..."
- [ ] **PO Data row:** Google Sheet "PO Data" tab has a new row
- [ ] **PO Items rows:** "PO Items" tab has item rows
- [ ] **Monitoring row:** "Monitoring Logs" tab has a log entry
- [ ] **Notification email:** Check inbox of `NOTIFICATION_RECIPIENTS` for HTML notification
- [ ] **Gmail label:** Original email now has label `PO-Processed`
- [ ] **Airtable rows:** `Customer POs` and `PO Items` tables have new rows (if Airtable is configured)

**Test B -- Image Tagger E2E (via Google Drive):**

1. Upload a test image (JPG, PNG) to the Google Drive folder you created in Phase 5.
2. Wait up to **5 minutes** (trigger interval).
3. Verify:

- [ ] **GAS picked up image:** Apps Script Executions shows `processNewImages` ran
- [ ] **Webhook reached Python:** `docker compose logs backend` shows received image webhook
- [ ] **Processing completed:** Docker logs show image tagging pipeline finished
- [ ] **Callback to GAS:** Docker logs show callback sent
- [ ] **Image Data row:** Image Tagger Google Sheet "Image Data" tab has a new row with tags
- [ ] **Image Monitoring row:** "Image Monitoring" tab has a log entry

**Test C -- Image Tagger E2E (via Frontend UI):**

1. Open http://localhost:3000 in your browser.
2. Use the upload area to select or drag an image.
3. Verify:

- [ ] **Image uploads:** Progress indicator shown
- [ ] **Tags displayed:** After processing, image tags appear in the UI
- [ ] **No console errors:** Browser DevTools console has no red errors

---

### File: `18_PRODUCTION_CHECKLIST.md`

**Must include as a checkbox list:**

- [ ] All secrets (`WEBHOOK_SECRET`, `GAS_WEBAPP_SECRET`) are long random values (64+ hex chars)
- [ ] `WEBHOOK_SECRET` matches between `ROOT/.env` and GAS Script Properties
- [ ] `GAS_WEBAPP_SECRET` matches between `ROOT/.env` and GAS Script Properties
- [ ] `GAS_WEBAPP_URL` in `.env` matches the deployed Web App URL
- [ ] GAS code pushed (`clasp push`) and Web App redeployed (new version)
- [ ] Both time-driven triggers are active (check Apps Script Triggers page)
- [ ] PO Parser Google Sheet has 3 tabs with correct headers
- [ ] Image Tagger Google Sheet has 2 tabs with correct headers (SEPARATE sheet)
- [ ] `SPREADSHEET_ID` in Script Properties points to PO Parser sheet
- [ ] `IMAGE_SPREADSHEET_ID` in Script Properties points to Image Tagger sheet
- [ ] `IMAGE_FOLDER_ID` in Script Properties points to correct Drive folder
- [ ] Airtable base has correct tables and field names (if using PO Parser)
- [ ] `docker compose up` succeeds and backend health returns 200
- [ ] Frontend loads at http://localhost:3000
- [ ] ngrok URL is current and both `WEBHOOK_URL` and `IMAGE_WEBHOOK_URL` are updated
- [ ] LangSmith traces appear (if `LANGCHAIN_*` vars are set)
- [ ] For production: replace ngrok with a stable URL (reserved domain or cloud deployment)

---

**File 18 must also include these appendix sections:**

### Appendix A -- Environment Variable Quick Reference (inside `18_PRODUCTION_CHECKLIST.md`)

**Full table (must be included in the guide):**

| Variable | Where to set | Agent | Required | Example |
|----------|-------------|-------|----------|---------|
| `WEBHOOK_SECRET` | `.env` + GAS Script Property | Both | Yes | `a1b2c3d4e5f6...` (64 hex chars) |
| `GAS_WEBAPP_SECRET` | `.env` + GAS Script Property | Both | Yes | `f6e5d4c3b2a1...` (64 hex chars) |
| `GAS_WEBAPP_URL` | `.env` only | Both | Yes | `https://script.google.com/macros/s/.../exec` |
| `OPENAI_API_KEY` | `.env` only | Both | Yes | `sk-proj-...` |
| `OPENAI_CLASSIFICATION_MODEL` | `.env` only | PO Parser | Yes | `gpt-4o-mini` |
| `OPENAI_EXTRACTION_MODEL` | `.env` only | PO Parser | Yes | `gpt-4o-mini` |
| `OPENAI_OCR_MODEL` | `.env` only | PO Parser | Yes | `gpt-4o` |
| `OPENAI_MODEL` | `.env` only | Image Tagger | Yes | `gpt-4o` |
| `OPENAI_MAX_TOKENS` | `.env` only | PO Parser | Yes | `4096` |
| `OPENAI_TEMPERATURE` | `.env` only | PO Parser | Yes | `0` |
| `LANGCHAIN_TRACING_V2` | `.env` only | Both | No | `true` |
| `LANGCHAIN_API_KEY` | `.env` only | Both | No | `lsv2_pt_...` |
| `LANGCHAIN_PROJECT` | `.env` only | Both | No | `multi-agent-platform` |
| `AIRTABLE_API_KEY` | `.env` only | PO Parser | Yes (PO) | `pat_...` |
| `AIRTABLE_BASE_ID` | `.env` only | PO Parser | Yes (PO) | `appXXX...` |
| `AIRTABLE_PO_TABLE` | `.env` only | PO Parser | Yes (PO) | `Customer POs` |
| `AIRTABLE_ITEMS_TABLE` | `.env` only | PO Parser | Yes (PO) | `PO Items` |
| `AIRTABLE_ATTACHMENTS_FIELD` | `.env` only | PO Parser | No | `Attachments` |
| `DATABASE_URI` | `.env` only | Image Tagger | No | `postgresql://...` |
| `NEXT_PUBLIC_API_URL` | `.env` only | Frontend | Yes | `http://localhost:8000` |
| `LOG_LEVEL` | `.env` only | Both | No | `INFO` |
| `WEBHOOK_URL` | GAS Script Property only | PO Parser | Yes | `https://ngrok.../webhook/email` |
| `IMAGE_WEBHOOK_URL` | GAS Script Property only | Image Tagger | Yes | `https://ngrok.../webhook/drive-image` |
| `SPREADSHEET_ID` | GAS Script Property only | PO Parser | Yes | `1BxiMV...` |
| `IMAGE_SPREADSHEET_ID` | GAS Script Property only | Image Tagger | Yes | `1CyiNW...` |
| `IMAGE_FOLDER_ID` | GAS Script Property only | Image Tagger | Yes | `1DziOX...` |
| `NOTIFICATION_RECIPIENTS` | GAS Script Property only | PO Parser | Yes | `you@co.com,team@co.com` |

---

### Appendix B -- Troubleshooting (inside `18_PRODUCTION_CHECKLIST.md`)

**Organized by category with exact symptoms, causes, and fixes:**

**Docker:**

| Symptom | Cause | Fix |
|---------|-------|-----|
| Docker won't start | Virtualization disabled (Windows) | Enable in BIOS |
| Build fails | Network issue or missing files | Run from ROOT; check `requirements.txt` exists |
| Container exits immediately | Missing `.env` or `OPENAI_API_KEY` | Check `docker compose logs`; fill `.env` |
| Port 8000 in use | Another process on 8000 | Stop it, or change port in `docker-compose.yml` |
| Backend `ValueError: OPENAI_API_KEY` | Key not in `.env` or `.env` not loaded | Ensure `.env` is at ROOT and contains the key |

**GAS:**

| Symptom | Cause | Fix |
|---------|-------|-----|
| `clasp create` says project exists | `.clasp.json` already on disk | Delete it, re-run |
| Script API not enabled | API toggle is OFF | Turn ON at script.google.com/home/usersettings |
| 401 on webhook | `WEBHOOK_SECRET` mismatch | Ensure `.env` and Script Property match exactly |
| Callback fails | Wrong `GAS_WEBAPP_URL` or secret mismatch | Check URL; check `GAS_WEBAPP_SECRET` matches |
| No webhook fires | Trigger not installed, or email doesn't match query | Check Triggers page; test search in Gmail |
| `Cannot find sheet` | Tab name typo | Must be exact: `PO Data`, `PO Items`, `Monitoring Logs` |

**ngrok:**

| Symptom | Cause | Fix |
|---------|-------|-----|
| ERR_NGROK_108 | Authtoken not set | `ngrok config add-authtoken TOKEN` |
| 502 Bad Gateway | Docker not running | Start Docker first |
| URL changed | Free tier rotates URLs | Update `WEBHOOK_URL` and `IMAGE_WEBHOOK_URL` in GAS |

**OpenAI:**

| Symptom | Cause | Fix |
|---------|-------|-----|
| 401 / auth error | Invalid API key | Regenerate at platform.openai.com |
| Rate limit (429) | Too many requests | Wait and retry; check billing |

**Airtable:**

| Symptom | Cause | Fix |
|---------|-------|-----|
| 403 Unauthorized | Bad PAT or missing base access | Recreate token with correct scopes |
| 422 INVALID_VALUE | Field name typo | Compare every name exactly |
| Duplicate check fails | `PO Number` field missing | Ensure field exists with exact name |

**Frontend:**

| Symptom | Cause | Fix |
|---------|-------|-----|
| Can't reach API | Wrong `NEXT_PUBLIC_API_URL` | Must be `http://localhost:8000` for local |
| 503 on tag-images | No `DATABASE_URI` | Set it or accept that save/search is disabled |

---

### Appendix C -- Windows PowerShell Notes (inside `18_PRODUCTION_CHECKLIST.md`)

**Must include:**

1. **`curl` vs `curl.exe`:** In PowerShell, `curl` is an alias for `Invoke-WebRequest`, which behaves differently from Unix curl. Always use `curl.exe` for Unix-like behavior:

```powershell
# WRONG (PowerShell alias, prints verbose object):
curl http://localhost:8000/health

# CORRECT:
curl.exe http://localhost:8000/health

# ALSO CORRECT:
Invoke-RestMethod http://localhost:8000/health
```

2. **Setting environment variables:**
```powershell
$env:PYTHONPATH = "C:\path\to\apps\agents"
$env:OPENAI_API_KEY = "sk-..."
```

3. **Copying files:**
```powershell
Copy-Item .env.example .env
```

4. **Creating directories:**
```powershell
New-Item -ItemType Directory -Force -Path "path\to\folder"
```

5. **Generating secrets:**
```powershell
python -c "import secrets; print(secrets.token_hex(32))"
```

---

## Cross-reference reminders (must be embedded in the files)

Several files ask the reader to "come back" and fill in a value from a later file. The LLM must embed explicit reminder callouts in the correct files:

| After completing... | Go back to... | And fill in... |
|---------------------|---------------|----------------|
| `06_GOOGLE_SHEETS_SETUP.md` | `05_GAS_SCRIPT_PROPERTIES.md` | `SPREADSHEET_ID` and `IMAGE_SPREADSHEET_ID` |
| `08_GOOGLE_DRIVE_SETUP.md` | `05_GAS_SCRIPT_PROPERTIES.md` | `IMAGE_FOLDER_ID` |
| `14_NGROK_SETUP.md` | `05_GAS_SCRIPT_PROPERTIES.md` | `WEBHOOK_URL` and `IMAGE_WEBHOOK_URL` |

Each of the "After completing" files must end with a boxed reminder:

```markdown
> **NEXT ACTION:** Go back to [05_GAS_SCRIPT_PROPERTIES.md](05_GAS_SCRIPT_PROPERTIES.md) and fill in `PROPERTY_NAME` with the value you just obtained. Then continue to the next file.
```

---

## Key adaptations from original per-project docs (context for the LLM, NOT in output files)

- All `.env` references point to `ROOT/.env` (single file, not per-project)
- Docker commands run from `ROOT/` (the folder containing `docker-compose.yml`)
- GAS files are in `gas-scripts/` (Git submodule), not `gas/`
- Backend entry point is `apps/agents/src/api/main.py` (unified FastAPI), not separate servers
- Port 8000 is shared by both agents' API endpoints (single FastAPI app)
- Port 3000 is the Next.js frontend
- `langgraph.json` is at `apps/agents/langgraph.json` and registers both `po_parser` and `image_tagging` graphs
- Google Sheets are SEPARATE for each agent (different spreadsheet IDs, different tabs)
- GAS Script Properties include keys for BOTH agents
- The `WEBHOOK_URL` and `IMAGE_WEBHOOK_URL` Script Properties both point to the same ngrok host but different paths (`/webhook/email` vs `/webhook/drive-image`)

---

## Execution order for the LLM

The LLM must create the files in this exact order (to avoid forward references during writing):

1. Create folder `apps/agents/docs/shared/setup/`
2. Write `00_SETUP_INDEX.md`
3. Write `01_PREREQUISITES.md`
4. Write `02_CLONE_AND_REPO_SETUP.md`
5. Write `03_ENVIRONMENT_VARIABLES.md`
6. Write `04_GAS_CLASP_SETUP.md`
7. Write `05_GAS_SCRIPT_PROPERTIES.md`
8. Write `06_GOOGLE_SHEETS_SETUP.md`
9. Write `07_GMAIL_SETUP.md`
10. Write `08_GOOGLE_DRIVE_SETUP.md`
11. Write `09_GAS_TRIGGERS.md`
12. Write `10_OPENAI_SETUP.md`
13. Write `11_AIRTABLE_SETUP.md`
14. Write `12_DATABASE_SETUP.md`
15. Write `13_DOCKER_BUILD_AND_RUN.md`
16. Write `14_NGROK_SETUP.md`
17. Write `15_LANGSMITH_SETUP.md`
18. Write `16_LANGGRAPH_STUDIO_SETUP.md`
19. Write `17_END_TO_END_VERIFICATION.md`
20. Write `18_PRODUCTION_CHECKLIST.md`
