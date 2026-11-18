"""
constants.py - shared fixed values for the Aspira backend.

PURPOSE
    Keeps every fixed word the app uses (task statuses, task types and
    evidence types) in one place. Without this, one file might write
    "complete" and another "completed", and the two would never match.

WHO USES IT
    - task_service.py       -> checks that a status is allowed
    - evidence_service.py   -> finds which proof a task type needs
    - analytics_service.py  -> counts tasks by status

HOW TO USE IT
    from app.utils.constants import TASK_COMPLETED, TASK_STATUSES

NOTE
    This file contains no logic. It only holds values that never change
    while the program is running. Names in CAPITALS are constants.
"""

# --- Task statuses -------------------------------------------------
TASK_PENDING = "pending"        # task created, no proof given yet
TASK_SUBMITTED = "submitted"    # user gave proof, waiting to be checked
TASK_COMPLETED = "completed"    # proof accepted; counts in graph and score
TASK_OVERDUE = "overdue"          # due date passed; used by re-planning

# Every allowed status, so other files can check "is this status valid?"
TASK_STATUSES = [TASK_PENDING, TASK_SUBMITTED, TASK_COMPLETED, TASK_OVERDUE]

# --- Task types ----------------------------------------------------
# The four kinds of task defined in the project synopsis
TASK_TYPES = ["project", "course", "learning", "practical"]

# --- Evidence ------------------------------------------------------
# For each task type, the proof the user must give (a dictionary)
EVIDENCE_FOR_TASK_TYPE = {
    "project": "github_link",     # a link to the project on GitHub
    "course": "certificate",      # an uploaded certificate file
    "learning": "quiz",           # a short quiz made by the model
    "practical": "screenshot",    # an uploaded screenshot
}