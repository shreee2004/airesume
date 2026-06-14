"""LLM client.

Talks to Groq via its OpenAI-compatible Chat Completions endpoint.

Reliability strategy: a small fallback chain of models. The first model in
LLM_MODELS is tried with JSON mode; if Groq rejects it (`json_validate_failed`)
we retry the same model without JSON mode; if that also fails we move to the
next model. This is robust against (a) a model being unavailable on a given
Groq account, (b) Groq's strict JSON validator over-rejecting some outputs,
and (c) a model not yet supporting `response_format`.
"""

from __future__ import annotations

import json
import logging
import os
import re

from openai import OpenAI, BadRequestError, NotFoundError

from app.prompts.system_prompt import SYSTEM_PROMPT
from app.schemas import GenerateResponse

logger = logging.getLogger(__name__)

BASE_URL = os.getenv("LLM_BASE_URL", "https://api.groq.com/openai/v1")
MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", "4000"))
TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.4"))

# Comma-separated list, tried left-to-right. Override via env to pin a model.
# Llama 3.3 70B is first because its TPM ceiling on Groq's free tier (~12k)
# is the only one that comfortably fits our prompt + output budget.
_DEFAULT_MODELS = "llama-3.3-70b-versatile,openai/gpt-oss-20b,llama-3.1-8b-instant"
MODELS: list[str] = [
    m.strip() for m in os.getenv("LLM_MODEL", _DEFAULT_MODELS).split(",") if m.strip()
]

_API_KEY_ENV = "GROQ_API_KEY"
_client: OpenAI | None = None


def get_client() -> OpenAI:
    global _client
    if _client is None:
        api_key = os.environ.get(_API_KEY_ENV)
        if not api_key:
            raise RuntimeError(
                f"{_API_KEY_ENV} is not set. Copy backend/.env.example to "
                "backend/.env and fill it in (get a free key at "
                "https://console.groq.com)."
            )
        _client = OpenAI(api_key=api_key, base_url=BASE_URL)
    return _client


def _build_user_message(
    resume_text: str,
    job_description: str,
    experience_level: str,
    industry: str,
    tone: str,
) -> str:
    return (
        f"<resume_text>\n{resume_text.strip()}\n</resume_text>\n\n"
        f"<job_description>\n{job_description.strip()}\n</job_description>\n\n"
        f"<experience_level>{experience_level}</experience_level>\n"
        f"<industry>{industry.strip()}</industry>\n"
        f"<tone>{tone}</tone>\n\n"
        "Return ONLY the JSON object described in the system message. "
        "No prose, no markdown fences. Begin with `{` and end with `}`."
    )


_FENCE_RE = re.compile(r"^```(?:json)?\s*|\s*```$", re.IGNORECASE)


def _extract_json(text: str) -> str:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = _FENCE_RE.sub("", cleaned).strip()
    if not cleaned.startswith("{"):
        first = cleaned.find("{")
        last = cleaned.rfind("}")
        if first != -1 and last != -1 and last > first:
            cleaned = cleaned[first : last + 1]
    return cleaned


def _call_one(
    client: OpenAI, model: str, system: str, user: str, json_mode: bool
) -> tuple[str, str | None]:
    """Make one API call. Returns (raw_text, finish_reason). Raises on API error."""
    kwargs: dict[str, object] = dict(
        model=model,
        max_tokens=MAX_TOKENS,
        temperature=TEMPERATURE,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    )
    if json_mode:
        kwargs["response_format"] = {"type": "json_object"}

    completion = client.chat.completions.create(**kwargs)
    usage = getattr(completion, "usage", None)
    if usage is not None:
        logger.info(
            "[%s json=%s] prompt=%s completion=%s",
            model,
            json_mode,
            getattr(usage, "prompt_tokens", None),
            getattr(usage, "completion_tokens", None),
        )
    choice = completion.choices[0]
    return choice.message.content or "", choice.finish_reason


def generate_analysis(
    resume_text: str,
    job_description: str,
    experience_level: str,
    industry: str,
    tone: str,
) -> GenerateResponse:
    client = get_client()
    user_msg = _build_user_message(
        resume_text, job_description, experience_level, industry, tone
    )

    attempts: list[str] = []
    for model in MODELS:
        for json_mode in (True, False):
            label = f"{model} (json={json_mode})"
            try:
                raw, finish_reason = _call_one(
                    client, model, SYSTEM_PROMPT, user_msg, json_mode
                )
            except NotFoundError as exc:
                attempts.append(f"{label}: model not available ({exc.message})")
                break  # try next model entirely
            except BadRequestError as exc:
                # e.g. json_validate_failed — try the same model without JSON
                # mode, or skip if we already did.
                attempts.append(f"{label}: {exc.message}")
                if not json_mode:
                    break
                continue
            except Exception as exc:
                attempts.append(f"{label}: {type(exc).__name__}: {exc}")
                if not json_mode:
                    break
                continue

            cleaned = _extract_json(raw)
            if not cleaned:
                attempts.append(
                    f"{label}: empty output (finish_reason={finish_reason})"
                )
                continue
            try:
                payload = json.loads(cleaned)
            except json.JSONDecodeError as exc:
                snippet = raw[:200].replace("\n", " ")
                attempts.append(f"{label}: invalid JSON ({exc}); starts: {snippet}")
                continue
            try:
                return GenerateResponse.model_validate(payload)
            except Exception as exc:
                attempts.append(f"{label}: schema mismatch ({exc})")
                continue

    raise RuntimeError(
        "All LLM attempts failed. Tried:\n  - " + "\n  - ".join(attempts)
    )
