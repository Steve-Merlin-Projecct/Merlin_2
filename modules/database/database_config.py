"""
Database Configuration Module

Provides environment-aware database connection configuration that automatically
detects whether the application is running in a Docker container or locally,
and constructs the appropriate PostgreSQL connection string.

Environment Detection:
    - Docker: Uses DATABASE_HOST (host.docker.internal or localhost) from container env
    - Local: Falls back to localhost connection

Connection Priority:
    1. Use DATABASE_URL if explicitly set (highest priority)
    2. Build from individual components (DATABASE_HOST, DATABASE_PORT, etc.)
    3. Fall back to localhost defaults
"""

import os
import logging


class DatabaseConfig:
    """
    Database configuration manager with environment detection.

    Automatically detects Docker vs local environment and provides
    the appropriate PostgreSQL connection string.

    Attributes:
        is_docker (bool): True if running in Docker container
        database_url (str): Constructed PostgreSQL connection URL
    """

    def __init__(self):
        """Initialize database configuration with environment detection."""
        self.is_docker = self._detect_docker_environment()
        self.database_url = self._build_connection_string()

        logging.info(f"Database config initialized - Environment: {'Docker' if self.is_docker else 'Local'}")
        logging.info(f"Database URL: {self._safe_url_log()}")

    def _detect_docker_environment(self) -> bool:
        """
        Detect if running in Docker container.

        Checks multiple indicators in priority order:
        - DATABASE_HOST environment variable set to Docker-specific values
        - Both DATABASE_HOST and DATABASE_USER set (from devcontainer.json)
        - Presence of /.dockerenv file (final fallback)

        Returns:
            bool: True if running in Docker, False otherwise
        """
        # Priority 1: Check for Docker-specific environment variables
        db_host = os.environ.get('DATABASE_HOST', '')
        if db_host in ['host.docker.internal', 'docker.internal']:
            return True

        # Priority 2: Check if containerEnv variables are set (from devcontainer.json)
        # Both must be present to indicate Docker environment
        if os.environ.get('DATABASE_HOST') and os.environ.get('DATABASE_USER'):
            return True

        # Priority 3: Check for Docker-specific files (final fallback)
        # This is less reliable as it doesn't guarantee env vars are set
        if os.path.exists('/.dockerenv'):
            # Only return True if we have some database config
            if os.environ.get('DATABASE_HOST') or os.environ.get('DATABASE_PASSWORD'):
                return True

        return False

    def _build_connection_string(self) -> str:
        """
        Build PostgreSQL connection string based on environment.

        Priority order:
        1. DATABASE_URL (if explicitly set)
        2. Individual components (DATABASE_HOST, DATABASE_PORT, etc.)
        3. Local fallback defaults

        Returns:
            str: PostgreSQL connection URL

        Raises:
            ValueError: If required credentials are missing
        """
        # Priority 1: Use DATABASE_URL if explicitly set
        if os.environ.get('DATABASE_URL'):
            logging.info("Using DATABASE_URL from environment")
            return os.environ.get('DATABASE_URL')

        # Priority 2: Build from individual components
        if self.is_docker:
            # Docker environment - use container environment variables
            host = os.environ.get('DATABASE_HOST', 'localhost')
            port = os.environ.get('DATABASE_PORT', '5432')
            database = os.environ.get('DATABASE_NAME', 'local_Merlin_3')
            user = os.environ.get('DATABASE_USER', 'postgres')
            password = os.environ.get('DATABASE_PASSWORD') or os.environ.get('PGPASSWORD')

            logging.info(f"Building Docker connection string: {host}:{port}/{database}")
        else:
            # Local environment - fall back to .env or local defaults
            host = 'localhost'
            port = '5432'
            database = os.environ.get('DATABASE_NAME', 'local_Merlin_3')
            user = 'postgres'
            password = os.environ.get('PGPASSWORD')

            logging.info(f"Building local connection string: {host}:{port}/{database}")

        # Validate required credentials
        if not password:
            raise ValueError(
                "Database password not found. Set PGPASSWORD or DATABASE_PASSWORD "
                "in environment variables or .env file"
            )

        # Construct PostgreSQL URL
        return f"postgresql://{user}:{password}@{host}:{port}/{database}"

    def _safe_url_log(self) -> str:
        """
        Create safe version of database URL for logging (password masked).

        Returns:
            str: Database URL with password replaced by asterisks
        """
        if not self.database_url:
            return "Not configured"

        # Mask password in URL for logging
        import re
        safe_url = re.sub(
            r'(://[^:]+:)([^@]+)(@)',
            r'\1****\3',
            self.database_url
        )
        return safe_url

    def get_connection_url(self) -> str:
        """
        Get the database connection URL.

        Returns:
            str: PostgreSQL connection URL
        """
        return self.database_url

    def get_connection_params(self) -> dict:
        """
        Get individual connection parameters as dictionary.

        Useful for applications that need separate host, port, etc.

        Returns:
            dict: Connection parameters (host, port, database, user, password)
        """
        import re

        # Parse URL: postgresql://user:password@host:port/database
        pattern = r'postgresql://([^:]+):([^@]+)@([^:]+):(\d+)/(.+)'
        match = re.match(pattern, self.database_url)

        if not match:
            raise ValueError("Invalid database URL format")

        user, password, host, port, database = match.groups()

        return {
            'user': user,
            'password': password,
            'host': host,
            'port': int(port),
            'database': database
        }


# Singleton instance
_config_instance = None

def get_database_config() -> DatabaseConfig:
    """
    Get singleton instance of database configuration.

    Returns:
        DatabaseConfig: Singleton configuration instance
    """
    global _config_instance
    if _config_instance is None:
        _config_instance = DatabaseConfig()
    return _config_instance
