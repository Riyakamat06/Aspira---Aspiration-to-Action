"""
dream_schema.py - data shapes for creating and returning dreams (goals).

PURPOSE
    Defines what data the app accepts when a user adds a dream, and what
    it sends back. Pydantic checks the data automatically, so bad input
    is rejected before it reaches the service code.

SCHEMAS
    DreamCreate   -> what the user SENDS: a title and an optional description
    DreamResponse -> what the app SENDS BACK: the saved dream, with its id

WHO USES IT
    - dream_router.py  -> uses DreamCreate for input, DreamResponse for output
    - dream_service.py -> receives the checked DreamCreate data

NOTE
    Field names must match Ananya's Dream database model (dream.py).
    If her names differ, change them here.
"""

from datetime import datetime                      # a date plus a time of day
from pydantic import BaseModel, ConfigDict, Field  # BaseModel = a checked data form


class DreamCreate(BaseModel):
    # the dream's name; must have 1 to 200 characters (empty titles are rejected)
    title: str = Field(min_length=1, max_length=200)
    # optional extra detail; None means the user did not give one
    description: str | None = None


class DreamResponse(BaseModel):
    # from_attributes lets Pydantic read data straight from a database object
    model_config = ConfigDict(from_attributes=True)

    id: int                          # unique number the database gave this dream
    title: str                       # the dream's name
    description: str | None = None   # optional detail
    created_at: datetime             # when the dream was added