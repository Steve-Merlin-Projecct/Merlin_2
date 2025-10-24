---
title: "Rate Limiting Deployment Guide"
type: guide
component: general
status: draft
tags: []
---

# Rate Limiting Deployment Guide

**Quick Start Guide for Deploying API Rate Limiting System**

---

## Prerequisites

- Python 3.11+
- PostgreSQL database access
- Flask application running (`app_modular.py`)

---

## Step 1: Install Dependencies

```bash
pip install Flask-Limiter>=3.5.0
```

Or if using requirements.txt:
```bash
pip install -r requirements.txt
```

**Verify installation:**
```bash
python -c "import flask_limiter; print(flask_limiter.__version__)"
# Should output: 3.5.0 or higher
```

---

## Step 2: Run Database Migration

**Option A: Using psql directly**
```bash
psql -h localhost -U postgres -d local_Merlin_3 \
  -f database_tools/migrations/rate_limiting_analytics_schema.sql
```

**Option B: Using environment variables**
```bash
export PGPASSWORD="your_password"
psql -h localhost -U postgres -d local_Merlin_3 \
  -f database_tools/migrations/rate_limiting_analytics_schema.sql
```

**Verify tables created:**
```sql
\c local_Merlin_3
\dt rate_limit*
-- Should show: rate_limit_analytics, query_logs, cache_analysis_daily
```

---

## Step 3: Configure Environment (Optional)

Create `.env` file or set environment variables:

```bash
# Optional: Use Redis/Valkey instead of in-memory (for production scaling)
RATE_LIMIT_STORAGE_URI=memory://  # Default (no Redis needed)
# RATE_LIMIT_STORAGE_URI=redis://localhost:6379  # For Redis

# Optional: Adjust query logging
ENABLE_QUERY_LOGGING=true
QUERY_LOG_SAMPLE_RATE=1.0  # 100% of queries

# Optional: Adjust violation logging
ENABLE_VIOLATION_LOGGING=true
```

---

## Step 4: Start Application

```bash
python app_modular.py
```

**Expected startup logs:**
```
INFO: Rate limiter initialized successfully
INFO: Rate limiter initialized with storage: memory://
INFO: Default rate limit: 100/minute
INFO: Max memory: 50MB
INFO: Fail closed: True
INFO: Maximum daily cost with all limits hit: $240.00
INFO: Memory monitoring and cleanup thread started
INFO: Rate Limiting Analytics API registered successfully
```

---

## Step 5: Verify Installation

### Test 1: Check Health Endpoint (Should NOT be rate limited)
```bash
curl http://localhost:5001/health
# Should return 200 OK always
```

### Test 2: Check Rate Limited Endpoint
```bash
# First request - should work
curl -X POST http://localhost:5001/api/ai/analyze-jobs \
  -H "Content-Type: application/json" \
  -H "Cookie: authenticated=true" \
  -d '{"batch_size": 5}'

# Check rate limit headers in response:
# X-RateLimit-Limit: 10
# X-RateLimit-Remaining: 9
# X-RateLimit-Reset: <timestamp>
```

### Test 3: Trigger Rate Limit (Optional)
```bash
# Send 11 requests rapidly (limit is 10/minute)
for i in {1..11}; do
  curl -X POST http://localhost:5001/api/ai/analyze-jobs \
    -H "Content-Type: application/json" \
    -H "Cookie: authenticated=true" \
    -d '{"batch_size": 1}'
  echo "Request $i"
done

# Last request should return 429 Too Many Requests
```

### Test 4: Check Metrics API
```bash
curl http://localhost:5001/api/rate-limit/metrics \
  -H "Cookie: authenticated=true" | jq .

# Should return:
# {
#   "status": "success",
#   "metrics": {
#     "memory": { "current_mb": 0.01, "utilization_percent": 0.02 },
#     "keys": { "total_active": 1 },
#     "cleanup": { "total_cleanups": 0 }
#   }
# }
```

---

## Step 6: Monitor System

### Real-Time Monitoring

**Memory Usage:**
```bash
watch -n 5 'curl -s http://localhost:5001/api/rate-limit/metrics \
  -H "Cookie: authenticated=true" | jq ".metrics.memory"'
```

**Active Keys:**
```bash
curl -s http://localhost:5001/api/rate-limit/metrics \
  -H "Cookie: authenticated=true" | jq ".metrics.keys"
```

### Database Monitoring

**Check recent violations:**
```sql
SELECT
    endpoint,
    COUNT(*) as violation_count,
    MAX(timestamp) as last_violation
FROM rate_limit_analytics
WHERE timestamp > NOW() - INTERVAL '1 hour'
GROUP BY endpoint
ORDER BY violation_count DESC;
```

**Check cache hit potential:**
```sql
SELECT * FROM calculate_cache_hit_potential(24);
```

---

## Configuration Tuning

### Adjust Rate Limits

Edit `modules/security/rate_limit_config.py`:

```python
# Make AI analysis more generous
RATE_LIMIT_TIERS["expensive"]["ai_analysis"] = "20/minute;100/hour"  # Was 10/min

# Make scraping stricter
RATE_LIMIT_TIERS["expensive"]["job_scraping"] = "3/hour;10/day"  # Was 5/hour
```

Restart application for changes to take effect.

### Adjust Memory Limits

```python
# In rate_limit_config.py
MAX_MEMORY_MB = 30  # Lower if memory is constrained
ALERT_THRESHOLD_MB = 25  # Adjust warning threshold
CLEANUP_INTERVAL_SECONDS = 30  # Clean up more frequently
```

