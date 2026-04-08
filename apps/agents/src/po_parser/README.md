# PO parser agent (LangGraph)

- **`po_parser.py`** — Exports compiled `graph` for `langgraph.json` / Studio.
- **`graph_builder.py`** — `StateGraph(AgentState)`, `START` / `END`, conditional route after classify.
- **`nodes/`** — Each node returns a **partial** `dict` (pitfall #7).
- **`schemas/`** — Pydantic models + `AgentState` TypedDict.
- **`tools/`** — Helpers (e.g. temp files / base64 for attachments).
- **`configuration.py`** / **`settings.py`** / **`utils.py`** — Hooks for future config and small utilities.

Python does **not** call Gmail/Sheets APIs; GAS handles Google after the callback.
