"""Responsible-AI notices attached to roadmaps and chatbot answers.

Detects sensitive topics in AI output (pay, guarantees, legal/visa, health,
investing) and appends the matching short notice once, so users are not told
the AI's output is a promise.
"""
from __future__ import annotations

import re

ROADMAP_DISCLAIMER = (
    "This roadmap is AI-generated guidance. Timelines and hours are estimates; "
    "adapt it to your situation and verify important details with trusted sources."
)
CHAT_BASE_DISCLAIMER = "Aspira's assistant gives general career guidance, not professional advice."

REFUSAL_MESSAGE = (
    "I'm here for career and learning-roadmap questions only. "
    "Ask me about your goal, skills, tasks or next steps and I'll gladly help."
)

_RULES: list[tuple[str, re.Pattern[str], str]] = [
    ("salary", re.compile(r"\b(salary|salaries|ctc|lpa|package|compensation|per\s+(year|annum|month))\b|[₹$€£]\s?\d", re.I),
     "Salary figures vary widely by company, city and time; treat them as rough indications."),
    ("guarantee", re.compile(r"\b(guarantee[sd]?|definitely\s+get|will\s+(surely|certainly)\s+(get|land)|100%\s+(placement|selection))\b", re.I),
     "No outcome such as a job offer can be guaranteed; results depend on your effort and the market."),
    ("legal", re.compile(r"\b(visa|immigration|work\s+permit|contract\s+clause|non-?compete|lawsuit)\b", re.I),
     "For visas, contracts or legal matters, consult a qualified professional or official source."),
    ("health", re.compile(r"\b(burnout|anxiety|depress(ed|ion)|medication|therapy|panic)\b", re.I),
     "For health or wellbeing concerns, please talk to a qualified professional or someone you trust."),
    ("finance", re.compile(r"\b(invest(ing|ment)?|stocks?|crypto|loan|mutual\s+funds?)\b", re.I),
     "This is not financial advice; consult a certified financial adviser."),
]


def detect_topics(text: str) -> list[str]:
    return [name for name, pat, _ in _RULES if pat.search(text or "")]


def apply_disclaimers(answer: str) -> tuple[str, list[str]]:
    """Return (answer, notices). Notices are returned separately so the UI can style them."""
    notices = [note for _, pat, note in _RULES if pat.search(answer or "")]
    return answer, notices


def roadmap_notice() -> str:
    return ROADMAP_DISCLAIMER


def refusal() -> str:
    return REFUSAL_MESSAGE
