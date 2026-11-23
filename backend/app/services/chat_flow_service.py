"""Database side of the career chatbot: builds the learner's context and saves the conversation.

chat_service.py talks to Gemini and is database-free. This file feeds it and stores the result:

* prepare_chat   – finds the dream the question is about (the given one, or the user's newest),
                   builds the ``ChatContext`` (career, level, roadmap title, next tasks, progress)
                   and loads the recent history through Ananya's chat_repository.
* save_exchange  – stores the user message and the assistant reply in ONE transaction.
* history        – the saved messages, oldest first, for the chat window.

Only answered, in-scope exchanges are saved: refused or blocked messages (including prompt-injection
attempts) never pollute the history that is sent back to the model on the next question.
"""
from __future__ import annotations

import json
from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.models.chat_message import ChatMessage
from app.repositories import chat_repository, dream_repository, roadmap_repository, task_repository
from app.services.chat_service import ChatContext, ChatTurn
from app.services.roadmap_service import get_owned_dream
from app.utils.constants import TASK_COMPLETED

HISTORY_ROWS = 30  # rows fetched; chat_service trims further to the character budget


@dataclass
class ChatPrep:
    ctx: ChatContext
    history: list[ChatTurn]


def _level_from_roadmap(roadmap) -> str:
    raw = getattr(roadmap, "intake_json", None)
    if raw:
        try:
            return str(json.loads(raw).get("current_level", "not specified"))
        except (ValueError, AttributeError):
            pass
    return "not specified"


def prepare_chat(db: Session, user_id: int, dream_id: int | None) -> ChatPrep:
    if dream_id is not None:
        dream = get_owned_dream(db, user_id, dream_id)
    else:
        dreams = dream_repository.list_dreams(db, user_id)  # newest first
        dream = dreams[0] if dreams else None

    ctx = ChatContext(career=dream.title if dream else "not specified yet")
    if dream is not None:
        roadmaps = roadmap_repository.list_roadmaps(db, dream.id)
        if roadmaps:
            latest = roadmaps[0]
            tasks = task_repository.list_tasks_for_roadmap(db, latest.id)
            open_tasks = sorted((t for t in tasks if t.status != TASK_COMPLETED), key=lambda t: t.due_date)
            ctx.roadmap_title = latest.title
            ctx.level = _level_from_roadmap(latest)
            ctx.upcoming_tasks = [t.title for t in open_tasks[:6]]
            ctx.total_count = len(tasks)
            ctx.completed_count = len(tasks) - len(open_tasks)

    rows = chat_repository.list_messages(db, user_id, dream_id, limit=HISTORY_ROWS)
    history = [ChatTurn(role="user" if m.role == "user" else "assistant", text=m.content) for m in rows]
    return ChatPrep(ctx=ctx, history=history)


def save_exchange(db: Session, user_id: int, dream_id: int | None, user_text: str, reply_text: str) -> None:
    try:
        db.add_all([
            ChatMessage(user_id=user_id, dream_id=dream_id, role="user", content=user_text),
            ChatMessage(user_id=user_id, dream_id=dream_id, role="assistant", content=reply_text),
        ])
        db.commit()
    except Exception:
        db.rollback()
        raise


def history(db: Session, user_id: int, dream_id: int | None, limit: int = 50) -> list[ChatMessage]:
    if dream_id is not None:
        get_owned_dream(db, user_id, dream_id)
    return chat_repository.list_messages(db, user_id, dream_id, limit=max(1, min(limit, 200)))
