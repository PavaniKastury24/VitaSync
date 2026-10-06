-- ====================================================================
-- VitaSync — Initial Database Migration Schema
-- Version: 20261005000000
-- Target: Supabase PostgreSQL 15+
-- Description: Core tables, 9 tracking modules, daily summaries,
--              user goals, AI recommendations, indices, and RLS policies.
-- ====================================================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ====================================================================
-- 1. PROFILES (Extends Supabase auth.users)
-- ====================================================================
CREATE TABLE IF NOT EXISTS public.profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    username VARCHAR(50) UNIQUE,
    full_name VARCHAR(100),
    avatar_url TEXT,
    timezone VARCHAR(50) DEFAULT 'UTC',
    metric_units BOOLEAN DEFAULT TRUE, -- TRUE for metric (ml, km), FALSE for imperial (oz, mi)
    preferences JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT timezone('utc'::text, now()) NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- Trigger to automatically create profile on signup
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS trigger AS $$
BEGIN
    INSERT INTO public.profiles (id, full_name, avatar_url)
    VALUES (
        new.id,
        new.raw_user_meta_data->>'full_name',
        new.raw_user_meta_data->>'avatar_url'
    );
    RETURN new;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

-- ====================================================================
-- 2. WATER INTAKE TRACKER
-- ====================================================================
CREATE TABLE IF NOT EXISTS public.water_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    amount_ml INT NOT NULL CHECK (amount_ml > 0 AND amount_ml <= 5000),
    logged_at TIMESTAMPTZ DEFAULT timezone('utc'::text, now()) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- ====================================================================
-- 3. SLEEP TRACKER
-- ====================================================================
CREATE TABLE IF NOT EXISTS public.sleep_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    start_time TIMESTAMPTZ NOT NULL,
    end_time TIMESTAMPTZ NOT NULL,
    duration_minutes INT GENERATED ALWAYS AS (
        GREATEST(0, ROUND(EXTRACT(EPOCH FROM (end_time - start_time)) / 60))
    ) STORED,
    quality_rating INT CHECK (quality_rating BETWEEN 1 AND 5),
    disruptions_count INT DEFAULT 0 CHECK (disruptions_count >= 0),
    notes TEXT,
    logged_date DATE NOT NULL DEFAULT CURRENT_DATE,
    created_at TIMESTAMPTZ DEFAULT timezone('utc'::text, now()) NOT NULL,
    CONSTRAINT sleep_valid_range CHECK (end_time >= start_time)
);

-- ====================================================================
-- 4. EXERCISE TRACKER
-- ====================================================================
CREATE TABLE IF NOT EXISTS public.exercise_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    exercise_type VARCHAR(50) NOT NULL, -- e.g. running, weightlifting, cycling, yoga
    duration_minutes INT NOT NULL CHECK (duration_minutes > 0 AND duration_minutes <= 1440),
    intensity_level INT CHECK (intensity_level BETWEEN 1 AND 10), -- RPE scale
    calories_burned INT CHECK (calories_burned >= 0),
    notes TEXT,
    logged_at TIMESTAMPTZ DEFAULT timezone('utc'::text, now()) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- ====================================================================
-- 5. FOOD HABITS TRACKER
-- ====================================================================
CREATE TABLE IF NOT EXISTS public.food_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    meal_type VARCHAR(20) NOT NULL CHECK (meal_type IN ('breakfast', 'lunch', 'dinner', 'snack')),
    quality_rating INT CHECK (quality_rating BETWEEN 1 AND 5), -- nutritional health score
    hunger_before INT CHECK (hunger_before BETWEEN 1 AND 5),
    mindful_eating BOOLEAN DEFAULT TRUE,
    notes TEXT,
    logged_at TIMESTAMPTZ DEFAULT timezone('utc'::text, now()) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- ====================================================================
-- 6. STUDY & PRODUCTIVITY TRACKER
-- ====================================================================
CREATE TABLE IF NOT EXISTS public.productivity_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    category VARCHAR(50) NOT NULL, -- e.g. programming, reading, deep work, math
    duration_minutes INT NOT NULL CHECK (duration_minutes > 0 AND duration_minutes <= 1440),
    focus_rating INT CHECK (focus_rating BETWEEN 1 AND 5),
    notes TEXT,
    logged_date DATE NOT NULL DEFAULT CURRENT_DATE,
    created_at TIMESTAMPTZ DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- ====================================================================
