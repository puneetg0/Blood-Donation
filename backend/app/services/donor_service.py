"""Donor service — CRUD logic for donor profiles.

HashMap concept: the DB primary key acts like a hash map key.
We do O(1)-style lookups using .get(id) rather than scanning all rows.
"""

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.user import Donor, User
from app.models.enums import AvailabilityStatus, BloodGroup, Role
from app.schemas.donor import DonorCreate, DonorUpdate


def create_donor(current_user: User, payload: DonorCreate, db: Session) -> Donor:
    """Create a donor profile for the logged-in user."""
    if current_user.role != Role.donor:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only donor accounts can create a donor profile.",
        )

    existing = db.query(Donor).filter(Donor.user_id == current_user.id).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="You already have a donor profile.",
        )

    donor = Donor(user_id=current_user.id, **payload.model_dump())
    db.add(donor)
    try:
        db.commit()
    except IntegrityError as error:
        db.rollback()
        if db.query(Donor).filter(Donor.user_id == current_user.id).first():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="You already have a donor profile.",
            ) from error
        raise
    db.refresh(donor)
    return donor


def get_donor_by_id(donor_id: int, current_user: User, db: Session) -> Donor:
    """Fetch a donor profile only for its owner or an administrator."""
    donor = db.get(Donor, donor_id)  # db.get() is the O(1) PK lookup
    if not donor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Donor not found.",
        )
    if current_user.role != Role.admin and donor.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view your own donor profile.",
        )
    return donor


def get_my_donor_profile(user_id: int, db: Session) -> Donor:
    """Fetch the donor profile belonging to the logged-in user."""
    donor = db.query(Donor).filter(Donor.user_id == user_id).first()
    if not donor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="You do not have a donor profile yet.",
        )
    return donor


def list_donors(
    blood_group: BloodGroup | None,
    city: str | None,
    availability_status: AvailabilityStatus,
    offset: int,
    limit: int,
    db: Session,
) -> list[Donor]:
    """Search only consenting donors and return only the requested public fields."""
    query = db.query(Donor).filter(Donor.consent_to_contact.is_(True))

    if blood_group:
        query = query.filter(Donor.blood_group == blood_group)
    if availability_status:
        query = query.filter(Donor.availability_status == availability_status)
    if city:
        query = query.filter(Donor.city.ilike(f"%{city}%"))

    return query.order_by(Donor.city, Donor.id).offset(offset).limit(limit).all()


def update_donor(
    donor_id: int, current_user: User, payload: DonorUpdate, db: Session
) -> Donor:
    """Update a donor profile. Only its owner or an administrator can update it."""
    donor = db.get(Donor, donor_id)
    if not donor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Donor not found.")
    if current_user.role != Role.admin and donor.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own donor profile.",
        )

    # Apply only the fields that were actually sent
    for field, value in payload.model_dump(exclude_none=True).items():
        setattr(donor, field, value)

    db.commit()
    db.refresh(donor)
    return donor


def delete_donor(donor_id: int, current_user: User, db: Session) -> None:
    """Delete a donor profile. Only its owner or an administrator can delete it."""
    donor = db.get(Donor, donor_id)
    if not donor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Donor not found.")
    if current_user.role != Role.admin and donor.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own donor profile.",
        )
    if donor.coordinations:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This donor has coordination history and cannot be deleted.",
        )

    db.delete(donor)
    db.commit()
