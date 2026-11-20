"""
journal_router.py - web addresses (endpoints) for journal entries (feature 6).

ENDPOINTS
    POST /journal              -> add an entry (reply 201; 404 if the
                                  dream it names is missing or not theirs)
    GET  /journal              -> list this user's entries, newest first
    GET  /journal?dream_id=1   -> only the entries for one dream

WHO USES IT
    - Tanushree's journalApi.js, JournalPage and JournalEditor
    - main.py must include it: app.include_router(journal_router.router)

NOTE
    The current user comes from get_current_user_id() in dream_router.py
    (temporary: the demo user, until Riya's login is in main).
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.routers.dream_router import get_current_user_id
from app.schemas.journal_schema import JournalCreate, JournalResponse
from app.services import journal_service

router = APIRouter(prefix="/journal", tags=["Journal"])


@router.post("", response_model=JournalResponse, status_code=status.HTTP_201_CREATED)
def add_entry(data: JournalCreate, db: Session = Depends(get_db),
              user_id: int = Depends(get_current_user_id)):
    # the service checks that the dream exists and is theirs when a dream_id is given
    return journal_service.create_entry(db, user_id, data)


@router.get("", response_model=list[JournalResponse])
def list_all_entries(dream_id: int | None = None, db: Session = Depends(get_db),
                     user_id: int = Depends(get_current_user_id)):
    # dream_id is optional; without it, every entry of this user is returned
    return journal_service.list_entries(db, user_id, dream_id)
