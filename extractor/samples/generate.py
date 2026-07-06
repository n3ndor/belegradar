"""Generate the sample invoice gallery: fake PDFs + ground truth JSON.

Every invoice is entirely fictional (companies, addresses, IBANs are the
official ISO/test examples or made up but checksum-valid). Totals are
computed from the line items, so the ground truth is consistent by
construction. Deterministic: same input data, same output files.

Usage:  python samples/generate.py
"""

from __future__ import annotations

import json
import sys
from datetime import date
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen.canvas import Canvas

OUT = Path(__file__).parent

# Checksum-valid test IBANs (official examples / generated valid).
IBAN_DE = "DE89370400440532013000"
IBAN_DE2 = "DE02120300000000202051"
IBAN_AT = "AT611904300234573201"
IBAN_NL = "NL91ABNA0417164300"
IBAN_GB = "GB29NWBK60161331926819"


def de(amount: Decimal) -> str:
    """1234.56 -> '1.234,56'"""
    s = f"{amount:,.2f}"  # 1,234.56
    return s.replace(",", "_").replace(".", ",").replace("_", ".")


def en(amount: Decimal) -> str:
    return f"{amount:,.2f}"


def q2(x: Decimal) -> Decimal:
    return x.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


INVOICES = [
    # --- German, single 19% rate, the baseline ---------------------------
    dict(
        id="01_de_simple", lang="de", vendor="Schreiner & Sohn GmbH",
        address="Handwerkerweg 12, 80331 München", vat_id="DE123456789",
        number="RE-2026-0101", inv_date=date(2026, 5, 12), due=date(2026, 6, 11),
        customer="Bergblick Hotel AG", iban=IBAN_DE, bic="COBADEFFXXX",
        items=[("Einbauschrank Eiche, Anfertigung", 1, "2400.00", 19),
               ("Montage vor Ort", 8, "65.00", 19)],
        terms="Zahlbar innerhalb von 30 Tagen ohne Abzug.",
    ),
    # --- German, 7% only (books) -----------------------------------------
    dict(
        id="02_de_7pct", lang="de", vendor="Buchhandlung Lesezeit e.K.",
        address="Marktplatz 3, 04109 Leipzig", vat_id="DE813992525",
        number="2026-1187", inv_date=date(2026, 6, 2), due=None,
        customer="Stadtbibliothek Leipzig", iban=IBAN_DE2, bic=None,
        items=[("Fachbuch: Moderne Holzverbindungen", 12, "34.90", 7),
               ("Kinderbuch-Paket Fruehling", 3, "89.50", 7)],
        terms="Bereits per Lastschrift beglichen.",
    ),
    # --- German, mixed 19% + 7% (restaurant catering) ---------------------
    dict(
        id="03_de_mixed_rates", lang="de", vendor="Gasthaus zur Linde",
        address="Lindenstr. 8, 79098 Freiburg", vat_id="DE297543867",
        number="R-4471", inv_date=date(2026, 4, 28), due=date(2026, 5, 12),
        customer="Weber Consulting GmbH", iban=IBAN_DE, bic="GENODEF1S02",
        items=[("Catering Speisen (7% USt)", 1, "860.00", 7),
               ("Getraenke (19% USt)", 1, "412.00", 19),
               ("Servicepersonal 6 Std (19% USt)", 6, "38.00", 19)],
        terms="Zahlbar sofort netto.",
    ),
    # --- German with discount line (negative) -----------------------------
    dict(
        id="04_de_discount", lang="de", vendor="BüroTech Handels GmbH",
        address="Industriering 44, 30179 Hannover", vat_id="DE118645675",
        number="RG26-00893", inv_date=date(2026, 3, 15), due=date(2026, 4, 14),
        customer="Kanzlei Dr. Sommer", iban=IBAN_DE2, bic="NOLADE2HXXX",
        items=[("Bürostuhl ErgoPlus", 4, "289.00", 19),
               ("Schreibtisch elektrisch", 2, "549.00", 19),
               ("Treuerabatt 5%", 1, "-112.70", 19)],
        terms="30 Tage netto, 2% Skonto bei Zahlung in 10 Tagen.",
    ),
    # --- German Kleinunternehmer (0% VAT, §19 UStG note) -------------------
    dict(
        id="05_de_kleinunternehmer", lang="de", vendor="Fotografie Anna Bergmann",
        address="Am Muehlbach 2, 87561 Oberstdorf", vat_id=None,
        number="2026-031", inv_date=date(2026, 6, 20), due=date(2026, 7, 4),
        customer="Alpenverein Sektion Allgäu", iban=IBAN_DE, bic=None,
        items=[("Vereinsfest Fotoreportage", 1, "480.00", 0),
               ("Bildbearbeitung 40 Fotos", 40, "3.50", 0)],
        terms="Gemäß §19 UStG wird keine Umsatzsteuer berechnet.",
    ),
    # --- German credit note (Gutschrift, negative amounts) -----------------
    dict(
        id="06_de_gutschrift", lang="de", vendor="BüroTech Handels GmbH",
        address="Industriering 44, 30179 Hannover", vat_id="DE118645675",
        number="GS26-00102", inv_date=date(2026, 4, 2), due=None,
        customer="Kanzlei Dr. Sommer", iban=IBAN_DE2, bic="NOLADE2HXXX",
        items=[("Gutschrift: Retoure Bürostuhl ErgoPlus", 1, "-289.00", 19)],
        terms="Gutschrift, wird mit der naechsten Rechnung verrechnet.",
        title="GUTSCHRIFT",
    ),
    # --- German, missing IBAN (deliberate gap) -----------------------------
    dict(
        id="07_de_no_iban", lang="de", vendor="Nachhilfe Institut Klug",
        address="Schulstr. 19, 50667 Köln", vat_id="DE327556139",
        number="NIK-2026-2201", inv_date=date(2026, 5, 30), due=date(2026, 6, 13),
        customer="Familie Öztürk", iban=None, bic=None,
        items=[("Mathematik Nachhilfe Mai (8 Einheiten)", 8, "42.00", 19)],
        terms="Betrag wird per SEPA-Lastschrift eingezogen.",
    ),
    # --- Austrian invoice (ATU vat id, 20% rate) ---------------------------
    dict(
        id="08_at_20pct", lang="de", vendor="Alpenblick Software GmbH",
        address="Getreidegasse 31, 5020 Salzburg, Österreich", vat_id="ATU12345678",
        number="A-2026-077", inv_date=date(2026, 6, 10), due=date(2026, 7, 10),
        customer="Bergbahnen Kitzbühel AG", iban=IBAN_AT, bic="SPSBAT21XXX",
        items=[("Wartungsvertrag Q2/2026", 1, "1500.00", 20),
               ("Zusatzentwicklung Schnittstellen", 12, "110.00", 20)],
        terms="Zahlbar binnen 30 Tagen.",
    ),
    # --- English, EU style with VAT ----------------------------------------
    dict(
        id="09_en_nl_vat", lang="en", vendor="Windmill Digital B.V.",
        address="Keizersgracht 120, 1015 CX Amsterdam, Netherlands",
        vat_id="NL123456789B01",
        number="INV-2026-0455", inv_date=date(2026, 5, 5), due=date(2026, 6, 4),
        customer="Nordwind Logistics GmbH", iban=IBAN_NL, bic="ABNANL2A",
        items=[("UX design sprint (2 weeks)", 1, "6800.00", 21),
               ("Design system documentation", 1, "1200.00", 21)],
        terms="Payment due within 30 days of invoice date.",
    ),
    # --- English, UK, 20% -------------------------------------------------
    dict(
        id="10_en_uk", lang="en", vendor="Thames Analytics Ltd",
        address="14 Clerkenwell Green, London EC1R 0DP, United Kingdom",
        vat_id="GB123456789",
        number="TA-1187", inv_date=date(2026, 4, 18), due=date(2026, 5, 2),
        customer="Continental Retail SE", iban=IBAN_GB, bic="NWBKGB2L",
        items=[("Market analysis report", 1, "3450.00", 20),
               ("Stakeholder workshop", 2, "780.00", 20)],
        terms="Net 14 days. Late payments subject to statutory interest.",
    ),
    # --- English, USD, no VAT (reverse charge style) -----------------------
    dict(
        id="11_en_usd_novat", lang="en", vendor="Prairie Cloud Services LLC",
        address="2201 Ranch Road, Austin, TX 78701, USA", vat_id=None,
        number="PCS-26-3302", inv_date=date(2026, 6, 1), due=date(2026, 6, 15),
        customer="Datenwerk Berlin GmbH", iban=None, bic=None,
        currency="USD",
        items=[("Managed hosting June 2026", 1, "890.00", 0),
               ("Priority support add-on", 1, "150.00", 0)],
        terms="Reverse charge: VAT to be accounted for by the recipient. Pay by card or ACH.",
    ),
    # --- German, big numbers with thousands separators ---------------------
    dict(
        id="12_de_thousands", lang="de", vendor="Stahlbau Krämer AG",
        address="Hüttenweg 7, 47119 Duisburg", vat_id="DE812526315",
        number="SBK-2026-0044", inv_date=date(2026, 2, 27), due=date(2026, 3, 29),
        customer="Hafen Logistik Duisburg GmbH", iban=IBAN_DE, bic="COBADEFFXXX",
        items=[("Stahltraeger HEB 300, Position A", 24, "1240.00", 19),
               ("Statik-Nachweis", 1, "4850.00", 19),
               ("Lieferung und Kranstellung", 1, "2300.00", 19)],
        terms="Zahlung: 50% Anzahlung erhalten, Rest 30 Tage netto.",
    ),
    # --- German freelancer, hours, English-style layout mix ---------------
    dict(
        id="13_de_freelancer", lang="de", vendor="Jonas Winter IT-Beratung",
        address="Fichtestr. 5, 10967 Berlin", vat_id="DE267352437",
        number="JW-2026-18", inv_date=date(2026, 6, 30), due=date(2026, 7, 14),
        customer="HealthTech Rhein GmbH", iban=IBAN_DE2, bic="BYLADEM1001",
        items=[("Backend-Entwicklung Juni (Stundensatz 95 EUR)", 62, "95.00", 19),
               ("Code-Review Sprint 14", 6, "95.00", 19)],
        terms="Zahlbar innerhalb 14 Tagen ohne Abzug.",
    ),
    # --- English services, quantity fractions ------------------------------
    dict(
        id="14_en_fractions", lang="en", vendor="Beacon Legal Translations",
        address="Rue du Commerce 9, 1000 Brussels, Belgium", vat_id=None,
        number="BLT-0921", inv_date=date(2026, 3, 3), due=date(2026, 3, 17),
        customer="Van Der Berg Advocaten", iban=None, bic=None,
        items=[("Contract translation DE->EN (0.14 EUR/word, 8,450 words)", 1, "1183.00", 21),
               ("Certified copies", 3, "25.00", 21),
               ("Express surcharge 50%", 0.5, "1183.00", 21)],
        terms="Wire transfer within 14 days. Reference the invoice number.",
    ),
    # --- German utility style, small amounts, 19% --------------------------
    dict(
        id="15_de_utility", lang="de", vendor="Stadtwerke Sonnenfeld GmbH",
        address="Energieallee 1, 34117 Kassel", vat_id="DE152847293",
        number="SW-2026-448291", inv_date=date(2026, 1, 31), due=date(2026, 2, 14),
        customer="Herr Martin Vogel", iban=IBAN_DE, bic="HELADEF1KAS",
        items=[("Stromverbrauch 12/2025 (312 kWh)", 312, "0.34", 19),
               ("Grundpreis Dezember", 1, "12.90", 19)],
        terms="Der Betrag wird am 14.02.2026 abgebucht.",
    ),
    # --- English, larger consulting with two rates (goods + services) ------
    dict(
        id="16_en_mixed", lang="en", vendor="Fjord Consulting ApS",
        address="Nyhavn 17, 1051 Copenhagen, Denmark", vat_id=None,
        number="FC-2026-210", inv_date=date(2026, 5, 22), due=date(2026, 6, 21),
        customer="Hansa Maritime GmbH", iban=None, bic=None,
        items=[("Strategy engagement May (services)", 1, "9500.00", 25),
               ("Printed report copies (goods)", 20, "18.00", 25)],
        terms="Payment within 30 days to the account stated in the contract.",
    ),
]


