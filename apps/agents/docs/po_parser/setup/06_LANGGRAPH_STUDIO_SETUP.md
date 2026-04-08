# LangGraph Studio setup

**When:** After the graph is implemented (`src/po_parser/po_parser.py` exports **`graph`**, root **`langgraph.json`** points to it). Optional for day-to-day running; use Studio to **visualize** nodes/edges and **step through** runs with inspectable state.

**Outcome:** You can open **LangGraph Studio** (browser UI) against this repo, select graph **`po_parser`**, and run or debug with a valid **`AgentState`**-shaped input.

**Related:** [05_LANGSMITH_SETUP.md](05_LANGSMITH_SETUP.md) (tracing in the LangSmith dashboard), [../documentations/LANGGRAPH_REFERENCE.md](../documentations/LANGGRAPH_REFERENCE.md) (graph wiring, `AgentState`).

---

## What you need in this repo (already present)

| Artifact | Purpose |
|----------|---------|
| **[`langgraph.json`](../../langgraph.json)** at **repository root** (next to `Dockerfile`) | Registers graph id **`po_parser`** → `./src/po_parser/po_parser.py:graph` |
| **`graph = build_graph()`** in `po_parser.py` | Compiled `StateGraph` for Studio / CLI |

Do **not** move `langgraph.json` under `src/` ([implementation-pitfalls](../../.cursor/rules/implementation-pitfalls.mdc)).

---

## Path A — LangGraph CLI (`langgraph dev`) — recommended

The official workflow is the **LangGraph CLI** dev server: it loads `langgraph.json`, serves the Studio UI, and hot-reloads on code changes.

### 1. Install CLI (and project deps) locally

This repo normally runs in **Docker**, but Studio is easiest with a **local Python 3.11** environment so the CLI can start the dev server on your machine.

From the **repository root**:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -U pip
pip install -r requirements.txt
pip install "langgraph-cli[inmem]"
```

macOS / Linux:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -r requirements.txt
pip install "langgraph-cli[inmem]"
```

Use **Python 3.11** to match the [Dockerfile](../../Dockerfile).

### 2. `PYTHONPATH` (imports use `src.`)

Imports are like `from src.po_parser...`. The repo root must be on **`PYTHONPATH`** so `src` resolves.

**Windows PowerShell (repo root):**

```powershell
$env:PYTHONPATH = (Get-Location).Path
```

**macOS / Linux:**

```bash
export PYTHONPATH="$(pwd)"
```

Set this **in the same shell** before `langgraph dev`.

### 3. Optional: load `.env` for real LLM / Airtable steps

To step through nodes that call OpenAI or Airtable, copy [.env.example](../../.env.example) to `.env` and fill keys ([04_OPENAI_SETUP.md](04_OPENAI_SETUP.md), [10_AIRTABLE_SETUP.md](10_AIRTABLE_SETUP.md)). The CLI can load env from a file if you extend `langgraph.json` (see **Optional `langgraph.json` tweaks** below), or export variables in the shell before `langgraph dev`.

### 4. Start the dev server

From the **repository root**, with venv activated and `PYTHONPATH` set:

```bash
langgraph dev
```

