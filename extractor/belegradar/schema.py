"""The extraction schema: what BelegRadar pulls out of an invoice.

The German fields are the differentiator: VAT breakdown per rate
(MwSt-Aufschluesselung), USt-IdNr, IBAN, and the paragraph 14 UStG
required-fields check all reflect how DACH back offices actually
process invoices.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from enum import Enum

from pydantic import BaseModel, Field


class Confidence(str, Enum):
    high = "high"
    medium = "medium"
    low = "low"


class LineItem(BaseModel):
    description: str
    quantity: Decimal = Decimal(1)
    unit_price: Decimal
    total: Decimal


class VatEntry(BaseModel):
    """One VAT rate bucket: rate in percent (19, 7, 0 for DE), the net base
    it applies to, and the resulting tax amount."""

    rate: Decimal
    base: Decimal
    amount: Decimal


class InvoiceExtraction(BaseModel):
    vendor_name: str
    vendor_address: str | None = None
    vendor_vat_id: str | None = None  # USt-IdNr, format-validated separately
    invoice_number: str
    invoice_date: date | None = None
    due_date: date | None = None
    customer_name: str | None = None
    line_items: list[LineItem] = Field(default_factory=list)
    net_total: Decimal | None = None
    vat_breakdown: list[VatEntry] = Field(default_factory=list)
    gross_total: Decimal | None = None
    currency: str = "EUR"
    iban: str | None = None
    bic: str | None = None
    payment_terms: str | None = None
    # LLM self-reported confidence per field name; rule checks may downgrade.
    confidence: dict[str, Confidence] = Field(default_factory=dict)


class Flag(BaseModel):
    """One validation finding. Severity 'error' means the numbers do not add
    up; 'warn' means a field is missing or failed a format check."""

    field: str
    severity: str  # "error" | "warn"
    message: str


class ValidationReport(BaseModel):
    flags: list[Flag] = Field(default_factory=list)
    pflichtangaben: dict[str, bool] = Field(default_factory=dict)

    @property
    def ok(self) -> bool:
        return not any(f.severity == "error" for f in self.flags)
