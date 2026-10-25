"""Pydantic schemas for User read/write operations."""

import re
from datetime import datetime

from pydantic import BaseModel, Field, field_validator

from app.models.enums import Role

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def _validate_email(v: str) -> str:
    v = v.strip()
    if not _EMAIL_RE.match(v):
        raise ValueError("Enter a valid email address.")
    return v.lower()


class UserRegister(BaseModel):
    """Payload the client sends to create an account."""

    full_name: str = Field(min_length=2, max_length=100)
    email: str = Field(max_length=254)
    password: str = Field(min_length=8)
    role: Role = Role.requester

    @field_validator("full_name")
    @classmethod
    def name_is_not_blank(cls, value: str) -> str:
        value = value.strip()
        if len(value) < 2:
            raise ValueError("Full name must contain at least 2 characters.")
        return value

    @field_validator("email")
    @classmethod
    def email_valid(cls, v: str) -> str:
        return _validate_email(v)

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if len(v.encode("utf-8")) > 72:
            raise ValueError("Password must be no more than 72 bytes.")
        return v

    @field_validator("role")
    @classmethod
    def public_registration_role(cls, value: Role) -> Role:
        if value == Role.admin:
            raise ValueError("Administrator accounts must be provisioned by an administrator.")
        return value


class UserLogin(BaseModel):
    """Payload the client sends to authenticate."""

    email: str = Field(max_length=254)
    password: str

    @field_validator("email")
    @classmethod
    def email_valid(cls, v: str) -> str:
        return _validate_email(v)

    @field_validator("password")
    @classmethod
    def password_supported_by_hashing(cls, value: str) -> str:
        if len(value.encode("utf-8")) > 72:
            raise ValueError("Password must be no more than 72 bytes.")
        return value


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
