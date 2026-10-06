from datetime import datetime, timezone, timedelta
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "version" in data


def test_health_ready_endpoint():
    response = client.get("/api/v1/health/ready")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "details" in data


def test_water_tracker_flow():
    # 1. Log water
    payload = {"amount_ml": 650}
    res = client.post("/api/v1/trackers/water", json=payload)
    assert res.status_code == 201
    created = res.json()
    assert created["amount_ml"] == 650
    assert "id" in created

    # 2. Retrieve water
    res = client.get("/api/v1/trackers/water")
    assert res.status_code == 200
    items = res.json()
    assert len(items) >= 1
    assert any(item["amount_ml"] == 650 for item in items)


def test_water_validation_error():
    # Negative amount should fail validation
    res = client.post("/api/v1/trackers/water", json={"amount_ml": -100})
    assert res.status_code == 422


def test_sleep_tracker_flow():
    now = datetime.now(timezone.utc)
    start = (now - timedelta(hours=8)).isoformat()
    end = now.isoformat()

    payload = {
        "start_time": start,
        "end_time": end,
        "quality_rating": 4,
        "disruptions_count": 1,
        "notes": "Good sleep test",
    }
    res = client.post("/api/v1/trackers/sleep", json=payload)
    assert res.status_code == 201
    data = res.json()
    assert data["duration_minutes"] >= 470
    assert data["quality_rating"] == 4

    res = client.get("/api/v1/trackers/sleep")
    assert res.status_code == 200
    assert len(res.json()) >= 1


def test_exercise_tracker_flow():
    payload = {
        "exercise_type": "running",
        "duration_minutes": 35,
        "intensity_level": 7,
        "calories_burned": 320,
        "notes": "Morning jog",
    }
    res = client.post("/api/v1/trackers/exercise", json=payload)
    assert res.status_code == 201
    data = res.json()
    assert data["exercise_type"] == "running"
    assert data["duration_minutes"] == 35

    res = client.get("/api/v1/trackers/exercise")
    assert res.status_code == 200
    assert len(res.json()) >= 1


def test_food_tracker_flow():
    payload = {
        "meal_type": "lunch",
        "quality_rating": 5,
        "hunger_before": 3,
        "mindful_eating": True,
        "notes": "Salad with protein",
    }
    res = client.post("/api/v1/trackers/food", json=payload)
    assert res.status_code == 201
    assert res.json()["meal_type"] == "lunch"

    # Invalid meal type should fail
    bad_res = client.post("/api/v1/trackers/food", json={"meal_type": "brunch"})
    assert bad_res.status_code == 422


def test_productivity_tracker_flow():
    payload = {
        "category": "programming",
        "duration_minutes": 120,
        "focus_rating": 5,
        "notes": "Built Phase 3 endpoints",
    }
    res = client.post("/api/v1/trackers/productivity", json=payload)
    assert res.status_code == 201
    assert res.json()["category"] == "programming"


def test_screen_time_tracker_flow():
    payload = {
        "total_minutes": 340,
        "work_minutes": 250,
        "leisure_minutes": 90,
        "night_minutes": 15,
        "notes": "Controlled evening usage",
    }
    res = client.post("/api/v1/trackers/screen-time", json=payload)
    assert res.status_code == 201
    assert res.json()["total_minutes"] == 340


def test_mood_tracker_flow():
    payload = {
        "score": 8,
        "energy_level": 4,
        "tags": ["focused", "energized"],
        "notes": "Productive sprint",
    }
    res = client.post("/api/v1/trackers/mood", json=payload)
    assert res.status_code == 201
    assert res.json()["score"] == 8
    assert "energized" in res.json()["tags"]


def test_meditation_tracker_flow():
    payload = {
        "duration_minutes": 15,
        "technique": "breathwork",
        "calmness_rating": 5,
        "notes": "Box breathing",
    }
    res = client.post("/api/v1/trackers/meditation", json=payload)
    assert res.status_code == 201
    assert res.json()["duration_minutes"] == 15


def test_step_tracker_flow():
    payload = {
        "step_count": 10500,
        "distance_meters": 7800,
        "active_duration_minutes": 80,
    }
    res = client.post("/api/v1/trackers/steps", json=payload)
    assert res.status_code == 201
    assert res.json()["step_count"] == 10500


def test_user_goals_flow():
    payload = {
        "metric_type": "water",
        "target_value": 2500,
        "unit": "ml",
        "frequency": "daily",
    }
    res = client.post("/api/v1/trackers/goals", json=payload)
    assert res.status_code == 201
    assert res.json()["metric_type"] == "water"

    res = client.get("/api/v1/trackers/goals")
    assert res.status_code == 200
    assert len(res.json()) >= 1


def test_daily_summary_and_wellness_score():
    res = client.get("/api/v1/summary/daily")
    assert res.status_code == 200
    data = res.json()

    assert "lifestyle_score" in data
    assert 0 <= data["lifestyle_score"] <= 100
    assert "score_breakdown" in data
    assert "metrics" in data
    assert "highlights" in data
    assert len(data["highlights"]) >= 1

    breakdown = data["score_breakdown"]
    assert 0 <= breakdown["hydration_score"] <= 15
    assert 0 <= breakdown["sleep_score"] <= 20
    assert 0 <= breakdown["movement_score"] <= 15
    assert 0 <= breakdown["nutrition_score"] <= 15
    assert 0 <= breakdown["screen_hygiene_score"] <= 15
    assert 0 <= breakdown["mental_wellness_score"] <= 20
    assert breakdown["grade"] in ["Optimal", "Good", "Balanced", "Needs Attention"]


def test_authenticated_request_with_bearer_token():
    headers = {"Authorization": "Bearer dummy-jwt-token-for-test"}
    res = client.get("/api/v1/summary/daily", headers=headers)
    assert res.status_code == 200
    assert "lifestyle_score" in res.json()
