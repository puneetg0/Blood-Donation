"""Pydantic schemas for Donor CRUD operations."""

from datetime import datetime
from pydantic import BaseModel
from app.models.enums import BloodGroup, AvailabilityStatus


class DonorCreate(BaseModel):
    """Data required to create or update a donor profile."""
    blood_group: BloodGroup
    phone_number: str
    city: str
    availability_status: AvailabilityStatus = AvailabilityStatus.available
    consent_to_contact: bool = False


class DonorUpdate(BaseModel):
    """All fields are optional for partial updates."""
    blood_group: BloodGroup | None = None
    phone_number: str | None = None
    city: str | None = None
    availability_status: AvailabilityStatus | None = None
    consent_to_contact: bool | None = None


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
