"""LLM provider factory. Swap providers by changing LLM_PROVIDER in .env."""

from __future__ import annotations

from functools import lru_cache

from app.config import get_settings
from app.services.llm.base import LLMProvider

settings = get_settings()


@lru_cache
def get_llm_provider() -> LLMProvider:
    if settings.llm_provider == "openai":
        from app.services.llm.openai_provider import OpenAIProvider

        return OpenAIProvider()
    raise ValueError(
        f"Unknown LLM_PROVIDER '{settings.llm_provider}'. Only 'openai' is currently supported "
        "(other providers can be added behind the same LLMProvider interface)."
    )
