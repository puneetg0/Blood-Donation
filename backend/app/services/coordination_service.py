"""Coordination service — links consenting donors to blood requests."""

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.enums import AvailabilityStatus, Role
from app.models.user import BloodRequest, DonationCoordination, Donor, User
from app.schemas.coordination import CoordinationCreate, CoordinationUpdate


def _can_manage_request(user: User) -> bool:
    return user.role == Role.admin


def create_coordination(
    payload: CoordinationCreate, current_user: User, db: Session
) -> DonationCoordination:
    request = db.get(BloodRequest, payload.request_id)
    if not request:
        raise HTTPException(status_code=404, detail="Blood request not found.")
    if not _can_manage_request(current_user):
        raise HTTPException(status_code=403, detail="Only administrators can manage donation coordination.")
    donor = db.get(Donor, payload.donor_id)
    if not donor:
        raise HTTPException(status_code=404, detail="Donor not found.")
    if not donor.consent_to_contact or donor.availability_status != AvailabilityStatus.available:
        raise HTTPException(
            status_code=409,
            detail="Only available donors who consented to contact can be linked.",
        )
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
    try:
        db.commit()
    except IntegrityError as error:
        db.rollback()
        if (
            db.query(DonationCoordination)
            .filter(
                DonationCoordination.request_id == payload.request_id,
                DonationCoordination.donor_id == payload.donor_id,
            )
            .first()
        ):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="This donor is already linked to this request.",
            ) from error
        raise
    db.refresh(coordination)
    return coordination


def get_coordination_by_id(
    coordination_id: int, current_user: User, db: Session
) -> DonationCoordination:
    coordination = db.get(DonationCoordination, coordination_id)
    if not coordination:
        raise HTTPException(status_code=404, detail="Coordination record not found.")
    if not _can_manage_request(current_user):
        raise HTTPException(status_code=403, detail="Not authorized.")
    return coordination


def list_coordinations_for_request(
    request_id: int, current_user: User, db: Session
) -> list[DonationCoordination]:
    request = db.get(BloodRequest, request_id)
    if not request:
        raise HTTPException(status_code=404, detail="Blood request not found.")
    if not _can_manage_request(current_user):
        raise HTTPException(status_code=403, detail="Not authorized.")
    return (
        db.query(DonationCoordination)
        .filter(DonationCoordination.request_id == request_id)
        .order_by(DonationCoordination.created_at)
        .all()
    )


def update_coordination(
    coordination_id: int,
    payload: CoordinationUpdate,
    current_user: User,
    db: Session,
) -> DonationCoordination:
    coordination = get_coordination_by_id(coordination_id, current_user, db)
    current_status = coordination.coordination_status
    new_status = payload.coordination_status
    transitions = {
        "contact_pending": {"contacted"},
        "contacted": {"declined", "completed"},
        "declined": set(),
        "completed": set(),
    }
    if new_status != current_status and new_status.value not in transitions[current_status.value]:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Cannot change coordination from {current_status.value} to {new_status.value}.",
        )
    coordination.coordination_status = new_status
    db.commit()
    db.refresh(coordination)
    return coordination


def delete_coordination(
    coordination_id: int, current_user: User, db: Session
) -> None:
    coordination = get_coordination_by_id(coordination_id, current_user, db)
    db.delete(coordination)
    db.commit()
