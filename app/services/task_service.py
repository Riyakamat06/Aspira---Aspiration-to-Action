"""
task_service.py - business rules for tasks.

PURPOSE
    Holds the rules about how a task's status may change. This first
    version contains only the rules, which need no database. The
    database parts (finding and saving tasks) are added once Ananya's
    Task model and repository are available.

FUNCTIONS
    can_change_status(current, new) -> True if the move is allowed
    check_status_change(current, new) -> raises an error if not allowed

STATUS RULES (from constants.py)
    pending   -> submitted (proof given) or missed (due date passed)
    submitted -> completed (proof accepted) or pending (proof rejected)
    missed    -> pending (deadline moved) or submitted (late proof)
    completed -> no further changes; a finished task stays finished

WHY THE RULES EXIST
    Without them, a user could mark a task "completed" without giving
    proof. This is the core idea of the project: progress is based on
    evidence, not on claims.

WHO USES IT
    - task_router.py -> calls check_status_change before saving a change
"""

from app.core.exceptions import InvalidInputError   # the shared "bad request" error
from app.utils.constants import (                    # the shared status words
    TASK_PENDING,
    TASK_SUBMITTED,
    TASK_COMPLETED,
    TASK_MISSED,
)

# For each status, the list of statuses it is allowed to change to.
ALLOWED_CHANGES = {
    TASK_PENDING: [TASK_SUBMITTED, TASK_MISSED],     # not started -> proof given, or late
    TASK_SUBMITTED: [TASK_COMPLETED, TASK_PENDING],  # proof accepted, or rejected
    TASK_MISSED: [TASK_PENDING, TASK_SUBMITTED],     # rescheduled, or late proof
    TASK_COMPLETED: [],                              # finished tasks do not change
}


def can_change_status(current: str, new: str) -> bool:
    """Return True if a task may move from `current` to `new`."""
    # .get(current, []) gives an empty list if the status is unknown
    return new in ALLOWED_CHANGES.get(current, [])


def check_status_change(current: str, new: str) -> None:
    """Raise InvalidInputError if the status change is not allowed."""
    if not can_change_status(current, new):
        # f-string: puts the two status names into the message
        raise InvalidInputError(f"A task cannot change from '{current}' to '{new}'")