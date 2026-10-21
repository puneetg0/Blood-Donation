"""Pydantic schemas for User read/write operations."""

import re
from datetime import datetime

from pydantic import BaseModel, field_validator

from app.models.enums import Role

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def _validate_email(v: str) -> str:
    if not _EMAIL_RE.match(v):
        raise ValueError("Enter a valid email address.")
    return v.lower()


class UserRegister(BaseModel):
    """Payload the client sends to create an account."""

    full_name: str
    email: str
    password: str
    role: Role = Role.requester

    @field_validator("email")
    @classmethod
    def email_valid(cls, v: str) -> str:
        return _validate_email(v)

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters.")
        return v


class UserLogin(BaseModel):
    """Payload the client sends to authenticate."""

    email: str
    password: str

    @field_validator("email")
    @classmethod
    def email_valid(cls, v: str) -> str:
        return _validate_email(v)


class UserOut(BaseModel):
    """Safe user representation returned by the API (no password hash)."""

    id: int
    full_name: str
    email: str
    role: Role
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    """JWT token response returned after a successful login or registration."""

    access_token: str
    token_type: str = "bearer"
    user: UserOut
