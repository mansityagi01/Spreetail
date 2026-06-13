from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# MySQL connection string: mysql+pymysql://user:password@host:port/database
# For local dev, we'll use SQLite first, then switch to MySQL when deployed
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")

# For MySQL, use: mysql+pymysql://root:password@localhost/splitwise_mvp
# For now using SQLite for rapid local dev
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
    echo=True  # Log all SQL queries
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
