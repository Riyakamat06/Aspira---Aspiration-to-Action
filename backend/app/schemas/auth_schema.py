"""
auth_schema.py - data shapes for registering and logging in.

PURPOSE
    Defines the data accepted when a user creates an account or logs
    in, and what is sent back. Pydantic rejects bad input (a short
    password, an address with no "@") before any code runs.

SCHEMAS
    RegisterRequest -> input: name, email and password
    LoginRequest    -> input: email and password
    TokenResponse   -> output: an access token the website keeps after login
    UserResponse    -> output: the user's public details (never the password)

WHO USES IT
    - auth_router.py (Riya) and auth_service.py (Riya)
    - Tanushree's authApi.js, LoginPage and RegisterPage

NOTE
    Field names must match Ananya's User model (user.py).
    The password must never appear in a response schema.
    UserResponse.name is read from the database column full_name (Ananya's User model).
"""

from pydantic import AliasChoices, BaseModel, ConfigDict, Field, field_validator  # AliasChoices: accept two names for one field


class RegisterRequest(BaseModel):
    name: str = Field(min_length=1, max_length=100)     # the user's display name
    email: str                                          # login address
    password: str = Field(min_length=8, max_length=100)  # at least 8 characters

    @field_validator("email")
    @classmethod
    def check_email(cls, value: str) -> str:
        # a simple check: there must be an "@" with text on both sides
        name, _, domain = value.partition("@")
        if not name or not domain:
            raise ValueError("email must look like name@example.com")
        return value.lower()      # store emails in lower case so matching is easy


class LoginRequest(BaseModel):
    email: str          # the address used to register
    password: str       # the password to check


class TokenResponse(BaseModel):
    access_token: str            # the token proving the user is logged in
    token_type: str = "bearer"   # the standard word for this kind of token


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)   # read data from a database object

    id: int          # unique number of the user
    name: str = Field(validation_alias=AliasChoices("name", "full_name"))   # display name; the database column is called full_name
    email: str       # login address
    # there is deliberately NO password field here