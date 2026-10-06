import json
import asyncio
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.schemas.recommendation import AIRecommendationItem, AIRecommendationResponse
from app.services.correlation_engine import correlation_engine

# Official Google GenAI SDK
try:
    from google import genai
    from google.genai import types
    GENAI_SDK_AVAILABLE = True
except ImportError:
    GENAI_SDK_AVAILABLE = False


# ─────────────────────────────────────────────────────────────────────────────
# Heuristic Rule Engine (offline fallback when no Gemini API key is present)
# ─────────────────────────────────────────────────────────────────────────────

def _build_heuristic_recommendations(
    metrics_summary: Dict[str, Any],
) -> List[AIRecommendationItem]:
    """
    Pure Python heuristic engine.
    Generates 2-4 prioritised habit recommendations from the metrics summary
    without calling any external AI service.
    """
    averages = metrics_summary.get("averages", {})
    correlations = metrics_summary.get("correlations", [])

    recs: List[AIRecommendationItem] = []

    # 1. Sleep & screen time ------------------------------------------------
    night_screen = averages.get("avg_screen_night_minutes", 35)
    sleep_hours = averages.get("avg_sleep_hours", 7.0)
    sleep_quality = averages.get("avg_sleep_quality", 3.5)
    target_sleep = averages.get("target_sleep_hours", 8.0)

    has_screen_sleep_corr = any(
        c.get("factor_a") in ("late_night_screen_time",) for c in correlations
    )

    if night_screen > 40 or has_screen_sleep_corr:
        recs.append(
            AIRecommendationItem(
                category="sleep",
                priority="high",
                title="Establish a 30-Minute Screen Wind-Down",
                insight_text=(
                    f"Your late-night screen time averages {night_screen} minutes, "
                    "which delays melatonin onset and fragments deep sleep cycles. "
                    f"Average sleep quality is currently {sleep_quality}/5."
                ),
                actionable_step=(
                    "Enable your device's night mode at 9:30 PM and place your phone "
                    "on charge in another room 30 minutes before your target bedtime."
                ),
                contributing_factors=["screen_time", "sleep_quality", "sleep_duration"],
            )
        )
    elif sleep_hours < target_sleep - 0.5:
        deficit = round(target_sleep - sleep_hours, 1)
        recs.append(
            AIRecommendationItem(
                category="sleep",
                priority="high",
                title="Close Your Sleep Deficit",
                insight_text=(
                    f"You are averaging {sleep_hours}h of sleep — "
                    f"{deficit}h below your {target_sleep}h goal. "
                    "Sleep debt accumulates day-over-day and impairs cognitive performance."
                ),
                actionable_step=(
                    f"Move your bedtime {int(deficit * 60)} minutes earlier tonight "
                    "and protect that schedule for the next 5 days."
                ),
                contributing_factors=["sleep_duration", "sleep_consistency"],
            )
        )

    # 2. Hydration ----------------------------------------------------------
    water_ml = averages.get("avg_water_ml", 2000)
    target_water = averages.get("target_water_ml", 2500)

    if water_ml < target_water * 0.8:
        deficit_ml = target_water - water_ml
        recs.append(
            AIRecommendationItem(
                category="hydration",
                priority="medium",
                title="Pre-load Morning Hydration",
                insight_text=(
                    f"You're averaging {water_ml} ml/day — {deficit_ml} ml short of your "
                    f"{target_water} ml goal. Mild dehydration reduces cognitive focus "
                    "and increases perceived fatigue."
                ),
                actionable_step=(
                    "Drink 500 ml of water within 15 minutes of waking up, "
                    "and place a full 1-litre bottle on your desk as a visible reminder."
                ),
                contributing_factors=["water_intake", "energy_level"],
            )
        )

    # 3. Movement & mood ---------------------------------------------------
    avg_steps = averages.get("avg_steps", 7000)
    target_steps = averages.get("target_steps", 10000)
    avg_mood = averages.get("avg_mood_score", 7.0)
    exercise_sessions = averages.get("exercise_sessions", 3)

    has_step_mood_corr = any(
        c.get("factor_b") in ("mood_valence", "emotional_vitality") for c in correlations
    )

    if avg_steps < target_steps * 0.75 or has_step_mood_corr:
        shortfall = target_steps - avg_steps
        step_priority = "medium" if avg_mood >= 7 else "high"
        recs.append(
            AIRecommendationItem(
                category="exercise",
                priority=step_priority,
                title="Close the Daily Step Gap with Micro-Walks",
                insight_text=(
                    f"Daily step average is {avg_steps:,} — {shortfall:,} steps short of your "
                    f"{target_steps:,} goal. "
                    + (
                        "Movement strongly correlates with elevated daily mood in your data. "
                        if has_step_mood_corr
                        else f"Consistent daily movement supports sustained mood ({avg_mood}/10) and energy. "
                    )
                ),
                actionable_step=(
                    "Add two 10-minute brisk walks — one after lunch and one after dinner — "
                    "to reliably add ~2,500 steps per day."
                ),
                contributing_factors=["step_count", "mood_valence", "energy_level"],
            )
        )

    # 4. Mindfulness reinforcement or meditation nudge ----------------------
    meditation_minutes = averages.get("total_meditation_minutes", 0)
    window_days = metrics_summary.get("window_days", 7)

    if meditation_minutes >= 30:
        recs.append(
            AIRecommendationItem(
                category="holistic",
                priority="low",
                title="Sustain Your Mindfulness Momentum",
                insight_text=(
                    f"You've logged {meditation_minutes} minutes of mindfulness practice "
                    f"over the past {window_days} days — this is building measurable "
                    "calm and focus capacity."
                ),
                actionable_step=(
                    "Lock in a consistent 10-minute morning mindfulness slot at the same "
                    "time each day to turn this into a reliable anchor habit."
                ),
                contributing_factors=["meditation", "focus_rating", "mood_valence"],
            )
        )
    elif meditation_minutes < 10:
        recs.append(
            AIRecommendationItem(
                category="holistic",
                priority="low",
                title="Start a 5-Minute Breath Reset",
                insight_text=(
                    "Mindfulness practice is minimal this week. Even brief breathing "
                    "exercises (2-5 minutes) are clinically shown to lower cortisol "
                    "and sharpen cognitive focus within days."
                ),
                actionable_step=(
                    "Try box breathing (4s in, 4s hold, 4s out, 4s hold × 5 cycles) "
                    "right after your morning alarm for the next 7 days."
                ),
                contributing_factors=["meditation", "stress_reduction"],
            )
        )

    # Guarantee at least 2 recommendations
    if len(recs) < 2:
        recs.append(
            AIRecommendationItem(
                category="holistic",
                priority="low",
                title="Maintain Your Solid Lifestyle Foundation",
                insight_text=(
                    "Your tracked wellness dimensions are performing well across the board. "
                    "Consistency is the bridge between good habits and lasting health."
                ),
                actionable_step=(
                    "Continue logging daily to keep your wellness score visible "
                    "and let VitaSync surface new patterns as they emerge."
                ),
                contributing_factors=["lifestyle_score", "habit_consistency"],
            )
        )

    return recs[:4]  # cap at 4


