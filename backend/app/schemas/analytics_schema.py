"""
analytics_schema.py - data shapes for the weekly progress analysis (feature 7).

PURPOSE
    Defines the data the backend sends for the weekly progress graph.
    This is the agreed "contract" with Tanushree (M3), who draws the
    chart from exactly these fields. Changing a field name here breaks
    her chart, so tell her before changing anything.

SCHEMAS
    WeeklyProgress          -> one week: its Monday, tasks due, tasks completed
    WeeklyAnalyticsResponse -> a dream's id and the list of weeks

WHO USES IT
    - analytics_router.py  -> the output of the weekly analytics endpoint
    - analytics_service.py -> builds the list of weeks
    - Tanushree's analyticsApi.js and ProgressChart.jsx -> read this shape

EXAMPLE OF THE DATA SENT
    {"dream_id": 1, "weeks": [
        {"week_start": "2026-11-16", "tasks_due": 5, "tasks_completed": 3}
    ]}
"""

from datetime import date          # a calendar day
from pydantic import BaseModel     # BaseModel = a checked data form


class WeeklyProgress(BaseModel):
    week_start: date        # the Monday that starts this week
    tasks_due: int          # how many tasks were due that week
    tasks_completed: int    # how many of them were completed with accepted proof


class WeeklyAnalyticsResponse(BaseModel):
    dream_id: int                  # which dream these weeks belong to
    weeks: list[WeeklyProgress]    # one item per week, oldest first