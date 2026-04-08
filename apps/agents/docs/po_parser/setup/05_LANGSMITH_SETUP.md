# LangSmith setup

**When:** Phase 2+ (optional). Use it to **trace** LLM calls and LangGraph runs in the [LangSmith](https://smith.langchain.com) UI — helpful for debugging classification, extraction, and full pipeline latency.

**Not required** for the app to run; if you leave tracing off, behavior is unchanged.

**Outcome:** A LangSmith **project**, an **API key** in `.env`, and traces appearing when you process a PO through the **production** Docker profile.

---

## Prerequisites

- A LangSmith account (free tier is enough to start).
- Your **production** stack already runs with OpenAI enabled ([04_OPENAI_SETUP.md](04_OPENAI_SETUP.md), [12_DOCKER_PRODUCTION_SETUP.md](12_DOCKER_PRODUCTION_SETUP.md)), since traces are meaningful when the real graph and LLMs execute.

**Note:** The **mock** profile (`scripts/test_e2e_mock.py`) does not run the full LangGraph + OpenAI pipeline. Enable LangSmith for **`po-parser` (production)** when you want traces.

---

## Step 1 — Create an account and a project

1. Open [https://smith.langchain.com](https://smith.langchain.com) and sign up or log in (you can use GitHub / Google).
2. In the LangSmith UI, go to **Projects** (or the project picker).
3. Click **Create project** (or **New project**).
4. Name it e.g. **`po-parsing-agent`** (must match `LANGCHAIN_PROJECT` in `.env` if you want a single named project — see Step 3).

You can use one project for dev and prod, or separate projects via different `LANGCHAIN_PROJECT` values in different `.env` files.

---

## Step 2 — Create an API key

1. Open your **LangSmith** settings:
   - Click your **profile / workspace** menu → **Settings**, or go to **API Keys** / **Personal** access depending on the current UI.
2. Create a new **API key** (often labeled **LangSmith API Key** or **Service key**).
3. Copy the key once. It typically starts with **`lsv2_`** (older keys sometimes looked like `ls__...`).

Store it only in `.env` or a secrets manager — **never** commit it.

---

## Step 3 — Configure `.env`

In the repo root, edit `.env` (see [.env.example](../../.env.example)):

```env
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=lsv2_pt_xxxxxxxx
LANGCHAIN_PROJECT=po-parsing-agent
```

| Variable | Meaning |
|----------|---------|
| `LANGCHAIN_TRACING_V2` | Must be **`true`** (string) to turn on tracing for LangChain / LangGraph integrations. |
| `LANGCHAIN_API_KEY` | Your LangSmith API key from Step 2. |
| `LANGCHAIN_PROJECT` | Project **name** in LangSmith where runs are grouped. Match the project you created in Step 1, or LangSmith may create a project with this name when the first trace arrives. |

**Optional** — only if your organization uses a non-default endpoint (e.g. self-hosted or region-specific; most users omit this):

```env
LANGCHAIN_ENDPOINT=https://api.smith.langchain.com
```

The LangChain ecosystem reads these **`LANGCHAIN_*`** names even though the product is branded **LangSmith**.

---

## Step 4 — Pass variables into Docker

This repo’s [docker-compose.yml](../../docker-compose.yml) uses **`env_file: .env`** for the **`po-parser`** service. Any `LANGCHAIN_*` keys in `.env` are injected into the container automatically.

After changing `.env`:

```powershell
docker compose --profile production down
docker compose --profile production up --build
```

(From the repo root, same folder as `docker-compose.yml`.)

---

## Step 5 — Verify tracing

1. Trigger a real pipeline run — e.g. POST a valid webhook payload to `/webhook/email` or let GAS send an email while ngrok points to your API.
2. Open [https://smith.langchain.com](https://smith.langchain.com) → select your **workspace** → open project **`po-parsing-agent`** (or whatever you set in `LANGCHAIN_PROJECT`).
3. You should see new **Runs** / **Traces** with timestamps matching your test. Open a run to see LLM spans, latency, and inputs/outputs (subject to LangSmith retention and your plan).

If nothing appears within a minute, see **Troubleshooting** below.

---

## How this project uses LangSmith

- Tracing is **environment-driven**: with `LANGCHAIN_TRACING_V2=true` and a valid `LANGCHAIN_API_KEY`, LangChain’s instrumentation sends traces **without** extra code in each node ([implementation-pitfalls](../../.cursor/rules/implementation-pitfalls.mdc), [LANGGRAPH_REFERENCE.md](../documentations/LANGGRAPH_REFERENCE.md)).
- **`langsmith`** is listed in [requirements.txt](../../requirements.txt).

---

## Troubleshooting

| Symptom | Likely cause | What to do |
|---------|----------------|------------|
| No traces in the UI | `LANGCHAIN_TRACING_V2` not `true` | Set to **`true`**, restart the container. |
| No traces | Empty or wrong API key | Regenerate key in LangSmith; paste into `.env`; restart. |
| Traces in wrong project | `LANGCHAIN_PROJECT` mismatch | Align name with the project in the UI, or pick the project LangSmith auto-created. |
| 401 / auth errors in logs | Invalid or revoked key | Create a new key. |
| Only testing mock profile | Mock server does not run full graph | Use **production** profile (`po-parser`) for traces. |
| Tracing worked, then stopped | `.env` not loaded | Confirm `docker compose` uses `env_file: .env` and you recreated the container after edits. |

---

## Related docs

- [../documentations/ENVIRONMENT_VARIABLES.md](../documentations/ENVIRONMENT_VARIABLES.md) — full variable list
- [12_DOCKER_PRODUCTION_SETUP.md](12_DOCKER_PRODUCTION_SETUP.md) — production container
- [../documentations/TESTING_GUIDE.md](../documentations/TESTING_GUIDE.md) — mentions LangSmith for inspection

Plan reference: `.cursor/plans/po_parsing_ai_agent_211da517.plan.md` (LangSmith / env).
