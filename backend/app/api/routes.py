from fastapi import APIRouter
from app.api.endpoints import health, auth

api_router = APIRouter()

# Include endpoint routers
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])

@api_router.get("/")
async def api_root():
    return {"message": "GenAI CloudOps API v1.0", "status": "running"} 