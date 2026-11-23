"""Shared FastAPI dependencies (the "plumbing" every protected endpoint uses).

What it provides
* ``get_db``            – one database session per request (re-exported from Ananya's session.py,
                          so tests can override it in one place).
* ``get_current_user``  – reads the ``Authorization: Bearer <token>`` header, verifies the JWT,
                          loads the user, or answers 401.
* ``SlidingWindowLimiter`` – small thread-safe in-memory rate limiter (per user / per key).
* ``chat_rate_limit`` / ``roadmap_rate_limit`` – ready-made dependencies using the limits from
                          config.py (chat per minute, roadmap generation per hour). AI calls cost
                          money and quota, so each user gets a fair share.

Note: the limiter lives in process memory. That is right for one server process (our beta);
with several workers, move it to Redis.
"""
from __future__ import annotations

import threading
import time
from collections import deque
from typing import Callable

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.config import settings
from app.core.http_errors import AuthError, RateLimitError
from app.core.security import TokenError, decode_access_token
from app.db.session import get_db  # noqa: F401  (re-exported on purpose)
from app.models.user import User
from app.repositories import user_repository

_bearer = HTTPBearer(auto_error=False, description="Paste the access_token returned by /auth/login")


def get_current_user(credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
                     db=Depends(get_db)) -> User:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise AuthError("Not authenticated")
    try:
        payload = decode_access_token(credentials.credentials)
        user_id = int(payload["sub"])
    except TokenError as exc:
        raise AuthError(str(exc)) from exc
    except (KeyError, ValueError) as exc:
        raise AuthError("Invalid token") from exc
    user = user_repository.get_user_by_id(db, user_id)
    if user is None:
        raise AuthError("Account no longer exists")
    return user


class SlidingWindowLimiter:
    """Allow at most ``max_calls`` per ``window`` seconds for each key."""

    def __init__(self) -> None:
        self._hits: dict[object, deque[float]] = {}
        self._lock = threading.Lock()

    def hit(self, key: object, max_calls: int, window: float) -> float | None:
        """Record a call. Returns None if allowed, else the seconds to wait."""
        now = time.monotonic()
        with self._lock:
            q = self._hits.setdefault(key, deque())
            while q and now - q[0] >= window:
                q.popleft()
            if len(q) >= max_calls:
                return window - (now - q[0])
            q.append(now)
            if len(self._hits) > 10_000:  # cheap memory guard
                for k in [k for k, v in self._hits.items() if not v or now - v[-1] >= window]:
                    self._hits.pop(k, None)
            return None

    def blocked(self, key: object, max_calls: int, window: float) -> float | None:
        """Like ``hit`` but only looks: seconds to wait if the key is over its limit, else None."""
        now = time.monotonic()
        with self._lock:
            q = self._hits.get(key)
            if not q:
                return None
            while q and now - q[0] >= window:
                q.popleft()
            return window - (now - q[0]) if len(q) >= max_calls else None

    def record(self, key: object) -> None:
        """Count one event (for example a failed login) without checking the limit."""
        with self._lock:
            self._hits.setdefault(key, deque()).append(time.monotonic())

    def reset(self) -> None:
        with self._lock:
            self._hits.clear()


chat_limiter = SlidingWindowLimiter()
roadmap_limiter = SlidingWindowLimiter()
login_limiter = SlidingWindowLimiter()


def _limit_dependency(limiter: SlidingWindowLimiter, max_calls: Callable[[], int],
                      window: float, message: str):
    def dependency(user: User = Depends(get_current_user)) -> None:
        wait = limiter.hit(user.id, max_calls(), window)
        if wait is not None:
            raise RateLimitError(wait, message)
    return dependency


chat_rate_limit = _limit_dependency(
    chat_limiter, lambda: settings.chat_rate_limit_per_minute, 60,
    "You are sending messages too quickly. Please wait a moment.")
roadmap_rate_limit = _limit_dependency(
    roadmap_limiter, lambda: settings.roadmap_rate_limit_per_hour, 3600,
    "Roadmap generation limit reached. Please try again later.")
