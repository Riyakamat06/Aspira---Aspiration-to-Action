"""
exceptions.py - shared error types for the Aspira backend.

PURPOSE
    Gives every service the same way to report a problem. When a service
    raises one of these errors, FastAPI turns it into a proper reply with
    the right status code and a clear message, so each file does not have
    to build error replies by hand.

ERRORS
    NotFoundError(what)       -> status 404, message "<what> not found"
    InvalidInputError(message) -> status 400, message explains what was wrong

WHO USES IT
    - dream_service.py, task_service.py, journal_service.py, and the
      other services, whenever a record is missing or input is not allowed.

HOW TO USE IT
    from app.core.exceptions import NotFoundError, InvalidInputError

    raise NotFoundError("Dream")                  # reply: "Dream not found"
    raise InvalidInputError("Unknown status")     # reply: "Unknown status"
"""

from fastapi import HTTPException, status   # HTTPException = an error FastAPI can send back


class NotFoundError(HTTPException):
    """Raised when something that was asked for does not exist."""

    def __init__(self, what: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,   # 404 means "not found"
            detail=f"{what} not found",              # message the caller sees
        )


class InvalidInputError(HTTPException):
    """Raised when the user sends something that is not allowed."""

    def __init__(self, message: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,  # 400 means "bad request"
            detail=message,                           # explains what was wrong
        )