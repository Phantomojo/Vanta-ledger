import os
import secrets
from typing import Optional

class Settings:
    # Application
    APP_NAME: str = "Vanta Ledger API"
    VERSION: str = "2.0.0"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    # Server
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8500"))
    
    # Database - Use environment variables only
    MONGO_URI: str = os.getenv("MONGO_URI", "mongodb://user:password@localhost:27017/vanta_ledger")
    POSTGRES_URI: str = os.getenv("POSTGRES_URI", "postgresql://user:password@localhost:5432/vanta_ledger")
    REDIS_URI: str = os.getenv("REDIS_URI", "redis://localhost:6379/0")
    DATABASE_NAME: str = os.getenv("DATABASE_NAME", "vanta_ledger")
    
    # Security - Generate secure defaults if not provided
    SECRET_KEY: str = os.getenv("SECRET_KEY", secrets.token_urlsafe(32))
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = int(os.getenv("RATE_LIMIT_PER_MINUTE", "100"))
    RATE_LIMIT_PER_HOUR: int = int(os.getenv("RATE_LIMIT_PER_HOUR", "1000"))
    
    # File Storage
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "../data/uploads")
    PROCESSED_DOCUMENTS_DIR: str = os.getenv("PROCESSED_DOCUMENTS_DIR", "../data/processed_documents")
    MAX_FILE_SIZE: int = int(os.getenv("MAX_FILE_SIZE", "10485760"))  # 10MB
    
    # Cache
    CACHE_DURATION: int = int(os.getenv("CACHE_DURATION", "300"))  # 5 minutes
    
    # Pagination
    DEFAULT_PAGE_SIZE: int = int(os.getenv("DEFAULT_PAGE_SIZE", "100"))
    MAX_PAGE_SIZE: int = int(os.getenv("MAX_PAGE_SIZE", "1000"))
    
    # CORS
    ALLOWED_ORIGINS: list = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173,http://localhost:5174,http://127.0.0.1:5174,http://localhost:5175,http://127.0.0.1:5175,http://localhost:5176,http://127.0.0.1:5176").split(",")
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: str = os.getenv("LOG_FILE", "logs/app.log")

settings = Settings() 