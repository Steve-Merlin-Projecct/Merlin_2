---
title: "Prd Api Rate Limiting System"
type: api_spec
component: general
status: draft
tags: []
---

# Product Requirements Document: API Rate Limiting & Request Throttling System

**Version:** 1.0.0
**Created:** 2025-10-11
**Status:** Active
**Owner:** Steve Glen
**Project:** Automated Job Application System

---

## 1. Executive Summary

### 1.1 Purpose
Implement comprehensive API rate limiting and request throttling to protect the job application system from abuse, control costs (Gemini AI, Apify), and provide visibility into system resource usage and database optimization opportunities.

### 1.2 Goals
1. **Cost Protection**: Prevent runaway AI/scraping costs through strict endpoint-specific rate limits
2. **Resource Monitoring**: Track memory usage of rate limiting storage and identify database optimization opportunities
3. **Security Enhancement**: Protect all API endpoints with appropriate rate limits
4. **Observability**: Provide real-time metrics on rate limiting effectiveness and cache hit potential

### 1.3 Non-Goals
- Distributed rate limiting (Redis/Valkey) - using in-memory for simplicity
- Real-time user-facing dashboards (batch analytics sufficient)
- WAF/DDoS protection (handled by DigitalOcean)

---

## 2. Background & Context

### 2.1 Current State
- **Inconsistent Protection**: Only 3 of ~30 API endpoints have rate limiting
- **Multiple Implementations**: Custom decorators in different modules (link_tracking, ai_integration)
- **No Monitoring**: Zero visibility into rate limit hits, memory usage, or optimization opportunities
- **Cost Exposure**: AI analysis and scraping endpoints can be abused, leading to unexpected bills

### 2.2 Key Constraints
- **Single User System**: Only Steve Glen uses the system (simplifies authentication)
- **Latency Tolerant**: Not user-facing, 50-100ms latency acceptable
- **Cost Sensitive**: Using external APIs (Gemini AI ~$0.001/request, Apify ~$0.10-$0.50/scrape)
- **Infrastructure**: Deploying to DigitalOcean App Platform with Supabase PostgreSQL

### 2.3 Success Metrics
- ✅ 100% of API endpoints protected with appropriate rate limits
- ✅ <50MB memory usage for rate limiting storage
- ✅ Zero cost overruns from API abuse
- ✅ Identify ≥20% database queries that could benefit from caching

---

## 3. Requirements

### 3.1 Functional Requirements

#### FR-1: Centralized Rate Limiting System
**Priority:** P0 (Critical)
- **FR-1.1**: Install and configure Flask-Limiter with in-memory storage
- **FR-1.2**: Define endpoint-specific rate limit tiers (expensive, moderate, cheap operations)
- **FR-1.3**: Create reusable decorators for common rate limit patterns
- **FR-1.4**: Implement graceful degradation (fail closed on errors)

#### FR-2: Endpoint Protection
**Priority:** P0 (Critical)
- **FR-2.1**: Protect AI analysis endpoints (10 req/min, 50/hour)
- **FR-2.2**: Protect scraping endpoints (5 req/hour, 20/day)
- **FR-2.3**: Protect document generation endpoints (20 req/min)
- **FR-2.4**: Protect email sending endpoints (10 req/min, 100/hour)
- **FR-2.5**: Protect database write operations (50 req/min)
- **FR-2.6**: Apply default limits to all unprotected endpoints (100 req/min)

#### FR-3: Memory Usage Monitoring
**Priority:** P0 (Critical)
- **FR-3.1**: Track in-memory rate limit storage size (MB)
- **FR-3.2**: Count active rate limit keys (unique IPs/users tracked)
- **FR-3.3**: Monitor key expiration and cleanup effectiveness
- **FR-3.4**: Alert when memory usage exceeds 50MB threshold
- **FR-3.5**: Expose metrics via `/api/rate-limit/metrics` endpoint

#### FR-4: Database Optimization Analysis
**Priority:** P1 (High)
- **FR-4.1**: Log all database queries with timestamp, endpoint, query hash
- **FR-4.2**: Identify repeated queries (same query within 5-minute window)
- **FR-4.3**: Calculate cache hit potential (% of queries that are duplicates)
- **FR-4.4**: Generate daily report showing top 10 cacheable queries
- **FR-4.5**: Estimate cost savings from implementing Redis cache

#### FR-5: Rate Limit Analytics
**Priority:** P1 (High)
- **FR-5.1**: Log all rate limit violations (endpoint, IP, timestamp, limit exceeded)
- **FR-5.2**: Track rate limit hit rate by endpoint
- **FR-5.3**: Calculate "breathing room" (actual usage vs limit)
- **FR-5.4**: Generate weekly summary reports
- **FR-5.5**: Store analytics in `rate_limit_analytics` database table

