from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import api_router
from app.core.config import settings
from app.core.database import create_tables, init_default_roles

app = FastAPI(
    title="GenAI CloudOps API",
    version="1.0.0",
    description="Backend API for GenAI CloudOps Platform with Authentication"
)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    """Initialize database and default data on startup"""
    try:
        # Create all database tables
        create_tables()
        print("Database tables created successfully")
        
        # Initialize default roles
        init_default_roles()
        print("Default roles initialized successfully")
        
    except Exception as e:
        print(f"Error during startup: {e}")

# Include API routes
app.include_router(api_router, prefix="/api/v1")

@app.get("/")
async def root():
    return {
        "message": "Welcome to GenAI CloudOps API", 
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "GenAI CloudOps API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 