"""
journal_router.py - web addresses (endpoints) for journal entries (feature 6).

ENDPOINTS
    POST /journal              -> add an entry (reply 201; 404 if the
                                  dream it names does not exist)
    GET  /journal              -> list entries, newest first
    GET  /journal?dream_id=1   -> only the entries for one dream

WHO USES IT
    - Tanushree's journalApi.js, JournalPage and JournalEditor
    - main.py must include it: app.include_router(journal_router.router)

THE PLACE THAT CHANGES LATER
    get_journal_repo() is where Ananya's journal repository plugs in.
    The dream check reuses get_dream_repo() from dream_router.py.
"""

from fastapi import APIRouter, Depends, status

from app.routers.dream_router import get_dream_repo          # reused, one place to connect
from app.schemas.journal_schema import JournalCreate, JournalResponse
from app.services import journal_service

router = APIRouter(prefix="/journal", tags=["Journal"])


def get_journal_repo():
    # TO DO: return Ananya's journal repository once it exists
    raise NotImplementedError("Connect the journal repository from M1 here")


@router.post("", response_model=JournalResponse, status_code=status.HTTP_201_CREATED)
def add_entry(
    data: JournalCreate,
    journal_repo=Depends(get_journal_repo),
    dream_repo=Depends(get_dream_repo),
):
    # the service checks that the dream exists when a dream_id is given
    return journal_service.create_entry(journal_repo, dream_repo, data)


@router.get("", response_model=list[JournalResponse])
def list_all_entries(dream_id: int | None = None, journal_repo=Depends(get_journal_repo)):
    # dream_id is optional; without it, every entry is returned
    return journal_service.list_entries(journal_repo, dream_id)