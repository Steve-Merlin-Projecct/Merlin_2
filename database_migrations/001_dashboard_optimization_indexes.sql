-- Dashboard Redesign: Critical Database Indexes
-- Migration: 001_dashboard_optimization_indexes
-- Date: 2025-10-09
-- Purpose: Add indexes to improve dashboard query performance by 80%+

-- ============================================================
-- DASHBOARD QUERY OPTIMIZATION INDEXES
-- ============================================================

-- Index 1: Jobs created_at (for time-based filtering)
-- Used by: Dashboard stats, recent jobs queries
-- Impact: 24h/7d job counts
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_jobs_created_at
ON jobs(created_at DESC);

-- Index 2: Jobs eligibility + priority (for job discovery)
-- Used by: ApplicationOrchestrator, job matching
-- Impact: Eligible job queries
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_jobs_eligibility_priority
ON jobs(eligibility_flag, priority_score DESC, application_status)
WHERE eligibility_flag = true;

-- Index 3: Job applications created + status (for dashboard applications table)
-- Used by: Dashboard recent applications, application stats
-- Impact: Application counts, filtering by status
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_applications_created_status
ON job_applications(created_at DESC, application_status);

-- ============================================================
-- WORKFLOW PROCESSING OPTIMIZATION INDEXES
-- ============================================================

-- Index 4: Analyzed jobs eligibility (for application workflow)
-- Used by: Job discovery, application orchestrator
-- Impact: Finding eligible unapplied jobs
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_analyzed_jobs_eligible
ON analyzed_jobs(eligibility_flag, priority_score DESC, ai_analysis_completed)
WHERE eligibility_flag = true AND application_status = 'not_applied';

-- Index 5: Pre-analyzed jobs queue (for AI analysis pipeline)
-- Used by: Batch AI analyzer
-- Impact: Finding jobs queued for analysis
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_pre_analyzed_queued
ON pre_analyzed_jobs(queued_for_analysis, created_at DESC)
WHERE queued_for_analysis = true;

-- ============================================================
-- PIPELINE STATISTICS OPTIMIZATION INDEXES
-- ============================================================

-- Index 6: Cleaned jobs timestamp (for pipeline stats)
-- Used by: Pipeline status, scraping velocity
-- Impact: Cleaned job counts, time-based queries
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_cleaned_jobs_timestamp
ON cleaned_job_scrapes(cleaned_timestamp DESC);

-- Index 7: Raw scrapes timestamp (for pipeline entry point)
-- Used by: Pipeline stats, scraping monitoring
-- Impact: Raw job counts, scraping rate calculations
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_raw_scrapes_timestamp
ON raw_job_scrapes(scrape_timestamp DESC);

-- ============================================================
-- SEARCH & LOOKUP OPTIMIZATION INDEXES
-- ============================================================

-- Index 8: Company name fuzzy search (for company lookup)
-- Used by: Company search, job filtering
-- Impact: Fast company name searches
-- Note: Requires pg_trgm extension
CREATE EXTENSION IF NOT EXISTS pg_trgm;

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_companies_name_trgm
ON companies USING gin(name gin_trgm_ops);

-- ============================================================
-- VERIFICATION QUERIES
-- ============================================================

-- Verify indexes were created
SELECT
    schemaname,
    tablename,
    indexname,
    indexdef
FROM pg_indexes
WHERE indexname LIKE 'idx_%'
    AND tablename IN (
        'jobs',
        'job_applications',
        'analyzed_jobs',
        'pre_analyzed_jobs',
        'cleaned_job_scrapes',
        'raw_job_scrapes',
        'companies'
    )
ORDER BY tablename, indexname;

-- Check index sizes
SELECT
    schemaname,
    tablename,
    indexname,
    pg_size_pretty(pg_relation_size(indexrelid)) as index_size
FROM pg_stat_user_indexes
WHERE indexrelname LIKE 'idx_%'
ORDER BY pg_relation_size(indexrelid) DESC;

-- ============================================================
-- ROLLBACK SCRIPT (if needed)
-- ============================================================

-- To rollback, run:
-- DROP INDEX CONCURRENTLY IF EXISTS idx_jobs_created_at;
-- DROP INDEX CONCURRENTLY IF EXISTS idx_jobs_eligibility_priority;
-- DROP INDEX CONCURRENTLY IF EXISTS idx_applications_created_status;
-- DROP INDEX CONCURRENTLY IF EXISTS idx_analyzed_jobs_eligible;
-- DROP INDEX CONCURRENTLY IF EXISTS idx_pre_analyzed_queued;
-- DROP INDEX CONCURRENTLY IF EXISTS idx_cleaned_jobs_timestamp;
-- DROP INDEX CONCURRENTLY IF EXISTS idx_raw_scrapes_timestamp;
-- DROP INDEX CONCURRENTLY IF EXISTS idx_companies_name_trgm;
