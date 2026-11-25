"""
session.py  (M1 Database, owner: Ananya)

What it is for:
    Connects the app to the database and gives out database "sessions".
    A session is one conversation with the database.

Who uses it:
    init_db.py, the repositories, and Riya's FastAPI routers (via get_db).

What it contains:
    engine         - the connection to the database.
    SessionLocal   - a factory that makes new sessions.
    get_db()       - gives one session to a request and closes it after.

Note:
    The database address comes from Riya's shared settings
    (settings.database_url in app/config.py, set in the .env file).
    So everyone on the team uses the same address.
    To switch to PostgreSQL later: change DATABASE_URL in .env and install
    the PostgreSQL driver. This has NOT been tested on PostgreSQL yet.
    Importing this file loads the settings, which need SECRET_KEY and
    GEMINI_API_KEY in the environment or in .env.
"""

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

from app.config import settings

# Database address from the shared settings. Default: sqlite:///./aspira.db
DATABASE_URL = settings.database_url

# SQLite needs this option because FastAPI uses more than one thread.
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args)


@event.listens_for(engine, "connect")
def enable_sqlite_foreign_keys(dbapi_connection, connection_record):
    """SQLite ignores foreign keys unless we switch them on for each connection."""
    if DATABASE_URL.startswith("sqlite"):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")  # needed so ON DELETE CASCADE works
        cursor.close()


# autoflush=False and autocommit=False: we save only when we call commit().
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def get_db():
    """Give one session to a request, then always close it."""
    db = SessionLocal()
    try:
        yield db  # the request uses the session here
    finally:
        db.close()  # runs even if an error happened