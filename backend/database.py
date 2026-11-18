from sqlalchemy import create_engine, event
from sqlalchemy.orm import DeclarativeBase, sessionmaker

DATABASE_URL = "sqlite:///./aspira.db"


class Base(DeclarativeBase):
    pass


def make_engine(url: str = DATABASE_URL):
    engine = create_engine(
        url,
        connect_args={"check_same_thread": False} if url.startswith("sqlite") else {},
    )

    if url.startswith("sqlite"):
        @event.listens_for(engine, "connect")
        def _fk_on(dbapi_conn, _record):
            cur = dbapi_conn.cursor()
            cur.execute("PRAGMA foreign_keys=ON")  # SQLite me ye ON na ho toh cascade delete nahi chalta
            cur.close()

    return engine


engine = make_engine()
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def get_db():
    """FastAPI dependency: ek request = ek session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()