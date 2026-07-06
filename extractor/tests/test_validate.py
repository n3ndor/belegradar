from decimal import Decimal

from belegradar.schema import InvoiceExtraction, LineItem, VatEntry
from belegradar.validate import iban_is_valid, validate, vat_id_is_valid


def make_invoice(**overrides) -> InvoiceExtraction:
    base = dict(
        vendor_name="Muster GmbH",
        vendor_address="Musterstr. 1, 10115 Berlin",
        vendor_vat_id="DE123456789",
        invoice_number="RE-2026-001",
        invoice_date="2026-07-01",
        line_items=[
            LineItem(description="Beratung", quantity=Decimal(10),
                     unit_price=Decimal("100.00"), total=Decimal("1000.00")),
        ],
        net_total=Decimal("1000.00"),
        vat_breakdown=[VatEntry(rate=Decimal(19), base=Decimal("1000.00"),
                                amount=Decimal("190.00"))],
        gross_total=Decimal("1190.00"),
        iban="DE89370400440532013000",  # official ISO example, checksum-valid
    )
    base.update(overrides)
    return InvoiceExtraction(**base)


def test_valid_invoice_has_no_errors():
    report = validate(make_invoice())
    assert report.ok
    assert all(report.pflichtangaben.values())


def test_gross_mismatch_is_an_error():
    report = validate(make_invoice(gross_total=Decimal("1200.00")))
    assert not report.ok
    assert any(f.field == "gross_total" for f in report.flags)


def test_line_items_must_sum_to_net():
    report = validate(make_invoice(net_total=Decimal("900.00"),
                                   gross_total=Decimal("1071.00"),
                                   vat_breakdown=[VatEntry(rate=Decimal(19),
                                                           base=Decimal("900.00"),
                                                           amount=Decimal("171.00"))]))
    assert any(f.field == "net_total" and f.severity == "error" for f in report.flags)


def test_vat_amount_must_match_rate():
    report = validate(make_invoice(
        vat_breakdown=[VatEntry(rate=Decimal(19), base=Decimal("1000.00"),
                                amount=Decimal("150.00"))],
        gross_total=Decimal("1150.00"),
    ))
    assert any(f.field.startswith("vat_breakdown") for f in report.flags)


def test_rounding_tolerance_accepted():
    # 33.33 * 3 = 99.99 vs net 100.00: inside the 2-cent tolerance
    report = validate(make_invoice(
        line_items=[LineItem(description="x", quantity=Decimal(3),
                             unit_price=Decimal("33.33"), total=Decimal("99.99"))],
        net_total=Decimal("100.00"),
        vat_breakdown=[VatEntry(rate=Decimal(19), base=Decimal("100.00"),
                                amount=Decimal("19.00"))],
        gross_total=Decimal("119.00"),
    ))
    assert report.ok


def test_iban_checksum():
    assert iban_is_valid("DE89 3704 0044 0532 0130 00")  # spaces tolerated
    assert not iban_is_valid("DE89370400440532013001")  # last digit flipped
    assert not iban_is_valid("DE8937040044053201300")  # wrong length for DE
    assert not iban_is_valid("XX00INVALID")


def test_bad_iban_is_flagged():
    report = validate(make_invoice(iban="DE89370400440532013001"))
    assert any(f.field == "iban" and f.severity == "error" for f in report.flags)


def test_vat_id_formats():
    assert vat_id_is_valid("DE123456789")
    assert vat_id_is_valid("ATU12345678")
    assert vat_id_is_valid("NL123456789B01")
    assert not vat_id_is_valid("DE12345678")  # too short
    assert not vat_id_is_valid("FANTASIA123")


def test_missing_pflichtangaben_are_warned():
    report = validate(make_invoice(vendor_vat_id=None, invoice_date=None))
    assert report.pflichtangaben["vat_id_or_tax_number"] is False
    assert report.pflichtangaben["invoice_date"] is False
    # missing Pflichtangaben warn but are not arithmetic errors
    assert report.ok
