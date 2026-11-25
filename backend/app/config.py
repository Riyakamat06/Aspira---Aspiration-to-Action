"""Central application settings for Aspira.

Every tunable value (secrets, database URL, Gemini options, the 50-user cap,
rate limits) is declared here once, typed, validated at start-up and read from
environment variables / a local ``.env`` file. Other modules never call
``os.getenv``; they import ``settings``.
"""
from __future__ import annotations

from functools import lru_cache
from typing import Annotated, Literal

from pydantic import Field, SecretStr, field_validator, model_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # ── Application ────────────────────────────────────────────────────────
    app_name: str = "Aspira – Aspiration to Action"
    app_version: str = "0.1.0"
    environment: Literal["development", "testing", "production"] = "development"
    debug: bool = False
    api_prefix: str = "/api/v1"
    cors_origins: Annotated[list[str], NoDecode] = ["http://localhost:3000", "http://localhost:5173"]

    # ── Database (SQLite for the two-week model; switch by changing the URL) ──
    database_url: str = "sqlite:///./aspira.db"

    # ── Auth ───────────────────────────────────────────────────────────────
    secret_key: SecretStr = Field(min_length=32)
    jwt_algorithm: Literal["HS256", "HS384", "HS512"] = "HS256"
    access_token_expire_minutes: int = Field(default=60, ge=5, le=60 * 24 * 7)
    max_users: int = Field(default=50, ge=1)  # beta cap; raise it to scale
    password_min_length: int = Field(default=8, ge=8, le=64)
    bcrypt_rounds: int = Field(default=12, ge=4, le=15)

    # ── Gemini ─────────────────────────────────────────────────────────────
    gemini_api_key: SecretStr = Field(min_length=10)
    gemini_model: str = "gemini-3.8-flash"
    # Comma-separated backup models, tried in order when the main one is overloaded (503/429) or missing (404).
    gemini_fallback_models: str = ""
    gemini_timeout_seconds: float = Field(default=45.0, gt=0)
    gemini_max_retries: int = Field(default=3, ge=0, le=6)
    gemini_max_concurrency: int = Field(default=8, ge=1, le=64)
    gemini_roadmap_max_output_tokens: int = Field(default=8192, ge=512)
    gemini_chat_max_output_tokens: int = Field(default=1024, ge=64)

    # ── Chatbot / roadmap behaviour ────────────────────────────────────────
    chat_history_char_budget: int = Field(default=12_000, ge=1_000)
    chat_message_max_chars: int = Field(default=1_500, ge=50)
    chat_rate_limit_per_minute: int = Field(default=15, ge=1)
    roadmap_rate_limit_per_hour: int = Field(default=10, ge=1)
    roadmap_dedupe_ttl_seconds: int = Field(default=300, ge=0)
    max_dreams_per_user: int = Field(default=5, ge=1)
    evidence_required: bool = True  # SRS FR-EV-01: tasks complete only via accepted evidence; the demo .env sets EVIDENCE_REQUIRED=false

    @field_validator("cors_origins", mode="before")
    @classmethod
    def _split_origins(cls, v):
        if isinstance(v, str):
            s = v.strip()
            if s.startswith("["):
                import json

                return json.loads(s)
            return [o.strip() for o in s.split(",") if o.strip()]
        return v

    @model_validator(mode="after")
    def _production_guards(self) -> "Settings":
        if self.environment == "production":
            if self.debug:
                raise ValueError("debug must be False in production")
            if "*" in self.cors_origins:
                raise ValueError("wildcard CORS is not allowed in production")
        return self

    @property
    def gemini_fallback_list(self) -> list[str]:
        """The backup models from GEMINI_FALLBACK_MODELS (blanks ignored)."""
        return [m.strip() for m in self.gemini_fallback_models.split(",") if m.strip()]

    @property
    def is_production(self) -> bool:
        return self.environment == "production"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]


settings = get_settings()
