from datetime import date
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class WellnessScoreBreakdown(BaseModel):
    hydration_score: float = Field(..., ge=0, le=15, description="Score out of 15 based on water goal")
    sleep_score: float = Field(..., ge=0, le=20, description="Score out of 20 based on sleep duration & quality")
    movement_score: float = Field(..., ge=0, le=15, description="Score out of 15 based on steps & exercise")
    nutrition_score: float = Field(..., ge=0, le=15, description="Score out of 15 based on food quality & mindfulness")
    screen_hygiene_score: float = Field(..., ge=0, le=15, description="Score out of 15 based on screen limits & night use")
    mental_wellness_score: float = Field(..., ge=0, le=20, description="Score out of 20 based on mood & meditation")
    total_lifestyle_score: int = Field(..., ge=0, le=100, description="Composite wellness score 0 to 100")
    grade: str = Field(..., description="e.g. Optimal, Good, Balanced, Needs Attention")


class DailySummaryMetrics(BaseModel):
    summary_date: date
    water_ml: int = 0
    water_goal_ml: int = 2500
    water_percent: int = 0
    sleep_minutes: int = 0
    sleep_hours: float = 0.0
    sleep_quality: Optional[int] = None
    exercise_minutes: int = 0
    exercise_sessions: int = 0
    calories_burned: int = 0
    meals_logged: int = 0
    avg_food_quality: Optional[float] = None
    productivity_minutes: int = 0
    screen_total_minutes: int = 0
    screen_night_minutes: int = 0
    mood_score: Optional[float] = None
    mood_tags: List[str] = Field(default_factory=list)
    meditation_minutes: int = 0
    steps: int = 0
    step_goal: int = 10000
    step_percent: int = 0


class DailySummaryResponse(BaseModel):
    user_id: str
    summary_date: date
    lifestyle_score: int
    score_breakdown: WellnessScoreBreakdown
    metrics: DailySummaryMetrics
    highlights: List[str]
