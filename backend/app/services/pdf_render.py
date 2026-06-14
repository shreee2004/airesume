"""Render the tailored resume and cover letter to PDF.

Uses xhtml2pdf (pure Python, no system dependencies) so this works
out-of-the-box on Windows, macOS, and Linux without GTK/Pango/Cairo.
"""

from __future__ import annotations

import datetime as dt
import io
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape
from xhtml2pdf import pisa

from app.schemas import TailoredResume

TEMPLATE_DIR = Path(__file__).parent.parent / "prompts" / "templates"

_env = Environment(
    loader=FileSystemLoader(str(TEMPLATE_DIR)),
    autoescape=select_autoescape(["html", "xml"]),
)


class PdfRenderError(Exception):
    pass


def _html_to_pdf(html: str) -> bytes:
    out = io.BytesIO()
    result = pisa.CreatePDF(src=html, dest=out, encoding="utf-8")
    if result.err:
        raise PdfRenderError(f"xhtml2pdf reported {result.err} error(s)")
    return out.getvalue()


def render_resume_pdf(resume: TailoredResume) -> bytes:
    template = _env.get_template("resume.html")
    return _html_to_pdf(template.render(resume=resume))


def render_cover_pdf(
    cover_letter: str,
    candidate_name: str,
    contact: dict[str, str] | None = None,
    company_name: str | None = None,
    role_title: str | None = None,
) -> bytes:
    paragraphs = [p.strip() for p in cover_letter.split("\n\n") if p.strip()]
    template = _env.get_template("cover.html")
    return _html_to_pdf(
        template.render(
            candidate_name=candidate_name,
            contact=contact or {},
            company_name=company_name,
            role_title=role_title,
            today=dt.date.today().strftime("%B %d, %Y"),
            paragraphs=paragraphs,
        )
    )
