-- Migration 002: Create Analytics Views
-- Date: 2025-10-09
-- Task: task-01-database-schema-extensions
-- Description: Create SQL views for engagement and outcome analysis

-- Drop views if they exist (for re-running migration)
DROP VIEW IF EXISTS application_engagement_outcomes CASCADE;
DROP VIEW IF EXISTS link_function_effectiveness CASCADE;

-- View 1: Application Engagement Outcomes
-- Correlates link clicks with application outcomes
CREATE VIEW application_engagement_outcomes AS
SELECT
  ja.id AS application_id,
  ja.status,
  ja.created_at AS application_date,
  COUNT(lc.click_id) AS total_clicks,
  COUNT(DISTINCT lc.session_id) AS unique_sessions,
  MIN(lc.clicked_at) AS first_click_timestamp,
  MAX(lc.clicked_at) AS last_click_timestamp,
  EXTRACT(EPOCH FROM (MIN(lc.clicked_at) - ja.created_at))/3600 AS hours_to_first_click,
  ARRAY_AGG(DISTINCT lt.link_function ORDER BY lt.link_function) FILTER (WHERE lt.link_function IS NOT NULL) AS clicked_functions,
  MODE() WITHIN GROUP (ORDER BY lt.link_function) AS most_clicked_function
FROM job_applications ja
LEFT JOIN link_tracking lt ON ja.id = lt.application_id
LEFT JOIN link_clicks lc ON lt.tracking_id = lc.tracking_id
GROUP BY ja.id, ja.status, ja.created_at;

COMMENT ON VIEW application_engagement_outcomes IS
  'Aggregates link click data by application for outcome correlation analysis';

-- View 2: Link Function Effectiveness
-- Ranks link types by conversion rate to interviews/offers
CREATE VIEW link_function_effectiveness AS
SELECT
  lt.link_function,
  COUNT(DISTINCT lt.application_id) AS applications_with_link,
  COUNT(lc.click_id) AS total_clicks,
  ROUND(COUNT(lc.click_id)::NUMERIC / NULLIF(COUNT(DISTINCT lt.application_id), 0), 2) AS avg_clicks_per_application,
  COUNT(DISTINCT CASE WHEN ja.status = 'interview' THEN ja.id END) AS interviews_generated,
  COUNT(DISTINCT CASE WHEN ja.status = 'offer' THEN ja.id END) AS offers_generated,
  ROUND(100.0 * COUNT(DISTINCT CASE WHEN ja.status IN ('interview', 'offer') THEN ja.id END) /
    NULLIF(COUNT(DISTINCT lt.application_id), 0), 2) AS interview_conversion_rate
FROM link_tracking lt
LEFT JOIN link_clicks lc ON lt.tracking_id = lc.tracking_id
LEFT JOIN job_applications ja ON lt.application_id = ja.id
WHERE lt.is_active = true
GROUP BY lt.link_function
ORDER BY interview_conversion_rate DESC NULLS LAST;

COMMENT ON VIEW link_function_effectiveness IS
  'Performance metrics for each link type ranked by interview conversion rate';

-- Create indexes on underlying tables to improve view performance
CREATE INDEX IF NOT EXISTS idx_link_tracking_active_application
  ON link_tracking(is_active, application_id) WHERE is_active = true;

CREATE INDEX IF NOT EXISTS idx_link_clicks_session
  ON link_clicks(session_id, clicked_at);
