"""Application configuration management."""
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application
    APP_NAME: str = "PhD Timeline Intelligence Platform"
    DEBUG: bool = False
    ENVIRONMENT: str = "production"
    
    # Database
    DATABASE_URL: str
    DATABASE_ECHO: bool = False
    
    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000"]
    
    # API
    API_V1_PREFIX: str = "/api/v1"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore"
    )


try:
    settings = Settings()
    # #region agent log
    import json
    with open(r'd:\Frensei-Engine\.cursor\debug.log', 'a') as f:
        f.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"D","location":"config.py:36","message":"Settings loaded","data":{"has_database_url":hasattr(settings, 'DATABASE_URL'),"has_secret_key":hasattr(settings, 'SECRET_KEY'),"database_url_set":bool(getattr(settings, 'DATABASE_URL', None))},"timestamp":int(__import__('time').time()*1000)}) + '\n')
    # #endregion
except Exception as e:
    # #region agent log
    import json
    with open(r'd:\Frensei-Engine\.cursor\debug.log', 'a') as f:
        f.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"D","location":"config.py:36","message":"Settings load failed","data":{"error":str(e),"error_type":type(e).__name__},"timestamp":int(__import__('time').time()*1000)}) + '\n')
    # #endregion
    raise
