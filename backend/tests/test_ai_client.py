"""
test_ai_client.py - independent tests for Riya's Gemini gateway (ai_client.py).

PURPOSE
    ai_client.py is the only door through which Aspira talks to Gemini. It adds
    safety around every call: retries for temporary errors, a circuit breaker
    that stops calls after repeated failures, and clear errors for blocked or
    empty answers. These tests check those rules from the outside. A FAKE
    Gemini is used in every test, so no network call is made and no money is
    spent.

WHAT IS TESTED
    1. Circuit breaker: opens after 5 failures, resets on success, lets one
       trial call through after the cool-down time.
    2. Which errors are retried: 408, 429 and timeouts yes; 400 and 404 no.
    3. Cleaning of text wrapped in ``` code fences.
    4. Reading an answer: normal text, empty text, blocked prompt, safety stop.
    5. generate_text: success, retry then success, no retry for a bad request,
       retries run out, blocked answers are not retried, empty answers fail,
       the breaker opens after 5 failed calls.
    6. generate_structured: ready object, JSON text inside code fences,
       invalid JSON twice gives an error (and the second try asks for valid JSON).
    7. stream_text: pieces arrive in order, a safety stop raises an error,
       an open breaker stops the call before Gemini is asked.
    8. get_ai_client returns the same client every time.

SETTINGS
    A fixture switches off the backup Gemini models (GEMINI_FALLBACK_MODELS), so
    the call counts below are the same on every machine, whatever is in .env.

NOTE ON PRIVATE NAMES
    Some tests touch names that start with an underscore (_client, _breaker,
    _CircuitBreaker). That is on purpose: the fake Gemini must be placed
    inside the client, and the breaker rules can only be checked directly.

HOW TO RUN
    cd backend
    pytest tests/test_ai_client.py -v

WHO USES IT
    Sonali (M4 testing), reviewed by Riya (owner of ai_client.py).
"""

import os  # to set dummy settings before the app loads

# dummy settings so the app can load in tests; never put a real key here
os.environ.setdefault("SECRET_KEY", "test-secret-key-for-tests-only-0000")  # fake secret
os.environ.setdefault("GEMINI_API_KEY", "fake-key-not-real")                # fake AI key

import asyncio                          # for the timeout error type
from types import SimpleNamespace       # makes quick fake objects with named fields

import pytest                           # the test tool
from google.genai import errors as genai_errors  # the real Gemini error base class
from pydantic import BaseModel          # to build a small schema for structured answers

from app.config import settings         # the real settings (retry count, etc.)
from app.services.ai_client import (    # the things we test
    AIBlockedError,       # safety system refused
    AIResponseError,      # empty or invalid answer
    AIUnavailableError,   # provider down, retries used up, or breaker open
    GeminiClient,         # the gateway class
    _CircuitBreaker,      # the breaker (private, tested directly)
    get_ai_client,        # returns the one shared client
)


@pytest.fixture
def anyio_backend():
    # tells the async test tool (anyio) to use Python's standard asyncio
    return "asyncio"


@pytest.fixture(autouse=True)
def no_waiting(monkeypatch):
    # the real client waits between retries; tests must not wait, so replace the wait with nothing
    async def instant(attempt):
        return None
    monkeypatch.setattr(GeminiClient, "_sleep_backoff", staticmethod(instant))


@pytest.fixture(autouse=True)
def no_backup_models(monkeypatch):
    # a developer's .env may list backup Gemini models (GEMINI_FALLBACK_MODELS);
    # the call counts in these tests assume there are none, so switch them off here
    monkeypatch.setattr(settings, "gemini_fallback_models", "")


class FakeAPIError(genai_errors.APIError):
    """A Gemini error with the status code we choose."""

    def __init__(self, code):
        Exception.__init__(self, f"fake error {code}")  # set the message without Gemini's own setup
        self.code = code                                 # the field the client reads

    def __str__(self):
        return f"fake error {self.code}"                 # readable text for the error message


class Reply(BaseModel):
    """A tiny schema used for structured answers."""
    answer: str


def ok(text):
    # a fake Gemini answer that contains the given text
    return SimpleNamespace(text=text, parsed=None, candidates=[], prompt_feedback=None)


