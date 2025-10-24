---
title: "Task Api Rate Limiting Implementation"
type: api_spec
component: general
status: draft
tags: []
---

# Task Breakdown: API Rate Limiting & Request Throttling System

**PRD Reference:** `prd-api-rate-limiting-system.md`
**Version:** 1.0.0
**Created:** 2025-10-11

---

## Task 1: Foundation - Install and Configure Flask-Limiter

**Priority:** P0 (Critical)
**Estimated Time:** 2 hours
**Dependencies:** None

### Subtask 1.1: Add Flask-Limiter to Dependencies
- [ ] Add `Flask-Limiter>=3.5.0` to `requirements.txt`
- [ ] Document version rationale in changelog
- [ ] Verify no conflicts with existing dependencies

### Subtask 1.2: Create Rate Limit Configuration Module
- [ ] Create `modules/security/rate_limit_config.py`
- [ ] Define rate limit tiers (expensive, moderate, cheap, default)
- [ ] Define memory management settings
- [ ] Define analytics settings
- [ ] Add comprehensive docstrings

### Subtask 1.3: Create Rate Limit Manager Module
- [ ] Create `modules/security/rate_limit_manager.py`
- [ ] Initialize Flask-Limiter with in-memory storage
- [ ] Implement key function (per-IP + per-user hybrid)
- [ ] Configure fixed-window strategy
- [ ] Add error handlers for rate limit breaches
- [ ] Implement graceful degradation (fail closed)

### Subtask 1.4: Integrate with Main Application
- [ ] Import rate limiter in `app_modular.py`
- [ ] Initialize limiter with Flask app
- [ ] Apply default rate limit globally
- [ ] Test basic functionality with health check endpoint

**Acceptance Criteria:**
- ✅ Flask-Limiter installed and imported successfully
- ✅ Basic rate limiting works on test endpoint
- ✅ Rate limit headers appear in responses
- ✅ Configuration is centralized and documented

---

## Task 2: Endpoint Protection - Apply Rate Limits

**Priority:** P0 (Critical)
**Estimated Time:** 4 hours
**Dependencies:** Task 1

### Subtask 2.1: Protect Expensive Operations (AI & Scraping)
- [ ] Apply limits to `/api/ai/analyze-jobs` (10/min, 50/hour)
- [ ] Apply limits to `/api/ai/analysis-results/*` (10/min)
- [ ] Apply limits to `/api/scrape` endpoints (5/hour, 20/day)
- [ ] Apply limits to `/api/intelligent-scrape` (5/hour)
- [ ] Apply limits to batch AI endpoints (5/min, 20/hour)
- [ ] Test each endpoint exceeds limit correctly

### Subtask 2.2: Protect Moderate Operations (Documents & Email)
- [ ] Apply limits to document generation routes (20/min, 200/hour)
- [ ] Apply limits to email send endpoints (10/min, 100/hour)
- [ ] Apply limits to database write operations (50/min, 500/hour)
- [ ] Apply limits to workflow orchestration (20/min)
- [ ] Test each endpoint with various load patterns

### Subtask 2.3: Protect Cheap Operations (Reads & Dashboard)
- [ ] Apply limits to database read endpoints (200/min)
- [ ] Apply limits to dashboard endpoints (500/min)
- [ ] Apply limits to analytics endpoints (100/min)
- [ ] Ensure health check endpoint is exempt from limits

### Subtask 2.4: Audit All Endpoints for Coverage
- [ ] Generate list of all registered routes
- [ ] Identify endpoints without explicit limits
- [ ] Apply default limit (100/min) to remaining endpoints
- [ ] Create coverage report (% of endpoints protected)
- [ ] Document rate limit strategy for each endpoint category

**Acceptance Criteria:**
- ✅ 100% of API endpoints have rate limits applied
- ✅ Expensive operations have strictest limits
- ✅ Rate limit violations return 429 status with retry-after header
- ✅ Health check endpoint remains unrestricted

---

## Task 3: Memory Monitoring - Track Storage Usage

**Priority:** P0 (Critical)
**Estimated Time:** 3 hours
**Dependencies:** Task 1

### Subtask 3.1: Create Memory Monitor Module
- [ ] Create `modules/security/rate_limit_monitor.py`
- [ ] Implement `get_storage_size()` - calculate memory usage in bytes
- [ ] Implement `get_active_keys()` - count unique rate limit keys
- [ ] Implement `get_key_distribution()` - breakdown by endpoint/user
- [ ] Implement `check_memory_health()` - compare against thresholds

