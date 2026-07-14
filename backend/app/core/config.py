import os

class Settings:
    PROJECT_NAME: str = "AuraFinance API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")
    
    # CORS
    _env_origins = os.getenv("BACKEND_CORS_ORIGINS")
    if _env_origins:
        BACKEND_CORS_ORIGINS: list[str] = [o.strip() for o in _env_origins.split(",") if o.strip()]
    else:
        BACKEND_CORS_ORIGINS: list[str] = [
            "http://localhost:5173",
            "http://127.0.0.1:5173",
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            "https://quanlichitieu-2-i20i.onrender.com",
        ]

settings = Settings()

# Fail fast if SECRET_KEY is not set in production
if settings.ENVIRONMENT == "production" and not settings.SECRET_KEY:
    raise RuntimeError(
        "CRITICAL: SECRET_KEY environment variable is not set! "
        "A strong random SECRET_KEY is required for production."
    )