class FakeModels:
    """Plays the part of client.aio.models. Returns or raises what we queue."""

    def __init__(self, items=None, chunks=None):
        self.items = list(items or [])      # answers or errors to give, in order (the last one repeats)
        self.chunks = list(chunks or [])    # pieces for streaming
        self.calls = 0                      # how many times generate_content was asked
        self.stream_calls = 0               # how many times a stream was asked
        self.kwargs_list = []               # what each call was sent

    async def generate_content(self, **kwargs):
        self.calls += 1                                  # count the call
        self.kwargs_list.append(kwargs)                  # remember what was sent
        item = self.items.pop(0) if len(self.items) > 1 else self.items[0]  # next item; keep the last one
        if isinstance(item, Exception):                  # an error item is raised
            raise item
        return item                                      # an answer item is returned

    async def generate_content_stream(self, **kwargs):
        self.stream_calls += 1                           # count the stream request
        chunks = self.chunks                             # the pieces to give

        async def pieces():
            for chunk in chunks:                         # give the pieces one by one
                yield chunk
        return pieces()                                  # the client awaits this, then loops over it


def make_client(items=None, chunks=None):
    client = GeminiClient(api_key="fake-key-not-real")   # a real client object with a fake key
    models = FakeModels(items, chunks)                   # the fake Gemini
    client._client = SimpleNamespace(aio=SimpleNamespace(models=models))  # put the fake inside
    return client, models


# ---------- circuit breaker ----------

def test_breaker_allows_calls_below_threshold():
    breaker = _CircuitBreaker(threshold=3, cooldown=30.0)  # opens after 3 failures
    breaker.failure()                                      # failure 1
    breaker.failure()                                      # failure 2
    assert breaker.allow() is True                         # still below 3, so calls are allowed


def test_breaker_opens_after_threshold_failures():
    breaker = _CircuitBreaker(threshold=2, cooldown=30.0)  # opens after 2 failures
    breaker.failure()
    breaker.failure()
    assert breaker.allow() is False                        # open: calls are refused


def test_breaker_success_resets_failures():
    breaker = _CircuitBreaker(threshold=2, cooldown=30.0)
    breaker.failure()                                      # one failure
    breaker.success()                                      # a success clears the count
    breaker.failure()                                      # one new failure
    assert breaker.allow() is True                         # only 1 failure counted, so still allowed


def test_breaker_allows_one_trial_after_cooldown():
    breaker = _CircuitBreaker(threshold=2, cooldown=30.0)
    breaker.failure()
    breaker.failure()                                      # now open
    assert breaker.allow() is False                        # refused during the cool-down
    breaker._opened_at -= 31.0                             # pretend 31 seconds have passed
    assert breaker.allow() is True                         # one trial call is allowed again


# ---------- which errors are retried ----------

@pytest.mark.parametrize("code, retried", [  # the same test runs once for each pair
    (408, True), (429, True), (503, True),    # temporary problems: retry
    (400, False), (404, False),               # our own mistake: do not retry
])
def test_error_codes_are_retried_or_not(code, retried):
    assert GeminiClient._is_retryable(FakeAPIError(code)) is retried


def test_timeout_is_retried():
    assert GeminiClient._is_retryable(asyncio.TimeoutError()) is True  # a timeout is temporary


# ---------- cleaning code fences ----------

def test_code_fence_is_removed():
    text = '```json\n{"answer": "hi"}\n```'                 # JSON wrapped in a fence
    assert GeminiClient._strip_fence(text) == '{"answer": "hi"}'  # only the JSON remains


def test_text_without_fence_is_unchanged():
    assert GeminiClient._strip_fence('  {"a": 1}  ') == '{"a": 1}'  # only spaces are trimmed


# ---------- reading an answer ----------

def test_extract_text_returns_trimmed_text():
    assert GeminiClient._extract_text(ok("  hello  ")) == "hello"  # spaces trimmed


@pytest.mark.parametrize("empty", ["", "   "])  # nothing, and only spaces
def test_empty_answer_raises_response_error(empty):
    with pytest.raises(AIResponseError):
        GeminiClient._extract_text(ok(empty))


def test_blocked_prompt_raises_blocked_error():
    resp = SimpleNamespace(text="", parsed=None, candidates=[],
                           prompt_feedback=SimpleNamespace(block_reason="SAFETY"))  # prompt was refused
    with pytest.raises(AIBlockedError):
        GeminiClient._extract_text(resp)


def test_safety_stop_raises_blocked_error():
    resp = SimpleNamespace(text="partial", parsed=None, prompt_feedback=None,
                           candidates=[SimpleNamespace(finish_reason="SAFETY")])  # answer stopped by safety
    with pytest.raises(AIBlockedError):
        GeminiClient._extract_text(resp)


# ---------- generate_text ----------

@pytest.mark.anyio
async def test_generate_text_returns_the_answer():
    client, models = make_client([ok("Start with SQL.")])
    result = await client.generate_text("How do I start?", system="Be brief.")
    assert result == "Start with SQL."          # the text comes back
    assert models.calls == 1                    # one call was enough


@pytest.mark.anyio
async def test_temporary_error_is_retried_then_succeeds():
    if settings.gemini_max_retries < 1:         # this test needs at least one retry
        pytest.skip("gemini_max_retries is 0")
    client, models = make_client([FakeAPIError(503), ok("Fine.")])  # fail once, then work
    result = await client.generate_text("Hi", system="s")
    assert result == "Fine."                    # the second try worked
    assert models.calls == 2                    # exactly one retry


@pytest.mark.anyio
async def test_bad_request_is_not_retried():
    client, models = make_client([FakeAPIError(400)])  # our own mistake
    with pytest.raises(AIUnavailableError):
        await client.generate_text("Hi", system="s")
    assert models.calls == 1                    # no retry


@pytest.mark.anyio
async def test_retries_run_out_and_raise_unavailable():
    client, models = make_client([FakeAPIError(503)])  # fails every time
    with pytest.raises(AIUnavailableError):
        await client.generate_text("Hi", system="s")
    assert models.calls == settings.gemini_max_retries + 1  # the first try plus every retry


@pytest.mark.anyio
async def test_blocked_answer_is_not_retried():
    blocked = SimpleNamespace(text="", parsed=None, candidates=[],
                              prompt_feedback=SimpleNamespace(block_reason="SAFETY"))
    client, models = make_client([blocked])
    with pytest.raises(AIBlockedError):
        await client.generate_text("Hi", system="s")
    assert models.calls == 1                    # asking again would not help


@pytest.mark.anyio
async def test_empty_answer_raises_response_error():
    client, _ = make_client([ok("")])
    with pytest.raises(AIResponseError):
        await client.generate_text("Hi", system="s")


@pytest.mark.anyio
async def test_breaker_opens_after_five_failed_calls_and_stops_asking_gemini():
    client, models = make_client([FakeAPIError(400)])  # every call fails
    for _ in range(5):                                 # five failed calls
        with pytest.raises(AIUnavailableError):
            await client.generate_text("Hi", system="s")
    assert models.calls == 5                           # Gemini was asked five times
    with pytest.raises(AIUnavailableError):            # the sixth call is refused
        await client.generate_text("Hi", system="s")
    assert models.calls == 5                           # and Gemini was NOT asked again


# ---------- generate_structured ----------

@pytest.mark.anyio
async def test_structured_returns_the_ready_object():
    resp = SimpleNamespace(text="", parsed=Reply(answer="hi"), candidates=[], prompt_feedback=None)
    client, _ = make_client([resp])
    result = await client.generate_structured("Hi", system="s", schema=Reply)
    assert result == Reply(answer="hi")          # the ready object is returned as it is


@pytest.mark.anyio
async def test_structured_reads_json_inside_code_fences():
    client, _ = make_client([ok('```json\n{"answer": "fenced"}\n```')])  # no ready object, only text
    result = await client.generate_structured("Hi", system="s", schema=Reply)
    assert result.answer == "fenced"             # the fence was removed and the JSON was read


@pytest.mark.anyio
async def test_structured_invalid_json_twice_raises_and_asks_again_for_valid_json():
    client, models = make_client([ok("this is not json")])  # always invalid
    with pytest.raises(AIResponseError):
        await client.generate_structured("Make a roadmap", system="s", schema=Reply)
    assert models.calls == 2                                # first try plus one repair attempt
    assert "ONLY valid JSON" in models.kwargs_list[1]["contents"]  # the second try asks for valid JSON


# ---------- stream_text ----------

@pytest.mark.anyio
async def test_stream_gives_pieces_in_order():
    chunks = [SimpleNamespace(text="Hello ", candidates=[]), SimpleNamespace(text="world", candidates=[])]
    client, _ = make_client(chunks=chunks)
    pieces = [piece async for piece in client.stream_text("Hi", system="s")]  # read the whole stream
    assert pieces == ["Hello ", "world"]         # same pieces, same order


@pytest.mark.anyio
async def test_stream_safety_stop_raises_blocked_error():
    chunks = [SimpleNamespace(text="", candidates=[SimpleNamespace(finish_reason="SAFETY")])]
    client, _ = make_client(chunks=chunks)
    with pytest.raises(AIBlockedError):
        [piece async for piece in client.stream_text("Hi", system="s")]


@pytest.mark.anyio
async def test_stream_with_open_breaker_never_asks_gemini():
    client, models = make_client(chunks=[SimpleNamespace(text="x", candidates=[])])
    for _ in range(5):                           # five failures open the breaker
        client._breaker.failure()
    with pytest.raises(AIUnavailableError):
        [piece async for piece in client.stream_text("Hi", system="s")]
    assert models.stream_calls == 0              # the call was stopped before Gemini


# ---------- shared client ----------

def test_get_ai_client_returns_the_same_client():
    assert get_ai_client() is get_ai_client()    # one shared client, not a new one each time