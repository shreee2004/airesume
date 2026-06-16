"""Streamlit frontend for the AI Resume & Cover Letter Generator.

Pure-Python replacement for the React/Vite frontend. It talks to the same
FastAPI backend over HTTP:

  POST /api/generate         -> structured analysis (multipart upload)
  POST /api/download/resume  -> resume PDF
  POST /api/download/cover   -> cover letter PDF

Run:
  cd frontend_py
  pip install -r requirements.txt
  streamlit run app.py        # -> http://localhost:8501

Point it at the backend with the BACKEND_URL env var (default
http://localhost:8000).
"""

from __future__ import annotations

import os

import requests
import streamlit as st

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000").rstrip("/")

MAX_RESUME_BYTES = 5 * 1024 * 1024  # mirror backend limit

LEVELS = {"fresher": "Fresher", "experienced": "Experienced"}
TONES = {"professional": "Professional", "confident": "Confident", "formal": "Formal"}


# --------------------------------------------------------------------------- #
# Backend calls
# --------------------------------------------------------------------------- #
def _error_message(res: requests.Response) -> str:
    try:
        data = res.json()
        detail = data.get("detail")
        if isinstance(detail, str):
            return detail
        if detail is not None:
            return str(detail)
    except ValueError:
        pass
    return res.reason or f"HTTP {res.status_code}"


def generate(file_name, file_bytes, content_type, job_description, level, industry, tone):
    files = {"resume_pdf": (file_name, file_bytes, content_type or "application/pdf")}
    data = {
        "job_description": job_description,
        "experience_level": level,
        "industry": industry,
        "tone": tone,
    }
    res = requests.post(f"{BACKEND_URL}/api/generate", files=files, data=data, timeout=180)
    if not res.ok:
        raise RuntimeError(_error_message(res))
    return res.json()


def download_resume_pdf(tailored_resume) -> bytes:
    res = requests.post(
        f"{BACKEND_URL}/api/download/resume",
        json={"tailored_resume": tailored_resume},
        timeout=60,
    )
    if not res.ok:
        raise RuntimeError(_error_message(res))
    return res.content


def download_cover_pdf(cover_letter, candidate_name, contact) -> bytes:
    res = requests.post(
        f"{BACKEND_URL}/api/download/cover",
        json={
            "cover_letter": cover_letter,
            "candidate_name": candidate_name,
            "contact": contact,
        },
        timeout=60,
    )
    if not res.ok:
        raise RuntimeError(_error_message(res))
    return res.content


def _slug(name: str) -> str:
    safe = "".join(c if c.isalnum() or c in "._-" else "_" for c in (name or "document"))
    return safe.strip("_") or "document"


# --------------------------------------------------------------------------- #
# Result rendering
# --------------------------------------------------------------------------- #
def render_ats(ats):
    st.subheader("ATS analysis")
    c1, c2 = st.columns([1, 3])
    with c1:
        st.metric("ATS score", f"{ats['score']} / 100")
        st.metric("Keyword match", f"{ats['keyword_match_percent']}%")
    with c2:
        st.write(ats.get("explanation", ""))
        if ats.get("strength_areas"):
            st.markdown("**Strengths**")
            st.success(" · ".join(ats["strength_areas"]))
        if ats.get("weak_areas"):
            st.markdown("**Weak areas**")
            st.warning(" · ".join(ats["weak_areas"]))


def render_keywords(ats):
    st.subheader("Keyword analysis")
    c1, c2 = st.columns(2)
    with c1:
        matched = ats.get("matched_keywords", [])
        st.markdown(f"**Matched ({len(matched)})**")
        st.success(", ".join(matched) if matched else "None yet")
    with c2:
        missing = ats.get("missing_keywords", [])
        st.markdown(f"**Missing ({len(missing)})**")
        st.error(", ".join(missing) if missing else "All covered")


def render_resume(resume):
    st.subheader("Tailored resume")
    st.markdown(f"### {resume['candidate_name']}")
    contact_values = [v for v in resume.get("contact", {}).values() if v]
    if contact_values:
        st.caption(" • ".join(contact_values))

    if resume.get("professional_summary"):
        st.markdown("#### Professional Summary")
        st.write(resume["professional_summary"])

    if resume.get("technical_skills"):
        st.markdown("#### Technical Skills")
        st.write(", ".join(resume["technical_skills"]))

    if resume.get("experience"):
        st.markdown("#### Experience")
        for job in resume["experience"]:
            dates = ""
            if job.get("start_date") or job.get("end_date"):
                dates = f" ({job.get('start_date') or ''} – {job.get('end_date') or 'Present'})"
            st.markdown(f"**{job['role']} — {job['company']}**{dates}")
            if job.get("location"):
                st.caption(job["location"])
            for bullet in job.get("bullets", []):
                st.markdown(f"- {bullet}")

    if resume.get("projects"):
        st.markdown("#### Projects")
        for proj in resume["projects"]:
            tech = f" — _{', '.join(proj['tech'])}_" if proj.get("tech") else ""
            st.markdown(f"**{proj['name']}**{tech}")
            if proj.get("description"):
                st.caption(proj["description"])
            for bullet in proj.get("bullets", []):
                st.markdown(f"- {bullet}")

    if resume.get("education"):
        st.markdown("#### Education")
        for edu in resume["education"]:
            dates = " – ".join(d for d in [edu.get("start_date"), edu.get("end_date")] if d)
            dates = f" ({dates})" if dates else ""
            st.markdown(f"**{edu['degree']} — {edu['institution']}**{dates}")
            if edu.get("details"):
                st.caption(edu["details"])

    if resume.get("certifications"):
        st.markdown("#### Certifications")
        for cert in resume["certifications"]:
            st.markdown(f"- {cert}")

    if resume.get("achievements"):
        st.markdown("#### Achievements")
        for ach in resume["achievements"]:
            st.markdown(f"- {ach}")

    if resume.get("tools_technologies"):
        st.markdown("#### Tools & Technologies")
        st.write(", ".join(resume["tools_technologies"]))