Defaults (see [LangGraph CLI](https://github.com/langchain-ai/langgraph/blob/main/libs/cli/README.md)):

- Binds to **`127.0.0.1:2024`** (not port 8000 — that is Uvicorn/FastAPI in Docker).
- May open a **browser** tab for Studio; if not, open the URL the CLI prints.

Useful flags:

```bash
langgraph dev --no-browser
langgraph dev --port 2024
langgraph dev -c langgraph.json
```

**Safari / localhost issues:** some setups block plain HTTP on localhost; the LangGraph team documents using a tunnel:

```bash
langgraph dev --tunnel
```

(requires a recent `langgraph-cli`, e.g. `>=0.2.6`).

### 5. Use Studio

1. In the UI, select graph **`po_parser`** (name from `langgraph.json` → `"graphs"` key).
2. Confirm the **graph visualization** matches [graph_builder.py](../../src/po_parser/graph_builder.py) (nodes and edges).
3. **Run** / **step** with an initial state shaped like FastAPI’s `initial` dict in [`main.py`](../../src/api/main.py): at minimum `email` (an `IncomingEmail`-compatible object), lists like `pdf_texts`, `excel_data`, `errors`, `processing_start_time`, and other `AgentState` keys — see [LANGGRAPH_REFERENCE.md](../documentations/LANGGRAPH_REFERENCE.md) § LangGraph Studio.

Using **mock** attachment data is fine for stepping through parsers; **OpenAI** / **Airtable** need valid `.env` if you execute those nodes.

---

## Path B — LangSmith web app (Studio entry)

1. Sign in at [smith.langchain.com](https://smith.langchain.com).
2. Open **Studio** from the product navigation (wording may vary by LangSmith version).
3. Connect to a **local** dev server when prompted: base URL is typically **`http://127.0.0.1:2024`** while **`langgraph dev`** is running.

You can use [05_LANGSMITH_SETUP.md](05_LANGSMITH_SETUP.md) in parallel so **traces** appear in the LangSmith project while you exercise the graph.

---

## Optional `langgraph.json` tweaks (CLI)

The [LangGraph CLI](https://github.com/langchain-ai/langgraph/blob/main/libs/cli/README.md) supports extra keys alongside `graphs`, for example:

- **`"env": "./.env"`** — load environment variables for dev runs.
- **`"dependencies": [...]`** — list local packages or pip deps for isolated builds (templates often use a package path; this repo uses a flat `src/` tree + `PYTHONPATH` instead).

If `langgraph dev` fails because the config is too minimal, check the CLI version and the latest **langgraph.json** schema in the LangGraph docs; you may need to add a **`dependencies`** entry that matches your layout.

**Do not remove** the existing `"graphs"` block — it is what registers **`po_parser`**.

---

## How this differs from Docker on port 8000

| | FastAPI (`docker compose --profile production`) | LangGraph CLI (`langgraph dev`) |
|--|-----------------------------------------------|----------------------------------|
| **Port** | **8000** — HTTP API, `POST /webhook/email`, `/health` | **2024** (default) — Studio + LangGraph dev API |
| **Purpose** | Production-style webhook + background `graph.invoke` | Interactive graph debugging |
| **Entry** | `uvicorn src.api.main:app` | `langgraph.json` → `po_parser.py:graph` |

Run **either** the Docker API **or** `langgraph dev` if both bind ports; avoid two processes fighting for the same port.

---

## Troubleshooting

| Symptom | Likely cause | What to do |
|---------|----------------|------------|
| `ModuleNotFoundError: src` | `PYTHONPATH` not set | Export **`PYTHONPATH`** to repo root (step 2). |
| `langgraph: command not found` | CLI not installed | `pip install "langgraph-cli[inmem]"` in the active venv. |
| `No dependencies found in config` | Newer LangGraph CLI | Ensure root **`langgraph.json`** includes `"dependencies": ["."]` (already in this repo). |
| `domain "127.0.0.1" is not allowed` (Studio) | LangSmith blocks local URLs until you allow them | In Studio, **Connect to a local server** → open **Advanced Settings** → add **`127.0.0.1`** (and/or **`localhost`**) to the **allowed domains / allowed origins** list → connect using `http://127.0.0.1:2024`. Or run `langgraph dev --tunnel`, paste the **HTTPS** tunnel URL, and add that host to the allow list (see [Studio troubleshooting](https://docs.langchain.com/langgraph-platform/troubleshooting-studio)). |
| `Failed to fetch` / Studio won’t reach localhost (Chrome 142+) | Private Network Access (PNA) | In Chrome: site menu for `smith.langchain.com` → **Local network access** → **Allow** → reload. |
| Graph empty / import error inside `po_parser` | Missing deps | `pip install -r requirements.txt` in the same venv. |
| LLM nodes fail in Studio | No API key | Set `OPENAI_*` in `.env` or shell; optional `"env": "./.env"` in `langgraph.json`. |
| Studio does not match code | Stale process | Restart `langgraph dev`; use `--no-reload` only when debugging reload issues. |

---

## Related docs

- [../documentations/LANGGRAPH_REFERENCE.md](../documentations/LANGGRAPH_REFERENCE.md) — nodes, `AgentState`, Studio subsection
- [../curriculum/03_GRAPH_INITIALIZATION.md](../curriculum/03_GRAPH_INITIALIZATION.md) — graph init walkthrough
- `.cursor/plans/po_parsing_ai_agent_211da517.plan.md` — plan sections on LangGraph / Studio

Official references: [LangGraph CLI README](https://github.com/langchain-ai/langgraph/blob/main/libs/cli/README.md), [LangGraph Studio repo](https://github.com/langchain-ai/langgraph-studio) (tunnel / Safari notes).
