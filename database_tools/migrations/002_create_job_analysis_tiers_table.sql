-- Migration: 002_create_job_analysis_tiers_table.sql
-- Date: 2025-10-09
-- Purpose: Create table for tracking 3-tier sequential batch analysis completion
-- Part of: Gemini Prompt Optimization - Phase 2 (Core Analysis Refactoring)

-- Create job_analysis_tiers table
CREATE TABLE IF NOT EXISTS job_analysis_tiers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id UUID NOT NULL UNIQUE REFERENCES jobs(id) ON DELETE CASCADE,

    -- Tier 1: Core Analysis
    tier_1_completed BOOLEAN DEFAULT FALSE,
    tier_1_timestamp TIMESTAMP,
    tier_1_tokens_used INTEGER,
    tier_1_model VARCHAR(50),
    tier_1_response_time_ms INTEGER,

    -- Tier 2: Enhanced Analysis
    tier_2_completed BOOLEAN DEFAULT FALSE,
    tier_2_timestamp TIMESTAMP,
    tier_2_tokens_used INTEGER,
    tier_2_model VARCHAR(50),
    tier_2_response_time_ms INTEGER,

    -- Tier 3: Strategic Insights
    tier_3_completed BOOLEAN DEFAULT FALSE,
    tier_3_timestamp TIMESTAMP,
    tier_3_tokens_used INTEGER,
    tier_3_model VARCHAR(50),
    tier_3_response_time_ms INTEGER,

    -- Metadata
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX idx_job_analysis_tiers_job_id ON job_analysis_tiers(job_id);
CREATE INDEX idx_job_analysis_tiers_tier1 ON job_analysis_tiers(tier_1_completed);
CREATE INDEX idx_job_analysis_tiers_tier2 ON job_analysis_tiers(tier_2_completed);
CREATE INDEX idx_job_analysis_tiers_tier3 ON job_analysis_tiers(tier_3_completed);
CREATE INDEX idx_job_analysis_tiers_created ON job_analysis_tiers(created_at);

-- Create trigger to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_job_analysis_tiers_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_job_analysis_tiers_updated_at
    BEFORE UPDATE ON job_analysis_tiers
    FOR EACH ROW
    EXECUTE FUNCTION update_job_analysis_tiers_updated_at();

-- Add comments
COMMENT ON TABLE job_analysis_tiers IS 'Tracks completion status for 3-tier sequential batch analysis';
COMMENT ON COLUMN job_analysis_tiers.tier_1_completed IS 'Tier 1 (Core): Skills, authenticity, industry, structured data';
COMMENT ON COLUMN job_analysis_tiers.tier_2_completed IS 'Tier 2 (Enhanced): Stress, red flags, implicit requirements';
COMMENT ON COLUMN job_analysis_tiers.tier_3_completed IS 'Tier 3 (Strategic): Prestige, cover letter insights, positioning';
