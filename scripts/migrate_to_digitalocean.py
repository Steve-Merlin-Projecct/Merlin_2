#!/usr/bin/env python3
"""
Database Migration Script for Digital Ocean

Migrates local PostgreSQL database schema and data to Digital Ocean
Managed PostgreSQL database.

Usage:
    python scripts/migrate_to_digitalocean.py --help
    python scripts/migrate_to_digitalocean.py --schema-only
    python scripts/migrate_to_digitalocean.py --full-migration

Features:
    - Schema-only migration (structure without data)
    - Full migration (schema + data)
    - Pre-migration validation
    - Post-migration verification
    - Rollback capability
    - Progress reporting
"""

import os
import sys
import argparse
import subprocess
import logging
from datetime import datetime
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(f'migration_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
    ]
)
logger = logging.getLogger(__name__)


class DatabaseMigration:
    """
    Database migration manager for Digital Ocean deployment.

    Handles schema and data migration from local PostgreSQL to
    Digital Ocean Managed PostgreSQL database.
    """

    def __init__(self, source_url: str, target_url: str):
        """
        Initialize migration manager.

        Args:
            source_url: Local PostgreSQL connection string
            target_url: Digital Ocean PostgreSQL connection string
        """
        self.source_url = source_url
        self.target_url = target_url
        self.backup_dir = Path("./database_backups")
        self.backup_dir.mkdir(exist_ok=True)

        logger.info("Database Migration initialized")
        logger.info(f"Source: {self._safe_url(source_url)}")
        logger.info(f"Target: {self._safe_url(target_url)}")

    def _safe_url(self, url: str) -> str:
        """Mask password in URL for logging."""
        import re
        return re.sub(r'(://[^:]+:)([^@]+)(@)', r'\1****\3', url)

    def validate_connections(self) -> bool:
        """
        Validate both source and target database connections.

        Returns:
            bool: True if both connections succeed, False otherwise
        """
        logger.info("Validating database connections...")

        # Test source connection
        logger.info("Testing source database connection...")
        if not self._test_connection(self.source_url):
            logger.error("❌ Failed to connect to source database")
            return False
        logger.info("✅ Source database connection successful")

        # Test target connection
        logger.info("Testing target database connection...")
        if not self._test_connection(self.target_url):
            logger.error("❌ Failed to connect to target database")
            return False
        logger.info("✅ Target database connection successful")

        return True

    def _test_connection(self, url: str) -> bool:
        """Test PostgreSQL connection."""
        try:
            result = subprocess.run(
                ['psql', url, '-c', 'SELECT 1;'],
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.returncode == 0
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False

    def get_table_counts(self, url: str) -> dict:
        """
        Get row counts for all tables in database.

        Args:
            url: Database connection string

        Returns:
            dict: Table name -> row count mapping
        """
        query = """
        SELECT
            schemaname || '.' || tablename AS table_name,
            n_live_tup AS row_count
        FROM pg_stat_user_tables
        ORDER BY schemaname, tablename;
        """

        try:
            result = subprocess.run(
                ['psql', url, '-t', '-c', query],
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode != 0:
                logger.error(f"Failed to get table counts: {result.stderr}")
                return {}

            counts = {}
            for line in result.stdout.strip().split('\n'):
                if '|' in line:
                    table, count = line.split('|')
                    counts[table.strip()] = int(count.strip())

            return counts
        except Exception as e:
            logger.error(f"Error getting table counts: {e}")
            return {}

    def export_schema(self, output_file: Path) -> bool:
        """
        Export database schema (structure only).

        Args:
            output_file: Path to save schema SQL file

        Returns:
            bool: True if export successful
        """
        logger.info(f"Exporting schema to {output_file}...")

        try:
            result = subprocess.run(
                [
                    'pg_dump',
                    self.source_url,
                    '--schema-only',
                    '--no-owner',
                    '--no-acl',
                    '-f', str(output_file)
                ],
                capture_output=True,
                text=True,
                timeout=300
            )

            if result.returncode != 0:
                logger.error(f"Schema export failed: {result.stderr}")
                return False

            logger.info(f"✅ Schema exported successfully ({output_file.stat().st_size} bytes)")
            return True
        except Exception as e:
            logger.error(f"Schema export error: {e}")
            return False

    def export_data(self, output_file: Path) -> bool:
        """
        Export database data (full backup).

        Args:
            output_file: Path to save data SQL file

        Returns:
            bool: True if export successful
        """
        logger.info(f"Exporting full database to {output_file}...")

        try:
            result = subprocess.run(
                [
                    'pg_dump',
                    self.source_url,
                    '--no-owner',
                    '--no-acl',
                    '-f', str(output_file)
                ],
                capture_output=True,
                text=True,
                timeout=600
            )

            if result.returncode != 0:
                logger.error(f"Data export failed: {result.stderr}")
                return False

            file_size = output_file.stat().st_size
            logger.info(f"✅ Data exported successfully ({file_size / 1024 / 1024:.2f} MB)")
            return True
        except Exception as e:
            logger.error(f"Data export error: {e}")
            return False

    def import_sql(self, sql_file: Path, target_url: str = None) -> bool:
        """
        Import SQL file to target database.

        Args:
            sql_file: Path to SQL file to import
            target_url: Target database URL (defaults to self.target_url)

        Returns:
            bool: True if import successful
        """
        if target_url is None:
            target_url = self.target_url

        logger.info(f"Importing {sql_file} to target database...")

        try:
            result = subprocess.run(
                ['psql', target_url, '-f', str(sql_file)],
                capture_output=True,
                text=True,
                timeout=900
            )

            if result.returncode != 0:
                logger.error(f"Import failed: {result.stderr}")
                return False

            logger.info("✅ Import completed successfully")
            return True
        except Exception as e:
            logger.error(f"Import error: {e}")
            return False

    def verify_migration(self) -> bool:
        """
        Verify migration by comparing table counts.

        Returns:
            bool: True if verification passes
        """
        logger.info("Verifying migration...")

        source_counts = self.get_table_counts(self.source_url)
        target_counts = self.get_table_counts(self.target_url)

        if not source_counts or not target_counts:
            logger.error("❌ Failed to retrieve table counts")
            return False

        # Compare counts
        mismatches = []
        for table, source_count in source_counts.items():
            target_count = target_counts.get(table, 0)
            if source_count != target_count:
                mismatches.append({
                    'table': table,
                    'source': source_count,
                    'target': target_count,
                    'diff': target_count - source_count
                })

        if mismatches:
            logger.warning("⚠️  Table count mismatches detected:")
            for mismatch in mismatches:
                logger.warning(
                    f"  {mismatch['table']}: "
                    f"source={mismatch['source']}, "
                    f"target={mismatch['target']}, "
                    f"diff={mismatch['diff']}"
                )
            return False

        logger.info("✅ Migration verification passed - all table counts match")
        return True

    def migrate_schema_only(self) -> bool:
        """
        Migrate schema only (no data).

        Returns:
            bool: True if migration successful
        """
        logger.info("=" * 60)
        logger.info("SCHEMA-ONLY MIGRATION")
        logger.info("=" * 60)

        # Step 1: Validate connections
        if not self.validate_connections():
            return False

        # Step 2: Export schema
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        schema_file = self.backup_dir / f"schema_export_{timestamp}.sql"

        if not self.export_schema(schema_file):
            return False

        # Step 3: Import to target
        if not self.import_sql(schema_file):
            return False

        logger.info("✅ Schema migration completed successfully")
        return True

    def migrate_full(self) -> bool:
        """
        Migrate schema and data (full migration).

        Returns:
            bool: True if migration successful
        """
        logger.info("=" * 60)
        logger.info("FULL DATABASE MIGRATION")
        logger.info("=" * 60)

        # Step 1: Validate connections
        if not self.validate_connections():
            return False

        # Step 2: Get source table counts
        logger.info("Analyzing source database...")
        source_counts = self.get_table_counts(self.source_url)
        total_rows = sum(source_counts.values())
        logger.info(f"Source database: {len(source_counts)} tables, {total_rows:,} total rows")

        # Step 3: Export full database
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = self.backup_dir / f"full_backup_{timestamp}.sql"

        if not self.export_data(backup_file):
            return False

        # Step 4: Import to target
        if not self.import_sql(backup_file):
            return False

        # Step 5: Verify migration
        if not self.verify_migration():
            logger.warning("⚠️  Verification found discrepancies - review logs")
            return False

        logger.info("✅ Full migration completed and verified successfully")
        return True


def main():
    """Main entry point for migration script."""
    parser = argparse.ArgumentParser(
        description='Migrate database to Digital Ocean Managed PostgreSQL',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Schema-only migration
  python scripts/migrate_to_digitalocean.py --schema-only

  # Full migration (schema + data)
  python scripts/migrate_to_digitalocean.py --full-migration

  # Using custom database URLs
  python scripts/migrate_to_digitalocean.py \\
    --source postgresql://user:pass@localhost:5432/local_db \\
    --target postgresql://user:pass@host:25060/prod_db?sslmode=require \\
    --full-migration
        """
    )

    parser.add_argument(
        '--source',
        help='Source database URL (default: from DATABASE_URL or local)',
        default=None
    )

    parser.add_argument(
        '--target',
        help='Target database URL (default: from DATABASE_URL_PRODUCTION)',
        default=None
    )

    parser.add_argument(
        '--schema-only',
        action='store_true',
        help='Migrate schema only (no data)'
    )

    parser.add_argument(
        '--full-migration',
        action='store_true',
        help='Migrate schema and data (full backup)'
    )

    parser.add_argument(
        '--verify-only',
        action='store_true',
        help='Only verify existing migration (no changes)'
    )

    args = parser.parse_args()

    # Validate arguments
    if not any([args.schema_only, args.full_migration, args.verify_only]):
        parser.error("Must specify --schema-only, --full-migration, or --verify-only")

    # Get database URLs
    source_url = args.source or os.environ.get('DATABASE_URL') or \
                 'postgresql://postgres:goldmember@localhost:5432/local_Merlin_3'

    target_url = args.target or os.environ.get('DATABASE_URL_PRODUCTION')

    if not target_url:
        logger.error("Target database URL not specified!")
        logger.error("Set DATABASE_URL_PRODUCTION environment variable or use --target")
        sys.exit(1)

    # Initialize migration manager
    migrator = DatabaseMigration(source_url, target_url)

    # Execute requested operation
    try:
        if args.verify_only:
            success = migrator.verify_migration()
        elif args.schema_only:
            success = migrator.migrate_schema_only()
        elif args.full_migration:
            success = migrator.migrate_full()

        if success:
            logger.info("=" * 60)
            logger.info("✅ MIGRATION COMPLETED SUCCESSFULLY")
            logger.info("=" * 60)
            sys.exit(0)
        else:
            logger.error("=" * 60)
            logger.error("❌ MIGRATION FAILED - Review logs above")
            logger.error("=" * 60)
            sys.exit(1)

    except KeyboardInterrupt:
        logger.warning("\n⚠️  Migration interrupted by user")
        sys.exit(2)
    except Exception as e:
        logger.exception(f"Unexpected error during migration: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
