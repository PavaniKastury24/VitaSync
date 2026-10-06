# VitaSync Python Backend (FastAPI)

VitaSync's core business logic, lifestyle data correlation, and Google Gemini AI recommendation engine.

## Features
- **FastAPI**: Async, high performance, automatic OpenAPI documentation.
- **Google Gemini**: Uses official `google-genai` Python SDK for intelligent lifestyle habits synthesis.
- **Supabase Integration**: Asymmetric JWT verification for Row Level Security (RLS) support.
- **SQLAlchemy (Asyncpg)**: Async database connectivity for PostgreSQL.

## Getting Started

### 1. Setup Virtual Environment
```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 2. Install Dependencies
```powershell
pip install -r requirements.txt
```

### 3. Environment Variables
Copy `.env.example` to `.env` and fill in your keys:
```powershell
cp .env.example .env
```

### 4. Run the Server
```powershell
uvicorn app.main:app --reload --port 8000
```

- API Base URL: `http://localhost:8000`
- Swagger Documentation: `http://localhost:8000/docs`
- Redoc Documentation: `http://localhost:8000/redoc`
- Liveness Probe: `http://localhost:8000/api/v1/health`
- Readiness Probe: `http://localhost:8000/api/v1/health/ready`
