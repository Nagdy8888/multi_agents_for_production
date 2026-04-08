"""Webhook authentication (GAS -> Python)."""

import hmac
import os

from fastapi import Header, HTTPException


def verify_webhook_secret(
    x_webhook_secret: str | None = Header(default=None, alias="x-webhook-secret"),
) -> None:
    expected = os.getenv("WEBHOOK_SECRET", "")
    if not expected or not x_webhook_secret:
        raise HTTPException(status_code=401, detail="Missing webhook secret")
    a, b = x_webhook_secret.encode("utf-8"), expected.encode("utf-8")
    if not hmac.compare_digest(a, b):
        raise HTTPException(status_code=401, detail="Invalid webhook secret")
