"""Coordination service — links donors to blood requests."""

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.user import DonationCoordination, BloodRequest, Donor
from app.schemas.coordination import CoordinationCreate, CoordinationUpdate


def create_coordination(payload: CoordinationCreate, db: Session) -> DonationCoordination:
    """Link a donor to a blood request."""
    # Make sure the request and donor actually exist
    if not db.get(BloodRequest, payload.request_id):
        raise HTTPException(status_code=404, detail="Blood request not found.")
    if not db.get(Donor, payload.donor_id):
        raise HTTPException(status_code=404, detail="Donor not found.")

    # Prevent duplicate coordination entries
    existing = (
        db.query(DonationCoordination)
        .filter(
            DonationCoordination.request_id == payload.request_id,
            DonationCoordination.donor_id == payload.donor_id,
        )
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This donor is already linked to this request.",
        )

    coordination = DonationCoordination(**payload.model_dump())
    db.add(coordination)
    db.commit()
    db.refresh(coordination)
    return coordination


def get_coordination_by_id(coordination_id: int, db: Session) -> DonationCoordination:
    """Fetch a single coordination record by ID."""
    coordination = db.get(DonationCoordination, coordination_id)
    if not coordination:
        raise HTTPException(status_code=404, detail="Coordination record not found.")
    return coordination


def list_coordinations_for_request(request_id: int, db: Session) -> list[DonationCoordination]:
    """Return all coordination records for a specific blood request."""
    return (
        db.query(DonationCoordination)
        .filter(DonationCoordination.request_id == request_id)
        .all()
    )


def update_coordination(
    coordination_id: int, payload: CoordinationUpdate, db: Session
) -> DonationCoordination:
    """Update the status of a coordination record."""
    coordination = get_coordination_by_id(coordination_id, db)
    coordination.coordination_status = payload.coordination_status
    db.commit()
    db.refresh(coordination)
    return coordination


def delete_coordination(coordination_id: int, db: Session) -> None:
    """Remove a coordination record."""
    coordination = get_coordination_by_id(coordination_id, db)
    db.delete(coordination)
    db.commit()
