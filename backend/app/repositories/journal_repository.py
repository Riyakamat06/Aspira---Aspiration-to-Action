"""
journal_repository.py  (M1 Database, owner: Ananya)

What it is for:
    All database reads and writes for the "journal_entries" table.

Who uses it:
    Sonali's journal_service.py.

What it contains:
    create_entry(db, user_id, content, dream_id=None) -> JournalEntry
    get_entry(db, entry_id, user_id) -> JournalEntry or None
    list_entries(db, user_id) -> list of JournalEntry
    delete_entry(db, entry_id, user_id) -> True if deleted, False if not found

Note:
    Every function asks for user_id, so users only see their own journal.
"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.journal_entry import JournalEntry


def create_entry(db: Session, user_id: int, content: str, dream_id: int | None = None) -> JournalEntry:
    """Save a new journal entry."""
    entry = JournalEntry(user_id=user_id, dream_id=dream_id, content=content)
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


def get_entry(db: Session, entry_id: int, user_id: int) -> JournalEntry | None:
    """Find one entry, only if it belongs to this user."""
    return db.scalar(select(JournalEntry).where(
        JournalEntry.id == entry_id, JournalEntry.user_id == user_id))


def list_entries(db: Session, user_id: int) -> list[JournalEntry]:
    """All entries of this user, newest first."""
    return list(db.scalars(
        select(JournalEntry).where(JournalEntry.user_id == user_id)
        .order_by(JournalEntry.id.desc())
    ))


def delete_entry(db: Session, entry_id: int, user_id: int) -> bool:
    """Delete one entry of this user."""
    entry = get_entry(db, entry_id, user_id)
    if entry is None:
        return False
    db.delete(entry)
    db.commit()
    return True