"""Single gateway to Google Gemini.

Nothing else in Aspira talks to Gemini directly, so provider swaps (or the
planned in-house chatbot) only touch this file.

Features
* ``generate_text`` / ``generate_structured`` (schema-validated JSON) /
  ``stream_text`` (async token stream).
* Concurrency cap (semaphore) so a burst of users cannot exhaust the quota.
* Per-call timeout, exponential back-off with jitter on 429/5xx/timeouts.
* Small circuit breaker: after repeated hard failures calls fail fast for a
  cool-down instead of piling up.
* Safety-block and empty-response detection → typed exceptions the API layer
  can map to clean HTTP errors.
"""
from __future__ import annotations

import asyncio
import json
import logging
import random
import time
from typing import AsyncIterator, Sequence, TypeVar

from google import genai
from google.genai import errors as genai_errors
from google.genai import types
from pydantic import BaseModel, ValidationError

from app.config import settings

log = logging.getLogger("aspira.ai")
T = TypeVar("T", bound=BaseModel)


# ── Exceptions ─────────────────────────────────────────────────────────────
class AIError(Exception):
    """Base class for AI failures."""


class AIUnavailableError(AIError):
    """Provider down, rate-limited past retries, timed out, or circuit open."""


class AIBlockedError(AIError):
    """The provider's safety system refused to answer."""


class AIResponseError(AIError):
    """Provider answered but the output was empty or failed schema validation."""


# ── Circuit breaker ────────────────────────────────────────────────────────
class _CircuitBreaker:
    def __init__(self, threshold: int = 5, cooldown: float = 30.0) -> None:
        self.threshold, self.cooldown = threshold, cooldown
        self._failures = 0
        self._opened_at = 0.0

    def allow(self) -> bool:
        if self._failures < self.threshold:
            return True
        if time.monotonic() - self._opened_at >= self.cooldown:
            self._failures = self.threshold - 1  # half-open: allow one probe
            return True
        return False

    def success(self) -> None:
        self._failures = 0

    def failure(self) -> None:
        self._failures += 1
        if self._failures >= self.threshold:
            self._opened_at = time.monotonic()


_RETRYABLE_CODES = {408, 429, 500, 502, 503, 504}

_SAFETY = [
    types.SafetySetting(category=c, threshold="BLOCK_MEDIUM_AND_ABOVE")
    for c in (
        "HARM_CATEGORY_HARASSMENT",
        "HARM_CATEGORY_HATE_SPEECH",
        "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "HARM_CATEGORY_DANGEROUS_CONTENT",
    )
]


