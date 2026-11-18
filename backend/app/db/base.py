"""
base.py  (M1 Database, owner: Ananya)

What it is for:
    Defines the one shared "Base" class. Every database table (model)
    in backend/app/models/ inherits from it.

Who uses it:
    All model files (user.py, dream.py, roadmap.py, ...) and init_db.py.

What it contains:
    Base - the parent class that SQLAlchemy uses to collect all tables.
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Parent class for all tables. It has no columns of its own."""
    pass  # SQLAlchemy keeps a list of every table that inherits from Base