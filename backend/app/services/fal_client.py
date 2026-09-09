"""fal.ai integration: a soft, heuristic "does this look AI-generated?"
signal for the article's lead/hero image.

Important honesty note: fal.ai does not offer a dedicated, purpose-built
AI-image-authenticity classifier (that's a narrower niche served by tools
like Sightengine/Hive). What it does offer is `fal-ai/any-llm/vision`, a
gateway to hosted vision-language models. We use that with a targeted
prompt to get a rough 0-100 likelihood estimate. This is explicitly a soft
LLM judgement, not a forensic detector - always surfaced in the UI as a
likelihood/signal, never a verdict, per project scope (no sophisticated
AI-image-detection system).

Docs: https://fal.ai/models/fal-ai/any-llm/vision
Get a free API key at https://fal.ai -> Dashboard -> Keys ($1 free credit).

Optional integration - purely additive. If FAL_API_KEY is unset, the caller should
treat this as unavailable rather than failing the whole analysis.
"""

from __future__ import annotations

import json
import logging

import httpx

from app.config import get_settings

logger = logging.getLogger("storylens.fal")
settings = get_settings()

FAL_BASE_URL = "https://fal.run"

SYSTEM_PROMPT = (
    "You are a cautious visual-forensics assistant. You never claim certainty. "
    "Reply with strict JSON only, no markdown fences, no extra text."
)

PROMPT_TEMPLATE = (
    "This is the lead image accompanying a news article. Estimate the likelihood "
    "(0-100) that this specific image was generated or heavily manipulated by AI, "
    "as opposed to being an authentic photograph. Consider signs like unnatural "
    "textures, inconsistent lighting/shadows, warped hands/text, or an overly "
    "'rendered' look. If the image looks like an ordinary photo, score it low. "
    'Respond with strict JSON: {"ai_likelihood": <integer 0-100>, "reasoning": '
    '"<one short sentence>"}'
)


class FalError(RuntimeError):
    pass


def is_configured() -> bool:
    return bool(settings.fal_api_key)


def assess_ai_image_likelihood(image_url: str) -> dict | None:
    """Returns {"ai_likelihood": float, "reasoning": str} or None on failure.

    Never raises for expected failure modes (missing key, bad response) -
    this is a nice-to-have signal, not core to the Trust Score.
    """
    if not settings.fal_api_key or not image_url:
        return None

    try:
        resp = httpx.post(
            f"{FAL_BASE_URL}/fal-ai/any-llm/vision",
            headers={
                "Authorization": f"Key {settings.fal_api_key}",
                "Content-Type": "application/json",
            },
            json={
                "prompt": PROMPT_TEMPLATE,
                "image_url": image_url,
                "model": settings.fal_vision_model,
                "system_prompt": SYSTEM_PROMPT,
            },
            timeout=30.0,
        )
        if resp.status_code >= 400:
            logger.warning("fal.ai returned %s: %s", resp.status_code, resp.text[:300])
            return None

        output = (resp.json() or {}).get("output", "")
        cleaned = output.strip().strip("`")
        if cleaned.lower().startswith("json"):
            cleaned = cleaned[4:].strip()

        parsed = json.loads(cleaned)
        likelihood = float(parsed.get("ai_likelihood", 0))
        reasoning = str(parsed.get("reasoning", "")).strip()
        return {"ai_likelihood": max(0.0, min(100.0, likelihood)), "reasoning": reasoning}
    except Exception as exc:  # noqa: BLE001 - best-effort signal, never fatal
        logger.warning("fal.ai AI-image assessment failed: %s", exc)
        return None
