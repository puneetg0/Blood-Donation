"""Blood request service — CRUD logic for blood requests.

HashMap concept: we use db.get(model, pk) for O(1) primary key lookups,
just like accessing a value in a dictionary by key.
"""

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.user import BloodRequest
from app.models.enums import BloodGroup, RequestStatus
from app.schemas.blood_request import BloodRequestCreate, BloodRequestUpdate


def create_request(requester_id: int, payload: BloodRequestCreate, db: Session) -> BloodRequest:
    """Create a new blood request."""
    request = BloodRequest(requester_id=requester_id, **payload.model_dump())
    db.add(request)
    db.commit()
    db.refresh(request)
    return request


def get_request_by_id(request_id: int, db: Session) -> BloodRequest:
    """Fetch a single blood request by ID — O(1) PK lookup."""
    request = db.get(BloodRequest, request_id)
    if not request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Blood request not found.",
        )
    return request


def list_requests(
    blood_group: BloodGroup | None,
    city: str | None,
    status: RequestStatus | None,
    db: Session,
) -> list[BloodRequest]:
    """Return all blood requests, optionally filtered."""
    query = db.query(BloodRequest)

    if blood_group:
        query = query.filter(BloodRequest.blood_group == blood_group)
    if city:
        query = query.filter(BloodRequest.city.ilike(f"%{city}%"))
    if status:
        query = query.filter(BloodRequest.status == status)

    return query.order_by(BloodRequest.created_at.desc()).all()


def list_my_requests(requester_id: int, db: Session) -> list[BloodRequest]:
    """Return all requests created by the logged-in user."""
    return (
        db.query(BloodRequest)
        .filter(BloodRequest.requester_id == requester_id)
        .order_by(BloodRequest.created_at.desc())
        .all()
    )


def update_request(
    request_id: int, requester_id: int, payload: BloodRequestUpdate, db: Session
) -> BloodRequest:
    """Update a blood request. Only the owner can update it."""
    request = get_request_by_id(request_id, db)

    if request.requester_id != requester_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own requests.",
        )

    for field, value in payload.model_dump(exclude_none=True).items():
        setattr(request, field, value)

    db.commit()
    db.refresh(request)
    return request


def delete_request(request_id: int, requester_id: int, db: Session) -> None:
    """Delete a blood request. Only the owner can delete it."""
    request = get_request_by_id(request_id, db)

    if request.requester_id != requester_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own requests.",
        )

    db.delete(request)
    db.commit()
