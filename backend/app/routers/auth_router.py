"""Authentication endpoints.

    POST   /auth/register   create an account (201). 403 when the beta is full, 409 duplicate email.
    POST   /auth/login      email + password -> {"access_token", "token_type": "bearer"}.
                            Blocked for 15 minutes after 10 FAILED attempts for the same email (brute-force guard).
    GET    /auth/me         the logged-in user's profile.
    DELETE /auth/me         delete the account and all its data (204).
    GET    /auth/capacity   public: {"max_users", "registered", "open"} for a "beta full" message.

Endpoints are plain ``def`` on purpose: password hashing (bcrypt) is CPU-heavy, and FastAPI runs
sync endpoints in a worker thread so it never blocks other requests.
"""
from fastapi import APIRouter, Depends, status

from app.core.http_errors import AuthError, RateLimitError
from app.dependencies import get_current_user, get_db, login_limiter
from app.models.user import User
from app.schemas.auth_schema import LoginRequest, RegisterRequest, TokenResponse, UserResponse
from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["Auth"])

LOGIN_ATTEMPTS, LOGIN_WINDOW_SECONDS = 10, 15 * 60


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(data: RegisterRequest, db=Depends(get_db)):
    return auth_service.to_user_response(auth_service.register_user(db, data))


@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, db=Depends(get_db)):
    key = ("login", data.email.strip().lower())
    wait = login_limiter.blocked(key, LOGIN_ATTEMPTS, LOGIN_WINDOW_SECONDS)
    if wait is not None:
        raise RateLimitError(wait, "Too many failed login attempts. Please try again later.")
    try:
        return auth_service.authenticate(db, data)
    except AuthError:
        login_limiter.record(key)  # only FAILED attempts count towards the limit
        raise


@router.get("/me", response_model=UserResponse)
def me(user: User = Depends(get_current_user)):
    return auth_service.to_user_response(user)


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
def delete_me(user: User = Depends(get_current_user), db=Depends(get_db)):
    auth_service.delete_account(db, user)


@router.get("/capacity")
def capacity(db=Depends(get_db)):
    return auth_service.capacity(db)
