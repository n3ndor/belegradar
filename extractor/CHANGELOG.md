# Changelog

Format follows [Keep a Changelog](https://keepachangelog.com/); the project
adheres to [Semantic Versioning](https://semver.org/).

## [0.1.0] - 2026-07-06

### Added

- `extract_text()`: PDF text-layer extraction (pypdf), rejecting scans and
  over-long documents.
- `extract_invoice()`: LLM structured extraction (Groq, model fallback on
  429) into a validated `InvoiceExtraction`. The model copies values
  verbatim; all number/date parsing is deterministic.
- `validate()`: arithmetic checks (gross/net/VAT, line sums, per-rate VAT),
  IBAN mod-97, VAT-id country formats, and the paragraph 14 UStG
  Pflichtangaben checklist, returned as a `ValidationReport` of flags.
- `iban_is_valid()`, `vat_id_is_valid()` helpers.
- `py.typed`; fully typed.
