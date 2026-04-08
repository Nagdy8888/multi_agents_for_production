# Schemas

- **Pydantic v2** — use `model_validate` / `model_validate_json` / `model_dump` (not v1 `parse_obj` / `dict`).
- **`AgentState`** — TypedDict for LangGraph state; initialize all keys when invoking the graph.
