from fastapi import APIRouter
from app.api.endpoints import health

api_router = APIRouter()

# Include endpoint routers
api_router.include_router(health.router, prefix="/health", tags=["health"])

@api_router.get("/")
async def api_root():
    return {"message": "GenAI CloudOps API v1.0"} 