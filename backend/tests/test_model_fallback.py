"""Backup models: when the main Gemini model is overloaded, the next one answers."""
import asyncio

import pytest
from google.genai import errors as genai_errors

from app.services import ai_client
from app.services.ai_client import AIUnavailableError, GeminiClient


class _Resp:
    text = "hello"
    candidates = []
    prompt_feedback = None
    parsed = None


class _Models:
    def __init__(self, busy):
        self.busy, self.asked = set(busy), []

    async def generate_content(self, model, contents, config):
        self.asked.append(model)
        if model in self.busy:
            raise genai_errors.ServerError(503, {"error": {"message": "high demand", "status": "UNAVAILABLE"}})
        return _Resp()


class _Fake:
    def __init__(self, busy):
        self.aio = type("A", (), {"models": _Models(busy)})()


def make(busy, monkeypatch, chain=("backup-a", "backup-b")):
    monkeypatch.setattr(ai_client.settings, "gemini_fallback_models", ",".join(chain))

    async def instant(attempt):
        return None
    monkeypatch.setattr(GeminiClient, "_sleep_backoff", staticmethod(instant))
    c = GeminiClient(api_key="x" * 12, model="main")
    c._client = _Fake(busy)
    return c


def test_busy_main_model_falls_back_to_the_next(monkeypatch):
    c = make({"main"}, monkeypatch)
    assert asyncio.run(c.generate_text("hi", system="s")) == "hello"
    assert c._client.aio.models.asked[-1] == "backup-a"


def test_every_model_busy_raises_unavailable(monkeypatch):
    c = make({"main", "backup-a", "backup-b"}, monkeypatch)
    with pytest.raises(AIUnavailableError):
        asyncio.run(c.generate_text("hi", system="s"))
    assert set(c._client.aio.models.asked) == {"main", "backup-a", "backup-b"}


def test_without_backups_only_the_main_model_is_used(monkeypatch):
    c = make({"main"}, monkeypatch, chain=())
    with pytest.raises(AIUnavailableError):
        asyncio.run(c.generate_text("hi", system="s"))
    assert set(c._client.aio.models.asked) == {"main"}
