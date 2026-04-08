"""Shared service utilities (optional helpers for settings-backed clients)."""

from __future__ import annotations

from typing import TypeVar

from pydantic_settings import BaseSettings

S = TypeVar("S", bound=BaseSettings)


def load_settings(settings_cls: type[S]) -> S:
    """Instantiate a pydantic-settings class (loads `.env` per model_config)."""
    return settings_cls()
