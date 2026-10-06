from typing import Any, Dict, Optional
from fastapi import APIRouter, Depends, Query, status
from app.core.security import get_current_user
from app.schemas.recommendation import AIRecommendationRequest, AIRecommendationResponse
from app.services.ai_recommender import ai_recommender_service

router = APIRouter(prefix="/recommendations", tags=["AI Recommendations"])


@router.post("/generate", response_model=AIRecommendationResponse, status_code=status.HTTP_200_OK)
async def generate_recommendations(
    request: AIRecommendationRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Generates personalised lifestyle recommendations for the authenticated user.

    **Full pipeline:**
    1. Aggregates the past `days_window` days of logs from all 9 wellness trackers.
    2. Runs the VitaSync Correlation Engine to detect cross-pillar habit patterns
       (e.g. late-night screen time ↔ sleep disruptions, step count ↔ mood).
    3. Sends anonymised metrics to Google Gemini (gemini-2.5-flash) with a
       strict structured-JSON prompt.
    4. If Gemini is unavailable or unconfigured, falls back to the built-in
       heuristic rule engine — ensuring offline development always works.

    Returns 2–4 prioritised recommendations (High / Medium / Low) each with:
    - A data-grounded insight citing specific metric values
    - One concrete micro-habit action to take today
    - The detected cross-pillar correlations that drove the analysis
    """
    return await ai_recommender_service.generate_lifestyle_recommendations(
        user_id=current_user["id"],
        days_window=request.days_window,
    )


@router.get("/status", status_code=status.HTTP_200_OK)
async def recommendations_status(
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Returns the current AI engine status — whether Gemini is configured
    or the heuristic fallback engine is active.
    """
    return {
        "gemini_configured": ai_recommender_service.is_configured(),
        "active_engine": (
            f"Google Gemini ({ai_recommender_service.model_name})"
            if ai_recommender_service.is_configured()
            else "VitaSync Heuristic Engine (set GEMINI_API_KEY to enable AI)"
        ),
        "user_id": current_user["id"],
        "is_dev_mode": current_user.get("is_dev_mode", False),
    }
