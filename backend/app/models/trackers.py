import uuid
from sqlalchemy import (
    Column,
    String,
    Integer,
    Boolean,
    DateTime,
    Date,
    ForeignKey,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from app.core.database import Base


class WaterLog(Base):
    """
    Tracks water intake in milliliters.
    """
    __tablename__ = "water_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False)
    amount_ml = Column(Integer, nullable=False)
    logged_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class SleepLog(Base):
    """
    Tracks sleep duration, timing, disruptions, and quality rating (1-5).
    """
    __tablename__ = "sleep_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False)
    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=False)
    duration_minutes = Column(Integer, nullable=True)
    quality_rating = Column(Integer, nullable=True)  # 1 to 5
    disruptions_count = Column(Integer, default=0, nullable=False)
    notes = Column(Text, nullable=True)
    logged_date = Column(Date, server_default=func.current_date(), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class ExerciseLog(Base):
    """
    Tracks workout sessions, duration, intensity (RPE 1-10), and calories burned.
    """
    __tablename__ = "exercise_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False)
    exercise_type = Column(String(50), nullable=False)  # running, cycling, weightlifting, yoga
    duration_minutes = Column(Integer, nullable=False)
    intensity_level = Column(Integer, nullable=True)  # 1 to 10
    calories_burned = Column(Integer, nullable=True)
    notes = Column(Text, nullable=True)
    logged_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class FoodLog(Base):
    """
    Tracks meals, nutritional health rating (1-5), and mindful eating practices.
    """
    __tablename__ = "food_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False)
    meal_type = Column(String(20), nullable=False)  # breakfast, lunch, dinner, snack
    quality_rating = Column(Integer, nullable=True)  # 1 to 5
    hunger_before = Column(Integer, nullable=True)  # 1 to 5
    mindful_eating = Column(Boolean, default=True, nullable=False)
    notes = Column(Text, nullable=True)
    logged_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class ProductivityLog(Base):
    """
    Tracks focused study and work intervals with categories and focus ratings.
    """
    __tablename__ = "productivity_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False)
    category = Column(String(50), nullable=False)  # coding, study, reading, writing
    duration_minutes = Column(Integer, nullable=False)
    focus_rating = Column(Integer, nullable=True)  # 1 to 5
    notes = Column(Text, nullable=True)
    logged_date = Column(Date, server_default=func.current_date(), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class ScreenTimeLog(Base):
    """
    Tracks daily digital screen exposure (work vs leisure vs late-night).
    """
    __tablename__ = "screen_time_logs"
    __table_args__ = (
        UniqueConstraint("user_id", "logged_date", name="uq_user_screentime_date"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False)
    total_minutes = Column(Integer, nullable=False)
    work_minutes = Column(Integer, default=0, nullable=False)
    leisure_minutes = Column(Integer, default=0, nullable=False)
    night_minutes = Column(Integer, default=0, nullable=False)  # within 1 hour of sleep
    notes = Column(Text, nullable=True)
    logged_date = Column(Date, server_default=func.current_date(), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class MoodLog(Base):
    """
    Tracks emotional valence (1-10), energy levels (1-5), and emotional tags.
    """
    __tablename__ = "mood_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False)
    score = Column(Integer, nullable=False)  # 1 to 10
    energy_level = Column(Integer, nullable=True)  # 1 to 5
    tags = Column(ARRAY(String), default=list, nullable=True)
    notes = Column(Text, nullable=True)
    logged_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class MeditationLog(Base):
    """
    Tracks mindfulness and meditation duration, technique, and calmness score.
    """
    __tablename__ = "meditation_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False)
    duration_minutes = Column(Integer, nullable=False)
    technique = Column(String(50), default="mindfulness", nullable=False)
    calmness_rating = Column(Integer, nullable=True)  # 1 to 5
    notes = Column(Text, nullable=True)
    logged_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class StepLog(Base):
    """
    Tracks daily physical step count, distance, and active minutes.
    """
    __tablename__ = "step_logs"
    __table_args__ = (
        UniqueConstraint("user_id", "logged_date", name="uq_user_step_date"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False)
    step_count = Column(Integer, nullable=False)
    distance_meters = Column(Integer, nullable=True)
    active_duration_minutes = Column(Integer, nullable=True)
    logged_date = Column(Date, server_default=func.current_date(), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
