from fastapi import APIRouter
from app.api.endpoints import health, auth, monitoring, cloud
from app.core.gateway import get_gateway

api_router = APIRouter()

# Include endpoint routers
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(monitoring.router, prefix="/monitoring", tags=["monitoring"])
api_router.include_router(cloud.router, prefix="/cloud", tags=["cloud-operations"])

# Include gateway routes
gateway = get_gateway()
api_router.include_router(gateway.router, prefix="/gateway", tags=["gateway"])

@api_router.get("/")
async def api_root():
    return {
        "message": "GenAI CloudOps API v1.0", 
        "status": "running",
        "features": [
            "authentication", 
            "role-based-access-control",
            "monitoring", 
            "api-gateway", 
            "rate-limiting",
            "cloud-operations",
            "kubernetes-integration",
            "async-microservices"
        ],
        "endpoints": {
            "health": "/health",
            "auth": "/auth", 
            "monitoring": "/monitoring",
            "gateway": "/gateway",
            "cloud": "/cloud"
        },
        "microservices": {
            "authentication": "User management and JWT-based auth",
            "cloud-operations": "OCI/AWS/Azure resource management",
            "kubernetes": "Pod and cluster monitoring",
            "security": "Alert management and remediation",
            "cost-analysis": "Resource cost optimization"
        }
    } 