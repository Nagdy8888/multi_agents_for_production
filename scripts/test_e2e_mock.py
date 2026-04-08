"""
Phase 1.5 mock backend: accepts GAS webhooks and POSTs a hardcoded success callback to GAS Web App.
Run: docker-compose --profile mock up   OR   python scripts/test_e2e_mock.py
"""

from __future__ import annotations

import os
import time
from typing import Any

import httpx
from dotenv import load_dotenv
from fastapi import BackgroundTasks, FastAPI, Header, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

load_dotenv()

WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "")
GAS_WEBAPP_URL = os.getenv("GAS_WEBAPP_URL", "").strip()
GAS_WEBAPP_SECRET = os.getenv("GAS_WEBAPP_SECRET", "")

app = FastAPI(title="PO Parsing Mock E2E", version="0.1.0")


class Attachment(BaseModel):
    filename: str
    content_type: str
    data_base64: str


class IncomingEmail(BaseModel):
    subject: str
    body: str
    sender: str
    timestamp: str
    message_id: str
    attachments: list[Attachment] = Field(default_factory=list)


def send_mock_callback(email: IncomingEmail) -> None:
    time.sleep(2)
    if not GAS_WEBAPP_URL:
        print("ERROR: GAS_WEBAPP_URL is not set; skipping callback.")
        return

    payload: dict[str, Any] = {
        "secret": GAS_WEBAPP_SECRET,
        "message_id": email.message_id,
        "status": "success",
        "po_data": {
            "po_number": "MOCK-001",
            "customer": "Mock Test Company",
            "po_date": "2025-01-15",
            "ship_date": "2025-02-01",
            "source_type": "email",
        },
        "items": [
            {
                "sku": "TEST-SKU-001",
                "description": "Test Item",
                "quantity": 100,
                "unit_price": 5.99,
                "total_price": 599.0,
                "destination": "DC-01",
            }
        ],
        "validation": {"status": "Ready for Review", "issues": []},
        "confidence": 0.95,
        "airtable_url": "https://airtable.com/mock/test-record",
        "processing_time_ms": 2000,
        "errors": [],
    }

    with httpx.Client(timeout=60.0) as client:
        r = client.post(GAS_WEBAPP_URL, json=payload)
        print(f"Callback sent to GAS, response: {r.status_code} {r.text}")


@app.post("/webhook/email")
async def webhook_email(
    email: IncomingEmail,
    background_tasks: BackgroundTasks,
    x_webhook_secret: str | None = Header(default=None, alias="x-webhook-secret"),
) -> JSONResponse:
    if not WEBHOOK_SECRET or not x_webhook_secret:
        raise HTTPException(status_code=401, detail="Missing webhook secret")
    if x_webhook_secret != WEBHOOK_SECRET:
        raise HTTPException(status_code=401, detail="Invalid webhook secret")

    print("Received webhook payload:", email.model_dump())
    background_tasks.add_task(send_mock_callback, email)
    return JSONResponse(
        status_code=202,
        content={"status": "accepted", "message_id": email.message_id},
    )


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "healthy", "mode": "mock"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
