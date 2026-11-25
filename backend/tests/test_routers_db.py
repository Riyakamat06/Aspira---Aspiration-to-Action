"""
test_routers_db.py - tests for Sonali's four routers against a REAL (temporary) database.

PURPOSE
    Runs the dream, journal, task and analytics endpoints through FastAPI
    on top of Ananya's models and repositories. The database is a fresh
    SQLite database in memory for every test, so aspira.db is never
    touched and tests cannot affect each other. Two users exist in every
    test, so we can prove that one user cannot see or change another
    user's data (SRS DR-01).

WHAT IS TESTED
    Dreams:    add, list, view, delete, empty title, missing, other user's dream
    Journal:   add, list (newest first), filter by dream, unknown or other user's dream
    Tasks:     view, allowed status change, "completed" refused (SRS FR-EV-01),
               unknown status, other user's task, missing task
    Analytics: weekly counts, only the newest roadmap counts, no roadmap, other user's dream
    Cascade:   deleting a dream removes its tasks (SRS DR-02)

NOT TESTED HERE
    Login (the demo user is replaced per test by choosing a user id),
    evidence, readiness and the roadmap generator.

HOW TO RUN
    cd backend
    pytest tests/test_routers_db.py -v

NOTE
    These tests are written by the author of the routers. The team rule is that
    nobody tests their own code, so Riya should review them (they do not replace
    an independent review).
"""

import os

# settings the app needs when config is loaded; evidence is required by default (SRS FR-EV-01)
os.environ.setdefault("SECRET_KEY", "test-secret-key-for-tests-only-0000")
os.environ.setdefault("GEMINI_API_KEY", "fake-key-not-real")
os.environ["EVIDENCE_REQUIRED"] = "true"

from datetime import date
from types import SimpleNamespace

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.session import get_db
import app.models.chat_message      # noqa: F401  (the models must be imported so their tables exist)
import app.models.dream             # noqa: F401
import app.models.journal_entry     # noqa: F401
import app.models.milestone         # noqa: F401
import app.models.progress_snapshot # noqa: F401
import app.models.roadmap           # noqa: F401
import app.models.task              # noqa: F401
import app.models.user              # noqa: F401
from app.repositories import (
    dream_repository, roadmap_repository, task_repository, user_repository,
)
from app.routers import analytics_router, dream_router, journal_router, task_router
from app.routers.dream_router import get_current_user_id
from app.core.exceptions import InvalidInputError
from app.services import task_service
from app.config import settings  # the real settings object (switched in the fixture at the end of this file)


@pytest.fixture
def env():
    # a fresh database in memory; StaticPool keeps one connection so every session sees the same data
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False},
                           poolclass=StaticPool)

    @event.listens_for(engine, "connect")
    def _foreign_keys_on(connection, _record):
        cursor = connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")   # needed so deleting a dream cascades
        cursor.close()

    Base.metadata.create_all(bind=engine)           # create every table
    Session = sessionmaker(bind=engine, autoflush=False, autocommit=False)

    db = Session()                                  # the test's own session, for setting up data
    user_repository.create_user(db, full_name="User One", email="one@example.com", hashed_password="x")
    user_repository.create_user(db, full_name="User Two", email="two@example.com", hashed_password="x")

    current = {"id": 1}                             # which user is "logged in"; tests change it

    api = FastAPI()
    for module in (dream_router, journal_router, task_router, analytics_router):
        api.include_router(module.router)

    def override_get_db():
        session = Session()                         # one session per request, like the real app
        try:
            yield session
        finally:
            session.close()

    api.dependency_overrides[get_db] = override_get_db
    api.dependency_overrides[get_current_user_id] = lambda: current["id"]

    yield SimpleNamespace(client=TestClient(api), db=db, current=current)

    db.close()
    engine.dispose()


def add_roadmap(db, dream_id, rows):
    """Create a roadmap with one milestone and one task per (due_date, status) row."""
    roadmap = roadmap_repository.create_roadmap(db, dream_id=dream_id, title="Roadmap")
    milestone = roadmap_repository.add_milestone(db, roadmap_id=roadmap.id, title="Milestone")
    tasks = []
    for due, status in rows:
        task = task_repository.create_task(db, milestone_id=milestone.id, title="Task",
                                           task_type="project", due_date=due)
        if status != "pending":                     # new tasks start as pending
            task_repository.update_task_status(db, task_id=task.id, status=status)
        tasks.append(task)
    return tasks


