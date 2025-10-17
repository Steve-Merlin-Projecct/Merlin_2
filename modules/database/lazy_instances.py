"""
Lazy Database Instance Management

Provides singleton instances that only connect when first accessed.
This prevents database connections from being established at module import time.

Key Benefits:
- No connections during import
- Thread-safe singleton pattern
- Efficient reuse of database instances
- Graceful degradation on connection failures

Usage:
    from modules.database.lazy_instances import get_database_manager, get_database_client

    # In route handlers:
    @app.route('/some-endpoint')
    def my_route():
        db_manager = get_database_manager()  # Lazy! Only connects on first call
        return db_manager.get_recent_jobs()
"""

import logging
from functools import lru_cache
from typing import Optional

logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def get_database_manager():
    """
    Get singleton DatabaseManager instance with lazy initialization.

    The instance is created only on first call and reused for subsequent calls.
    Uses @lru_cache for thread-safe singleton pattern.

    Returns:
        DatabaseManager: Singleton database manager instance

    Raises:
        Exception: If database manager cannot be initialized

    Example:
        >>> db_manager = get_database_manager()
        >>> jobs = db_manager.get_recent_jobs()
    """
    from .database_manager import DatabaseManager

    try:
        logger.info("Initializing DatabaseManager singleton (lazy)")
        return DatabaseManager()
    except Exception as e:
        logger.error(f"Failed to initialize DatabaseManager: {e}")
        raise


@lru_cache(maxsize=1)
def get_database_client():
    """
    Get singleton DatabaseClient instance with lazy initialization.

    The instance is created only on first call and reused for subsequent calls.
    Uses @lru_cache for thread-safe singleton pattern.

    Returns:
        DatabaseClient: Singleton database client instance

    Raises:
        Exception: If database client cannot be initialized

    Example:
        >>> db_client = get_database_client()
        >>> with db_client.get_session() as session:
        ...     result = session.execute(text("SELECT 1"))
    """
    from .database_client import DatabaseClient

    try:
        logger.info("Initializing DatabaseClient singleton (lazy)")
        return DatabaseClient()
    except Exception as e:
        logger.error(f"Failed to initialize DatabaseClient: {e}")
        raise


def reset_singletons():
    """
    Reset singleton instances (useful for testing).

    Clears the LRU cache, forcing new instances to be created on next access.
    Should only be used in test scenarios.

    Example:
        >>> reset_singletons()  # Clear cached instances
        >>> db_manager = get_database_manager()  # Creates fresh instance
    """
    get_database_manager.cache_clear()
    get_database_client.cache_clear()
    logger.info("Database singletons reset")
