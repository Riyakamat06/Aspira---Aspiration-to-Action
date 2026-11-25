"""
task_router.py - web addresses (endpoints) for tasks.

ENDPOINTS
    GET   /tasks/{id}          -> view one task (404 if it is not theirs)
    PATCH /tasks/{id}/status   -> change a task's status

STATUS RULES (enforced by task_service.py, from SRS FR-EV-01)
    A task can NEVER be set to "completed" through this endpoint. It
    becomes completed only when its evidence is accepted, which is done
    by the evidence service. Other changes follow the allowed list in
    task_service.py; a forbidden change returns 400.

OWNERSHIP
    Tasks are looked up through their owner, so a user cannot read or
    change another user's task by guessing its id.

NOT HERE
    Tasks are created by the roadmap generator, so there is no POST.

WHO USES IT
    - Tanushree's taskApi.js, TaskCard and StatusToggle
    - main.py must include it: app.include_router(task_router.router)
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.routers.dream_router import get_current_user_id
from app.schemas.task_schema import TaskResponse, TaskStatusUpdate
from app.services import task_service

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.get("/{task_id}", response_model=TaskResponse)
def view_task(task_id: int, db: Session = Depends(get_db),
              user_id: int = Depends(get_current_user_id)):
    return task_service.get_task(db, user_id, task_id)


@router.patch("/{task_id}/status", response_model=TaskResponse)
def update_task_status(task_id: int, data: TaskStatusUpdate,
                       db: Session = Depends(get_db),
                       user_id: int = Depends(get_current_user_id)):
    # TaskStatusUpdate already rejected any status word outside the allowed list
    return task_service.change_task_status(db, user_id, task_id, data.status)