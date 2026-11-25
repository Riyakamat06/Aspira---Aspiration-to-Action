"""Roadmap endpoints (features 1, 2, 9, 13). All except the questionnaire need a logged-in user.

    GET    /roadmaps/intake/questions    the fixed intake questions (public; the UI renders the form)
    POST   /roadmaps/generate            answers (+ optional dream_id) -> new roadmap (201)
    POST   /roadmaps/{id}/regenerate     feedback -> a new roadmap VERSION; finished tasks are kept (201)
    GET    /roadmaps?dream_id=           roadmap versions of a dream with progress, newest first
    GET    /roadmaps/{id}                the full roadmap: milestones, tasks, completion percentages
    DELETE /roadmaps/{id}                delete a roadmap and its tasks (204)
    GET    /roadmaps/readiness/{dream_id}  readiness score with its breakdown and next step

Generation and regeneration are limited per user per hour (config: ROADMAP_RATE_LIMIT_PER_HOUR).
The request is validated and ownership is checked BEFORE the AI is called, so bad requests cost no
quota. Database work runs in a worker thread and the AI call is awaited, so the server stays
responsive while Gemini thinks. AI failures become 503 / 502 / 422 through the handlers in main.py.
"""
from datetime import date, timedelta
from typing import Any

from fastapi import APIRouter, Depends, Query, status
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel, Field

from app.core.exceptions import InvalidInputError
from app.core.http_errors import UnprocessableError
from app.dependencies import get_current_user, get_db, roadmap_rate_limit
from app.models.user import User
from app.services import readiness_service, roadmap_service
from app.services.intake_service import IntakeError, get_questions, validate_answers
from app.services.readiness_service import ReadinessReport
from app.services.roadmap_generator import generate_roadmap
from app.services.roadmap_regenerator import UnsafeFeedbackError, regenerate_roadmap
from app.services.roadmap_service import RoadmapDetail, RoadmapSummary

router = APIRouter(prefix="/roadmaps", tags=["Roadmaps"])


class GenerateRoadmapRequest(BaseModel):
    answers: dict[str, Any]      # keys from /roadmaps/intake/questions
    dream_id: int | None = None  # None = create a new dream from the target career


class RegenerateRequest(BaseModel):
    feedback: str = Field(default="", max_length=800)
    keep_completed: bool = True
    answers: dict[str, Any] | None = None  # only needed if the original answers are not stored


class RegenerationDetail(RoadmapDetail):
    kept_titles: list[str] = []
    added_titles: list[str] = []
    removed_titles: list[str] = []


@router.get("/intake/questions")
def intake_questions():
    return get_questions()


@router.post("/generate", response_model=RoadmapDetail, status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(roadmap_rate_limit)])
async def generate(body: GenerateRoadmapRequest, user: User = Depends(get_current_user), db=Depends(get_db)):
    user_id = user.id
    try:
        answers = validate_answers(body.answers)
    except IntakeError as exc:
        raise UnprocessableError({"answers": exc.errors}) from exc
    dream = await run_in_threadpool(roadmap_service.prepare_generation, db, user_id, body.dream_id)
    draft = await generate_roadmap(answers)

    def save():
        roadmap = roadmap_service.persist_roadmap(db, user_id, draft, answers, dream=dream)
        return roadmap_service.build_response(db, roadmap)
    return await run_in_threadpool(save)


@router.post("/{roadmap_id}/regenerate", response_model=RegenerationDetail,
             status_code=status.HTTP_201_CREATED, dependencies=[Depends(roadmap_rate_limit)])
async def regenerate(roadmap_id: int, body: RegenerateRequest,
                     user: User = Depends(get_current_user), db=Depends(get_db)):
    user_id = user.id
    state = await run_in_threadpool(roadmap_service.load_regeneration_state, db, user_id, roadmap_id, body.answers)
    try:
        result = await regenerate_roadmap(state.answers, state.previous, feedback=body.feedback,
                                          weeks_elapsed=state.weeks_elapsed, keep_completed=body.keep_completed)
    except UnsafeFeedbackError as exc:
        raise InvalidInputError(str(exc)) from exc

    def save():
        # Fresh weeks are counted from the original start, so anchor dates that far back.
        anchor = date.today() - timedelta(weeks=state.weeks_elapsed if result.kept_titles else 0)
        roadmap = roadmap_service.persist_roadmap(db, user_id, result.draft, state.answers, dream=state.dream,
                                                  start=anchor, due_overrides=state.due_overrides)
        detail = roadmap_service.build_response(db, roadmap)
        return RegenerationDetail(**detail.model_dump(), kept_titles=result.kept_titles,
                                  added_titles=result.added_titles, removed_titles=result.removed_titles)
    return await run_in_threadpool(save)


@router.get("/readiness/{dream_id}", response_model=ReadinessReport)
def readiness(dream_id: int, user: User = Depends(get_current_user), db=Depends(get_db)):
    return readiness_service.get_readiness(db, user.id, dream_id)


@router.get("", response_model=list[RoadmapSummary])
def list_for_dream(dream_id: int = Query(...), user: User = Depends(get_current_user), db=Depends(get_db)):
    return roadmap_service.list_roadmaps(db, user.id, dream_id)


@router.get("/{roadmap_id}", response_model=RoadmapDetail)
def get_one(roadmap_id: int, user: User = Depends(get_current_user), db=Depends(get_db)):
    roadmap, dream = roadmap_service.get_owned_roadmap(db, user.id, roadmap_id)
    return roadmap_service.build_response(db, roadmap, dream)


@router.delete("/{roadmap_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_one(roadmap_id: int, user: User = Depends(get_current_user), db=Depends(get_db)):
    roadmap_service.delete_roadmap(db, user.id, roadmap_id)
