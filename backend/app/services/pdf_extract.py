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


class NotAResumeError(Exception):
    """Raised when an uploaded PDF parses fine but does not look like a resume."""


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


# Section headers / phrases that are characteristic of a resume or CV. A genuine
# resume reliably hits several of these; certificates, offer letters, invoices,
# and other documents almost never do.
_RESUME_SIGNALS = (
    r"work experience",
    r"professional experience",
    r"employment history",
    r"\beducation\b",
    r"\bskills?\b",
    r"technical skills",
    r"work history",
    r"\bprojects?\b",
    r"certifications?",
    r"achievements?",
    r"\bsummary\b",
    r"objective",
    r"references?",
    r"curriculum vitae",
    r"\bresume\b",
    r"\bcv\b",
)

# Phrases that strongly indicate the document is a *certificate* rather than a
# resume. These short-circuit acceptance even if a stray resume keyword appears.
_CERTIFICATE_SIGNALS = (
    r"this is to certify",
    r"certificate of (completion|achievement|participation|appreciation|excellence)",
    r"has successfully completed",
    r"is hereby awarded",
    r"in recognition of",
)


def assert_is_resume(text: str) -> None:
    """Reject text that does not look like a resume.

    Heuristic, not perfect: we require at least two distinct resume-style
    section signals and bail out early if the document reads like a certificate.
    Raises :class:`NotAResumeError` when the check fails.
    """
    lowered = text.lower()

    for pattern in _CERTIFICATE_SIGNALS:
        if re.search(pattern, lowered):
            raise NotAResumeError(
                "This looks like a certificate, not a resume. Please upload "
                "your resume or CV."
            )

    matches = sum(1 for pattern in _RESUME_SIGNALS if re.search(pattern, lowered))
    if matches < 2:
        raise NotAResumeError(
            "This file does not look like a resume. Please upload your resume "
            "or CV (we can't accept certificates or other documents)."
        )
