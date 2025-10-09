-- Migration 001: Add Engagement Metrics to job_applications
-- Date: 2025-10-09
-- Task: task-01-database-schema-extensions
-- Description: Extend job_applications table with link tracking engagement metrics

-- Add engagement tracking columns to job_applications
ALTER TABLE job_applications
  ADD COLUMN IF NOT EXISTS first_click_timestamp TIMESTAMP,
  ADD COLUMN IF NOT EXISTS last_click_timestamp TIMESTAMP,
  ADD COLUMN IF NOT EXISTS total_clicks INTEGER DEFAULT 0,
  ADD COLUMN IF NOT EXISTS unique_click_sessions INTEGER DEFAULT 0,
  ADD COLUMN IF NOT EXISTS most_clicked_link_function VARCHAR(100),
  ADD COLUMN IF NOT EXISTS engagement_score INTEGER DEFAULT 0;

-- Add indexes for performance
CREATE INDEX IF NOT EXISTS idx_job_applications_engagement_score
  ON job_applications(engagement_score DESC);

CREATE INDEX IF NOT EXISTS idx_job_applications_first_click
  ON job_applications(first_click_timestamp);

CREATE INDEX IF NOT EXISTS idx_job_applications_total_clicks
  ON job_applications(total_clicks DESC);

-- Add comments for documentation
COMMENT ON COLUMN job_applications.first_click_timestamp IS 'Timestamp of first link click for this application';
COMMENT ON COLUMN job_applications.last_click_timestamp IS 'Timestamp of most recent link click for this application';
COMMENT ON COLUMN job_applications.total_clicks IS 'Total number of link clicks across all tracked links';
COMMENT ON COLUMN job_applications.unique_click_sessions IS 'Number of unique sessions that clicked links';
COMMENT ON COLUMN job_applications.most_clicked_link_function IS 'The link function type that received the most clicks';
COMMENT ON COLUMN job_applications.engagement_score IS 'Calculated engagement score (0-100) based on click behavior';
