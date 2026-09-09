"""ElevenLabs integration: text -> spoken audio for the Story Profile summary.

Docs: https://elevenlabs.io/docs/api-reference/text-to-speech/convert
Get a free API key at https://elevenlabs.io -> Profile -> API Keys
(free tier: ~10,000 characters/month, no card required).

Optional integration - purely additive. If ELEVENLABS_API_KEY is unset, the caller
should treat this as unavailable rather than failing the whole analysis.
"""

from __future__ import annotations

import httpx

from app.config import get_settings

settings = get_settings()

ELEVENLABS_BASE_URL = "https://api.elevenlabs.io"


class ElevenLabsError(RuntimeError):
    pass


def is_configured() -> bool:
    return bool(settings.elevenlabs_api_key)


def synthesize_speech(text: str) -> bytes:
    """Convert text to speech, returning raw MP3 bytes."""
    if not settings.elevenlabs_api_key:
        raise ElevenLabsError("ELEVENLABS_API_KEY is not configured.")

    # Keep it short - this is a ~30s audio summary, not a full narration.
    text = text.strip()[:1200]

    try:
        resp = httpx.post(
            f"{ELEVENLABS_BASE_URL}/v1/text-to-speech/{settings.elevenlabs_voice_id}",
            params={"output_format": "mp3_44100_128"},
            headers={
                "xi-api-key": settings.elevenlabs_api_key,
                "Content-Type": "application/json",
            },
            json={
                "text": text,
                "model_id": settings.elevenlabs_model_id,
                "voice_settings": {"stability": 0.5, "similarity_boost": 0.75},
            },
            timeout=30.0,
        )
    except httpx.HTTPError as exc:
        raise ElevenLabsError(f"ElevenLabs request failed: {exc}") from exc

    if resp.status_code >= 400:
        raise ElevenLabsError(f"ElevenLabs returned {resp.status_code}: {resp.text[:300]}")

    return resp.content
