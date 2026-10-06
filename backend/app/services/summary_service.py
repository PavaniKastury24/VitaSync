from datetime import date
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.summary import (
    DailySummaryResponse,
    DailySummaryMetrics,
    WellnessScoreBreakdown,
)
from app.services.tracker_service import tracker_service


class SummaryService:
    """
    Computes daily wellness summaries and the composite VitaSync Lifestyle Score (0-100).
    """

    async def get_daily_summary(
        self, user_id: str, target_date: date, db: Optional[AsyncSession] = None
    ) -> DailySummaryResponse:
        # Retrieve logs for the user
        water_logs = await tracker_service.get_water_logs(user_id, limit=100, db=db)
        sleep_logs = await tracker_service.get_sleep_logs(user_id, limit=30, db=db)
        exercise_logs = await tracker_service.get_exercise_logs(user_id, limit=50, db=db)
        food_logs = await tracker_service.get_food_logs(user_id, limit=50, db=db)
        productivity_logs = await tracker_service.get_productivity_logs(user_id, limit=50, db=db)
        screen_logs = await tracker_service.get_screen_time_logs(user_id, limit=30, db=db)
        mood_logs = await tracker_service.get_mood_logs(user_id, limit=50, db=db)
        meditation_logs = await tracker_service.get_meditation_logs(user_id, limit=50, db=db)
        step_logs = await tracker_service.get_step_logs(user_id, limit=30, db=db)
        goals = await tracker_service.get_goals(user_id, db=db)

        # 1. Hydration
        water_goal = 2500
        for g in goals:
            if g.metric_type == "water":
                water_goal = int(g.target_value)

        day_water = sum(
            w.amount_ml
            for w in water_logs
            if w.logged_at.date() == target_date
        )
        water_percent = int(min(100, (day_water / water_goal) * 100)) if water_goal > 0 else 0
        hydration_score = min(15.0, (day_water / max(1, water_goal)) * 15.0)

        # 2. Sleep
        day_sleep = next((s for s in sleep_logs if s.logged_date == target_date), None)
        sleep_minutes = day_sleep.duration_minutes if day_sleep else 0
        sleep_hours = round(sleep_minutes / 60.0, 1)
        sleep_quality = day_sleep.quality_rating if day_sleep else None

        sleep_duration_score = 0.0
        if 7.0 <= sleep_hours <= 9.0:
            sleep_duration_score = 12.0
        elif 6.0 <= sleep_hours < 7.0 or 9.0 < sleep_hours <= 10.0:
            sleep_duration_score = 9.0
        elif 5.0 <= sleep_hours < 6.0:
            sleep_duration_score = 6.0
        elif sleep_hours > 0:
            sleep_duration_score = 3.0

        sleep_quality_score = ((sleep_quality or 3) / 5.0) * 8.0 if sleep_minutes > 0 else 0.0
        sleep_score = min(20.0, sleep_duration_score + sleep_quality_score)

        # 3. Movement (Steps & Exercise)
        step_goal = 10000
        for g in goals:
            if g.metric_type == "steps":
                step_goal = int(g.target_value)

        day_step = next((s for s in step_logs if s.logged_date == target_date), None)
        step_count = day_step.step_count if day_step else 0
        step_percent = int(min(100, (step_count / max(1, step_goal)) * 100))

        day_exercises = [
            e for e in exercise_logs if e.logged_at.date() == target_date
        ]
        exercise_minutes = sum(e.duration_minutes for e in day_exercises)
        calories_burned = sum(e.calories_burned or 0 for e in day_exercises)

        step_score = min(9.0, (step_count / max(1, step_goal)) * 9.0)
        exercise_score = min(6.0, (exercise_minutes / 30.0) * 6.0)
        movement_score = min(15.0, step_score + exercise_score)

        # 4. Nutrition
        day_foods = [f for f in food_logs if f.logged_at.date() == target_date]
        meals_logged = len(day_foods)
        if meals_logged > 0:
            ratings = [f.quality_rating for f in day_foods if f.quality_rating]
            avg_food_quality = round(sum(ratings) / len(ratings), 1) if ratings else 3.5
            mindful_count = sum(1 for f in day_foods if f.mindful_eating)
            nutrition_score = min(15.0, (avg_food_quality / 5.0) * 12.0 + (mindful_count / meals_logged) * 3.0)
        else:
            avg_food_quality = None
            nutrition_score = 8.0  # neutral baseline

        # 5. Productivity
        day_prod = [p for p in productivity_logs if p.logged_date == target_date]
        prod_minutes = sum(p.duration_minutes for p in day_prod)

        # 6. Screen Time
        day_screen = next((s for s in screen_logs if s.logged_date == target_date), None)
        screen_total = day_screen.total_minutes if day_screen else 0
        screen_night = day_screen.night_minutes if day_screen else 0

        if screen_total == 0:
            screen_score = 12.0  # baseline
        else:
            base_screen_score = 9.0 if screen_total <= 360 else (6.0 if screen_total <= 480 else 3.0)
            night_penalty = 6.0 if screen_night <= 15 else (4.0 if screen_night <= 30 else (2.0 if screen_night <= 60 else 0.0))
            screen_score = min(15.0, base_screen_score + night_penalty)

        # 7. Mental Wellness (Mood & Meditation)
        day_moods = [m for m in mood_logs if m.logged_at.date() == target_date]
        if day_moods:
            avg_mood = round(sum(m.score for m in day_moods) / len(day_moods), 1)
            all_tags = []
            for m in day_moods:
                if m.tags:
                    all_tags.extend(m.tags)
            mood_tags = list(set(all_tags))
            mood_points = (avg_mood / 10.0) * 12.0
        else:
            avg_mood = None
            mood_tags = []
            mood_points = 7.0  # neutral baseline

        day_meditation = [m for m in meditation_logs if m.logged_at.date() == target_date]
        meditation_minutes = sum(m.duration_minutes for m in day_meditation)
        meditation_points = min(8.0, (meditation_minutes / 15.0) * 8.0)
        mental_score = min(20.0, mood_points + meditation_points)

        # Total Lifestyle Score
        total_score = int(round(
            hydration_score + sleep_score + movement_score + nutrition_score + screen_score + mental_score
        ))
        total_score = max(0, min(100, total_score))

        # Grade
        if total_score >= 85:
            grade = "Optimal"
        elif total_score >= 70:
            grade = "Good"
        elif total_score >= 50:
            grade = "Balanced"
        else:
            grade = "Needs Attention"

        # Highlights
        highlights: List[str] = []
        if water_percent >= 100:
            highlights.append(f"💧 Hydration target reached ({day_water} ml / {water_goal} ml)")
        if 7.0 <= sleep_hours <= 9.0:
            highlights.append(f"😴 Optimal sleep logged: {sleep_hours} hours")
        if step_percent >= 100:
            highlights.append(f"👟 Step goal achieved: {step_count:,} steps")
        if exercise_minutes >= 30:
            highlights.append(f"🏃 Strong physical activity: {exercise_minutes} active minutes")
        if meditation_minutes >= 10:
            highlights.append(f"🧘 Mindfulness session completed: {meditation_minutes} mins")
        if not highlights:
            highlights.append("📈 Keep logging your daily wellness habits to unlock lifestyle insights!")

        breakdown = WellnessScoreBreakdown(
            hydration_score=round(hydration_score, 1),
            sleep_score=round(sleep_score, 1),
            movement_score=round(movement_score, 1),
            nutrition_score=round(nutrition_score, 1),
            screen_hygiene_score=round(screen_score, 1),
            mental_wellness_score=round(mental_score, 1),
            total_lifestyle_score=total_score,
            grade=grade,
        )

        metrics = DailySummaryMetrics(
            summary_date=target_date,
            water_ml=day_water,
            water_goal_ml=water_goal,
            water_percent=water_percent,
            sleep_minutes=sleep_minutes,
            sleep_hours=sleep_hours,
            sleep_quality=sleep_quality,
            exercise_minutes=exercise_minutes,
            exercise_sessions=len(day_exercises),
            calories_burned=calories_burned,
            meals_logged=meals_logged,
            avg_food_quality=avg_food_quality,
            productivity_minutes=prod_minutes,
            screen_total_minutes=screen_total,
            screen_night_minutes=screen_night,
            mood_score=avg_mood,
            mood_tags=mood_tags,
            meditation_minutes=meditation_minutes,
            steps=step_count,
            step_goal=step_goal,
            step_percent=step_percent,
        )

        return DailySummaryResponse(
            user_id=str(user_id),
            summary_date=target_date,
            lifestyle_score=total_score,
            score_breakdown=breakdown,
            metrics=metrics,
            highlights=highlights,
        )


summary_service = SummaryService()
