from datetime import date
from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, Query
from app.core.security import get_current_user
from app.schemas.summary import DailySummaryResponse
from app.services.summary_service import summary_service

router = APIRouter(prefix="/summary", tags=["Daily Summary & Lifestyle Score"])


@router.get("/daily", response_model=DailySummaryResponse)
async def get_daily_summary(
    target_date: Optional[date] = Query(default=None, description="Date for summary (defaults to today)"),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Computes today's multi-dimensional daily summary and composite
    Lifestyle Wellness Score (0-100) based on all logged metrics.
    """
    summary_date = target_date or date.today()
    return await summary_service.get_daily_summary(
        user_id=current_user["id"],
        target_date=summary_date,
    )
