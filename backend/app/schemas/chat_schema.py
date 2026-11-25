"""
chat_schema.py - data shapes for the career chatbot (feature 3).

PURPOSE
    Defines what the user sends to the chatbot and what comes back.

SCHEMAS
    ChatRequest         -> input: the user's message, optionally tied to a dream
    ChatResponse        -> output: the chatbot's reply
    ChatMessageResponse -> output: one saved message in the chat history

WHO USES IT
    - chat_router.py and chat_service.py (Riya)
    - Tanushree's chatApi.js and ChatWindow component

NOTE
    Field names must match Ananya's ChatMessage model (chat_message.py).
    The rule that the chatbot answers career topics only is enforced in
    scope_guard.py, not here.
"""

from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=1500)   # the user's question
    dream_id: int | None = None   # optional: the dream the question is about


class ChatResponse(BaseModel):
    reply: str    # what the chatbot says back


class ChatMessageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)   # read data from a database object

    id: int                 # unique number of the message
    role: str               # "user" or "assistant"
    content: str            # the message text
    created_at: datetime    # when it was sent