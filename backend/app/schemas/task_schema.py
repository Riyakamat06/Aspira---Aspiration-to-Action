"""
task_schema.py - data shapes for creating, updating and returning tasks.

PURPOSE
    Defines the data accepted and returned for roadmap tasks, and checks
    that task types and statuses are only ever values the project allows
    (listed in constants.py).

SCHEMAS
    TaskCreate       -> input to create a task (roadmap, title, type, due date)
    TaskStatusUpdate -> input to change a task's status
    TaskResponse     -> the task sent back, including its id and status

WHO USES IT
    - task_router.py  -> input and output of the task endpoints
    - task_service.py -> receives the checked data

VALIDATION
    A task_type outside TASK_TYPES, or a status outside TASK_STATUSES,
    is rejected with a clear message before any code runs.

NOTE
    Field names must match Ananya's Task database model (task.py).
"""

from datetime import date                                       # a calendar day
from pydantic import BaseModel, ConfigDict, Field, field_validator
from app.utils.constants import TASK_TYPES, TASK_STATUSES       # the allowed values


class TaskCreate(BaseModel):
    roadmap_id: int                                  # which roadmap this task belongs to
    title: str = Field(min_length=1, max_length=200) # the task's name
    task_type: str                                   # project, course, learning or practical
    due_date: date                                   # the deadline

    @field_validator("task_type")
    @classmethod
    def check_task_type(cls, value: str) -> str:
        # reject any type that is not in the allowed list
        if value not in TASK_TYPES:
            raise ValueError(f"task_type must be one of {TASK_TYPES}")
        return value


class TaskStatusUpdate(BaseModel):
    status: str                                      # the new status for the task

    @field_validator("status")
    @classmethod
    def check_status(cls, value: str) -> str:
        # reject any status that is not in the allowed list
        if value not in TASK_STATUSES:
            raise ValueError(f"status must be one of {TASK_STATUSES}")
        return value


class TaskResponse(BaseModel):
    # lets Pydantic read data straight from a database object
    model_config = ConfigDict(from_attributes=True)

    id: int                # unique number of the task
    roadmap_id: int        # the roadmap it belongs to
    title: str             # the task's name
    task_type: str         # its type
    status: str            # its current status
    due_date: date         # its deadline