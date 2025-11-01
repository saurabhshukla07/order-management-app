"""
Database configuration and session management
Handles database connection and provides session for database operations
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get database URL from environment variable
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/order_management")

# Create database engine
# echo=True will print all SQL queries (useful for debugging)
engine = create_engine(
    DATABASE_URL,
    echo=False,  # Set to True to see SQL queries in console
    pool_pre_ping=True  # Verify connections before using them
)

# Create SessionLocal class for database sessions
# autocommit=False: Don't auto-commit transactions
# autoflush=False: Don't auto-flush before queries
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """
    Dependency function to get database session
    Yields a database session and ensures it's closed after use
    Usage: db: Session = Depends(get_db)
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """
    Initialize database by creating all tables
    Should be called on application startup
    """
    from models import Base
    Base.metadata.create_all(bind=engine)
    print("✓ Database tables created successfully")