from __future__ import annotations

import re

from fastapi import APIRouter, HTTPException
from fastapi.responses import Response

from app.schemas import DownloadCoverRequest, DownloadResumeRequest
from app.services.pdf_render import render_cover_pdf, render_resume_pdf

router = APIRouter()


def _safe_filename(name: str, suffix: str) -> str:
    base = re.sub(r"[^A-Za-z0-9._-]+", "_", name).strip("_") or "document"
    return f"{base}_{suffix}.pdf"


@router.post("/api/download/resume")
def download_resume(req: DownloadResumeRequest) -> Response:
    try:
        pdf_bytes = render_resume_pdf(req.tailored_resume)
    except Exception as exc:
        raise HTTPException(500, f"Failed to render resume PDF: {exc}") from exc

    filename = _safe_filename(req.tailored_resume.candidate_name, "resume")
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.post("/api/download/cover")
def download_cover(req: DownloadCoverRequest) -> Response:
    if not req.cover_letter.strip():
        raise HTTPException(400, "Cover letter text is empty.")
    try:
        pdf_bytes = render_cover_pdf(
            cover_letter=req.cover_letter,
            candidate_name=req.candidate_name,
            contact=req.contact,
            company_name=req.company_name,
            role_title=req.role_title,
        )
    except Exception as exc:
        raise HTTPException(500, f"Failed to render cover letter PDF: {exc}") from exc

    filename = _safe_filename(req.candidate_name, "cover_letter")
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
