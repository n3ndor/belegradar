"""Field-level accuracy eval: run the real extraction (live LLM) over the
sample gallery and score against ground truth.

Usage:
    python evals/run_evals.py         (needs GROQ_API_KEY)

Writes evals/RESULTS.md with per-field accuracy, failures included. Honest
numbers policy: the table is committed as generated.
"""

from __future__ import annotations

import json
import os
import re
import sys
import time
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1]))

from belegradar.extract import extract_invoice
from belegradar.pdftext import extract_text
from belegradar.validate import validate

SAMPLES = Path(__file__).parents[1] / "samples"

SCORED_FIELDS = [
    "vendor_name", "vendor_vat_id", "invoice_number", "invoice_date",
    "net_total", "gross_total", "currency", "iban", "vat_breakdown",
    "line_item_count",
]


def norm_text(v) -> str:
    return re.sub(r"\s+", " ", str(v or "")).strip().lower()


def norm_iban(v) -> str:
    return re.sub(r"\s+", "", str(v or "")).upper()


def compare(field: str, truth, extracted) -> bool:
    if field in ("net_total", "gross_total"):
        if truth is None:
            return extracted is None
        return extracted is not None and Decimal(truth) == extracted
    if field == "vat_breakdown":
        # A zero-amount entry (0% rate on a Kleinunternehmer or reverse-charge
        # invoice) is equivalent to no entry: both mean "no VAT charged".
        want = {(Decimal(v["rate"]), Decimal(v["amount"])) for v in truth
                if Decimal(v["amount"]) != 0}
        got = {(v.rate, v.amount) for v in extracted if v.amount != 0}
        return want == got
    if field == "iban":
        return norm_iban(truth) == norm_iban(extracted)
    if field == "line_item_count":
        return truth == len(extracted)
    if field == "invoice_date":
        return str(truth or "") == (extracted.isoformat() if extracted else "")
    return norm_text(truth) == norm_text(extracted)


def extracted_value(inv, field):
    if field == "line_item_count":
        return inv.line_items
    return getattr(inv, field)


def run() -> int:
    if not os.environ.get("GROQ_API_KEY"):
        print("error: GROQ_API_KEY must be set", file=sys.stderr)
        return 1

    docs = sorted(SAMPLES.glob("*.json"))
    field_hits: dict[str, list[bool]] = {f: [] for f in SCORED_FIELDS}
    failures: list[str] = []
    tokens_total = 0
    flag_notes: list[str] = []

    print(f"evaluating {len(docs)} sample invoices\n")
    for truth_path in docs:
        doc_id = truth_path.stem
        truth = json.loads(truth_path.read_text(encoding="utf-8"))
        text = extract_text((SAMPLES / f"{doc_id}.pdf").read_bytes())

        try:
            inv, tokens = extract_invoice(text)
        except Exception as exc:  # noqa: BLE001 - a doc failing is a result
            failures.append(f"- `{doc_id}`: extraction failed entirely: {exc}")
            for f in SCORED_FIELDS:
                field_hits[f].append(False)
            print(f"  {doc_id:<24} EXTRACTION FAILED: {exc}")
            continue
        tokens_total += tokens

        wrong = []
        for field in SCORED_FIELDS:
            ok = compare(field, truth.get(field) if field != "vat_breakdown"
                         else truth.get("vat_breakdown", []),
                         extracted_value(inv, field))
            field_hits[field].append(ok)
            if not ok:
                wrong.append(field)
        report = validate(inv)
        errors = [f for f in report.flags if f.severity == "error"]
        if errors:
            flag_notes.append(f"- `{doc_id}`: {'; '.join(f.field + ': ' + f.message for f in errors)}")

        status = "OK " if not wrong else f"MISS {', '.join(wrong)}"
        print(f"  {doc_id:<24} {status}")
        if wrong:
            for field in wrong:
                failures.append(
                    f"- `{doc_id}` / {field}: expected "
                    f"`{truth.get(field)}`, got `{extracted_value(inv, field)}`"
                )
        time.sleep(10)  # stay inside Groq free-tier per-minute budgets

    write_results(field_hits, failures, flag_notes, len(docs), tokens_total)

    overall = [hit for hits in field_hits.values() for hit in hits]
    rate = sum(overall) / len(overall)
    print(f"\noverall field accuracy: {rate:.1%} ({sum(overall)}/{len(overall)})")
    return 0 if rate >= 0.85 else 1


def write_results(field_hits, failures, flag_notes, doc_count, tokens) -> None:
    lines = [
        "# BelegRadar extraction eval",
        "",
        f"Run: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')} · "
        f"{doc_count} sample invoices (German, Austrian, English; tricky cases "
        f"included: mixed VAT rates, discounts, credit note, Kleinunternehmer, "
        f"missing IBAN) · ~{tokens} LLM tokens total",
        "",
        "| Field | Accuracy |",
        "| --- | --- |",
    ]
    for field, hits in field_hits.items():
        lines.append(f"| {field} | {sum(hits)}/{len(hits)} |")
    overall = [h for hits in field_hits.values() for h in hits]
    lines += ["", f"**Overall: {sum(overall)}/{len(overall)} "
                  f"({sum(overall) / len(overall):.1%})**", ""]
    if failures:
        lines += ["## Misses (documented, not hidden)", "", *failures, ""]
    else:
        lines += ["No field misses in this run.", ""]
    if flag_notes:
        lines += ["## Validation errors raised on extracted data", "", *flag_notes, ""]
    out = Path(__file__).parent / "RESULTS.md"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"\nwrote {out}")


if __name__ == "__main__":
    raise SystemExit(run())
