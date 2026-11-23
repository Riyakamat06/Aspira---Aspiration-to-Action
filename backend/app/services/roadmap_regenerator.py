"""Roadmap regeneration (feature 2).

Rebuilds the *remaining* plan using the learner's feedback while protecting
progress: finished tasks are carried over untouched in a leading
"Completed so far" phase and the AI only plans what is left, with the time
budget reduced by weeks already spent. Returns a diff so the UI can show what
changed.
"""
from __future__ import annotations

from typing import Optional

from pydantic import BaseModel

from app.prompts.roadmap_prompts import REGEN_SYSTEM, build_regen_prompt
from app.services.ai_client import GeminiClient
from app.services.intake_service import IntakeAnswers
from app.services.roadmap_generator import (
    PhaseDraft, RoadmapDraft, produce_draft, prompt_from_answers)
from app.services.scope_guard import Verdict, check_user_text, neutralise_for_prompt


class UnsafeFeedbackError(ValueError):
    """Feedback text was rejected by the input guard."""


class RegenerationResult(BaseModel):
    draft: RoadmapDraft
    kept_titles: list[str]
    added_titles: list[str]
    removed_titles: list[str]


def _norm(s: str) -> str:
    return " ".join(s.lower().split())


async def regenerate_roadmap(answers: IntakeAnswers, previous: RoadmapDraft, *, feedback: str = "",
                             weeks_elapsed: int = 0, keep_completed: bool = True,
                             ai: Optional[GeminiClient] = None) -> RegenerationResult:
    fb = check_user_text(feedback, max_chars=800) if feedback.strip() else None
    if fb and fb.verdict in (Verdict.INJECTION, Verdict.SPAM, Verdict.TOO_LONG):
        raise UnsafeFeedbackError(fb.message)
    clean_fb = fb.text if fb else ""

    completed = [t for t in previous.tasks if t.completed] if keep_completed else []
    remaining_weeks = max(1, answers.total_weeks - max(0, weeks_elapsed))
    remaining_hours = max(float(answers.hours_per_week), float(answers.hours_per_week * remaining_weeks))

    prompt = build_regen_prompt(
        base=prompt_from_answers(answers),
        previous_titles=[t.title for t in previous.tasks],
        completed_titles=[t.title for t in completed],
        feedback=f"<user_input>{neutralise_for_prompt(clean_fb)}</user_input>" if clean_fb else "",
        remaining_weeks=remaining_weeks, remaining_hours=int(remaining_hours))

    fresh = await produce_draft(system=REGEN_SYSTEM, prompt=prompt, total_weeks=remaining_weeks,
                                hours_budget=remaining_hours, ai=ai, temperature=0.8)

    # Drop AI tasks that repeat completed work, then merge.
    done_keys = {_norm(t.title) for t in completed}
    for ph in fresh.phases:
        ph.tasks = [t for t in ph.tasks if _norm(t.title) not in done_keys]
    fresh.phases = [p for p in fresh.phases if p.tasks]

    phases: list[PhaseDraft] = []
    if completed:
        carried = [t.model_copy(update={"completed": True}) for t in completed]
        phases.append(PhaseDraft(position=0, name="Completed so far", goal="Progress you have already made.",
                                 tasks=carried))
    # Fresh tasks come after the weeks already spent: the AI plans weeks 1..N for the
    # time that is left, so move them later by the weeks elapsed (never past the total).
    # The caller anchors due dates at (today - weeks_elapsed) so dates stay correct.
    offset = max(0, weeks_elapsed) if completed else 0
    for ph in fresh.phases:
        for t in ph.tasks:
            t.week = min(answers.total_weeks, t.week + offset)
        phases.append(ph)
    for pi, p in enumerate(phases, 1):
        p.position = pi
    n = 0
    for p in phases:
        for t in p.tasks:
            n += 1
            t.position = n

    merged = fresh.model_copy(update={
        "phases": phases, "total_weeks": answers.total_weeks,
        "total_hours": round(sum(t.estimated_hours for p in phases for t in p.tasks), 1),
        "warnings": fresh.warnings})
    old_keys = {_norm(t.title): t.title for t in previous.tasks if not t.completed}
    new_keys = {_norm(t.title): t.title for t in merged.tasks if not t.completed}
    return RegenerationResult(
        draft=merged, kept_titles=[t.title for t in completed],
        added_titles=[v for k, v in new_keys.items() if k not in old_keys],
        removed_titles=[v for k, v in old_keys.items() if k not in new_keys])
