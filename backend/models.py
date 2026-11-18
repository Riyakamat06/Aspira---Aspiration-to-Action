import enum
from datetime import date, datetime, timezone
from typing import Optional

from sqlalchemy import (Boolean, Date, DateTime, Enum, ForeignKey, Integer,
                        String, Text, UniqueConstraint)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


def _now() -> datetime:
    return datetime.now(timezone.utc)


class TaskStatus(str, enum.Enum):
    INCOMPLETE = "Incomplete"
    FINISHED = "Finished"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)

    dreams: Mapped[list["Dream"]] = relationship(
        back_populates="user", cascade="all, delete-orphan", passive_deletes=True
    )
    journal_entries: Mapped[list["JournalEntry"]] = relationship(
        back_populates="user", cascade="all, delete-orphan", passive_deletes=True
    )


class Dream(Base):
    __tablename__ = "dreams"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    title: Mapped[str] = mapped_column(String(200))
    status: Mapped[str] = mapped_column(String(20), default="active")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)

    user: Mapped["User"] = relationship(back_populates="dreams")
    roadmaps: Mapped[list["Roadmap"]] = relationship(
        back_populates="dream", cascade="all, delete-orphan", passive_deletes=True
    )
    journal_entries: Mapped[list["JournalEntry"]] = relationship(
        back_populates="dream", passive_deletes=True
    )


class Roadmap(Base):
    __tablename__ = "roadmaps"
    __table_args__ = (UniqueConstraint("dream_id", "version", name="uq_roadmap_dream_version"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    dream_id: Mapped[int] = mapped_column(ForeignKey("dreams.id", ondelete="CASCADE"), index=True)
    version: Mapped[int] = mapped_column(Integer, default=1)
    answers_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    generated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)

    dream: Mapped["Dream"] = relationship(back_populates="roadmaps")
    milestones: Mapped[list["Milestone"]] = relationship(
        back_populates="roadmap", cascade="all, delete-orphan", passive_deletes=True,
        order_by="Milestone.order_index",
    )


class Milestone(Base):
    __tablename__ = "milestones"

    id: Mapped[int] = mapped_column(primary_key=True)
    roadmap_id: Mapped[int] = mapped_column(ForeignKey("roadmaps.id", ondelete="CASCADE"), index=True)
    title: Mapped[str] = mapped_column(String(200))
    order_index: Mapped[int] = mapped_column(Integer, default=0)
    target_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    roadmap: Mapped["Roadmap"] = relationship(back_populates="milestones")
    tasks: Mapped[list["Task"]] = relationship(
        back_populates="milestone", cascade="all, delete-orphan", passive_deletes=True
    )


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(primary_key=True)
    milestone_id: Mapped[int] = mapped_column(ForeignKey("milestones.id", ondelete="CASCADE"), index=True)
    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[TaskStatus] = mapped_column(Enum(TaskStatus), default=TaskStatus.INCOMPLETE)
    due_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    milestone: Mapped["Milestone"] = relationship(back_populates="tasks")


class JournalEntry(Base):
    __tablename__ = "journal_entries"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    dream_id: Mapped[Optional[int]] = mapped_column(ForeignKey("dreams.id", ondelete="SET NULL"), nullable=True)
    content: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)

    user: Mapped["User"] = relationship(back_populates="journal_entries")
    dream: Mapped[Optional["Dream"]] = relationship(back_populates="journal_entries")