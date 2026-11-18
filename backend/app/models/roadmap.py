"""
roadmap.py  (M1 Database, owner: Ananya)

What it is for:
    The "roadmaps" table: one row per roadmap of a dream. A roadmap is either
    made by the AI or entered by the user (the synopsis supports both).

Who uses it:
    roadmap_repository.py, analytics_repository.py.

What it contains:
    Roadmap - columns: id, dream_id, title, summary, source, created_at.

Note:
    When a dream is deleted, its roadmaps are deleted too (ondelete CASCADE).
"""

from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Roadmap(Base):
    __tablename__ = "roadmaps"

    id: Mapped[int] = mapped_column(primary_key=True)
    dream_id: Mapped[int] = mapped_column(
        ForeignKey("dreams.id", ondelete="CASCADE"), index=True
    )
    title: Mapped[str] = mapped_column(String(200))
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    source: Mapped[str] = mapped_column(String(20), default="ai")  # "ai" or "user"
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )