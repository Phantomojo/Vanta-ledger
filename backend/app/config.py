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
    SECRET_KEY: str = os.getenv("SECRET_KEY", secrets.token_urlsafe(64))
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))
    
    # Password Security
    MIN_PASSWORD_LENGTH: int = int(os.getenv("MIN_PASSWORD_LENGTH", "8"))
    REQUIRE_SPECIAL_CHARS: bool = os.getenv("REQUIRE_SPECIAL_CHARS", "True").lower() == "true"
    REQUIRE_NUMBERS: bool = os.getenv("REQUIRE_NUMBERS", "True").lower() == "true"
    REQUIRE_UPPERCASE: bool = os.getenv("REQUIRE_UPPERCASE", "True").lower() == "true"
    PASSWORD_HISTORY_SIZE: int = int(os.getenv("PASSWORD_HISTORY_SIZE", "5"))
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = int(os.getenv("RATE_LIMIT_PER_MINUTE", "100"))
    RATE_LIMIT_PER_HOUR: int = int(os.getenv("RATE_LIMIT_PER_HOUR", "1000"))
    LOGIN_RATE_LIMIT_PER_MINUTE: int = int(os.getenv("LOGIN_RATE_LIMIT_PER_MINUTE", "5"))
    
    # File Storage
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "../data/uploads")
    PROCESSED_DOCUMENTS_DIR: str = os.getenv("PROCESSED_DOCUMENTS_DIR", "../data/processed_documents")
    MAX_FILE_SIZE: int = int(os.getenv("MAX_FILE_SIZE", "10485760"))  # 10MB
    ALLOWED_FILE_EXTENSIONS: list = os.getenv("ALLOWED_FILE_EXTENSIONS", ".pdf,.docx,.doc,.txt,.png,.jpg,.jpeg,.tiff,.bmp").split(",")
    
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
    
    # Security Headers
    ENABLE_HSTS: bool = os.getenv("ENABLE_HSTS", "True").lower() == "true"
    HSTS_MAX_AGE: int = int(os.getenv("HSTS_MAX_AGE", "31536000"))  # 1 year
    ENABLE_CSP: bool = os.getenv("ENABLE_CSP", "True").lower() == "true"
    
    # Session Security
    SESSION_TIMEOUT_MINUTES: int = int(os.getenv("SESSION_TIMEOUT_MINUTES", "30"))
    MAX_CONCURRENT_SESSIONS: int = int(os.getenv("MAX_CONCURRENT_SESSIONS", "5"))
    
    # API Security
    API_KEY_HEADER: str = os.getenv("API_KEY_HEADER", "X-API-Key")
    REQUIRE_API_KEY: bool = os.getenv("REQUIRE_API_KEY", "False").lower() == "true"
    
    # Local LLM Configuration
    ENABLE_LOCAL_LLM: bool = os.getenv("ENABLE_LOCAL_LLM", "True").lower() == "true"
    LLM_MODELS_DIR: str = os.getenv("LLM_MODELS_DIR", "../models")
    LLM_CACHE_TTL: int = int(os.getenv("LLM_CACHE_TTL", "3600"))  # 1 hour
    LLM_MAX_CONTEXT_LENGTH: int = int(os.getenv("LLM_MAX_CONTEXT_LENGTH", "4096"))
    LLM_DEFAULT_TEMPERATURE: float = float(os.getenv("LLM_DEFAULT_TEMPERATURE", "0.7"))
    LLM_USE_GPU: bool = os.getenv("LLM_USE_GPU", "True").lower() == "true"

settings = Settings() 