-- 7. SCREEN TIME TRACKER
-- ====================================================================
CREATE TABLE IF NOT EXISTS public.screen_time_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    total_minutes INT NOT NULL CHECK (total_minutes >= 0 AND total_minutes <= 1440),
    work_minutes INT DEFAULT 0 CHECK (work_minutes >= 0),
    leisure_minutes INT DEFAULT 0 CHECK (leisure_minutes >= 0),
    night_minutes INT DEFAULT 0 CHECK (night_minutes >= 0), -- Screen time within 1 hour of sleep
    notes TEXT,
    logged_date DATE NOT NULL DEFAULT CURRENT_DATE,
    created_at TIMESTAMPTZ DEFAULT timezone('utc'::text, now()) NOT NULL,
    UNIQUE (user_id, logged_date)
);

-- ====================================================================
-- 8. MOOD TRACKER
-- ====================================================================
CREATE TABLE IF NOT EXISTS public.mood_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    score INT NOT NULL CHECK (score BETWEEN 1 AND 10), -- 1 = very low, 10 = euphoric
    energy_level INT CHECK (energy_level BETWEEN 1 AND 5),
    tags TEXT[] DEFAULT '{}', -- e.g. ['calm', 'anxious', 'inspired', 'tired']
    notes TEXT,
    logged_at TIMESTAMPTZ DEFAULT timezone('utc'::text, now()) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- ====================================================================
-- 9. MEDITATION TRACKER
-- ====================================================================
CREATE TABLE IF NOT EXISTS public.meditation_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    duration_minutes INT NOT NULL CHECK (duration_minutes > 0 AND duration_minutes <= 360),
    technique VARCHAR(50) DEFAULT 'mindfulness', -- e.g. mindfulness, breathwork, guided, body_scan
    calmness_rating INT CHECK (calmness_rating BETWEEN 1 AND 5),
    notes TEXT,
    logged_at TIMESTAMPTZ DEFAULT timezone('utc'::text, now()) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- ====================================================================
-- 10. STEPS TRACKER
-- ====================================================================
CREATE TABLE IF NOT EXISTS public.step_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    step_count INT NOT NULL CHECK (step_count >= 0 AND step_count <= 100000),
    distance_meters INT CHECK (distance_meters >= 0),
    active_duration_minutes INT CHECK (active_duration_minutes >= 0),
    logged_date DATE NOT NULL DEFAULT CURRENT_DATE,
    created_at TIMESTAMPTZ DEFAULT timezone('utc'::text, now()) NOT NULL,
    UNIQUE (user_id, logged_date)
);

-- ====================================================================
-- 11. USER GOALS
-- ====================================================================
CREATE TABLE IF NOT EXISTS public.user_goals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    metric_type VARCHAR(30) NOT NULL, -- water, sleep_hours, steps, exercise_minutes, screen_time_max, etc.
    target_value NUMERIC(10, 2) NOT NULL CHECK (target_value > 0),
    unit VARCHAR(20) NOT NULL, -- ml, hours, steps, minutes
    frequency VARCHAR(20) DEFAULT 'daily' CHECK (frequency IN ('daily', 'weekly')),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT timezone('utc'::text, now()) NOT NULL,
    UNIQUE (user_id, metric_type)
);

-- ====================================================================
-- 12. DAILY SUMMARIES (Aggregated analytical cache)
-- ====================================================================
CREATE TABLE IF NOT EXISTS public.daily_summaries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    summary_date DATE NOT NULL,
    total_water_ml INT DEFAULT 0,
    total_sleep_minutes INT DEFAULT 0,
    sleep_quality INT DEFAULT 0,
    total_exercise_minutes INT DEFAULT 0,
    total_steps INT DEFAULT 0,
    total_screen_time_minutes INT DEFAULT 0,
    total_productivity_minutes INT DEFAULT 0,
    total_meditation_minutes INT DEFAULT 0,
    average_mood NUMERIC(3, 1),
    lifestyle_score INT DEFAULT 0 CHECK (lifestyle_score BETWEEN 0 AND 100),
    summary_metadata JSONB DEFAULT '{}'::jsonb,
    calculated_at TIMESTAMPTZ DEFAULT timezone('utc'::text, now()) NOT NULL,
    UNIQUE (user_id, summary_date)
);

-- ====================================================================
-- 13. AI RECOMMENDATIONS (Google Gemini Generated)
-- ====================================================================
CREATE TABLE IF NOT EXISTS public.ai_recommendations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    date_generated DATE NOT NULL DEFAULT CURRENT_DATE,
    category VARCHAR(50) NOT NULL, -- sleep_optimization, hydration, productivity, screen_balance, holistic
    priority VARCHAR(20) DEFAULT 'medium' CHECK (priority IN ('low', 'medium', 'high')),
    title VARCHAR(150) NOT NULL,
    insight_text TEXT NOT NULL,
    actionable_step TEXT NOT NULL,
    contributing_factors JSONB DEFAULT '[]'::jsonb,
    is_read BOOLEAN DEFAULT FALSE,
    is_bookmarked BOOLEAN DEFAULT FALSE,
    user_feedback INT DEFAULT 0 CHECK (user_feedback IN (-1, 0, 1)), -- -1 = unhelpful, 1 = helpful
    created_at TIMESTAMPTZ DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- ====================================================================
