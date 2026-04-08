from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class GASCallbackSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
        populate_by_name=True,
    )

    webapp_url: str = Field(default="", alias="GAS_WEBAPP_URL")
    webapp_secret: str = Field(default="", alias="GAS_WEBAPP_SECRET")
    timeout: int = 30
