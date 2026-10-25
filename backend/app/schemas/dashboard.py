"""Dashboard summary response schema."""

from pydantic import BaseModel


class DashboardSummaryOut(BaseModel):
    total_donors: int
    total_requests: int
    pending_requests: int
    in_progress_requests: int
    fulfilled_requests: int
    cancelled_requests: int
