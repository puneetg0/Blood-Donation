"""Blood request service — CRUD logic and request lifecycle rules."""

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.enums import BloodGroup, RequestStatus, Role
from app.models.user import BloodRequest, RequestStatusHistory, User
from app.schemas.blood_request import BloodRequestCreate, BloodRequestUpdate


def _is_admin(user: User) -> bool:
    return user.role == Role.admin


def create_request(
    requester_id: int, payload: BloodRequestCreate, db: Session
) -> BloodRequest:
    request = BloodRequest(requester_id=requester_id, **payload.model_dump())
    db.add(request)
    db.commit()
    db.refresh(request)
    return request


def get_request_by_id(request_id: int, db: Session) -> BloodRequest:
    request = db.get(BloodRequest, request_id)
    if not request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Blood request not found.",
        )
    return request


def get_authorized_request(
    request_id: int, current_user: User, db: Session
) -> BloodRequest:
    request = get_request_by_id(request_id, db)
    can_view = (
        _is_admin(current_user)
        or request.requester_id == current_user.id
        or (
            current_user.role == Role.donor
            and request.status in (RequestStatus.pending, RequestStatus.in_progress)
        )
    )
    if not can_view:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to view this request.",
        )
    return request


def list_requests(
    blood_group: BloodGroup | None,
    city: str | None,
    request_status: RequestStatus | None,
    offset: int,
    limit: int,
    current_user: User,
    db: Session,
) -> list[BloodRequest]:
    query = db.query(BloodRequest)
    if current_user.role == Role.requester:
        query = query.filter(BloodRequest.requester_id == current_user.id)
    elif current_user.role == Role.donor:
        query = query.filter(
            BloodRequest.status.in_(
                (RequestStatus.pending, RequestStatus.in_progress)
            )
        )

    if blood_group:
        query = query.filter(BloodRequest.blood_group == blood_group)
    if city:
        query = query.filter(BloodRequest.city.ilike(f"%{city.strip()}%"))
    if request_status:
        query = query.filter(BloodRequest.status == request_status)

    return (
        query.order_by(BloodRequest.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )


def list_my_requests(requester_id: int, db: Session) -> list[BloodRequest]:
    return (
        db.query(BloodRequest)
        .filter(BloodRequest.requester_id == requester_id)
        .order_by(BloodRequest.created_at.desc())
        .all()
    )


def update_request(
    request_id: int, current_user: User, payload: BloodRequestUpdate, db: Session
) -> BloodRequest:
    request = get_request_by_id(request_id, db)
    is_admin = _is_admin(current_user)
    if not is_admin and request.requester_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own requests.",
        )

    changes = payload.model_dump(exclude_none=True)
    new_status = changes.pop("status", None)
    if changes and not is_admin and request.status in (
        RequestStatus.fulfilled,
        RequestStatus.cancelled,
    ):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Closed requests cannot be edited.",
        )
    if new_status is not None and new_status != request.status:
        allowed_transitions = {
            RequestStatus.pending: {
                RequestStatus.in_progress,
                RequestStatus.cancelled,
            },
            RequestStatus.in_progress: {
                RequestStatus.fulfilled,
                RequestStatus.cancelled,
            },
            RequestStatus.fulfilled: set(),
            RequestStatus.cancelled: set(),
        }
        if new_status not in allowed_transitions[request.status]:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    f"Cannot change request status from {request.status.value} "
                    f"to {new_status.value}."
                ),
            )
        if not is_admin and new_status != RequestStatus.cancelled:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only administrators can advance a request's status.",
            )

    for field, value in changes.items():
        setattr(request, field, value)

    if new_status is not None and new_status != request.status:
        db.add(
            RequestStatusHistory(
                request_id=request.id,
                changed_by=current_user.id,
                previous_status=request.status.value,
                new_status=new_status.value,
            )
        )
        request.status = new_status

    db.commit()
    db.refresh(request)
    return request


def delete_request(request_id: int, current_user: User, db: Session) -> None:
    request = get_request_by_id(request_id, db)
    if not _is_admin(current_user) and request.requester_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own requests.",
        )
    if request.coordinations or request.status_history:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "This request has coordination or status history. "
                "Cancel it instead of deleting it."
            ),
        )
    db.delete(request)
    db.commit()


def get_request_history(
    request_id: int, current_user: User, db: Session
) -> list[RequestStatusHistory]:
    request = get_request_by_id(request_id, db)
    if not _is_admin(current_user) and request.requester_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the requester or an administrator can view status history.",
        )
    return (
        db.query(RequestStatusHistory)
        .filter(RequestStatusHistory.request_id == request_id)
        .order_by(RequestStatusHistory.created_at, RequestStatusHistory.id)
        .all()
    )
