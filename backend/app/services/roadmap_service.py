"""Roadmap persistence and presentation: connects the AI services to the database.

roadmap_generator / roadmap_regenerator only produce an in-memory ``RoadmapDraft``. This file
turns a draft into rows (Dream -> Roadmap -> Milestone -> Task), guards ownership, and turns rows
back into the JSON shape the frontend reads (Sonali's ``RoadmapResponse``).

Mapping used (the AI's "phase" is a database "milestone")
    draft.phase  -> Milestone(title=name, description=goal, order_index=position, target_date=last task due)
    draft.task   -> Task(title, task_type, status, due_date = start date + the task's week)
    Roadmap.source = "ai"   (API shows "generated");  Roadmap.version = order of creation per dream.

Design decisions
* One transaction per save (all rows or nothing). Ananya's repositories commit after every single
  row, which for a 40-task roadmap means ~50 commits and a half-saved roadmap if something fails;
  so the *write* path uses the models directly, while reads/ownership checks use her repositories.
* Ownership is always checked through the dream: roadmap -> dream -> user_id. Someone else's
  roadmap answers 404, never 403, so ids cannot be probed.
* Forward compatible with two requested columns (Task.description / Task.estimated_hours and
  Roadmap.intake_json): they are saved only if the model has them. Without ``intake_json`` the
  client must resend the intake answers when regenerating.

Public functions: get_owned_dream, get_owned_roadmap, get_owned_task, prepare_generation, persist_roadmap, load_regeneration_state, get_owned_roadmap,
build_response, list_roadmaps, delete_roadmap.
"""
from __future__ import annotations

import json
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import date

from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.config import settings
from app.core.exceptions import NotFoundError
from app.core.http_errors import ForbiddenError, UnprocessableError
from app.models.dream import Dream
from app.models.milestone import Milestone
from app.models.roadmap import Roadmap
from app.models.task import Task
from app.repositories import dream_repository, roadmap_repository, task_repository
from app.schemas.roadmap_schema import MilestoneResponse, RoadmapResponse
from app.schemas.task_schema import TaskResponse
from app.services import disclaimer_service
from app.services.intake_service import IntakeAnswers, IntakeError, validate_answers
from app.services.roadmap_generator import PhaseDraft, RoadmapDraft, TaskDraft, due_date_for_week
from app.utils.constants import TASK_COMPLETED, TASK_PENDING

COMPLETED_PHASE = "Completed so far"


# ── Response models (extend Sonali's RoadmapResponse with what the UI also needs) ──
class RoadmapDetail(RoadmapResponse):
    """Sonali's RoadmapResponse plus title, summary, progress and the AI notice."""
    title: str
    summary: str | None = None
    total_tasks: int = 0
    completed_tasks: int = 0
    completion_percent: float = 0.0
    notice: str = ""


class RoadmapSummary(BaseModel):
    id: int
    dream_id: int
    title: str
    summary: str | None = None
    source: str
    version: int
    total_tasks: int
    completed_tasks: int
    completion_percent: float


# ── Ownership helpers ──────────────────────────────────────────────────────
def get_owned_dream(db: Session, user_id: int, dream_id: int) -> Dream:
    dream = dream_repository.get_dream(db, dream_id, user_id)
    if dream is None:
        raise NotFoundError("Dream")
    return dream


def get_owned_roadmap(db: Session, user_id: int, roadmap_id: int) -> tuple[Roadmap, Dream]:
    roadmap = roadmap_repository.get_roadmap(db, roadmap_id)
    dream = dream_repository.get_dream(db, roadmap.dream_id, user_id) if roadmap else None
    if roadmap is None or dream is None:
        raise NotFoundError("Roadmap")
    return roadmap, dream


def get_owned_task(db: Session, user_id: int, task_id: int) -> Task:
    """Return a task only if it belongs to this user (task -> milestone -> roadmap -> dream -> user).

    Ananya's task repository has no user check, so any service that reads or changes a task by id
    (for example Sonali's task_service / task_router) must call this first; otherwise one user could
    change another user's tasks by guessing ids. Not found and not yours both answer 404.
    """
    task = task_repository.get_task(db, task_id)
    milestone = db.get(Milestone, task.milestone_id) if task else None
    if task is None or milestone is None:
        raise NotFoundError("Task")
    parent = roadmap_repository.get_roadmap(db, milestone.roadmap_id)
    dream = (dream_repository.get_dream(db, parent.dream_id, user_id)
             if parent else None)
    if dream is None:
        raise NotFoundError("Task")
    return task


