"""Rule checks beyond the LLM. This is the engineering showcase: the model
extracts, plain Python verifies.

- gross = net + sum(vat amounts), within rounding tolerance
- line items sum to net_total, within tolerance
- IBAN mod-97 checksum (ISO 13616), pure Python
- USt-IdNr / VAT id format per country prefix
- paragraph 14 UStG required-fields checklist (Pflichtangaben)
"""

from __future__ import annotations

import re
from decimal import Decimal

from .schema import Flag, InvoiceExtraction, ValidationReport

TOLERANCE = Decimal("0.02")  # rounding differences accumulate per line

# VAT id formats for the markets the demo targets (extendable).
VAT_ID_FORMATS = {
    "DE": re.compile(r"^DE[0-9]{9}$"),
    "AT": re.compile(r"^ATU[0-9]{8}$"),
    "CH": re.compile(r"^CHE-?[0-9]{3}\.?[0-9]{3}\.?[0-9]{3}(\s?(MWST|TVA|IVA))?$"),
    "NL": re.compile(r"^NL[0-9]{9}B[0-9]{2}$"),
    "FR": re.compile(r"^FR[0-9A-Z]{2}[0-9]{9}$"),
    "GB": re.compile(r"^GB([0-9]{9}|[0-9]{12})$"),
}

IBAN_LENGTHS = {
    "DE": 22, "AT": 20, "CH": 21, "NL": 18, "FR": 27, "GB": 22, "ES": 24,
    "IT": 27, "BE": 16, "LU": 20, "PL": 28, "CZ": 24, "DK": 18, "SE": 24,
}


def iban_is_valid(iban: str) -> bool:
    """ISO 13616 mod-97 checksum, no dependencies."""
    compact = re.sub(r"\s+", "", iban).upper()
    if not re.match(r"^[A-Z]{2}[0-9]{2}[A-Z0-9]{10,30}$", compact):
        return False
    expected_len = IBAN_LENGTHS.get(compact[:2])
    if expected_len and len(compact) != expected_len:
        return False
    rearranged = compact[4:] + compact[:4]
    digits = "".join(str(ord(c) - 55) if c.isalpha() else c for c in rearranged)
    return int(digits) % 97 == 1


def vat_id_is_valid(vat_id: str) -> bool:
    compact = re.sub(r"\s+", "", vat_id).upper()
    pattern = VAT_ID_FORMATS.get(compact[:2])
    return bool(pattern and pattern.match(compact))


def validate(inv: InvoiceExtraction) -> ValidationReport:
    report = ValidationReport()
    flags = report.flags

    # --- arithmetic ------------------------------------------------------
    if inv.net_total is not None and inv.gross_total is not None and inv.vat_breakdown:
        vat_sum = sum((v.amount for v in inv.vat_breakdown), Decimal(0))
        if abs(inv.net_total + vat_sum - inv.gross_total) > TOLERANCE:
            flags.append(Flag(
                field="gross_total",
                severity="error",
                message=(
                    f"gross ({inv.gross_total}) != net ({inv.net_total}) "
                    f"+ VAT ({vat_sum})"
                ),
            ))

    if inv.line_items and inv.net_total is not None:
        items_sum = sum((li.total for li in inv.line_items), Decimal(0))
        if abs(items_sum - inv.net_total) > TOLERANCE:
            flags.append(Flag(
                field="net_total",
                severity="error",
                message=f"line items sum to {items_sum}, net_total is {inv.net_total}",
            ))

    for i, li in enumerate(inv.line_items):
        if abs(li.quantity * li.unit_price - li.total) > TOLERANCE:
            flags.append(Flag(
                field=f"line_items[{i}]",
                severity="warn",
                message=f"{li.quantity} x {li.unit_price} != {li.total}",
            ))

    for i, v in enumerate(inv.vat_breakdown):
        expected = (v.base * v.rate / Decimal(100)).quantize(Decimal("0.01"))
        if abs(expected - v.amount) > TOLERANCE:
            flags.append(Flag(
                field=f"vat_breakdown[{i}]",
                severity="error",
                message=f"{v.rate}% of {v.base} is {expected}, stated {v.amount}",
            ))

    # --- formats ---------------------------------------------------------
    if inv.iban and not iban_is_valid(inv.iban):
        flags.append(Flag(field="iban", severity="error",
                          message="IBAN fails the mod-97 checksum"))
    if inv.vendor_vat_id and not vat_id_is_valid(inv.vendor_vat_id):
        flags.append(Flag(field="vendor_vat_id", severity="warn",
                          message="VAT id does not match the country format"))

    # --- paragraph 14 UStG Pflichtangaben --------------------------------
    # The fields a German invoice must carry to be valid for input tax
    # deduction. The demo checks presence, not legal sufficiency.
    report.pflichtangaben = {
        "vendor_name_address": bool(inv.vendor_name and inv.vendor_address),
        "vat_id_or_tax_number": bool(inv.vendor_vat_id),
        "invoice_date": inv.invoice_date is not None,
        "invoice_number": bool(inv.invoice_number),
        "line_items": bool(inv.line_items),
        "net_amount": inv.net_total is not None,
        "vat_rate_and_amount": bool(inv.vat_breakdown),
        "gross_amount": inv.gross_total is not None,
    }
    for key, present in report.pflichtangaben.items():
        if not present:
            flags.append(Flag(field=key, severity="warn",
                              message=f"Pflichtangabe missing: {key}"))

    return report