### 3.2 Non-Functional Requirements

#### NFR-1: Performance
- Rate limit check overhead: <5ms per request
- Memory usage: <50MB for rate limiting storage
- No impact on existing endpoint response times

#### NFR-2: Reliability
- 99.9% uptime for rate limiting system
- Graceful degradation if rate limiter fails (fail closed)
- Automatic cleanup of expired keys every 60 seconds

#### NFR-3: Security
- Rate limits cannot be bypassed via header manipulation
- IP detection handles proxies (X-Forwarded-For)
- Session-based limits for authenticated users

#### NFR-4: Maintainability
- Centralized configuration in `modules/security/rate_limit_config.py`
- Clear documentation for adding rate limits to new endpoints
- Automated tests for rate limiting logic

---

## 4. Technical Design

### 4.1 Architecture Overview

```
┌─────────────────────────────────────────────────────┐
│  Flask Application (app_modular.py)                 │
│  ┌───────────────────────────────────────────────┐  │
│  │  Flask-Limiter (In-Memory Storage)            │  │
│  │  - Fixed window strategy                      │  │
│  │  - Per-IP + Per-User key functions           │  │
│  │  - Automatic cleanup every 60s               │  │
│  └───────────────────────────────────────────────┘  │
│                         │                            │
│  ┌─────────────────────┼──────────────────────────┐ │
│  │  Rate Limit Middleware                        │ │
│  │  - Check limits before request               │ │
│  │  - Log violations                            │ │
│  │  - Add headers to response                   │ │
│  └───────────────────────────────────────────────┘ │
│                         │                            │
│  ┌─────────────────────┼──────────────────────────┐ │
│  │  Monitoring Module (rate_limit_monitor.py)   │ │
│  │  - Memory usage tracker                      │ │
│  │  - Query logger & analyzer                   │ │
│  │  - Cache hit calculator                      │ │
│  └───────────────────────────────────────────────┘ │
│                         │                            │
│  ┌─────────────────────┼──────────────────────────┐ │
│  │  Analytics API (/api/rate-limit/*)           │ │
│  │  - /metrics - Real-time metrics              │ │
│  │  - /analytics - Historical data              │ │
│  │  - /cache-analysis - Optimization report     │ │
│  └───────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────┘
                         │
                         ▼
          ┌──────────────────────────┐
          │  PostgreSQL (Supabase)   │
          │  - rate_limit_analytics  │
          │  - query_logs            │
          │  - cache_analysis_daily  │
          └──────────────────────────┘
```

### 4.2 Database Schema

```sql
-- Rate limit violation tracking
CREATE TABLE rate_limit_analytics (
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
    request_method VARCHAR(10)
);

CREATE INDEX idx_rate_limit_timestamp ON rate_limit_analytics(timestamp);
CREATE INDEX idx_rate_limit_endpoint ON rate_limit_analytics(endpoint);

-- Query logging for cache analysis
CREATE TABLE query_logs (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL DEFAULT NOW(),
    endpoint VARCHAR(255) NOT NULL,
    query_hash VARCHAR(64) NOT NULL,
    query_template TEXT,
    execution_time_ms FLOAT,
    result_size_bytes INTEGER,
    client_ip VARCHAR(45)
);

CREATE INDEX idx_query_hash ON query_logs(query_hash, timestamp);
CREATE INDEX idx_query_timestamp ON query_logs(timestamp);

-- Daily cache analysis reports
CREATE TABLE cache_analysis_daily (
    id SERIAL PRIMARY KEY,
    analysis_date DATE NOT NULL UNIQUE,
    total_queries INTEGER,
    unique_queries INTEGER,
    duplicate_queries INTEGER,
    cache_hit_potential_percent FLOAT,
    top_cacheable_queries JSONB,
    estimated_latency_savings_ms INTEGER,
    memory_required_mb FLOAT,
    recommended_ttl_seconds INTEGER,
    generated_at TIMESTAMP DEFAULT NOW()
);
```

### 4.3 Rate Limit Configuration

