# LangGraph Studio (optional)

> **Prev:** [15_LANGSMITH_SETUP.md](15_LANGSMITH_SETUP.md) | **Index:** [00_SETUP_INDEX.md](00_SETUP_INDEX.md) | **Next:** [17_END_TO_END_VERIFICATION.md](17_END_TO_END_VERIFICATION.md)

```powershell
cd apps/agents
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
pip install "langgraph-cli[inmem]"
$env:PYTHONPATH = (Get-Location).Path
langgraph dev
```

Studio defaults to **127.0.0.1:2024** (not 8000).

Select graphs **`po_parser`** or **`image_tagging`**.

`langgraph.json` → `"env": "../../.env"` for keys when invoking LLM nodes.

**Troubleshooting:** Use the CLI name **`langgraph`** (not `lenggraph`). If graphs fail with `No module named 'src'`, set `PYTHONPATH` to the `apps/agents` directory (see above) before `langgraph dev`. The Studio entry files `po_parser.py` and `image_tagging.py` use `from src....` imports so LangGraph can load them by file path.
