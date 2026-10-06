import os
from pathlib import Path
import pytest
from app.core.database import Base
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
    DailySummary,
    AIRecommendation,
)

EXPECTED_TABLES = {
    "profiles",
    "user_goals",
    "water_logs",
    "sleep_logs",
    "exercise_logs",
    "food_logs",
    "productivity_logs",
    "screen_time_logs",
    "mood_logs",
    "meditation_logs",
    "step_logs",
    "daily_summaries",
    "ai_recommendations",
}


def test_sqlalchemy_metadata_contains_all_tables():
    """Verify all 13 tables are registered in the SQLAlchemy Base metadata."""
    registered_tables = set(Base.metadata.tables.keys())
    assert EXPECTED_TABLES.issubset(registered_tables), (
        f"Missing tables in metadata: {EXPECTED_TABLES - registered_tables}"
    )


def test_models_have_primary_and_foreign_keys():
    """Verify models have correct primary keys and foreign keys linking to profiles."""
    models_with_user_fk = [
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
        DailySummary,
        AIRecommendation,
    ]

    # Check Profile has primary key 'id'
    assert "id" in Profile.__table__.columns
    assert Profile.__table__.columns["id"].primary_key is True

    # Check each child model has user_id foreign key targeting profiles.id
    for model in models_with_user_fk:
        cols = model.__table__.columns
        assert "id" in cols, f"{model.__name__} missing id column"
        assert cols["id"].primary_key is True, f"{model.__name__} id must be primary key"
        assert "user_id" in cols, f"{model.__name__} missing user_id column"

        fk_targets = [fk.target_fullname for fk in cols["user_id"].foreign_keys]
        assert "profiles.id" in fk_targets, (
            f"{model.__name__}.user_id does not reference profiles.id (found: {fk_targets})"
        )


def test_migration_sql_covers_all_tables_and_rls():
    """Verify the Supabase SQL migration file covers all 13 tables with RLS enabled."""
    # Find root directory from backend/tests/
    repo_root = Path(__file__).resolve().parent.parent.parent
    migration_dir = repo_root / "supabase" / "migrations"
    migration_files = list(migration_dir.glob("*.sql"))

    assert len(migration_files) > 0, "No migration SQL files found in supabase/migrations"

    migration_content = migration_files[0].read_text(encoding="utf-8")

    # Check table creation DDL for all 13 tables
    for tbl in EXPECTED_TABLES:
        assert f"CREATE TABLE IF NOT EXISTS public.{tbl}" in migration_content, (
            f"Table public.{tbl} not created in migration SQL"
        )
        assert f"ALTER TABLE public.{tbl} ENABLE ROW LEVEL SECURITY;" in migration_content, (
            f"RLS not enabled for table {tbl} in migration SQL"
        )


def test_seed_sql_references_modules():
    """Verify seed.sql contains insert statements for all tracking modules."""
    repo_root = Path(__file__).resolve().parent.parent.parent
    seed_file = repo_root / "supabase" / "seed.sql"

    assert seed_file.exists(), "supabase/seed.sql does not exist"
    seed_content = seed_file.read_text(encoding="utf-8")

    for tbl in EXPECTED_TABLES:
        assert tbl in seed_content, f"Table {tbl} not referenced in seed.sql"
