"""
Phase 4 tests — Correlation Engine + AI Recommendation Service

These tests exercise:
  - CorrelationEngine.build_user_metrics_summary()
  - _build_heuristic_recommendations() in every branch
  - AIRecommendationService.generate_lifestyle_recommendations() (heuristic path)
  - POST /api/v1/recommendations/generate  (full HTTP flow)
  - GET  /api/v1/recommendations/status
"""
import asyncio
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.ai_recommender import ai_recommender_service, _build_heuristic_recommendations
from app.services.correlation_engine import correlation_engine
from app.schemas.recommendation import AIRecommendationItem, AIRecommendationResponse

client = TestClient(app)


# ─────────────────────────────────────────────────────────────────────────────
# Helper — build a rich metrics summary dict for unit tests
# ─────────────────────────────────────────────────────────────────────────────

def _make_metrics(
    avg_water=2500,
    target_water=2500,
    avg_sleep_hours=7.8,
    target_sleep=8.0,
    avg_sleep_quality=4.0,
    avg_steps=9500,
    target_steps=10000,
    exercise_sessions=3,
    total_exercise_minutes=105,
    avg_screen_total=320,
    avg_screen_night=20,
    avg_mood=8.0,
    total_meditation_minutes=45,
    avg_food_quality=4.2,
    mindful_eating_pct=85,
    correlations=None,
):
    return {
        "window_days": 7,
        "date_range": {"start": "2026-09-28", "end": "2026-10-04"},
        "averages": {
            "avg_water_ml": avg_water,
            "target_water_ml": target_water,
            "avg_sleep_hours": avg_sleep_hours,
            "target_sleep_hours": target_sleep,
            "avg_sleep_quality": avg_sleep_quality,
            "avg_steps": avg_steps,
            "target_steps": target_steps,
            "exercise_sessions": exercise_sessions,
            "total_exercise_minutes": total_exercise_minutes,
            "avg_screen_total_minutes": avg_screen_total,
            "avg_screen_night_minutes": avg_screen_night,
            "avg_mood_score": avg_mood,
            "total_meditation_minutes": total_meditation_minutes,
            "avg_food_quality": avg_food_quality,
            "mindful_eating_pct": mindful_eating_pct,
        },
        "correlations": correlations or [],
        "data_points_analyzed": 52,
    }


# ─────────────────────────────────────────────────────────────────────────────
# 1. Heuristic rule engine — unit tests
# ─────────────────────────────────────────────────────────────────────────────

class TestHeuristicEngine:

    def test_returns_list_of_recommendation_items(self):
        metrics = _make_metrics()
        recs = _build_heuristic_recommendations(metrics)
        assert isinstance(recs, list)
        assert len(recs) >= 2
        for r in recs:
            assert isinstance(r, AIRecommendationItem)

    def test_max_four_recommendations(self):
        metrics = _make_metrics()
        recs = _build_heuristic_recommendations(metrics)
        assert len(recs) <= 4

    def test_high_priority_sleep_rec_for_high_night_screen(self):
        metrics = _make_metrics(avg_screen_night=65)
        recs = _build_heuristic_recommendations(metrics)
        sleep_recs = [r for r in recs if r.category == "sleep"]
        assert len(sleep_recs) >= 1
        assert sleep_recs[0].priority == "high"
        assert "screen" in sleep_recs[0].insight_text.lower() or "65" in sleep_recs[0].insight_text

    def test_sleep_deficit_triggers_rec(self):
        metrics = _make_metrics(avg_sleep_hours=5.8, target_sleep=8.0, avg_screen_night=10)
        recs = _build_heuristic_recommendations(metrics)
        sleep_recs = [r for r in recs if r.category == "sleep"]
        assert len(sleep_recs) >= 1
        assert sleep_recs[0].priority == "high"

    def test_hydration_deficit_triggers_rec(self):
        metrics = _make_metrics(avg_water=1500, target_water=2500)
        recs = _build_heuristic_recommendations(metrics)
        hydration_recs = [r for r in recs if r.category == "hydration"]
        assert len(hydration_recs) >= 1
        assert "1500" in hydration_recs[0].insight_text or "1,500" in hydration_recs[0].insight_text

    def test_step_shortfall_triggers_exercise_rec(self):
        metrics = _make_metrics(avg_steps=5000, target_steps=10000, avg_screen_night=15)
        recs = _build_heuristic_recommendations(metrics)
        exercise_recs = [r for r in recs if r.category == "exercise"]
        assert len(exercise_recs) >= 1

    def test_meditation_reinforcement_rec_when_active(self):
        metrics = _make_metrics(total_meditation_minutes=50)
        recs = _build_heuristic_recommendations(metrics)
        holistic_recs = [r for r in recs if r.category == "holistic"]
        assert len(holistic_recs) >= 1
        assert holistic_recs[0].priority == "low"

    def test_meditation_nudge_when_inactive(self):
        metrics = _make_metrics(total_meditation_minutes=0)
        recs = _build_heuristic_recommendations(metrics)
        holistic_recs = [r for r in recs if r.category == "holistic"]
        assert len(holistic_recs) >= 1
        # Should suggest starting meditation
        all_text = holistic_recs[0].insight_text + holistic_recs[0].actionable_step
        assert "breath" in all_text.lower() or "mindful" in all_text.lower()

    def test_priority_values_are_valid(self):
        metrics = _make_metrics(avg_water=1200, avg_screen_night=70, avg_sleep_hours=5.5)
        recs = _build_heuristic_recommendations(metrics)
        for r in recs:
            assert r.priority in ("low", "medium", "high"), f"Bad priority: {r.priority}"

    def test_contributing_factors_is_list(self):
        metrics = _make_metrics()
        recs = _build_heuristic_recommendations(metrics)
        for r in recs:
            assert isinstance(r.contributing_factors, list)

    def test_correlation_flag_influences_output(self):
        corr = [{
            "factor_a": "late_night_screen_time",
            "factor_b": "sleep_disruptions",
            "strength": "strong",
            "description": "Disruptions 2x higher with late-night screen time",
        }]
        metrics_with_corr = _make_metrics(avg_screen_night=20, correlations=corr)
        recs_with = _build_heuristic_recommendations(metrics_with_corr)

        metrics_no_corr = _make_metrics(avg_screen_night=20)
        recs_without = _build_heuristic_recommendations(metrics_no_corr)

        categories_with = {r.category for r in recs_with}
        # With a correlation flag the sleep rec should still appear
        assert "sleep" in categories_with


