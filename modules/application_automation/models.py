"""
Database Models for Application Automation

This module defines the SQLAlchemy model for tracking automated application
submissions. It should be integrated with the existing database models in
modules/database/database_models.py.

Note: This is a standalone model file for the MVP. In production, these models
should be added to the main database_models.py file and migrations should be
created using the database schema automation tools.
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, Boolean, Text, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base

# Use existing Base from database client
try:
    from modules.database.database_client import Base
except ImportError:
    # Fallback for standalone usage
    Base = declarative_base()


class ApplicationSubmission(Base):
    """
    Table for tracking automated application form submissions

    This table stores comprehensive information about each automated application
    attempt, including success/failure status, form details, screenshots, and
    error information for post-review and debugging.

    Attributes:
        submission_id: UUID primary key for the submission
        application_id: Foreign key to applications table (optional)
        job_id: Job posting ID from jobs table
        actor_run_id: Apify Actor run ID for tracking
        status: Submission status ('submitted', 'failed', 'pending', 'reviewed')
        form_platform: Platform where form was filled ('indeed', 'greenhouse', etc.)
        form_type: Specific form type ('indeed_quick_apply', 'standard_indeed_apply', etc.)
        fields_filled: List of field names that were successfully filled
        submission_confirmed: Boolean flag indicating if submission was verified
        confirmation_message: Confirmation message from platform if available
        screenshot_urls: JSON array of screenshot URLs/paths
        screenshot_metadata: JSON object with screenshot details
        error_message: Human-readable error message if failed
        error_details: Detailed error information as JSON
        submitted_at: Timestamp when submission was attempted
        reviewed_at: Timestamp when user reviewed the submission
        reviewed_by: User ID who reviewed (for multi-user systems)
        review_notes: User notes from review
        created_at: Timestamp when record was created
        updated_at: Timestamp when record was last updated
    """

    __tablename__ = "apify_application_submissions"

    # Primary key - auto-generated UUID
    submission_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Application tracking
    application_id = Column(String(255), nullable=True)  # Optional FK to applications
    job_id = Column(String(255), nullable=False, index=True)  # Job posting ID
    actor_run_id = Column(String(255), nullable=True)  # Apify Actor run ID

    # Submission status
    status = Column(
        String(50), nullable=False, default="pending", index=True
    )  # 'submitted', 'failed', 'pending', 'reviewed'

    # Form details
    form_platform = Column(String(50), nullable=False)  # 'indeed', 'greenhouse', 'lever', etc.
    form_type = Column(String(100), nullable=True)  # 'indeed_quick_apply', 'standard_indeed_apply', etc.

    # Form filling details
    fields_filled = Column(JSON, nullable=True)  # Array of field names that were filled
    submission_confirmed = Column(Boolean, default=False)  # Was submission verified?
    confirmation_message = Column(Text, nullable=True)  # Confirmation message from platform

    # Screenshots for review
    screenshot_urls = Column(JSON, nullable=True)  # Array of screenshot URLs/paths
    screenshot_metadata = Column(JSON, nullable=True)  # Screenshot details and metadata

    # Error handling
    error_message = Column(Text, nullable=True)  # Human-readable error message
    error_details = Column(JSON, nullable=True)  # Detailed error information

    # Timestamps
    submitted_at = Column(DateTime, nullable=False, default=datetime.utcnow)  # When submission attempted
    reviewed_at = Column(DateTime, nullable=True)  # When user reviewed the submission
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Review tracking
    reviewed_by = Column(String(255), nullable=True)  # User ID who reviewed
    review_notes = Column(Text, nullable=True)  # User notes from review

    # Multi-page form navigation support (Migration 002)
    checkpoint_data = Column(JSON, nullable=True, default=dict)  # Form state for resuming after failures
    current_page = Column(Integer, nullable=False, default=1)  # Current page number (1-indexed)
    total_pages = Column(Integer, nullable=True)  # Total pages detected (NULL if unknown)
    pages_completed = Column(JSON, nullable=True, default=list)  # Array of completed page numbers
    validation_errors = Column(JSON, nullable=True, default=list)  # Validation errors encountered
    navigation_history = Column(JSON, nullable=True, default=list)  # Chronological navigation log

    def __repr__(self):
        return f"<ApplicationSubmission(submission_id={self.submission_id}, job_id={self.job_id}, status={self.status})>"

    def to_dict(self):
        """Convert model to dictionary for JSON serialization"""
        return {
            "submission_id": str(self.submission_id),
            "application_id": self.application_id,
            "job_id": self.job_id,
            "actor_run_id": self.actor_run_id,
            "status": self.status,
            "form_platform": self.form_platform,
            "form_type": self.form_type,
            "fields_filled": self.fields_filled,
            "submission_confirmed": self.submission_confirmed,
            "confirmation_message": self.confirmation_message,
            "screenshot_urls": self.screenshot_urls,
            "screenshot_metadata": self.screenshot_metadata,
            "error_message": self.error_message,
            "error_details": self.error_details,
            "submitted_at": self.submitted_at.isoformat() if self.submitted_at else None,
            "reviewed_at": self.reviewed_at.isoformat() if self.reviewed_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "reviewed_by": self.reviewed_by,
            "review_notes": self.review_notes,
            # Multi-page navigation fields
            "checkpoint_data": self.checkpoint_data,
            "current_page": self.current_page,
            "total_pages": self.total_pages,
            "pages_completed": self.pages_completed,
            "validation_errors": self.validation_errors,
            "navigation_history": self.navigation_history,
        }

    def has_checkpoint(self) -> bool:
        """Check if submission has a valid checkpoint for resuming"""
        if not self.checkpoint_data:
            return False
        # Check if checkpoint is not stale (within 1 hour)
        if "timestamp" in self.checkpoint_data:
            from datetime import datetime, timedelta

            checkpoint_time = datetime.fromisoformat(self.checkpoint_data["timestamp"])
            if datetime.utcnow() - checkpoint_time > timedelta(hours=1):
                return False  # Checkpoint is stale
        return True

    def is_multipage_form(self) -> bool:
        """Check if this submission is for a multi-page form"""
        return self.total_pages is not None and self.total_pages > 1

    def get_next_page(self) -> int:
        """Get the next page number to fill (current_page + 1)"""
        return self.current_page + 1 if self.current_page else 2

    def mark_page_completed(self, page_num: int):
        """Mark a page as completed"""
        if self.pages_completed is None:
            self.pages_completed = []
        if page_num not in self.pages_completed:
            self.pages_completed.append(page_num)


# SQL migration for creating the table
# This should be run via database migration tools
CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS apify_application_submissions (
    submission_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    application_id VARCHAR(255),
    job_id VARCHAR(255) NOT NULL,
    actor_run_id VARCHAR(255),
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    form_platform VARCHAR(50) NOT NULL,
    form_type VARCHAR(100),
    fields_filled JSONB,
    submission_confirmed BOOLEAN DEFAULT FALSE,
    confirmation_message TEXT,
    screenshot_urls JSONB,
    screenshot_metadata JSONB,
    error_message TEXT,
    error_details JSONB,
    submitted_at TIMESTAMP NOT NULL DEFAULT NOW(),
    reviewed_at TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    reviewed_by VARCHAR(255),
    review_notes TEXT
);

-- Create indexes for common queries
CREATE INDEX IF NOT EXISTS idx_apify_application_submissions_job_id ON apify_application_submissions(job_id);
CREATE INDEX IF NOT EXISTS idx_apify_application_submissions_status ON apify_application_submissions(status);
CREATE INDEX IF NOT EXISTS idx_apify_application_submissions_submitted_at ON apify_application_submissions(submitted_at DESC);
CREATE INDEX IF NOT EXISTS idx_apify_application_submissions_application_id ON apify_application_submissions(application_id);

-- Create updated_at trigger
CREATE OR REPLACE FUNCTION update_apify_application_submissions_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_apify_application_submissions_updated_at
    BEFORE UPDATE ON apify_application_submissions
    FOR EACH ROW
    EXECUTE FUNCTION update_apify_application_submissions_updated_at();
"""


