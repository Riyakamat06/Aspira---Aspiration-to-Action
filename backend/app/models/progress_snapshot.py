"""
progress_snapshot.py  (M1 Database, owner: Ananya)

What it is for:
    The "progress_snapshots" table: one row per dream per week, used for
    the weekly progress graph.

Who uses it:
    analytics_repository.py, and Riya's/Sonali's analytics and readiness services.

What it contains:
    ProgressSnapshot - columns: id, user_id, dream_id, week_start,
    tasks_completed, tasks_total.
"""

from datetime import date

from sqlalchemy import Date, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class ProgressSnapshot(Base):
    __tablename__ = "progress_snapshots"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    dream_id: Mapped[int] = mapped_column(
        ForeignKey("dreams.id", ondelete="CASCADE"), index=True
    )
    week_start: Mapped[date] = mapped_column(Date)  # Monday of that week
    tasks_completed: Mapped[int] = mapped_column(default=0)
    tasks_total: Mapped[int] = mapped_column(default=0)