```python
# modules/security/rate_limit_config.py

RATE_LIMIT_TIERS = {
    # Expensive operations (protect costs)
    "expensive": {
        "ai_analysis": "10/minute;50/hour;200/day",
        "job_scraping": "5/hour;20/day",
        "batch_ai_processing": "5/minute;20/hour",
    },

    # Moderate operations
    "moderate": {
        "document_generation": "20/minute;200/hour",
        "email_send": "10/minute;100/hour",
        "db_write": "50/minute;500/hour",
    },

    # Cheap operations
    "cheap": {
        "db_read": "200/minute",
        "dashboard": "500/minute",
        "analytics": "100/minute",
    },

    # Default for unspecified endpoints
    "default": "100/minute",
}

# Memory management
CLEANUP_INTERVAL_SECONDS = 60
MAX_MEMORY_MB = 50
ALERT_THRESHOLD_MB = 40

# Analytics
ENABLE_QUERY_LOGGING = True
QUERY_LOG_SAMPLE_RATE = 1.0  # Log 100% of queries
CACHE_ANALYSIS_LOOKBACK_MINUTES = 1440  # 24 hours
```

### 4.4 Key Components

#### Component 1: Rate Limit Manager
**Location:** `modules/security/rate_limit_manager.py`
**Responsibilities:**
- Initialize Flask-Limiter
- Provide decorator functions
- Handle rate limit breaches
- Cleanup expired keys

#### Component 2: Memory Monitor
**Location:** `modules/security/rate_limit_monitor.py`
**Responsibilities:**
- Track storage size
- Count active keys
- Calculate memory usage
- Trigger alerts

#### Component 3: Query Analyzer
**Location:** `modules/analytics/query_analyzer.py`
**Responsibilities:**
- Log database queries
- Hash queries for deduplication
- Identify repeat patterns
- Calculate cache hit potential

#### Component 4: Analytics API
**Location:** `modules/security/rate_limit_analytics_api.py`
**Responsibilities:**
- Expose real-time metrics
- Generate reports
- Provide cache analysis
- Dashboard integration

---

## 5. Implementation Plan

### Phase 1: Foundation (Week 1)
- Install Flask-Limiter
- Create centralized configuration
- Implement basic rate limiting
- Add memory monitoring

### Phase 2: Endpoint Protection (Week 1-2)
- Apply rate limits to all endpoints
- Test with actual usage patterns
- Tune limits based on data

### Phase 3: Analytics & Monitoring (Week 2-3)
- Implement query logging
- Build cache analysis engine
- Create analytics API endpoints
- Generate daily reports

### Phase 4: Integration & Documentation (Week 3-4)
- Dashboard integration
- Comprehensive testing
- Documentation updates
- Deployment to DigitalOcean

---

## 6. Testing Strategy

### 6.1 Unit Tests
- Rate limit decorator functionality
- Memory usage calculations
- Query hash generation
- Cache hit percentage calculations

### 6.2 Integration Tests
- End-to-end rate limiting with Flask app
- Database logging under load
- Analytics API responses
- Memory cleanup effectiveness

### 6.3 Load Tests
- 1000 requests/minute sustained
- Memory usage under load
- Performance impact measurement

---

## 7. Monitoring & Alerts

### 7.1 Key Metrics
- Rate limit hit rate by endpoint
- Memory usage (current, peak, average)
- Cache hit potential percentage
- Query deduplication ratio

### 7.2 Alerts
- Memory usage >40MB (warning), >50MB (critical)
- Rate limit hit rate >10% (investigate usage patterns)
- Cache hit potential >50% (consider Redis investment)

---

## 8. Success Criteria

### 8.1 Must Have
- ✅ All API endpoints protected
- ✅ Zero cost overruns from abuse
- ✅ Memory usage <50MB
- ✅ Real-time metrics available

### 8.2 Should Have
- ✅ Daily cache analysis reports
- ✅ Automated alerts for anomalies
- ✅ Dashboard integration

### 8.3 Nice to Have
- ⭕ Historical trend analysis
- ⭕ Predictive cost modeling
- ⭕ Automated cache implementation recommendations

---

## 9. Risks & Mitigations

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Memory leak in storage | High | Low | Automated cleanup + monitoring |
| Rate limits too strict | Medium | Medium | Start generous, tune based on data |
| Performance degradation | Medium | Low | <5ms overhead requirement |
| False positives (legitimate use blocked) | Low | Low | Single user system reduces risk |

---

## 10. Appendix

### 10.1 Related Documents
- `docs/component_docs/security/security_implementation_guide.md`
- `modules/security/security_config.py`
- `modules/link_tracking/security_controls.py`

### 10.2 References
- Flask-Limiter Documentation: https://flask-limiter.readthedocs.io/
- DigitalOcean App Platform Limits: https://docs.digitalocean.com/products/app-platform/details/limits/
- Rate Limiting Strategies: https://redis.io/glossary/rate-limiting/

### 10.3 Changelog
- 2025-10-11: Initial PRD creation
