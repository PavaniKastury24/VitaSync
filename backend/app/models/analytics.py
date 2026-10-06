import uuid
from sqlalchemy import (
    Column,
    String,
    Integer,
    Numeric,
    Boolean,
    DateTime,
    Date,
    ForeignKey,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.core.database import Base


class DailySummary(Base):
    """
    Cached analytical summary of a user's 9 wellness dimensions for a specific date,
    including the composite lifestyle score (0-100).
    """
    __tablename__ = "daily_summaries"
    __table_args__ = (
        UniqueConstraint("user_id", "summary_date", name="uq_user_summary_date"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False)
    summary_date = Column(Date, nullable=False)
    total_water_ml = Column(Integer, default=0, nullable=False)
    total_sleep_minutes = Column(Integer, default=0, nullable=False)
    sleep_quality = Column(Integer, default=0, nullable=False)
    total_exercise_minutes = Column(Integer, default=0, nullable=False)
    total_steps = Column(Integer, default=0, nullable=False)
    total_screen_time_minutes = Column(Integer, default=0, nullable=False)
    total_productivity_minutes = Column(Integer, default=0, nullable=False)
    total_meditation_minutes = Column(Integer, default=0, nullable=False)
    average_mood = Column(Numeric(3, 1), nullable=True)
    lifestyle_score = Column(Integer, default=0, nullable=False)
    summary_metadata = Column(JSONB, default=dict, nullable=False)
    calculated_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class AIRecommendation(Base):
    """
    Personalized lifestyle recommendations synthesized by Google Gemini.
    """
    __tablename__ = "ai_recommendations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False)
    date_generated = Column(Date, server_default=func.current_date(), nullable=False)
    category = Column(String(50), nullable=False)  # sleep_optimization, hydration, productivity, screen_balance, holistic
    priority = Column(String(20), default="medium", nullable=False)  # low, medium, high
    title = Column(String(150), nullable=False)
    insight_text = Column(Text, nullable=False)
    actionable_step = Column(Text, nullable=False)
    contributing_factors = Column(JSONB, default=list, nullable=False)
    is_read = Column(Boolean, default=False, nullable=False)
    is_bookmarked = Column(Boolean, default=False, nullable=False)
    user_feedback = Column(Integer, default=0, nullable=False)  # -1, 0, 1
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
