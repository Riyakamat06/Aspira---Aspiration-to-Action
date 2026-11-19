"""
task_repository.py  (M1 Database, owner: Ananya)

What it is for:
    All database reads and writes for the "tasks" table.

Who uses it:
    Sonali's task_service.py.

What it contains:
    create_task(db, milestone_id, title, task_type, due_date) -> Task
    get_task(db, task_id) -> Task or None  (no owner check)
    get_task_for_user(db, task_id, user_id) -> Task or None  (owner checked)
    list_tasks_for_milestone(db, milestone_id) -> list of Task
    list_tasks_for_roadmap(db, roadmap_id) -> list of Task
    update_task_status(db, task_id, status) -> Task or None

Note:
    This file does not check if a status or type is allowed. The schema
    (task_schema.py) and the service do that before calling here.
    To stop one user reading another user's task, the service should call
    get_task_for_user first.
"""

from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.dream import Dream
from app.models.milestone import Milestone
from app.models.roadmap import Roadmap
from app.models.task import Task


def create_task(db: Session, milestone_id: int, title: str,
                task_type: str, due_date: date) -> Task:
    """Save a new task. Its status starts as "pending"."""
    task = Task(milestone_id=milestone_id, title=title, task_type=task_type, due_date=due_date)
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


def get_task(db: Session, task_id: int) -> Task | None:
    """Find one task by id. Does NOT check who owns it."""
    return db.get(Task, task_id)


def get_task_for_user(db: Session, task_id: int, user_id: int) -> Task | None:
    """Find one task only if it belongs to this user (task -> milestone -> roadmap -> dream)."""
    return db.scalar(
        select(Task)
        .join(Milestone, Task.milestone_id == Milestone.id)
        .join(Roadmap, Milestone.roadmap_id == Roadmap.id)
        .join(Dream, Roadmap.dream_id == Dream.id)
        .where(Task.id == task_id, Dream.user_id == user_id)
    )


def list_tasks_for_milestone(db: Session, milestone_id: int) -> list[Task]:
    """Tasks of one milestone, earliest deadline first."""
    return list(db.scalars(
        select(Task).where(Task.milestone_id == milestone_id).order_by(Task.due_date, Task.id)
    ))


def list_tasks_for_roadmap(db: Session, roadmap_id: int) -> list[Task]:
    """All tasks of a roadmap (joins tasks with milestones)."""
    return list(db.scalars(
        select(Task).join(Milestone, Task.milestone_id == Milestone.id)
        .where(Milestone.roadmap_id == roadmap_id)
        .order_by(Milestone.order_index, Task.due_date, Task.id)
    ))


def update_task_status(db: Session, task_id: int, status: str) -> Task | None:
    """Change a task's status. Returns None if the task does not exist."""
    task = db.get(Task, task_id)
    if task is None:
        return None
    task.status = status
    db.commit()
    db.refresh(task)
    return task