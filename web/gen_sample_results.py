"""Pre-compute extraction results for the sample gallery.

Sample invoices never change, so extracting them live wastes tokens on every
visitor. Run this once (needs GROQ_API_KEY) to bake the results into
public/samples/results.json; the frontend serves those instantly and only
real uploads hit the LLM.

    GROQ_API_KEY=... python gen_sample_results.py
"""

from __future__ import annotations

import importlib.util
import json
import os
import time
from pathlib import Path

HERE = Path(__file__).parent
SAMPLES = HERE / "public" / "samples"
OUT = SAMPLES / "results.json"

_spec = importlib.util.spec_from_file_location("extract_fn", HERE / "api" / "extract.py")
_fn = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_fn)


def _write(results: dict) -> None:
    OUT.write_text(json.dumps(results, ensure_ascii=False, indent=2) + "\n",
                   encoding="utf-8", newline="\n")


def main() -> int:
    if not os.environ.get("GROQ_API_KEY"):
        print("GROQ_API_KEY must be set")
        return 1

    # Resume: keep already-computed samples, only fill the gaps.
    results: dict[str, dict] = {}
    if OUT.exists():
        results = json.loads(OUT.read_text(encoding="utf-8"))

    for pdf in sorted(SAMPLES.glob("*.pdf")):
        if pdf.stem in results:
            print(f"  {pdf.stem}: cached, skip")
            continue
        body = None
        for attempt in range(5):
            status, body = _fn.run_extraction(pdf.read_bytes())
            if status == 200 and body.get("ok"):
                break
            wait = 30 * (attempt + 1)
            print(f"  {pdf.stem}: {status}, retry in {wait}s")
            time.sleep(wait)
        if not body or not body.get("ok"):
            print(f"  {pdf.stem}: gave up")
            _write(results)
            return 1
        results[pdf.stem] = body
        print(f"  {pdf.stem}: ok ({body['tokens']} tokens)")
        _write(results)  # persist after each success so a crash resumes
        time.sleep(12)   # pace within Groq free-tier per-minute budget

    total = sum(r["tokens"] for r in results.values())
    print(f"wrote {OUT} ({len(results)} samples, {total} tokens spent once)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
