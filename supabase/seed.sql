-- ====================================================================
-- VitaSync — Development & Testing Seed Data
-- Target: Supabase PostgreSQL 15+
-- Description: Realistic 7-day multi-dimensional wellness logs for testing
--              correlations, score computations, and AI recommendations.
-- ====================================================================

DO $$
DECLARE
    target_user_id UUID;
BEGIN
    -- 1. Determine target user: Look for an existing registered auth user,
    --    or fallback to a deterministic local dev UUID.
    SELECT id INTO target_user_id FROM auth.users ORDER BY created_at ASC LIMIT 1;

    IF target_user_id IS NULL THEN
        target_user_id := '00000000-0000-0000-0000-000000000001'::uuid;
        -- If running in local mock environment without Supabase auth.users table constraints,
        -- create mock profile directly if possible:
        BEGIN
            INSERT INTO public.profiles (id, username, full_name, timezone, metric_units)
            VALUES (target_user_id, 'demo_user', 'Demo Wellness User', 'UTC', TRUE)
            ON CONFLICT (id) DO NOTHING;
        EXCEPTION WHEN foreign_key_violation THEN
            RAISE NOTICE 'No auth.users found. Please sign up at least one user before running seed.sql.';
            RETURN;
        END;
    ELSE
        -- Ensure profile exists for the active user
        INSERT INTO public.profiles (id, username, full_name, timezone, metric_units)
        VALUES (target_user_id, 'demo_user', 'Demo Wellness User', 'UTC', TRUE)
        ON CONFLICT (id) DO UPDATE SET full_name = EXCLUDED.full_name;
    END IF;

    RAISE NOTICE 'Seeding VitaSync logs for user_id: %', target_user_id;

    -- 2. User Wellness Goals
    INSERT INTO public.user_goals (user_id, metric_type, target_value, unit, frequency)
    VALUES
        (target_user_id, 'water', 2500, 'ml', 'daily'),
        (target_user_id, 'sleep_hours', 8.0, 'hours', 'daily'),
        (target_user_id, 'steps', 10000, 'steps', 'daily'),
        (target_user_id, 'exercise_minutes', 45, 'minutes', 'daily'),
        (target_user_id, 'screen_time_max', 360, 'minutes', 'daily'),
        (target_user_id, 'meditation', 15, 'minutes', 'daily')
    ON CONFLICT (user_id, metric_type) DO UPDATE
        SET target_value = EXCLUDED.target_value;

    -- 3. Water Intake Logs (Past 7 Days)
    INSERT INTO public.water_logs (user_id, amount_ml, logged_at)
    VALUES
        (target_user_id, 500, now() - interval '6 days' + interval '8 hours'),
        (target_user_id, 750, now() - interval '6 days' + interval '13 hours'),
        (target_user_id, 600, now() - interval '6 days' + interval '18 hours'),
        (target_user_id, 500, now() - interval '5 days' + interval '8 hours'),
        (target_user_id, 800, now() - interval '5 days' + interval '14 hours'),
        (target_user_id, 500, now() - interval '4 days' + interval '9 hours'),
        (target_user_id, 650, now() - interval '4 days' + interval '15 hours'),
        (target_user_id, 700, now() - interval '3 days' + interval '8 hours'),
        (target_user_id, 750, now() - interval '3 days' + interval '13 hours'),
        (target_user_id, 800, now() - interval '3 days' + interval '19 hours'),
        (target_user_id, 600, now() - interval '2 days' + interval '9 hours'),
        (target_user_id, 500, now() - interval '2 days' + interval '14 hours'),
        (target_user_id, 750, now() - interval '1 day' + interval '8 hours'),
        (target_user_id, 1000, now() - interval '1 day' + interval '13 hours'),
        (target_user_id, 750, now() - interval '1 day' + interval '18 hours'),
        (target_user_id, 500, now() - interval '2 hours')
    ON CONFLICT DO NOTHING;

    -- 4. Sleep Logs (Past 7 Days)
    INSERT INTO public.sleep_logs (user_id, start_time, end_time, quality_rating, disruptions_count, notes, logged_date)
    VALUES
        (target_user_id, now() - interval '7 days' + interval '23 hours', now() - interval '6 days' + interval '7 hours', 4, 1, 'Felt well-rested', (CURRENT_DATE - 6)),
        (target_user_id, now() - interval '6 days' + interval '23 hours 30 mins', now() - interval '5 days' + interval '6 hours 30 mins', 3, 2, 'Woke up once around 3 AM', (CURRENT_DATE - 5)),
        (target_user_id, now() - interval '5 days' + interval '23 hours', now() - interval '4 days' + interval '7 hours 15 mins', 4, 0, 'Deep restorative sleep', (CURRENT_DATE - 4)),
        (target_user_id, now() - interval '4 days' + interval '23 hours 45 mins', now() - interval '3 days' + interval '6 hours 15 mins', 2, 3, 'Late screen time, restless', (CURRENT_DATE - 3)),
        (target_user_id, now() - interval '3 days' + interval '22 hours 45 mins', now() - interval '2 days' + interval '7 hours', 4, 1, 'Good recovery after workout', (CURRENT_DATE - 2)),
        (target_user_id, now() - interval '2 days' + interval '23 hours', now() - interval '1 day' + interval '7 hours 30 mins', 5, 0, 'Optimal 8.5h sleep cycle', (CURRENT_DATE - 1)),
        (target_user_id, now() - interval '1 day' + interval '23 hours 15 mins', now() - interval '7 hours', 4, 1, 'Consistent sleep schedule', CURRENT_DATE)
    ON CONFLICT DO NOTHING;

    -- 5. Exercise Logs (Past 7 Days)
    INSERT INTO public.exercise_logs (user_id, exercise_type, duration_minutes, intensity_level, calories_burned, notes, logged_at)
    VALUES
        (target_user_id, 'running', 35, 7, 340, 'Morning outdoor run at moderate pace', now() - interval '6 days' + interval '8 hours'),
        (target_user_id, 'weightlifting', 45, 8, 290, 'Upper body strength session', now() - interval '4 days' + interval '17 hours'),
        (target_user_id, 'cycling', 40, 6, 310, 'Evening indoor cycling session', now() - interval '3 days' + interval '18 hours'),
        (target_user_id, 'yoga', 30, 4, 120, 'Vinyasa flow and mobility routine', now() - interval '1 day' + interval '8 hours')
    ON CONFLICT DO NOTHING;

    -- 6. Food Logs (Past 7 Days)
    INSERT INTO public.food_logs (user_id, meal_type, quality_rating, hunger_before, mindful_eating, notes, logged_at)
    VALUES
        (target_user_id, 'breakfast', 5, 4, TRUE, 'Oatmeal, blueberries, chia seeds and almond milk', now() - interval '3 days' + interval '8 hours'),
        (target_user_id, 'lunch', 4, 3, TRUE, 'Grilled chicken salad with quinoa and olive oil', now() - interval '3 days' + interval '13 hours'),
        (target_user_id, 'dinner', 4, 4, TRUE, 'Baked salmon with steamed asparagus and brown rice', now() - interval '3 days' + interval '19 hours'),
        (target_user_id, 'breakfast', 4, 3, TRUE, 'Avocado toast with poached eggs', now() - interval '1 day' + interval '8 hours'),
        (target_user_id, 'lunch', 5, 4, TRUE, 'Mediterranean bowl with hummus, greens, and lentils', now() - interval '1 day' + interval '13 hours')
    ON CONFLICT DO NOTHING;

    -- 7. Productivity Logs (Past 7 Days)
    INSERT INTO public.productivity_logs (user_id, category, duration_minutes, focus_rating, notes, logged_date)
    VALUES
        (target_user_id, 'programming', 180, 5, 'Built VitaSync backend API architecture', CURRENT_DATE - 3),
        (target_user_id, 'reading', 45, 4, 'Read 2 chapters on habit psychology', CURRENT_DATE - 2),
        (target_user_id, 'deep work', 150, 4, 'Focused system design and analysis', CURRENT_DATE - 1),
        (target_user_id, 'programming', 120, 5, 'Completed database integration modules', CURRENT_DATE)
    ON CONFLICT DO NOTHING;

    -- 8. Screen Time Logs (Past 7 Days)
    INSERT INTO public.screen_time_logs (user_id, total_minutes, work_minutes, leisure_minutes, night_minutes, notes, logged_date)
    VALUES
        (target_user_id, 340, 240, 100, 25, 'Standard workday screen time', CURRENT_DATE - 6),
        (target_user_id, 390, 270, 120, 45, 'Checked emails before bed', CURRENT_DATE - 5),
        (target_user_id, 310, 230, 80, 15, 'Read physical book at night', CURRENT_DATE - 4),
        (target_user_id, 450, 280, 170, 85, 'Late-night social media video streaming', CURRENT_DATE - 3),
        (target_user_id, 330, 250, 80, 20, 'Screen cutoff at 10 PM adhered to', CURRENT_DATE - 2),
        (target_user_id, 290, 220, 70, 10, 'Excellent digital hygiene evening', CURRENT_DATE - 1),
        (target_user_id, 310, 230, 80, 15, 'On track with screen time target', CURRENT_DATE)
    ON CONFLICT (user_id, logged_date) DO UPDATE
        SET total_minutes = EXCLUDED.total_minutes;

    -- 9. Mood Logs (Past 7 Days)
    INSERT INTO public.mood_logs (user_id, score, energy_level, tags, notes, logged_at)
    VALUES
        (target_user_id, 8, 4, ARRAY['energized', 'motivated'], 'Great start to the week', now() - interval '6 days' + interval '12 hours'),
        (target_user_id, 6, 3, ARRAY['tired', 'neutral'], 'Midweek slight fatigue', now() - interval '5 days' + interval '15 hours'),
        (target_user_id, 8, 4, ARRAY['focused', 'accomplished'], 'Finished critical milestone', now() - interval '4 days' + interval '18 hours'),
        (target_user_id, 5, 2, ARRAY['stressed', 'groggy'], 'Late night screen caused morning grogginess', now() - interval '3 days' + interval '10 hours'),
        (target_user_id, 9, 5, ARRAY['euphoric', 'peaceful'], 'Great workout and quality sleep', now() - interval '2 days' + interval '14 hours'),
        (target_user_id, 8, 4, ARRAY['content', 'balanced'], 'Solid productive day', now() - interval '1 day' + interval '16 hours'),
        (target_user_id, 9, 4, ARRAY['inspired', 'optimistic'], 'Feeling centered and ready for the week', now() - interval '2 hours')
    ON CONFLICT DO NOTHING;

    -- 10. Meditation Logs (Past 7 Days)
    INSERT INTO public.meditation_logs (user_id, duration_minutes, technique, calmness_rating, notes, logged_at)
    VALUES
        (target_user_id, 15, 'mindfulness', 4, '15-min breath focus session', now() - interval '6 days' + interval '7 hours'),
        (target_user_id, 20, 'body_scan', 5, 'Evening progressive relaxation', now() - interval '4 days' + interval '21 hours'),
        (target_user_id, 10, 'breathwork', 4, 'Box breathing during work break', now() - interval '2 days' + interval '14 hours'),
        (target_user_id, 15, 'mindfulness', 5, 'Morning silent meditation', now() - interval '1 day' + interval '7 hours')
    ON CONFLICT DO NOTHING;

    -- 11. Step Logs (Past 7 Days)
    INSERT INTO public.step_logs (user_id, step_count, distance_meters, active_duration_minutes, logged_date)
    VALUES
        (target_user_id, 10450, 7800, 75, CURRENT_DATE - 6),
        (target_user_id, 8750, 6500, 60, CURRENT_DATE - 5),
        (target_user_id, 11200, 8400, 85, CURRENT_DATE - 4),
        (target_user_id, 6800, 5100, 45, CURRENT_DATE - 3),
        (target_user_id, 10900, 8150, 80, CURRENT_DATE - 2),
        (target_user_id, 12400, 9300, 95, CURRENT_DATE - 1),
        (target_user_id, 8900, 6650, 65, CURRENT_DATE)
    ON CONFLICT (user_id, logged_date) DO UPDATE
        SET step_count = EXCLUDED.step_count;

    -- 12. Daily Summaries (Aggregated scores)
    INSERT INTO public.daily_summaries (
        user_id, summary_date, total_water_ml, total_sleep_minutes, sleep_quality,
        total_exercise_minutes, total_steps, total_screen_time_minutes,
        total_productivity_minutes, total_meditation_minutes, average_mood, lifestyle_score
    )
    VALUES
        (target_user_id, CURRENT_DATE - 2, 2100, 495, 4, 0, 10900, 330, 45, 10, 9.0, 84),
        (target_user_id, CURRENT_DATE - 1, 2500, 510, 5, 30, 12400, 290, 150, 15, 8.0, 92),
        (target_user_id, CURRENT_DATE, 1850, 465, 4, 0, 8900, 310, 120, 0, 9.0, 78)
    ON CONFLICT (user_id, summary_date) DO UPDATE
        SET lifestyle_score = EXCLUDED.lifestyle_score;

    -- 13. Sample AI Recommendations
    INSERT INTO public.ai_recommendations (
        user_id, date_generated, category, priority, title,
        insight_text, actionable_step, contributing_factors, is_read, is_bookmarked
    )
    VALUES
        (
            target_user_id,
            CURRENT_DATE,
            'sleep_optimization',
            'high',
            'Limit Late-Night Screen Exposure',
            'Your sleep logs show disruptions increase by 2x when late-night screen time exceeds 45 minutes.',
            'Activate bedtime screen mode and replace screen time with 15 minutes of light reading.',
            '["screen_time", "sleep_disruptions"]'::jsonb,
            FALSE,
            TRUE
        ),
        (
            target_user_id,
            CURRENT_DATE,
            'hydration',
            'medium',
            'Pre-load Water Before Morning Workouts',
            'On days where morning hydration is under 500ml, your perceived workout intensity rating is 2 points higher.',
            'Drink 1 tall glass (400ml) of water immediately after waking before starting exercise.',
            '["water_intake", "exercise_intensity"]'::jsonb,
            FALSE,
            FALSE
        ),
        (
            target_user_id,
            CURRENT_DATE,
            'holistic',
            'low',
            'Maintain Solid Step Consistency',
            'You have achieved >10,000 steps on 5 out of 7 days, maintaining a strong baseline daily wellness score.',
            'Keep up the post-dinner 15-minute walk to hit today''s 10k target.',
            '["steps", "lifestyle_score"]'::jsonb,
            TRUE,
            FALSE
        )
    ON CONFLICT DO NOTHING;

    RAISE NOTICE 'VitaSync 7-day seed dataset populated successfully for user %!', target_user_id;
END $$;
