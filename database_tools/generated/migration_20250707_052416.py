"""
Database Migration Script
Generated on 2025-07-07 05:24:16
"""

from sqlalchemy import text
from sqlalchemy.orm import Session

def migrate_database(db: Session):
    """
    Apply database schema changes
    """
    migration_statements = []
    
    # Create new table: clicks
    migration_statements.append("""
CREATE TABLE clicks (
    tracking_id character varying(255) NOT NULL,
    timestamp timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (tracking_id) REFERENCES link_tracking(tracking_id)
);    """)

    # Add column application_email to cleaned_job_scrapes
    migration_statements.append("""ALTER TABLE cleaned_job_scrapes ADD COLUMN application_email text;""")

    # Drop column job_id from document_tone_analysis
    migration_statements.append("""ALTER TABLE document_tone_analysis DROP COLUMN job_id;""")

    # Drop column application_id from document_tone_analysis
    migration_statements.append("""ALTER TABLE document_tone_analysis DROP COLUMN application_id;""")

    # Drop column created_at from document_tone_analysis
    migration_statements.append("""ALTER TABLE document_tone_analysis DROP COLUMN created_at;""")

    # Drop column id from link_tracking
    migration_statements.append("""ALTER TABLE link_tracking DROP COLUMN id;""")

    # Drop column job_id from link_tracking
    migration_statements.append("""ALTER TABLE link_tracking DROP COLUMN job_id;""")

    # Drop column application_id from link_tracking
    migration_statements.append("""ALTER TABLE link_tracking DROP COLUMN application_id;""")

    # Drop column click_count from link_tracking
    migration_statements.append("""ALTER TABLE link_tracking DROP COLUMN click_count;""")

    # Drop column first_clicked_at from link_tracking
    migration_statements.append("""ALTER TABLE link_tracking DROP COLUMN first_clicked_at;""")

    # Drop column last_clicked_at from link_tracking
    migration_statements.append("""ALTER TABLE link_tracking DROP COLUMN last_clicked_at;""")

    # Drop column created_at from link_tracking
    migration_statements.append("""ALTER TABLE link_tracking DROP COLUMN created_at;""")


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

