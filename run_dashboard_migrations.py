#!/usr/bin/env python3
"""
Run Dashboard V2 Database Migrations
Applies indexes, materialized views, and aggregation tables
"""

import os
import sys
from modules.database.database_client import DatabaseClient
from sqlalchemy import text

def parse_sql_statements(sql_content):
    """
    Parse SQL content into individual statements
    Handles multi-line statements and nested structures
    """
    statements = []
    current_statement = []
    in_dollar_quote = False
    dollar_quote_tag = None

    lines = sql_content.split('\n')

    for line in lines:
        stripped = line.strip()

        # Skip pure comment lines when not building a statement
        if stripped.startswith('--') and not current_statement:
            continue

        # Check for dollar-quoted strings (e.g., $$ or $body$)
        for tag in ['$$', '$body$', '$function$']:
            if tag in line:
                if not in_dollar_quote:
                    in_dollar_quote = True
                    dollar_quote_tag = tag
                elif dollar_quote_tag == tag:
                    # Closing the same tag
                    in_dollar_quote = False
                    dollar_quote_tag = None
                break

        current_statement.append(line)

        # Check for statement terminator (semicolon) outside of dollar quotes
        if ';' in line and not in_dollar_quote:
            statement_text = '\n'.join(current_statement).strip()
            # Remove pure comment blocks at the start
            while statement_text.startswith('--'):
                lines_in_statement = statement_text.split('\n')
                if len(lines_in_statement) > 1:
                    statement_text = '\n'.join(lines_in_statement[1:]).strip()
                else:
                    break

            if statement_text and not statement_text.startswith('--'):
                statements.append(statement_text)
            current_statement = []

    return statements


def run_migration(db_client, migration_file, migration_name):
    """Run a single migration file"""
    print(f"\n{'='*60}")
    print(f"Running: {migration_name}")
    print(f"{'='*60}\n")

    try:
        with open(migration_file, 'r') as f:
            sql = f.read()

        # Parse SQL statements properly
        statements = parse_sql_statements(sql)

        for i, statement in enumerate(statements, 1):
            # Skip empty statements
            if not statement.strip():
                continue

            # Check if this is a CONCURRENT operation
            is_concurrent = 'CONCURRENTLY' in statement.upper()

            # Get a preview of the statement type
            statement_preview = statement[:60].replace('\n', ' ') + '...'

            if is_concurrent:
                # CONCURRENT operations need autocommit (no transaction)
                print(f"[{i}/{len(statements)}] CONCURRENT: {statement_preview}")
                connection = db_client.engine.connect()
                connection.execution_options(isolation_level="AUTOCOMMIT")
                connection.execute(text(statement))
                connection.close()
            else:
                # Regular statement in transaction
                print(f"[{i}/{len(statements)}] {statement_preview}")
                with db_client.get_session() as session:
                    session.execute(text(statement))
                    session.commit()

        print(f"\n✅ {migration_name} completed successfully\n")
        return True

    except Exception as e:
        print(f"\n❌ Error in {migration_name}: {e}\n")
        print(f"Failed statement preview: {statement[:200] if 'statement' in locals() else 'N/A'}")
        return False


def check_migration_status(db_session):
    """Check current migration status"""
    print("\n" + "="*60)
    print("Checking Current Database State")
    print("="*60 + "\n")

    # Check indexes
    result = db_session.execute(text("""
        SELECT COUNT(*)
        FROM pg_indexes
        WHERE indexname IN (
            'idx_jobs_created_at',
            'idx_jobs_eligibility_priority',
            'idx_applications_created_status',
            'idx_jobs_company_status',
            'idx_analyzed_jobs_eligibility',
            'idx_applications_job_created'
        )
    """)).scalar()
    print(f"Dashboard indexes: {result}/6")

    # Check materialized views
    result = db_session.execute(text("""
        SELECT COUNT(*)
        FROM pg_matviews
        WHERE matviewname = 'application_summary_mv'
    """)).scalar()
    print(f"Materialized views: {result}/1")

    # Check aggregation tables
    result = db_session.execute(text("""
        SELECT COUNT(*)
        FROM information_schema.tables
        WHERE table_name IN ('dashboard_metrics_hourly', 'dashboard_metrics_daily')
    """)).scalar()
    print(f"Aggregation tables: {result}/2")

    # Check if aggregation functions exist
    result = db_session.execute(text("""
        SELECT COUNT(*)
        FROM pg_proc
        WHERE proname IN ('compute_hourly_metrics', 'compute_daily_metrics')
    """)).scalar()
    print(f"Aggregation functions: {result}/2")

    print()


def main():
    """Main migration runner"""
    print("\n" + "="*60)
    print("Dashboard V2 Migration Runner")
    print("="*60)

    db_client = DatabaseClient()

    with db_client.get_session() as session:
        # Check current status
        check_migration_status(session)

        # Run migrations
        migrations = [
            ('database_migrations/001_dashboard_optimization_indexes.sql',
             'Migration 001: Dashboard Optimization Indexes'),
            ('database_migrations/002_dashboard_materialized_views.sql',
             'Migration 002: Materialized Views'),
            ('database_migrations/003_dashboard_aggregation_tables.sql',
             'Migration 003: Aggregation Tables & Functions'),
        ]

        success_count = 0
        for migration_file, migration_name in migrations:
            if os.path.exists(migration_file):
                if run_migration(db_client, migration_file, migration_name):
                    success_count += 1
            else:
                print(f"❌ Migration file not found: {migration_file}")

        print("\n" + "="*60)
        print(f"Migration Summary: {success_count}/{len(migrations)} completed")
        print("="*60)

        # Check final status
        check_migration_status(session)

        # Backfill aggregation data if migrations succeeded
        if success_count == len(migrations):
            print("\n" + "="*60)
            print("Backfilling Aggregation Data")
            print("="*60 + "\n")

            try:
                # Backfill daily metrics (last 30 days)
                print("Backfilling daily metrics (last 30 days)...")
                session.execute(text("SELECT backfill_daily_metrics(30)"))
                session.commit()
                print("✅ Daily metrics backfilled\n")

                # Backfill hourly metrics (last 7 days)
                print("Backfilling hourly metrics (last 7 days)...")
                session.execute(text("SELECT backfill_hourly_metrics(168)"))  # 7 days * 24 hours
                session.commit()
                print("✅ Hourly metrics backfilled\n")

                # Refresh materialized view
                print("Refreshing materialized view...")
                session.execute(text("REFRESH MATERIALIZED VIEW CONCURRENTLY application_summary_mv"))
                session.commit()
                print("✅ Materialized view refreshed\n")

            except Exception as e:
                print(f"❌ Error backfilling data: {e}\n")
                session.rollback()

        print("\n" + "="*60)
        print("✅ All migrations complete! Dashboard V2 ready to use.")
        print("="*60 + "\n")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Migration interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
