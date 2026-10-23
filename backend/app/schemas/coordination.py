"""Pydantic schemas for DonationCoordination CRUD operations."""

from datetime import datetime
from pydantic import BaseModel
from app.models.enums import CoordinationStatus


class CoordinationCreate(BaseModel):
    """Data required to link a donor to a blood request."""
    request_id: int
    donor_id: int


class CoordinationUpdate(BaseModel):
    """Update the status of a coordination record."""
    coordination_status: CoordinationStatus


class CoordinationOut(BaseModel):
    """Coordination record returned by the API."""
    id: int
    request_id: int
    donor_id: int
    coordination_status: CoordinationStatus
    created_at: datetime

    model_config = {"from_attributes": True}
