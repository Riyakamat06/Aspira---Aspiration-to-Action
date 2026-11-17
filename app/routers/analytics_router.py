"""
analytics_router.py - web address for the weekly progress graph (feature 7).

ENDPOINT
    GET /analytics/weekly/{dream_id}
        -> the weeks for one dream: for each week, the Monday date, how
           many tasks were due and how many were completed.
           404 if the dream does not exist.

THE DATA SHAPE
    WeeklyAnalyticsResponse in analytics_schema.py, the agreed contract
    with Tanushree, whose ProgressChart reads exactly these fields.

WHO USES IT
    - Tanushree's analyticsApi.js, AnalyticsPage and ProgressChart
    - main.py must include it: app.include_router(analytics_router.router)

THE PLACE THAT CHANGES LATER
    get_analytics_repo() is where Ananya's analytics repository plugs
    in. It needs one method: tasks_for_dream(dream_id), returning the
    tasks of that dream; each needs a due_date and a status.
"""

from fastapi import APIRouter, Depends

from app.routers.dream_router import get_dream_repo
from app.schemas.analytics_schema import WeeklyAnalyticsResponse
from app.services import dream_service
from app.services.analytics_service import build_weekly_progress

router = APIRouter(prefix="/analytics", tags=["Analytics"])


def get_analytics_repo():
    # TO DO: return Ananya's analytics repository once it exists
    raise NotImplementedError("Connect the analytics repository from M1 here")


@router.get("/weekly/{dream_id}", response_model=WeeklyAnalyticsResponse)
def weekly_progress(
    dream_id: int,
    analytics_repo=Depends(get_analytics_repo),
    dream_repo=Depends(get_dream_repo),
):
    dream_service.get_dream(dream_repo, dream_id)       # 404 if the dream is missing
    tasks = analytics_repo.tasks_for_dream(dream_id)    # this dream's tasks
    return WeeklyAnalyticsResponse(
        dream_id=dream_id,
        weeks=build_weekly_progress(tasks),             # your weekly calculation
    )