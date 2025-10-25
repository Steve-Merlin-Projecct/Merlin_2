#!/usr/bin/env python3
"""
Test database connection to Digital Ocean managed PostgreSQL.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import psycopg2

# Load environment variables from .env file in current directory
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path, override=True)

def test_connection():
    """Test connection to Digital Ocean database."""

    # Get credentials from environment
    db_url = os.getenv('DATABASE_URL')

    print("=" * 80)
    print("Digital Ocean Database Connection Test")
    print("=" * 80)
    print(f"\nConnection String: {db_url.replace(os.getenv('PGPASSWORD', ''), '***HIDDEN***')}")
    print("\nAttempting to connect...")

    try:
        # Connect to database
        conn = psycopg2.connect(db_url)
        cursor = conn.cursor()

        # Test query
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]

        print("\n✅ SUCCESS! Connected to Digital Ocean database")
        print(f"\nPostgreSQL Version: {version}")

        # Get database info
        cursor.execute("SELECT current_database(), current_user;")
        db_name, db_user = cursor.fetchone()

        print(f"Database Name: {db_name}")
        print(f"Connected User: {db_user}")

        # Check if our schema exists
        cursor.execute("""
            SELECT COUNT(*)
            FROM information_schema.tables
            WHERE table_schema = 'public';
        """)
        table_count = cursor.fetchone()[0]

        print(f"Number of tables in public schema: {table_count}")

        # Close connection
        cursor.close()
        conn.close()

        print("\n" + "=" * 80)
        print("Connection test completed successfully!")
        print("=" * 80)

        return True

    except Exception as e:
        print(f"\n❌ ERROR: Failed to connect to database")
        print(f"\nError details: {str(e)}")
        print("\nPlease verify:")
        print("1. Database credentials are correct")
        print("2. Database server is running and accessible")
        print("3. SSL mode is properly configured")
        print("4. Firewall allows connections from this IP")

        return False

if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1)
