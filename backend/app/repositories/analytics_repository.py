"""
analytics_repository.py  (M1 Database, owner: Ananya)

What it is for:
    Database queries for the weekly progress graph and the readiness score.

Who uses it:
    Sonali's analytics_service.py and Riya's readiness_service.py.

What it contains:
    count_tasks_by_status(db, dream_id) -> dict like {"pending": 3, "completed": 2}
    save_weekly_snapshot(db, user_id, dream_id, week_start, tasks_completed,
                         tasks_total) -> ProgressSnapshot
    list_snapshots(db, user_id, dream_id) -> list of ProgressSnapshot, oldest first

Note:
    save_weekly_snapshot updates the row if that week already has one,
    so there is only one snapshot per dream per week.
"""

from datetime import date

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.milestone import Milestone
from app.models.progress_snapshot import ProgressSnapshot
from app.models.roadmap import Roadmap
from app.models.task import Task


def count_tasks_by_status(db: Session, dream_id: int) -> dict[str, int]:
    """Count tasks of a dream for each status (joins tasks, milestones, roadmaps)."""
    rows = db.execute(
        select(Task.status, func.count(Task.id))
        .join(Milestone, Task.milestone_id == Milestone.id)
        .join(Roadmap, Milestone.roadmap_id == Roadmap.id)
        .where(Roadmap.dream_id == dream_id)
        .group_by(Task.status)
    ).all()
    return {status: count for status, count in rows}


def save_weekly_snapshot(db: Session, user_id: int, dream_id: int, week_start: date,
                         tasks_completed: int, tasks_total: int) -> ProgressSnapshot:
    """Create this week's snapshot, or update it if it already exists."""
    snapshot = db.scalar(select(ProgressSnapshot).where(
        ProgressSnapshot.user_id == user_id,
        ProgressSnapshot.dream_id == dream_id,
        ProgressSnapshot.week_start == week_start,
    ))
    if snapshot is None:
        snapshot = ProgressSnapshot(user_id=user_id, dream_id=dream_id, week_start=week_start)
        db.add(snapshot)
    snapshot.tasks_completed = tasks_completed
    snapshot.tasks_total = tasks_total
    db.commit()
    db.refresh(snapshot)
    return snapshot


def list_snapshots(db: Session, user_id: int, dream_id: int) -> list[ProgressSnapshot]:
    """All weekly snapshots of a dream, oldest first (good for a line graph)."""
    return list(db.scalars(
        select(ProgressSnapshot)
        .where(ProgressSnapshot.user_id == user_id, ProgressSnapshot.dream_id == dream_id)
        .order_by(ProgressSnapshot.week_start)
    ))