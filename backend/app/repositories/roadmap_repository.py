"""
roadmap_repository.py  (M1 Database, owner: Ananya)

What it is for:
    All database reads and writes for "roadmaps" and their "milestones".

Who uses it:
    Riya's roadmap_generator.py and roadmap_regenerator.py (through services).

What it contains:
    create_roadmap(db, dream_id, title, summary=None, source="ai") -> Roadmap
    get_roadmap(db, roadmap_id) -> Roadmap or None
    list_roadmaps(db, dream_id) -> list of Roadmap
    delete_roadmap(db, roadmap_id) -> True if deleted, False if not found
    add_milestone(db, roadmap_id, title, description=None, order_index=0,
                  target_date=None) -> Milestone
    list_milestones(db, roadmap_id) -> list of Milestone, in order
"""

from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.milestone import Milestone
from app.models.roadmap import Roadmap


def create_roadmap(db: Session, dream_id: int, title: str,
                   summary: str | None = None, source: str = "ai") -> Roadmap:
    """Save a new roadmap. source is "ai" or "user"."""
    roadmap = Roadmap(dream_id=dream_id, title=title, summary=summary, source=source)
    db.add(roadmap)
    db.commit()
    db.refresh(roadmap)
    return roadmap


def get_roadmap(db: Session, roadmap_id: int) -> Roadmap | None:
    """Find one roadmap by id."""
    return db.get(Roadmap, roadmap_id)


def list_roadmaps(db: Session, dream_id: int) -> list[Roadmap]:
    """All roadmaps of one dream, newest first."""
    return list(db.scalars(
        select(Roadmap).where(Roadmap.dream_id == dream_id).order_by(Roadmap.id.desc())
    ))


def delete_roadmap(db: Session, roadmap_id: int) -> bool:
    """Delete a roadmap and, by cascade, its milestones and tasks."""
    roadmap = db.get(Roadmap, roadmap_id)
    if roadmap is None:
        return False
    db.delete(roadmap)
    db.commit()
    return True


def add_milestone(db: Session, roadmap_id: int, title: str,
                  description: str | None = None, order_index: int = 0,
                  target_date: date | None = None) -> Milestone:
    """Add one milestone to a roadmap."""
    milestone = Milestone(roadmap_id=roadmap_id, title=title, description=description,
                          order_index=order_index, target_date=target_date)
    db.add(milestone)
    db.commit()
    db.refresh(milestone)
    return milestone


def list_milestones(db: Session, roadmap_id: int) -> list[Milestone]:
    """Milestones of one roadmap, in their planned order."""
    return list(db.scalars(
        select(Milestone).where(Milestone.roadmap_id == roadmap_id)
        .order_by(Milestone.order_index, Milestone.id)
    ))