"""
dream.py  (M1 Database, owner: Ananya)

What it is for:
    The "dreams" table: one row per career goal. A user can have many dreams.

Who uses it:
    dream_repository.py, roadmap_repository.py.

What it contains:
    Dream - columns: id, user_id, title, description, status, created_at.

Note:
    ondelete="CASCADE" means: when a user is deleted, their dreams are deleted too.
"""

from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Dream(Base):
    __tablename__ = "dreams"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True  # owner of this dream
    )
    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="active")
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )