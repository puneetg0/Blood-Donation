"""Pydantic schemas for Donor CRUD operations."""

import re
from datetime import datetime
from pydantic import BaseModel, Field, field_validator
from app.models.enums import BloodGroup, AvailabilityStatus

_PHONE_RE = re.compile(r"^\+?[0-9][0-9\s().-]{5,24}$")


def _validate_phone(value: str) -> str:
    value = value.strip()
    if not _PHONE_RE.fullmatch(value) or sum(char.isdigit() for char in value) < 7:
        raise ValueError("Enter a valid phone number.")
    return value


def _validate_city(value: str) -> str:
    value = value.strip()
    if len(value) < 2:
        raise ValueError("City must contain at least 2 characters.")
    return value


class DonorCreate(BaseModel):
    """Data required to create or update a donor profile."""
    blood_group: BloodGroup
    phone_number: str = Field(min_length=7, max_length=25)
    city: str = Field(min_length=2, max_length=100)
    availability_status: AvailabilityStatus = AvailabilityStatus.available
    consent_to_contact: bool = False

    @field_validator("phone_number")
    @classmethod
    def phone_is_valid(cls, value: str) -> str:
        return _validate_phone(value)

    @field_validator("city")
    @classmethod
    def city_is_not_blank(cls, value: str) -> str:
        return _validate_city(value)


class DonorUpdate(BaseModel):
    """All fields are optional for partial updates."""
    blood_group: BloodGroup | None = None
    phone_number: str | None = Field(default=None, min_length=7, max_length=25)
    city: str | None = Field(default=None, min_length=2, max_length=100)
    availability_status: AvailabilityStatus | None = None
    consent_to_contact: bool | None = None

    @field_validator("phone_number")
    @classmethod
    def phone_is_valid(cls, value: str | None) -> str | None:
        return _validate_phone(value) if value is not None else None

    @field_validator("city")
    @classmethod
    def city_is_not_blank(cls, value: str | None) -> str | None:
        return _validate_city(value) if value is not None else None


class DonorOut(BaseModel):
    """Donor profile returned by the API."""
    id: int
    user_id: int
    blood_group: BloodGroup
    phone_number: str
    city: str
    availability_status: AvailabilityStatus
    consent_to_contact: bool
    updated_at: datetime

    model_config = {"from_attributes": True}


class DonorSearchOut(BaseModel):
    """Minimal donor listing; contact details are never exposed by search."""

    id: int
    blood_group: BloodGroup
    city: str
    availability_status: AvailabilityStatus

    model_config = {"from_attributes": True}
