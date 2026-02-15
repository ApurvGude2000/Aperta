"""
Database session management.
"""
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    async_sessionmaker,
    AsyncEngine
)
from sqlalchemy.pool import NullPool
from config import settings
from utils.logger import setup_logger

logger = setup_logger(__name__)


def _get_engine() -> AsyncEngine:
    """
    Get database engine - auto-detects Cloud SQL or uses local database.

    Returns:
        AsyncEngine: Database engine
    """
    # Check if Cloud SQL is configured
    if settings.cloud_sql_instance_connection_name and settings.cloud_sql_password:
        logger.info("Using Cloud SQL connection")
        from utils.cloud_sql import get_cloud_sql_engine
        import asyncio

        # Create Cloud SQL engine (async)
        # Note: This creates the engine synchronously for initialization
        # The actual connections are async
        try:
            from google.cloud.sql.connector import Connector
            import asyncpg

            connector = Connector()

            def getconn():
                """Create sync connection for engine initialization."""
                loop = asyncio.new_event_loop()
                conn = loop.run_until_complete(
                    connector.connect_async(
                        settings.cloud_sql_instance_connection_name,
                        "asyncpg",
                        user=settings.cloud_sql_user,
                        password=settings.cloud_sql_password,
                        db=settings.cloud_sql_database_name,
                    )
                )
                return conn

            engine = create_async_engine(
                "postgresql+asyncpg://",
                async_creator=lambda: connector.connect_async(
                    settings.cloud_sql_instance_connection_name,
                    "asyncpg",
                    user=settings.cloud_sql_user,
                    password=settings.cloud_sql_password,
                    db=settings.cloud_sql_database_name,
                ),
                echo=settings.debug,
                pool_size=5,
                max_overflow=10,
            )
            logger.info(f"Cloud SQL engine created: {settings.cloud_sql_instance_connection_name}")
            return engine

        except Exception as e:
            logger.error(f"Failed to create Cloud SQL engine: {e}")
            logger.warning("Falling back to local database")

    # Use local database (SQLite or other)
    logger.info(f"Using local database: {settings.database_url}")
    engine = create_async_engine(
        settings.database_url,
        echo=settings.debug,
        future=True,
        poolclass=NullPool if "sqlite" in settings.database_url else None
    )
    return engine


# Create async engine (auto-detects Cloud SQL or local)
engine = _get_engine()

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Get database session.

    Yields:
        AsyncSession: Database session
    """
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


async def init_db() -> None:
    """Initialize database tables."""
    from .models import Base
    from .models_auth import Base as AuthBase

    async with engine.begin() as conn:
        # Create main app tables
        await conn.run_sync(Base.metadata.create_all)
        # Create auth tables
        await conn.run_sync(AuthBase.metadata.create_all)
    logger.info("Database tables created successfully")


async def close_db() -> None:
    """Close database connections."""
    await engine.dispose()
    logger.info("Database connections closed")
