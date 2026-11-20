"""
user.py  (M1 Database, owner: Ananya)

What it is for:
    The "users" table: one row per registered person.

Who uses it:
    user_repository.py, and Riya's auth_service.py (through the repository).

What it contains:
    User - columns: id, full_name, email, hashed_password, created_at.

Note:
    We store only the HASH of the password, never the real password.
"""

from datetime import datetime, timezone

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    full_name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)  # one account per email
    hashed_password: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )