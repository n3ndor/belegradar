"""LLM structured extraction: invoice text in, validated InvoiceExtraction out.

Division of labor:
- The LLM reads prose and layout and fills the schema (it is good at that).
- It never does arithmetic or locale conversion: every amount is re-parsed
  by numbers.parse_amount, and validate.validate() checks the math.
"""

from __future__ import annotations

from datetime import date, datetime

from pydantic import ValidationError

from .numbers import parse_amount
from .providers import complete_json
from .schema import Confidence, InvoiceExtraction, LineItem, VatEntry

SYSTEM_PROMPT = """You extract structured data from invoice and receipt text.
Reply ONLY with a JSON object with these keys (use null when a value is not
present in the document; never invent values):

vendor_name, vendor_address, vendor_vat_id (the USt-IdNr / VAT id),
invoice_number, invoice_date (YYYY-MM-DD), due_date (YYYY-MM-DD),
customer_name,
line_items: [{description, quantity, unit_price, total}],
net_total, vat_breakdown: [{rate, base, amount}] (one entry per VAT rate),
gross_total, currency (ISO code like EUR),
iban, bic, payment_terms,
confidence: {field_name: "high"|"medium"|"low"} for every field you filled.

Amounts: copy them EXACTLY as written in the document, as strings, keeping
the original decimal format (German 1.234,56 or English 1,234.56). Do not
convert, compute, or round anything. Rates are plain numbers (19, 7, 0).
The document language may be German or English."""

AMOUNT_FIELDS = ("net_total", "gross_total")


def extract_invoice(text: str) -> tuple[InvoiceExtraction, int]:
    """Extract a structured invoice from raw text. Returns (extraction, tokens).

    Raises pydantic.ValidationError when the model output cannot be shaped
    into the schema even after normalization.
    """
    raw, tokens = complete_json(SYSTEM_PROMPT, text[:20_000])
    return _shape(raw), tokens


def _shape(raw: dict) -> InvoiceExtraction:
    data: dict = {
        "vendor_name": (raw.get("vendor_name") or "").strip() or "Unknown",
        "vendor_address": _clean_str(raw.get("vendor_address")),
        "vendor_vat_id": _clean_str(raw.get("vendor_vat_id")),
        "invoice_number": (raw.get("invoice_number") or "").strip() or "unknown",
        "invoice_date": _parse_date(raw.get("invoice_date")),
        "due_date": _parse_date(raw.get("due_date")),
        "customer_name": _clean_str(raw.get("customer_name")),
        "currency": (_clean_str(raw.get("currency")) or "EUR").upper()[:3],
        "iban": _clean_str(raw.get("iban")),
        "bic": _clean_str(raw.get("bic")),
        "payment_terms": _clean_str(raw.get("payment_terms")),
    }

    for field in AMOUNT_FIELDS:
        data[field] = parse_amount(raw.get(field))

    items = []
    for item in raw.get("line_items") or []:
        try:
            items.append(LineItem(
                description=str(item.get("description") or "").strip()[:300],
                quantity=parse_amount(item.get("quantity")) or 1,
                unit_price=parse_amount(item.get("unit_price")) or 0,
                total=parse_amount(item.get("total")) or 0,
            ))
        except (ValidationError, TypeError):
            continue  # a malformed line item must not sink the document
    data["line_items"] = items

    vat = []
    for entry in raw.get("vat_breakdown") or []:
        rate = parse_amount(entry.get("rate"))
        base = parse_amount(entry.get("base"))
        amount = parse_amount(entry.get("amount"))
        if rate is None or amount is None:
            continue
        vat.append(VatEntry(rate=rate, base=base if base is not None else 0, amount=amount))
    data["vat_breakdown"] = vat

    confidence = {}
    for key, value in (raw.get("confidence") or {}).items():
        try:
            confidence[str(key)] = Confidence(str(value).lower())
        except ValueError:
            continue
    data["confidence"] = confidence

    return InvoiceExtraction(**data)


def _clean_str(value) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


_DATE_FORMATS = ("%Y-%m-%d", "%d.%m.%Y", "%d/%m/%Y", "%B %d, %Y", "%d %B %Y")


def _parse_date(value) -> date | None:
    """Deterministic date parsing; the model copies dates as written and we
    handle the formats. Smaller models do not reliably convert German
    DD.MM.YYYY to ISO, and per the design rule the LLM is never trusted
    with format conversion anyway."""
    if not value:
        return None
    text = str(value).strip()
    for fmt in _DATE_FORMATS:
        try:
            return datetime.strptime(text[:20], fmt).date()
        except ValueError:
            continue
    try:
        return date.fromisoformat(text[:10])
    except ValueError:
        return None
