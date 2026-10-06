from typing import Dict, Any, Optional
from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str = "ok"
    version: str
    environment: str
    timestamp: str


class ReadinessResponse(BaseModel):
    status: str
    database_configured: bool
    supabase_configured: bool
    gemini_configured: bool
    details: Dict[str, Any]
