import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest
from sqlalchemy import delete, func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker

import crud
import models  # noqa: F401
from database import Base, make_engine
from models import Dream, Task, TaskStatus, User

SAMPLE = [
    {"title": "Learn Python", "tasks": [{"title": "Finish basics"}, {"title": "Build a CLI app"}]},
    {"title": "Learn DSA", "tasks": [{"title": "Arrays"}, {"title": "Trees"}]},
]


@pytest.fixture()
def db():
    engine = make_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine, expire_on_commit=False)()
    yield session
    session.close()


def _setup(db, email="a@x.com"):
    user = crud.create_user(db, "A", email, "hash")
    dream = crud.create_dream(db, user.id, "SDE")
    crud.save_roadmap(db, dream.id, SAMPLE)
    return user, dream


def test_unique_email(db):
    crud.create_user(db, "A", "a@x.com", "h")
    with pytest.raises(IntegrityError):
        crud.create_user(db, "B", "A@X.com", "h")


def test_user_limit(db, monkeypatch):
    monkeypatch.setattr(crud, "MAX_USERS", 1)
    crud.create_user(db, "A", "a@x.com", "h")
    with pytest.raises(ValueError):
        crud.create_user(db, "B", "b@x.com", "h")


def test_regenerate_keeps_history_and_one_active(db):
    _, dream = _setup(db)
    crud.save_roadmap(db, dream.id, SAMPLE)
    versions = db.execute(select(models.Roadmap.version, models.Roadmap.is_active)).all()
    assert sorted(versions) == [(1, False), (2, True)]


def test_deleting_dream_cascades_to_tasks(db):
    user, dream = _setup(db)
    assert crud.delete_dream(db, user.id, dream.id) is True
    assert db.scalar(select(func.count(Task.id))) == 0


def test_db_level_cascade_works_with_raw_delete(db):
    _setup(db)
    db.execute(delete(User))
    db.commit()
    assert db.scalar(select(func.count(Task.id))) == 0
    assert db.scalar(select(func.count(Dream.id))) == 0


def test_user_cannot_touch_another_users_data(db):
    user1, dream1 = _setup(db, "a@x.com")
    user2 = crud.create_user(db, "B", "b@x.com", "h")
    task_id = db.scalar(select(Task.id))
    assert crud.set_task_status(db, user2.id, task_id, TaskStatus.FINISHED) is False
    assert crud.delete_dream(db, user2.id, dream1.id) is False


def test_readiness_score_and_weekly_progress(db):
    user, dream = _setup(db)
    assert crud.readiness_score(db, user.id, dream.id) == 0.0
    task_ids = list(db.scalars(select(Task.id)))
    crud.set_task_status(db, user.id, task_ids[0], TaskStatus.FINISHED)
    assert crud.readiness_score(db, user.id, dream.id) == 25.0
    assert sum(n for _, n in crud.weekly_completed(db, user.id, dream.id)) == 1


def test_journal(db):
    user, _ = _setup(db)
    crud.add_journal_entry(db, user.id, "Day 1 done")
    assert len(crud.list_journal_entries(db, user.id)) == 1