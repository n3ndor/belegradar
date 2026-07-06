<div align="center">

# 🧾 BelegRadar

**Drop a PDF invoice, get validated structured data back.**

LLM document extraction done like an engineer: strict pydantic schema,
German tax-law-aware validation, confidence flags, and a published accuracy
evaluation. Built for the DACH market; MwSt handling is the point.

![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)
![Groq](https://img.shields.io/badge/LLM-Groq-f55036)
![Cost](https://img.shields.io/badge/infra%20cost-%240%2Fmonth-3ddc97)

</div>

---

## What it does

Every company processes invoices; most still type them into software by hand.
BelegRadar turns a PDF invoice into validated JSON: vendor, line items, VAT
breakdown per rate (MwSt-Aufschluesselung), totals, checksum-validated IBAN,
and a paragraph 14 UStG required-fields check (Pflichtangaben), with flags on
everything that does not add up.

## Division of labor (the engineering part)

The LLM reads prose and layout. It is never trusted with arithmetic:

- Amounts are copied verbatim from the document and re-parsed by
  deterministic German/English locale rules (`1.234,56` vs `1,234.56`).
- Plain Python verifies gross = net + VAT, line-item sums, per-rate VAT
  amounts, IBAN mod-97 checksums, and VAT-id country formats.
- Anything that fails becomes a visible flag, not a silent wrong number.

## Accuracy, published

The eval suite runs the real extraction over a gallery of 16 self-made
sample invoices (German, Austrian, English; deliberately tricky cases:
mixed VAT rates, discount lines, a credit note, Kleinunternehmer with 0%
VAT, missing IBAN) and scores every field against ground truth. Results,
failures included, live in [`extractor/evals/RESULTS.md`](extractor/evals/RESULTS.md).

Samples are generated deterministically (`extractor/samples/generate.py`);
CI fails if the committed gallery drifts from the generator.

## Status

- [x] Milestone 1: extraction core: schema, validators, locale-aware number
      parsing, PDF text extraction with scan rejection, Groq extraction,
      eval suite with published per-field accuracy
- [x] Milestone 2: `belegradar` published on PyPI; Next.js web app
      (`web/`) with drag-and-drop, sample gallery, side-by-side result view,
      confidence dots, VAT breakdown, and the Pflichtangaben checklist. The
      live demo runs the published package via a Vercel Python function.
- [ ] Milestone 3: deploy to beleg.nagysolution.com, OG image, LinkedIn launch

## Repository layout

```
extractor/   the belegradar Python package (published to PyPI) + tests + evals + samples
web/         Next.js frontend + api/extract.py (Vercel Python function) that
             pip-installs belegradar; devserver.py runs the API locally
```

## Honest constraints

- Text-layer PDFs only. Scanned or photographed invoices are politely
  rejected; free reliable OCR at $0/month does not exist, and pretending
  would produce silently wrong data. OCR is a roadmap item.
- Extraction will not be perfect; the product stance is extraction WITH
  validation and flags, which is what real back-office workflows need.
- Sample invoices are entirely fictional. Never feed real third-party
  invoices into demos.

---

<div align="center">

Built by [**Nandor Nagy**](https://github.com/n3ndor) · part of a public portfolio ·
[nagysolution.com](https://nagysolution.com)

</div>
