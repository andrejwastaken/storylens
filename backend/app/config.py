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

    # CORS
    cors_origins: str = "http://localhost:5173"

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
