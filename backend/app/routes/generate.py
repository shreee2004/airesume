from __future__ import annotations

import logging
from typing import Annotated

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from app.schemas import ExperienceLevel, GenerateResponse, Tone
from app.services.claude_client import generate_analysis
from app.services.pdf_extract import (
    NotAResumeError,
    PdfExtractionError,
    assert_is_resume,
    extract_text,
)

logger = logging.getLogger(__name__)
router = APIRouter()

MAX_RESUME_BYTES = 5 * 1024 * 1024  # 5 MB
MAX_JD_CHARS = 30_000


@router.post("/api/generate", response_model=GenerateResponse)
async def generate(
    resume_pdf: Annotated[UploadFile, File(description="Candidate resume as PDF")],
    job_description: Annotated[str, Form()],
    experience_level: Annotated[ExperienceLevel, Form()],
    industry: Annotated[str, Form()],
    tone: Annotated[Tone, Form()],
) -> GenerateResponse:
    if resume_pdf.content_type not in {"application/pdf", "application/x-pdf"}:
        raise HTTPException(415, "Resume must be a PDF file.")

    raw = await resume_pdf.read()
    if len(raw) > MAX_RESUME_BYTES:
        raise HTTPException(413, "Resume file is larger than 5 MB.")
    if not raw:
        raise HTTPException(400, "Resume file is empty.")

    job_description = job_description.strip()
    if not job_description:
        raise HTTPException(400, "Job description is required.")
    if len(job_description) > MAX_JD_CHARS:
        raise HTTPException(
            413, f"Job description exceeds {MAX_JD_CHARS} characters."
        )

    industry = industry.strip() or "General"

    try:
        resume_text = extract_text(raw)
    except PdfExtractionError as exc:
        raise HTTPException(422, str(exc)) from exc

    try:
        assert_is_resume(resume_text)
    except NotAResumeError as exc:
        raise HTTPException(422, str(exc)) from exc

    try:
        return generate_analysis(
            resume_text=resume_text,
            job_description=job_description,
            experience_level=experience_level,
            industry=industry,
            tone=tone,
        )
    except Exception as exc:
        logger.exception("Claude generation failed")
        raise HTTPException(502, f"Generation failed: {exc}") from exc
