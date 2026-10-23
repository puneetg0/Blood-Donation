"""Pydantic schemas for BloodRequest CRUD operations."""

from datetime import datetime
from pydantic import BaseModel, field_validator
from app.models.enums import BloodGroup, Urgency, RequestStatus


class BloodRequestCreate(BaseModel):
    """Data required to create a blood request."""
    blood_group: BloodGroup
    units_required: int
    hospital_name: str
    city: str
    urgency: Urgency = Urgency.routine
    required_by: datetime | None = None

    @field_validator("units_required")
    @classmethod
    def units_must_be_positive(cls, v: int) -> int:
        if v < 1:
            raise ValueError("units_required must be at least 1.")
        return v


class BloodRequestUpdate(BaseModel):
    """All fields are optional for partial updates."""
    units_required: int | None = None
    hospital_name: str | None = None
    city: str | None = None
    urgency: Urgency | None = None
    required_by: datetime | None = None
    status: RequestStatus | None = None


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
