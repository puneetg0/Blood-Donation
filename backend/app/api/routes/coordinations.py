"""Coordination endpoints — link donors to blood requests."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.coordination import CoordinationCreate, CoordinationOut, CoordinationUpdate
from app.services import coordination_service

router = APIRouter(prefix="/coordinations", tags=["coordinations"])


@router.post("/", response_model=CoordinationOut, status_code=201)
def create_coordination(
    payload: CoordinationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Link a donor to a blood request."""
    return coordination_service.create_coordination(payload, current_user, db)


@router.get("/request/{request_id}", response_model=list[CoordinationOut])
def list_coordinations(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all coordination records for a specific blood request."""
    return coordination_service.list_coordinations_for_request(request_id, current_user, db)


@router.get("/{coordination_id}", response_model=CoordinationOut)
def get_coordination(
    coordination_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a single coordination record by ID."""
    return coordination_service.get_coordination_by_id(coordination_id, current_user, db)


@router.patch("/{coordination_id}", response_model=CoordinationOut)
def update_coordination(
    coordination_id: int,
    payload: CoordinationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update the status of a coordination record."""
    return coordination_service.update_coordination(coordination_id, payload, current_user, db)


@router.delete("/{coordination_id}", status_code=204)
def delete_coordination(
    coordination_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Remove a coordination record."""
    coordination_service.delete_coordination(coordination_id, current_user, db)
