"""
task.py  (M1 Database, owner: Ananya)

What it is for:
    The "tasks" table: small steps inside a milestone. Each task has a type
    (which decides what evidence is needed) and a status.

Who uses it:
    task_repository.py, analytics_repository.py, and Sonali's task_schema.py
    (its field names must match this model).

What it contains:
    Task - columns: id, milestone_id, title, task_type, status, due_date,
    description, estimated_hours.

Note:
    Allowed task_type: project, course, learning, practical.
    Allowed status: pending, submitted, completed, overdue.
    These lists live in Sonali's app/utils/constants.py; the model only
    stores the text, and the schema checks it.
"""

from datetime import date

from sqlalchemy import Date, Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(primary_key=True)
    milestone_id: Mapped[int] = mapped_column(
        ForeignKey("milestones.id", ondelete="CASCADE"), index=True  # deleted with its milestone
    )
    title: Mapped[str] = mapped_column(String(200))
    task_type: Mapped[str] = mapped_column(String(20))  # project / course / learning / practical
    status: Mapped[str] = mapped_column(String(20), default="pending")  # new tasks start as pending
    due_date: Mapped[date] = mapped_column(Date)  # TaskCreate requires a due date
    description: Mapped[str | None] = mapped_column(Text, nullable=True)  # AI-written explanation of the task
    estimated_hours: Mapped[float | None] = mapped_column(Float, nullable=True)  # AI estimate of time needed