"""
task_service.py - business rules for tasks.

PURPOSE
    Holds the rules about how a task's status may change, and the two
    functions the task router uses to find a task and change its status.
    The storage helper (`repo`) is passed in as a parameter, so the real
    database (Ananya's repository) can replace the test stand-in without
    changing this file.

FUNCTIONS
    can_change_status(current, new)     -> True if the move is allowed
    check_status_change(current, new)   -> raises an error if not allowed
    get_task(repo, task_id)             -> returns the task, or raises NotFoundError
    change_task_status(repo, id, new)   -> checks the rules, saves, returns the task

STATUS RULES (statuses come from constants.py)
    pending   -> submitted (proof given) or overdue (due date passed)
    submitted -> completed (proof accepted) or pending (proof rejected)
    overdue   -> pending (deadline moved) or submitted (late proof)
    completed -> no further changes; a finished task stays finished

WHY THE RULES EXIST
    SRS requirement FR-EV-01: a task becomes completed only when its
    evidence is accepted, never because the user says so. For that
    reason change_task_status() refuses to set "completed" at all. The
    evidence service will do that step once evidence is accepted.

WHO USES IT
    - task_router.py -> calls get_task and change_task_status
"""

from app.core.exceptions import InvalidInputError, NotFoundError   # the shared errors
from app.utils.constants import (                                   # the shared status words
    TASK_PENDING,
    TASK_SUBMITTED,
    TASK_COMPLETED,
    TASK_OVERDUE,
)

# For each status, the list of statuses it is allowed to change to.
ALLOWED_CHANGES = {
    TASK_PENDING: [TASK_SUBMITTED, TASK_OVERDUE],     # not started -> proof given, or late
    TASK_SUBMITTED: [TASK_COMPLETED, TASK_PENDING],   # proof accepted, or rejected
    TASK_OVERDUE: [TASK_PENDING, TASK_SUBMITTED],     # rescheduled, or late proof
    TASK_COMPLETED: [],                               # finished tasks do not change
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


def get_task(repo, task_id: int):
    """Return one task, or raise NotFoundError if it does not exist."""
    task = repo.get(task_id)            # ask the repo; it gives None if missing
    if task is None:
        raise NotFoundError("Task")     # reply: "Task not found" (status 404)
    return task


def change_task_status(repo, task_id: int, new_status: str):
    """Change a task's status if the rules allow it, and return the task."""
    task = get_task(repo, task_id)      # 404 if the task does not exist
    # SRS FR-EV-01: only accepted evidence may complete a task, never a request
    if new_status == TASK_COMPLETED:
        raise InvalidInputError("A task becomes completed only when its evidence is accepted")
    check_status_change(task.status, new_status)    # raises an error if not allowed
    return repo.update(task_id, status=new_status)  # save the new status