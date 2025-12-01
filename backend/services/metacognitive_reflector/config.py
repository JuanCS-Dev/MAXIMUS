"""
Metacognitive Reflector - Configuration
=======================================

Pydantic-based configuration for the Metacognitive Reflector service.
"""
# pylint: disable=too-few-public-methods

from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


def create_service_settings() -> "ServiceSettings":
    """Factory for ServiceSettings."""
    return ServiceSettings(
        name="metacognitive-reflector",
        log_level="INFO"
    )


def create_llm_settings() -> "LLMSettings":
    """Factory for LLMSettings."""
    return LLMSettings(
        api_key="dummy_key", # Default for tests
        model="gemini-2.0-pro-exp",
        temperature=0.7,
        max_tokens=8192
    )


class ServiceSettings(BaseSettings):
    """
    General service settings.
    """
    name: str = Field(
        default="metacognitive-reflector",
        validation_alias="SERVICE_NAME"
    )
    log_level: str = Field(
        default="INFO",
        validation_alias="LOG_LEVEL"
    )

    model_config = SettingsConfigDict(env_file=".env", populate_by_name=True, extra="ignore")


class LLMSettings(BaseSettings):
    """
    LLM configuration settings.
    """
    api_key: str = Field(..., validation_alias="GEMINI_API_KEY")
    model: str = Field(
        default="gemini-2.0-pro-exp",
        validation_alias="LLM_MODEL"
    )
    temperature: float = Field(
        default=0.7,
        validation_alias="LLM_TEMPERATURE"
    )
    max_tokens: int = Field(
        default=8192,
        validation_alias="LLM_MAX_TOKENS"
    )

    model_config = SettingsConfigDict(env_file=".env", populate_by_name=True, extra="ignore")


class Settings(BaseSettings):
    """
    Global application settings.
    """
    service: ServiceSettings = Field(default_factory=create_service_settings)
    llm: LLMSettings = Field(default_factory=create_llm_settings)

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.
    """
    return Settings()
