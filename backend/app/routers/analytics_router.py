"""
analytics_router.py - web address for the weekly progress graph (feature 7).

ENDPOINT
    GET /analytics/weekly/{dream_id}
        -> the weeks for one of this user's dreams: for each week, the
           Monday date, how many tasks were due and how many were completed.
           404 if the dream is missing or not theirs.

THE DATA SHAPE
    WeeklyAnalyticsResponse in analytics_schema.py, the agreed contract
    with Tanushree, whose ProgressChart reads exactly these fields.

WHO USES IT
    - Tanushree's analyticsApi.js, AnalyticsPage and ProgressChart
    - main.py must include it: app.include_router(analytics_router.router)

NOTE
    The current user comes from get_current_user_id() in dream_router.py
    (temporary: the demo user, until Riya's login is in main).
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.routers.dream_router import get_current_user_id
from app.schemas.analytics_schema import WeeklyAnalyticsResponse
from app.services import analytics_service

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/weekly/{dream_id}", response_model=WeeklyAnalyticsResponse)
def weekly_progress(dream_id: int, db: Session = Depends(get_db),
                    user_id: int = Depends(get_current_user_id)):
    return analytics_service.weekly_for_dream(db, user_id, dream_id)