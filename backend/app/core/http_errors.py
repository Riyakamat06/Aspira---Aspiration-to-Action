"""Extra HTTP errors used by Aspira's auth, roadmap and chat code.

Sonali's ``core/exceptions.py`` already provides NotFoundError (404) and
InvalidInputError (400). These add the remaining status codes so services never
build raw HTTP replies by hand.

    AuthError(msg)             401  not logged in / bad credentials / bad token
    ForbiddenError(msg)        403  allowed to ask, not allowed to do (e.g. user cap reached)
    ConflictError(msg)         409  duplicate (e.g. email already registered)
    UnprocessableError(detail) 422  input understood but unusable (detail may be a dict)
    RateLimitError(retry)      429  too many requests, with a Retry-After header
    ServiceUnavailableError()  503  the AI provider is down or busy
"""
from __future__ import annotations

import math
from typing import Any

from fastapi import HTTPException, status


class AuthError(HTTPException):
    def __init__(self, message: str = "Not authenticated"):
        super().__init__(status.HTTP_401_UNAUTHORIZED, message, headers={"WWW-Authenticate": "Bearer"})


class ForbiddenError(HTTPException):
    def __init__(self, message: str = "Not allowed"):
        super().__init__(status.HTTP_403_FORBIDDEN, message)


class ConflictError(HTTPException):
    def __init__(self, message: str):
        super().__init__(status.HTTP_409_CONFLICT, message)


class UnprocessableError(HTTPException):
    def __init__(self, detail: Any):
        super().__init__(422, detail)  # literal: Starlette renamed the constant


class RateLimitError(HTTPException):
    def __init__(self, retry_after_seconds: float, message: str = "Too many requests. Please slow down."):
        wait = max(1, math.ceil(retry_after_seconds))
        super().__init__(status.HTTP_429_TOO_MANY_REQUESTS, message, headers={"Retry-After": str(wait)})


class ServiceUnavailableError(HTTPException):
    def __init__(self, message: str = "The AI service is busy. Please try again shortly.", retry_after: int = 15):
        super().__init__(status.HTTP_503_SERVICE_UNAVAILABLE, message, headers={"Retry-After": str(retry_after)})
