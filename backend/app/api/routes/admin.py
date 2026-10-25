"""Administrator-only operational endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies.auth import require_role
from app.models.enums import Role
from app.models.user import User
from app.schemas.dashboard import DashboardSummaryOut
from app.services.dashboard_service import get_dashboard_summary

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/dashboard", response_model=DashboardSummaryOut)
def dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(Role.admin)),
):
    """Return system-wide totals for administrators."""
    return get_dashboard_summary(current_user, db)
