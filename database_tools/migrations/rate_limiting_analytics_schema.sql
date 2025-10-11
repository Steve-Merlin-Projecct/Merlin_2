-- ============================================================================
-- Rate Limiting Analytics Schema
-- Version: 1.0.0
-- Created: 2025-10-11
-- Purpose: Track rate limit violations, query patterns, and cache optimization
-- ============================================================================

-- ============================================================================
-- Table 1: Rate Limit Analytics
-- Purpose: Track all rate limit violations for monitoring and analysis
-- ============================================================================

CREATE TABLE IF NOT EXISTS rate_limit_analytics (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL DEFAULT NOW(),
    endpoint VARCHAR(255) NOT NULL,
    client_ip VARCHAR(45),
    user_id VARCHAR(100),
    limit_exceeded VARCHAR(50),
    current_count INTEGER,
    limit_value INTEGER,
    window_seconds INTEGER,
    user_agent TEXT,
    request_method VARCHAR(10),

    -- Indexes for fast queries
    CONSTRAINT rate_limit_analytics_timestamp_check CHECK (timestamp IS NOT NULL)
);

-- Indexes for rate_limit_analytics
CREATE INDEX IF NOT EXISTS idx_rate_limit_timestamp
    ON rate_limit_analytics(timestamp DESC);

CREATE INDEX IF NOT EXISTS idx_rate_limit_endpoint
    ON rate_limit_analytics(endpoint);

CREATE INDEX IF NOT EXISTS idx_rate_limit_client_ip
    ON rate_limit_analytics(client_ip);

CREATE INDEX IF NOT EXISTS idx_rate_limit_user_id
    ON rate_limit_analytics(user_id);

-- Composite index for common queries
CREATE INDEX IF NOT EXISTS idx_rate_limit_endpoint_timestamp
    ON rate_limit_analytics(endpoint, timestamp DESC);

-- Comment on table
COMMENT ON TABLE rate_limit_analytics IS 'Tracks all rate limit violations for security monitoring and usage analysis';
COMMENT ON COLUMN rate_limit_analytics.endpoint IS 'API endpoint that was rate limited';
COMMENT ON COLUMN rate_limit_analytics.client_ip IS 'Client IP address that exceeded limit';
COMMENT ON COLUMN rate_limit_analytics.user_id IS 'Authenticated user ID (or anonymous)';
COMMENT ON COLUMN rate_limit_analytics.limit_exceeded IS 'Rate limit string that was exceeded (e.g., 10/minute)';


-- ============================================================================
-- Table 2: Query Logs
-- Purpose: Log database queries for cache analysis and optimization
-- ============================================================================

CREATE TABLE IF NOT EXISTS query_logs (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL DEFAULT NOW(),
    endpoint VARCHAR(255) NOT NULL,
    query_hash VARCHAR(64) NOT NULL,
    query_template TEXT,
    execution_time_ms FLOAT,
    result_size_bytes INTEGER,
    client_ip VARCHAR(45),
    user_id VARCHAR(100),

    -- Constraints
    CONSTRAINT query_logs_timestamp_check CHECK (timestamp IS NOT NULL),
    CONSTRAINT query_logs_hash_check CHECK (length(query_hash) = 64)
);

-- Indexes for query_logs
CREATE INDEX IF NOT EXISTS idx_query_hash_timestamp
    ON query_logs(query_hash, timestamp DESC);

CREATE INDEX IF NOT EXISTS idx_query_timestamp
    ON query_logs(timestamp DESC);

CREATE INDEX IF NOT EXISTS idx_query_endpoint
    ON query_logs(endpoint);

-- Composite index for deduplication analysis
CREATE INDEX IF NOT EXISTS idx_query_hash_endpoint
    ON query_logs(query_hash, endpoint, timestamp DESC);

-- Comment on table
COMMENT ON TABLE query_logs IS 'Logs all database queries for cache hit analysis and optimization recommendations';
COMMENT ON COLUMN query_logs.query_hash IS 'SHA-256 hash of normalized query for deduplication';
COMMENT ON COLUMN query_logs.query_template IS 'Parameterized query template (without specific values)';
COMMENT ON COLUMN query_logs.execution_time_ms IS 'Query execution time in milliseconds';
COMMENT ON COLUMN query_logs.result_size_bytes IS 'Size of result set in bytes';


-- ============================================================================
-- Table 3: Cache Analysis Daily
-- Purpose: Daily aggregated analysis of caching potential
-- ============================================================================

