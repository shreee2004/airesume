"""Extract plain text from an uploaded resume PDF.

v1 supports digital PDFs only - scanned/image PDFs return empty text and
trigger a 422 upstream. OCR is intentionally out of scope.
"""

from __future__ import annotations

import io
import re
import unicodedata

from pypdf import PdfReader


class PdfExtractionError(Exception):
    """Raised when the PDF cannot be parsed or contains no extractable text."""


# Map of common Unicode characters that PDFs often emit as garbled glyphs to
# safe ASCII replacements. We do this AFTER NFKC normalization so most of
# the obvious cases (smart quotes, fi/fl ligatures, etc.) are already handled.
_REPLACEMENTS = {
    "•": "- ",      # bullet
    "‣": "- ",
    "▪": "- ",
    "●": "- ",
    "⁃": "- ",
    "·": "- ",      # middle dot
    "–": "-",       # en dash
    "—": "-",       # em dash
    "‘": "'",
    "’": "'",
    "“": '"',
    "”": '"',
    " ": " ",       # non-breaking space
    "​": "",        # zero-width space
    "‌": "",
    "‍": "",
    "﻿": "",        # BOM
}


def _clean(text: str) -> str:
    # Canonical decomposition + recomposition handles most ligatures/diacritics.
    text = unicodedata.normalize("NFKC", text)
    for src, dst in _REPLACEMENTS.items():
        text = text.replace(src, dst)
    # Drop characters in Latin Extended-A/B that almost always indicate
    # decode errors in CV PDFs (e.g. Ă, Ĉ from miscoded bullets).
    text = re.sub(r"[Ā-ɏ]+", " ", text)
    # Collapse runs of 3+ spaces and 3+ blank lines.
    text = re.sub(r"[ \t]{2,}", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def extract_text(file_bytes: bytes) -> str:
    try:
        reader = PdfReader(io.BytesIO(file_bytes))
    except Exception as exc:
        raise PdfExtractionError(f"Could not parse PDF: {exc}") from exc

    pages: list[str] = []
    for page in reader.pages:
        try:
            pages.append(page.extract_text() or "")
        except Exception:
            pages.append("")

    raw = "\n\n".join(p.strip() for p in pages if p.strip())
    text = _clean(raw)
    if not text:
        raise PdfExtractionError(
            "No text could be extracted from this PDF. If it is a scanned "
            "document, please upload a digital (text-based) PDF."
        )
    return text
