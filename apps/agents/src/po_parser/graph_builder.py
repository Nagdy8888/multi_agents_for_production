"""LangGraph StateGraph wiring for the PO pipeline."""

from langgraph.graph import END, START, StateGraph

from src.po_parser.nodes import (
    airtable_writer_node,
    classify_node,
    extract_po_node,
    gas_callback_node,
    route_after_classify,
    validator_node,
)
from src.po_parser.schemas.states import AgentState


def build_graph():
    gb = StateGraph(AgentState)
    gb.add_node("classify", classify_node)
    gb.add_node("extract_po", extract_po_node)
    gb.add_node("validate", validator_node)
    gb.add_node("write_airtable", airtable_writer_node)
    gb.add_node("callback_gas", gas_callback_node)

    gb.add_edge(START, "classify")
    gb.add_conditional_edges(
        "classify",
        route_after_classify,
        {"parse": "extract_po", "end": END},
    )
    gb.add_edge("extract_po", "validate")
    gb.add_edge("validate", "write_airtable")
    gb.add_edge("write_airtable", "callback_gas")
    gb.add_edge("callback_gas", END)
    return gb.compile()
