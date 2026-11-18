"""
chat_message.py  (M1 Database, owner: Ananya)

What it is for:
    The "chat_messages" table: the career chatbot conversation history.

Who uses it:
    chat_repository.py.

What it contains:
    ChatMessage - columns: id, user_id, dream_id (optional), role, content, created_at.

Note:
    role is "user" for the person and "assistant" for the chatbot.
"""

from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    dream_id: Mapped[int | None] = mapped_column(
        ForeignKey("dreams.id", ondelete="SET NULL"), nullable=True
    )
    role: Mapped[str] = mapped_column(String(20))  # "user" or "assistant"
    content: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )