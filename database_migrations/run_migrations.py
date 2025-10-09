#!/usr/bin/env python3
"""
Database Migration Runner for Analytics System
Runs SQL migrations in order with error handling and logging
"""

import os
import sys
import logging
import psycopg2
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def get_db_connection():
    """Get database connection using environment variables"""
    try:
        conn = psycopg2.connect(
            host=os.environ.get('PGHOST', 'localhost'),
            database=os.environ.get('PGDATABASE', 'local_Merlin_3'),
            user=os.environ.get('PGUSER', 'postgres'),
            password=os.environ.get('PGPASSWORD'),
            port=os.environ.get('PGPORT', '5432')
        )
        return conn
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        sys.exit(1)

def run_migration_file(conn, filepath):
    """Run a single SQL migration file"""
    logger.info(f"Running migration: {filepath.name}")

    try:
        with open(filepath, 'r') as f:
            sql = f.read()

        cursor = conn.cursor()
        cursor.execute(sql)
        conn.commit()
        cursor.close()

        logger.info(f"✓ Migration {filepath.name} completed successfully")
        return True

    except Exception as e:
        logger.error(f"✗ Migration {filepath.name} failed: {e}")
        conn.rollback()
        return False

def main():
    """Run all migrations in order"""
    migrations_dir = Path(__file__).parent

    # Migration files in order
    migrations = [
        '001_add_engagement_metrics.sql',
        '002_create_analytics_views.sql',
        '003_backfill_engagement_data.sql'
    ]

    logger.info("="*60)
    logger.info("Starting Analytics Database Migrations")
    logger.info("="*60)

    conn = get_db_connection()
    logger.info(f"Connected to database: {os.environ.get('PGDATABASE')}")

    success_count = 0
    fail_count = 0

    for migration_file in migrations:
        filepath = migrations_dir / migration_file

        if not filepath.exists():
            logger.warning(f"Migration file not found: {migration_file}")
            continue

        if run_migration_file(conn, filepath):
            success_count += 1
        else:
            fail_count += 1
            logger.error(f"Stopping migrations due to failure in {migration_file}")
            break

    conn.close()

    logger.info("="*60)
    logger.info(f"Migration Summary: {success_count} succeeded, {fail_count} failed")
    logger.info("="*60)

    return 0 if fail_count == 0 else 1

if __name__ == '__main__':
    sys.exit(main())
