"""
journal_entry.py  (M1 Database, owner: Ananya)

What it is for:
    The "journal_entries" table: a user's reflections and learning notes.

Who uses it:
    journal_repository.py.

What it contains:
    JournalEntry - columns: id, user_id, dream_id (optional), content, created_at.
"""

from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class JournalEntry(Base):
    __tablename__ = "journal_entries"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    dream_id: Mapped[int | None] = mapped_column(
        ForeignKey("dreams.id", ondelete="SET NULL"), nullable=True  # entry may be general
    )
    content: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )