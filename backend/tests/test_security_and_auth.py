"""
test_security_and_auth.py - independent tests for Riya's security helpers.

PURPOSE
    security.py (app/core/security.py) protects the login system. It hashes
    passwords with bcrypt, checks that a password is strong enough, and creates
    and checks the signed tokens (JWT) that keep a user logged in. A mistake
    here would let someone log in as another user, so these tests check the
    rules from the outside. No network and no database are used.

WHAT IS TESTED
    1. Password hashing: the hash is a bcrypt hash and hides the password; the
       right password verifies and a wrong one does not; the same password
       gives a different hash each time; passwords that differ only after the
       72nd byte are told apart; an unknown user or a broken stored hash never
       verifies; old hashes (fewer rounds) are marked for re-hashing.
    2. Password strength: a strong password passes; too short, too long, no
       upper or lower case, no digit, a common password, and a password that
       contains the email name are refused with a clear message; several
       problems are reported together.
    3. Tokens: the token holds the subject (as text), issue time, expiry and a
       unique id; extra claims are added; the expiry follows the settings; an
       expired token, a token signed with another secret, a token whose
       payload was swapped, garbage text, a token with a missing claim and a
       token with algorithm "none" are all refused with TokenError.

NOT TESTED HERE
    auth_service.py and auth_router.py (login and sign-up flow). They are not
    in main yet. This file will be extended when they arrive.

HOW TO RUN
    cd backend
    pytest tests/test_security_and_auth.py -v

WHO USES IT
    Sonali (M4 testing), reviewed by Riya (owner of security.py).
"""

import os  # to set dummy settings before the app loads

# dummy settings so the app can load in tests; never put a real key here
os.environ.setdefault("SECRET_KEY", "test-secret-key-for-tests-only-0000")  # fake secret
os.environ.setdefault("GEMINI_API_KEY", "fake-key-not-real")                # fake AI key

import base64  # to build token parts by hand
import json    # to turn a dictionary into text for a token part
import time    # to get the current time as a number
from datetime import datetime, timedelta, timezone  # for token expiry checks

import bcrypt  # to make an old, weak hash for the re-hash test
import jwt     # to build tokens with a missing claim or another secret
import pytest  # the test tool

from app.config import settings  # the real settings (rounds, minimum length, token minutes)
from app.core.security import (  # the things we test
    TokenError,                # raised for any bad token
    WeakPasswordError,         # raised for a weak password
    create_access_token,       # makes a token
    decode_access_token,       # checks a token and reads it
    hash_password,             # makes a bcrypt hash
    needs_rehash,              # True when a stored hash is weaker than today's setting
    validate_password_strength,  # raises WeakPasswordError for a weak password
    verify_password,           # checks a password against a stored hash
)

STRONG = "Tr1ckyLongPhraseOk99"  # a password that passes every rule


# ---------- helpers: small builders so the tests stay short ----------

def b64(data):
    # turns a dictionary into one base64 text part of a token (no "=" at the end)
    raw = json.dumps(data).encode()                       # dictionary -> bytes
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode()  # bytes -> token-safe text


def claims(**changes):
    # a normal set of token claims: subject 1, issued now, expires in one hour
    now = int(time.time())                                # the current time as a number
    data = {"sub": "1", "iat": now, "exp": now + 3600}    # the three required claims
    data.update(changes)                                  # apply the changes the test asks for
    return data


def sign(payload, secret=None):
    # signs a payload with the real secret, or with another secret if one is given
    key = secret or settings.secret_key.get_secret_value()  # which secret to use
    return jwt.encode(payload, key, algorithm=settings.jwt_algorithm)


# ---------- password hashing ----------

def test_hash_is_a_bcrypt_hash_and_hides_the_password():
    hashed = hash_password("Secret123")       # make a hash
    assert hashed.startswith("$2")            # bcrypt hashes start with $2
    assert len(hashed) == 60                  # and are always 60 characters
    assert "Secret123" not in hashed          # the password itself is not inside


def test_right_password_verifies_and_wrong_one_does_not():
    hashed = hash_password("Secret123")
    assert verify_password("Secret123", hashed) is True    # the right password
    assert verify_password("secret123", hashed) is False   # capital letters matter


def test_same_password_gives_different_hashes_that_both_verify():
    first = hash_password("Secret123")
    second = hash_password("Secret123")
    assert first != second                                 # a new random salt each time
    assert verify_password("Secret123", first) is True     # but both still work
    assert verify_password("Secret123", second) is True


def test_passwords_that_differ_only_after_72_bytes_are_told_apart():
    one = "Ab1" + "x" * 100 + "ONE"           # bcrypt alone would cut both at 72 bytes
    two = "Ab1" + "x" * 100 + "TWO"           # same first 72 bytes, different ending
    hashed = hash_password(one)
    assert verify_password(one, hashed) is True    # the real password works
    assert verify_password(two, hashed) is False   # the look-alike does not


def test_unknown_user_never_verifies():
    assert verify_password("anything", None) is False      # no stored hash means no login


@pytest.mark.parametrize("stored", ["not-a-hash", ""])      # a broken hash and an empty one
def test_broken_stored_hash_never_verifies(stored):
    assert verify_password("Secret123", stored) is False   # and it must not crash


def test_current_hash_does_not_need_rehash():
    assert needs_rehash(hash_password("Secret123")) is False   # made with today's rounds


def test_old_hash_with_fewer_rounds_needs_rehash():
    if settings.bcrypt_rounds <= 4:                        # 4 is the smallest bcrypt allows
        pytest.skip("bcrypt_rounds is already the minimum")
    old = bcrypt.hashpw(b"x", bcrypt.gensalt(rounds=4)).decode()  # a weak hash on purpose
    assert needs_rehash(old) is True                       # it must be marked for re-hashing


@pytest.mark.parametrize("stored", ["garbage", "$2b$xx$abc"])  # not a hash; rounds are not a number
def test_unreadable_hash_needs_rehash(stored):
    assert needs_rehash(stored) is True


# ---------- password strength ----------

def test_a_strong_password_passes():
    assert validate_password_strength(STRONG, email="someone@example.com") is None  # nothing is raised


def test_too_short_password_is_refused():
    with pytest.raises(WeakPasswordError) as info:
        validate_password_strength("Ab1")                  # 3 characters
    assert f"at least {settings.password_min_length} characters" in str(info.value)  # the message names the limit


def test_too_long_password_is_refused():
    with pytest.raises(WeakPasswordError) as info:
        validate_password_strength("Aa1" + "x" * 130)      # 133 characters
    assert "at most 128 characters" in str(info.value)


@pytest.mark.parametrize("password", ["alllowercase123456", "ALLUPPERCASE123456"])  # only one case each
def test_password_needs_both_letter_cases(password):
    with pytest.raises(WeakPasswordError) as info:
        validate_password_strength(password)
    assert "both upper and lower case letters" in str(info.value)


def test_password_needs_a_digit():
    with pytest.raises(WeakPasswordError) as info:
        validate_password_strength("NoDigitsHereAtAll")
    assert "a digit" in str(info.value)


def test_common_password_is_refused_even_if_other_rules_pass():
    with pytest.raises(WeakPasswordError) as info:
        validate_password_strength("Password1")            # has both cases and a digit, but is on the common list
    assert "commonly used" in str(info.value)


def test_password_containing_the_email_name_is_refused():
    with pytest.raises(WeakPasswordError) as info:
        validate_password_strength("Sonali.Gandgale99", email="sonali.gandgale@example.com")
    assert "email name" in str(info.value)


def test_a_very_short_email_name_is_ignored():
    # "ab" is only 2 letters, so it must not count (the rule starts at 4 letters)
    assert validate_password_strength("StrongAb1Password", email="ab@example.com") is None


def test_several_problems_are_reported_together():
    with pytest.raises(WeakPasswordError) as info:
        validate_password_strength("abc")                  # short, no capital, no digit
    message = str(info.value)
    assert "at least" in message                           # too short
    assert "both upper and lower case letters" in message  # no capital letter
    assert "a digit" in message                            # no digit


# ---------- tokens ----------

def test_token_holds_subject_as_text_and_the_standard_claims():
    token, _ = create_access_token(42)                     # the subject is a number
    payload = decode_access_token(token)
    assert payload["sub"] == "42"                          # stored as text
    assert {"sub", "iat", "exp", "jti"} <= set(payload)    # all four claims are present
    assert len(payload["jti"]) == 16                       # the unique id has 16 characters


def test_extra_claims_are_added():
    token, _ = create_access_token(1, extra={"role": "learner"})
    assert decode_access_token(token)["role"] == "learner"


def test_expiry_follows_the_settings():
    token, expires = create_access_token(1)
    payload = decode_access_token(token)
    wait = (expires - datetime.now(timezone.utc)).total_seconds()  # seconds until it expires
    assert expires.tzinfo is not None                      # the expiry has a time zone
    assert abs(wait - settings.access_token_expire_minutes * 60) < 5  # about the configured minutes
    assert payload["exp"] == int(expires.timestamp())      # the token says the same as the returned time


def test_custom_expiry_is_exact():
    token, _ = create_access_token(1, expires_delta=timedelta(minutes=5))
    payload = decode_access_token(token)
    assert payload["exp"] - payload["iat"] == 300          # exactly 5 minutes


def test_two_tokens_for_the_same_user_are_different():
    first, _ = create_access_token(1)
    second, _ = create_access_token(1)
    assert first != second                                 # different tokens
    assert decode_access_token(first)["jti"] != decode_access_token(second)["jti"]  # different unique ids


def test_expired_token_is_refused_with_a_clear_message():
    token, _ = create_access_token(1, expires_delta=timedelta(seconds=-10))  # already expired
    with pytest.raises(TokenError, match="expired"):
        decode_access_token(token)


def test_token_signed_with_another_secret_is_refused():
    forged = sign(claims(), secret="a-completely-different-secret-key-0123456789")
    with pytest.raises(TokenError, match="Invalid token"):
        decode_access_token(forged)


def test_token_with_a_swapped_payload_is_refused():
    token, _ = create_access_token(1)
    header, _, signature = token.split(".")                # keep the real header and signature
    forged = ".".join([header, b64(claims(sub="999")), signature])  # but claim to be user 999
    with pytest.raises(TokenError, match="Invalid token"):
        decode_access_token(forged)


@pytest.mark.parametrize("text", ["", "garbage", "a.b.c"])  # empty, no dots, three dots but nonsense
def test_garbage_is_refused(text):
    with pytest.raises(TokenError, match="Invalid token"):
        decode_access_token(text)


@pytest.mark.parametrize("missing", ["sub", "exp", "iat"])  # the three required claims
def test_token_without_a_required_claim_is_refused(missing):
    payload = claims()                                     # a normal payload
    del payload[missing]                                   # take one claim out
    with pytest.raises(TokenError):
        decode_access_token(sign(payload))                 # even with the right secret


def test_token_with_algorithm_none_is_refused():
    header = b64({"alg": "none", "typ": "JWT"})            # says: "no signature needed"
    unsigned = f"{header}.{b64(claims())}."                # and has an empty signature
    with pytest.raises(TokenError):
        decode_access_token(unsigned)