"""Donor endpoints — create, read, update, delete donor profiles."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies.auth import get_current_user
from app.models.enums import AvailabilityStatus, BloodGroup
from app.models.user import User
from app.schemas.donor import DonorCreate, DonorOut, DonorSearchOut, DonorUpdate
from app.services import donor_service

router = APIRouter(prefix="/donors", tags=["donors"])


@router.post("/", response_model=DonorOut, status_code=201)
def create_donor(
    payload: DonorCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Register yourself as a donor. Requires a logged-in account."""
    return donor_service.create_donor(current_user, payload, db)


@router.get("/", response_model=list[DonorSearchOut])
def list_donors(
    blood_group: BloodGroup | None = Query(default=None),
    city: str | None = Query(default=None),
    availability_status: AvailabilityStatus = Query(default=AvailabilityStatus.available),
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),  # must be logged in to search
):
    """Search consenting donors without exposing their private contact details."""
    return donor_service.list_donors(
        blood_group, city, availability_status, offset, limit, db
    )


@router.get("/me", response_model=DonorOut)
def get_my_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get your own donor profile."""
    return donor_service.get_my_donor_profile(current_user.id, db)


@router.get("/{donor_id}", response_model=DonorOut)
def get_donor(
    donor_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get your own profile, or a donor profile as an administrator."""
    return donor_service.get_donor_by_id(donor_id, current_user, db)


@router.patch("/{donor_id}", response_model=DonorOut)
def update_donor(
    donor_id: int,
    payload: DonorUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update your donor profile."""
    return donor_service.update_donor(donor_id, current_user, payload, db)


@router.delete("/{donor_id}", status_code=204)
def delete_donor(
    donor_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete your donor profile."""
    donor_service.delete_donor(donor_id, current_user, db)
