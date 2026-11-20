"""
dream_repository.py  (M1 Database, owner: Ananya)

What it is for:
    All database reads and writes for the "dreams" table (career goals).

Who uses it:
    Sonali's dream_service.py.

What it contains:
    create_dream(db, user_id, title, description=None) -> Dream
    get_dream(db, dream_id, user_id) -> Dream or None
    list_dreams(db, user_id) -> list of Dream
    delete_dream(db, dream_id, user_id) -> True if deleted, False if not found

Note:
    Every function asks for user_id, so one user can never see another
    user's dreams (per-user data isolation).
"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.dream import Dream


def create_dream(db: Session, user_id: int, title: str, description: str | None = None) -> Dream:
    """Save a new dream for this user."""
    dream = Dream(user_id=user_id, title=title, description=description)
    db.add(dream)
    db.commit()
    db.refresh(dream)
    return dream


def get_dream(db: Session, dream_id: int, user_id: int) -> Dream | None:
    """Find one dream, only if it belongs to this user."""
    return db.scalar(select(Dream).where(Dream.id == dream_id, Dream.user_id == user_id))


def list_dreams(db: Session, user_id: int) -> list[Dream]:
    """All dreams of this user, newest first."""
    return list(db.scalars(
        select(Dream).where(Dream.user_id == user_id).order_by(Dream.id.desc())
    ))


def delete_dream(db: Session, dream_id: int, user_id: int) -> bool:
    """Delete one dream and, by cascade, its roadmaps, milestones and tasks."""
    dream = get_dream(db, dream_id, user_id)
    if dream is None:
        return False
    db.delete(dream)
    db.commit()
    return True