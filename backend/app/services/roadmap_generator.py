"""Goal-based roadmap generation (feature 1).

Pipeline: validated intake -> prompt -> Gemini structured JSON -> strict
validation and *normalisation* (week ordering, hour budget, duplicate titles)
-> one automatic repair round if the plan is structurally unusable -> a clean
``RoadmapDraft`` the router/DB layer can persist as Dream -> Phases -> Tasks.

Also provides single-flight de-duplication: identical simultaneous requests
(double clicks) share one AI call, and an identical request within the TTL
returns the cached draft instead of spending quota again.
"""
from __future__ import annotations

import asyncio
import logging
import time
from datetime import date, timedelta
from typing import Optional

from pydantic import BaseModel, Field

from app.config import settings
from app.prompts.roadmap_prompts import ROADMAP_SYSTEM, build_repair_note, build_roadmap_prompt
from app.services.ai_client import AIResponseError, GeminiClient, get_ai_client
from app.services.disclaimer_service import roadmap_notice
from app.services.intake_service import IntakeAnswers
from app.services.scope_guard import neutralise_for_prompt
from app.utils.constants import TASK_TYPES

log = logging.getLogger("aspira.roadmap")

MIN_TASKS, MAX_TASKS = 6, 60


# ── Schema sent to Gemini (kept constraint-free for provider compatibility) ──
class _AITask(BaseModel):
    title: str
    description: str
    estimated_hours: float
    week: int
    skill_tags: list[str]
    task_type: str = "learning"  # optional so older fakes/replies without it still validate


class _AIPhase(BaseModel):
    name: str
    goal: str
    tasks: list[_AITask]


class _AIRoadmap(BaseModel):
    title: str
    summary: str
    phases: list[_AIPhase]


# ── Domain objects returned to the rest of the app ─────────────────────────
class TaskDraft(BaseModel):
    position: int
    title: str = Field(max_length=120)
    description: str
    estimated_hours: float = Field(ge=0.5, le=60)
    week: int = Field(ge=1)
    skill_tags: list[str] = []
    task_type: str = "learning"
    completed: bool = False


class PhaseDraft(BaseModel):
    position: int
    name: str
    goal: str
    tasks: list[TaskDraft]


class RoadmapDraft(BaseModel):
    title: str
    summary: str
    total_weeks: int
    total_hours: float
    phases: list[PhaseDraft]
    disclaimer: str = ""
    warnings: list[str] = []

    @property
    def tasks(self) -> list[TaskDraft]:
        return [t for p in self.phases for t in p.tasks]


def due_date_for_week(start: date, week: int) -> date:
    """Calendar due date for a task: the last day of its 1-based roadmap week.

    Lets the persistence layer always fill a required ``due_date`` column.
    """
    return start + timedelta(weeks=max(1, week)) - timedelta(days=1)


# ── Normalisation / validation ─────────────────────────────────────────────
def _clean_type(value: str) -> str:
    """Map the model's task_type onto the project's allowed set (default: learning)."""
    value = (value or "").strip().lower()
    return value if value in TASK_TYPES else "learning"


def _clip(s: str, n: int) -> str:
    s = " ".join((s or "").split())
    return s if len(s) <= n else s[: n - 1].rstrip() + "…"


