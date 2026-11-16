"""
journal_service.py - business logic for journal entries (feature 6).

PURPOSE
    Saves and lists the reflections a user writes along their journey.
    An entry can be general, or linked to one of the user's dreams. If
    it is linked to a dream, that dream must exist.

FUNCTIONS
    create_entry(journal_repo, dream_repo, data) -> saves an entry
    list_entries(journal_repo, dream_id=None)    -> entries, newest first;
                                                    only one dream's entries
                                                    if dream_id is given

WHO USES IT
    - journal_router.py -> calls these functions for each endpoint

NOTE
    Like dream_service, the storage helpers are passed in as parameters,
    so the real database can replace the in-memory stand-in later
    without changing this file.
"""

from app.schemas.journal_schema import JournalCreate   # the checked input shape
from app.services.dream_service import get_dream       # reused to check a dream exists


def create_entry(journal_repo, dream_repo, data: JournalCreate):
    """Save a journal entry, checking its dream exists if one is given."""
    if data.dream_id is not None:
        # get_dream raises NotFoundError("Dream") if the dream is missing,
        # so an entry can never point at a dream that does not exist
        get_dream(dream_repo, data.dream_id)
    return journal_repo.create(content=data.content, dream_id=data.dream_id)


def list_entries(journal_repo, dream_id: int | None = None):
    """Return entries newest first, optionally only for one dream."""
    entries = journal_repo.list_all()                      # every saved entry
    if dream_id is not None:                               # filter if a dream was asked for
        entries = [e for e in entries if e.dream_id == dream_id]
    # a higher id means a newer entry, so sort high to low
    return sorted(entries, key=lambda e: e.id, reverse=True)