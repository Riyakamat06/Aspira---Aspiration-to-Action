"""
journal_service.py - business logic for journal entries (feature 6).

PURPOSE
    Saves and lists the reflections a user writes along their journey,
    using Ananya's journal_repository. An entry can be general, or linked
    to one of the user's dreams. If it is linked to a dream, that dream
    must exist and belong to the same user.

FUNCTIONS
    create_entry(db, user_id, data)               -> saves an entry
    list_entries(db, user_id, dream_id=None)      -> entries, newest first;
                                                     only one dream's entries
                                                     if dream_id is given

WHO USES IT
    - journal_router.py -> calls these functions for each endpoint
"""

from app.repositories import journal_repository        # Ananya's database functions
from app.schemas.journal_schema import JournalCreate   # the checked input shape
from app.services.dream_service import get_dream       # checks the dream is the user's


def create_entry(db, user_id: int, data: JournalCreate):
    """Save a journal entry, checking its dream belongs to the user if one is given."""
    if data.dream_id is not None:
        # raises NotFoundError("Dream") if the dream is missing or someone else's
        get_dream(db, user_id, data.dream_id)
    return journal_repository.create_entry(
        db, user_id=user_id, content=data.content, dream_id=data.dream_id
    )


def list_entries(db, user_id: int, dream_id: int | None = None):
    """Return this user's entries newest first, optionally only for one dream."""
    entries = journal_repository.list_entries(db, user_id=user_id)
    if dream_id is not None:                                # filter if a dream was asked for
        entries = [e for e in entries if e.dream_id == dream_id]
    # a higher id means a newer entry, so sort high to low
    return sorted(entries, key=lambda e: e.id, reverse=True)