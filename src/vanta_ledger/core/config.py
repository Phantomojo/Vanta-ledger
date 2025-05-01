import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite+aiosqlite:///./vanta_ledger.db"
    API_KEY: str = "supersecretadmintoken"

    class Config:
        env_file = ".env"

settings = Settings()