CREATE TABLE IF NOT EXISTS cache_analysis_daily (
    id SERIAL PRIMARY KEY,
    analysis_date DATE NOT NULL UNIQUE,
    total_queries INTEGER NOT NULL DEFAULT 0,
    unique_queries INTEGER NOT NULL DEFAULT 0,
    duplicate_queries INTEGER NOT NULL DEFAULT 0,
    cache_hit_potential_percent FLOAT,
    top_cacheable_queries JSONB,
    estimated_latency_savings_ms INTEGER,
    memory_required_mb FLOAT,
    recommended_ttl_seconds INTEGER,
    generated_at TIMESTAMP DEFAULT NOW(),

    -- Constraints
    CONSTRAINT cache_analysis_date_check CHECK (analysis_date IS NOT NULL),
    CONSTRAINT cache_analysis_totals_check CHECK (total_queries >= unique_queries),
    CONSTRAINT cache_analysis_percent_check CHECK (cache_hit_potential_percent >= 0 AND cache_hit_potential_percent <= 100)
);

-- Indexes for cache_analysis_daily
CREATE INDEX IF NOT EXISTS idx_cache_analysis_date
    ON cache_analysis_daily(analysis_date DESC);

-- Comment on table
COMMENT ON TABLE cache_analysis_daily IS 'Daily aggregated cache analysis showing optimization opportunities';
COMMENT ON COLUMN cache_analysis_daily.total_queries IS 'Total number of queries executed';
COMMENT ON COLUMN cache_analysis_daily.unique_queries IS 'Number of unique query patterns';
COMMENT ON COLUMN cache_analysis_daily.duplicate_queries IS 'Number of repeated queries (caching opportunity)';
COMMENT ON COLUMN cache_analysis_daily.cache_hit_potential_percent IS 'Percentage of queries that could benefit from caching';
COMMENT ON COLUMN cache_analysis_daily.top_cacheable_queries IS 'JSON array of most frequently repeated queries';
COMMENT ON COLUMN cache_analysis_daily.estimated_latency_savings_ms IS 'Estimated total latency savings from caching per day';
COMMENT ON COLUMN cache_analysis_daily.memory_required_mb IS 'Estimated Redis memory required for caching';
COMMENT ON COLUMN cache_analysis_daily.recommended_ttl_seconds IS 'Recommended TTL for cached entries';


-- ============================================================================
-- View: Latest Cache Analysis
-- Purpose: Quick access to most recent cache analysis
-- ============================================================================

CREATE OR REPLACE VIEW v_latest_cache_analysis AS
SELECT
    analysis_date,
    total_queries,
    unique_queries,
    duplicate_queries,
    cache_hit_potential_percent,
    estimated_latency_savings_ms,
    memory_required_mb,
    recommended_ttl_seconds,
    generated_at
FROM cache_analysis_daily
ORDER BY analysis_date DESC
LIMIT 1;

COMMENT ON VIEW v_latest_cache_analysis IS 'Most recent cache analysis results for quick dashboard access';


-- ============================================================================
-- View: Rate Limit Violations Summary
-- Purpose: Aggregated view of rate limit violations by endpoint
-- ============================================================================

CREATE OR REPLACE VIEW v_rate_limit_violations_summary AS
SELECT
    endpoint,
    COUNT(*) AS total_violations,
    COUNT(DISTINCT client_ip) AS unique_ips,
    COUNT(DISTINCT user_id) AS unique_users,
    MIN(timestamp) AS first_violation,
    MAX(timestamp) AS last_violation,
    ROUND(AVG(current_count), 2) AS avg_current_count,
    MAX(current_count) AS max_current_count
FROM rate_limit_analytics
WHERE timestamp > NOW() - INTERVAL '7 days'
GROUP BY endpoint
ORDER BY total_violations DESC;

COMMENT ON VIEW v_rate_limit_violations_summary IS '7-day summary of rate limit violations grouped by endpoint';


-- ============================================================================
-- View: Top Cacheable Queries
-- Purpose: Identify most frequently repeated queries for caching
-- ============================================================================

CREATE OR REPLACE VIEW v_top_cacheable_queries AS
SELECT
    query_hash,
    query_template,
    COUNT(*) AS execution_count,
    ROUND(AVG(execution_time_ms), 2) AS avg_execution_time_ms,
    ROUND(SUM(execution_time_ms), 2) AS total_execution_time_ms,
    ROUND(AVG(result_size_bytes) / 1024.0, 2) AS avg_result_size_kb,
    COUNT(DISTINCT endpoint) AS used_by_endpoints,
    MIN(timestamp) AS first_seen,
    MAX(timestamp) AS last_seen
