from __future__ import annotations

import logging
import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)

from app.routes import download, generate  # noqa: E402

app = FastAPI(title="AI Resume & Cover Letter Generator")

allowed_origins = [
    o.strip()
    for o in os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
    if o.strip()
]
# Optional regex (handy for Vercel preview URLs, e.g.
# r"^https://airesume-frontend-.*\.vercel\.app$").
allowed_origin_regex = os.getenv("CORS_ORIGIN_REGEX") or None

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_origin_regex=allowed_origin_regex,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def _check_api_key() -> None:
    if not os.environ.get("GROQ_API_KEY"):
        # Fail loud and early so the first request doesn't 500 mysteriously.
        raise RuntimeError(
            "GROQ_API_KEY is not set. Copy backend/.env.example to "
            "backend/.env and fill it in before starting the server. "
            "Get a free key at https://console.groq.com."
        )


@app.get("/api/health")
def health() -> dict[str, bool]:
    return {"ok": True}


app.include_router(generate.router)
app.include_router(download.router)
