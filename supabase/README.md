# VitaSync Database & Supabase Guide

This directory houses the PostgreSQL schema migrations and seed scripts for VitaSync.

## Applying the Migration

### Option A: Via Supabase Web Dashboard (Recommended)
1. Log into your project at [Supabase Dashboard](https://supabase.com/dashboard).
2. Go to the **SQL Editor** tab on the left sidebar.
3. Open `supabase/migrations/20261005000000_vitasync_initial_schema.sql`, copy all contents, and click **Run**.
4. Verify that 13 tables are created under the `public` schema with RLS enabled.

### Option B: Via Supabase CLI (Local Development)
```bash
# Install Supabase CLI if not present
npx supabase login
npx supabase init
npx supabase start
npx supabase db push
```

## Security & RLS
Every table has **Row Level Security (RLS)** active. All read, insert, update, and delete actions are checked against `auth.uid() = user_id`, guaranteeing full data isolation between users.
