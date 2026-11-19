"""
milestone.py  (M1 Database, owner: Ananya)

What it is for:
    The "milestones" table: big steps inside a roadmap. Each milestone
    holds many tasks.

Who uses it:
    roadmap_repository.py, task_repository.py.

What it contains:
    Milestone - columns: id, roadmap_id, title, description, order_index, target_date.
"""

from datetime import date

from sqlalchemy import Date, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Milestone(Base):
    __tablename__ = "milestones"

    id: Mapped[int] = mapped_column(primary_key=True)
    roadmap_id: Mapped[int] = mapped_column(
        ForeignKey("roadmaps.id", ondelete="CASCADE"), index=True
    )
    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    order_index: Mapped[int] = mapped_column(default=0)  # position inside the roadmap
    target_date: Mapped[date | None] = mapped_column(Date, nullable=True)