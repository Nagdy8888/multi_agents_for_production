from __future__ import annotations

import logging
import os
import time
from typing import Any

from openai import APIError, OpenAI, RateLimitError

from src.services.openai.settings import OpenAISettings

logger = logging.getLogger(__name__)


def _wrap(client: OpenAI) -> OpenAI:
    """Wrap the raw OpenAI client with LangSmith instrumentation when tracing is on."""
    if os.getenv("LANGCHAIN_TRACING_V2", "").lower() == "true":
        try:
            from langsmith.wrappers import wrap_openai
            return wrap_openai(client)
        except Exception as e:
            logger.warning("LangSmith wrap_openai failed (tracing disabled): %s", e)
    return client


def _log_tokens(response, label: str) -> str:
    text = (response.choices[0].message.content or "").strip()
    usage = response.usage
    if usage:
        logger.info(
            "%s tokens — prompt: %d, completion: %d, total: %d",
            label,
            usage.prompt_tokens,
            usage.completion_tokens,
            usage.total_tokens,
        )
    return text


class OpenAIClient:
    def __init__(self, settings: OpenAISettings | None = None) -> None:
        self.settings = settings or OpenAISettings()
        self._client: OpenAI | None = None
        if self.settings.api_key:
            self._client = _wrap(OpenAI(api_key=self.settings.api_key))

    @property
    def enabled(self) -> bool:
        return self._client is not None

    def chat_completion(
        self,
        messages: list[dict[str, Any]],
        model: str | None = None,
        json_mode: bool = False,
    ) -> str:
        if not self._client:
            raise RuntimeError("OpenAI client not configured (missing OPENAI_API_KEY)")
        use_model = model or self.settings.classification_model
        kwargs: dict[str, Any] = {
            "model": use_model,
            "messages": messages,
            "max_tokens": self.settings.max_tokens,
            "temperature": self.settings.temperature,
        }
        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}

        try:
            r = self._client.chat.completions.create(**kwargs)
            return _log_tokens(r, f"chat/{use_model}")
        except RateLimitError:
            logger.warning("OpenAI rate limited; retrying once after 2s")
            time.sleep(2)
            r = self._client.chat.completions.create(**kwargs)
            return _log_tokens(r, f"chat/{use_model} retry")
        except APIError:
            raise

    def vision_completion(self, messages: list[dict[str, Any]]) -> str:
        if not self._client:
            raise RuntimeError("OpenAI client not configured (missing OPENAI_API_KEY)")
        kwargs: dict[str, Any] = {
            "model": self.settings.ocr_model,
            "messages": messages,
            "max_tokens": self.settings.max_tokens,
            "temperature": self.settings.temperature,
        }
        try:
            r = self._client.chat.completions.create(**kwargs)
            return _log_tokens(r, f"vision/{self.settings.ocr_model}")
        except RateLimitError:
            logger.warning("OpenAI vision rate limited; retrying once after 2s")
            time.sleep(2)
            r = self._client.chat.completions.create(**kwargs)
            return _log_tokens(r, f"vision/{self.settings.ocr_model} retry")
        except APIError:
            raise
