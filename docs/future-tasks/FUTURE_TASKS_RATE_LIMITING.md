# Future Tasks - Rate Limiting System

**Created:** 2025-10-11
**Status:** Deferred
**Priority:** Medium

---

## Overview

These tasks were identified during the rate limiting implementation but deferred as non-critical. They can be completed during future maintenance windows without breaking existing functionality.

---

## Task 1: Complete Endpoint Coverage (15% Remaining)

**Priority:** Medium
**Estimated Time:** 2 hours
**Status:** Deferred

### Description
Apply rate limits to remaining unprotected endpoints.

### Endpoints to Protect

**Database API (Cheap tier - 200/min):**
- `GET /api/db/jobs/<job_id>` - Get specific job details
- `GET /api/db/statistics` - Get job statistics
- `GET /api/db/settings` - Get application settings
- `GET /api/db/jobs/<job_id>/logs` - Get job logs

**Email API (Moderate tier - 10/min; 100/hour):**
- `POST /api/email/send-job-application` - Send job application email
- `POST /api/email/test` - Send test email

**Main App Endpoints:**
- `POST /api/process-scrapes` - Process raw scrapes (Moderate tier)
- `POST /api/intelligent-scrape` - Intelligent scraping (Expensive tier)
- `GET /api/pipeline-stats` - Pipeline statistics (Cheap tier)

### Implementation Steps

1. Import rate limit decorators in each module:
   ```python
   from modules.security.rate_limit_manager import rate_limit_cheap, rate_limit_moderate, rate_limit_expensive
   ```

2. Apply appropriate decorator to each endpoint:
   ```python
   @database_bp.route("/jobs/<job_id>", methods=["GET"])
   @rate_limit_cheap
   def get_job(job_id):
       ...
   ```

3. Test each endpoint to verify rate limiting works
4. Update `IMPLEMENTATION_SUMMARY_RATE_LIMITING.md` to reflect 100% coverage

### Acceptance Criteria
- ✅ All remaining endpoints have rate limit decorators applied
- ✅ Appropriate tier assigned based on cost/resource usage
- ✅ Tests verify rate limiting works correctly
- ✅ Documentation updated to show 100% coverage

---

## Task 2: Query Analyzer Module (Optional)

**Priority:** Low
**Estimated Time:** 3 hours
**Status:** Deferred

### Description
Implement automatic query analyzer that logs database queries and provides cache recommendations.

### Why It's Optional
- Analytics API can already calculate cache hit potential on-the-fly
- Database schema is ready (query_logs table exists)
- Can be added later without breaking changes

### Implementation Plan

**File:** `modules/analytics/query_analyzer.py`

**Features to Implement:**
1. **Query Hashing**
   - Normalize SQL queries (remove parameters, whitespace)
   - Generate SHA-256 hash for deduplication
   - Handle prepared statements

2. **Query Logging**
   - Hook into DatabaseManager.execute_query()
   - Capture: query template, execution time, result size
   - Log to query_logs table asynchronously
   - Implement sampling (configurable sample rate)

3. **Duplicate Detection**
   - Group queries by hash within time windows
   - Calculate duplicate query percentage
   - Identify top 10 most repeated queries

4. **Cache Recommendations**
   - Estimate latency savings from caching
   - Calculate recommended TTL based on query patterns
   - Estimate Redis memory requirements
   - Generate cost-benefit analysis

**Integration:**
```python
# In modules/database/database_manager.py
from modules.analytics.query_analyzer import QueryAnalyzer

class DatabaseManager:
    def __init__(self):
        self.query_analyzer = QueryAnalyzer()

    def execute_query(self, query, params=None):
        # Execute query
        result = self.cursor.execute(query, params)

        # Log query asynchronously
        if config.ENABLE_QUERY_LOGGING:
            self.query_analyzer.log_query(query, params, execution_time, len(result))

        return result
```

