"""
analytics_service.py - calculations for the weekly progress graph (feature 7).

PURPOSE
    Turns a dream's tasks into one row per week, showing how many tasks
    were due and how many were completed. The result matches the
    WeeklyAnalyticsResponse shape in analytics_schema.py, which Tanushree's
    chart reads.

FUNCTIONS
    build_weekly_progress(tasks)             -> list of WeeklyProgress, oldest week first
    weekly_for_dream(db, user_id, dream_id)  -> the full response for one dream

RULES
    - A task counts as "completed" only when its status is "completed",
      meaning its proof was accepted. Tasks that are only "submitted"
      do not count yet.
    - Only the NEWEST roadmap of the dream is counted. Ananya's Roadmap
      table has no "active" flag, so the roadmap with the highest id is
      treated as the current one. Counting older roadmaps too would count
      the same goals twice after a regeneration.
    - The dream must belong to the user, otherwise NotFoundError (404).

WHO USES IT
    - analytics_router.py -> sends the result to the website
"""

from app.repositories import roadmap_repository, task_repository   # Ananya's database functions
from app.schemas.analytics_schema import WeeklyAnalyticsResponse, WeeklyProgress
from app.services import dream_service                              # checks the dream is the user's
from app.utils.constants import TASK_COMPLETED                      # the "completed" status word
from app.utils.date_utils import get_week_start                     # finds the Monday of a week


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


def weekly_for_dream(db, user_id: int, dream_id: int) -> WeeklyAnalyticsResponse:
    """Return the weekly progress of one of this user's dreams."""
    dream_service.get_dream(db, user_id, dream_id)      # 404 if missing or not theirs
    roadmaps = roadmap_repository.list_roadmaps(db, dream_id=dream_id)
    if roadmaps:
        newest = max(roadmaps, key=lambda r: r.id)      # the current roadmap
        tasks = task_repository.list_tasks_for_roadmap(db, roadmap_id=newest.id)
    else:
        tasks = []                                      # no roadmap yet, so no weeks
    return WeeklyAnalyticsResponse(dream_id=dream_id, weeks=build_weekly_progress(tasks))