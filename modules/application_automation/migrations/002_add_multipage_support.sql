-- Migration: Add Multi-Page Form Navigation Support
-- Version: 002
-- Created: 2025-10-17
-- Description: Adds columns for multi-page form state tracking, checkpointing, and validation error handling

-- ============================================================================
-- FORWARD MIGRATION
-- ============================================================================

BEGIN;

-- Add checkpoint and navigation tracking columns
ALTER TABLE apify_application_submissions
    ADD COLUMN IF NOT EXISTS checkpoint_data JSONB DEFAULT '{}',
    ADD COLUMN IF NOT EXISTS current_page INTEGER DEFAULT 1,
    ADD COLUMN IF NOT EXISTS total_pages INTEGER,
    ADD COLUMN IF NOT EXISTS pages_completed INTEGER[] DEFAULT '{}',
    ADD COLUMN IF NOT EXISTS validation_errors JSONB DEFAULT '[]',
    ADD COLUMN IF NOT EXISTS navigation_history JSONB DEFAULT '[]';

-- Add comments for documentation
COMMENT ON COLUMN apify_application_submissions.checkpoint_data IS
    'Stores form state for resuming after failures. Contains page-specific fields filled, timestamps, and metadata.';

COMMENT ON COLUMN apify_application_submissions.current_page IS
    'Current page number in multi-page form (1-indexed). Default: 1 for single-page forms.';

COMMENT ON COLUMN apify_application_submissions.total_pages IS
    'Total number of pages detected in form. NULL if unknown or single-page form.';

COMMENT ON COLUMN apify_application_submissions.pages_completed IS
    'Array of page numbers successfully completed (e.g., {1, 2} means pages 1 and 2 are done).';

COMMENT ON COLUMN apify_application_submissions.validation_errors IS
    'Array of validation errors encountered during form filling. Each entry: {"field": "email", "error": "Invalid format", "page": 1}';

COMMENT ON COLUMN apify_application_submissions.navigation_history IS
    'Chronological log of page navigations. Each entry: {"from_page": 1, "to_page": 2, "timestamp": "2025-10-17T10:30:00Z", "action": "next"}';

-- Create GIN index on checkpoint_data for efficient JSONB queries
CREATE INDEX IF NOT EXISTS idx_apify_submissions_checkpoint_data
    ON apify_application_submissions USING gin(checkpoint_data);

-- Create index on current_page for filtering multi-page submissions
CREATE INDEX IF NOT EXISTS idx_apify_submissions_current_page
    ON apify_application_submissions(current_page)
    WHERE current_page > 1;

-- Create index on pages_completed for checkpoint recovery queries
CREATE INDEX IF NOT EXISTS idx_apify_submissions_pages_completed
    ON apify_application_submissions USING gin(pages_completed);

COMMIT;

-- ============================================================================
-- ROLLBACK MIGRATION
-- ============================================================================

-- To rollback this migration, run the following:

/*
BEGIN;

-- Drop indexes
DROP INDEX IF EXISTS idx_apify_submissions_checkpoint_data;
DROP INDEX IF EXISTS idx_apify_submissions_current_page;
DROP INDEX IF EXISTS idx_apify_submissions_pages_completed;

-- Remove columns
ALTER TABLE apify_application_submissions
    DROP COLUMN IF EXISTS checkpoint_data,
    DROP COLUMN IF EXISTS current_page,
    DROP COLUMN IF EXISTS total_pages,
    DROP COLUMN IF EXISTS pages_completed,
    DROP COLUMN IF EXISTS validation_errors,
    DROP COLUMN IF EXISTS navigation_history;

COMMIT;
*/

-- ============================================================================
-- VERIFICATION QUERIES
-- ============================================================================

-- Verify columns were added:
-- SELECT column_name, data_type, column_default
-- FROM information_schema.columns
-- WHERE table_name = 'apify_application_submissions'
-- AND column_name IN ('checkpoint_data', 'current_page', 'total_pages', 'pages_completed', 'validation_errors', 'navigation_history');

-- Verify indexes were created:
-- SELECT indexname, indexdef
-- FROM pg_indexes
-- WHERE tablename = 'apify_application_submissions'
-- AND indexname LIKE '%checkpoint%' OR indexname LIKE '%page%';
