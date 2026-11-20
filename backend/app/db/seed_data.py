"""
seed_data.py  (M1 Database, owner: Ananya)

What it is for:
    Adds a small demo user, dream, roadmap, milestone and task, so the
    app and the tests have starter data to look at.

Who uses it:
    You, from the terminal. Not used by the live app.

What it contains:
    seed() - adds the demo rows only if the database has no users yet.

How to run (from the backend/ folder):
    python -m app.db.seed_data

Note:
    The password below is NOT a real password. It is a placeholder, because
    hashing belongs to Riya's security.py. Do not use this user to log in.
"""

from datetime import date, timedelta

from app.db.init_db import init_db
from app.db.session import SessionLocal
from app.models.dream import Dream
from app.models.milestone import Milestone
from app.models.roadmap import Roadmap
from app.models.task import Task
from app.models.user import User


def seed() -> None:
    """Add demo rows once. If a user already exists, do nothing."""
    init_db()  # make sure the tables exist first
    db = SessionLocal()
    try:
        if db.query(User).first() is not None:
            print("Database already has data. Nothing added.")
            return

        user = User(
            full_name="Demo Student",
            email="demo@aspira.test",
            hashed_password="not-a-real-hash",  # placeholder only
        )
        db.add(user)
        db.flush()  # gives user.id without saving for good yet

        dream = Dream(user_id=user.id, title="Get placed as a software engineer")
        db.add(dream)
        db.flush()

        roadmap = Roadmap(dream_id=dream.id, title="Placement roadmap", source="ai")
        db.add(roadmap)
        db.flush()

        milestone = Milestone(roadmap_id=roadmap.id, title="Learn Python basics", order_index=1)
        db.add(milestone)
        db.flush()

        task = Task(
            milestone_id=milestone.id,
            title="Build a small Python project",
            task_type="project",
            due_date=date.today() + timedelta(days=14),
        )
        db.add(task)

        db.commit()  # save everything at once
        print("Demo data added.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()