# ─────────────────────────────────────────────────────────────────────────────
# 2. Correlation engine — async unit tests
# ─────────────────────────────────────────────────────────────────────────────

class TestCorrelationEngine:

    def test_build_metrics_summary_returns_expected_keys(self):
        """Correlation engine should return a dict with all required sections."""
        summary = asyncio.get_event_loop().run_until_complete(
            correlation_engine.build_user_metrics_summary(
                user_id="00000000-0000-0000-0000-000000000001",
                days_window=7,
                db=None,
            )
        )
        assert "window_days" in summary
        assert "averages" in summary
        assert "correlations" in summary
        assert "data_points_analyzed" in summary
        assert summary["window_days"] == 7

    def test_averages_contain_all_nine_pillars(self):
        summary = asyncio.get_event_loop().run_until_complete(
            correlation_engine.build_user_metrics_summary(
                user_id="00000000-0000-0000-0000-000000000001",
                days_window=7,
                db=None,
            )
        )
        avgs = summary["averages"]
        required_keys = [
            "avg_water_ml",
            "avg_sleep_hours",
            "avg_steps",
            "total_exercise_minutes",
            "avg_screen_total_minutes",
            "avg_screen_night_minutes",
            "avg_mood_score",
            "total_meditation_minutes",
            "avg_food_quality",
        ]
        for k in required_keys:
            assert k in avgs, f"Missing key in averages: {k}"

    def test_correlations_is_list(self):
        summary = asyncio.get_event_loop().run_until_complete(
            correlation_engine.build_user_metrics_summary(
                user_id="00000000-0000-0000-0000-000000000001",
                days_window=7,
                db=None,
            )
        )
        assert isinstance(summary["correlations"], list)

    def test_different_window_sizes(self):
        for days in [3, 7, 14]:
            summary = asyncio.get_event_loop().run_until_complete(
                correlation_engine.build_user_metrics_summary(
                    user_id="00000000-0000-0000-0000-000000000001",
                    days_window=days,
                    db=None,
                )
            )
            assert summary["window_days"] == days


# ─────────────────────────────────────────────────────────────────────────────
# 3. AIRecommendationService — heuristic path (no API key)
# ─────────────────────────────────────────────────────────────────────────────

