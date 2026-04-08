from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class OpenAISettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="OPENAI_",
        env_file=".env",
        extra="ignore",
    )

    api_key: str = Field(default="")
    classification_model: str = "gpt-4o-mini"
    extraction_model: str = "gpt-4o-mini"
    extraction_vision_model: str = "gpt-4o"
    ocr_model: str = "gpt-4o"
    max_tokens: int = 4096
    temperature: float = 0.0
