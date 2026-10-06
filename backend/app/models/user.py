import uuid
from sqlalchemy import (
    Column,
    String,
    Numeric,
    Boolean,
    DateTime,
    ForeignKey,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.core.database import Base


class Profile(Base):
    """
    User profile model extending Supabase auth.users.
    """
    __tablename__ = "profiles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(50), unique=True, nullable=True)
    full_name = Column(String(100), nullable=True)
    avatar_url = Column(Text, nullable=True)
    timezone = Column(String(50), default="UTC", nullable=False)
    metric_units = Column(Boolean, default=True, nullable=False)
    preferences = Column(JSONB, default=dict, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class UserGoal(Base):
    """
    User wellness goal model for setting daily or weekly habit targets.
    """
    __tablename__ = "user_goals"
    __table_args__ = (
        UniqueConstraint("user_id", "metric_type", name="uq_user_goal_metric"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False)
    metric_type = Column(String(30), nullable=False)  # water, sleep_hours, steps, exercise_minutes, etc.
    target_value = Column(Numeric(10, 2), nullable=False)
    unit = Column(String(20), nullable=False)  # ml, hours, steps, minutes
    frequency = Column(String(20), default="daily", nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
