# backend/core/config.py
from decimal import Decimal
from pathlib import Path
from pydantic_settings import BaseSettings
from pydantic import Field, validator

class Settings(BaseSettings):
    # Mock flag
    USE_MOCK_OSP: bool = Field(False)

    # Core
    DATABASE_URL: str
    SECRET_KEY: str
    DEBUG: bool = Field(False)
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    CORS_ORIGINS: str = ""

    # OSP
    OSP_BASE_URL: str
    OSP_AUTH: str
    OSP_PARTNER: str = ""
    OSP_TIMEOUT: int = 30

    # Money
    FEE_AMOUNT: Decimal
    USD_TO_KHR_RATE: Decimal

    # API metadata
    API_VERSION: str = "v1.0.0"
    API_TITLE: str = "Dummy Bank API"
    API_DESCRIPTION: str = "API for Dummy Bank Application"
    API_CONTACT_NAME: str = "Dummy Bank Support Team"
    API_CONTACT_EMAIL: str = "dummybank@dev.com"

    # Logging
    SINGLE_PROCESS: bool = Field(False)
    LOG_LEVEL: str = Field("INFO")
    LOG_PATH: str = Field("/workspace/logs")

    @validator("LOG_PATH")
    def ensure_log_path(cls, v):
        Path(v).mkdir(parents=True, exist_ok=True)
        return v

    model_config = {
        "env_file": ".env",
        "case_sensitive": False
    }


settings = Settings()
