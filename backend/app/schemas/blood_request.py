"""Pydantic schemas for BloodRequest CRUD operations."""

from datetime import datetime
from pydantic import BaseModel, Field, field_validator
from app.models.enums import BloodGroup, Urgency, RequestStatus


class BloodRequestCreate(BaseModel):
    """Data required to create a blood request."""
    blood_group: BloodGroup
    units_required: int = Field(ge=1)
    hospital_name: str = Field(min_length=2, max_length=150)
    city: str = Field(min_length=2, max_length=100)
    urgency: Urgency = Urgency.routine
    required_by: datetime | None = None

    @field_validator("hospital_name", "city")
    @classmethod
    def text_is_not_blank(cls, value: str) -> str:
        value = value.strip()
        if len(value) < 2:
            raise ValueError("Enter at least 2 non-whitespace characters.")
        return value


class BloodRequestUpdate(BaseModel):
    """All fields are optional for partial updates."""
    blood_group: BloodGroup | None = None
    units_required: int | None = Field(default=None, ge=1)
    hospital_name: str | None = Field(default=None, min_length=2, max_length=150)
    city: str | None = Field(default=None, min_length=2, max_length=100)
    urgency: Urgency | None = None
    required_by: datetime | None = None
    status: RequestStatus | None = None

    @field_validator("hospital_name", "city")
    @classmethod
    def text_is_not_blank(cls, value: str | None) -> str | None:
        if value is None:
            return value
        value = value.strip()
        if len(value) < 2:
            raise ValueError("Enter at least 2 non-whitespace characters.")
        return value

class BloodRequestOut(BaseModel):
    """Blood request returned by the API."""
    id: int
    requester_id: int
    blood_group: BloodGroup
    units_required: int
    hospital_name: str
    city: str
    urgency: Urgency
    required_by: datetime | None
    status: RequestStatus
    created_at: datetime

    model_config = {"from_attributes": True}


class RequestStatusHistoryOut(BaseModel):
    id: int
    request_id: int
    changed_by: int
    previous_status: str | None
    new_status: str
    note: str | None
    created_at: datetime

    model_config = {"from_attributes": True}
