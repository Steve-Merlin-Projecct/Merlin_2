"""
Database Migration Script
Generated on 2025-07-07 05:11:14
"""

from sqlalchemy import text
from sqlalchemy.orm import Session

def migrate_database(db: Session):
    """
    Apply database schema changes
    """
    migration_statements = []
    
    # Add column location_street_address to cleaned_job_scrapes
    migration_statements.append("""ALTER TABLE cleaned_job_scrapes ADD COLUMN location_street_address text;""")

    # Drop column location_raw from cleaned_job_scrapes
    migration_statements.append("""ALTER TABLE cleaned_job_scrapes DROP COLUMN location_raw;""")

    # Drop column salary_raw from cleaned_job_scrapes
    migration_statements.append("""ALTER TABLE cleaned_job_scrapes DROP COLUMN salary_raw;""")

    # Drop column company_description from cleaned_job_scrapes
    migration_statements.append("""ALTER TABLE cleaned_job_scrapes DROP COLUMN company_description;""")

    # Drop column company_website from cleaned_job_scrapes
    migration_statements.append("""ALTER TABLE cleaned_job_scrapes DROP COLUMN company_website;""")

    # Drop column reviews_count from cleaned_job_scrapes
    migration_statements.append("""ALTER TABLE cleaned_job_scrapes DROP COLUMN reviews_count;""")

    # Drop column duplicates_count from cleaned_job_scrapes
    migration_statements.append("""ALTER TABLE cleaned_job_scrapes DROP COLUMN duplicates_count;""")

    # Add column company_description to companies
    migration_statements.append("""ALTER TABLE companies ADD COLUMN company_description text;""")

    # Add column strategic_mission to companies
    migration_statements.append("""ALTER TABLE companies ADD COLUMN strategic_mission text;""")

    # Add column strategic_values to companies
    migration_statements.append("""ALTER TABLE companies ADD COLUMN strategic_values text;""")

    # Add column recent_news to companies
    migration_statements.append("""ALTER TABLE companies ADD COLUMN recent_news text;""")

    # Drop column stock_symbol from companies
    migration_statements.append("""ALTER TABLE companies DROP COLUMN stock_symbol;""")

    # Drop column revenue_range from companies
    migration_statements.append("""ALTER TABLE companies DROP COLUMN revenue_range;""")

    # Add column first_response_received_at to job_applications
    migration_statements.append("""ALTER TABLE job_applications ADD COLUMN first_response_received_at timestamp without time zone;""")

    # Add column last_response_received_at to job_applications
    migration_statements.append("""ALTER TABLE job_applications ADD COLUMN last_response_received_at timestamp without time zone;""")

    # Drop column response_received_at from job_applications
    migration_statements.append("""ALTER TABLE job_applications DROP COLUMN response_received_at;""")


    # Execute migrations
    for statement in migration_statements:
        try:
            db.execute(text(statement))
            print(f"Executed: {statement[:50]}...")
        except Exception as e:
            print(f"Error executing migration: {e}")
            print(f"Statement: {statement}")
            raise
    
    db.commit()
    print("Migration completed successfully!")

