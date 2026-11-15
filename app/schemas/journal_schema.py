"""
journal_schema.py - data shapes for journal entries (feature 6).

PURPOSE
    Defines what data is accepted when a user writes a journal entry
    (a reflection on their journey) and what is sent back.

SCHEMAS
    JournalCreate   -> input: the text of the entry, and optionally which
                       dream it is about
    JournalResponse -> output: the saved entry with its id and date

WHO USES IT
    - journal_router.py  -> input and output of the journal endpoints
    - journal_service.py -> receives the checked data

NOTE
    Field names must match Ananya's JournalEntry model (journal_entry.py).
"""

from datetime import datetime                      # a date plus a time of day
from pydantic import BaseModel, ConfigDict, Field  # BaseModel = a checked data form


class JournalCreate(BaseModel):
    # the entry's text; must not be empty, and is limited to 5000 characters
    content: str = Field(min_length=1, max_length=5000)
    # optional: the dream this entry is about; None means a general entry
    dream_id: int | None = None


class JournalResponse(BaseModel):
    # lets Pydantic read data straight from a database object
    model_config = ConfigDict(from_attributes=True)

    id: int                      # unique number of the entry
    content: str                 # the entry's text
    dream_id: int | None = None  # the dream it belongs to, if any
    created_at: datetime         # when the entry was written