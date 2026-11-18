from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from models import (Dream, JournalEntry, Milestone, Roadmap, Task, TaskStatus,
                    User)

MAX_USERS = 50  # MVP limit


# ---------- users ----------
def create_user(db: Session, name: str, email: str, password_hash: str) -> User:
    if db.scalar(select(func.count(User.id))) >= MAX_USERS:
        raise ValueError("User limit reached")
    user = User(name=name, email=email.lower().strip(), password_hash=password_hash)
    db.add(user)
    db.commit()
    return user


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.scalar(select(User).where(User.email == email.lower().strip()))


def delete_user(db: Session, user_id: int) -> None:
    user = db.get(User, user_id)
    if user:
        db.delete(user)
        db.commit()


# ---------- dreams ----------
def create_dream(db: Session, user_id: int, title: str) -> Dream:
    dream = Dream(user_id=user_id, title=title)
    db.add(dream)
    db.commit()
    return dream


def list_dreams(db: Session, user_id: int) -> list[Dream]:
    return list(db.scalars(select(Dream).where(Dream.user_id == user_id)))


def delete_dream(db: Session, user_id: int, dream_id: int) -> bool:
    dream = db.scalar(select(Dream).where(Dream.id == dream_id, Dream.user_id == user_id))
    if not dream:
        return False
    db.delete(dream)
    db.commit()
    return True


# ---------- roadmaps ----------
def save_roadmap(db: Session, dream_id: int, milestones: list[dict], answers_json: str | None = None) -> Roadmap:
    """milestones = [{"title": "...", "tasks": [{"title": "...", "description": "..."}]}, ...]"""
    latest = db.scalar(select(func.max(Roadmap.version)).where(Roadmap.dream_id == dream_id)) or 0
    for old in db.scalars(select(Roadmap).where(Roadmap.dream_id == dream_id, Roadmap.is_active)):
        old.is_active = False

    roadmap = Roadmap(dream_id=dream_id, version=latest + 1, answers_json=answers_json, is_active=True)
    for i, m in enumerate(milestones):
        ms = Milestone(title=m["title"], order_index=i)
        ms.tasks = [Task(title=t["title"], description=t.get("description")) for t in m.get("tasks", [])]
        roadmap.milestones.append(ms)
    db.add(roadmap)
    db.commit()
    return roadmap


def get_active_roadmap(db: Session, dream_id: int) -> Roadmap | None:
    return db.scalar(select(Roadmap).where(Roadmap.dream_id == dream_id, Roadmap.is_active))


# ---------- tasks & progress ----------
def set_task_status(db: Session, user_id: int, task_id: int, status: TaskStatus) -> bool:
    task = db.scalar(
        select(Task)
        .join(Milestone).join(Roadmap).join(Dream)
        .where(Task.id == task_id, Dream.user_id == user_id)
    )
    if not task:
        return False
    task.status = status
    task.completed_at = datetime.now(timezone.utc) if status == TaskStatus.FINISHED else None
    db.commit()
    return True


def readiness_score(db: Session, user_id: int, dream_id: int) -> float:
    rows = db.execute(
        select(Task.status, func.count(Task.id))
        .join(Milestone).join(Roadmap).join(Dream)
        .where(Dream.id == dream_id, Dream.user_id == user_id, Roadmap.is_active)
        .group_by(Task.status)
    ).all()
    counts = {status: n for status, n in rows}
    total = sum(counts.values())
    if total == 0:
        return 0.0
    return round(100 * counts.get(TaskStatus.FINISHED, 0) / total, 1)


def weekly_completed(db: Session, user_id: int, dream_id: int) -> list[tuple[str, int]]:
    week = func.strftime("%Y-%W", Task.completed_at)  # PostgreSQL pe date_trunc('week', ...) use karna
    return list(
        db.execute(
            select(week, func.count(Task.id))
            .join(Milestone).join(Roadmap).join(Dream)
            .where(Dream.id == dream_id, Dream.user_id == user_id, Task.completed_at.is_not(None))
            .group_by(week).order_by(week)
        ).all()
    )


# ---------- journal ----------
def add_journal_entry(db: Session, user_id: int, content: str, dream_id: int | None = None) -> JournalEntry:
    entry = JournalEntry(user_id=user_id, dream_id=dream_id, content=content)
    db.add(entry)
    db.commit()
    return entry


def list_journal_entries(db: Session, user_id: int) -> list[JournalEntry]:
    return list(
        db.scalars(
            select(JournalEntry)
            .where(JournalEntry.user_id == user_id)
            .order_by(JournalEntry.created_at.desc())
        )
    )