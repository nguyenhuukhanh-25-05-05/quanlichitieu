import logging
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

logger = logging.getLogger(__name__)

db_url = settings.DATABASE_URL
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

if not db_url:
    if settings.ENVIRONMENT == "production":
        raise RuntimeError("DATABASE_URL environment variable is not set!")
    db_url = "sqlite:///./finance.db"
    logger.warning("DATABASE_URL not set, falling back to SQLite for local development")

if db_url.startswith("sqlite"):
    engine = create_engine(
        db_url, connect_args={"check_same_thread": False}
    )
else:
    connect_args = {"connect_timeout": 3} if "postgresql" in db_url else {}
    engine = create_engine(
        db_url,
        connect_args=connect_args,
        pool_size=10,
        max_overflow=20,
        pool_recycle=3600,
    )
    try:
        with engine.connect() as conn:
            pass
    except Exception as e:
        logger.critical("Database connection failed: %s", e)
        raise

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
