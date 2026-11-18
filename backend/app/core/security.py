"""Password hashing and JWT helpers.

* Passwords are SHA-256 pre-hashed then bcrypt-hashed, so bcrypt's 72-byte
  truncation can never silently weaken long passphrases.
* ``verify_password`` always performs a bcrypt comparison (against a dummy hash
  when the user does not exist) to blunt user-enumeration via timing.
* Tokens are short-lived signed JWTs with ``sub``, ``iat``, ``exp`` and a unique
  ``jti``; decoding enforces expiry and required claims.
"""
from __future__ import annotations

import base64
import hashlib
import re
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any

import bcrypt
import jwt

from app.config import settings


class TokenError(Exception):
    """Raised for any invalid, expired or malformed token."""


class WeakPasswordError(ValueError):
    """Raised when a password fails the strength policy."""


def _prehash(password: str) -> bytes:
    digest = hashlib.sha256(password.encode("utf-8")).digest()
    return base64.b64encode(digest)  # 44 bytes, always < 72


def hash_password(password: str) -> str:
    return bcrypt.hashpw(_prehash(password), bcrypt.gensalt(rounds=settings.bcrypt_rounds)).decode("utf-8")


_DUMMY_HASH = hash_password(secrets.token_urlsafe(16))


def verify_password(password: str, hashed: str | None) -> bool:
    """Constant-ish time check; pass ``hashed=None`` for unknown users."""
    target = (hashed or _DUMMY_HASH).encode("utf-8")
    try:
        ok = bcrypt.checkpw(_prehash(password), target)
    except ValueError:
        return False
    return ok and hashed is not None


def needs_rehash(hashed: str) -> bool:
    """True when the stored hash used fewer rounds than the current setting."""
    try:
        rounds = int(hashed.split("$")[2])
    except (IndexError, ValueError):
        return True
    return rounds < settings.bcrypt_rounds


_COMMON = {"password", "password1", "12345678", "123456789", "qwerty123", "iloveyou", "admin123", "letmein1"}


def validate_password_strength(password: str, *, email: str | None = None) -> None:
    problems: list[str] = []
    if len(password) < settings.password_min_length:
        problems.append(f"at least {settings.password_min_length} characters")
    if len(password) > 128:
        problems.append("at most 128 characters")
    if not re.search(r"[a-z]", password) or not re.search(r"[A-Z]", password):
        problems.append("both upper and lower case letters")
    if not re.search(r"\d", password):
        problems.append("a digit")
    if password.lower() in _COMMON:
        problems.append("to not be a commonly used password")
    if email and email.split("@")[0].lower() in password.lower() and len(email.split("@")[0]) >= 4:
        problems.append("to not contain your email name")
    if problems:
        raise WeakPasswordError("Password needs " + ", ".join(problems) + ".")


def create_access_token(subject: str | int, *, extra: dict[str, Any] | None = None,
                        expires_delta: timedelta | None = None) -> tuple[str, datetime]:
    now = datetime.now(timezone.utc)
    expires = now + (expires_delta or timedelta(minutes=settings.access_token_expire_minutes))
    payload: dict[str, Any] = {
        "sub": str(subject),
        "iat": int(now.timestamp()),
        "exp": int(expires.timestamp()),
        "jti": secrets.token_hex(8),
        **(extra or {}),
    }
    token = jwt.encode(payload, settings.secret_key.get_secret_value(), algorithm=settings.jwt_algorithm)
    return token, expires


def decode_access_token(token: str) -> dict[str, Any]:
    try:
        return jwt.decode(
            token,
            settings.secret_key.get_secret_value(),
            algorithms=[settings.jwt_algorithm],
            options={"require": ["sub", "exp", "iat"]},
        )
    except jwt.ExpiredSignatureError as exc:
        raise TokenError("Token has expired") from exc
    except jwt.PyJWTError as exc:
        raise TokenError("Invalid token") from exc
