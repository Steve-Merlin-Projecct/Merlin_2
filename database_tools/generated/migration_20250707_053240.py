"""
Database Migration Script
Generated on 2025-07-07 05:32:40
"""

from sqlalchemy import text
from sqlalchemy.orm import Session

def migrate_database(db: Session):
    """
    Apply database schema changes
    """
    migration_statements = []
    
    # Drop column intended_document from sentence_bank_cover_letter
    migration_statements.append("""ALTER TABLE sentence_bank_cover_letter DROP COLUMN intended_document;""")

    # Drop column intended_document from sentence_bank_resume
    migration_statements.append("""ALTER TABLE sentence_bank_resume DROP COLUMN intended_document;""")

    # Add column acceptable_stress to user_job_preferences
    migration_statements.append("""ALTER TABLE user_job_preferences ADD COLUMN acceptable_stress integer;""")

    # Add column street_address to user_job_preferences
    migration_statements.append("""ALTER TABLE user_job_preferences ADD COLUMN street_address text;""")

    # Drop column salary_maximum from user_job_preferences
    migration_statements.append("""ALTER TABLE user_job_preferences DROP COLUMN salary_maximum;""")

    # Drop column hourly_rate_maximum from user_job_preferences
    migration_statements.append("""ALTER TABLE user_job_preferences DROP COLUMN hourly_rate_maximum;""")

    # Drop column work_life_balance_importance from user_job_preferences
    migration_statements.append("""ALTER TABLE user_job_preferences DROP COLUMN work_life_balance_importance;""")


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

