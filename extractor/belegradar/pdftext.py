"""PDF text extraction. Text-layer PDFs only, by design.

Scanned or photographed invoices are politely rejected in the MVP: there is
no reliable free OCR at $0/month without infrastructure, and pretending to
support them would produce silently bad extractions, which is worse than a
clear message. OCR is a roadmap item.
"""

from __future__ import annotations

from io import BytesIO

from pypdf import PdfReader

MAX_PAGES = 10
MIN_TEXT_CHARS = 120  # below this a "PDF" is almost certainly a scan


class NoTextLayerError(ValueError):
    """The PDF carries no usable text layer (probably a scan or a photo)."""


class TooManyPagesError(ValueError):
    """Invoice PDFs are short; a long document is not an invoice."""


def extract_text(data: bytes) -> str:
    reader = PdfReader(BytesIO(data))
    if len(reader.pages) > MAX_PAGES:
        raise TooManyPagesError(
            f"{len(reader.pages)} pages; invoices are expected to have at most {MAX_PAGES}"
        )
    parts = [page.extract_text() or "" for page in reader.pages]
    text = "\n".join(parts).strip()
    if len(text) < MIN_TEXT_CHARS:
        raise NoTextLayerError(
            "No usable text layer found. Scanned or photographed invoices "
            "are not supported yet; please upload a digitally created PDF."
        )
    return text