### Subtask 3.2: Implement Automatic Cleanup
- [ ] Create background thread for expired key cleanup
- [ ] Run cleanup every 60 seconds
- [ ] Log cleanup statistics (keys removed, memory freed)
- [ ] Ensure thread-safe access to storage
- [ ] Add shutdown hook for graceful cleanup thread termination

### Subtask 3.3: Add Memory Metrics to Logging
- [ ] Log memory usage on application startup
- [ ] Log memory usage after each cleanup cycle
- [ ] Log warning when usage exceeds 40MB
- [ ] Log critical alert when usage exceeds 50MB
- [ ] Include key count and distribution in logs

### Subtask 3.4: Create Metrics API Endpoint
- [ ] Create `/api/rate-limit/metrics` endpoint
- [ ] Return current memory usage (bytes, MB, percentage of limit)
- [ ] Return active key count
- [ ] Return key distribution by endpoint
- [ ] Return cleanup cycle statistics
- [ ] Require authentication for access

**Acceptance Criteria:**
- ✅ Memory usage tracked in real-time
- ✅ Cleanup runs automatically every 60 seconds
- ✅ Alerts trigger at 40MB and 50MB thresholds
- ✅ Metrics API provides comprehensive memory stats

---

## Task 4: Database Schema - Create Analytics Tables

**Priority:** P1 (High)
**Estimated Time:** 2 hours
**Dependencies:** None (can run parallel to Tasks 1-3)

### Subtask 4.1: Create Rate Limit Analytics Table
- [ ] Write SQL migration for `rate_limit_analytics` table
- [ ] Add indexes for timestamp and endpoint columns
- [ ] Document table schema in database docs
- [ ] Test INSERT performance (should be <5ms)

### Subtask 4.2: Create Query Logs Table
- [ ] Write SQL migration for `query_logs` table
- [ ] Add indexes for query_hash and timestamp
- [ ] Implement partitioning strategy for large dataset
- [ ] Document query logging format

### Subtask 4.3: Create Cache Analysis Table
- [ ] Write SQL migration for `cache_analysis_daily` table
- [ ] Add unique constraint on analysis_date
- [ ] Create view for latest analysis results
- [ ] Document analysis metrics

### Subtask 4.4: Run Migrations and Verify
- [ ] Execute all migrations on development database
- [ ] Verify table structures with `\d+` commands
- [ ] Run automated database schema update tool
- [ ] Commit generated schema documentation

**Acceptance Criteria:**
- ✅ All three tables created successfully
- ✅ Indexes created for optimal query performance
- ✅ Schema documentation auto-generated
- ✅ INSERT operations perform within SLA (<5ms)

---

## Task 5: Rate Limit Analytics - Track Violations

**Priority:** P1 (High)
**Estimated Time:** 3 hours
**Dependencies:** Task 1, Task 4

### Subtask 5.1: Implement Violation Logger
- [ ] Create `log_rate_limit_violation()` function
- [ ] Capture endpoint, client_ip, user_id, limit exceeded
- [ ] Store current count and limit value
- [ ] Include user-agent and request method
- [ ] Batch writes to database (every 10 violations or 60 seconds)

### Subtask 5.2: Hook into Flask-Limiter Error Handler
- [ ] Override default rate limit handler
- [ ] Call violation logger on 429 responses
- [ ] Include rate limit details in response headers
- [ ] Add `Retry-After` header with seconds until reset
- [ ] Log to both database and application logs

### Subtask 5.3: Create Analytics Query Functions
- [ ] `get_violations_by_endpoint(start_date, end_date)`
- [ ] `get_violations_by_ip(start_date, end_date)`
- [ ] `calculate_hit_rate_by_endpoint()` - % of requests that hit limit
- [ ] `calculate_breathing_room()` - actual usage vs limit
- [ ] Add SQL optimization for date range queries

### Subtask 5.4: Create Analytics API Endpoint
- [ ] Create `/api/rate-limit/analytics` endpoint
- [ ] Support query parameters: date_range, endpoint, group_by
- [ ] Return violation counts, hit rates, breathing room
- [ ] Include top offending IPs and endpoints
- [ ] Require authentication

**Acceptance Criteria:**
- ✅ All rate limit violations logged to database
- ✅ No performance impact from logging (<1ms overhead)
- ✅ Analytics API returns actionable insights
- ✅ Data persists across application restarts

---

