"""Conditional edge routing."""

from src.po_parser.schemas.states import AgentState


def route_after_classify(state: AgentState) -> str:
    c = state.get("classification")
    if c is None or not c.is_po or c.confidence < 0.7:
        return "end"
    return "parse"
