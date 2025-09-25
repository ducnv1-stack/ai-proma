from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func
import asyncpg
from configs import get_database_url

# Use centralized configuration for database URL
DATABASE_URL = get_database_url()

# Direct connection helper (no pool)
async def get_db_connection():
    """Create a new database connection each time"""
    return await asyncpg.connect(DATABASE_URL)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()