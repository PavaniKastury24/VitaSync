from fastapi import APIRouter
from app.api.v1.endpoints import health, recommendations, trackers, summary

api_v1_router = APIRouter()

# Register core endpoints
api_v1_router.include_router(health.router)
api_v1_router.include_router(recommendations.router)
api_v1_router.include_router(trackers.router)
api_v1_router.include_router(summary.router)
