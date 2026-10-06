import uuid
from datetime import datetime, date, timezone
from typing import List, Optional, Dict, Any
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import (
    Profile,
    UserGoal,
    WaterLog,
    SleepLog,
    ExerciseLog,
    FoodLog,
    ProductivityLog,
    ScreenTimeLog,
    MoodLog,
    MeditationLog,
    StepLog,
)
from app.schemas.trackers import (
    WaterLogCreate,
    SleepLogCreate,
    ExerciseLogCreate,
    FoodLogCreate,
    ProductivityLogCreate,
    ScreenTimeLogCreate,
    MoodLogCreate,
    MeditationLogCreate,
    StepLogCreate,
    UserGoalCreate,
)


class TrackerService:
    """
    Service coordinating CRUD operations for all 9 health tracking modules.
    Provides persistence via SQLAlchemy AsyncSession with an in-memory fallback
    for offline / initial development environments.
    """

    def __init__(self):
        # In-memory stores for dev/offline testing
        self._dev_store: Dict[str, Dict[str, List[Any]]] = {}

    def _get_user_dev_store(self, user_id: str) -> Dict[str, List[Any]]:
        if user_id not in self._dev_store:
            self._dev_store[user_id] = {
                "water": [],
                "sleep": [],
                "exercise": [],
                "food": [],
                "productivity": [],
                "screen_time": [],
                "mood": [],
                "meditation": [],
                "steps": [],
                "goals": [],
            }
        return self._dev_store[user_id]

    # -------------------------------------------------------------
    # 1. WATER TRACKER
    # -------------------------------------------------------------
    async def log_water(
        self, user_id: str, data: WaterLogCreate, db: Optional[AsyncSession] = None
    ) -> WaterLog:
        now = datetime.now(timezone.utc)
        logged_at = data.logged_at or now

        log = WaterLog(
            id=uuid.uuid4(),
            user_id=uuid.UUID(user_id) if isinstance(user_id, str) else user_id,
            amount_ml=data.amount_ml,
            logged_at=logged_at,
            created_at=now,
        )

        if db:
            try:
                db.add(log)
                await db.commit()
                await db.refresh(log)
                return log
            except Exception:
                await db.rollback()

        # Dev fallback
        self._get_user_dev_store(str(user_id))["water"].insert(0, log)
        return log

    async def get_water_logs(
        self, user_id: str, limit: int = 50, db: Optional[AsyncSession] = None
    ) -> List[WaterLog]:
        if db:
            try:
                stmt = (
                    select(WaterLog)
                    .where(WaterLog.user_id == uuid.UUID(user_id))
                    .order_by(desc(WaterLog.logged_at))
                    .limit(limit)
                )
                res = await db.execute(stmt)
                return list(res.scalars().all())
            except Exception:
                pass

        return self._get_user_dev_store(str(user_id))["water"][:limit]

    # -------------------------------------------------------------
    # 2. SLEEP TRACKER
    # -------------------------------------------------------------
    async def log_sleep(
        self, user_id: str, data: SleepLogCreate, db: Optional[AsyncSession] = None
    ) -> SleepLog:
        now = datetime.now(timezone.utc)
        logged_date = data.logged_date or now.date()
        duration_minutes = max(0, int((data.end_time - data.start_time).total_seconds() / 60))

        log = SleepLog(
            id=uuid.uuid4(),
            user_id=uuid.UUID(user_id) if isinstance(user_id, str) else user_id,
            start_time=data.start_time,
            end_time=data.end_time,
            duration_minutes=duration_minutes,
            quality_rating=data.quality_rating,
            disruptions_count=data.disruptions_count,
            notes=data.notes,
            logged_date=logged_date,
            created_at=now,
        )

        if db:
            try:
                db.add(log)
                await db.commit()
                await db.refresh(log)
                return log
            except Exception:
                await db.rollback()

        self._get_user_dev_store(str(user_id))["sleep"].insert(0, log)
        return log

    async def get_sleep_logs(
        self, user_id: str, limit: int = 30, db: Optional[AsyncSession] = None
    ) -> List[SleepLog]:
        if db:
            try:
                stmt = (
                    select(SleepLog)
                    .where(SleepLog.user_id == uuid.UUID(user_id))
                    .order_by(desc(SleepLog.logged_date))
                    .limit(limit)
                )
                res = await db.execute(stmt)
                return list(res.scalars().all())
            except Exception:
                pass

        return self._get_user_dev_store(str(user_id))["sleep"][:limit]

    # -------------------------------------------------------------
    # 3. EXERCISE TRACKER
    # -------------------------------------------------------------
    async def log_exercise(
        self, user_id: str, data: ExerciseLogCreate, db: Optional[AsyncSession] = None
    ) -> ExerciseLog:
        now = datetime.now(timezone.utc)
        logged_at = data.logged_at or now

        log = ExerciseLog(
            id=uuid.uuid4(),
            user_id=uuid.UUID(user_id) if isinstance(user_id, str) else user_id,
            exercise_type=data.exercise_type,
            duration_minutes=data.duration_minutes,
            intensity_level=data.intensity_level,
            calories_burned=data.calories_burned,
            notes=data.notes,
            logged_at=logged_at,
            created_at=now,
        )

        if db:
            try:
                db.add(log)
                await db.commit()
                await db.refresh(log)
                return log
            except Exception:
                await db.rollback()

        self._get_user_dev_store(str(user_id))["exercise"].insert(0, log)
        return log

    async def get_exercise_logs(
        self, user_id: str, limit: int = 50, db: Optional[AsyncSession] = None
    ) -> List[ExerciseLog]:
        if db:
            try:
                stmt = (
                    select(ExerciseLog)
                    .where(ExerciseLog.user_id == uuid.UUID(user_id))
                    .order_by(desc(ExerciseLog.logged_at))
                    .limit(limit)
                )
                res = await db.execute(stmt)
                return list(res.scalars().all())
            except Exception:
                pass

        return self._get_user_dev_store(str(user_id))["exercise"][:limit]

    # -------------------------------------------------------------
    # 4. FOOD HABITS TRACKER
    # -------------------------------------------------------------
    async def log_food(
        self, user_id: str, data: FoodLogCreate, db: Optional[AsyncSession] = None
    ) -> FoodLog:
        now = datetime.now(timezone.utc)
        logged_at = data.logged_at or now

        log = FoodLog(
            id=uuid.uuid4(),
            user_id=uuid.UUID(user_id) if isinstance(user_id, str) else user_id,
            meal_type=data.meal_type,
            quality_rating=data.quality_rating,
            hunger_before=data.hunger_before,
            mindful_eating=data.mindful_eating,
            notes=data.notes,
            logged_at=logged_at,
            created_at=now,
        )

        if db:
            try:
                db.add(log)
                await db.commit()
                await db.refresh(log)
                return log
            except Exception:
                await db.rollback()

        self._get_user_dev_store(str(user_id))["food"].insert(0, log)
        return log

    async def get_food_logs(
        self, user_id: str, limit: int = 50, db: Optional[AsyncSession] = None
    ) -> List[FoodLog]:
        if db:
            try:
                stmt = (
                    select(FoodLog)
                    .where(FoodLog.user_id == uuid.UUID(user_id))
                    .order_by(desc(FoodLog.logged_at))
                    .limit(limit)
                )
                res = await db.execute(stmt)
                return list(res.scalars().all())
            except Exception:
                pass

        return self._get_user_dev_store(str(user_id))["food"][:limit]

    # -------------------------------------------------------------
    # 5. PRODUCTIVITY TRACKER
    # -------------------------------------------------------------
    async def log_productivity(
        self, user_id: str, data: ProductivityLogCreate, db: Optional[AsyncSession] = None
    ) -> ProductivityLog:
        now = datetime.now(timezone.utc)
        logged_date = data.logged_date or now.date()

        log = ProductivityLog(
            id=uuid.uuid4(),
            user_id=uuid.UUID(user_id) if isinstance(user_id, str) else user_id,
            category=data.category,
            duration_minutes=data.duration_minutes,
            focus_rating=data.focus_rating,
            notes=data.notes,
            logged_date=logged_date,
            created_at=now,
        )

        if db:
            try:
                db.add(log)
                await db.commit()
                await db.refresh(log)
                return log
            except Exception:
                await db.rollback()

        self._get_user_dev_store(str(user_id))["productivity"].insert(0, log)
        return log

    async def get_productivity_logs(
        self, user_id: str, limit: int = 50, db: Optional[AsyncSession] = None
    ) -> List[ProductivityLog]:
        if db:
            try:
                stmt = (
                    select(ProductivityLog)
                    .where(ProductivityLog.user_id == uuid.UUID(user_id))
                    .order_by(desc(ProductivityLog.logged_date))
                    .limit(limit)
                )
                res = await db.execute(stmt)
                return list(res.scalars().all())
            except Exception:
                pass

        return self._get_user_dev_store(str(user_id))["productivity"][:limit]

    # -------------------------------------------------------------
    # 6. SCREEN TIME TRACKER
    # -------------------------------------------------------------
    async def log_screen_time(
        self, user_id: str, data: ScreenTimeLogCreate, db: Optional[AsyncSession] = None
    ) -> ScreenTimeLog:
        now = datetime.now(timezone.utc)
        logged_date = data.logged_date or now.date()

        log = ScreenTimeLog(
            id=uuid.uuid4(),
            user_id=uuid.UUID(user_id) if isinstance(user_id, str) else user_id,
            total_minutes=data.total_minutes,
            work_minutes=data.work_minutes,
            leisure_minutes=data.leisure_minutes,
            night_minutes=data.night_minutes,
            notes=data.notes,
            logged_date=logged_date,
            created_at=now,
        )

        if db:
            try:
                db.add(log)
                await db.commit()
                await db.refresh(log)
                return log
            except Exception:
                await db.rollback()

        # Update existing record for the date if present in dev store
        store = self._get_user_dev_store(str(user_id))["screen_time"]
        existing = next((s for s in store if s.logged_date == logged_date), None)
        if existing:
            existing.total_minutes = data.total_minutes
            existing.work_minutes = data.work_minutes
            existing.leisure_minutes = data.leisure_minutes
            existing.night_minutes = data.night_minutes
            return existing

        store.insert(0, log)
        return log

    async def get_screen_time_logs(
        self, user_id: str, limit: int = 30, db: Optional[AsyncSession] = None
    ) -> List[ScreenTimeLog]:
        if db:
            try:
                stmt = (
                    select(ScreenTimeLog)
                    .where(ScreenTimeLog.user_id == uuid.UUID(user_id))
                    .order_by(desc(ScreenTimeLog.logged_date))
                    .limit(limit)
                )
                res = await db.execute(stmt)
                return list(res.scalars().all())
            except Exception:
                pass

        return self._get_user_dev_store(str(user_id))["screen_time"][:limit]

    # -------------------------------------------------------------
    # 7. MOOD TRACKER
    # -------------------------------------------------------------
    async def log_mood(
        self, user_id: str, data: MoodLogCreate, db: Optional[AsyncSession] = None
    ) -> MoodLog:
        now = datetime.now(timezone.utc)
        logged_at = data.logged_at or now

        log = MoodLog(
            id=uuid.uuid4(),
            user_id=uuid.UUID(user_id) if isinstance(user_id, str) else user_id,
            score=data.score,
            energy_level=data.energy_level,
            tags=data.tags,
            notes=data.notes,
            logged_at=logged_at,
            created_at=now,
        )

        if db:
            try:
                db.add(log)
                await db.commit()
                await db.refresh(log)
                return log
            except Exception:
                await db.rollback()

        self._get_user_dev_store(str(user_id))["mood"].insert(0, log)
        return log

    async def get_mood_logs(
        self, user_id: str, limit: int = 50, db: Optional[AsyncSession] = None
    ) -> List[MoodLog]:
        if db:
            try:
                stmt = (
                    select(MoodLog)
                    .where(MoodLog.user_id == uuid.UUID(user_id))
                    .order_by(desc(MoodLog.logged_at))
                    .limit(limit)
                )
                res = await db.execute(stmt)
                return list(res.scalars().all())
            except Exception:
                pass

        return self._get_user_dev_store(str(user_id))["mood"][:limit]

    # -------------------------------------------------------------
    # 8. MEDITATION TRACKER
    # -------------------------------------------------------------
    async def log_meditation(
        self, user_id: str, data: MeditationLogCreate, db: Optional[AsyncSession] = None
    ) -> MeditationLog:
        now = datetime.now(timezone.utc)
        logged_at = data.logged_at or now

        log = MeditationLog(
            id=uuid.uuid4(),
            user_id=uuid.UUID(user_id) if isinstance(user_id, str) else user_id,
            duration_minutes=data.duration_minutes,
            technique=data.technique,
            calmness_rating=data.calmness_rating,
            notes=data.notes,
            logged_at=logged_at,
            created_at=now,
        )

        if db:
            try:
                db.add(log)
                await db.commit()
                await db.refresh(log)
                return log
            except Exception:
                await db.rollback()

        self._get_user_dev_store(str(user_id))["meditation"].insert(0, log)
        return log

    async def get_meditation_logs(
        self, user_id: str, limit: int = 50, db: Optional[AsyncSession] = None
    ) -> List[MeditationLog]:
        if db:
            try:
                stmt = (
                    select(MeditationLog)
                    .where(MeditationLog.user_id == uuid.UUID(user_id))
                    .order_by(desc(MeditationLog.logged_at))
                    .limit(limit)
                )
                res = await db.execute(stmt)
                return list(res.scalars().all())
            except Exception:
                pass

        return self._get_user_dev_store(str(user_id))["meditation"][:limit]

    # -------------------------------------------------------------
    # 9. STEP TRACKER
    # -------------------------------------------------------------
    async def log_steps(
        self, user_id: str, data: StepLogCreate, db: Optional[AsyncSession] = None
    ) -> StepLog:
        now = datetime.now(timezone.utc)
        logged_date = data.logged_date or now.date()

        log = StepLog(
            id=uuid.uuid4(),
            user_id=uuid.UUID(user_id) if isinstance(user_id, str) else user_id,
            step_count=data.step_count,
            distance_meters=data.distance_meters,
            active_duration_minutes=data.active_duration_minutes,
            logged_date=logged_date,
            created_at=now,
        )

        if db:
            try:
                db.add(log)
                await db.commit()
                await db.refresh(log)
                return log
            except Exception:
                await db.rollback()

        store = self._get_user_dev_store(str(user_id))["steps"]
        existing = next((s for s in store if s.logged_date == logged_date), None)
        if existing:
            existing.step_count = data.step_count
            existing.distance_meters = data.distance_meters
            existing.active_duration_minutes = data.active_duration_minutes
            return existing

        store.insert(0, log)
        return log

    async def get_step_logs(
        self, user_id: str, limit: int = 30, db: Optional[AsyncSession] = None
    ) -> List[StepLog]:
        if db:
            try:
                stmt = (
                    select(StepLog)
                    .where(StepLog.user_id == uuid.UUID(user_id))
                    .order_by(desc(StepLog.logged_date))
                    .limit(limit)
                )
                res = await db.execute(stmt)
                return list(res.scalars().all())
            except Exception:
                pass

        return self._get_user_dev_store(str(user_id))["steps"][:limit]

    # -------------------------------------------------------------
    # 10. USER GOALS
    # -------------------------------------------------------------
    async def set_goal(
        self, user_id: str, data: UserGoalCreate, db: Optional[AsyncSession] = None
    ) -> UserGoal:
        now = datetime.now(timezone.utc)
        goal = UserGoal(
            id=uuid.uuid4(),
            user_id=uuid.UUID(user_id) if isinstance(user_id, str) else user_id,
            metric_type=data.metric_type,
            target_value=data.target_value,
            unit=data.unit,
            frequency=data.frequency,
            is_active=True,
            created_at=now,
        )

        if db:
            try:
                db.add(goal)
                await db.commit()
                await db.refresh(goal)
                return goal
            except Exception:
                await db.rollback()

        store = self._get_user_dev_store(str(user_id))["goals"]
        existing = next((g for g in store if g.metric_type == data.metric_type), None)
        if existing:
            existing.target_value = data.target_value
            existing.unit = data.unit
            existing.frequency = data.frequency
            return existing

        store.append(goal)
        return goal

    async def get_goals(
        self, user_id: str, db: Optional[AsyncSession] = None
    ) -> List[UserGoal]:
        if db:
            try:
                stmt = (
                    select(UserGoal)
                    .where(UserGoal.user_id == uuid.UUID(user_id), UserGoal.is_active == True)
                )
                res = await db.execute(stmt)
                return list(res.scalars().all())
            except Exception:
                pass

        return self._get_user_dev_store(str(user_id))["goals"]


tracker_service = TrackerService()
