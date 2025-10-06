import logging
from .database_client import DatabaseClient
from .database_reader import DatabaseReader
from .database_writer import DatabaseWriter


class DatabaseManager:
    """
    Database manager that combines reader and writer functionality.

    Provides a single interface for all database operations, combining
    the functionality of DatabaseReader and DatabaseWriter into one
    cohesive interface.

    Attributes:
        client: DatabaseClient instance for connection management
        reader: DatabaseReader instance for read operations
        writer: DatabaseWriter instance for write operations
    """

    def __init__(self):
        """
        Initialize database manager with reader and writer.

        Creates instances of DatabaseClient, DatabaseReader, and DatabaseWriter.
        Also initializes database tables and sets default application settings.
        """
        self.client = DatabaseClient()
        self.reader = DatabaseReader()
        self.writer = DatabaseWriter()

        # Initialize database tables
        self.initialize_database()

        logging.info("Database manager initialized successfully")

    def initialize_database(self):
        """
        Initialize database tables and check connectivity.

        Tests database connection, creates tables if they don't exist,
        and sets default application settings.

        Raises:
            Exception: If database connection test fails
        """
        try:
            # Test connection
            if not self.client.test_connection():
                raise Exception("Database connection test failed")

            # Create tables if they don't exist
            self.client.create_tables()

            # Set default application settings if they don't exist
            self._set_default_settings()

            logging.info("Database initialization completed")

        except Exception as e:
            logging.error(f"Database initialization failed: {e}")
            raise

    def _set_default_settings(self):
        """
        Set default application settings.

        Creates default settings in the database if they don't already exist.
        Settings include service version, default author, cleanup days, and logging flags.
        """
        default_settings = [
            {"key": "service_version", "value": "2.0.0", "type": "string", "description": "Current service version"},
            {
                "key": "default_author",
                "value": "Steve Glen",
                "type": "string",
                "description": "Default document author",
            },
            {"key": "cleanup_days", "value": "30", "type": "integer", "description": "Days to keep old job records"},
            {"key": "enable_logging", "value": "true", "type": "boolean", "description": "Enable detailed job logging"},
        ]

        for setting in default_settings:
            # Only set if doesn't exist
            existing = self.reader.get_application_setting(setting["key"])
            if not existing:
                self.writer.set_application_setting(
                    setting["key"], setting["value"], setting["type"], setting["description"]
                )

    # Reader methods (delegated)
    def get_job_by_id(self, job_id):
        """Get a specific job by ID"""
        return self.reader.get_job_by_id(job_id)

    def get_recent_jobs(self, limit=20, document_type=None):
        """Get recent jobs"""
        return self.reader.get_recent_jobs(limit, document_type)

    def get_jobs_by_status(self, status, limit=50):
        """Get jobs by status"""
        return self.reader.get_jobs_by_status(status, limit)

    def get_job_statistics(self):
        """Get overall job statistics"""
        return self.reader.get_job_statistics()

    def search_jobs(self, search_term, limit=20):
        """Search jobs"""
        return self.reader.search_jobs(search_term, limit)

    def get_application_setting(self, setting_key):
        """Get application setting"""
        return self.reader.get_application_setting(setting_key)

    # Writer methods (delegated)
    def create_job(self, document_type, webhook_data=None, title=None, author=None):
        """Create a new job"""
        return self.writer.create_job(document_type, webhook_data, title, author)

    def update_job_success(self, job_id, file_info):
        """Update job with success details"""
        return self.writer.update_job_success(job_id, file_info)

    def update_job_failure(self, job_id, error_code, error_message, error_details=None):
        """Update job with failure details"""
        return self.writer.update_job_failure(job_id, error_code, error_message, error_details)

    def add_job_log(self, job_id, message, log_level="INFO", details=None):
        """Add job log entry"""
        return self.writer.add_job_log(job_id, message, log_level, details)

    def execute_query(self, query: str, params: tuple = ()) -> list:
        """Execute SQL query with security validation and proper error handling"""
        try:
            # Basic SQL injection protection
            if not self._validate_query_security(query):
                raise ValueError("Query failed security validation")

            return self.client.execute_query(query, params)

        except Exception as e:
            logging.error(f"Query execution failed: {e}")
            raise

    def execute_raw_sql(self, sql: str, params: tuple = ()) -> dict:
        """Execute raw SQL with comprehensive logging and validation"""
        try:
            import time

            start_time = time.time()
            result = self.execute_query(sql, params)
            execution_time = time.time() - start_time

            return {
                "success": True,
                "result": result,
                "execution_time": execution_time,
                "rows_affected": len(result) if isinstance(result, list) else 0,
            }
        except Exception as e:
            return {"success": False, "error": str(e), "execution_time": 0, "rows_affected": 0}

    def _validate_query_security(self, query: str) -> bool:
        """Basic SQL injection validation"""
        dangerous_patterns = [
            "DROP TABLE",
            "DELETE FROM",
            "TRUNCATE",
            "ALTER TABLE",
            "--",
            "/*",
            "*/",
            "xp_",
            "sp_",
            "EXEC",
            "EXECUTE",
        ]
        query_upper = query.upper()
        return not any(pattern in query_upper for pattern in dangerous_patterns)

    def set_application_setting(self, setting_key, setting_value, setting_type="string", description=None):
        """Set application setting"""
        return self.writer.set_application_setting(setting_key, setting_value, setting_type, description)
