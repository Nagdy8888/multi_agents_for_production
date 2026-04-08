"""Webhook payload models (GAS -> Python)."""

from pydantic import BaseModel, Field


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
