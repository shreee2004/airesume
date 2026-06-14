# AI Resume & Cover Letter Generator

A two-part web app:

- **`backend/`** — FastAPI service that extracts text from an uploaded resume
  PDF, calls an LLM (Groq's free Llama 3.3 70B by default, via its
  OpenAI-compatible API with forced tool calling) to produce a tailored
  resume, cover letter, ATS score, and skill-gap analysis, and renders
  downloadable PDFs with `xhtml2pdf` (pure Python, Windows-friendly).
- **`frontend/`** — React + Vite + TypeScript UI for uploading the resume,
  pasting a job description, viewing results, and downloading the PDFs.

## Prerequisites

- Python 3.10+
- Node.js 18+ (and npm) for the frontend. Download from <https://nodejs.org>
  if `node --version` does not work in your shell.

## Quick start

### 1. Backend

```powershell
cd "D:\AI Resume & Cover Letter Generator\backend"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env          # then edit .env to add GROQ_API_KEY
uvicorn app.main:app --reload
```

PDF rendering uses `xhtml2pdf` (pure Python) — no system libraries needed.

Verify: <http://localhost:8000/api/health> → `{"ok": true}`.

### 2. Frontend

```powershell
cd "D:\AI Resume & Cover Letter Generator\frontend"
npm install
npm run dev
```

Open <http://localhost:5173>. The Vite dev server proxies `/api/*` to the
FastAPI backend on `:8000`, so CORS is a non-issue locally.

### Convenience script

From the project root: `.\start-dev.ps1` opens two PowerShell windows and
boots both halves (creates the venv and installs deps on first run).

## How it works

1. User uploads a PDF resume, pastes a job description, picks experience
   level / industry / tone.
2. The backend extracts text from the PDF with `pypdf`.
3. The backend calls Groq (OpenAI-compatible API) with a large system prompt
   and forces a single `submit_analysis` tool call whose JSON Schema is
   derived from the Pydantic response model (one source of truth).
4. The structured JSON comes back to the React UI, which renders an ATS score
   ring, matched/missing keywords, the tailored resume preview, the cover
   letter, and a stack of skill-gap accordions.
5. Download buttons POST the relevant slice back to the backend, which renders
   it to PDF with `xhtml2pdf` and streams the file as a download.

## Project layout

```
backend/
  app/
    main.py                 FastAPI app + CORS + health
    schemas.py              Pydantic models (single source of truth)
    routes/
      generate.py           POST /api/generate
      download.py           POST /api/download/{resume,cover}
    services/
      claude_client.py      OpenAI SDK pointed at Groq (forced tool call)
      pdf_extract.py        pypdf text extraction
      pdf_render.py         xhtml2pdf HTML → PDF (pure Python)
    prompts/
      system_prompt.py      The strategist prompt
      templates/
        resume.html         ATS-friendly resume PDF template
        cover.html          Cover letter PDF template
  requirements.txt
  .env.example

frontend/
  src/
    main.tsx, App.tsx
    api.ts                  typed fetch wrapper
    types.ts                mirrors schemas.py
    styles.css
    components/
      ResumeForm.tsx
      ResultsView.tsx
      AtsScorePanel.tsx
      KeywordsPanel.tsx
      ResumePreview.tsx
      CoverLetterPreview.tsx
      SuggestionsPanel.tsx
      DownloadButtons.tsx
  index.html, vite.config.ts, package.json, tsconfig.json
```

## Limitations (v1)

- **Digital PDFs only.** Scanned/image-only PDFs are rejected with a clear
  error; OCR is intentionally out of scope.
- **No persistence, no auth, no rate limiting.** Run on localhost or behind
  your own gateway — anyone who can hit `/api/generate` can consume your
  Groq free-tier quota.
- **Synchronous generation.** A request takes 20–40 s; the UI shows a spinner.
  Streaming is a future enhancement.
- **Truthfulness is enforced via the prompt, not the code.** The prompt
  explicitly forbids inventing companies, roles, degrees, or skills. Spot-check
  the tailored resume against your source before sending it out.

## Verification checklist

1. `GET /api/health` returns `{"ok": true}`.
2. The frontend loads at <http://localhost:5173>.
3. Upload a real PDF resume + a real JD, click Generate. Within ~40 s the
   results view shows ATS score, keywords, resume, cover letter, and
   suggestions.
4. Both download buttons produce a clean PDF.
5. Backend logs show `llm usage: prompt=... completion=... total=...` on
   each request.
```