### Disable Features (If Needed)

```python
# In rate_limit_config.py
ENABLE_QUERY_LOGGING = False  # Disable query logging
ENABLE_VIOLATION_LOGGING = False  # Disable violation logging
TRACK_PERFORMANCE_OVERHEAD = False  # Disable performance tracking
```

---

## Troubleshooting

### Problem: "Module not found: flask_limiter"
**Solution:**
```bash
pip install Flask-Limiter>=3.5.0
python -c "import flask_limiter"  # Verify
```

### Problem: "Database tables not found"
**Solution:**
```bash
# Re-run migration
psql -h localhost -U postgres -d local_Merlin_3 \
  -f database_tools/migrations/rate_limiting_analytics_schema.sql

# Check tables
psql -h localhost -U postgres -d local_Merlin_3 -c "\dt rate_limit*"
```

### Problem: "Rate limiting not working"
**Solution:**
```bash
# Check logs for initialization
grep "Rate limiter initialized" logs/application.log

# Verify decorator applied
grep "@rate_limit" modules/ai_job_description_analysis/ai_integration_routes.py

# Test directly
curl -i http://localhost:5001/api/ai/analyze-jobs
# Look for X-RateLimit-* headers
```

### Problem: "Memory usage too high"
**Solution:**
```python
# In rate_limit_config.py, reduce limits or increase cleanup frequency
MAX_MEMORY_MB = 30
CLEANUP_INTERVAL_SECONDS = 30

# Check current usage
curl http://localhost:5001/api/rate-limit/metrics | jq ".metrics.memory"
```

### Problem: "Too many 429 errors"
**Solution:**
1. Check if limits are too strict for actual usage
2. Review analytics: `curl http://localhost:5001/api/rate-limit/analytics`
3. Adjust limits in `rate_limit_config.py`
4. Restart application

---

## Production Deployment (DigitalOcean)

### App Platform Deployment

1. **Update requirements.txt** (already done)
   ```
   Flask-Limiter>=3.5.0
   ```

2. **Set environment variables in App Platform:**
   ```
   RATE_LIMIT_STORAGE_URI=memory://
   ENABLE_QUERY_LOGGING=true
   ENABLE_VIOLATION_LOGGING=true
   ```

3. **Run database migration** (one-time)
   ```bash
   # From local machine connected to production DB
   psql -h production-db.ondigitalocean.com -U doadmin -d local_Merlin_3 \
     -f database_tools/migrations/rate_limiting_analytics_schema.sql
   ```

4. **Deploy application**
   - Push to GitHub
   - DigitalOcean auto-deploys
   - Check deployment logs for "Rate limiter initialized"

5. **Monitor for first 24 hours**
   ```bash
   # Check metrics
   curl https://your-app.ondigitalocean.app/api/rate-limit/metrics \
     -H "Cookie: authenticated=true"

   # Check violations
   psql -h production-db -U doadmin -d local_Merlin_3 \
     -c "SELECT * FROM v_rate_limit_violations_summary;"
   ```

### Scaling to Multiple Instances (Future)

If you scale to multiple app instances, upgrade to Valkey:

1. **Provision Managed Valkey** ($15/month)
2. **Update environment variable:**
   ```
   RATE_LIMIT_STORAGE_URI=redis://valkey-connection-string:6379
   ```
3. **Redeploy** - no code changes needed!

---

## Quick Reference

### Endpoints

| Endpoint | Purpose |
|----------|---------|
| `/api/rate-limit/metrics` | Real-time metrics |
| `/api/rate-limit/metrics/summary` | Human-readable summary |
| `/api/rate-limit/status` | Current user status |
| `/api/rate-limit/analytics` | Historical violations |
| `/api/rate-limit/cache-analysis` | Optimization insights |
| `/api/rate-limit/config` | Configuration summary |

### Rate Limit Tiers

| Tier | Limit | Use Cases |
|------|-------|-----------|
| Expensive | 10/min; 50/hour; 200/day | AI analysis, Job scraping |
| Moderate | 20/min; 200/hour | Documents, Email |
| Cheap | 200/min | Database reads, Dashboard |
| Default | 100/min | All other endpoints |

### Key Files

| File | Purpose |
|------|---------|
| `modules/security/rate_limit_config.py` | Configuration |
| `modules/security/rate_limit_manager.py` | Core logic |
| `modules/security/rate_limit_monitor.py` | Monitoring |
| `modules/security/rate_limit_analytics_api.py` | Analytics API |
| `database_tools/migrations/rate_limiting_analytics_schema.sql` | Database schema |

---

## Next Steps After Deployment

1. **Monitor for 1 week**
   - Check daily: `/api/rate-limit/metrics`
   - Review weekly: `/api/rate-limit/analytics?start_date=YYYY-MM-DD`

2. **Tune limits based on actual usage**
   - Too many 429s? Increase limits
   - No 429s ever? Decrease limits (save costs)

3. **Review cache analysis**
   - Monthly: `/api/rate-limit/cache-analysis`
   - If cache hit potential >50%, consider Redis investment

4. **Document any custom limits**
   - Update `rate_limit_config.py` comments
   - Add to team documentation

---

## Support

For issues:
1. Check logs: `grep "rate limit" logs/application.log`
2. Check metrics: `curl /api/rate-limit/metrics`
3. Review database: `SELECT * FROM v_rate_limit_violations_summary;`
4. See `IMPLEMENTATION_SUMMARY_RATE_LIMITING.md` for detailed troubleshooting

**Deployment Date:** 2025-10-11
**Version:** 1.0.0
