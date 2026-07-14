import os
import secrets

_SECRET_KEY_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".secret_key")

class Settings:
    PROJECT_NAME: str = "AuraFinance API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    
    # Security
    _key = os.getenv("SECRET_KEY", "")
    if _key:
        SECRET_KEY: str = _key
    elif ENVIRONMENT == "production":
        raise RuntimeError(
            "CRITICAL: SECRET_KEY environment variable is not set! "
            "A strong random SECRET_KEY is required for production. "
            "Go to Render Dashboard > Environment > add SECRET_KEY."
        )
    else:
        _from_file = None
        try:
            with open(_SECRET_KEY_FILE, "r") as f:
                _from_file = f.read().strip()
        except (FileNotFoundError, PermissionError):
            pass
        if _from_file:
            SECRET_KEY: str = _from_file
        else:
            _generated = secrets.token_urlsafe(48)
            SECRET_KEY: str = _generated
            try:
                with open(_SECRET_KEY_FILE, "w") as f:
                    f.write(_generated)
            except PermissionError:
                pass
            import logging
            logging.getLogger(__name__).warning(
                "SECRET_KEY not set, generated one for development: %s", _generated
            )
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
