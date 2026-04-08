"""Extracted PO structures."""

from typing import Optional

from pydantic import BaseModel, Field, field_validator


class Destination(BaseModel):
    dc_name: Optional[str] = None
    address: Optional[str] = None


class POItem(BaseModel):
    sku: Optional[str] = None
    description: Optional[str] = None
    quantity: Optional[int] = None
    unit_price: Optional[float] = None
    total_price: Optional[float] = None
    destination: Optional[str] = None


class ExtractedPO(BaseModel):
    po_number: Optional[str] = None
    customer: Optional[str] = None
    po_date: Optional[str] = None
    ship_date: Optional[str] = None
    cancel_date: Optional[str] = None
    items: list[POItem] = Field(default_factory=list)
    destinations: list[Destination] = Field(default_factory=list)
    source_type: Optional[str] = None
    raw_confidence: Optional[float] = None
    total_amount: Optional[float] = None
    currency: Optional[str] = "USD"
    payment_terms: Optional[str] = None
    ship_to: Optional[str] = None
    bill_to: Optional[str] = None

    @field_validator("currency", mode="before")
    @classmethod
    def _currency_not_null(cls, v: object) -> str:
        if v is None or (isinstance(v, str) and not v.strip()):
            return "USD"
        return str(v)
