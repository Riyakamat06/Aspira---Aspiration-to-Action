"""
task_router.py - web addresses (endpoints) for tasks.

ENDPOINTS
    GET   /tasks/{id}          -> view one task (404 if it does not exist)
    PATCH /tasks/{id}/status   -> change a task's status

STATUS RULES (enforced by task_service.py, from SRS FR-EV-01)
    A task can NEVER be set to "completed" through this endpoint. It
    becomes completed only when its evidence is accepted, which is
    done by the evidence service. Other changes follow the allowed
    list in task_service.py; a forbidden change returns 400.

NOT HERE
    Tasks are created by the roadmap generator, so there is no POST.

WHO USES IT
    - Tanushree's taskApi.js, TaskCard and StatusToggle
    - main.py must include it: app.include_router(task_router.router)

THE PLACE THAT CHANGES LATER
    get_task_repo() is where Ananya's task repository plugs in.
"""

from fastapi import APIRouter, Depends

from app.schemas.task_schema import TaskResponse, TaskStatusUpdate
from app.services import task_service

router = APIRouter(prefix="/tasks", tags=["Tasks"])


def get_task_repo():
    # TO DO: return Ananya's task repository once it exists
    raise NotImplementedError("Connect the task repository from M1 here")


@router.get("/{task_id}", response_model=TaskResponse)
def view_task(task_id: int, repo=Depends(get_task_repo)):
    return task_service.get_task(repo, task_id)


@router.patch("/{task_id}/status", response_model=TaskResponse)
def update_task_status(task_id: int, data: TaskStatusUpdate, repo=Depends(get_task_repo)):
    # TaskStatusUpdate already rejected any status word outside the allowed list
    return task_service.change_task_status(repo, task_id, data.status)