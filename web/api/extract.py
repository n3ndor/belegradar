"""Vercel Python serverless function: PDF bytes in, validated invoice out.

The extraction engine is the published `belegradar` package (installed via
requirements.txt), the same code proven by the repo's eval suite. This file
is only the HTTP wrapper plus abuse guards.

Privacy: nothing is stored. We read the request body, extract, and respond.
Only sizes, timings, and token counts would ever be logged, never document
content.
"""

from __future__ import annotations

import json
import os
from http.server import BaseHTTPRequestHandler

from belegradar import (
    NoTextLayerError,
    TooManyPagesError,
    extract_invoice,
    extract_text,
    validate,
)
from belegradar.providers import ProviderError

MAX_BYTES = 4 * 1024 * 1024  # 4 MB
PDF_MAGIC = b"%PDF"


def run_extraction(pdf_bytes: bytes) -> tuple[int, dict]:
    """Pure core: returns (http_status, json_body). No I/O beyond the LLM call."""
    if not pdf_bytes:
        return 400, _err("Empty request body.", "empty")
    if len(pdf_bytes) > MAX_BYTES:
        return 413, _err("File too large (max 4 MB).", "too_large")
    if not pdf_bytes.lstrip()[:4] == PDF_MAGIC:
        return 400, _err("That does not look like a PDF file.", "not_pdf")

    try:
        text = extract_text(pdf_bytes)
    except NoTextLayerError as exc:
        return 422, _err(str(exc), "no_text")
    except TooManyPagesError as exc:
        return 422, _err(str(exc), "too_many_pages")
    except Exception:  # noqa: BLE001
        return 400, _err("Could not read this PDF.", "bad_pdf")

    if not os.environ.get("GROQ_API_KEY"):
        return 503, _err("Extraction service is not configured.", "no_key")

    try:
        invoice, tokens = extract_invoice(text)
    except ProviderError:
        return 503, _err(
            "The extraction model is busy right now (free-tier limit). "
            "Please try again in a moment.",
            "llm_busy",
        )
    except Exception:  # noqa: BLE001
        return 502, _err("Extraction failed on this document.", "extract_failed")

    report = validate(invoice)
    return 200, {
        "ok": True,
        "extraction": invoice.model_dump(mode="json"),
        "validation": {
            "ok": report.ok,
            "flags": [f.model_dump() for f in report.flags],
            "pflichtangaben": report.pflichtangaben,
        },
        "raw_text": text,
        "tokens": tokens,
    }


def _err(message: str, kind: str) -> dict:
    return {"ok": False, "error": message, "kind": kind}


class handler(BaseHTTPRequestHandler):
    def do_POST(self):  # noqa: N802 - Vercel/BaseHTTPRequestHandler contract
        try:
            length = int(self.headers.get("Content-Length") or 0)
        except ValueError:
            length = 0
        if length > MAX_BYTES:
            self._send(413, _err("File too large (max 4 MB).", "too_large"))
            return
        body = self.rfile.read(length) if length else b""
        status, payload = run_extraction(body)
        self._send(status, payload)

    def _send(self, status: int, payload: dict) -> None:
        data = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)
