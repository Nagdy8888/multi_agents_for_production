"""Build LangGraph pipeline: preprocessor → vision → parallel taggers → validator → confidence → aggregator (Phase 3)."""
from langgraph.graph import END, START, StateGraph

from .nodes import (
    image_preprocessor,
    vision_analyzer,
    validate_tags,
    filter_by_confidence,
    aggregate_tags,
    ALL_TAGGERS,
    TAGGER_NODE_NAMES,
)
from .schemas.states import ImageTaggingState


def build_graph():
    """Full pipeline with parallel taggers and validator/confidence/aggregator."""
    builder = StateGraph(ImageTaggingState)

    builder.add_node("image_preprocessor", image_preprocessor)
    builder.add_node("vision_analyzer", vision_analyzer)
    for name, fn in ALL_TAGGERS.items():
        builder.add_node(name, fn)
    builder.add_node("tag_validator", validate_tags)
    builder.add_node("confidence_filter", filter_by_confidence)
    builder.add_node("tag_aggregator", aggregate_tags)

    builder.add_edge(START, "image_preprocessor")
    builder.add_edge("image_preprocessor", "vision_analyzer")
    for name in TAGGER_NODE_NAMES:
        builder.add_edge("vision_analyzer", name)
        builder.add_edge(name, "tag_validator")
    builder.add_edge("tag_validator", "confidence_filter")
    builder.add_edge("confidence_filter", "tag_aggregator")
    builder.add_edge("tag_aggregator", END)

    return builder.compile()