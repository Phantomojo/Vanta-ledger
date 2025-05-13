import os
from pydantic_settings import BaseSettings
from pydantic import ConfigDict

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./vanta_ledger.db"
    API_KEY: str = "supersecretadmintoken"
    EXPORT_LIMIT: int = 1000  # Max number of transactions to export
    ALLOWED_EXPORT_FORMATS: list = ["csv", "excel", "pdf"]
    LEDGER_DEFAULT_CURRENCY: str = "USD"
    LEDGER_ALLOW_NEGATIVE_BALANCE: bool = False

    model_config = ConfigDict(env_file=".env")

settings = Settings()
