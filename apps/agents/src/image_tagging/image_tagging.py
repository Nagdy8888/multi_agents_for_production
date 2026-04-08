"""Compiled graph export for image tagging pipeline (LangGraph Studio loads this as a module; use absolute import)."""
from src.image_tagging.graph_builder import build_graph

graph = build_graph()

__all__ = ["graph", "build_graph"]
