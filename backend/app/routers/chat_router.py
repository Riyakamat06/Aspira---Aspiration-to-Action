"""Career chatbot endpoints (feature 3). Login required; limited per user per minute.

    POST /chat           {"message", "dream_id"?} -> {"reply", "in_scope", "blocked", "notices"}
    POST /chat/stream    same input; Server-Sent Events: lines ``data: {json}`` with
                         {"kind": "delta", "text"} ... then {"kind": "done", "notices": [...]}
                         or {"kind": "refused", "text"} / {"kind": "error", "text"}.
    GET  /chat/history?dream_id=&limit=   saved messages, oldest first (Sonali's ChatMessageResponse)

The model answers career topics only; anything else gets a polite refusal. Only answered, in-scope
exchanges are saved. Streaming lets the UI show the reply word by word. In the streaming endpoint the
exchange is saved with its own short-lived database session, because the request's session may already
be closed while the stream is still running.
"""
import json

from fastapi import APIRouter, Depends, Query
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import StreamingResponse

from app.config import settings
from app.db.session import SessionLocal
from app.dependencies import chat_rate_limit, get_current_user, get_db
from app.models.user import User
from app.schemas.chat_schema import ChatMessageResponse, ChatRequest, ChatResponse
from app.services import chat_flow_service, chat_service
from app.services.ai_client import AIBlockedError, AIError
from app.services.scope_guard import normalise

router = APIRouter(prefix="/chat", tags=["Chat"])


class ChatReplyResponse(ChatResponse):
    """Sonali's ChatResponse plus flags the UI can use (refusal styling, disclaimer chips)."""
    in_scope: bool = True
    blocked: bool = False
    notices: list[str] = []


def _save_in_new_session(user_id: int, dream_id, question: str, answer: str) -> None:
    with SessionLocal() as session:
        chat_flow_service.save_exchange(session, user_id, dream_id, question, answer)


@router.post("", response_model=ChatReplyResponse, dependencies=[Depends(chat_rate_limit)])
async def chat(data: ChatRequest, user: User = Depends(get_current_user), db=Depends(get_db)):
    user_id = user.id
    prep = await run_in_threadpool(chat_flow_service.prepare_chat, db, user_id, data.dream_id)
    result = await chat_service.reply(data.message, prep.history, prep.ctx)
    if result.in_scope and not result.blocked:
        question = normalise(data.message, max_chars=settings.chat_message_max_chars)
        await run_in_threadpool(chat_flow_service.save_exchange, db, user_id, data.dream_id, question, result.text)
    return ChatReplyResponse(reply=result.text, in_scope=result.in_scope, blocked=result.blocked,
                             notices=result.notices)


def _sse(payload: dict) -> str:
    return f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"


@router.post("/stream", dependencies=[Depends(chat_rate_limit)])
async def chat_stream(data: ChatRequest, user: User = Depends(get_current_user), db=Depends(get_db)):
    user_id = user.id
    prep = await run_in_threadpool(chat_flow_service.prepare_chat, db, user_id, data.dream_id)
    question = normalise(data.message, max_chars=settings.chat_message_max_chars)

    async def events():
        parts: list[str] = []
        try:
            async for ev in chat_service.stream_reply(data.message, prep.history, prep.ctx):
                if ev.kind == "delta":
                    parts.append(ev.text)
                elif ev.kind == "done":
                    await run_in_threadpool(_save_in_new_session, user_id, data.dream_id, question, "".join(parts))
                yield _sse(ev.model_dump())
        except AIBlockedError:
            yield _sse({"kind": "error", "text": "This request could not be processed. Try rephrasing."})
        except AIError:
            yield _sse({"kind": "error", "text": "The AI service is busy. Please try again shortly."})

    return StreamingResponse(events(), media_type="text/event-stream",
                             headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})


@router.get("/history", response_model=list[ChatMessageResponse])
def get_history(dream_id: int | None = Query(default=None), limit: int = Query(default=50, ge=1, le=200),
                user: User = Depends(get_current_user), db=Depends(get_db)):
    return chat_flow_service.history(db, user.id, dream_id, limit)