# ─────────────────────────────────────────────────────────────────────────────
# AI Recommendation Service — Google Gemini + heuristic fallback
# ─────────────────────────────────────────────────────────────────────────────

SYSTEM_INSTRUCTION = (
    "You are VitaSync's AI Lifestyle and Habit Coach — a compassionate, evidence-based "
    "wellness advisor. Your role is to analyse the user's lifestyle metrics across "
    "9 wellness dimensions (water, sleep, exercise, food habits, study/productivity, "
    "screen time, mood, mindfulness, and daily steps) and identify meaningful correlations.\n\n"
    "RULES:\n"
    "1. Return EXACTLY 3 recommendations: one 'high' priority, one 'medium' priority, "
    "and one 'low' priority.\n"
    "2. Each recommendation MUST directly cite a specific metric value from the data "
    "(e.g. 'your average of 1,800 ml is 700 ml below your 2,500 ml goal').\n"
    "3. Every actionable_step must be a concrete, implementable micro-action "
    "that the user can start today.\n"
    "4. Do NOT diagnose diseases, prescribe medications, or use medical terminology.\n"
    "5. Respond ONLY with valid JSON — no markdown, no preamble, no explanation.\n"
    "6. Use an empathetic, motivating tone."
)

RESPONSE_SCHEMA_HINT = """
Return a JSON object with a top-level "recommendations" array. Each element must have:
{
  "category": "sleep" | "hydration" | "exercise" | "focus" | "screentime" | "holistic",
  "priority": "high" | "medium" | "low",
  "title": "<concise motivating title, max 10 words>",
  "insight_text": "<data-grounded observation, 1-3 sentences>",
  "actionable_step": "<concrete micro-habit action, 1-2 sentences>",
  "contributing_factors": ["<metric1>", "<metric2>"]
}
"""


