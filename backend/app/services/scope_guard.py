"""Input hygiene and scope protection for everything user-written that reaches the AI.

Layer 1 (this file, no AI call, microseconds): normalise text, strip control /
invisible characters, cap length, detect prompt-injection and abuse patterns.
Layer 2 (model, in chat prompts): the model itself refuses non-career topics
using the OFF_TOPIC sentinel.
"""
from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from enum import Enum

OFF_TOPIC_SENTINEL = "[[OFF_TOPIC]]"


class Verdict(str, Enum):
    OK = "ok"
    EMPTY = "empty"
    TOO_LONG = "too_long"
    INJECTION = "injection"
    SPAM = "spam"


@dataclass(frozen=True)
class GuardResult:
    verdict: Verdict
    text: str  # sanitised text (safe to embed in a prompt)
    message: str = ""

    @property
    def allowed(self) -> bool:
        return self.verdict is Verdict.OK


_INVISIBLE = dict.fromkeys(
    [0x200B, 0x200C, 0x200D, 0x2060, 0xFEFF, 0x202A, 0x202B, 0x202C, 0x202D, 0x202E, 0x2066, 0x2067, 0x2068, 0x2069]
)

_INJECTION = [re.compile(p, re.I) for p in (
    r"ignore\s+(all\s+|any\s+|the\s+)?(previous|prior|above|earlier)\s+(instructions?|prompts?|rules?)",
    r"disregard\s+(all\s+|your\s+)?(previous|prior|above|system)\s+(instructions?|prompts?|rules?)",
    r"(reveal|show|print|repeat|leak)\s+(me\s+)?(your|the)\s+(system|hidden|initial)\s+(prompt|instructions?)",
    # role-reset attempts only; ordinary "you are now ready/eligible/..." must pass
    r"\byou\s+are\s+now\s+(?:in\s+\w+\s+mode|dan\b|(?:an?\s+)?(?:unrestricted|uncensored|unfiltered|jailbroken|evil|different|new)\b|no\s+longer\b|free\s+(?:of|from)\b|my\s+\w+\b)",
    r"\b(jailbreak|dan\s+mode|developer\s+mode)\b",
    r"act\s+as\s+(if\s+you\s+(have|had)\s+no|an?\s+unrestricted)",
    r"</?\s*(system|assistant|instructions?)\s*>",
    # "new instructions:" only when followed by an override verb, not in normal prose
    r"\bnew\s+instructions?\s*:\s*(?:you\b|ignore\b|disregard\b|forget\b|from\s+now\b|act\b|always\b|never\b)",
)]

_ROLE_TAG = re.compile(r"</?\s*(user_input|system|assistant|context)\s*>", re.I)


def normalise(text: str, *, max_chars: int) -> str:
    text = unicodedata.normalize("NFKC", text or "").translate(_INVISIBLE)
    text = "".join(ch for ch in text if ch in "\n\t" or unicodedata.category(ch)[0] != "C")
    text = re.sub(r"[ \t]{3,}", "  ", text)
    text = re.sub(r"\n{3,}", "\n\n", text).strip()
    return text[:max_chars]


def check_user_text(text: str, *, max_chars: int = 1500) -> GuardResult:
    raw = text or ""
    if len(raw) > max_chars * 2:
        return GuardResult(Verdict.TOO_LONG, "", f"Message is too long (limit {max_chars} characters).")
    clean = normalise(raw, max_chars=max_chars)
    if not clean:
        return GuardResult(Verdict.EMPTY, "", "Message is empty.")
    if len(raw.strip()) > max_chars:
        return GuardResult(Verdict.TOO_LONG, clean, f"Message is too long (limit {max_chars} characters).")
    if any(p.search(clean) for p in _INJECTION):
        return GuardResult(Verdict.INJECTION, clean,
                           "I can only help with your career roadmap and career questions.")
    if len(clean) > 40 and len(set(clean.lower())) <= 4:
        return GuardResult(Verdict.SPAM, clean, "That message doesn't look meaningful. Please rephrase.")
    return GuardResult(Verdict.OK, clean)


def neutralise_for_prompt(text: str) -> str:
    """Make user text inert inside prompt delimiters (cannot close our tags)."""
    return _ROLE_TAG.sub("", text).replace("```", "'''")


def wrap_user_input(text: str, tag: str = "user_input") -> str:
    return f"<{tag}>\n{neutralise_for_prompt(text)}\n</{tag}>"


def split_off_topic(text: str) -> tuple[bool, str]:
    """Detect the model's off-topic sentinel; returns (is_off_topic, text_without_sentinel)."""
    if OFF_TOPIC_SENTINEL in text:
        return True, text.replace(OFF_TOPIC_SENTINEL, "").strip()
    return False, text
