-- Migration: Create application_submissions table
-- Version: 1.0.0
-- Date: 2025-10-14
-- Description: Creates the application_submissions table for tracking automated
--              job application form submissions with comprehensive metadata.

BEGIN;

-- Create the application_submissions table
CREATE TABLE IF NOT EXISTS application_submissions (
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
    review_notes TEXT,

    -- Constraints
    CONSTRAINT valid_status CHECK (status IN ('pending', 'submitted', 'failed', 'reviewed')),
    CONSTRAINT valid_platform CHECK (form_platform IN ('indeed', 'greenhouse', 'lever', 'workday', 'other'))
);

-- Create indexes for common queries
CREATE INDEX IF NOT EXISTS idx_application_submissions_job_id
    ON application_submissions(job_id);

CREATE INDEX IF NOT EXISTS idx_application_submissions_status
    ON application_submissions(status);

CREATE INDEX IF NOT EXISTS idx_application_submissions_submitted_at
    ON application_submissions(submitted_at DESC);

CREATE INDEX IF NOT EXISTS idx_application_submissions_application_id
    ON application_submissions(application_id);

CREATE INDEX IF NOT EXISTS idx_application_submissions_actor_run_id
    ON application_submissions(actor_run_id);

CREATE INDEX IF NOT EXISTS idx_application_submissions_platform
    ON application_submissions(form_platform);

-- Create trigger function for updated_at
CREATE OR REPLACE FUNCTION update_application_submissions_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger
DROP TRIGGER IF EXISTS trigger_update_application_submissions_updated_at
    ON application_submissions;

CREATE TRIGGER trigger_update_application_submissions_updated_at
    BEFORE UPDATE ON application_submissions
    FOR EACH ROW
    EXECUTE FUNCTION update_application_submissions_updated_at();

-- Add comments for documentation
COMMENT ON TABLE application_submissions IS
    'Tracks automated job application form submissions with comprehensive metadata for review and debugging';

COMMENT ON COLUMN application_submissions.submission_id IS
    'Primary key UUID for the submission record';

COMMENT ON COLUMN application_submissions.application_id IS
    'Optional foreign key to applications table for linking';

COMMENT ON COLUMN application_submissions.job_id IS
    'Job posting ID from jobs table';

COMMENT ON COLUMN application_submissions.actor_run_id IS
    'Apify Actor run ID for tracking and debugging';

COMMENT ON COLUMN application_submissions.status IS
    'Submission status: pending, submitted, failed, reviewed';

COMMENT ON COLUMN application_submissions.form_platform IS
    'Platform where form was filled: indeed, greenhouse, lever, workday';

COMMENT ON COLUMN application_submissions.form_type IS
    'Specific form type detected (e.g., indeed_quick_apply, standard_indeed_apply)';

COMMENT ON COLUMN application_submissions.fields_filled IS
    'JSON array of field names that were successfully filled';

COMMENT ON COLUMN application_submissions.submission_confirmed IS
    'Boolean flag indicating if submission was verified via confirmation page';

COMMENT ON COLUMN application_submissions.confirmation_message IS
    'Confirmation message extracted from platform if available';

COMMENT ON COLUMN application_submissions.screenshot_urls IS
    'JSON array of screenshot URLs/paths for post-review';

COMMENT ON COLUMN application_submissions.screenshot_metadata IS
    'JSON object with detailed screenshot metadata';

COMMENT ON COLUMN application_submissions.error_message IS
    'Human-readable error message if submission failed';

COMMENT ON COLUMN application_submissions.error_details IS
    'Detailed error information as JSON for debugging';

COMMENT ON COLUMN application_submissions.submitted_at IS
    'Timestamp when submission was attempted';

COMMENT ON COLUMN application_submissions.reviewed_at IS
    'Timestamp when user reviewed the submission';

COMMENT ON COLUMN application_submissions.reviewed_by IS
    'User ID who reviewed the submission';

COMMENT ON COLUMN application_submissions.review_notes IS
    'User notes from manual review';

-- Insert sample data for testing (optional - comment out for production)
-- INSERT INTO application_submissions (
--     application_id, job_id, status, form_platform, form_type,
--     fields_filled, submission_confirmed
-- ) VALUES (
--     'app_test_001',
--     'job_test_001',
--     'submitted',
--     'indeed',
--     'standard_indeed_apply',
--     '["full_name", "email", "resume"]'::jsonb,
--     true
-- );

COMMIT;

-- Rollback script (run separately if needed):
-- BEGIN;
-- DROP TRIGGER IF EXISTS trigger_update_application_submissions_updated_at ON application_submissions;
-- DROP FUNCTION IF EXISTS update_application_submissions_updated_at();
-- DROP TABLE IF EXISTS application_submissions CASCADE;
-- COMMIT;
