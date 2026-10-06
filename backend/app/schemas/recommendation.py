from datetime import date
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class AIRecommendationItem(BaseModel):
    """A single prioritised lifestyle recommendation produced by Gemini or the heuristic engine."""
    category: str = Field(
        description="Pillar: sleep | hydration | exercise | focus | screentime | holistic"
    )
    priority: str = Field(
        default="medium",
        description="Priority: low | medium | high",
    )
    title: str = Field(description="Concise, motivating title (max ~10 words)")
    insight_text: str = Field(description="Data-grounded observation with specific metric values")
    actionable_step: str = Field(description="Concrete micro-habit action the user can start today")
    contributing_factors: List[str] = Field(
        default_factory=list,
        description="Metric keys that contributed to this recommendation",
    )


class AIRecommendationRequest(BaseModel):
    """Request body for triggering AI recommendation generation."""
    days_window: int = Field(
        default=7,
        ge=1,
        le=30,
        description="How many days of historical data to analyse",
    )
    focus_category: Optional[str] = Field(
        default=None,
        description="Optional: focus on a specific wellness pillar",
    )


class CorrelationSummary(BaseModel):
    """A detected cross-pillar habit correlation."""
    factor_a: str
    factor_b: str
    strength: str  # strong | moderate | weak
    description: str


class MetricsSnapshot(BaseModel):
    """Anonymised averages fed into the AI prompt."""
    avg_water_ml: float
    target_water_ml: int
    avg_sleep_hours: float
    target_sleep_hours: float
    avg_sleep_quality: float
    avg_steps: int
    target_steps: int
    total_exercise_minutes: int
    exercise_sessions: int
    avg_screen_total_minutes: int
    avg_screen_night_minutes: int
    avg_mood_score: float
    total_meditation_minutes: int
    avg_food_quality: float
    mindful_eating_pct: int


class AIRecommendationResponse(BaseModel):
    """Full AI recommendation response including metadata and lifestyle insights."""
    user_id: str
    generated_at: str
    provider: str = Field(
        description="'Google Gemini (model)' or 'VitaSync Heuristic Engine'"
    )
    data_points_analyzed: int
    recommendations: List[AIRecommendationItem]
    correlations_detected: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Cross-pillar correlations identified by the correlation engine",
    )
    metrics_snapshot: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Anonymised lifestyle averages used for this analysis",
    )