class GeminiClient:
    def __init__(self, api_key: str | None = None, model: str | None = None) -> None:
        self._client = genai.Client(api_key=api_key or settings.gemini_api_key.get_secret_value())
        self.model = model or settings.gemini_model
        self._sem = asyncio.Semaphore(settings.gemini_max_concurrency)
        self._breaker = _CircuitBreaker()

    # ── public API ─────────────────────────────────────────────────────────
    async def generate_text(self, prompt: str | Sequence[types.Content], *, system: str,
                            temperature: float = 0.6, max_tokens: int | None = None) -> str:
        cfg = self._config(system, temperature, max_tokens or settings.gemini_chat_max_output_tokens)
        resp = await self._call(lambda: self._client.aio.models.generate_content(
            model=self.model, contents=prompt, config=cfg))
        return self._extract_text(resp)

    async def generate_structured(self, prompt: str | Sequence[types.Content], *, system: str,
                                  schema: type[T], temperature: float = 0.7,
                                  max_tokens: int | None = None, repair_attempts: int = 1) -> T:
        cfg = self._config(system, temperature, max_tokens or settings.gemini_roadmap_max_output_tokens)
        cfg.response_mime_type = "application/json"
        cfg.response_schema = schema
        contents: str | Sequence[types.Content] = prompt
        last_err: Exception | None = None
        for attempt in range(repair_attempts + 1):
            resp = await self._call(lambda c=contents: self._client.aio.models.generate_content(
                model=self.model, contents=c, config=cfg))
            parsed = getattr(resp, "parsed", None)
            try:
                if isinstance(parsed, schema):
                    return parsed
                return schema.model_validate(json.loads(self._strip_fence(self._extract_text(resp))))
            except (ValidationError, json.JSONDecodeError) as exc:
                last_err = exc
                log.warning("structured output invalid (attempt %s): %s", attempt + 1, str(exc)[:300])
                if isinstance(prompt, str):
                    contents = (f"{prompt}\n\nYour previous reply was invalid JSON for the required schema "
                                f"({str(exc)[:300]}). Reply again with ONLY valid JSON.")
        raise AIResponseError(f"Model returned invalid structured output: {last_err}")

    async def stream_text(self, prompt: str | Sequence[types.Content], *, system: str,
                          temperature: float = 0.6, max_tokens: int | None = None) -> AsyncIterator[str]:
        """Yield text chunks. Retries only before the first chunk is emitted."""
        cfg = self._config(system, temperature, max_tokens or settings.gemini_chat_max_output_tokens)
        if not self._breaker.allow():
            raise AIUnavailableError("AI service is cooling down; try again shortly.")
        emitted = False
        for attempt in range(settings.gemini_max_retries + 1):
            try:
                async with self._sem:
                    stream = await asyncio.wait_for(
                        self._client.aio.models.generate_content_stream(
                            model=self.model, contents=prompt, config=cfg),
                        timeout=settings.gemini_timeout_seconds)
                    async for chunk in stream:
                        if chunk.candidates and chunk.candidates[0].finish_reason == "SAFETY":
                            raise AIBlockedError("Response blocked by safety filters.")
                        if chunk.text:
                            emitted = True
                            yield chunk.text
                self._breaker.success()
                return
            except AIBlockedError:
                raise
            except (genai_errors.APIError, asyncio.TimeoutError) as exc:
                if emitted or not self._is_retryable(exc) or attempt >= settings.gemini_max_retries:
                    self._breaker.failure()
                    raise AIUnavailableError(f"AI provider error: {exc}") from exc
                await self._sleep_backoff(attempt)

    # ── internals ──────────────────────────────────────────────────────────
    def _config(self, system: str, temperature: float, max_tokens: int) -> types.GenerateContentConfig:
        return types.GenerateContentConfig(
            system_instruction=system, temperature=temperature,
            max_output_tokens=max_tokens, safety_settings=_SAFETY)

    async def _call(self, factory):
        if not self._breaker.allow():
            raise AIUnavailableError("AI service is cooling down; try again shortly.")
        last: Exception | None = None
        for attempt in range(settings.gemini_max_retries + 1):
            try:
                async with self._sem:
                    resp = await asyncio.wait_for(factory(), timeout=settings.gemini_timeout_seconds)
                self._breaker.success()
                return resp
            except (genai_errors.APIError, asyncio.TimeoutError) as exc:
                last = exc
                if not self._is_retryable(exc) or attempt >= settings.gemini_max_retries:
                    break
                log.warning("Gemini retry %s after %s", attempt + 1, type(exc).__name__)
                await self._sleep_backoff(attempt)
        self._breaker.failure()
        raise AIUnavailableError(f"AI provider error: {last}") from last

    @staticmethod
    def _is_retryable(exc: Exception) -> bool:
        if isinstance(exc, asyncio.TimeoutError):
            return True
        return getattr(exc, "code", None) in _RETRYABLE_CODES

    @staticmethod
    async def _sleep_backoff(attempt: int) -> None:
        await asyncio.sleep(min(8.0, 0.8 * (2 ** attempt)) * (0.5 + random.random() / 2))

    @staticmethod
    def _extract_text(resp) -> str:
        fb = getattr(resp, "prompt_feedback", None)
        if fb is not None and getattr(fb, "block_reason", None):
            raise AIBlockedError(f"Prompt blocked: {fb.block_reason}")
        cands = getattr(resp, "candidates", None) or []
        if cands and str(cands[0].finish_reason).endswith("SAFETY"):
            raise AIBlockedError("Response blocked by safety filters.")
        text = (getattr(resp, "text", None) or "").strip()
        if not text:
            raise AIResponseError("Model returned an empty response.")
        return text

    @staticmethod
    def _strip_fence(text: str) -> str:
        if text.startswith("```"):
            text = text.split("\n", 1)[-1]
            text = text.rsplit("```", 1)[0]
        return text.strip()


_client: GeminiClient | None = None


def get_ai_client() -> GeminiClient:
    """Lazy singleton; also the FastAPI dependency (override it in tests)."""
    global _client
    if _client is None:
        _client = GeminiClient()
    return _client
