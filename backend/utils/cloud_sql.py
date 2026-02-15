# ABOUTME: Cloud SQL connection helper for GCP Cloud SQL instances using Cloud SQL Python Connector.
# ABOUTME: Provides async PostgreSQL connections with automatic IAM authentication and connection pooling.

from google.cloud.sql.connector import Connector
import asyncpg
import sqlalchemy
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine
from config import settings
from utils.logger import setup_logger
from typing import Optional

logger = setup_logger(__name__)


async def get_cloud_sql_engine() -> AsyncEngine:
    """
    Create SQLAlchemy async engine for Cloud SQL PostgreSQL.

    Returns:
        AsyncEngine: SQLAlchemy async engine
    """
    if not settings.cloud_sql_instance_connection_name:
        raise ValueError("Cloud SQL instance connection name not configured")

    logger.info(f"Connecting to Cloud SQL: {settings.cloud_sql_instance_connection_name}")

    # Initialize Cloud SQL Python Connector
    connector = Connector()

    async def getconn() -> asyncpg.Connection:
        """Create connection to Cloud SQL instance."""
        conn = await connector.connect_async(
            settings.cloud_sql_instance_connection_name,
            "asyncpg",
            user=settings.cloud_sql_user,
            password=settings.cloud_sql_password,
            db=settings.cloud_sql_database_name,
        )
        return conn

    # Create SQLAlchemy engine
    engine = create_async_engine(
        "postgresql+asyncpg://",
        async_creator=getconn,
        echo=settings.debug,
        pool_size=5,
        max_overflow=10,
    )

    logger.info("Cloud SQL engine created successfully")
    return engine


def should_use_cloud_sql() -> bool:
    """
    Check if Cloud SQL should be used based on configuration.

    Returns:
        bool: True if Cloud SQL is configured
    """
    return (
        settings.cloud_sql_instance_connection_name is not None
        and settings.cloud_sql_password is not None
    )