-- 14. PERFORMANCE INDEXES
-- ====================================================================
CREATE INDEX IF NOT EXISTS idx_water_logs_user_date ON public.water_logs(user_id, logged_at DESC);
CREATE INDEX IF NOT EXISTS idx_sleep_logs_user_date ON public.sleep_logs(user_id, logged_date DESC);
CREATE INDEX IF NOT EXISTS idx_exercise_logs_user_date ON public.exercise_logs(user_id, logged_at DESC);
CREATE INDEX IF NOT EXISTS idx_food_logs_user_date ON public.food_logs(user_id, logged_at DESC);
CREATE INDEX IF NOT EXISTS idx_productivity_logs_user_date ON public.productivity_logs(user_id, logged_date DESC);
CREATE INDEX IF NOT EXISTS idx_screen_time_logs_user_date ON public.screen_time_logs(user_id, logged_date DESC);
CREATE INDEX IF NOT EXISTS idx_mood_logs_user_date ON public.mood_logs(user_id, logged_at DESC);
CREATE INDEX IF NOT EXISTS idx_meditation_logs_user_date ON public.meditation_logs(user_id, logged_at DESC);
CREATE INDEX IF NOT EXISTS idx_step_logs_user_date ON public.step_logs(user_id, logged_date DESC);
CREATE INDEX IF NOT EXISTS idx_daily_summaries_user_date ON public.daily_summaries(user_id, summary_date DESC);
CREATE INDEX IF NOT EXISTS idx_ai_recs_user_date ON public.ai_recommendations(user_id, date_generated DESC);

-- ====================================================================
-- 15. ROW LEVEL SECURITY (RLS) POLICIES
-- Enforce strict data isolation for every user
-- ====================================================================
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.water_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.sleep_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.exercise_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.food_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.productivity_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.screen_time_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.mood_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.meditation_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.step_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_goals ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.daily_summaries ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.ai_recommendations ENABLE ROW LEVEL SECURITY;

-- Helper macro for standard user ownership policies
DO $$
DECLARE
    tbl text;
BEGIN
    FOR tbl IN
        SELECT unnest(ARRAY[
            'profiles', 'water_logs', 'sleep_logs', 'exercise_logs',
            'food_logs', 'productivity_logs', 'screen_time_logs',
            'mood_logs', 'meditation_logs', 'step_logs', 'user_goals',
            'daily_summaries', 'ai_recommendations'
        ])
    LOOP
        IF tbl = 'profiles' THEN
            EXECUTE format('
                DROP POLICY IF EXISTS "Users can view their own profile" ON public.%I;
                CREATE POLICY "Users can view their own profile" ON public.%I
                    FOR SELECT USING (auth.uid() = id);

                DROP POLICY IF EXISTS "Users can update their own profile" ON public.%I;
                CREATE POLICY "Users can update their own profile" ON public.%I
                    FOR UPDATE USING (auth.uid() = id);
            ', tbl, tbl, tbl, tbl);
        ELSE
            EXECUTE format('
                DROP POLICY IF EXISTS "Users can view their own %s" ON public.%I;
                CREATE POLICY "Users can view their own %s" ON public.%I
                    FOR SELECT USING (auth.uid() = user_id);

                DROP POLICY IF EXISTS "Users can insert their own %s" ON public.%I;
                CREATE POLICY "Users can insert their own %s" ON public.%I
                    FOR INSERT WITH CHECK (auth.uid() = user_id);

                DROP POLICY IF EXISTS "Users can update their own %s" ON public.%I;
                CREATE POLICY "Users can update their own %s" ON public.%I
                    FOR UPDATE USING (auth.uid() = user_id);

                DROP POLICY IF EXISTS "Users can delete their own %s" ON public.%I;
                CREATE POLICY "Users can delete their own %s" ON public.%I
                    FOR DELETE USING (auth.uid() = user_id);
            ', tbl, tbl, tbl, tbl, tbl, tbl, tbl, tbl, tbl, tbl, tbl, tbl, tbl, tbl, tbl, tbl);
        END IF;
    END LOOP;
END
$$;

