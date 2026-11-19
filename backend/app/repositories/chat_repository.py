"""
chat_repository.py  (M1 Database, owner: Ananya)

What it is for:
    All database reads and writes for the "chat_messages" table.

Who uses it:
    Riya's chat_service.py.

What it contains:
    add_message(db, user_id, role, content, dream_id=None) -> ChatMessage
    list_messages(db, user_id, dream_id=None, limit=50) -> list of ChatMessage,
        oldest first (the last `limit` messages)

Note:
    role is "user" or "assistant".
"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.chat_message import ChatMessage


def add_message(db: Session, user_id: int, role: str, content: str,
                dream_id: int | None = None) -> ChatMessage:
    """Save one chat message."""
    message = ChatMessage(user_id=user_id, dream_id=dream_id, role=role, content=content)
    db.add(message)
    db.commit()
    db.refresh(message)
    return message


def list_messages(db: Session, user_id: int, dream_id: int | None = None,
                  limit: int = 50) -> list[ChatMessage]:
    """The latest `limit` messages, returned oldest first so they read in order."""
    query = select(ChatMessage).where(ChatMessage.user_id == user_id)
    if dream_id is not None:
        query = query.where(ChatMessage.dream_id == dream_id)
    latest = db.scalars(query.order_by(ChatMessage.id.desc()).limit(limit)).all()
    return list(reversed(latest))  # flip to oldest-first