## Task 6: Query Analyzer - Database Optimization Tracking

**Priority:** P1 (High)
**Estimated Time:** 4 hours
**Dependencies:** Task 4

### Subtask 6.1: Create Query Analyzer Module
- [ ] Create `modules/analytics/query_analyzer.py`
- [ ] Implement `hash_query()` - normalize and hash SQL queries
- [ ] Implement `log_query()` - record query execution
- [ ] Implement `detect_duplicates()` - find repeated queries
- [ ] Add sampling logic (configurable sample rate)

### Subtask 6.2: Integrate with Database Manager
- [ ] Hook into DatabaseManager.execute_query()
- [ ] Capture query template, execution time, result size
- [ ] Hash query for deduplication
- [ ] Log to query_logs table asynchronously
- [ ] Ensure zero impact on query performance (<1ms overhead)

### Subtask 6.3: Build Cache Hit Analyzer
- [ ] Implement `analyze_cache_potential()` function
- [ ] Group queries by hash within time windows
- [ ] Calculate duplicate query percentage
- [ ] Identify top 10 most repeated queries
- [ ] Estimate latency savings from caching
- [ ] Calculate recommended TTL based on query patterns

### Subtask 6.4: Create Daily Analysis Job
- [ ] Create `generate_daily_cache_report()` function
- [ ] Analyze last 24 hours of query logs
- [ ] Calculate total queries, unique queries, duplicates
- [ ] Store results in `cache_analysis_daily` table
- [ ] Schedule to run at midnight via cron or scheduler
- [ ] Send summary email to admin

**Acceptance Criteria:**
- ✅ All database queries logged with <1ms overhead
- ✅ Query deduplication accurate (hash collisions <0.1%)
- ✅ Daily cache analysis report generated automatically
- ✅ Report identifies ≥20% duplicate queries (if exists)

---

## Task 7: Cache Analysis API - Expose Optimization Insights

**Priority:** P1 (High)
**Estimated Time:** 2 hours
**Dependencies:** Task 6

### Subtask 7.1: Create Cache Analysis Endpoint
- [ ] Create `/api/rate-limit/cache-analysis` endpoint
- [ ] Return latest daily analysis results
- [ ] Support date range queries for historical trends
- [ ] Include cache hit potential percentage
- [ ] Show top cacheable queries with frequency
- [ ] Estimate memory requirements for Redis cache

### Subtask 7.2: Create Cost Savings Calculator
- [ ] Implement `calculate_redis_cost_benefit()` function
- [ ] Estimate latency savings (ms/day)
- [ ] Calculate query load reduction (%)
- [ ] Compare Redis cost vs latency savings value
- [ ] Recommend if caching is worthwhile
- [ ] Include break-even analysis

### Subtask 7.3: Create Visualization Data Format
- [ ] Format data for dashboard charts
- [ ] Time series of cache hit potential
- [ ] Top 10 cacheable queries bar chart
- [ ] Cost-benefit comparison table
- [ ] Export as JSON for frontend consumption

**Acceptance Criteria:**
- ✅ API returns actionable cache optimization data
- ✅ Cost-benefit analysis helps decision making
- ✅ Data formatted for easy dashboard integration
- ✅ Historical trends available for analysis

---

## Task 8: Integration & Testing

**Priority:** P0 (Critical)
**Estimated Time:** 4 hours
**Dependencies:** Tasks 1-7

### Subtask 8.1: Write Unit Tests
- [ ] Test rate limit decorators (hit limit, under limit, reset)
- [ ] Test memory monitoring calculations
- [ ] Test query hashing (same query = same hash)
- [ ] Test cache hit percentage calculations
- [ ] Test key expiration and cleanup
- [ ] Achieve ≥80% code coverage

### Subtask 8.2: Write Integration Tests
- [ ] Test end-to-end rate limiting on sample endpoints
- [ ] Test memory cleanup under sustained load
- [ ] Test analytics logging and retrieval
- [ ] Test cache analysis report generation
- [ ] Test fail-closed behavior on errors

### Subtask 8.3: Perform Load Testing
- [ ] Generate 1000 requests/minute to various endpoints
- [ ] Measure memory usage under load
- [ ] Verify cleanup effectiveness
- [ ] Measure performance overhead (<5ms per request)
- [ ] Document load test results

### Subtask 8.4: Security Testing
- [ ] Attempt to bypass rate limits via header manipulation
- [ ] Test with multiple IPs/user agents
- [ ] Verify fail-closed behavior
- [ ] Test for memory exhaustion attacks
- [ ] Document security findings