# Sample queries for common operations
SAMPLE_QUERIES = {
    "insert_submission": """
        INSERT INTO apify_application_submissions (
            application_id, job_id, actor_run_id, status, form_platform,
            form_type, fields_filled, submission_confirmed, confirmation_message,
            screenshot_urls, screenshot_metadata, submitted_at
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
        ) RETURNING submission_id;
    """,
    "get_submission_by_id": """
        SELECT * FROM apify_application_submissions WHERE submission_id = %s;
    """,
    "get_submissions_by_job_id": """
        SELECT * FROM apify_application_submissions WHERE job_id = %s ORDER BY submitted_at DESC;
    """,
    "get_pending_reviews": """
        SELECT * FROM apify_application_submissions
        WHERE status IN ('submitted', 'failed')
        AND reviewed_at IS NULL
        ORDER BY submitted_at DESC;
    """,
    "mark_as_reviewed": """
        UPDATE apify_application_submissions
        SET status = 'reviewed',
            reviewed_at = NOW(),
            reviewed_by = %s,
            review_notes = %s
        WHERE submission_id = %s;
    """,
    "get_submission_stats": """
        SELECT
            form_platform,
            status,
            COUNT(*) as count,
            AVG(CASE WHEN submission_confirmed THEN 1 ELSE 0 END) as confirmation_rate
        FROM apify_application_submissions
        WHERE submitted_at >= NOW() - INTERVAL '30 days'
        GROUP BY form_platform, status;
    """,
}
