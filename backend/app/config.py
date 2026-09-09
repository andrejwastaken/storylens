"""Central app configuration, loaded from environment variables / .env file.

Never commit real secrets. Copy backend/.env.example to backend/.env and fill in values.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Database
    database_url: str = "postgresql+psycopg://localhost:5432/storylens"

    # LLM provider (abstracted - see app/services/llm)
    llm_provider: str = "openai"
    openai_api_key: str = ""
    openai_model: str = "gpt-5.6"

    # Firecrawl (article extraction) - keyless tier works with low rate limits,
    # but a free API key from https://www.firecrawl.dev/app removes that limit.
    firecrawl_api_key: str = ""
    firecrawl_base_url: str = "https://api.firecrawl.dev"

    # Exa (related/corroborating source search) - https://dashboard.exa.ai/api-keys
    exa_api_key: str = ""
    exa_base_url: str = "https://api.exa.ai"

    # How many related sources to fetch full text for and compare against
    max_related_sources: int = 5

    # ElevenLabs (optional: spoken audio summary) - https://elevenlabs.io -> Profile -> API Keys
    elevenlabs_api_key: str = ""
    elevenlabs_voice_id: str = "JBFqnCBsd6RMkjVDRZzb"  # premade "George" voice, available on free tier
    elevenlabs_model_id: str = "eleven_turbo_v2_5"

    # fal.ai (optional: soft AI-generated-image heuristic on the article's lead image)
    # fal.ai has no dedicated authenticity-classifier model, so this uses a
    # hosted vision-language model (fal-ai/any-llm/vision) with a targeted
    # prompt. It is a soft heuristic signal, never a certainty claim.
    # https://fal.ai -> Dashboard -> Keys
    fal_api_key: str = ""
    fal_vision_model: str = "google/gemini-flash-1.5"

    # CORS
    cors_origins: str = "http://localhost:5173"

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def sqlalchemy_database_url(self) -> str:
        """Normalize managed-Postgres URLs (Render, etc. give plain
        postgres:// or postgresql://) to use the psycopg3 driver."""
        url = self.database_url
        if url.startswith("postgres://"):
            url = "postgresql+psycopg://" + url[len("postgres://") :]
        elif url.startswith("postgresql://"):
            url = "postgresql+psycopg://" + url[len("postgresql://") :]
        return url


@lru_cache
def get_settings() -> Settings:
    return Settings()
