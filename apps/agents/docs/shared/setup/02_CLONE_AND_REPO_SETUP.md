# Clone and repository setup

> **Prev:** [01_PREREQUISITES.md](01_PREREQUISITES.md) | **Index:** [00_SETUP_INDEX.md](00_SETUP_INDEX.md) | **Next:** [03_ENVIRONMENT_VARIABLES.md](03_ENVIRONMENT_VARIABLES.md)

## Clone with submodule

```bash
git clone --recurse-submodules <YOUR_AGENTS_REPO_URL>
cd Multi_agents
```

If you already cloned without submodules:

```bash
git submodule update --init --recursive
```

## Key directories

```
Multi_agents/
├── .env                 # created from .env.example (not committed)
├── docker-compose.yml
├── apps/agents/         # Python backend
├── apps/frontend/       # Next.js
├── gas-scripts/         # submodule → separate Git history
└── scripts/             # e.g. test_e2e_mock.py
```

## Create `.env`

**PowerShell:**

```powershell
Copy-Item .env.example .env
```

**macOS / Linux:**

```bash
cp .env.example .env
```

Fill values per [03_ENVIRONMENT_VARIABLES.md](03_ENVIRONMENT_VARIABLES.md) and [05_GAS_SCRIPT_PROPERTIES.md](05_GAS_SCRIPT_PROPERTIES.md).
