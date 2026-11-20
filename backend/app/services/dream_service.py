"""
dream_service.py - business logic for dreams (goals), part of feature 9.

PURPOSE
    Creates, finds, lists and deletes a user's dreams, using Ananya's
    dream_repository. Every function takes the database session `db` and
    the owner's `user_id`, so a user can only see and change their own
    dreams (SRS DR-01).

FUNCTIONS
    create_dream(db, user_id, data)     -> saves a new dream, returns it
    get_dream(db, user_id, dream_id)    -> returns the dream, or raises NotFoundError
    list_dreams(db, user_id)            -> returns the user's dreams
    delete_dream(db, user_id, dream_id) -> removes a dream and everything under
                                           it (the database cascades the delete,
                                           SRS DR-02), or raises NotFoundError

WHO USES IT
    - dream_router.py    -> calls these functions for each endpoint
    - journal_service.py -> uses get_dream to check that a dream exists

NOTE
    The repository functions are called with keyword arguments on purpose:
    their argument order differs between functions (create_dream takes
    user_id first, get_dream takes dream_id first).
"""

from app.core.exceptions import NotFoundError        # the shared "not found" error
from app.repositories import dream_repository        # Ananya's database functions
from app.schemas.dream_schema import DreamCreate     # the checked input shape


def create_dream(db, user_id: int, data: DreamCreate):
    """Save a new dream for this user and return it."""
    return dream_repository.create_dream(
        db, user_id=user_id, title=data.title, description=data.description
    )


def get_dream(db, user_id: int, dream_id: int):
    """Return one of this user's dreams, or raise NotFoundError."""
    dream = dream_repository.get_dream(db, dream_id=dream_id, user_id=user_id)
    if dream is None:                   # missing, or it belongs to someone else
        raise NotFoundError("Dream")    # reply: "Dream not found" (status 404)
    return dream


def list_dreams(db, user_id: int):
    """Return every dream that belongs to this user."""
    return dream_repository.list_dreams(db, user_id=user_id)


def delete_dream(db, user_id: int, dream_id: int):
    """Delete one of this user's dreams, or raise NotFoundError."""
    # the repository returns False when the dream was not found for this user
    if not dream_repository.delete_dream(db, dream_id=dream_id, user_id=user_id):
        raise NotFoundError("Dream")