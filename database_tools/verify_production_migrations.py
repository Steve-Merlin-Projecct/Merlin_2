#!/usr/bin/env python3
"""
Production Migration Verification System

Verifies that database migrations are ready for production deployment.
Runs at the end of worktree development cycle to ensure production readiness.

Usage:
    python database_tools/verify_production_migrations.py
    python database_tools/verify_production_migrations.py --apply-to-production
"""

import os
import sys
import psycopg2
from psycopg2.extras import RealDictCursor
from pathlib import Path
from typing import Dict, List, Tuple
import json
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


class ProductionMigrationVerifier:
    """Verifies migration status across local and production databases"""

    def __init__(self):
        self.local_config = self._get_local_config()
        self.prod_config = self._get_prod_config()
        self.migration_dir = Path(__file__).parent / "migrations"

    def _get_local_config(self) -> Dict:
        """Get local database configuration from environment"""
        return {
            'host': os.getenv('DATABASE_HOST', 'localhost'),
            'port': int(os.getenv('DATABASE_PORT', '5432')),
            'database': os.getenv('DATABASE_NAME', 'local_Merlin_3'),
            'user': os.getenv('DATABASE_USER', 'postgres'),
            'password': os.getenv('PGPASSWORD', '')
        }

    def _get_prod_config(self) -> Dict:
        """Get production database configuration from .env file"""
        # Try multiple locations for .env
        possible_paths = [
            Path(__file__).parent.parent / '.env',
            Path('/workspace/.env'),
            Path.cwd() / '.env'
        ]

        env_file = None
        for path in possible_paths:
            if path.exists():
                env_file = path
                break

        if not env_file:
            return None

        # Parse .env file for production credentials
        prod_config = {}
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line.startswith('#') or not line or '=' not in line:
                    continue
                key, value = line.split('=', 1)
                if key in ['DATABASE_HOST', 'DATABASE_PORT', 'DATABASE_NAME',
                          'DATABASE_USER', 'PGPASSWORD']:
                    prod_config[key.lower().replace('pgpassword', 'password')] = value

        # Rename keys to match psycopg2 expectations
        if 'database_host' in prod_config:
            prod_config['host'] = prod_config.pop('database_host')
        if 'database_port' in prod_config:
            prod_config['port'] = int(prod_config.pop('database_port'))
        if 'database_name' in prod_config:
            prod_config['database'] = prod_config.pop('database_name')
        if 'database_user' in prod_config:
            prod_config['user'] = prod_config.pop('database_user')

        # Add SSL mode for production
        prod_config['sslmode'] = 'require'

        return prod_config if len(prod_config) >= 4 else None

    def _test_connection(self, config: Dict, label: str) -> Tuple[bool, str]:
        """Test database connection"""
        try:
            # Add connection timeout
            conn_config = config.copy()
            conn_config['connect_timeout'] = 5  # 5 second timeout

            conn = psycopg2.connect(**conn_config)
            cursor = cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute("SELECT current_database(), version();")
            result = cursor.fetchone()
            cursor.close()
            conn.close()
            return True, f"Connected to {result['current_database']}"
        except psycopg2.OperationalError as e:
            error_msg = str(e)
            if "Connection refused" in error_msg or "timeout" in error_msg.lower():
                return False, "Connection refused/timeout - firewall may be blocking access"
            return False, error_msg
        except Exception as e:
            return False, str(e)

    def _get_table_list(self, config: Dict) -> List[str]:
        """Get list of tables in database"""
        try:
            conn = psycopg2.connect(**config)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
                ORDER BY table_name;
            """)
            tables = [row[0] for row in cursor.fetchall()]
            cursor.close()
            conn.close()
            return tables
        except Exception as e:
            return []

    def _find_migration_files(self) -> List[Path]:
        """Find all migration SQL files"""
        if not self.migration_dir.exists():
            return []
        return sorted(self.migration_dir.glob("*.sql"))

    def _extract_table_names_from_migration(self, migration_file: Path) -> List[str]:
        """Extract table names created by migration"""
        tables = []
        with open(migration_file) as f:
            content = f.read()

            # Remove SQL comments first
            import re
            # Remove single-line comments
            content = re.sub(r'--.*$', '', content, flags=re.MULTILINE)
            # Remove multi-line comments
            content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)

            # Look for CREATE TABLE statements (case insensitive)
            matches = re.findall(
                r'CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?(\w+)',
                content,
                re.IGNORECASE
            )
            tables.extend([m.lower() for m in matches])
        return tables

    def verify_local_migrations(self) -> Dict:
        """Verify migration status on local database"""
        print("=" * 70)
        print("LOCAL DATABASE VERIFICATION")
        print("=" * 70)

        # Test connection
        connected, msg = self._test_connection(self.local_config, "local")
        print(f"Connection: {'✓' if connected else '✗'} {msg}")

        if not connected:
            return {'status': 'error', 'message': msg}

        # Get current tables
        local_tables = self._get_table_list(self.local_config)
        print(f"Tables: {len(local_tables)} found")

        # Check migration files
        migrations = self._find_migration_files()
        print(f"\nMigration files found: {len(migrations)}")

        results = {
            'status': 'success',
            'connected': True,
            'tables': local_tables,
            'migrations': []
        }

        for migration in migrations:
            tables_created = self._extract_table_names_from_migration(migration)
            applied = all(table in local_tables for table in tables_created)

            results['migrations'].append({
                'file': migration.name,
                'tables': tables_created,
                'applied': applied
            })

            status = '✓' if applied else '✗'
            print(f"  {status} {migration.name}")
            for table in tables_created:
                table_status = '✓' if table in local_tables else '✗'
                print(f"      {table_status} {table}")

        return results

    def verify_production_migrations(self) -> Dict:
        """Verify migration status on production database"""
        print("\n" + "=" * 70)
        print("PRODUCTION DATABASE VERIFICATION")
        print("=" * 70)

        if not self.prod_config:
            print("✗ Production configuration not found in .env")
            return {'status': 'error', 'message': 'No production config'}

        # Test connection
        connected, msg = self._test_connection(self.prod_config, "production")
        print(f"Connection: {'✓' if connected else '✗'} {msg}")

        if not connected:
            return {'status': 'warning', 'connected': False, 'message': msg}

        # Get current tables
        prod_tables = self._get_table_list(self.prod_config)
        print(f"Tables: {len(prod_tables)} found")

        # Check migration files
        migrations = self._find_migration_files()

        results = {
            'status': 'success',
            'connected': True,
            'tables': prod_tables,
            'migrations': []
        }

        print(f"\nProduction migration status:")
        for migration in migrations:
            tables_created = self._extract_table_names_from_migration(migration)
            applied = all(table in prod_tables for table in tables_created)

            results['migrations'].append({
                'file': migration.name,
                'tables': tables_created,
                'applied': applied
            })

            status = '✓' if applied else '✗ NEEDS DEPLOYMENT'
            print(f"  {status} {migration.name}")
            for table in tables_created:
                table_status = '✓' if table in prod_tables else '✗ MISSING'
                print(f"      {table_status} {table}")

        return results

    def generate_deployment_instructions(self, local_results: Dict, prod_results: Dict):
        """Generate deployment instructions for production"""
        print("\n" + "=" * 70)
        print("PRODUCTION DEPLOYMENT INSTRUCTIONS")
        print("=" * 70)

        if not prod_results.get('connected', False):
            print("\n⚠️  Cannot connect to production database")
            print("\nTo apply migrations to production:")
            print("1. Ensure your IP is whitelisted on Digital Ocean firewall")
            print("   - Go to Digital Ocean → Databases → Your DB → Settings → Trusted Sources")
            print("   - Add your current IP address")
            print("\n2. Or use Digital Ocean console/proxy to connect")
            print("\n3. Or run from a whitelisted machine:")

            migrations = self._find_migration_files()
            for migration in migrations:
                print(f'\n   psql "$DATABASE_URL" -f {migration}')

            return

        # Check which migrations need to be applied
        unapplied = [
            m for m in prod_results.get('migrations', [])
            if not m['applied']
        ]

        if not unapplied:
            print("\n✓ All migrations already applied to production!")
            print("✓ Production database is up to date")
            return

        print(f"\n⚠️  {len(unapplied)} migration(s) need to be applied to production:\n")

        for migration in unapplied:
            print(f"  • {migration['file']}")
            print(f"    Creates: {', '.join(migration['tables'])}")

        print("\n" + "-" * 70)
        print("To apply these migrations, run:")
        print("-" * 70)

        db_url = self._format_db_url(self.prod_config)
        for migration in unapplied:
            print(f'\npsql "{db_url}" -f database_tools/migrations/{migration["file"]}')

        print("\n" + "-" * 70)
        print("Or use the automated deployment command:")
        print("-" * 70)
        print("\npython database_tools/verify_production_migrations.py --apply-to-production")

    def _format_db_url(self, config: Dict) -> str:
        """Format database configuration as connection URL"""
        return (
            f"postgresql://{config['user']}:{config['password']}@"
            f"{config['host']}:{config['port']}/{config['database']}"
            f"?sslmode={config.get('sslmode', 'prefer')}"
        )

    def apply_migrations_to_production(self):
        """Apply missing migrations to production database"""
        print("=" * 70)
        print("APPLYING MIGRATIONS TO PRODUCTION")
        print("=" * 70)

        if not self.prod_config:
            print("✗ Production configuration not found")
            return False

        # Get production status
        prod_results = self.verify_production_migrations()

        if not prod_results.get('connected', False):
            print("\n✗ Cannot connect to production database")
            return False

        # Find unapplied migrations
        unapplied = [
            m for m in prod_results.get('migrations', [])
            if not m['applied']
        ]

        if not unapplied:
            print("\n✓ No migrations to apply - production is up to date")
            return True

        print(f"\nFound {len(unapplied)} migration(s) to apply")

        # Apply each migration
        try:
            conn = psycopg2.connect(**self.prod_config)
            conn.autocommit = True
            cursor = conn.cursor()

            for migration_info in unapplied:
                migration_file = self.migration_dir / migration_info['file']

                print(f"\nApplying {migration_info['file']}...")

                with open(migration_file) as f:
                    sql = f.read()

                cursor.execute(sql)

                print(f"  ✓ {migration_info['file']} applied successfully")
                for table in migration_info['tables']:
                    print(f"    ✓ Created table: {table}")

            cursor.close()
            conn.close()

            print("\n" + "=" * 70)
            print("✓ ALL MIGRATIONS APPLIED SUCCESSFULLY")
            print("=" * 70)

            return True

        except Exception as e:
            print(f"\n✗ Error applying migrations: {e}")
            import traceback
            traceback.print_exc()
            return False

    def run_full_verification(self):
        """Run complete verification process"""
        print("\n" + "=" * 70)
        print("DATABASE MIGRATION VERIFICATION SYSTEM")
        print("Worktree: create-securitydetections-table-in-production-data")
        print(f"Timestamp: {datetime.now().isoformat()}")
        print("=" * 70)

        # Verify local
        local_results = self.verify_local_migrations()

        # Verify production
        prod_results = self.verify_production_migrations()

        # Generate instructions
        self.generate_deployment_instructions(local_results, prod_results)

        # Summary
        print("\n" + "=" * 70)
        print("VERIFICATION SUMMARY")
        print("=" * 70)

        local_ok = local_results.get('status') == 'success'
        prod_connected = prod_results.get('connected', False)

        print(f"Local migrations:  {'✓' if local_ok else '✗'}")
        print(f"Production access: {'✓' if prod_connected else '⚠️'}")

        if local_ok and prod_connected:
            unapplied = len([m for m in prod_results.get('migrations', []) if not m['applied']])
            if unapplied == 0:
                print("\n✓ READY TO MERGE - Production is up to date")
            else:
                print(f"\n⚠️  DEPLOY REQUIRED - {unapplied} migration(s) need production deployment")
        elif local_ok and not prod_connected:
            print("\n⚠️  LOCAL OK - Production deployment pending (firewall/access issue)")
        else:
            print("\n✗ ISSUES DETECTED - Review errors above")

        print("=" * 70)


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Verify database migrations for production deployment"
    )
    parser.add_argument(
        '--apply-to-production',
        action='store_true',
        help='Apply missing migrations to production database'
    )

    args = parser.parse_args()

    verifier = ProductionMigrationVerifier()

    if args.apply_to_production:
        success = verifier.apply_migrations_to_production()
        sys.exit(0 if success else 1)
    else:
        verifier.run_full_verification()


if __name__ == "__main__":
    main()