def compute_totals(items: list[tuple], currency: str) -> dict:
    """Totals from line items: per-rate bases, VAT amounts, net, gross."""
    by_rate: dict[Decimal, Decimal] = {}
    for _desc, qty, unit, rate in items:
        total = q2(Decimal(str(qty)) * Decimal(unit))
        by_rate.setdefault(Decimal(rate), Decimal(0))
        by_rate[Decimal(rate)] += total
    net = q2(sum(by_rate.values(), Decimal(0)))
    vat_entries = [
        {"rate": str(rate), "base": str(q2(base)), "amount": str(q2(base * rate / 100))}
        for rate, base in sorted(by_rate.items()) if rate != 0
    ]
    vat_total = q2(sum((Decimal(v["amount"]) for v in vat_entries), Decimal(0)))
    return {
        "net_total": str(net),
        "vat_breakdown": vat_entries,
        "gross_total": str(q2(net + vat_total)),
        "currency": currency,
    }


LABELS = {
    "de": dict(invoice="RECHNUNG", number="Rechnungsnummer", inv_date="Rechnungsdatum",
               due="Faellig bis", customer="Rechnungsempfaenger", pos="Pos. Beschreibung",
               qty="Menge", unit="Einzelpreis", total="Gesamt", net="Nettobetrag",
               vat="USt", gross="Rechnungsbetrag", vat_id="USt-IdNr.", terms=""),
    "en": dict(invoice="INVOICE", number="Invoice number", inv_date="Invoice date",
               due="Due date", customer="Bill to", pos="Description",
               qty="Qty", unit="Unit price", total="Amount", net="Subtotal",
               vat="VAT", gross="Total due", vat_id="VAT ID", terms=""),
}


