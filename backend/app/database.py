from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Determine SQLite fallback path based on environment
sqlite_path = "sqlite:////tmp/splitwise.db" if os.getenv("VERCEL") == "1" else "sqlite:///./splitwise.db"

# Vercel/Neon provides POSTGRES_URL or DATABASE_URL
raw_db_url = os.getenv("POSTGRES_URL") or os.getenv("DATABASE_URL") or sqlite_path

# SQLAlchemy needs postgresql:// instead of postgres://
if raw_db_url.startswith("postgres://"):
    raw_db_url = raw_db_url.replace("postgres://", "postgresql://", 1)

DATABASE_URL = raw_db_url

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
    echo=False  # Disabled in production
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
