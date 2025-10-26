"""
Database Configuration and Session Management
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
import os
from pathlib import Path

# Use SQLite for simplicity (can be changed to PostgreSQL in production)
DATABASE_DIR = Path(__file__).parent
DATABASE_URL = f"sqlite:///{DATABASE_DIR}/epiwatch.db"

# Create engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},  # Needed for SQLite
    poolclass=StaticPool,
    echo=False  # Set to True for SQL query logging
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """
    Dependency function to get database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Initialize database tables
    """
    try:
        from backend.models import Base
    except ImportError:
        from models import Base
    Base.metadata.create_all(bind=engine)
