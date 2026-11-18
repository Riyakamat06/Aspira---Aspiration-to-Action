"""Fixed intake questionnaire for goal-based roadmap generation.

Defines the questions the frontend renders (so UI and backend never drift) and
validates / sanitises the answers into an ``IntakeAnswers`` object that every
roadmap prompt is built from.
"""
from __future__ import annotations

import re
from typing import Any, Literal

from pydantic import BaseModel, Field, ValidationError, field_validator

from app.services.scope_guard import Verdict, check_user_text

Level = Literal["beginner", "intermediate", "advanced"]
LearningStyle = Literal["videos", "reading", "projects", "mixed"]


class IntakeQuestion(BaseModel):
    key: str
    label: str
    type: Literal["text", "textarea", "choice", "number"]
    required: bool = True
    options: list[str] | None = None
    min: int | None = None
    max: int | None = None
    placeholder: str | None = None


INTAKE_QUESTIONS: list[IntakeQuestion] = [
    IntakeQuestion(key="target_career", label="What career or role do you want to reach?", type="text",
                   placeholder="e.g. Backend Developer at a product company"),
    IntakeQuestion(key="current_level", label="How would you rate your current level for this goal?", type="choice",
                   options=["beginner", "intermediate", "advanced"]),
    IntakeQuestion(key="current_skills", label="Which relevant skills or tools do you already know?", type="textarea",
                   required=False, placeholder="e.g. Python basics, SQL, Git"),
    IntakeQuestion(key="hours_per_week", label="How many hours per week can you give?", type="number", min=1, max=60),
    IntakeQuestion(key="timeline_months", label="In how many months do you want to be ready?", type="number", min=1, max=36),
    IntakeQuestion(key="learning_style", label="How do you learn best?", type="choice",
                   options=["videos", "reading", "projects", "mixed"], required=False),
    IntakeQuestion(key="extra_context", label="Anything else we should know (education, constraints, target companies)?",
                   type="textarea", required=False),
]

_LETTER = re.compile(r"[A-Za-zऀ-ॿಀ-೿]")


class IntakeError(ValueError):
    def __init__(self, errors: dict[str, str]) -> None:
        super().__init__("; ".join(f"{k}: {v}" for k, v in errors.items()))
        self.errors = errors


class IntakeAnswers(BaseModel):
    target_career: str = Field(min_length=3, max_length=120)
    current_level: Level
    current_skills: str = Field(default="", max_length=600)
    hours_per_week: int = Field(ge=1, le=60)
    timeline_months: int = Field(ge=1, le=36)
    learning_style: LearningStyle = "mixed"
    extra_context: str = Field(default="", max_length=800)

    @field_validator("target_career")
    @classmethod
    def _career_meaningful(cls, v: str) -> str:
        if len(_LETTER.findall(v)) < 3:
            raise ValueError("Please describe a real career or role.")
        return v

    @property
    def total_hours(self) -> int:
        return round(self.hours_per_week * self.timeline_months * 4.345)

    @property
    def total_weeks(self) -> int:
        return max(1, round(self.timeline_months * 4.345))

    def fingerprint(self) -> str:
        import hashlib, json
        return hashlib.sha256(json.dumps(self.model_dump(), sort_keys=True).encode()).hexdigest()[:24]


_TEXT_LIMITS = {"target_career": 120, "current_skills": 600, "extra_context": 800}


def get_questions() -> list[dict[str, Any]]:
    return [q.model_dump(exclude_none=True) for q in INTAKE_QUESTIONS]


def validate_answers(raw: dict[str, Any]) -> IntakeAnswers:
    """Sanitise free text, coerce numbers, and raise ``IntakeError`` with per-field messages."""
    errors: dict[str, str] = {}
    cleaned: dict[str, Any] = {}
    for key, value in (raw or {}).items():
        if key in _TEXT_LIMITS:
            res = check_user_text(str(value or ""), max_chars=_TEXT_LIMITS[key])
            if res.verdict in (Verdict.INJECTION, Verdict.SPAM):
                errors[key] = "This text isn't acceptable. Please rewrite it."
                continue
            cleaned[key] = res.text if res.verdict is not Verdict.EMPTY else ""
        elif key in ("hours_per_week", "timeline_months"):
            try:
                cleaned[key] = int(float(value))
            except (TypeError, ValueError):
                errors[key] = "Must be a number."
        elif isinstance(value, str):
            cleaned[key] = value.strip().lower()
        else:
            cleaned[key] = value
    if errors:
        raise IntakeError(errors)
    try:
        return IntakeAnswers(**{k: v for k, v in cleaned.items() if k in IntakeAnswers.model_fields})
    except ValidationError as exc:
        raise IntakeError({".".join(map(str, e["loc"])): e["msg"] for e in exc.errors()}) from exc