# ---------------------------------------------------------------- dreams

def test_dream_add_list_view_and_delete(env):
    c = env.client
    created = c.post("/dreams", json={"title": "Become an engineer", "description": "Backend"})
    assert created.status_code == 201
    dream_id = created.json()["id"]
    assert created.json()["title"] == "Become an engineer"
    assert len(c.get("/dreams").json()) == 1
    assert c.get(f"/dreams/{dream_id}").status_code == 200
    assert c.delete(f"/dreams/{dream_id}").status_code == 204
    assert c.get(f"/dreams/{dream_id}").status_code == 404


def test_empty_dream_title_is_rejected(env):
    assert env.client.post("/dreams", json={"title": ""}).status_code == 422


def test_missing_dream_is_404(env):
    assert env.client.get("/dreams/999").status_code == 404


def test_user_cannot_see_or_delete_another_users_dream(env):
    dream_id = env.client.post("/dreams", json={"title": "Mine"}).json()["id"]
    env.current["id"] = 2                           # now user two is logged in
    assert env.client.get(f"/dreams/{dream_id}").status_code == 404
    assert env.client.get("/dreams").json() == []
    assert env.client.delete(f"/dreams/{dream_id}").status_code == 404
    env.current["id"] = 1                           # back to user one: the dream is still there
    assert env.client.get(f"/dreams/{dream_id}").status_code == 200


# ---------------------------------------------------------------- journal

def test_journal_add_list_newest_first_and_filter(env):
    c = env.client
    dream_id = c.post("/dreams", json={"title": "Goal"}).json()["id"]
    assert c.post("/journal", json={"content": "first", "dream_id": dream_id}).status_code == 201
    assert c.post("/journal", json={"content": "second"}).status_code == 201   # a general entry
    assert [e["content"] for e in c.get("/journal").json()] == ["second", "first"]
    assert [e["content"] for e in c.get(f"/journal?dream_id={dream_id}").json()] == ["first"]


def test_journal_entry_for_unknown_dream_is_404(env):
    assert env.client.post("/journal", json={"content": "x", "dream_id": 999}).status_code == 404


def test_journal_entry_for_another_users_dream_is_404(env):
    dream_id = env.client.post("/dreams", json={"title": "Mine"}).json()["id"]
    env.current["id"] = 2
    assert env.client.post("/journal", json={"content": "x", "dream_id": dream_id}).status_code == 404


# ---------------------------------------------------------------- tasks

def make_task(env, status="pending"):
    dream = dream_repository.create_dream(env.db, user_id=1, title="Goal")
    return dream, add_roadmap(env.db, dream.id, [(date(2026, 11, 17), status)])[0]


def test_task_can_be_viewed_and_moved_to_submitted(env):
    _, task = make_task(env)
    viewed = env.client.get(f"/tasks/{task.id}")
    assert viewed.status_code == 200 and viewed.json()["status"] == "pending"
    moved = env.client.patch(f"/tasks/{task.id}/status", json={"status": "submitted"})
    assert moved.status_code == 200 and moved.json()["status"] == "submitted"


def test_task_cannot_be_completed_by_request(env):
    _, task = make_task(env)
    # SRS FR-EV-01: only accepted evidence may complete a task
    assert env.client.patch(f"/tasks/{task.id}/status", json={"status": "completed"}).status_code == 400


def test_unknown_status_word_is_422(env):
    _, task = make_task(env)
    assert env.client.patch(f"/tasks/{task.id}/status", json={"status": "done"}).status_code == 422


def test_completed_task_stays_completed(env):
    _, task = make_task(env, status="completed")
    assert env.client.patch(f"/tasks/{task.id}/status", json={"status": "pending"}).status_code == 400


def test_user_cannot_read_or_change_another_users_task(env):
    _, task = make_task(env)
    env.current["id"] = 2
    assert env.client.get(f"/tasks/{task.id}").status_code == 404
    assert env.client.patch(f"/tasks/{task.id}/status", json={"status": "submitted"}).status_code == 404
    env.current["id"] = 1                           # the owner still sees it, unchanged
    assert env.client.get(f"/tasks/{task.id}").json()["status"] == "pending"


