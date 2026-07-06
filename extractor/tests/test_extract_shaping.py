"""Deterministic shaping tests: no LLM, feed _shape the kind of JSON models
actually return (including the sloppy variants smaller models produce)."""

from datetime import date
from decimal import Decimal

from belegradar.extract import _parse_date, _shape


def test_parse_date_formats():
    assert _parse_date("2026-05-12") == date(2026, 5, 12)
    assert _parse_date("12.05.2026") == date(2026, 5, 12)  # German, verbatim copy
    assert _parse_date("12/05/2026") == date(2026, 5, 12)
    assert _parse_date("May 12, 2026") == date(2026, 5, 12)
    assert _parse_date(None) is None
    assert _parse_date("n/a") is None


def test_shape_handles_german_amount_strings():
    inv = _shape({
        "vendor_name": "Muster GmbH",
        "invoice_number": "RE-1",
        "invoice_date": "28.04.2026",
        "net_total": "1.500,00",
        "gross_total": "1.769,60",
        "vat_breakdown": [
            {"rate": "7", "base": "860,00", "amount": "60,20"},
            {"rate": "19", "base": "640,00", "amount": "121,60"},
        ],
        "line_items": [
            {"description": "Catering", "quantity": "1", "unit_price": "860,00", "total": "860,00"},
        ],
        "confidence": {"net_total": "high", "iban": "nonsense-value"},
    })
    assert inv.invoice_date == date(2026, 4, 28)
    assert inv.net_total == Decimal("1500.00")
    assert inv.gross_total == Decimal("1769.60")
    assert {v.rate for v in inv.vat_breakdown} == {Decimal(7), Decimal(19)}
    assert inv.line_items[0].total == Decimal("860.00")
    assert "net_total" in inv.confidence
    assert "iban" not in inv.confidence  # invalid enum value dropped


def test_shape_survives_malformed_line_items():
    inv = _shape({
        "vendor_name": "X",
        "invoice_number": "1",
        "line_items": [
            {"description": "ok", "quantity": 1, "unit_price": "10", "total": "10"},
            {"description": None, "quantity": "abc", "unit_price": None, "total": None},
        ],
    })
    assert len(inv.line_items) == 2  # defaults keep the malformed one harmless
    assert inv.line_items[1].total == 0
