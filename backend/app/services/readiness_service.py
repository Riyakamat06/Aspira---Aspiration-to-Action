"""Readiness score (feature 13): a transparent 0-100 estimate of progress towards a dream.

The score is computed by ordinary code (not by the AI) from the learner's own roadmap data, so it is
explainable. Four components, each valued 0..1, are weighted and added:

    completion  50 %  finished tasks / all tasks of the current roadmap
    on_time     25 %  of the tasks whose due date has arrived, how many are finished
    momentum    15 %  in how many of the last 4 weeks was at least one more task finished
                      (from weekly progress snapshots)
    reflection  10 %  journal entries about this dream in the last 30 days (4 or more = full marks)

A component with no data yet (for example no tasks are due yet) is left out and the remaining
weights are scaled up to 100 %, so a brand-new roadmap is not punished for what cannot be measured.
The report lists every component with its points and a plain-language ``next_step``.

``compute_readiness`` is pure (no database) and fully unit-tested; ``get_readiness`` loads the data
from Ananya's repositories and also refreshes this week's progress snapshot (one upsert).

Contract for the frontend (Tanushree): the JSON of ``ReadinessReport`` below.
"""
from __future__ import annotations

from datetime import date, timedelta
from typing import Sequence

from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.repositories import (analytics_repository, dream_repository, journal_repository,
                              roadmap_repository, task_repository)
from app.utils.constants import TASK_COMPLETED
from app.utils.date_utils import get_week_start

BASE_WEIGHTS = {"completion": 0.50, "on_time": 0.25, "momentum": 0.15, "reflection": 0.10}
LEVELS = [(20, "Just starting"), (45, "Building foundations"), (70, "Making progress"),
          (90, "Almost ready"), (101, "Well prepared")]
NOTE = "An estimate of your progress against your own roadmap, not a prediction of hiring outcomes."


class ReadinessComponent(BaseModel):
    key: str
    label: str
    weight: float     # effective weight after leaving out unavailable parts (adds up to 1.0)
    value: float      # 0..1
    points: float     # value * weight * 100
    detail: str


class ReadinessReport(BaseModel):
    dream_id: int
    roadmap_id: int | None = None
    score: int
    level: str
    total_tasks: int
    completed_tasks: int
    overdue_tasks: int
    components: list[ReadinessComponent]
    next_step: str
    note: str = NOTE
    as_of: date


def _level(score: int) -> str:
    return next(name for limit, name in LEVELS if score < limit)


def weeks_with_progress(snapshots: Sequence[tuple[date, int]], today: date) -> int:
    """How many of the last 4 weeks (including this one) saw more finished tasks than the week before."""
    gains: set[date] = set()
    previous = 0
    for week, done in sorted(snapshots):
        if done > previous:
            gains.add(week)
        previous = done
    this_monday = get_week_start(today)
    window = {this_monday - timedelta(days=7 * k) for k in range(4)}
    return len(gains & window)


def compute_readiness(*, dream_id: int, roadmap_id: int | None, tasks: Sequence,
                      snapshots: Sequence[tuple[date, int]], journal_entries_30d: int,
                      today: date) -> ReadinessReport:
    """``tasks`` need ``.status``, ``.due_date`` and ``.title`` attributes."""
    total = len(tasks)
    done = [t for t in tasks if t.status == TASK_COMPLETED]
    open_tasks = sorted((t for t in tasks if t.status != TASK_COMPLETED), key=lambda t: t.due_date)
    overdue = [t for t in open_tasks if t.due_date < today]
    due_now = [t for t in tasks if t.due_date <= today]
    due_done = sum(1 for t in due_now if t.status == TASK_COMPLETED)

    if total == 0:
        return ReadinessReport(dream_id=dream_id, roadmap_id=roadmap_id, score=0, level="Not started",
                               total_tasks=0, completed_tasks=0, overdue_tasks=0, components=[],
                               next_step="Generate your roadmap to start tracking readiness.", as_of=today)

    raw: dict[str, tuple[str, float, str]] = {
        "completion": ("Tasks finished", len(done) / total, f"{len(done)} of {total} tasks finished"),
        "reflection": ("Reflection", min(journal_entries_30d, 4) / 4,
                       f"{journal_entries_30d} journal entries in the last 30 days"),
    }
    if due_now:
        raw["on_time"] = ("On schedule", due_done / len(due_now),
                          f"{due_done} of {len(due_now)} tasks that were due are finished")
    if snapshots:
        weeks = weeks_with_progress(snapshots, today)
        raw["momentum"] = ("Weekly momentum", weeks / 4, f"progress in {weeks} of the last 4 weeks")

    weight_sum = sum(BASE_WEIGHTS[k] for k in raw)
    components = []
    for key in ("completion", "on_time", "momentum", "reflection"):
        if key not in raw:
            continue
        label, value, detail = raw[key]
        weight = BASE_WEIGHTS[key] / weight_sum
        components.append(ReadinessComponent(key=key, label=label, weight=round(weight, 3),
                                             value=round(value, 3), points=round(value * weight * 100, 1),
                                             detail=detail))
    score = max(0, min(100, round(sum(c.points for c in components))))

    by_key = {c.key: c for c in components}
    next_title = open_tasks[0].title if open_tasks else None
    if overdue:
        step = f"Catch up on {len(overdue)} overdue task(s), starting with '{overdue[0].title}'."
    elif not open_tasks:
        step = "You have finished every task. Review your roadmap or start a new dream."
    elif "momentum" in by_key and by_key["momentum"].value < 0.5:
        step = f"Finish at least one task every week. Next up: '{next_title}'."
    elif by_key["reflection"].value < 0.5:
        step = "Write a journal entry about what you learned this week."
    else:
        step = f"Next up: '{next_title}'."

    return ReadinessReport(dream_id=dream_id, roadmap_id=roadmap_id, score=score, level=_level(score),
                           total_tasks=total, completed_tasks=len(done), overdue_tasks=len(overdue),
                           components=components, next_step=step, as_of=today)


def get_readiness(db: Session, user_id: int, dream_id: int, *, today: date | None = None,
                  record_snapshot: bool = True) -> ReadinessReport:
    today = today or date.today()
    if dream_repository.get_dream(db, dream_id, user_id) is None:
        raise NotFoundError("Dream")
    roadmaps = roadmap_repository.list_roadmaps(db, dream_id)  # newest first; older versions are superseded
    latest = roadmaps[0] if roadmaps else None
    tasks = task_repository.list_tasks_for_roadmap(db, latest.id) if latest else []

    if record_snapshot and tasks:
        analytics_repository.save_weekly_snapshot(
            db, user_id, dream_id, get_week_start(today),
            sum(1 for t in tasks if t.status == TASK_COMPLETED), len(tasks))
    snapshots = [(s.week_start, s.tasks_completed)
                 for s in analytics_repository.list_snapshots(db, user_id, dream_id)]
    recent = sum(1 for e in journal_repository.list_entries(db, user_id)
                 if e.dream_id == dream_id and 0 <= (today - e.created_at.date()).days <= 30)
    return compute_readiness(dream_id=dream_id, roadmap_id=latest.id if latest else None, tasks=tasks,
                             snapshots=snapshots, journal_entries_30d=recent, today=today)
