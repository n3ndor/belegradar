from decimal import Decimal

import pytest

from belegradar.numbers import parse_amount


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        # German formats
        ("1.234,56", Decimal("1234.56")),
        ("1.234.567,89", Decimal("1234567.89")),
        ("12,34", Decimal("12.34")),
        ("0,07", Decimal("0.07")),
        ("1.234", Decimal("1234")),  # German thousands, no decimals
        # English formats
        ("1,234.56", Decimal("1234.56")),
        ("1,234,567.89", Decimal("1234567.89")),
        ("12.34", Decimal("12.34")),
        ("1,234", Decimal("1234")),  # English thousands
        # plain
        ("1234.56", Decimal("1234.56")),
        ("19", Decimal("19")),
        ("-42,50", Decimal("-42.50")),  # credit notes are negative
        # currency noise
        ("1.234,56 EUR", Decimal("1234.56")),
        ("€ 99,00", Decimal("99.00")),
        ("$1,299.00", Decimal("1299.00")),
    ],
)
def test_parse_amount_formats(raw, expected):
    assert parse_amount(raw) == expected


@pytest.mark.parametrize("raw", [None, "", "   ", "n/a", "-", ","])
def test_parse_amount_rejects_junk(raw):
    assert parse_amount(raw) is None


def test_parse_amount_passthrough_numbers():
    assert parse_amount(42) == Decimal("42")
    assert parse_amount(3.14) == Decimal("3.14")
    assert parse_amount(Decimal("9.99")) == Decimal("9.99")