def prepare_generation(db: Session, user_id: int, dream_id: int | None) -> Dream | None:
    """Validate before spending an AI call: the dream must be the user's, or a new one must fit the cap."""
    if dream_id is not None:
        return get_owned_dream(db, user_id, dream_id)
    if len(dream_repository.list_dreams(db, user_id)) >= settings.max_dreams_per_user:
        raise ForbiddenError(
            f"You can keep up to {settings.max_dreams_per_user} dreams. Delete one before adding another.")
    return None


# ── Writing ────────────────────────────────────────────────────────────────
def _norm(title: str) -> str:
    return " ".join(title.lower().split())


def _set_optional(obj, **fields) -> None:
    """Set attributes only if the model defines that column (forward compatible)."""
    for name, value in fields.items():
        if hasattr(type(obj), name):
            setattr(obj, name, value)


def persist_roadmap(db: Session, user_id: int, draft: RoadmapDraft, answers: IntakeAnswers, *,
                    dream: Dream | None = None, start: date | None = None,
                    due_overrides: dict[str, date] | None = None) -> Roadmap:
    """Save draft as a new roadmap (and a new dream when ``dream`` is None) in ONE transaction.

    ``due_overrides`` maps normalised task titles to fixed due dates (used to keep the original
    deadlines of finished tasks when a roadmap is regenerated).
    """
    start = start or date.today()
    overrides = due_overrides or {}
    try:
        if dream is None:
            dream = Dream(user_id=user_id, title=answers.target_career[:200])
            db.add(dream)
            db.flush()
        roadmap = Roadmap(dream_id=dream.id, title=draft.title[:200], summary=draft.summary, source="ai")
        _set_optional(roadmap, intake_json=answers.model_dump_json())
        db.add(roadmap)
        db.flush()
        for phase in draft.phases:
            milestone = Milestone(roadmap_id=roadmap.id, title=phase.name[:200],
                                  description=phase.goal, order_index=phase.position)
            db.add(milestone)
            db.flush()
            tasks: list[Task] = []
            for t in phase.tasks:
                due = overrides.get(_norm(t.title)) or due_date_for_week(start, t.week)
                task = Task(milestone_id=milestone.id, title=t.title[:200], task_type=t.task_type,
                            status=TASK_COMPLETED if t.completed else TASK_PENDING, due_date=due)
                _set_optional(task, description=t.description, estimated_hours=t.estimated_hours)
                tasks.append(task)
            db.add_all(tasks)
            if tasks:
                milestone.target_date = max(t.due_date for t in tasks)
        db.commit()
    except Exception:
        db.rollback()
        raise
    db.refresh(roadmap)
    return roadmap


# ── Regeneration state (rebuild the previous plan from the database) ────────
@dataclass
class RegenState:
    roadmap: Roadmap
    dream: Dream
    answers: IntakeAnswers
    previous: RoadmapDraft
    weeks_elapsed: int
    due_overrides: dict[str, date] = field(default_factory=dict)


