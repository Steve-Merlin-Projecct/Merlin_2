"""
Module: database_client.py
Purpose: Base PostgreSQL database client with connection management
Created: 2024-08-18
Modified: 2025-10-21
Dependencies: SQLAlchemy, database_config
Related: database_manager.py, database_config.py, lazy_instances.py
Description: Provides PostgreSQL connection management with SQLAlchemy ORM,
             automatic Docker vs local environment detection, connection pooling,
             session handling with context managers, and transaction management.
             Base class for all database operations.
"""

import os
import logging
from datetime import datetime
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import SQLAlchemyError
from contextlib import contextmanager
from .database_config import get_database_config

# Create base class for database models
Base = declarative_base()


class DatabaseClient:
    """
    Base database client for PostgreSQL connections.

    Provides connection management and session handling for all database operations.
    Uses SQLAlchemy for ORM functionality and connection pooling.
    Automatically detects Docker vs local environment for connection configuration.

    Attributes:
        database_url (str): PostgreSQL connection URL from environment-aware config
        engine: SQLAlchemy engine with connection pooling
        SessionLocal: Session factory for creating database sessions
        is_docker (bool): True if running in Docker container
    """

    def __init__(self):
        """
        Initialize database connection with environment detection.

        Automatically detects Docker vs local environment and uses appropriate
        connection configuration. Falls back gracefully if environment detection fails.

        Raises:
            ValueError: If database configuration cannot be established
        """
        # Get environment-aware database configuration
        db_config = get_database_config()
        self.database_url = db_config.get_connection_url()
        self.is_docker = db_config.is_docker

        if not self.database_url:
            raise ValueError("Database configuration could not be established")

        # Get connection pool configuration from environment (for managed databases)
        pool_size = int(os.environ.get('DATABASE_POOL_SIZE', '10'))
        max_overflow = int(os.environ.get('DATABASE_MAX_OVERFLOW', '20'))
        pool_timeout = int(os.environ.get('DATABASE_POOL_TIMEOUT', '30'))
        pool_recycle = int(os.environ.get('DATABASE_POOL_RECYCLE', '300'))

        # Validate pool configuration
        total_connections = pool_size + max_overflow
        logging.info(
            f"Connection pool configured: "
            f"pool_size={pool_size}, max_overflow={max_overflow}, "
            f"total={total_connections}, timeout={pool_timeout}s"
        )

        # Create engine with connection pooling and resource limits
        self.engine = create_engine(
            self.database_url,
            pool_pre_ping=True,  # Test connections before use
            pool_recycle=pool_recycle,  # Recycle connections (default: 5 minutes)
            pool_size=pool_size,  # Maximum permanent connections in pool
            max_overflow=max_overflow,  # Additional connections if pool exhausted
            pool_timeout=pool_timeout,  # Wait before raising error
            echo=False  # Set to True for SQL debugging
        )

        # Configure query timeout at connection level
        from sqlalchemy import event

        @event.listens_for(self.engine, "connect")
        def set_query_timeout(dbapi_conn, connection_record):
            """Set statement timeout to prevent long-running queries from hanging."""
            try:
                cursor = dbapi_conn.cursor()
                cursor.execute("SET statement_timeout = '30s'")  # 30 second query timeout
                cursor.close()
            except Exception as e:
                logging.warning(f"Could not set query timeout: {e}")

        # Create session factory
        self.SessionLocal = sessionmaker(bind=self.engine)

        env_type = "Docker" if self.is_docker else "Local"
        logging.info(f"Database client initialized successfully ({env_type} environment)")

    @contextmanager
    def get_session(self):
        """
        Context manager for database sessions.

        Automatically handles commit/rollback and session cleanup.
        Commits on success, rolls back on exception.

        Yields:
            Session: SQLAlchemy session object

        Raises:
            Exception: Re-raises any exception after rolling back
        """
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logging.error(f"Database session error: {e}")
            raise
        finally:
            session.close()

    def test_connection(self):
        """
        Test database connectivity.

        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            with self.get_session() as session:
                result = session.execute(text("SELECT 1")).fetchone()
                logging.info("Database connection test successful")
                return True
        except Exception as e:
            logging.error(f"Database connection test failed: {e}")
            return False

    def execute_raw_sql(self, sql_query, parameters=None):
        """
        Execute raw SQL query

        Args:
            sql_query (str): SQL query to execute
            parameters (dict, optional): Query parameters

        Returns:
            Result set or None for non-SELECT queries
        """
        try:
            with self.get_session() as session:
                # Handle parameters properly for different query types
                if parameters:
                    result = session.execute(text(sql_query), parameters)
                else:
                    result = session.execute(text(sql_query))

                # Return results for SELECT queries
                if sql_query.strip().upper().startswith("SELECT"):
                    return result.fetchall()
                else:
                    # For non-SELECT queries, return rowcount if available
                    try:
                        return result.rowcount
                    except:
                        return 0

        except SQLAlchemyError as e:
            logging.error(f"Raw SQL execution error: {e}")
            raise

    def create_tables(self):
        """Create all tables defined in models"""
        try:
            Base.metadata.create_all(self.engine)
            logging.info("Database tables created successfully")
        except Exception as e:
            logging.error(f"Error creating tables: {e}")
            raise

    def execute_query(self, query: str, params=None) -> list:
        """Execute raw SQL query with proper error handling and flexible parameter formats"""
        try:
            with self.get_session() as session:
                # Handle different parameter formats for SQLAlchemy compatibility
                if params is not None:
                    # Convert parameters to proper format for SQLAlchemy text() queries
                    if isinstance(params, (list, tuple)):
                        # For positional parameters with %s placeholders, convert to dict
                        param_count = query.count("%s")
                        if param_count > 0 and len(params) == param_count:
                            # Create numbered parameter dict for %s style queries
                            param_dict = {f"param_{i}": param for i, param in enumerate(params)}
                            # Replace %s with :param_0, :param_1, etc.
                            formatted_query = query
                            for i in range(param_count):
                                formatted_query = formatted_query.replace("%s", f":param_{i}", 1)
                            result = session.execute(text(formatted_query), param_dict)
                        else:
                            # Use params as-is for named parameters
                            result = session.execute(text(query), dict(enumerate(params)))
                    elif isinstance(params, dict):
                        # Dict parameters, use as-is
                        result = session.execute(text(query), params)
                    else:
                        # Single parameter
                        result = session.execute(text(query), {"param_0": params})
                else:
                    result = session.execute(text(query))

                # Handle different query types
                if query.strip().upper().startswith("SELECT"):
                    return [dict(row._mapping) for row in result]
                else:
                    session.commit()
                    return []

        except Exception as e:
            logging.error(f"Database session error: {e}")
            logging.error(f"Query: {query}")
            logging.error(f"Params: {params}")
            raise

    def drop_tables(self):
        """Drop all tables (use with caution)"""
        try:
            Base.metadata.drop_all(self.engine)
            logging.info("Database tables dropped successfully")
        except Exception as e:
            logging.error(f"Error dropping tables: {e}")
            raise
