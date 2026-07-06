# BelegRadar extraction eval

Run: 2026-07-05 02:18 UTC · 16 sample invoices (German, Austrian, English; tricky cases included: mixed VAT rates, discounts, credit note, Kleinunternehmer, missing IBAN) · ~15006 LLM tokens total

| Field | Accuracy |
| --- | --- |
| vendor_name | 16/16 |
| vendor_vat_id | 16/16 |
| invoice_number | 16/16 |
| invoice_date | 16/16 |
| net_total | 16/16 |
| gross_total | 16/16 |
| currency | 16/16 |
| iban | 16/16 |
| vat_breakdown | 16/16 |
| line_item_count | 16/16 |

**Overall: 160/160 (100.0%)**

No field misses in this run.