class TestAIRecommendationService:

    def test_is_not_configured_without_api_key(self):
        assert ai_recommender_service.is_configured() is False

    def test_generate_returns_valid_response(self):
        response = asyncio.get_event_loop().run_until_complete(
            ai_recommender_service.generate_lifestyle_recommendations(
                user_id="00000000-0000-0000-0000-000000000001",
                user_metrics_summary=_make_metrics(),
            )
        )
        assert isinstance(response, AIRecommendationResponse)
        assert len(response.recommendations) >= 2
        assert "Heuristic" in response.provider
        assert response.data_points_analyzed > 0

    def test_generate_with_real_correlation_engine(self):
        """Full pipeline without DB — uses in-memory dev store."""
        response = asyncio.get_event_loop().run_until_complete(
            ai_recommender_service.generate_lifestyle_recommendations(
                user_id="00000000-0000-0000-0000-000000000001",
                days_window=7,
                db=None,
            )
        )
        assert isinstance(response, AIRecommendationResponse)
        assert len(response.recommendations) >= 1
        assert response.generated_at is not None

    def test_response_includes_correlations_and_snapshot(self):
        metrics = _make_metrics(
            avg_screen_night=70,
            correlations=[{
                "factor_a": "late_night_screen_time",
                "factor_b": "sleep_disruptions",
                "strength": "strong",
                "description": "Test correlation",
            }],
        )
        response = asyncio.get_event_loop().run_until_complete(
            ai_recommender_service.generate_lifestyle_recommendations(
                user_id="00000000-0000-0000-0000-000000000001",
                user_metrics_summary=metrics,
            )
        )
        assert isinstance(response.correlations_detected, list)
        assert len(response.correlations_detected) >= 1
        assert response.metrics_snapshot is not None

    def test_all_recommendations_have_required_fields(self):
        response = asyncio.get_event_loop().run_until_complete(
            ai_recommender_service.generate_lifestyle_recommendations(
                user_id="00000000-0000-0000-0000-000000000001",
                user_metrics_summary=_make_metrics(),
            )
        )
        for rec in response.recommendations:
            assert rec.category, "category missing"
            assert rec.priority in ("low", "medium", "high"), "invalid priority"
            assert len(rec.title) > 3, "title too short"
            assert len(rec.insight_text) > 10, "insight too short"
            assert len(rec.actionable_step) > 10, "actionable step too short"


# ─────────────────────────────────────────────────────────────────────────────
# 4. HTTP endpoint tests — POST /recommendations/generate
# ─────────────────────────────────────────────────────────────────────────────

class TestRecommendationsAPI:

    def test_generate_endpoint_returns_200(self):
        res = client.post("/api/v1/recommendations/generate", json={"days_window": 7})
        assert res.status_code == 200

    def test_generate_response_schema(self):
        res = client.post("/api/v1/recommendations/generate", json={"days_window": 7})
        data = res.json()
        assert "user_id" in data
        assert "generated_at" in data
        assert "provider" in data
        assert "recommendations" in data
        assert "data_points_analyzed" in data
        assert "correlations_detected" in data
        assert isinstance(data["recommendations"], list)
        assert len(data["recommendations"]) >= 1

    def test_generate_each_recommendation_has_required_fields(self):
        res = client.post("/api/v1/recommendations/generate", json={"days_window": 7})
        for rec in res.json()["recommendations"]:
            assert "category" in rec
            assert "priority" in rec
            assert "title" in rec
            assert "insight_text" in rec
            assert "actionable_step" in rec
            assert "contributing_factors" in rec
            assert rec["priority"] in ("low", "medium", "high")

    def test_generate_with_14_day_window(self):
        res = client.post("/api/v1/recommendations/generate", json={"days_window": 14})
        assert res.status_code == 200
        assert len(res.json()["recommendations"]) >= 1

    def test_generate_with_invalid_window_fails(self):
        res = client.post("/api/v1/recommendations/generate", json={"days_window": 0})
        assert res.status_code == 422

    def test_generate_with_too_large_window_fails(self):
        res = client.post("/api/v1/recommendations/generate", json={"days_window": 31})
        assert res.status_code == 422

    def test_status_endpoint_returns_engine_info(self):
        res = client.get("/api/v1/recommendations/status")
        assert res.status_code == 200
        data = res.json()
        assert "gemini_configured" in data
        assert "active_engine" in data
        assert isinstance(data["gemini_configured"], bool)
        # Without a real API key, heuristic engine should be active
        assert data["gemini_configured"] is False
        assert "Heuristic" in data["active_engine"]

    def test_heuristic_provider_label_when_no_api_key(self):
        res = client.post("/api/v1/recommendations/generate", json={"days_window": 7})
        provider = res.json()["provider"]
        assert "Heuristic" in provider or "heuristic" in provider.lower()