def render_pdf(spec: dict, totals: dict, path: Path) -> None:
    lang = spec["lang"]
    fmt = de if lang == "de" else en
    labels = LABELS[lang]
    cur = totals["currency"]
    # invariant=1 makes reportlab emit a fixed timestamp and document ID, so
    # the same input produces byte-identical PDFs. Without it every run
    # embeds a fresh /CreationDate and /ID, and the CI drift check fails.
    c = Canvas(str(path), pagesize=A4, invariant=1)
    w, h = A4
    y = h - 60

    def line(text: str, size=10, dy=16, bold=False, x=50):
        nonlocal y
        c.setFont("Helvetica-Bold" if bold else "Helvetica", size)
        c.drawString(x, y, text)
        y -= dy

    line(spec["vendor"], size=14, bold=True, dy=18)
    line(spec["address"])
    if spec.get("vat_id"):
        line(f"{labels['vat_id']} {spec['vat_id']}")
    y -= 14
    line(spec.get("title") or labels["invoice"], size=16, bold=True, dy=24)
    line(f"{labels['number']}: {spec['number']}")
    line(f"{labels['inv_date']}: {spec['inv_date'].strftime('%d.%m.%Y' if lang == 'de' else '%B %d, %Y')}")
    if spec.get("due"):
        line(f"{labels['due']}: {spec['due'].strftime('%d.%m.%Y' if lang == 'de' else '%B %d, %Y')}")
    line(f"{labels['customer']}: {spec['customer']}")
    y -= 12

    line(f"{labels['pos']:<58}{labels['qty']:>6}  {labels['unit']:>12}  {labels['total']:>12}", bold=True)
    for desc, qty, unit, rate in spec["items"]:
        total = q2(Decimal(str(qty)) * Decimal(unit))
        qty_s = f"{qty:g}"
        line(f"{desc[:56]:<58}{qty_s:>6}  {fmt(Decimal(unit)):>12}  {fmt(total):>12}", size=9, dy=14)
    y -= 10

    line(f"{labels['net']}: {fmt(Decimal(totals['net_total']))} {cur}", bold=True)
    for v in totals["vat_breakdown"]:
        rate = Decimal(v["rate"])
        line(f"{labels['vat']} {rate:g}% ({fmt(Decimal(v['base']))} {cur}): {fmt(Decimal(v['amount']))} {cur}")
    line(f"{labels['gross']}: {fmt(Decimal(totals['gross_total']))} {cur}", size=12, bold=True, dy=20)
    y -= 8

    if spec.get("iban"):
        line(f"IBAN: {spec['iban']}" + (f"   BIC: {spec['bic']}" if spec.get("bic") else ""))
    if spec.get("terms"):
        line(spec["terms"], size=9)
    c.showPage()
    c.save()


def main() -> int:
    for spec in INVOICES:
        currency = spec.get("currency", "EUR")
        totals = compute_totals(spec["items"], currency)
        truth = {
            "vendor_name": spec["vendor"],
            "vendor_vat_id": spec.get("vat_id"),
            "invoice_number": spec["number"],
            "invoice_date": spec["inv_date"].isoformat(),
            "iban": spec.get("iban"),
            "line_item_count": len(spec["items"]),
            **totals,
        }
        pdf_path = OUT / f"{spec['id']}.pdf"
        render_pdf(spec, totals, pdf_path)
        (OUT / f"{spec['id']}.json").write_text(
            json.dumps(truth, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        print(f"wrote {pdf_path.name}")
    print(f"{len(INVOICES)} sample invoices generated")
    return 0


if __name__ == "__main__":
    sys.exit(main())