class AIRecommendationService:
    """
    Lifestyle recommendation service powered by Google Gemini.

    Pipeline:
      1. CorrelationEngine aggregates 7-day metrics and detects cross-pillar patterns.
      2. An anonymised prompt (no PII) is sent to Gemini with strict JSON schema.
      3. The response is parsed and validated via Pydantic.
      4. If Gemini is unavailable, the heuristic rule engine generates equivalent output.
    """

    def __init__(self):
        self.model_name = settings.GEMINI_MODEL
        self._client = None

        _api_key = settings.GEMINI_API_KEY or ""
        _key_configured = (
            bool(_api_key)
            and not _api_key.startswith("your-")
            and not _api_key.startswith("AIzaSy-PLACE")
        )

        if _key_configured and GENAI_SDK_AVAILABLE:
            try:
                self._client = genai.Client(api_key=_api_key)
            except Exception:
                self._client = None

    def is_configured(self) -> bool:
        """Returns True when Gemini client is initialised with a valid API key."""
        return bool(self._client)

    async def generate_lifestyle_recommendations(
        self,
        user_id: str,
        user_metrics_summary: Optional[Dict[str, Any]] = None,
        days_window: int = 7,
        db: Optional[AsyncSession] = None,
    ) -> AIRecommendationResponse:
        """
        Full pipeline: aggregate metrics → correlate → call Gemini (or heuristics).
        `user_metrics_summary` can be supplied directly (e.g. in tests);
        otherwise the correlation engine fetches and builds it from user logs.
        """
        now_iso = datetime.now(timezone.utc).isoformat()

        # Step 1: Build or accept the metrics summary
        if user_metrics_summary is None:
            metrics_summary = await correlation_engine.build_user_metrics_summary(
                user_id=user_id,
                days_window=days_window,
                db=db,
            )
        else:
            # Backfill correlation data if caller passed a raw dict
            metrics_summary = user_metrics_summary
            if "correlations" not in metrics_summary:
                metrics_summary["correlations"] = []

        data_points = metrics_summary.get("data_points_analyzed", 0)

        # Step 2: Try Gemini; fall back to heuristics on any failure
        if self.is_configured():
            recs, provider = await self._call_gemini(
                user_id=user_id,
                metrics_summary=metrics_summary,
                now_iso=now_iso,
            )
        else:
            recs = _build_heuristic_recommendations(metrics_summary)
            provider = "VitaSync Heuristic Engine (configure GEMINI_API_KEY for AI insights)"

        return AIRecommendationResponse(
            user_id=user_id,
            generated_at=now_iso,
            provider=provider,
            data_points_analyzed=data_points,
            recommendations=recs,
            correlations_detected=metrics_summary.get("correlations", []),
            metrics_snapshot=metrics_summary.get("averages"),
        )

    async def _call_gemini(
        self,
        user_id: str,
        metrics_summary: Dict[str, Any],
        now_iso: str,
    ):
        """Calls Gemini asynchronously and parses the structured JSON response."""
        # Strip PII — only pass anonymised metric numbers
        safe_payload = {
            "analysis_window_days": metrics_summary.get("window_days", 7),
            "date_range": metrics_summary.get("date_range", {}),
            "lifestyle_averages": metrics_summary.get("averages", {}),
            "detected_correlations": metrics_summary.get("correlations", []),
        }

        user_prompt = (
            "Here are the anonymised lifestyle metrics for a VitaSync user "
            f"over the past {safe_payload['analysis_window_days']} days:\n\n"
            f"{json.dumps(safe_payload, indent=2)}\n\n"
            f"{RESPONSE_SCHEMA_HINT}"
        )

        try:
            # Run synchronous SDK call in thread pool to keep FastAPI async
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self._client.models.generate_content(
                    model=self.model_name,
                    contents=user_prompt,
                    config=types.GenerateContentConfig(
                        system_instruction=SYSTEM_INSTRUCTION,
                        response_mime_type="application/json",
                        temperature=0.35,
                        max_output_tokens=1200,
                    ),
                ),
            )

            raw = json.loads(response.text)

            # Normalise — Gemini may return a top-level dict or bare array
            if isinstance(raw, dict) and "recommendations" in raw:
                items_data = raw["recommendations"]
            elif isinstance(raw, list):
                items_data = raw
            else:
                items_data = [raw]

            recs = [AIRecommendationItem(**item) for item in items_data]
            provider = f"Google Gemini ({self.model_name})"
            return recs, provider

        except json.JSONDecodeError:
            # Gemini returned non-JSON — fall back gracefully
            recs = _build_heuristic_recommendations(metrics_summary)
            provider = f"VitaSync Heuristic Engine (Gemini returned malformed JSON)"
            return recs, provider

        except Exception as exc:
            recs = _build_heuristic_recommendations(metrics_summary)
            provider = f"VitaSync Heuristic Engine (Gemini error: {type(exc).__name__})"
            return recs, provider


# Singleton instance
ai_recommender_service = AIRecommendationService()
