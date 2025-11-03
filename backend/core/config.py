from decimal import Decimal
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    USE_MOCK_OSP: bool

    DATABASE_URL: str 
    SECRET_KEY: str
    DEBUG: bool 
    ACCESS_TOKEN_EXPIRE_MINUTES: int 
    CORS_ORIGINS: str 

    OSP_BASE_URL: str 
    OSP_AUTH: str 
    OSP_PARTNER: str
    OSP_TIMEOUT: int 

    FEE_AMOUNT: Decimal 
    USD_TO_KHR_RATE: Decimal 

    class Config:
        env_file = ".env"
        extra = "allow"

settings = Settings()
