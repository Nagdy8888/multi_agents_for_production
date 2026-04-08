from __future__ import annotations

import asyncio
import logging
import time
from typing import Any

import httpx

from src.services.gas_callback.settings import GASCallbackSettings

logger = logging.getLogger(__name__)


class GASCallbackClient:
    """POST results to GAS Web App; `secret` must be in JSON body (GAS cannot read custom headers)."""

    def __init__(self, settings: GASCallbackSettings | None = None) -> None:
        self.settings = settings or GASCallbackSettings()

    async def send_results_async(self, payload: dict[str, Any]) -> dict[str, Any]:
        if not self.settings.webapp_url:
            logger.error("GAS_WEBAPP_URL is not set")
            return {"status": "error", "message": "Missing GAS_WEBAPP_URL"}

        body = dict(payload)
        body["secret"] = self.settings.webapp_secret

        timeout = httpx.Timeout(float(self.settings.timeout))
        last_exc: Exception | None = None
        for attempt in range(2):
            try:
                async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
                    r = await client.post(
                        self.settings.webapp_url,
                        json=body,
                        headers={"Content-Type": "application/json"},
                    )
                try:
                    return r.json()
                except Exception:
                    return {
                        "status": "ok" if r.is_success else "error",
                        "body": r.text,
                    }
            except Exception as e:
                last_exc = e
                logger.warning("GAS callback attempt %s failed: %s", attempt + 1, e)
                if attempt == 0:
                    time.sleep(2)
        logger.error("GAS callback failed after retry: %s", last_exc)
        return {"status": "error", "message": str(last_exc)}

    def send_results(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Sync entry for LangGraph nodes / thread pools (wraps async httpx)."""
        return asyncio.run(self.send_results_async(payload))
