#!/usr/bin/env python3
"""
Database Schema Auditor
Extracts complete schema information for jobs, job_applications, and companies tables.
"""

import os
import sys
from sqlalchemy import create_engine, inspect, MetaData
from sqlalchemy.engine import reflection

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def get_database_url():
    """Get database URL from environment."""
    password = os.environ.get('PGPASSWORD', 'goldmember')
    database = os.environ.get('DATABASE_NAME', 'local_Merlin_3')
    host = os.environ.get('DATABASE_HOST', 'localhost')
    port = os.environ.get('DATABASE_PORT', '5432')
    user = os.environ.get('DATABASE_USER', 'postgres')

    return f"postgresql://{user}:{password}@{host}:{port}/{database}"

def audit_table_schema(inspector, table_name):
    """Extract complete schema information for a table."""
    print(f"\n{'='*80}")
    print(f"TABLE: {table_name}")
    print(f"{'='*80}\n")

    # Check if table exists
    if table_name not in inspector.get_table_names():
        print(f"⚠️  Table '{table_name}' does not exist in database")
        return None

    # Get columns
    columns = inspector.get_columns(table_name)
    print(f"COLUMNS ({len(columns)} total):")
    print(f"{'-'*80}")
    for col in columns:
        col_name = col['name']
        col_type = str(col['type'])
        nullable = "NULL" if col['nullable'] else "NOT NULL"
        default = f"DEFAULT {col['default']}" if col.get('default') else ""

        print(f"  {col_name:30s} {col_type:25s} {nullable:10s} {default}")

    # Get primary keys
    pk = inspector.get_pk_constraint(table_name)
    if pk and pk.get('constrained_columns'):
        print(f"\nPRIMARY KEY:")
        print(f"  {', '.join(pk['constrained_columns'])}")

    # Get foreign keys
    fks = inspector.get_foreign_keys(table_name)
    if fks:
        print(f"\nFOREIGN KEYS ({len(fks)} total):")
        for fk in fks:
            print(f"  {fk['constrained_columns']} -> {fk['referred_table']}.{fk['referred_columns']}")

    # Get indexes
    indexes = inspector.get_indexes(table_name)
    if indexes:
        print(f"\nINDEXES ({len(indexes)} total):")
        for idx in indexes:
            unique = "UNIQUE" if idx.get('unique') else ""
            # Handle None values in column names
            col_names = [str(col) if col is not None else 'NULL' for col in idx['column_names']]
            print(f"  {idx['name']:40s} {unique:10s} ({', '.join(col_names)})")

    # Get unique constraints
    unique_constraints = inspector.get_unique_constraints(table_name)
    if unique_constraints:
        print(f"\nUNIQUE CONSTRAINTS ({len(unique_constraints)} total):")
        for uc in unique_constraints:
            print(f"  {uc['name']:40s} ({', '.join(uc['column_names'])})")

    # Get check constraints
    try:
        check_constraints = inspector.get_check_constraints(table_name)
        if check_constraints:
            print(f"\nCHECK CONSTRAINTS ({len(check_constraints)} total):")
            for cc in check_constraints:
                print(f"  {cc['name']:40s} {cc.get('sqltext', '')}")
    except NotImplementedError:
        pass  # Not all databases support this

    return columns

def check_column_exists(columns, column_name):
    """Check if a column exists in the column list."""
    if not columns:
        return False
    return any(col['name'] == column_name for col in columns)

def main():
    """Main execution function."""
    print("="*80)
    print("DATABASE SCHEMA AUDIT")
    print("Dashboard V2 Completion - Schema Verification")
    print("="*80)

    # Connect to database
    database_url = get_database_url()
    print(f"\nConnecting to: {database_url.replace(os.environ.get('PGPASSWORD', 'goldmember'), '***')}")

    try:
        engine = create_engine(database_url)
        inspector = inspect(engine)

        print(f"\n✅ Connected successfully!")
        print(f"Database: {inspector.engine.url.database}")

        # Audit key tables
        tables_to_audit = ['jobs', 'job_applications', 'companies']
        table_schemas = {}

        for table_name in tables_to_audit:
            columns = audit_table_schema(inspector, table_name)
            table_schemas[table_name] = columns

        # Check for columns referenced in migration files
        print(f"\n{'='*80}")
        print("SCHEMA COMPATIBILITY CHECK")
        print("Checking for columns referenced in migration files")
        print(f"{'='*80}\n")

        # Columns that migrations assume exist
        assumed_columns = {
            'jobs': ['priority_score', 'salary_currency', 'location', 'experience_level'],
            'job_applications': [],
            'companies': []
        }

        for table_name, columns_to_check in assumed_columns.items():
            if not columns_to_check:
                continue

            print(f"\nTable: {table_name}")
            print(f"{'-'*80}")

            actual_columns = table_schemas.get(table_name)
            if not actual_columns:
                print(f"  ⚠️  Table not found in database")
                continue

            for col_name in columns_to_check:
                exists = check_column_exists(actual_columns, col_name)
                status = "✅ EXISTS" if exists else "❌ MISSING"
                print(f"  {col_name:30s} {status}")

        # Suggest alternative columns
        print(f"\n{'='*80}")
        print("SUGGESTED COLUMN ALTERNATIVES")
        print(f"{'='*80}\n")

        jobs_columns = table_schemas.get('jobs')
        if jobs_columns:
            print("For 'location' (missing), consider:")
            location_alternatives = ['city', 'state', 'country', 'remote_type', 'work_location', 'job_location']
            for alt in location_alternatives:
                if check_column_exists(jobs_columns, alt):
                    print(f"  ✅ {alt}")

            print("\nFor 'salary_currency' (missing), consider:")
            salary_alternatives = ['salary', 'salary_min', 'salary_max', 'compensation', 'pay_rate']
            for alt in salary_alternatives:
                if check_column_exists(jobs_columns, alt):
                    print(f"  ✅ {alt}")

            print("\nFor 'priority_score' (missing), consider:")
            score_alternatives = ['match_score', 'ranking', 'relevance_score', 'score', 'priority']
            for alt in score_alternatives:
                if check_column_exists(jobs_columns, alt):
                    print(f"  ✅ {alt}")

            print("\nFor 'experience_level' (missing), consider:")
            exp_alternatives = ['experience', 'seniority', 'level', 'years_experience', 'job_level']
            for alt in exp_alternatives:
                if check_column_exists(jobs_columns, alt):
                    print(f"  ✅ {alt}")

        print(f"\n{'='*80}")
        print("AUDIT COMPLETE")
        print(f"{'='*80}\n")

        engine.dispose()

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0

if __name__ == "__main__":
    sys.exit(main())
