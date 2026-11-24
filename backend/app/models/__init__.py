"""
models package  (M1 Database, owner: Ananya)

What it is for:
    Importing this package registers ALL 8 tables with Base.
    SQLAlchemy needs every table known before it can resolve a
    ForeignKey (for example dreams.user_id -> users.id).

Who uses it:
    Everything. Any import like "from app.models.dream import Dream"
    runs this file first.
"""

from app.models import (  # noqa: F401  (imported only to register the tables)
    chat_message,
    dream,
    journal_entry,
    milestone,
    progress_snapshot,
    roadmap,
    task,
    user,
)