### Acceptance Criteria
- ✅ All database queries logged to query_logs table
- ✅ Query deduplication accurate (<0.1% hash collisions)
- ✅ Cache recommendations generated automatically
- ✅ Performance overhead <1ms per query
- ✅ Daily cache analysis report generated

---

## Task 3: Integration Testing

**Priority:** Medium
**Estimated Time:** 2 hours
**Status:** Deferred

### Description
Create comprehensive integration tests for the rate limiting system.

### Test Cases to Implement

**File:** `tests/test_rate_limiting.py`

**1. Rate Limit Enforcement Tests**
```python
def test_rate_limit_expensive_endpoint():
    """Test that expensive endpoint respects 10/min limit"""
    # Send 10 requests - should all succeed
    # Send 11th request - should get 429
    # Wait 60 seconds - should succeed again

def test_rate_limit_headers():
    """Test that rate limit headers are present"""
    # Check X-RateLimit-Limit
    # Check X-RateLimit-Remaining
    # Check X-RateLimit-Reset
    # Verify headers update correctly

def test_rate_limit_different_tiers():
    """Test that different tiers have different limits"""
    # Test expensive endpoint (10/min)
    # Test moderate endpoint (20/min)
    # Test cheap endpoint (200/min)
    # Verify limits are enforced correctly
```

**2. Memory Monitoring Tests**
```python
def test_memory_usage_tracking():
    """Test that memory usage is tracked correctly"""
    # Get initial memory usage
    # Generate traffic
    # Verify memory increases
    # Verify cleanup reduces memory

def test_memory_alerts():
    """Test that memory alerts trigger correctly"""
    # Fill storage to 40MB (warning)
    # Verify warning logged
    # Fill to 45MB (critical)
    # Verify critical alert logged

def test_cleanup_effectiveness():
    """Test that cleanup removes expired keys"""
    # Create keys
    # Wait for expiration
    # Trigger cleanup
    # Verify keys removed
```

**3. Analytics Tests**
```python
def test_violation_logging():
    """Test that violations are logged to database"""
    # Trigger rate limit
    # Verify entry in rate_limit_analytics table
    # Check all fields populated correctly

def test_cache_analysis():
    """Test cache hit potential calculation"""
    # Execute duplicate queries
    # Calculate cache potential
    # Verify percentage correct

def test_metrics_api():
    """Test that metrics API returns correct data"""
    # Call /api/rate-limit/metrics
    # Verify structure
    # Verify values reasonable
```

**4. Authentication Integration Tests**
```python
def test_authenticated_user_keying():
    """Test that authenticated users use user-based keys"""
    # Login as user
    # Make requests
    # Verify key is user:steve_glen

def test_unauthenticated_ip_keying():
    """Test that unauthenticated requests use IP-based keys"""
    # Make requests without auth
    # Verify key is ip:127.0.0.1

def test_proxy_header_support():
    """Test that proxy headers are respected"""
    # Send requests with X-Forwarded-For
    # Verify IP extracted correctly
    # Test Cloudflare headers
```

### Running Tests
```bash
pytest tests/test_rate_limiting.py -v
pytest tests/test_rate_limiting.py::test_rate_limit_enforcement -v
```

### Acceptance Criteria
- ✅ All test cases pass
- ✅ Code coverage ≥80% for rate limiting modules
- ✅ Tests run in <30 seconds
- ✅ Tests can run in parallel
- ✅ CI/CD integration ready

---

## Task 4: Dashboard Integration

**Priority:** Low
**Estimated Time:** 3 hours
**Status:** Deferred

### Description
Integrate rate limiting metrics into the existing dashboard UI.

### Features to Add

**1. Rate Limit Metrics Widget** (`frontend_templates/dashboard_v2.html`)

Add widget showing:
- Current memory usage (gauge chart)
- Active rate limit keys count
- Recent violations (last 24 hours)
- Health status indicator