**Acceptance Criteria:**
- ✅ All tests pass with ≥80% coverage
- ✅ System performs within SLAs under load
- ✅ No security vulnerabilities identified
- ✅ Memory usage stays below 50MB threshold

---

## Task 9: Documentation & Deployment

**Priority:** P0 (Critical)
**Estimated Time:** 3 hours
**Dependencies:** Task 8

### Subtask 9.1: Update System Documentation
- [ ] Document rate limiting architecture in `docs/architecture/`
- [ ] Update API documentation with rate limit details
- [ ] Add rate limit headers documentation
- [ ] Document memory monitoring and alerts
- [ ] Update security implementation guide

### Subtask 9.2: Create Developer Guide
- [ ] Write guide: "Adding Rate Limits to New Endpoints"
- [ ] Document rate limit tier selection criteria
- [ ] Provide code examples and templates
- [ ] Explain monitoring and analytics
- [ ] Add troubleshooting section

### Subtask 9.3: Create Operations Guide
- [ ] Document memory monitoring procedures
- [ ] Explain alert thresholds and responses
- [ ] Provide cache analysis interpretation guide
- [ ] Document when to upgrade to Redis/Valkey
- [ ] Include performance tuning tips

### Subtask 9.4: Update CLAUDE.md
- [ ] Add rate limiting policy to CLAUDE.md
- [ ] Document that all new endpoints must have rate limits
- [ ] Reference centralized configuration
- [ ] Explain monitoring requirements
- [ ] Update changelog

### Subtask 9.5: Deploy to Development Environment
- [ ] Install dependencies on development server
- [ ] Run database migrations
- [ ] Verify rate limiting works
- [ ] Test monitoring endpoints
- [ ] Generate initial cache analysis report

### Subtask 9.6: Prepare for Production Deployment
- [ ] Create deployment checklist
- [ ] Document rollback procedure
- [ ] Set up monitoring alerts in production
- [ ] Schedule daily cache analysis job
- [ ] Brief user (Steve Glen) on new rate limits

**Acceptance Criteria:**
- ✅ Comprehensive documentation available
- ✅ Development environment fully operational
- ✅ Production deployment plan ready
- ✅ Monitoring and alerts configured

---

## Task 10: Dashboard Integration (Optional Enhancement)

**Priority:** P2 (Nice to Have)
**Estimated Time:** 3 hours
**Dependencies:** Task 7, Task 9

### Subtask 10.1: Add Rate Limit Metrics to Dashboard
- [ ] Create dashboard widget for memory usage
- [ ] Display current rate limit status by endpoint
- [ ] Show recent violations (last 24 hours)
- [ ] Add gauge for cache hit potential

### Subtask 10.2: Add Cache Analysis Visualization
- [ ] Create chart: Cache hit potential over time
- [ ] Create table: Top 10 cacheable queries
- [ ] Create cost-benefit comparison widget
- [ ] Add recommendation indicator (use Redis Y/N)

### Subtask 10.3: Add Real-Time Alerts
- [ ] Display memory usage alerts in dashboard
- [ ] Show rate limit violation alerts
- [ ] Highlight endpoints approaching limits
- [ ] Add dismiss/acknowledge functionality

**Acceptance Criteria:**
- ✅ Dashboard displays rate limiting metrics
- ✅ Cache analysis insights visible to user
- ✅ Real-time alerts integrated
- ✅ User can make informed decisions about Redis investment

---

## Summary

**Total Tasks:** 10
**Total Subtasks:** 53
**Estimated Total Time:** 26-30 hours
**Critical Path:** Tasks 1 → 2 → 8 → 9 (13 hours minimum)

**Implementation Order:**
1. Task 1 (Foundation) - 2 hours
2. Task 4 (Database Schema) - 2 hours [parallel]
3. Task 2 (Endpoint Protection) - 4 hours
4. Task 3 (Memory Monitoring) - 3 hours [parallel]
5. Task 5 (Rate Limit Analytics) - 3 hours
6. Task 6 (Query Analyzer) - 4 hours
7. Task 7 (Cache Analysis API) - 2 hours
8. Task 8 (Integration & Testing) - 4 hours
9. Task 9 (Documentation & Deployment) - 3 hours
10. Task 10 (Dashboard Integration) - 3 hours [optional]

**Next Step:** Begin implementation with Task 1, Subtask 1.1
