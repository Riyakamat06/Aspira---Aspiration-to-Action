"""Account logic: sign-up (with the beta user cap), login, profile and account deletion.

What it does
* register_user   – enforces the ``MAX_USERS`` cap (50 for the beta), checks password strength,
                    rejects duplicate emails (also when two sign-ups race, via the unique
                    constraint), hashes the password and saves the user through Ananya's repository.
* authenticate    – verifies email + password in constant time (unknown emails cost the same as
                    wrong passwords, so attackers cannot discover which emails exist) and returns
                    a signed access token. Errors are always the same vague 401 message.
* capacity        – how many of the beta slots are used (the frontend can show "beta full").
* to_user_response / delete_account – map the User model to Sonali's UserResponse
                    (model field ``full_name`` -> schema field ``name``) and delete an account.

The cap is checked just before inserting; two simultaneous sign-ups at the very last slot could
exceed it by one, which is acceptable for a 50-user beta.
"""
from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.config import settings
from app.core.exceptions import InvalidInputError
from app.core.http_errors import AuthError, ConflictError, ForbiddenError
from app.core.security import (WeakPasswordError, create_access_token, hash_password,
                               validate_password_strength, verify_password)
from app.models.user import User
from app.repositories import user_repository
from app.schemas.auth_schema import LoginRequest, RegisterRequest, TokenResponse, UserResponse


def count_users(db: Session) -> int:
    """Use Ananya's count_users() when it exists, otherwise count directly."""
    fn = getattr(user_repository, "count_users", None)
    if callable(fn):
        return int(fn(db))
    return int(db.scalar(select(func.count(User.id))) or 0)


def capacity(db: Session) -> dict:
    used = count_users(db)
    return {"max_users": settings.max_users, "registered": used, "open": used < settings.max_users}


def register_user(db: Session, data: RegisterRequest) -> User:
    if count_users(db) >= settings.max_users:
        raise ForbiddenError(f"Registration is closed: the beta is limited to {settings.max_users} users.")
    email = data.email.strip().lower()
    try:
        validate_password_strength(data.password, email=email)
    except WeakPasswordError as exc:
        raise InvalidInputError(str(exc)) from exc
    if user_repository.get_user_by_email(db, email) is not None:
        raise ConflictError("An account with this email already exists.")
    try:
        return user_repository.create_user(db, data.name.strip(), email, hash_password(data.password))
    except IntegrityError as exc:  # two sign-ups with the same email at the same moment
        db.rollback()
        raise ConflictError("An account with this email already exists.") from exc


def authenticate(db: Session, data: LoginRequest) -> TokenResponse:
    user = user_repository.get_user_by_email(db, data.email.strip().lower())
    ok = verify_password(data.password, user.hashed_password if user else None)
    if user is None or not ok:
        raise AuthError("Incorrect email or password.")
    token, _ = create_access_token(user.id)
    return TokenResponse(access_token=token)


def to_user_response(user: User) -> UserResponse:
    return UserResponse(id=user.id, name=user.full_name, email=user.email)


def delete_account(db: Session, user: User) -> None:
    user_repository.delete_user(db, user.id)  # cascade removes dreams, roadmaps, chat, journal
