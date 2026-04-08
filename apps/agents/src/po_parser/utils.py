"""PO-parser–specific utilities (keep small; prefer `tools/` for file I/O)."""

from __future__ import annotations


def clamp_text(text: str, max_chars: int) -> str:
    if len(text) <= max_chars:
        return text
    return text[:max_chars]
