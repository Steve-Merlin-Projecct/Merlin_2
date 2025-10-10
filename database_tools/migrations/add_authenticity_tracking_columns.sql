-- Migration: Add Authenticity Tracking to generated_documents table
-- Date: October 9, 2025
-- Purpose: Add columns to track document authenticity scoring and metadata

-- Add authenticity tracking columns
ALTER TABLE generated_documents
ADD COLUMN IF NOT EXISTS authenticity_score INTEGER,
ADD COLUMN IF NOT EXISTS metadata_creation_date TIMESTAMP,
ADD COLUMN IF NOT EXISTS metadata_modified_date TIMESTAMP,
ADD COLUMN IF NOT EXISTS editing_time_minutes INTEGER,
ADD COLUMN IF NOT EXISTS revision_number INTEGER,
ADD COLUMN IF NOT EXISTS typography_enhanced BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS verification_passed BOOLEAN,
ADD COLUMN IF NOT EXISTS verification_timestamp TIMESTAMP,
ADD COLUMN IF NOT EXISTS verification_issues_count INTEGER DEFAULT 0;

-- Add indexes for performance
CREATE INDEX IF NOT EXISTS idx_generated_documents_authenticity
ON generated_documents(authenticity_score);

CREATE INDEX IF NOT EXISTS idx_generated_documents_verification
ON generated_documents(verification_passed);

CREATE INDEX IF NOT EXISTS idx_generated_documents_typography
ON generated_documents(typography_enhanced);

-- Add comments for documentation
COMMENT ON COLUMN generated_documents.authenticity_score IS 'Overall authenticity score (0-100) based on metadata, typography, and structure validation';
COMMENT ON COLUMN generated_documents.metadata_creation_date IS 'Creation timestamp set in document metadata (not actual file creation)';
COMMENT ON COLUMN generated_documents.metadata_modified_date IS 'Modification timestamp set in document metadata';
COMMENT ON COLUMN generated_documents.editing_time_minutes IS 'Simulated editing time in minutes (set in TotalTime property)';
COMMENT ON COLUMN generated_documents.revision_number IS 'Document revision number (set in metadata)';
COMMENT ON COLUMN generated_documents.typography_enhanced IS 'Whether smart typography was applied (smart quotes, dashes, etc.)';
COMMENT ON COLUMN generated_documents.verification_passed IS 'Whether document passed authenticity verification checks';
COMMENT ON COLUMN generated_documents.verification_timestamp IS 'Timestamp when verification was performed';
COMMENT ON COLUMN generated_documents.verification_issues_count IS 'Number of issues found during verification';
