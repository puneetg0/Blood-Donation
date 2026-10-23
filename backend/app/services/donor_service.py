"""Donor service — CRUD logic for donor profiles.

HashMap concept: the DB primary key acts like a hash map key.
We do O(1)-style lookups using .get(id) rather than scanning all rows.
"""

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.user import Donor
from app.models.enums import BloodGroup
from app.schemas.donor import DonorCreate, DonorUpdate


def create_donor(user_id: int, payload: DonorCreate, db: Session) -> Donor:
    """Create a donor profile for the logged-in user."""
    # One user can only have one donor profile
    existing = db.query(Donor).filter(Donor.user_id == user_id).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="You already have a donor profile.",
        )

    donor = Donor(user_id=user_id, **payload.model_dump())
    db.add(donor)
    db.commit()
    db.refresh(donor)
    return donor


def get_donor_by_id(donor_id: int, db: Session) -> Donor:
    """Fetch a single donor by ID — like a hash map key lookup."""
    donor = db.get(Donor, donor_id)  # db.get() is the O(1) PK lookup
    if not donor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Donor not found.",
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


def list_donors(blood_group: BloodGroup | None, city: str | None, db: Session) -> list[Donor]:
    """Return all available donors, optionally filtered by blood group and city."""
    query = db.query(Donor)

    if blood_group:
        query = query.filter(Donor.blood_group == blood_group)
    if city:
        # Case-insensitive city filter
        query = query.filter(Donor.city.ilike(f"%{city}%"))

    return query.all()


def update_donor(donor_id: int, user_id: int, payload: DonorUpdate, db: Session) -> Donor:
    """Update a donor profile. Only the owner can update it."""
    donor = get_donor_by_id(donor_id, db)

    if donor.user_id != user_id:
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


def delete_donor(donor_id: int, user_id: int, db: Session) -> None:
    """Delete a donor profile. Only the owner can delete it."""
    donor = get_donor_by_id(donor_id, db)

    if donor.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own donor profile.",
        )

    db.delete(donor)
    db.commit()
