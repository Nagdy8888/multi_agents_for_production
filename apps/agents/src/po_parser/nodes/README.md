# Graph nodes

Contract: `def node_name(state: AgentState) -> dict` — return **only** updated keys; LangGraph merges into state.

Routing: `routing.route_after_classify` returns `"parse"` or `"end"` (strings), mapped to `parse_body` or `END`.
