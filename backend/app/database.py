from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Vercel Postgres provides POSTGRES_URL. SQLAlchemy needs postgresql:// instead of postgres://
vercel_url = os.getenv("POSTGRES_URL")
if vercel_url and vercel_url.startswith("postgres://"):
    vercel_url = vercel_url.replace("postgres://", "postgresql://", 1)

DATABASE_URL = vercel_url or os.getenv("DATABASE_URL", "sqlite:///./splitwise.db")

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
