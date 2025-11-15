from pydantic_settings import BaseSettings
from typing import Optional, List


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/coding_agent"
    REDIS_URL: str = "redis://localhost:6379"
    
    JWT_SECRET_KEY: str = "your-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 24
    
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    DEFAULT_OLLAMA_MODEL: str = "codellama:latest"
    HARDWARE_TIER: str = "standard"
    
    GITHUB_CLIENT_ID: Optional[str] = None
    GITHUB_CLIENT_SECRET: Optional[str] = None
    GITHUB_REDIRECT_URI: str = "http://localhost:8000/api/v1/auth/github/callback"
    
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:8080"
    
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = True
    
    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]


settings = Settings()
