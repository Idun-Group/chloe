"""
Configuration management for Chloé API
"""

from enum import StrEnum
from pydantic_settings import BaseSettings
from functools import lru_cache


class LLMProvider(StrEnum):
    """Supported LLM providers"""

    OPENAI = "openai"
    GEMINI = "gemini"


class Settings(BaseSettings):
    """Application settings with environment variable support"""

    # API Configuration
    api_key: str = ""
    api_version: str = "1.0.4"

    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = True

    # CORS Configuration
    cors_origins: list[str] = ["*"]
    cors_credentials: bool = True
    cors_methods: list[str] = ["*"]
    cors_headers: list[str] = ["*"]

    cloud_tracing: bool = False

    # Langfuse Configuration
    langfuse_public_key: str = ""
    langfuse_secret_key: str = ""
    langfuse_host: str = ""

    # Langgraph Agent Configuration
    postgresql_uri: str
    postgresql_pool_min_size: int = 2
    postgresql_pool_max_size: int = 10

    # API Tokens & Keys
    apify_api_token: str = ""
    tavily_api_key: str = ""
    fullenrich_api_key: str = ""

    # LLM Provider Configuration
    llm_provider: LLMProvider = LLMProvider.GEMINI
    llm_model_name: str = "gemini-2.0-flash"
    llm_temperature: float = 0.0
    openai_api_key: str = ""
    gemini_api_key: str = ""

    # Company Configuration
    company_name: str = "Company Name"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()