FROM query_logs
WHERE timestamp > NOW() - INTERVAL '24 hours'
GROUP BY query_hash, query_template
HAVING COUNT(*) > 5  -- Only show queries executed more than 5 times
ORDER BY execution_count DESC
LIMIT 10;

COMMENT ON VIEW v_top_cacheable_queries IS 'Top 10 most frequently executed queries in last 24 hours (caching candidates)';


-- ============================================================================
-- Function: Calculate Cache Hit Rate
-- Purpose: Calculate potential cache hit rate for a given time period
-- ============================================================================

CREATE OR REPLACE FUNCTION calculate_cache_hit_potential(
    lookback_hours INTEGER DEFAULT 24
) RETURNS TABLE (
    total_queries BIGINT,
    unique_queries BIGINT,
    duplicate_queries BIGINT,
    cache_hit_potential_percent NUMERIC(5,2)
) AS $$
BEGIN
    RETURN QUERY
    WITH query_stats AS (
        SELECT
            COUNT(*) AS total,
            COUNT(DISTINCT query_hash) AS unique_cnt
        FROM query_logs
        WHERE timestamp > NOW() - (lookback_hours || ' hours')::INTERVAL
    )
    SELECT
        total,
        unique_cnt,
        total - unique_cnt AS duplicates,
        CASE
            WHEN total > 0 THEN ROUND(((total - unique_cnt)::NUMERIC / total::NUMERIC) * 100, 2)
            ELSE 0
        END AS hit_potential
    FROM query_stats;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION calculate_cache_hit_potential IS 'Calculate potential cache hit rate for specified lookback period';


-- ============================================================================
-- Function: Cleanup Old Analytics Data
-- Purpose: Remove old analytics data to manage database size
-- ============================================================================

CREATE OR REPLACE FUNCTION cleanup_old_analytics(
    retention_days INTEGER DEFAULT 90
) RETURNS TABLE (
    rate_limit_rows_deleted BIGINT,
    query_log_rows_deleted BIGINT
) AS $$
DECLARE
    rate_limit_deleted BIGINT;
    query_log_deleted BIGINT;
BEGIN
    -- Delete old rate limit analytics
    DELETE FROM rate_limit_analytics
    WHERE timestamp < NOW() - (retention_days || ' days')::INTERVAL;
    GET DIAGNOSTICS rate_limit_deleted = ROW_COUNT;

    -- Delete old query logs
    DELETE FROM query_logs
    WHERE timestamp < NOW() - (retention_days || ' days')::INTERVAL;
    GET DIAGNOSTICS query_log_deleted = ROW_COUNT;

    RETURN QUERY SELECT rate_limit_deleted, query_log_deleted;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION cleanup_old_analytics IS 'Remove analytics data older than specified retention period (default 90 days)';


-- ============================================================================
-- Grant Permissions
-- ============================================================================

-- Grant read/write access to application user
-- GRANT SELECT, INSERT, UPDATE ON rate_limit_analytics TO app_user;
-- GRANT SELECT, INSERT, UPDATE ON query_logs TO app_user;
-- GRANT SELECT, INSERT, UPDATE ON cache_analysis_daily TO app_user;
-- GRANT SELECT ON v_latest_cache_analysis TO app_user;
-- GRANT SELECT ON v_rate_limit_violations_summary TO app_user;
-- GRANT SELECT ON v_top_cacheable_queries TO app_user;
-- GRANT EXECUTE ON FUNCTION calculate_cache_hit_potential TO app_user;
-- GRANT EXECUTE ON FUNCTION cleanup_old_analytics TO app_user;


-- ============================================================================
-- Verification Queries
-- ============================================================================

-- Verify tables created
SELECT
    table_name,
    (SELECT COUNT(*) FROM information_schema.columns WHERE table_name = t.table_name) AS column_count
FROM information_schema.tables t
WHERE table_schema = 'public'
    AND table_name IN ('rate_limit_analytics', 'query_logs', 'cache_analysis_daily')
ORDER BY table_name;

-- Verify indexes created
SELECT
    tablename,
    indexname
FROM pg_indexes
WHERE schemaname = 'public'
    AND tablename IN ('rate_limit_analytics', 'query_logs', 'cache_analysis_daily')
ORDER BY tablename, indexname;

-- Verify views created
SELECT
    viewname
FROM pg_views
WHERE schemaname = 'public'
    AND viewname LIKE 'v_%'
ORDER BY viewname;

-- Verify functions created
SELECT
    routine_name,
    routine_type
FROM information_schema.routines
WHERE routine_schema = 'public'
    AND routine_name IN ('calculate_cache_hit_potential', 'cleanup_old_analytics')
ORDER BY routine_name;
