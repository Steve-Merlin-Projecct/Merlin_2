-- Migration 003: Backfill Engagement Data
-- Date: 2025-10-09
-- Task: task-01-database-schema-extensions
-- Description: Populate engagement metrics for existing applications

-- Backfill engagement metrics for all existing applications
UPDATE job_applications ja
SET
  first_click_timestamp = subq.first_click,
  last_click_timestamp = subq.last_click,
  total_clicks = subq.total_clicks,
  unique_click_sessions = subq.unique_sessions,
  most_clicked_link_function = subq.most_clicked_function
FROM (
  SELECT
    lt.application_id,
    MIN(lc.clicked_at) AS first_click,
    MAX(lc.clicked_at) AS last_click,
    COUNT(lc.click_id) AS total_clicks,
    COUNT(DISTINCT lc.session_id) AS unique_sessions,
    MODE() WITHIN GROUP (ORDER BY lt.link_function) AS most_clicked_function
  FROM link_tracking lt
  LEFT JOIN link_clicks lc ON lt.tracking_id = lc.tracking_id
  WHERE lt.application_id IS NOT NULL
  GROUP BY lt.application_id
) subq
WHERE ja.id = subq.application_id;

-- Log the backfill results
DO $$
DECLARE
  updated_count INTEGER;
BEGIN
  SELECT COUNT(*) INTO updated_count
  FROM job_applications
  WHERE first_click_timestamp IS NOT NULL;

  RAISE NOTICE 'Backfill complete: % applications updated with engagement data', updated_count;
END $$;
