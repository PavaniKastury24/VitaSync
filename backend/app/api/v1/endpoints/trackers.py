from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, Query, status
from app.core.security import get_current_user
from app.schemas.trackers import (
    WaterLogCreate,
    WaterLogResponse,
    SleepLogCreate,
    SleepLogResponse,
    ExerciseLogCreate,
    ExerciseLogResponse,
    FoodLogCreate,
    FoodLogResponse,
    ProductivityLogCreate,
    ProductivityLogResponse,
    ScreenTimeLogCreate,
    ScreenTimeLogResponse,
    MoodLogCreate,
    MoodLogResponse,
    MeditationLogCreate,
    MeditationLogResponse,
    StepLogCreate,
    StepLogResponse,
    UserGoalCreate,
    UserGoalResponse,
)
from app.services.tracker_service import tracker_service

router = APIRouter(prefix="/trackers", tags=["Health Trackers"])


# 1. WATER TRACKER
@router.post("/water", response_model=WaterLogResponse, status_code=status.HTTP_201_CREATED)
async def log_water(
    payload: WaterLogCreate,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Log water intake in milliliters."""
    return await tracker_service.log_water(user_id=current_user["id"], data=payload)


@router.get("/water", response_model=List[WaterLogResponse])
async def get_water_logs(
    limit: int = Query(default=30, ge=1, le=100),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Retrieve recent water intake logs."""
    return await tracker_service.get_water_logs(user_id=current_user["id"], limit=limit)


# 2. SLEEP TRACKER
@router.post("/sleep", response_model=SleepLogResponse, status_code=status.HTTP_201_CREATED)
async def log_sleep(
    payload: SleepLogCreate,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Log sleep session timing, disruptions, and quality rating."""
    return await tracker_service.log_sleep(user_id=current_user["id"], data=payload)


@router.get("/sleep", response_model=List[SleepLogResponse])
async def get_sleep_logs(
    limit: int = Query(default=30, ge=1, le=60),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Retrieve recent sleep logs."""
    return await tracker_service.get_sleep_logs(user_id=current_user["id"], limit=limit)


# 3. EXERCISE TRACKER
@router.post("/exercise", response_model=ExerciseLogResponse, status_code=status.HTTP_201_CREATED)
async def log_exercise(
    payload: ExerciseLogCreate,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Log workout session, duration, exertion, and calories."""
    return await tracker_service.log_exercise(user_id=current_user["id"], data=payload)


@router.get("/exercise", response_model=List[ExerciseLogResponse])
async def get_exercise_logs(
    limit: int = Query(default=30, ge=1, le=100),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Retrieve recent exercise logs."""
    return await tracker_service.get_exercise_logs(user_id=current_user["id"], limit=limit)


# 4. FOOD HABITS TRACKER
@router.post("/food", response_model=FoodLogResponse, status_code=status.HTTP_201_CREATED)
async def log_food(
    payload: FoodLogCreate,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Log meal type, nutritional score, and mindful eating habits."""
    return await tracker_service.log_food(user_id=current_user["id"], data=payload)


@router.get("/food", response_model=List[FoodLogResponse])
async def get_food_logs(
    limit: int = Query(default=30, ge=1, le=100),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Retrieve recent meal logs."""
    return await tracker_service.get_food_logs(user_id=current_user["id"], limit=limit)


# 5. PRODUCTIVITY TRACKER
@router.post("/productivity", response_model=ProductivityLogResponse, status_code=status.HTTP_201_CREATED)
async def log_productivity(
    payload: ProductivityLogCreate,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Log focused study/work session and focus rating."""
    return await tracker_service.log_productivity(user_id=current_user["id"], data=payload)


@router.get("/productivity", response_model=List[ProductivityLogResponse])
async def get_productivity_logs(
    limit: int = Query(default=30, ge=1, le=100),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Retrieve recent productivity logs."""
    return await tracker_service.get_productivity_logs(user_id=current_user["id"], limit=limit)


# 6. SCREEN TIME TRACKER
@router.post("/screen-time", response_model=ScreenTimeLogResponse, status_code=status.HTTP_201_CREATED)
async def log_screen_time(
    payload: ScreenTimeLogCreate,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Log total screen minutes, work vs leisure, and late-night usage."""
    return await tracker_service.log_screen_time(user_id=current_user["id"], data=payload)


@router.get("/screen-time", response_model=List[ScreenTimeLogResponse])
async def get_screen_time_logs(
    limit: int = Query(default=30, ge=1, le=60),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Retrieve recent screen time logs."""
    return await tracker_service.get_screen_time_logs(user_id=current_user["id"], limit=limit)


# 7. MOOD TRACKER
@router.post("/mood", response_model=MoodLogResponse, status_code=status.HTTP_201_CREATED)
async def log_mood(
    payload: MoodLogCreate,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Log emotional valence, energy levels, and mood tags."""
    return await tracker_service.log_mood(user_id=current_user["id"], data=payload)


@router.get("/mood", response_model=List[MoodLogResponse])
async def get_mood_logs(
    limit: int = Query(default=30, ge=1, le=100),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Retrieve recent mood logs."""
    return await tracker_service.get_mood_logs(user_id=current_user["id"], limit=limit)


# 8. MEDITATION TRACKER
@router.post("/meditation", response_model=MeditationLogResponse, status_code=status.HTTP_201_CREATED)
async def log_meditation(
    payload: MeditationLogCreate,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Log mindfulness / meditation session and calmness rating."""
    return await tracker_service.log_meditation(user_id=current_user["id"], data=payload)


@router.get("/meditation", response_model=List[MeditationLogResponse])
async def get_meditation_logs(
    limit: int = Query(default=30, ge=1, le=100),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Retrieve recent meditation logs."""
    return await tracker_service.get_meditation_logs(user_id=current_user["id"], limit=limit)


# 9. STEP TRACKER
@router.post("/steps", response_model=StepLogResponse, status_code=status.HTTP_201_CREATED)
async def log_steps(
    payload: StepLogCreate,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Log daily step count and estimated distance."""
    return await tracker_service.log_steps(user_id=current_user["id"], data=payload)


@router.get("/steps", response_model=List[StepLogResponse])
async def get_step_logs(
    limit: int = Query(default=30, ge=1, le=60),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Retrieve recent step logs."""
    return await tracker_service.get_step_logs(user_id=current_user["id"], limit=limit)


# 10. USER GOALS
@router.post("/goals", response_model=UserGoalResponse, status_code=status.HTTP_201_CREATED)
async def set_goal(
    payload: UserGoalCreate,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Set or update daily habit goals (water, sleep, steps, etc.)."""
    return await tracker_service.set_goal(user_id=current_user["id"], data=payload)


@router.get("/goals", response_model=List[UserGoalResponse])
async def get_goals(
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Retrieve user's active habit goals."""
    return await tracker_service.get_goals(user_id=current_user["id"])