def load_regeneration_state(db: Session, user_id: int, roadmap_id: int,
                            answers_override: dict | None = None) -> RegenState:
    roadmap, dream = get_owned_roadmap(db, user_id, roadmap_id)
    raw = getattr(roadmap, "intake_json", None)
    try:
        answers = validate_answers(json.loads(raw)) if raw else (
            validate_answers(answers_override) if answers_override else None)
    except IntakeError as exc:
        raise UnprocessableError({"answers": exc.errors}) from exc
    if answers is None:
        raise UnprocessableError(
            "The original intake answers are not stored for this roadmap. Send them in 'answers'.")

    created = roadmap.created_at.date()
    milestones = roadmap_repository.list_milestones(db, roadmap.id)
    tasks = task_repository.list_tasks_for_roadmap(db, roadmap.id)
    by_milestone: dict[int, list[Task]] = defaultdict(list)
    for t in tasks:
        by_milestone[t.milestone_id].append(t)

    phases: list[PhaseDraft] = []
    position = 0
    overrides: dict[str, date] = {}
    for ms in milestones:
        drafts: list[TaskDraft] = []
        for t in by_milestone.get(ms.id, []):
            position += 1
            done = t.status == TASK_COMPLETED
            if done:
                overrides[_norm(t.title)] = t.due_date
            hours = getattr(t, "estimated_hours", None) or 1.0
            drafts.append(TaskDraft(
                position=position, title=t.title, description=getattr(t, "description", None) or t.title,
                estimated_hours=min(60.0, max(0.5, float(hours))),
                week=max(1, ((t.due_date - created).days + 6) // 7), skill_tags=[],
                task_type=t.task_type or "learning", completed=done))
        if drafts:
            phases.append(PhaseDraft(position=len(phases) + 1, name=ms.title,
                                     goal=ms.description or "", tasks=drafts))
    previous = RoadmapDraft(
        title=roadmap.title, summary=roadmap.summary or "", total_weeks=answers.total_weeks,
        total_hours=round(sum(t.estimated_hours for p in phases for t in p.tasks), 1), phases=phases)
    return RegenState(roadmap=roadmap, dream=dream, answers=answers, previous=previous,
                      weeks_elapsed=max(0, (date.today() - created).days // 7), due_overrides=overrides)


# ── Reading ────────────────────────────────────────────────────────────────
def _percent(done: int, total: int) -> float:
    return round(100.0 * done / total, 1) if total else 0.0


def _version(db: Session, roadmap: Roadmap) -> int:
    return sum(1 for r in roadmap_repository.list_roadmaps(db, roadmap.dream_id) if r.id <= roadmap.id)


def build_response(db: Session, roadmap: Roadmap, dream: Dream | None = None) -> RoadmapDetail:
    dream = dream or db.get(Dream, roadmap.dream_id)
    milestones = roadmap_repository.list_milestones(db, roadmap.id)
    tasks = task_repository.list_tasks_for_roadmap(db, roadmap.id)
    by_milestone: dict[int, list[Task]] = defaultdict(list)
    for t in tasks:
        by_milestone[t.milestone_id].append(t)

    out: list[MilestoneResponse] = []
    for ms in milestones:
        mts = by_milestone.get(ms.id, [])
        done = sum(1 for t in mts if t.status == TASK_COMPLETED)
        out.append(MilestoneResponse(
            id=ms.id, title=ms.title, order=ms.order_index, completion_percent=_percent(done, len(mts)),
            tasks=[TaskResponse.model_validate(t) for t in mts]))
    completed = sum(1 for t in tasks if t.status == TASK_COMPLETED)
    return RoadmapDetail(
        id=roadmap.id, dream_id=roadmap.dream_id,
        source="generated" if roadmap.source == "ai" else "user_created",
        version=_version(db, roadmap), disclaimer=disclaimer_service.needs_regulated_disclaimer(dream.title),
        created_at=roadmap.created_at, milestones=out, title=roadmap.title, summary=roadmap.summary,
        total_tasks=len(tasks), completed_tasks=completed, completion_percent=_percent(completed, len(tasks)),
        notice=disclaimer_service.roadmap_notice())


def list_roadmaps(db: Session, user_id: int, dream_id: int) -> list[RoadmapSummary]:
    get_owned_dream(db, user_id, dream_id)
    roadmaps = roadmap_repository.list_roadmaps(db, dream_id)  # newest first
    total = len(roadmaps)
    out = []
    for index, r in enumerate(roadmaps):
        tasks = task_repository.list_tasks_for_roadmap(db, r.id)
        done = sum(1 for t in tasks if t.status == TASK_COMPLETED)
        out.append(RoadmapSummary(
            id=r.id, dream_id=r.dream_id, title=r.title, summary=r.summary, source=r.source,
            version=total - index, total_tasks=len(tasks), completed_tasks=done,
            completion_percent=_percent(done, len(tasks))))
    return out


def delete_roadmap(db: Session, user_id: int, roadmap_id: int) -> None:
    roadmap, _ = get_owned_roadmap(db, user_id, roadmap_id)
    roadmap_repository.delete_roadmap(db, roadmap.id)  # cascades to milestones and tasks
