"""
date_utils.py - small date helpers used for weekly analytics and re-planning.

PURPOSE
    Holds the date rules in one place so they are written once and
    tested once. These functions use only dates. They never touch the
    database, so they are easy to test.

FUNCTIONS
    get_week_start(day)         -> the Monday of the week that contains `day`
    is_overdue(due_date, today) -> True if the due date is before today
    shift_date(due_date, days)  -> the due date moved by a number of days

WHO USES IT
    - analytics_service.py -> get_week_start groups completed tasks by week
                              for the weekly progress graph
    - replan_service.py    -> is_overdue finds late tasks and shift_date
                              moves their deadlines (a later feature)

EXAMPLE
    get_week_start(date(2026, 11, 18))  ->  date(2026, 11, 16)  (a Monday)
"""

from datetime import date, timedelta   # date = a calendar day; timedelta = a number of days


def get_week_start(day: date) -> date:
    """Return the Monday of the week that contains `day`."""
    # weekday() gives 0 for Monday, 1 for Tuesday ... 6 for Sunday.
    # Subtracting that many days always lands on that week's Monday.
    return day - timedelta(days=day.weekday())


def is_overdue(due_date: date, today: date | None = None) -> bool:
    """Return True if `due_date` is earlier than today."""
    # If no "today" is given, use the real date. Tests can pass a fake one.
    if today is None:
        today = date.today()
    # A task due today is not overdue yet; only earlier dates count.
    return due_date < today


def shift_date(due_date: date, days: int) -> date:
    """Return `due_date` moved by `days` (a negative number moves it earlier)."""
    return due_date + timedelta(days=days)