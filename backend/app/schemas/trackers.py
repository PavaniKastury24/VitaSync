from datetime import datetime, date
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict


# ==========================================
# 1. WATER TRACKER SCHEMAS
# ==========================================
class WaterLogCreate(BaseModel):
    amount_ml: int = Field(..., gt=0, le=5000, description="Amount of water consumed in ml")
    logged_at: Optional[datetime] = Field(default=None, description="Timestamp of consumption, defaults to now")


class WaterLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    amount_ml: int
    logged_at: datetime
    created_at: datetime


# ==========================================
# 2. SLEEP TRACKER SCHEMAS
# ==========================================
class SleepLogCreate(BaseModel):
    start_time: datetime = Field(..., description="Time went to bed")
    end_time: datetime = Field(..., description="Time woke up")
    quality_rating: Optional[int] = Field(None, ge=1, le=5, description="Subjective sleep quality score 1-5")
    disruptions_count: int = Field(0, ge=0, description="Number of times awakened")
    notes: Optional[str] = Field(None, max_length=500)
    logged_date: Optional[date] = Field(default=None, description="Date for sleep record")


class SleepLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    start_time: datetime
    end_time: datetime
    duration_minutes: Optional[int] = None
    quality_rating: Optional[int] = None
    disruptions_count: int
    notes: Optional[str] = None
    logged_date: date
    created_at: datetime


# ==========================================
# 3. EXERCISE TRACKER SCHEMAS
# ==========================================
class ExerciseLogCreate(BaseModel):
    exercise_type: str = Field(..., min_length=2, max_length=50, description="e.g. running, weightlifting, yoga")
    duration_minutes: int = Field(..., gt=0, le=1440, description="Duration in minutes")
    intensity_level: Optional[int] = Field(None, ge=1, le=10, description="Perceived exertion 1-10")
    calories_burned: Optional[int] = Field(None, ge=0, description="Estimated calories burned")
    notes: Optional[str] = Field(None, max_length=500)
    logged_at: Optional[datetime] = Field(default=None)


class ExerciseLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    exercise_type: str
    duration_minutes: int
    intensity_level: Optional[int] = None
    calories_burned: Optional[int] = None
    notes: Optional[str] = None
    logged_at: datetime
    created_at: datetime


# ==========================================
# 4. FOOD HABITS SCHEMAS
# ==========================================
class FoodLogCreate(BaseModel):
    meal_type: str = Field(..., pattern="^(breakfast|lunch|dinner|snack)$", description="Type of meal")
    quality_rating: Optional[int] = Field(None, ge=1, le=5, description="Health / nutrient rating 1-5")
    hunger_before: Optional[int] = Field(None, ge=1, le=5, description="Hunger level before eating 1-5")
    mindful_eating: bool = Field(True, description="Eaten without digital distractions")
    notes: Optional[str] = Field(None, max_length=500)
    logged_at: Optional[datetime] = Field(default=None)


class FoodLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    meal_type: str
    quality_rating: Optional[int] = None
    hunger_before: Optional[int] = None
    mindful_eating: bool
    notes: Optional[str] = None
    logged_at: datetime
    created_at: datetime


# ==========================================
# 5. PRODUCTIVITY SCHEMAS
# ==========================================
class ProductivityLogCreate(BaseModel):
    category: str = Field(..., min_length=2, max_length=50, description="e.g. programming, reading, deep work")
    duration_minutes: int = Field(..., gt=0, le=1440, description="Focus duration in minutes")
    focus_rating: Optional[int] = Field(None, ge=1, le=5, description="Subjective focus score 1-5")
    notes: Optional[str] = Field(None, max_length=500)
    logged_date: Optional[date] = Field(default=None)


class ProductivityLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    category: str
    duration_minutes: int
    focus_rating: Optional[int] = None
    notes: Optional[str] = None
    logged_date: date
    created_at: datetime


# ==========================================
# 6. SCREEN TIME SCHEMAS
# ==========================================
class ScreenTimeLogCreate(BaseModel):
    total_minutes: int = Field(..., ge=0, le=1440, description="Total daily screen minutes")
    work_minutes: int = Field(0, ge=0, description="Screen minutes for work/study")
    leisure_minutes: int = Field(0, ge=0, description="Screen minutes for leisure/entertainment")
    night_minutes: int = Field(0, ge=0, description="Screen minutes within 1h of bedtime")
    notes: Optional[str] = Field(None, max_length=500)
    logged_date: Optional[date] = Field(default=None)


class ScreenTimeLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    total_minutes: int
    work_minutes: int
    leisure_minutes: int
    night_minutes: int
    notes: Optional[str] = None
    logged_date: date
    created_at: datetime


# ==========================================
# 7. MOOD SCHEMAS
# ==========================================
class MoodLogCreate(BaseModel):
    score: int = Field(..., ge=1, le=10, description="Mood score 1 (lowest) to 10 (highest)")
    energy_level: Optional[int] = Field(None, ge=1, le=5, description="Energy rating 1-5")
    tags: List[str] = Field(default_factory=list, description="Tags like energized, calm, stressed")
    notes: Optional[str] = Field(None, max_length=500)
    logged_at: Optional[datetime] = Field(default=None)


class MoodLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    score: int
    energy_level: Optional[int] = None
    tags: List[str] = Field(default_factory=list)
    notes: Optional[str] = None
    logged_at: datetime
    created_at: datetime


# ==========================================
# 8. MEDITATION SCHEMAS
# ==========================================
class MeditationLogCreate(BaseModel):
    duration_minutes: int = Field(..., gt=0, le=360, description="Duration in minutes")
    technique: str = Field(default="mindfulness", max_length=50, description="mindfulness, breathwork, etc.")
    calmness_rating: Optional[int] = Field(None, ge=1, le=5, description="Post-session calm rating 1-5")
    notes: Optional[str] = Field(None, max_length=500)
    logged_at: Optional[datetime] = Field(default=None)


class MeditationLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    duration_minutes: int
    technique: str
    calmness_rating: Optional[int] = None
    notes: Optional[str] = None
    logged_at: datetime
    created_at: datetime


# ==========================================
# 9. STEP SCHEMAS
# ==========================================
class StepLogCreate(BaseModel):
    step_count: int = Field(..., ge=0, le=100000, description="Total daily steps")
    distance_meters: Optional[int] = Field(None, ge=0, description="Distance in meters")
    active_duration_minutes: Optional[int] = Field(None, ge=0, description="Active moving minutes")
    logged_date: Optional[date] = Field(default=None)


class StepLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    step_count: int
    distance_meters: Optional[int] = None
    active_duration_minutes: Optional[int] = None
    logged_date: date
    created_at: datetime


# ==========================================
# 10. USER GOAL SCHEMAS
# ==========================================
class UserGoalCreate(BaseModel):
    metric_type: str = Field(..., min_length=2, max_length=30)
    target_value: float = Field(..., gt=0)
    unit: str = Field(..., max_length=20)
    frequency: str = Field(default="daily", pattern="^(daily|weekly)$")


class UserGoalResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    metric_type: str
    target_value: float
    unit: str
    frequency: str
    is_active: bool
    created_at: datetime
