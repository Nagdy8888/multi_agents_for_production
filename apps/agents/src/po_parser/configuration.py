"""LangGraph configurable runtime parameters (extend when using `config` in invoke)."""

from __future__ import annotations

from typing import TypedDict


class GraphConfiguration(TypedDict, total=False):
    """Optional keys passed through `graph.invoke(..., config=)` in the future."""

    thread_id: str
