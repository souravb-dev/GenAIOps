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
    REDIS_ENABLED: bool = True  # Enable Redis when available for better performance
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    
    # OCI Configuration  
    OCI_CONFIG_FILE: str = "C:\\Users\\2374439\\.oci\\config"
    OCI_PROFILE: str = "DEFAULT"
    OCI_REGION: str = "eu-frankfurt-1"
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
    
    # GenAI Configuration
    GROQ_API_KEY: str = "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"
    GROQ_MODEL: str = "llama3-8b-8192"  # Default Groq model
    GROQ_MAX_TOKENS: int = 1024
    GROQ_TEMPERATURE: float = 0.7
    GROQ_TIMEOUT: int = 30  # seconds
    GENAI_CACHE_TTL: int = 3600  # 1 hour cache for GenAI responses
    GENAI_RATE_LIMIT_PER_MINUTE: int = 100
    GENAI_MAX_CONTEXT_LENGTH: int = 4000
    GENAI_ENABLE_CACHING: bool = False  # Disabled for now - can enable with Redis later
    GENAI_ENABLE_BATCHING: bool = True
    GENAI_BATCH_SIZE: int = 5
    GENAI_FALLBACK_MODEL: str = "mixtral-8x7b-32768"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings() 