def normalise(ai: _AIRoadmap, *, total_weeks: int, hours_budget: float) -> tuple[RoadmapDraft, list[str]]:
    """Return (draft, unrecoverable_problems). Fixable issues are repaired silently into warnings."""
    problems: list[str] = []
    warnings: list[str] = []
    seen: set[str] = set()
    phases: list[PhaseDraft] = []
    last_week = 1

    for ph in ai.phases:
        tasks: list[TaskDraft] = []
        for t in ph.tasks:
            key = " ".join(t.title.lower().split())
            if not key or key in seen:
                continue
            seen.add(key)
            week = min(max(int(t.week or 1), last_week), total_weeks)  # non-decreasing, capped
            last_week = week
            tasks.append(TaskDraft(
                position=0, title=_clip(t.title, 120), description=_clip(t.description, 500) or _clip(t.title, 120),
                estimated_hours=min(60.0, max(0.5, round(float(t.estimated_hours or 1), 1))), week=week,
                skill_tags=[_clip(x, 24) for x in t.skill_tags if x.strip()][:4],
                task_type=_clean_type(t.task_type)))
        if tasks:
            phases.append(PhaseDraft(position=0, name=_clip(ph.name, 80), goal=_clip(ph.goal, 300), tasks=tasks))

    flat = [t for p in phases for t in p.tasks]
    if len(phases) < 2:
        problems.append("Provide at least 2 phases.")
    if len(flat) < MIN_TASKS:
        problems.append(f"Provide at least {MIN_TASKS} distinct tasks (got {len(flat)}).")
    if len(flat) > MAX_TASKS:  # trim from the end, keep order
        keep = MAX_TASKS
        for p in phases:
            p.tasks = p.tasks[:keep]
            keep -= len(p.tasks)
            keep = max(keep, 0)
        phases = [p for p in phases if p.tasks]
        warnings.append(f"Plan trimmed to {MAX_TASKS} tasks.")
        flat = [t for p in phases for t in p.tasks]

    hours = sum(t.estimated_hours for t in flat)
    if hours_budget > 0 and hours > hours_budget:
        factor = (hours_budget * 0.95) / hours
        for t in flat:
            t.estimated_hours = max(0.5, round(t.estimated_hours * factor, 1))
        hours = sum(t.estimated_hours for t in flat)
        warnings.append("Task hours were scaled down to fit your weekly time budget.")

    for pi, p in enumerate(phases, 1):
        p.position = pi
    for ti, t in enumerate(flat, 1):
        t.position = ti

    draft = RoadmapDraft(
        title=_clip(ai.title, 120) or "My Career Roadmap", summary=_clip(ai.summary, 600),
        total_weeks=total_weeks, total_hours=round(hours, 1), phases=phases,
        disclaimer=roadmap_notice(), warnings=warnings)
    return draft, problems


async def produce_draft(*, system: str, prompt: str, total_weeks: int, hours_budget: float,
                        ai: Optional[GeminiClient] = None, temperature: float = 0.7) -> RoadmapDraft:
    """Shared engine used by generator and regenerator (structured call + one repair round)."""
    ai = ai or get_ai_client()
    current_prompt = prompt
    for attempt in range(2):
        raw = await ai.generate_structured(current_prompt, system=system, schema=_AIRoadmap,
                                           temperature=temperature)
        draft, problems = normalise(raw, total_weeks=total_weeks, hours_budget=hours_budget)
        if not problems:
            return draft
        log.warning("roadmap needs repair (attempt %s): %s", attempt + 1, problems)
        current_prompt = prompt + build_repair_note(problems)
    raise AIResponseError("Could not produce a valid roadmap. Please try again.")


# ── De-duplication (single-flight + short TTL cache) ───────────────────────
_cache: dict[str, tuple[float, RoadmapDraft]] = {}
_inflight: dict[str, "asyncio.Task[RoadmapDraft]"] = {}


def _cache_get(key: str) -> RoadmapDraft | None:
    hit = _cache.get(key)
    if hit and time.monotonic() - hit[0] < settings.roadmap_dedupe_ttl_seconds:
        return hit[1].model_copy(deep=True)
    _cache.pop(key, None)
    return None


def _cache_put(key: str, draft: RoadmapDraft) -> None:
    if len(_cache) > 256:
        _cache.pop(next(iter(_cache)))
    _cache[key] = (time.monotonic(), draft)


def prompt_from_answers(a: IntakeAnswers) -> str:
    n = neutralise_for_prompt
    return build_roadmap_prompt(
        career=f"<user_input>{n(a.target_career)}</user_input>", level=a.current_level,
        skills=f"<user_input>{n(a.current_skills)}</user_input>" if a.current_skills else "",
        hours_per_week=a.hours_per_week, timeline_months=a.timeline_months, total_weeks=a.total_weeks,
        total_hours=a.total_hours, learning_style=a.learning_style,
        extra=f"<user_input>{n(a.extra_context)}</user_input>" if a.extra_context else "")


async def generate_roadmap(answers: IntakeAnswers, *, ai: Optional[GeminiClient] = None,
                           use_cache: bool = True) -> RoadmapDraft:
    key = answers.fingerprint()
    if use_cache and (hit := _cache_get(key)):
        return hit
    if use_cache and (task := _inflight.get(key)):
        return (await asyncio.shield(task)).model_copy(deep=True)

    async def _run() -> RoadmapDraft:
        return await produce_draft(system=ROADMAP_SYSTEM, prompt=prompt_from_answers(answers),
                                   total_weeks=answers.total_weeks, hours_budget=answers.total_hours, ai=ai)

    task = asyncio.ensure_future(_run())
    if use_cache:
        _inflight[key] = task
    try:
        draft = await task
    finally:
        _inflight.pop(key, None)
    if use_cache:
        _cache_put(key, draft)
    return draft.model_copy(deep=True)
