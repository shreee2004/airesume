# Backend — AI Resume & Cover Letter Generator

FastAPI service that extracts text from an uploaded resume PDF, asks Claude to
produce a tailored resume + cover letter + ATS analysis, and renders the
downloadable PDFs with WeasyPrint.

## Setup

```bash
cd backend
python -m venv .venv
.\.venv\Scripts\activate         # Windows PowerShell
pip install -r requirements.txt
copy .env.example .env            # then edit .env to add your key
```

> PDF rendering uses `xhtml2pdf` (pure Python). No system libraries required.

## Run

```bash
uvicorn app.main:app --reload
# -> http://localhost:8000
```

## Endpoints

- `GET  /api/health` — liveness check.
- `POST /api/generate` — multipart: `resume_pdf`, `job_description`,
  `experience_level` (`fresher`|`experienced`), `industry`, `tone`
  (`professional`|`confident`|`formal`). Returns the full structured analysis.
- `POST /api/download/resume` — JSON `{ tailored_resume }`. Returns PDF.
- `POST /api/download/cover` — JSON `{ cover_letter, candidate_name, contact?,
  company_name?, role_title? }`. Returns PDF.

## Limitations

- v1 supports digital (text-based) PDFs only — scanned/image-only PDFs are
  rejected with HTTP 422. OCR is not in scope.
- No persistence; the backend is stateless.
- No auth or rate-limiting. Run on localhost or behind your own gateway.
