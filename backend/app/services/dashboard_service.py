"""Dashboard aggregates scoped to the current user's permissions."""

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.enums import AvailabilityStatus, RequestStatus, Role
from app.models.user import BloodRequest, Donor, User
from app.schemas.dashboard import DashboardSummaryOut


def get_dashboard_summary(current_user: User, db: Session) -> DashboardSummaryOut:
    donor_query = db.query(func.count(Donor.id))
    if current_user.role != Role.admin:
        donor_query = donor_query.filter(
            Donor.consent_to_contact.is_(True),
            Donor.availability_status == AvailabilityStatus.available,
        )

    request_query = db.query(BloodRequest.status, func.count(BloodRequest.id))
    if current_user.role == Role.requester:
        request_query = request_query.filter(
            BloodRequest.requester_id == current_user.id
        )
    elif current_user.role == Role.donor:
        request_query = request_query.filter(
            BloodRequest.status.in_(
                (RequestStatus.pending, RequestStatus.in_progress)
            )
        )

    request_counts = dict(request_query.group_by(BloodRequest.status).all())
    total_requests = sum(request_counts.values())
    return DashboardSummaryOut(
        total_donors=donor_query.scalar() or 0,
        total_requests=total_requests,
        pending_requests=request_counts.get(RequestStatus.pending, 0),
        in_progress_requests=request_counts.get(RequestStatus.in_progress, 0),
        fulfilled_requests=request_counts.get(RequestStatus.fulfilled, 0),
        cancelled_requests=request_counts.get(RequestStatus.cancelled, 0),
    )