**HTML Structure:**
```html
<div class="rate-limit-widget">
  <h3>Rate Limiting Status</h3>

  <div class="memory-gauge">
    <canvas id="memoryGaugeChart"></canvas>
    <p>Memory: <span id="memory-usage">0</span> MB / 50 MB</p>
  </div>

  <div class="stats">
    <div class="stat">
      <label>Active Keys:</label>
      <span id="active-keys">0</span>
    </div>
    <div class="stat">
      <label>Violations (24h):</label>
      <span id="violations-24h">0</span>
    </div>
    <div class="stat">
      <label>Health:</label>
      <span id="health-status" class="badge">Healthy</span>
    </div>
  </div>
</div>
```

**JavaScript (fetch metrics):**
```javascript
async function updateRateLimitMetrics() {
  const response = await fetch('/api/rate-limit/metrics');
  const data = await response.json();

  document.getElementById('memory-usage').textContent =
    data.metrics.memory.current_mb.toFixed(2);

  document.getElementById('active-keys').textContent =
    data.metrics.keys.total_active;

  updateHealthBadge(data.metrics.memory.status);

  // Update gauge chart
  updateMemoryGaugeChart(data.metrics.memory.utilization_percent);
}

// Update every 5 seconds
setInterval(updateRateLimitMetrics, 5000);
```

**2. Cache Analysis Visualization**

Add chart showing cache hit potential over time:
- Line chart: Cache hit potential % over last 7 days
- Table: Top 10 most cacheable queries
- Cost-benefit widget: Redis cost vs latency savings

**3. Violation Alerts**

Add notification system for rate limit violations:
- Toast notifications for memory alerts
- Badge showing violation count
- Click to view detailed violation log

**4. Configuration Panel**

Add read-only view of current rate limiting configuration:
- Rate limit tiers and values
- Memory limits and thresholds
- Enabled features (query logging, violation tracking)

### Files to Modify
- `frontend_templates/dashboard_v2.html` - Add widgets
- `static/js/dashboard.js` - Add JavaScript logic
- `static/css/dashboard.css` - Add styling

### Acceptance Criteria
- ✅ Dashboard displays real-time rate limit metrics
- ✅ Gauge chart updates automatically
- ✅ Cache analysis visualized clearly
- ✅ Violations trigger alerts in UI
- ✅ Mobile-responsive design

---

## Task 5: Redis/Valkey Migration Guide (Bonus)

**Priority:** Low
**Estimated Time:** 1 hour
**Status:** Future

### Description
Create detailed migration guide for upgrading from in-memory to Redis/Valkey storage.

### When to Upgrade
- Running multiple app instances (horizontal scaling)
- Need persistent rate limits across restarts
- Want distributed rate limiting

### Migration Steps

**File:** `docs/REDIS_MIGRATION_GUIDE.md`

**Content:**
1. When to upgrade (criteria)
2. DigitalOcean Managed Valkey setup
3. Environment variable configuration
4. Zero-downtime migration process
5. Verification steps
6. Rollback procedure
7. Performance comparison (in-memory vs Redis)
8. Cost analysis

---

## Implementation Priority

**Recommended Order:**

1. **Task 1: Complete Endpoint Coverage** (Medium Priority)
   - Provides 100% protection
   - Easy to implement (2 hours)
   - High value for completeness

2. **Task 3: Integration Testing** (Medium Priority)
   - Ensures system reliability
   - Prevents regressions
   - Required for production confidence

3. **Task 4: Dashboard Integration** (Low Priority)
   - Nice to have, not critical
   - Improves observability
   - User-facing value

4. **Task 2: Query Analyzer Module** (Low Priority)
   - Optional feature
   - Analytics API already provides cache analysis
   - Can be added anytime

5. **Task 5: Redis Migration Guide** (Future)
   - Only needed when scaling
   - Can be written when actually needed

---

## Notes

- All tasks are backwards-compatible
- No breaking changes required
- Can be implemented incrementally
- System is production-ready without these tasks

---

**Last Updated:** 2025-10-11
**Review Date:** Before next major version release
