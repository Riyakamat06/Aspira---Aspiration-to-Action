"""
fake_repository.py - an in-memory stand-in for the database, for TESTS ONLY.

PURPOSE
    Lets the dream and journal services be tested before Ananya's
    database code exists. Records live in a Python dictionary and are
    wiped when the program stops. It is kept in tests/ so it can never
    be mistaken for real application code.

METHODS
    create(**fields) -> saves a record, gives it an id and a created_at
    get(item_id)     -> returns the record, or None if it does not exist
    list_all()       -> returns every record as a list
    delete(item_id)  -> removes the record; True if it existed, else False

NOTE FOR THE REAL DATABASE
    Ananya's repositories need methods with these same four names,
    returning objects with an .id, so the services work unchanged.
"""

from datetime import datetime       # used to stamp when a record was created
from types import SimpleNamespace   # a simple object whose fields are read with a dot


class InMemoryRepository:
    def __init__(self):
        self._items = {}    # maps an id number -> the saved record
        self._next_id = 1   # the id the next saved record will get

    def create(self, **fields):
        # build a record with an id, a timestamp and the fields given
        item = SimpleNamespace(id=self._next_id, created_at=datetime.now(), **fields)
        self._items[self._next_id] = item   # save it under its id
        self._next_id += 1                  # so the next record gets a new id
        return item

    def get(self, item_id):
        # .get() gives None instead of an error when the id is missing
        return self._items.get(item_id)

    def list_all(self):
        # a new list, so callers cannot change the store by accident
        return list(self._items.values())

    def delete(self, item_id):
        # pop removes the record and returns it, or None if it was missing
        return self._items.pop(item_id, None) is not None