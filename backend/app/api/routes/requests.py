"""Blood request endpoints — create, read, update, delete blood requests."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies.auth import get_current_user
from app.models.enums import BloodGroup, RequestStatus
from app.models.user import User
from app.schemas.blood_request import BloodRequestCreate, BloodRequestOut, BloodRequestUpdate
from app.services import request_service

router = APIRouter(prefix="/requests", tags=["blood-requests"])


@router.post("/", response_model=BloodRequestOut, status_code=201)
def create_request(
    payload: BloodRequestCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new blood request. Requires a logged-in account."""
    return request_service.create_request(current_user.id, payload, db)


@router.get("/", response_model=list[BloodRequestOut])
def list_requests(
    blood_group: BloodGroup | None = Query(default=None),
    city: str | None = Query(default=None),
    status: RequestStatus | None = Query(default=None),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """List all blood requests. Filter by blood group, city, or status."""
    return request_service.list_requests(blood_group, city, status, db)


@router.get("/me", response_model=list[BloodRequestOut])
def list_my_requests(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all requests created by the logged-in user."""
    return request_service.list_my_requests(current_user.id, db)


@router.get("/{request_id}", response_model=BloodRequestOut)
def get_request(
    request_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """Get a single blood request by ID."""
    return request_service.get_request_by_id(request_id, db)


@router.patch("/{request_id}", response_model=BloodRequestOut)
def update_request(
    request_id: int,
    payload: BloodRequestUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a blood request. Only the creator can update it."""
    return request_service.update_request(request_id, current_user.id, payload, db)


@router.delete("/{request_id}", status_code=204)
def delete_request(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a blood request. Only the creator can delete it."""
    request_service.delete_request(request_id, current_user.id, db)
