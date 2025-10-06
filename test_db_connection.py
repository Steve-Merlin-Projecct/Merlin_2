#!/usr/bin/env python3
"""
Database Connection Test Script

Tests database connectivity in both Docker and local environments.
Displays connection details and verifies PostgreSQL access.
"""

import sys
import os
import logging

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def test_database_connection():
    """Test database connection and display configuration details."""

    print("=" * 60)
    print("DATABASE CONNECTION TEST")
    print("=" * 60)

    # Display environment variables
    print("\n1. Environment Variables:")
    print(f"   DATABASE_URL: {os.environ.get('DATABASE_URL', 'Not set')}")
    print(f"   DATABASE_HOST: {os.environ.get('DATABASE_HOST', 'Not set')}")
    print(f"   DATABASE_PORT: {os.environ.get('DATABASE_PORT', 'Not set')}")
    print(f"   DATABASE_NAME: {os.environ.get('DATABASE_NAME', 'Not set')}")
    print(f"   DATABASE_USER: {os.environ.get('DATABASE_USER', 'Not set')}")
    print(f"   PGPASSWORD: {'Set' if os.environ.get('PGPASSWORD') else 'Not set'}")
    print(f"   DATABASE_PASSWORD: {'Set' if os.environ.get('DATABASE_PASSWORD') else 'Not set'}")

    # Check for Docker environment
    print(f"\n2. Environment Detection:")
    print(f"   /.dockerenv exists: {os.path.exists('/.dockerenv')}")
    print(f"   Working directory: {os.getcwd()}")

    try:
        # Import database configuration
        from modules.database.database_config import get_database_config

        print("\n3. Database Configuration:")
        db_config = get_database_config()
        print(f"   Environment type: {'Docker' if db_config.is_docker else 'Local'}")
        print(f"   Connection URL: {db_config._safe_url_log()}")

        # Test connection
        print("\n4. Connection Test:")
        from modules.database.database_client import DatabaseClient

        db_client = DatabaseClient()

        if db_client.test_connection():
            print("   ✓ Database connection successful!")

            # Get database version
            print("\n5. Database Information:")
            result = db_client.execute_raw_sql("SELECT version()")
            if result:
                print(f"   PostgreSQL Version: {result[0][0][:80]}...")

            # List tables
            tables_query = """
                SELECT tablename
                FROM pg_tables
                WHERE schemaname = 'public'
                ORDER BY tablename
                LIMIT 10
            """
            tables = db_client.execute_raw_sql(tables_query)
            print(f"\n6. Database Tables (first 10):")
            if tables:
                for table in tables:
                    print(f"   - {table[0]}")
            else:
                print("   No tables found")

            print("\n" + "=" * 60)
            print("✓ ALL TESTS PASSED")
            print("=" * 60)
            return True

        else:
            print("   ✗ Database connection failed!")
            return False

    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    # Load .env file if running locally
    try:
        from dotenv import load_dotenv
        load_dotenv()
        print("Loaded .env file")
    except ImportError:
        print("python-dotenv not installed, skipping .env loading")
    except Exception as e:
        print(f"Could not load .env: {e}")

    success = test_database_connection()
    sys.exit(0 if success else 1)
