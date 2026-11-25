"""Aspira application entry point (replaces the minimal main.py; agree the change with Sonali).

* Creates the database tables at start-up (safe to repeat) through Ananya's init_db.
* CORS from config (CORS_ORIGINS), gzip for large replies, and an ``X-Process-Time`` header.
* Registers the auth, roadmap and chat routers under ``API_PREFIX`` (default ``/api/v1``).
* Turns AI failures into clean replies: provider down -> 503 (+Retry-After), blocked by the safety
  filter -> 422, unusable model output -> 502. Nothing leaks stack traces to the client.
* ``/health`` stays exactly ``{"status": "ok"}`` (Sonali's test_health depends on it).

Sonali's dream / journal / task / analytics routers are included at the bottom, with her temporary
"demo user" function replaced by the real login through a dependency override.
"""
import time
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.db.init_db import init_db
from app.routers import auth_router, chat_router, roadmap_router
from app.services.ai_client import AIBlockedError, AIResponseError, AIUnavailableError


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title=settings.app_name, version=settings.app_version, lifespan=lifespan,
              docs_url=None if settings.is_production else "/docs",
              redoc_url=None if settings.is_production else "/redoc")

app.add_middleware(GZipMiddleware, minimum_size=1024)
app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origins, allow_credentials=True,
                   allow_methods=["*"], allow_headers=["*"])


@app.middleware("http")
async def add_process_time(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    response.headers["X-Process-Time"] = f"{(time.perf_counter() - start) * 1000:.1f}ms"
    return response


@app.exception_handler(AIUnavailableError)
async def ai_unavailable(_: Request, __: AIUnavailableError):
    return JSONResponse(status_code=503, headers={"Retry-After": "15"},
                        content={"detail": "The AI service is busy. Please try again shortly."})


@app.exception_handler(AIBlockedError)
async def ai_blocked(_: Request, __: AIBlockedError):
    return JSONResponse(status_code=422,
                        content={"detail": "This request could not be processed. Try rephrasing it."})


@app.exception_handler(AIResponseError)
async def ai_bad_output(_: Request, __: AIResponseError):
    return JSONResponse(status_code=502,
                        content={"detail": "The AI returned an unusable answer. Please try again."})


@app.get("/health")
def health():
    return {"status": "ok"}


app.include_router(auth_router.router, prefix=settings.api_prefix)
app.include_router(roadmap_router.router, prefix=settings.api_prefix)
app.include_router(chat_router.router, prefix=settings.api_prefix)

# Sonali's dream / journal / task / analytics routers. They all read the logged-in user from one
# placeholder function (dream_router.get_current_user_id, "demo user 1"). Instead of editing her
# file, we point that function at the real login here: the routers then work per user.
from app.dependencies import get_current_user  # noqa: E402
from app.routers import analytics_router, dream_router, journal_router, task_router  # noqa: E402


def _logged_in_user_id(user=Depends(get_current_user)) -> int:
    return user.id


def use_real_login() -> None:
    """Point Sonali's placeholder user function at the real login (safe to call again)."""
    app.dependency_overrides[dream_router.get_current_user_id] = _logged_in_user_id


use_real_login()
for _router in (dream_router, journal_router, task_router, analytics_router):
    app.include_router(_router.router, prefix=settings.api_prefix)
