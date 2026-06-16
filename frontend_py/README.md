# Frontend (Python / Streamlit)

Pure-Python UI for the AI Resume & Cover Letter Generator. Replaces the
React/Vite TypeScript frontend. It calls the FastAPI backend over HTTP, so the
backend must be running first.

## Setup & run

```bash
# 1. Start the backend (separate terminal)
cd ../backend
source .venv/bin/activate
uvicorn app.main:app --reload        # -> http://localhost:8000

# 2. Start this Streamlit UI
cd ../frontend_py
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py                 # -> http://localhost:8501
```

## Config

- `BACKEND_URL` — base URL of the FastAPI backend. Defaults to
  `http://localhost:8000`.

  ```bash
  BACKEND_URL=https://your-backend.onrender.com streamlit run app.py
  ```

## Notes

- Only text-based PDF resumes are accepted (the uploader is restricted to
  `.pdf`; the backend additionally rejects scanned PDFs and non-resume
  documents such as certificates).
- The old React frontend still lives in `../frontend`. It is no longer needed
  if you use this Streamlit app — delete it when you're ready.
