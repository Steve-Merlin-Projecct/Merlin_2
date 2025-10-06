"""
Database Migration Script
Generated on 2025-07-07 04:56:35
"""

from sqlalchemy import text
from sqlalchemy.orm import Session

def migrate_database(db: Session):
    """
    Apply database schema changes
    """
    migration_statements = []
    
    # Drop column company_logo_url from cleaned_job_scrapes
    migration_statements.append("""ALTER TABLE cleaned_job_scrapes DROP COLUMN company_logo_url;""")

    # Drop column company_rating from cleaned_job_scrapes
    migration_statements.append("""ALTER TABLE cleaned_job_scrapes DROP COLUMN company_rating;""")

    # Drop column confidence_score from cleaned_job_scrapes
    migration_statements.append("""ALTER TABLE cleaned_job_scrapes DROP COLUMN confidence_score;""")


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

