"""Role-scoped dashboard summaries."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.dashboard import DashboardSummaryOut
from app.services.dashboard_service import get_dashboard_summary

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/summary", response_model=DashboardSummaryOut)
def summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return counts scoped to the current user's access."""
    return get_dashboard_summary(current_user, db)
