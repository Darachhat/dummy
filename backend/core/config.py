from decimal import Decimal
from pydantic_settings import BaseSettings

class Settings(BaseSettings):

    USE_MOCK_OSP: bool

    CDC_API_BASE: str
    CDC_API_AUTH: str
    CDC_PARTNER: str
    CDC_TIMEOUT: int

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

    class Config:
        env_file = ".env"
        extra = "allow" # allow extra fields env

settings = Settings()
