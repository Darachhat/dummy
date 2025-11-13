# backend/core/config.py
from decimal import Decimal
from pydantic_settings import BaseSettings
from decouple import config

class Settings(BaseSettings):
    USE_MOCK_OSP                    : bool = config('USE_MOCK_OSP', cast=lambda x: x.lower() == 'true', default=False)

    DATABASE_URL                    : str = config('DATABASE_URL', cast=str)
    SECRET_KEY                      : str = config('SECRET_KEY', cast=str)
    DEBUG                           : bool = config('DEBUG', cast=lambda x: x.lower() == 'true', default=False)
    ACCESS_TOKEN_EXPIRE_MINUTES     : int = config('ACCESS_TOKEN_EXPIRE_MINUTES', cast=int)
    CORS_ORIGINS                    : str = config('CORS_ORIGINS', cast=str)

    OSP_BASE_URL                    : str = config('OSP_BASE_URL', cast=str)
    OSP_AUTH                        : str = config('OSP_AUTH', cast=str)
    OSP_PARTNER                     : str = config('OSP_PARTNER', cast=str, default='')
    OSP_TIMEOUT                     : int = config('OSP_TIMEOUT', cast=int, default=30)

    FEE_AMOUNT                      : Decimal = config('FEE_AMOUNT', cast=Decimal)
    USD_TO_KHR_RATE                 : Decimal = config('USD_TO_KHR_RATE', cast=Decimal)

settings = Settings()
