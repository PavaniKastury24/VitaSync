# VitaSync — Sync Your Lifestyle With Better Habits

VitaSync is a lifestyle and habit-management platform that tracks and correlates nine key wellness dimensions, providing actionable AI-driven lifestyle recommendations powered by Google Gemini.

---

## 🏗️ Architecture Overview

```
User
  ↓
Next.js 15 + TypeScript (Frontend Tier)
  ↓
Python FastAPI (Business Logic, Correlation & AI Engine)
  ↓
Supabase PostgreSQL (Persistence & Row Level Security)
```

### 9 Core Tracking Modules
1. 💧 **Water Intake** (hydration goals, volume in ml)
2. 😴 **Sleep** (duration, quality score 1-5, disruptions)
3. 🏃 **Exercise** (type, duration, perceived exertion, calories)
4. 🥗 **Food Habits** (meal type, nutritional quality, mindful eating)
5. 📚 **Study / Productivity** (focus intervals, categories, ratings)
6. 📱 **Screen Time** (work vs leisure, late-night screen time)
7. 🧠 **Mood** (daily valence 1-10, tags, energy levels)
8. 🧘 **Meditation** (mindfulness minutes, technique, calmness)
9. 👟 **Steps** (daily step count, distance, active minutes)

---

## 📁 Repository Structure

```
VitaSync_Pro/
├── frontend/               # Next.js 15, TypeScript, Tailwind CSS
│   ├── src/
│   │   ├── app/            # App Router pages and layout
│   │   ├── components/     # UI primitives & tracker widgets
│   │   └── lib/            # API client & Supabase helpers
│   ├── package.json
│   └── .env.example
├── backend/                # Python FastAPI, SQLAlchemy Async, google-genai
│   ├── app/
│   │   ├── api/v1/         # Route endpoints (health, trackers, AI)
│   │   ├── core/           # Config, Security (JWT), Database
│   │   ├── schemas/        # Pydantic schemas
│   │   ├── services/       # AI Recommender (Google Gemini)
│   │   └── main.py         # Application entry point
│   ├── requirements.txt
│   └── .env.example
├── supabase/               # PostgreSQL migrations & seed data
│   ├── migrations/         # Full schema with tables, RLS, indexes
│   └── seed.sql            # Sample development seed data
└── README.md               # Root documentation
```

---

## 🚀 Quick Start (Local Development)

### 1. Backend Setup (Python FastAPI)

```powershell
# Navigate to backend
cd backend

# Create and activate virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Copy environment variables
cp .env.example .env

# Run FastAPI development server
uvicorn app.main:app --reload --port 8000
```
Backend will be live at `http://localhost:8000`
Interactive API Docs: `http://localhost:8000/docs`

---

### 2. Frontend Setup (Next.js + TypeScript)

```powershell
# Navigate to frontend
cd frontend

# Copy environment variables
cp .env.example .env.local

# Install dependencies
npm.cmd install

# Run Next.js development server
npm.cmd run dev
```
Frontend will be live at `http://localhost:3000`

---

### 3. Database Setup (Supabase PostgreSQL)

When ready to link Supabase:
1. Create a project at [supabase.com](https://supabase.com).
2. Run the migration script located at `supabase/migrations/20261005000000_vitasync_initial_schema.sql` in the Supabase SQL Editor.
3. Copy your project URL, Anon Key, and Service Role Key into both `backend/.env` and `frontend/.env.local`.