def render_cover_letter(cover_letter):
    words = len(cover_letter.split())
    st.subheader("Cover letter")
    st.caption(f"{words} words")
    for para in [p.strip() for p in cover_letter.split("\n\n") if p.strip()]:
        st.write(para)


def render_suggestions(s):
    st.subheader("Skill-gap suggestions")
    sections = [
        ("Missing skills to build", s.get("missing_skills", [])),
        ("Recommended certifications", s.get("certifications", [])),
        ("Project ideas", s.get("project_ideas", [])),
        ("Interview prep topics", s.get("interview_topics", [])),
        ("Resume improvement tips", s.get("resume_tips", [])),
        ("Portfolio tips", s.get("portfolio_tips", [])),
        ("LinkedIn optimization tips", s.get("linkedin_tips", [])),
    ]
    for title, items in sections:
        if not items:
            continue
        with st.expander(f"{title} ({len(items)})"):
            for item in items:
                st.markdown(f"- {item}")


def render_downloads(result):
    st.subheader("Download")
    resume = result["tailored_resume"]
    name = resume["candidate_name"]
    c1, c2 = st.columns(2)

    with c1:
        try:
            resume_pdf = download_resume_pdf(resume)
            st.download_button(
                "Download resume PDF",
                data=resume_pdf,
                file_name=f"{_slug(name)}_resume.pdf",
                mime="application/pdf",
                use_container_width=True,
            )
        except Exception as exc:  # noqa: BLE001
            st.error(f"Resume PDF unavailable: {exc}")

    with c2:
        try:
            cover_pdf = download_cover_pdf(result["cover_letter"], name, resume.get("contact", {}))
            st.download_button(
                "Download cover letter PDF",
                data=cover_pdf,
                file_name=f"{_slug(name)}_cover_letter.pdf",
                mime="application/pdf",
                use_container_width=True,
            )
        except Exception as exc:  # noqa: BLE001
            st.error(f"Cover letter PDF unavailable: {exc}")


# --------------------------------------------------------------------------- #
# App
# --------------------------------------------------------------------------- #
def main():
    st.set_page_config(page_title="AI Resume & Cover Letter Generator", page_icon="📄")
    st.title("AI Resume & Cover Letter Generator")
    st.write(
        "Upload your resume, paste a job description, and get a tailored, "
        "ATS-optimized resume plus a personalized cover letter."
    )

    if "result" not in st.session_state:
        st.session_state.result = None

    # Results view --------------------------------------------------------- #
    if st.session_state.result:
        result = st.session_state.result
        top_l, top_r = st.columns([3, 1])
        with top_l:
            st.markdown(f"**Results for {result['tailored_resume']['candidate_name']}**")
        with top_r:
            if st.button("← Start over", use_container_width=True):
                st.session_state.result = None
                st.rerun()

        render_ats(result["ats"])
        st.divider()
        render_keywords(result["ats"])
        st.divider()
        render_resume(result["tailored_resume"])
        st.divider()
        render_cover_letter(result["cover_letter"])
        st.divider()
        render_suggestions(result["suggestions"])
        st.divider()
        render_downloads(result)
        return

    # Form view ------------------------------------------------------------ #
    with st.form("generate"):
        uploaded = st.file_uploader(
            "Resume PDF — digital (text-based) PDFs only, max 5 MB. "
            "Upload your resume/CV, not certificates or other documents.",
            type=["pdf"],
        )
        job_description = st.text_area(
            "Job description",
            height=240,
            placeholder="Paste the full posting — responsibilities, requirements, everything.",
        )
        col1, col2 = st.columns(2)
        with col1:
            level = st.radio(
                "Experience level",
                options=list(LEVELS.keys()),
                format_func=lambda k: LEVELS[k],
                index=1,
            )
        with col2:
            industry = st.text_input("Industry", value="Technology")
        tone = st.radio(
            "Tone",
            options=list(TONES.keys()),
            format_func=lambda k: TONES[k],
            horizontal=True,
        )
        submitted = st.form_submit_button("Generate tailored resume", type="primary")

    if not submitted:
        return

    # Client-side validation (mirrors the old React form) ------------------ #
    if uploaded is None:
        st.error("Please upload a resume PDF.")
        return
    file_bytes = uploaded.getvalue()
    if len(file_bytes) > MAX_RESUME_BYTES:
        st.error("Resume must be under 5 MB.")
        return
    if len(job_description.strip()) <= 30:
        st.error("Please paste a fuller job description (at least ~30 characters).")
        return
    if not industry.strip():
        st.error("Industry is required.")
        return

    with st.spinner("Analyzing resume and generating tailored content — this usually takes 20–40 seconds."):
        try:
            result = generate(
                uploaded.name,
                file_bytes,
                uploaded.type,
                job_description.strip(),
                level,
                industry.strip(),
                tone,
            )
        except Exception as exc:  # noqa: BLE001
            st.error(str(exc))
            return

    st.session_state.result = result
    st.rerun()


if __name__ == "__main__":
    main()
