"""
Database configuration and models for Newsletter System
"""
from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Create database connection engine
# Uses SQLite for simplicity, can swap for PostgreSQL later
engine = create_engine(
    os.getenv("DATABASE_URL"),
    connect_args={"check_same_thread": False}  # SQLite specific
)

# Create session factory - each request gets its own session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for all models
Base = declarative_base()


class User(Base):
    """
    User model representing newsletter subscribers
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)  # Auto-incrementing ID
    email = Column(String, unique=True, index=True)     # User's email (unique)
    interests = Column(String)  # Comma-separated interests e.g., "tech,sports,business"
    subscribed = Column(Boolean, default=True)  # Subscription status


# Create all tables in the database
Base.metadata.create_all(bind=engine)