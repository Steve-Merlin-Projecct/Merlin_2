import os
import logging
from datetime import datetime
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import SQLAlchemyError
from contextlib import contextmanager

# Create base class for database models
Base = declarative_base()


class DatabaseClient:
    """
    Base database client for PostgreSQL connections.

    Provides connection management and session handling for all database operations.
    Uses SQLAlchemy for ORM functionality and connection pooling.

    Attributes:
        database_url (str): PostgreSQL connection URL from environment
        engine: SQLAlchemy engine with connection pooling
        SessionLocal: Session factory for creating database sessions
    """

    def __init__(self):
        """
        Initialize database connection.

        Raises:
            ValueError: If DATABASE_URL environment variable is not set
        """
        self.database_url = os.environ.get("DATABASE_URL")
        if not self.database_url:
            raise ValueError("DATABASE_URL environment variable not set")

        # Create engine with connection pooling
        self.engine = create_engine(
            self.database_url, pool_pre_ping=True, pool_recycle=300, echo=False  # Set to True for SQL debugging
        )

        # Create session factory
        self.SessionLocal = sessionmaker(bind=self.engine)

        logging.info("Database client initialized successfully")

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
