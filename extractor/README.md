<div align="center">

# 🧾 belegradar

**Invoice and receipt extraction with validation, built for the DACH market.**

```
pip install belegradar
```

![PyPI](https://img.shields.io/pypi/v/belegradar)
![Python](https://img.shields.io/badge/Python-3.11%20%7C%203.12%20%7C%203.13-3776AB?logo=python&logoColor=white)
![Typed](https://img.shields.io/badge/typing-py.typed-3ddc97)
![License](https://img.shields.io/badge/license-MIT-blue)

</div>

---

Turn a PDF invoice into validated structured data: vendor, line items, VAT
breakdown per rate (MwSt-Aufschluesselung), totals, checksum-validated IBAN,
and a paragraph 14 UStG required-fields check, with a flag on anything that
does not add up.

The design rule: **the LLM reads, plain Python verifies.** The model copies
values verbatim; deterministic code does all locale number parsing
(`1.234,56` vs `1,234.56`), date parsing, and arithmetic checks.

## Quickstart

```python
from belegradar import extract_text, extract_invoice, validate

text = extract_text(open("invoice.pdf", "rb").read())  # raises on scans
invoice, tokens = extract_invoice(text)                # needs GROQ_API_KEY
report = validate(invoice)

print(invoice.vendor_name, invoice.gross_total, invoice.currency)
for flag in report.flags:
    print(flag.severity, flag.field, flag.message)
print("Pflichtangaben:", report.pflichtangaben)
```

## What it validates (no LLM involved)

- `gross_total == net_total + sum(VAT amounts)`, within rounding tolerance
- line items sum to `net_total`; each `quantity * unit_price == total`
- each VAT bucket: `rate% of base == amount`
- **IBAN** ISO 13616 mod-97 checksum, pure Python
- **VAT id** country formats (DE/AT/CH/NL/FR/GB, extendable)
- **paragraph 14 UStG Pflichtangaben**: presence of every field a German
  invoice must carry to be valid for input-tax deduction

## Utilities

```python
from belegradar import iban_is_valid, vat_id_is_valid
iban_is_valid("DE89 3704 0044 0532 0130 00")  # True (spaces tolerated)
vat_id_is_valid("ATU12345678")                # True
```

## Honest constraints

- **Text-layer PDFs only.** Scanned or photographed invoices raise
  `NoTextLayerError`. There is no reliable free OCR at zero infrastructure
  cost, and pretending would produce silently wrong data. OCR is a roadmap
  item.
- Extraction is not perfect; the product stance is extraction **with
  validation and flags**, which is what real back-office workflows need.
- The LLM provider is swappable (Groq by default via `GROQ_API_KEY`); it is
  never trusted with arithmetic or locale conversion.

## Used in production by

The live demo at [beleg.nagysolution.com](https://beleg.nagysolution.com)
runs this package. Accuracy is measured by an eval suite over a gallery of
fake invoices; results are published in the
[repository](https://github.com/n3ndor/belegradar).

## License

MIT. Built by [Nandor Nagy](https://github.com/n3ndor) as part of a public
portfolio.
