from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """Application configuration from environment variables"""
    
    # Database
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/riskguard"
    
    # Server
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_V1_PREFIX: str = "/api/v1"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    CORS_ORIGINS: list = ["http://localhost:3000", "http://localhost:5173", "http://localhost:8080"]
    
    # Environment
    ENVIRONMENT: str = "development"  # development, staging, production
    DEBUG: bool = True
    
    # Monitoring
    PROMETHEUS_PORT: int = 8001
    ENABLE_MONITORING: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
