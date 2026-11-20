"""
init_db.py  (M1 Database, owner: Ananya)

What it is for:
    Creates all database tables. Run it once before starting the app.

Who uses it:
    You (from the terminal), and Riya's main.py if she wants tables
    created at startup.

What it contains:
    init_db() - creates every table that inherits from Base.

How to run (from the backend/ folder):
    python -m app.db.init_db
"""

from app.db.base import Base
from app.db.session import engine

# These imports look unused, but they are needed.
# Importing a model file tells Base about that table.
from app.models import (  # noqa: F401
    chat_message,
    dream,
    journal_entry,
    milestone,
    progress_snapshot,
    roadmap,
    task,
    user,
)


def init_db() -> None:
    """Create every table that does not exist yet."""
    Base.metadata.create_all(bind=engine)  # safe to run again: existing tables are kept


if __name__ == "__main__":
    init_db()
    print("Database tables created.")