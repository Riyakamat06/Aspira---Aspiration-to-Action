"""
dream_service.py - business logic for dreams (goals), part of feature 9.

PURPOSE
    Creates, finds, lists and deletes a user's dreams. A user can keep
    several dreams at once and can delete any of them.

    The functions never create their own storage. They receive a `repo`
    (storage helper) as a parameter. In tests it is an in-memory
    stand-in; in the app it will be Ananya's database repository.
    These functions do not change when that happens.

FUNCTIONS
    create_dream(repo, data)     -> saves a new dream, returns it
    get_dream(repo, dream_id)    -> returns the dream, or raises NotFoundError
    list_dreams(repo)            -> returns all dreams
    delete_dream(repo, dream_id) -> removes a dream, or raises NotFoundError

WHO USES IT
    - dream_router.py    -> calls these functions for each endpoint
    - journal_service.py -> uses get_dream to check that a dream exists

KNOWN GAP
    Deleting a dream does not yet delete its roadmaps, tasks or journal
    entries. That depends on Ananya's database rules.
"""

from app.core.exceptions import NotFoundError      # the shared "not found" error
from app.schemas.dream_schema import DreamCreate   # the checked input shape


def create_dream(repo, data: DreamCreate):
    """Save a new dream and return it."""
    # take the checked title and description and ask the repo to save them
    return repo.create(title=data.title, description=data.description)


def get_dream(repo, dream_id: int):
    """Return one dream, or raise NotFoundError if it does not exist."""
    dream = repo.get(dream_id)          # ask the repo; it gives None if missing
    if dream is None:
        raise NotFoundError("Dream")    # reply: "Dream not found" (status 404)
    return dream


def list_dreams(repo):
    """Return every saved dream."""
    return repo.list_all()


def delete_dream(repo, dream_id: int):
    """Delete a dream, or raise NotFoundError if it does not exist."""
    # repo.delete returns False when the id was not found
    if not repo.delete(dream_id):
        raise NotFoundError("Dream")