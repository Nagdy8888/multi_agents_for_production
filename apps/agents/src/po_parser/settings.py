"""Agent-level settings (shared env not owned by a single service)."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class PoParserAgentSettings(BaseSettings):
    """Reserved for future agent flags; services keep their own `settings.py`."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
