"""
seed_data.py  (M1 Database, owner: Ananya)

What it is for:
    Adds a demo user, dream, roadmap, 2 milestones and 7 tasks in all four
    statuses (completed, submitted, pending, overdue) with different due dates,
    so the weekly graph and the task screens have something to show.

Who uses it:
    You and Sonali, from the terminal. Not used by the live app.

What it contains:
    seed() - adds the demo rows only if the database has no users yet.

How to run (from the backend/ folder):
    python -m app.db.seed_data

Note:
    The password below is NOT a real password. It is a placeholder, because
    hashing belongs to Riya's security.py. Do not use this user to log in.
    Due dates are counted from today, so the demo always looks current.
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

        m1 = Milestone(roadmap_id=roadmap.id, title="Learn Python basics", order_index=1)
        m2 = Milestone(roadmap_id=roadmap.id, title="Build and show projects", order_index=2)
        db.add_all([m1, m2])
        db.flush()

        today = date.today()

        # (milestone, title, type, status, days from today; minus = in the past)
        demo_tasks = [
            (m1, "Finish a Python course", "course", "completed", -20),
            (m1, "Practise loops and functions", "learning", "completed", -13),
            (m1, "Solve 10 practice problems", "practical", "completed", -6),
            (m1, "Take the Python quiz", "learning", "overdue", -9),
            (m2, "Build a small Python project", "project", "submitted", -2),
            (m2, "Put the project on GitHub", "project", "pending", 7),
            (m2, "Make a project demo screenshot", "practical", "pending", 14),
        ]
        for milestone, title, task_type, status, days in demo_tasks:
            db.add(Task(
                milestone_id=milestone.id,
                title=title,
                task_type=task_type,
                status=status,
                due_date=today + timedelta(days=days),
            ))

        db.commit()  # save everything at once
        print("Demo data added.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()