def test_missing_task_is_404(env):
    assert env.client.get("/tasks/999").status_code == 404


# ---------------------------------------------------------------- analytics

def test_weekly_counts_due_and_completed(env):
    dream = dream_repository.create_dream(env.db, user_id=1, title="Goal")
    add_roadmap(env.db, dream.id, [
        (date(2026, 11, 17), "completed"),
        (date(2026, 11, 18), "pending"),
        (date(2026, 11, 24), "completed"),
    ])
    weeks = env.client.get(f"/analytics/weekly/{dream.id}").json()["weeks"]
    assert weeks == [
        {"week_start": "2026-11-16", "tasks_due": 2, "tasks_completed": 1},
        {"week_start": "2026-11-23", "tasks_due": 1, "tasks_completed": 1},
    ]


def test_weekly_counts_only_the_newest_roadmap(env):
    dream = dream_repository.create_dream(env.db, user_id=1, title="Goal")
    add_roadmap(env.db, dream.id, [(date(2026, 11, 17), "completed"), (date(2026, 11, 18), "completed")])  # old
    add_roadmap(env.db, dream.id, [(date(2026, 11, 19), "pending")])                                        # newest
    weeks = env.client.get(f"/analytics/weekly/{dream.id}").json()["weeks"]
    assert weeks == [{"week_start": "2026-11-16", "tasks_due": 1, "tasks_completed": 0}]


def test_weekly_for_a_dream_with_no_roadmap_is_empty(env):
    dream = dream_repository.create_dream(env.db, user_id=1, title="Goal")
    assert env.client.get(f"/analytics/weekly/{dream.id}").json()["weeks"] == []


def test_weekly_for_another_users_dream_is_404(env):
    dream = dream_repository.create_dream(env.db, user_id=1, title="Goal")
    env.current["id"] = 2
    assert env.client.get(f"/analytics/weekly/{dream.id}").status_code == 404


# ---------------------------------------------------------------- cascade

def test_deleting_a_dream_removes_its_tasks(env):
    dream, task = make_task(env)
    assert env.client.delete(f"/dreams/{dream.id}").status_code == 204
    assert env.client.get(f"/tasks/{task.id}").status_code == 404   # the task went with it (SRS DR-02)

# ---------------------------------------------------------------- evidence switch

def test_with_evidence_required_completed_is_refused_at_service_level(env):
    _, task = make_task(env)
    with pytest.raises(InvalidInputError):
        task_service.change_task_status(env.db, 1, task.id, "completed", evidence_required=True)


def test_without_evidence_a_task_can_be_finished_and_reopened(env):
    _, task = make_task(env)
    task_service.change_task_status(env.db, 1, task.id, "completed", evidence_required=False)
    assert env.client.get(f"/tasks/{task.id}").json()["status"] == "completed"
    task_service.change_task_status(env.db, 1, task.id, "pending", evidence_required=False)
    assert env.client.get(f"/tasks/{task.id}").json()["status"] == "pending"


@pytest.mark.parametrize("start", ["overdue", "submitted"])
def test_without_evidence_overdue_and_submitted_tasks_can_be_finished(env, start):
    _, task = make_task(env, status=start)
    task_service.change_task_status(env.db, 1, task.id, "completed", evidence_required=False)
    assert env.client.get(f"/tasks/{task.id}").json()["status"] == "completed"


def test_without_evidence_another_users_task_is_still_404(env):
    _, task = make_task(env)
    with pytest.raises(Exception) as error:
        task_service.change_task_status(env.db, 2, task.id, "completed", evidence_required=False)
    assert error.value.status_code == 404


@pytest.fixture(autouse=True)
def evidence_required_by_default(monkeypatch):
    # a developer's .env may say EVIDENCE_REQUIRED=false (the demo setting);
    # these tests check the rule of SRS FR-EV-01, so switch it on for every test in this file.
    # The 5 switch tests pass True or False directly and do not depend on this.
    monkeypatch.setattr(settings, "evidence_required", True)
