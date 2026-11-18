"""Career-only chatbot (feature 3) on top of Gemini.

Defence in depth: (1) scope_guard blocks injection/spam before any AI call,
(2) the system prompt makes the model emit ``[[OFF_TOPIC]]`` for out-of-scope
requests, (3) responses get responsible-AI notices. History is trimmed to a
character budget so long chats stay fast and cheap. Both a one-shot ``reply``
and a streaming ``stream_reply`` are provided.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import AsyncIterator, Literal, Optional, Sequence

from google.genai import types
from pydantic import BaseModel

from app.config import settings
from app.prompts.chat_prompts import CHAT_SYSTEM, build_context_block
from app.services import disclaimer_service as disclaimers
from app.services.ai_client import GeminiClient, get_ai_client
from app.services.scope_guard import (
    OFF_TOPIC_SENTINEL, check_user_text, split_off_topic, wrap_user_input)


@dataclass
class ChatContext:
    career: str
    level: str = "beginner"
    roadmap_title: Optional[str] = None
    upcoming_tasks: list[str] = field(default_factory=list)
    completed_count: int = 0
    total_count: int = 0


class ChatTurn(BaseModel):
    role: Literal["user", "assistant"]
    text: str


class ChatReply(BaseModel):
    text: str
    in_scope: bool = True
    blocked: bool = False
    notices: list[str] = []


def _trim_history(history: Sequence[ChatTurn]) -> list[ChatTurn]:
    kept: list[ChatTurn] = []
    budget = settings.chat_history_char_budget
    for turn in reversed(history):  # newest first
        cost = len(turn.text)
        if cost > budget and kept:
            break
        kept.append(turn)
        budget -= cost
        if budget <= 0:
            break
    kept.reverse()
    while kept and kept[0].role != "user":  # Gemini expects a user-first conversation
        kept.pop(0)
    return kept


def build_contents(message: str, history: Sequence[ChatTurn], ctx: ChatContext) -> list[types.Content]:
    contents: list[types.Content] = []
    for t in _trim_history(history):
        contents.append(types.Content(role="user" if t.role == "user" else "model",
                                      parts=[types.Part(text=wrap_user_input(t.text) if t.role == "user" else t.text)]))
    block = build_context_block(
        career=ctx.career, level=ctx.level, roadmap_title=ctx.roadmap_title,
        upcoming_tasks=ctx.upcoming_tasks, completed_count=ctx.completed_count, total_count=ctx.total_count)
    contents.append(types.Content(role="user", parts=[types.Part(text=f"{block}\n\n{wrap_user_input(message)}")]))
    return contents


def _refusal(message: str | None = None) -> ChatReply:
    return ChatReply(text=message or disclaimers.refusal(), in_scope=False, blocked=True)


async def reply(message: str, history: Sequence[ChatTurn], ctx: ChatContext, *,
                ai: Optional[GeminiClient] = None) -> ChatReply:
    guard = check_user_text(message, max_chars=settings.chat_message_max_chars)
    if not guard.allowed:
        return _refusal(guard.message)
    ai = ai or get_ai_client()
    raw = await ai.generate_text(build_contents(guard.text, history, ctx), system=CHAT_SYSTEM,
                                 temperature=0.5, max_tokens=settings.gemini_chat_max_output_tokens)
    off, text = split_off_topic(raw)
    if off:
        return ChatReply(text=text or disclaimers.refusal(), in_scope=False)
    text, notices = disclaimers.apply_disclaimers(text)
    return ChatReply(text=text, notices=notices)


class StreamEvent(BaseModel):
    kind: Literal["delta", "done", "refused"]
    text: str = ""
    notices: list[str] = []


async def stream_reply(message: str, history: Sequence[ChatTurn], ctx: ChatContext, *,
                       ai: Optional[GeminiClient] = None) -> AsyncIterator[StreamEvent]:
    """Yield ``delta`` events, then one ``done`` (with notices) or a single ``refused``."""
    guard = check_user_text(message, max_chars=settings.chat_message_max_chars)
    if not guard.allowed:
        yield StreamEvent(kind="refused", text=guard.message)
        return
    ai = ai or get_ai_client()
    stream = ai.stream_text(build_contents(guard.text, history, ctx), system=CHAT_SYSTEM,
                            temperature=0.5, max_tokens=settings.gemini_chat_max_output_tokens)
    mode, buf, parts = "probe", "", []
    async for chunk in stream:
        if mode == "stream":
            parts.append(chunk)
            yield StreamEvent(kind="delta", text=chunk)
            continue
        buf += chunk
        if mode == "off":
            continue
        probe = buf.lstrip()
        if len(probe) < len(OFF_TOPIC_SENTINEL) and OFF_TOPIC_SENTINEL.startswith(probe):
            continue  # might still become the sentinel; keep buffering
        if probe.startswith(OFF_TOPIC_SENTINEL):
            mode, buf = "off", probe  # collect the short refusal silently
            continue
        mode = "stream"
        parts.append(buf)
        yield StreamEvent(kind="delta", text=buf)
    if mode == "off" or (mode == "probe" and split_off_topic(buf)[0]):
        yield StreamEvent(kind="refused", text=split_off_topic(buf)[1] or disclaimers.refusal())
        return
    if mode == "probe" and buf:
        parts.append(buf)
        yield StreamEvent(kind="delta", text=buf)
    _, notices = disclaimers.apply_disclaimers("".join(parts))
    yield StreamEvent(kind="done", notices=notices)
