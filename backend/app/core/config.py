from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "GenAI CloudOps API"
    
    # CORS Settings
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",  # React dev server
        "http://localhost:5173",  # Vite dev server
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ]
    
    # Database Settings
    DATABASE_URL: str = "sqlite:///./genai_cloudops.db"
    
    # Security Settings
    SECRET_KEY: str = "your-secret-key-change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # Redis Settings
    REDIS_ENABLED: bool = True
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    
    # OCI Configuration
    OCI_CONFIG_FILE: str = "C:\\Users\\2375603\\.oci\\config"
    OCI_PROFILE: str = "DEFAULT"
    OCI_REGION: str = "us-ashburn-1"
    OCI_TENANCY_ID: str = ""
    OCI_USER_ID: str = ""
    OCI_FINGERPRINT: str = ""
    OCI_KEY_FILE: str = ""
    
    # Monitoring Configuration
    MONITORING_CACHE_TTL: int = 300  # 5 minutes cache for monitoring data
    ALERT_HISTORY_HOURS: int = 24  # Default hours of alert history to retrieve
    MAX_LOG_SEARCH_RESULTS: int = 1000  # Maximum log search results per query
    HEALTH_SCORE_THRESHOLD_HEALTHY: float = 90.0
    HEALTH_SCORE_THRESHOLD_WARNING: float = 70.0
    HEALTH_SCORE_THRESHOLD_DEGRADED: float = 50.0
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings() 