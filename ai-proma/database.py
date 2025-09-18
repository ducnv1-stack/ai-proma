"""
PostgreSQL Database Configuration for FARAMEX AI
"""
import os
from typing import AsyncGenerator
from sqlalchemy import create_engine, MetaData, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from databases import Database
from dotenv import load_dotenv
import logging

# Load environment variables
try:
    load_dotenv()
except:
    pass  # Ignore .env file errors

# Database configuration from environment variables
DB_HOST = os.getenv("DB_HOST", "103.20.97.195")
DB_PORT = os.getenv("DB_PORT", "5434")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "WfSYR4kQh3a8N3JD3VHaKfGysMUBKgdbF5V")
DB_NAME = os.getenv("DB_NAME", "postgres")

# Build database URL
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
ASYNC_DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")

# Add schema configuration - Enable ai_proma schema
SCHEMA_NAME = "ai_proma"

# Database instance for async operations
database = Database(ASYNC_DATABASE_URL)

# SQLAlchemy setup
engine = create_async_engine(
    ASYNC_DATABASE_URL,
    echo=os.getenv("DEBUG", "False").lower() == "true",
    pool_size=int(os.getenv("DB_POOL_SIZE", "5")),
    max_overflow=int(os.getenv("DB_MAX_OVERFLOW", "10")),
    pool_timeout=int(os.getenv("DB_POOL_TIMEOUT", "30")),
    connect_args={
        "server_settings": {
            "search_path": "ai_proma,public"
        }
    }
)

# Session maker
AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

# Base class for models with schema
Base = declarative_base()
if SCHEMA_NAME:
    Base.metadata.schema = SCHEMA_NAME

# Metadata for migrations
metadata = MetaData(schema=SCHEMA_NAME) if SCHEMA_NAME else MetaData()

# Logging
logger = logging.getLogger(__name__)

async def get_database() -> Database:
    """Get database instance"""
    return database

async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Get database session for dependency injection"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            await session.close()

async def connect_db():
    """Connect to database"""
    try:
        await database.connect()
        logger.info("✅ Connected to PostgreSQL database")
    except Exception as e:
        logger.error(f"❌ Failed to connect to database: {e}")
        raise

async def disconnect_db():
    """Disconnect from database"""
    try:
        await database.disconnect()
        logger.info("🔌 Disconnected from PostgreSQL database")
    except Exception as e:
        logger.error(f"❌ Failed to disconnect from database: {e}")

async def create_tables():
    """Create all tables"""
    try:
        async with engine.begin() as conn:
            # Create schema if it doesn't exist (only if schema is specified)
            if SCHEMA_NAME:
                try:
                    await conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS {SCHEMA_NAME}"))
                except Exception as schema_error:
                    logger.warning(f"Schema creation warning: {schema_error}")
            
            # Create all tables
            await conn.run_sync(Base.metadata.create_all)
        
        schema_msg = f" in schema {SCHEMA_NAME}" if SCHEMA_NAME else ""
        logger.info(f"✅ Database tables created successfully{schema_msg}")
    except Exception as e:
        logger.error(f"❌ Failed to create tables: {e}")
        # Continue without raising to allow server to start
        pass

async def check_db_connection():
    """Check database connection"""
    try:
        query = "SELECT 1"
        result = await database.fetch_one(query)
        if result:
            logger.info("✅ Database connection is healthy")
            return True
        return False
    except Exception as e:
        logger.error(f"❌ Database connection check failed: {e}")
        return False

# Database health check endpoint
async def get_db_health():
    """Get database health status"""
    try:
        is_connected = await check_db_connection()
        return {
            "database": "postgresql",
            "status": "healthy" if is_connected else "unhealthy",
            "url": DATABASE_URL.split("@")[1] if "@" in DATABASE_URL else "localhost"
        }
    except Exception as e:
        return {
            "database": "postgresql", 
            "status": "error",
            "error": str(e)
        }
