"""
analytics_service.py - calculations for the weekly progress graph (feature 7).

PURPOSE
    Turns a list of tasks into one row per week, showing how many tasks
    were due and how many were completed. The result matches the
    WeeklyProgress shape in analytics_schema.py, which Tanushree's chart reads.

    This first version contains only the calculation, which needs no
    database. Later, a small function will fetch the tasks through
    Ananya's analytics_repository and pass them in here.

FUNCTIONS
    build_weekly_progress(tasks) -> a list of WeeklyProgress, oldest week first

INPUT
    `tasks` is any list of objects that have two attributes:
        due_date -> a date
        status   -> a status word from constants.py

RULE
    A task counts as "completed" only when its status is "completed",
    meaning its proof was accepted. Tasks that are only "submitted"
    do not count yet.

WHO USES IT
    - analytics_router.py -> sends the result to the website
    - readiness_service.py -> may reuse the counts
"""

from app.schemas.analytics_schema import WeeklyProgress   # the agreed output shape
from app.utils.constants import TASK_COMPLETED            # the "completed" status word
from app.utils.date_utils import get_week_start           # finds the Monday of a week


def build_weekly_progress(tasks) -> list[WeeklyProgress]:
    """Group tasks by the week they were due and count them."""
    weeks = {}   # maps a Monday date -> {"due": count, "completed": count}

    for task in tasks:                                  # look at every task once
        monday = get_week_start(task.due_date)          # which week was it due in?
        if monday not in weeks:                         # first task seen for this week
            weeks[monday] = {"due": 0, "completed": 0}  # start both counts at zero
        weeks[monday]["due"] += 1                       # every task counts as due
        if task.status == TASK_COMPLETED:               # only accepted proof counts
            weeks[monday]["completed"] += 1

    result = []
    for monday in sorted(weeks):                        # sorted = oldest week first
        result.append(
            WeeklyProgress(
                week_start=monday,
                tasks_due=weeks[monday]["due"],
                tasks_completed=weeks[monday]["completed"],
            )
        )
    return result