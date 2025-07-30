from fastapi import APIRouter, Depends, status
from typing import Dict, Any
from datetime import datetime
import psutil
import sys
from app.core.middleware import get_monitoring_metrics
from app.core.database import get_db, engine
from app.core.security import verify_token
from sqlalchemy.orm import Session
from sqlalchemy import text

router = APIRouter()

@router.get("/metrics")
async def get_application_metrics() -> Dict[str, Any]:
    """Get application performance metrics"""
    metrics = get_monitoring_metrics()
    
    # Add system metrics
    system_metrics = {
        "cpu_usage": psutil.cpu_percent(interval=1),
        "memory_usage": psutil.virtual_memory().percent,
        "disk_usage": psutil.disk_usage('/').percent,
        "uptime": datetime.now().isoformat()
    }
    
    return {
        "application_metrics": metrics,
        "system_metrics": system_metrics,
        "timestamp": datetime.utcnow().isoformat()
    }

@router.get("/health/deep")
async def deep_health_check(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Comprehensive health check including database connectivity"""
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "environment": "development"
    }
    
    # Check database connectivity
    try:
        db.execute(text("SELECT 1"))
        health_status["database"] = {
            "status": "healthy",
            "connection": "active"
        }
    except Exception as e:
        health_status["status"] = "unhealthy"
        health_status["database"] = {
            "status": "unhealthy",
            "error": str(e)
        }
    
    # Check system resources
    try:
        cpu_usage = psutil.cpu_percent()
        memory_usage = psutil.virtual_memory().percent
        
        health_status["system"] = {
            "cpu_usage": cpu_usage,
            "memory_usage": memory_usage,
            "status": "healthy" if cpu_usage < 80 and memory_usage < 80 else "warning"
        }
    except Exception as e:
        health_status["system"] = {
            "status": "error",
            "error": str(e)
        }
    
    # Check Python version and dependencies
    health_status["runtime"] = {
        "python_version": sys.version,
        "platform": sys.platform
    }
    
    return health_status

@router.get("/stats")
async def get_application_stats() -> Dict[str, Any]:
    """Get detailed application statistics"""
    try:
        # Get database statistics
        with engine.connect() as conn:
            # Count total users
            user_count = conn.execute(text("SELECT COUNT(*) FROM users")).scalar()
            # Count total roles
            role_count = conn.execute(text("SELECT COUNT(*) FROM roles")).scalar()
        
        stats = {
            "database": {
                "total_users": user_count,
                "total_roles": role_count
            },
            "application": get_monitoring_metrics(),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return stats
        
    except Exception as e:
        return {
            "error": "Failed to retrieve statistics",
            "details": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

@router.get("/info")
async def get_api_info() -> Dict[str, Any]:
    """Get API information and available endpoints"""
    return {
        "name": "GenAI CloudOps API",
        "version": "1.0.0",
        "description": "Backend API for GenAI CloudOps Platform",
        "environment": "development",
        "features": [
            "Authentication & Authorization",
            "Role-Based Access Control",
            "Rate Limiting",
            "Request Logging",
            "Error Handling",
            "Monitoring & Metrics"
        ],
        "endpoints": {
            "auth": "/api/v1/auth",
            "health": "/api/v1/health",
            "monitoring": "/api/v1/monitoring",
            "docs": "/docs",
            "openapi": "/openapi.json"
        },
        "timestamp": datetime.utcnow().isoformat()
    } 