-- Dashboard Redesign: Aggregation Tables
-- Migration: 003_dashboard_aggregation_tables
-- Date: 2025-10-09
-- Purpose: Pre-compute metrics to avoid expensive aggregations on every dashboard load

-- ============================================================
-- HOURLY METRICS AGGREGATION TABLE
-- ============================================================

-- Drop existing table if it exists
DROP TABLE IF EXISTS dashboard_metrics_hourly CASCADE;

-- Create hourly metrics table
CREATE TABLE dashboard_metrics_hourly (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    metric_hour TIMESTAMP NOT NULL UNIQUE,

    -- Scraping metrics
    jobs_scraped_count INT DEFAULT 0,
    jobs_cleaned_count INT DEFAULT 0,
    jobs_deduplicated_count INT DEFAULT 0,
    scraping_errors_count INT DEFAULT 0,
    scraping_avg_duration_ms INT DEFAULT 0,

    -- AI Analysis metrics
    jobs_analyzed_count INT DEFAULT 0,
    ai_requests_sent INT DEFAULT 0,
    ai_tokens_input INT DEFAULT 0,
    ai_tokens_output INT DEFAULT 0,
    ai_cost_incurred DECIMAL(10,4) DEFAULT 0.00,
    ai_avg_duration_ms INT DEFAULT 0,

    -- Application metrics
    applications_sent_count INT DEFAULT 0,
    applications_success_count INT DEFAULT 0,
    applications_failed_count INT DEFAULT 0,
    documents_generated_count INT DEFAULT 0,
    application_avg_duration_ms INT DEFAULT 0,

    -- Pipeline health metrics
    pipeline_conversion_rate DECIMAL(5,2) DEFAULT 0.00,
    pipeline_bottleneck VARCHAR(50),

    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for time-based queries
CREATE INDEX idx_metrics_hourly_hour ON dashboard_metrics_hourly(metric_hour DESC);
CREATE INDEX idx_metrics_hourly_created ON dashboard_metrics_hourly(created_at DESC);

-- ============================================================
-- DAILY METRICS AGGREGATION TABLE
-- ============================================================

-- Drop existing table if it exists
DROP TABLE IF EXISTS dashboard_metrics_daily CASCADE;

-- Create daily metrics table (similar structure to hourly)
CREATE TABLE dashboard_metrics_daily (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    metric_date DATE NOT NULL UNIQUE,

    -- Scraping metrics (daily totals)
    jobs_scraped_count INT DEFAULT 0,
    jobs_cleaned_count INT DEFAULT 0,
    jobs_deduplicated_count INT DEFAULT 0,
    scraping_errors_count INT DEFAULT 0,
    scraping_avg_duration_ms INT DEFAULT 0,
    scraping_peak_hour INT, -- Hour with most activity (0-23)

    -- AI Analysis metrics (daily totals)
    jobs_analyzed_count INT DEFAULT 0,
    ai_requests_sent INT DEFAULT 0,
    ai_tokens_input INT DEFAULT 0,
    ai_tokens_output INT DEFAULT 0,
    ai_cost_incurred DECIMAL(10,4) DEFAULT 0.00,
    ai_avg_duration_ms INT DEFAULT 0,
    ai_model_used VARCHAR(100),

    -- Application metrics (daily totals)
    applications_sent_count INT DEFAULT 0,
    applications_success_count INT DEFAULT 0,
    applications_failed_count INT DEFAULT 0,
    documents_generated_count INT DEFAULT 0,
    application_avg_duration_ms INT DEFAULT 0,
    success_rate DECIMAL(5,2) DEFAULT 0.00,

    -- Pipeline health metrics
    pipeline_conversion_rate DECIMAL(5,2) DEFAULT 0.00,
    pipeline_bottleneck VARCHAR(50),
    total_pipeline_jobs INT DEFAULT 0,

    -- Comparisons (vs previous day)
    jobs_trend_pct DECIMAL(5,2) DEFAULT 0.00,
    applications_trend_pct DECIMAL(5,2) DEFAULT 0.00,

    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for time-based queries
CREATE INDEX idx_metrics_daily_date ON dashboard_metrics_daily(metric_date DESC);
CREATE INDEX idx_metrics_daily_created ON dashboard_metrics_daily(created_at DESC);

-- ============================================================
-- AGGREGATION FUNCTIONS
-- ============================================================

-- Function to compute hourly metrics for a specific hour
CREATE OR REPLACE FUNCTION compute_hourly_metrics(target_hour TIMESTAMP)
RETURNS void AS $$
DECLARE
    hour_start TIMESTAMP;
    hour_end TIMESTAMP;
    prev_hour_count INT;
BEGIN
    -- Round to start of hour
    hour_start := DATE_TRUNC('hour', target_hour);
    hour_end := hour_start + INTERVAL '1 hour';

    -- Delete existing entry for this hour (if recomputing)
    DELETE FROM dashboard_metrics_hourly WHERE metric_hour = hour_start;

    -- Insert computed metrics
    INSERT INTO dashboard_metrics_hourly (
        metric_hour,
        jobs_scraped_count,
        jobs_cleaned_count,
        jobs_analyzed_count,
        applications_sent_count,
        applications_success_count,
        applications_failed_count
    )
    SELECT
        hour_start,
        -- Scraping: Count jobs created in this hour
        (SELECT COUNT(*) FROM jobs WHERE created_at >= hour_start AND created_at < hour_end),
        -- Cleaning: Count cleaned jobs in this hour
        (SELECT COUNT(*) FROM cleaned_job_scrapes WHERE cleaned_timestamp >= hour_start AND cleaned_timestamp < hour_end),
        -- Analysis: Count analyzed jobs in this hour
        (SELECT COUNT(*) FROM analyzed_jobs WHERE ai_analysis_completed = true
            AND created_at >= hour_start AND created_at < hour_end),
        -- Applications: Count sent in this hour
        (SELECT COUNT(*) FROM job_applications WHERE created_at >= hour_start AND created_at < hour_end),
        -- Success: Count successful applications
        (SELECT COUNT(*) FROM job_applications WHERE created_at >= hour_start AND created_at < hour_end
            AND application_status = 'sent'),
        -- Failed: Count failed applications
        (SELECT COUNT(*) FROM job_applications WHERE created_at >= hour_start AND created_at < hour_end
            AND application_status = 'failed');

    RAISE NOTICE 'Computed hourly metrics for %', hour_start;
END;
$$ LANGUAGE plpgsql;

-- Function to compute daily metrics for a specific date
CREATE OR REPLACE FUNCTION compute_daily_metrics(target_date DATE)
RETURNS void AS $$
DECLARE
    day_start TIMESTAMP;
    day_end TIMESTAMP;
    prev_day_jobs INT;
    prev_day_apps INT;
    current_jobs INT;
    current_apps INT;
BEGIN
    -- Date range for the day
    day_start := target_date::TIMESTAMP;
    day_end := day_start + INTERVAL '1 day';

    -- Get previous day counts for trends
    SELECT COALESCE(jobs_scraped_count, 0), COALESCE(applications_sent_count, 0)
    INTO prev_day_jobs, prev_day_apps
    FROM dashboard_metrics_daily
    WHERE metric_date = target_date - INTERVAL '1 day';

    -- Delete existing entry (if recomputing)
    DELETE FROM dashboard_metrics_daily WHERE metric_date = target_date;

    -- Get current day counts
    SELECT COUNT(*) INTO current_jobs FROM jobs WHERE created_at >= day_start AND created_at < day_end;
    SELECT COUNT(*) INTO current_apps FROM job_applications WHERE created_at >= day_start AND created_at < day_end;

    -- Insert computed metrics
    INSERT INTO dashboard_metrics_daily (
        metric_date,
        jobs_scraped_count,
        jobs_cleaned_count,
        jobs_analyzed_count,
        applications_sent_count,
        applications_success_count,
        applications_failed_count,
        success_rate,
        jobs_trend_pct,
        applications_trend_pct,
        total_pipeline_jobs
    )
    SELECT
        target_date,
        current_jobs,
        (SELECT COUNT(*) FROM cleaned_job_scrapes WHERE cleaned_timestamp >= day_start AND cleaned_timestamp < day_end),
        (SELECT COUNT(*) FROM analyzed_jobs WHERE ai_analysis_completed = true
            AND created_at >= day_start AND created_at < day_end),
        current_apps,
        (SELECT COUNT(*) FROM job_applications WHERE created_at >= day_start AND created_at < day_end
            AND application_status = 'sent'),
        (SELECT COUNT(*) FROM job_applications WHERE created_at >= day_start AND created_at < day_end
            AND application_status = 'failed'),
        -- Success rate
        CASE
            WHEN current_apps > 0 THEN
                (SELECT COUNT(*) FROM job_applications WHERE created_at >= day_start AND created_at < day_end
                    AND application_status = 'sent')::DECIMAL / current_apps * 100
            ELSE 0
        END,
        -- Trend calculations
        CASE
            WHEN prev_day_jobs > 0 THEN ((current_jobs - prev_day_jobs)::DECIMAL / prev_day_jobs * 100)
            ELSE 0
        END,
        CASE
            WHEN prev_day_apps > 0 THEN ((current_apps - prev_day_apps)::DECIMAL / prev_day_apps * 100)
            ELSE 0
        END,
        (SELECT COUNT(*) FROM jobs); -- Total jobs in pipeline

    RAISE NOTICE 'Computed daily metrics for %', target_date;
END;
$$ LANGUAGE plpgsql;

-- ============================================================
-- BULK BACKFILL FUNCTIONS
-- ============================================================

-- Function to backfill hourly metrics for a date range
CREATE OR REPLACE FUNCTION backfill_hourly_metrics(
    start_date TIMESTAMP,
    end_date TIMESTAMP
)
RETURNS void AS $$
DECLARE
    current_hour TIMESTAMP;
BEGIN
    current_hour := DATE_TRUNC('hour', start_date);

    WHILE current_hour < end_date LOOP
        PERFORM compute_hourly_metrics(current_hour);
        current_hour := current_hour + INTERVAL '1 hour';
    END LOOP;

    RAISE NOTICE 'Backfilled hourly metrics from % to %', start_date, end_date;
END;
$$ LANGUAGE plpgsql;

-- Function to backfill daily metrics for a date range
CREATE OR REPLACE FUNCTION backfill_daily_metrics(
    start_date DATE,
    end_date DATE
)
RETURNS void AS $$
DECLARE
    current_date DATE;
BEGIN
    current_date := start_date;

    WHILE current_date <= end_date LOOP
        PERFORM compute_daily_metrics(current_date);
        current_date := current_date + INTERVAL '1 day';
    END LOOP;

    RAISE NOTICE 'Backfilled daily metrics from % to %', start_date, end_date;
END;
$$ LANGUAGE plpgsql;

-- ============================================================
-- USAGE EXAMPLES
-- ============================================================

-- Compute metrics for current hour
-- SELECT compute_hourly_metrics(NOW());

-- Compute metrics for today
-- SELECT compute_daily_metrics(CURRENT_DATE);

-- Backfill last 7 days
-- SELECT backfill_daily_metrics(CURRENT_DATE - INTERVAL '7 days', CURRENT_DATE);

-- Backfill last 24 hours (hourly)
-- SELECT backfill_hourly_metrics(NOW() - INTERVAL '24 hours', NOW());

-- ============================================================
-- QUERY EXAMPLES (Fast Aggregated Queries)
-- ============================================================

-- Get last 7 days of metrics (pre-computed)
COMMENT ON TABLE dashboard_metrics_daily IS
'Daily aggregated metrics for dashboard. Query this instead of aggregating live data.
Example: SELECT * FROM dashboard_metrics_daily WHERE metric_date >= CURRENT_DATE - INTERVAL ''7 days'' ORDER BY metric_date DESC;';

-- Get last 24 hours hourly breakdown
COMMENT ON TABLE dashboard_metrics_hourly IS
'Hourly aggregated metrics for dashboard. Query this for detailed time-series data.
Example: SELECT * FROM dashboard_metrics_hourly WHERE metric_hour >= NOW() - INTERVAL ''24 hours'' ORDER BY metric_hour DESC;';

-- ============================================================
-- SCHEDULED AGGREGATION (Setup Instructions)
-- ============================================================

-- Add to crontab for automatic updates:
-- # Compute hourly metrics (runs every hour at :05)
-- 5 * * * * psql -c "SELECT compute_hourly_metrics(DATE_TRUNC('hour', NOW() - INTERVAL '1 hour'));"
--
-- # Compute daily metrics (runs at 00:10 every day)
-- 10 0 * * * psql -c "SELECT compute_daily_metrics(CURRENT_DATE - INTERVAL '1 day');"

-- ============================================================
-- VERIFICATION
-- ============================================================

-- Check tables were created
SELECT
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables
WHERE tablename LIKE 'dashboard_metrics_%'
ORDER BY tablename;

-- Check if we have any data
SELECT 'hourly' as type, COUNT(*) as row_count, MIN(metric_hour) as earliest, MAX(metric_hour) as latest
FROM dashboard_metrics_hourly
UNION ALL
SELECT 'daily' as type, COUNT(*) as row_count, MIN(metric_date::TIMESTAMP) as earliest, MAX(metric_date::TIMESTAMP) as latest
FROM dashboard_metrics_daily;

-- ============================================================
-- ROLLBACK SCRIPT
-- ============================================================

-- To rollback, run:
-- DROP FUNCTION IF EXISTS compute_hourly_metrics(TIMESTAMP);
-- DROP FUNCTION IF EXISTS compute_daily_metrics(DATE);
-- DROP FUNCTION IF EXISTS backfill_hourly_metrics(TIMESTAMP, TIMESTAMP);
-- DROP FUNCTION IF EXISTS backfill_daily_metrics(DATE, DATE);
-- DROP TABLE IF EXISTS dashboard_metrics_hourly CASCADE;
-- DROP TABLE IF EXISTS dashboard_metrics_daily CASCADE;
