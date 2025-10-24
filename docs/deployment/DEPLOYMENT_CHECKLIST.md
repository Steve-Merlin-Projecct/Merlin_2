---
title: "Deployment Checklist"
type: technical_doc
component: general
status: draft
tags: []
---

# Gemini Prompt Optimization - Deployment Checklist

**System**: Three-Tier Sequential Batch Job Analysis
**Version**: 1.0
**Date**: October 9, 2025

---

## Pre-Deployment Checklist

### 1. Database Setup ✅

- [ ] **Apply security_detections table migration**
  ```bash
  psql -h localhost -U your_user -d your_db \
    -f database_tools/migrations/001_create_security_detections_table.sql
  ```
  - Verify table created: `\dt security_detections`
  - Verify indexes: `\di security_detections_*`

- [ ] **Apply job_analysis_tiers table migration**
  ```bash
  psql -h localhost -U your_user -d your_db \
    -f database_tools/migrations/002_create_job_analysis_tiers_table.sql
  ```
  - Verify table created: `\dt job_analysis_tiers`
  - Verify trigger: `\df update_job_analysis_tiers_updated_at`

- [ ] **Verify foreign key constraints**
  ```sql
  SELECT conname, conrelid::regclass, confrelid::regclass
  FROM pg_constraint
  WHERE conrelid::regclass::text IN ('security_detections', 'job_analysis_tiers');
  ```

---

### 2. Test Suite Execution ✅

- [ ] **Run security tests**
  ```bash
  cd /workspace/.trees/gemini-prompts
  python tests/security/test_unpunctuated_detector.py
  ```
  - Expected: All 20+ tests pass
  - Verify: DetectionResult class works correctly
  - Verify: Severity levels calculated properly
  - Verify: False positive rate is low

- [ ] **Run integration tests**
  ```bash
  python tests/integration/test_sequential_batch_workflow.py
  ```
  - Expected: All 30+ tests pass
  - Verify: Time window detection works
  - Verify: API authentication works
  - Verify: Tier progression logic works

---

### 3. Application Integration ✅

- [ ] **Register tiered analysis routes**

  Add to `app_modular.py` or your main Flask application file:

  ```python
  from modules.ai_job_description_analysis.api_routes_tiered import register_tiered_analysis_routes

  # After app initialization
  register_tiered_analysis_routes(app)

  logger.info("Tiered analysis routes registered at /api/analyze")
  ```

- [ ] **Verify API key configuration**

  Check `.env` file or environment variables:
  ```bash
  echo $WEBHOOK_API_KEY
  ```
  - Should be set to a secure random key
  - Minimum 32 characters recommended

- [ ] **Verify Gemini API key**

  Check environment variable:
  ```bash
  echo $GEMINI_API_KEY
  ```
  - Should be valid Google AI Studio API key
  - Test with a simple request to verify quota

---

### 4. Initial Smoke Testing ✅

- [ ] **Test health endpoint (no auth)**
  ```bash
  curl http://localhost:5000/api/analyze/health
  ```
  - Expected: `{"status": "healthy", "service": "tiered_job_analysis", "timestamp": "..."}`

- [ ] **Test status endpoint (with auth)**
  ```bash
  curl -H "X-API-Key: your_api_key" \
    http://localhost:5000/api/analyze/status
  ```
  - Expected: JSON with pending_tier1, pending_tier2, pending_tier3, fully_analyzed

- [ ] **Test Tier 1 with small batch**
  ```bash
  curl -X POST \
    -H "X-API-Key: your_api_key" \
    -H "Content-Type: application/json" \
    -d '{"max_jobs": 5}' \
    http://localhost:5000/api/analyze/tier1
  ```
  - Expected: Success response with tier=1, successful count, token usage
  - Verify jobs marked tier_1_completed in database

---

## Deployment Steps

### 5. Manual Test Execution ✅

Run manual tests to verify complete workflow:

```python
from modules.ai_job_description_analysis.sequential_batch_scheduler import (
    run_tier1_now,
    run_tier2_now,
    run_tier3_now,
    get_status
)

# 5.1 Check initial status
status = get_status()
print(f"Pending Tier 1: {status['pending_tier1']}")
print(f"Pending Tier 2: {status['pending_tier2']}")
print(f"Pending Tier 3: {status['pending_tier3']}")

# 5.2 Run Tier 1 (small batch)
tier1_results = run_tier1_now(max_jobs=5)
print(f"Tier 1 successful: {tier1_results['successful']}")
print(f"Tier 1 tokens: {tier1_results.get('total_tokens', 0)}")
print(f"Tier 1 avg response: {tier1_results.get('avg_response_time_ms', 0)}ms")

# Verify in database
# SELECT COUNT(*) FROM job_analysis_tiers WHERE tier_1_completed = TRUE;

# 5.3 Run Tier 2 (processes Tier 1 completed jobs)
tier2_results = run_tier2_now(max_jobs=5)
print(f"Tier 2 successful: {tier2_results['successful']}")

# Verify in database
# SELECT COUNT(*) FROM job_analysis_tiers WHERE tier_2_completed = TRUE;

# 5.4 Run Tier 3 (processes Tier 2 completed jobs)
tier3_results = run_tier3_now(max_jobs=5)
print(f"Tier 3 successful: {tier3_results['successful']}")

# Verify in database
# SELECT COUNT(*) FROM job_analysis_tiers WHERE tier_3_completed = TRUE;
```

**Checklist**:
- [ ] Tier 1 processes jobs successfully
- [ ] Token usage is ~1,500-2,000 per job (Tier 1)
- [ ] Response time is < 3 seconds (Tier 1)
- [ ] Tier 2 loads Tier 1 context successfully
- [ ] Token usage is ~1,000-1,500 per job (Tier 2)
- [ ] Tier 3 loads Tier 1+2 context successfully
- [ ] Token usage is ~1,500-2,000 per job (Tier 3)
- [ ] No errors in logs
- [ ] Database records updated correctly

---

### 6. Full Sequential Batch Test ✅

```python
from modules.ai_job_description_analysis.sequential_batch_scheduler import run_all_tiers_now

# Run complete sequential workflow
results = run_all_tiers_now(tier1_max=10, tier2_max=10, tier3_max=10)

print(f"Total jobs processed: {results['summary']['total_jobs_processed']}")
print(f"Total failures: {results['summary']['total_failures']}")
print(f"Total tokens: {results['summary']['total_tokens']}")
print(f"Total time: {results['total_time_seconds']:.2f}s")

# Verify expected ranges
assert results['tier1']['avg_response_time_ms'] < 3000, "Tier 1 too slow"
assert results['tier2']['avg_response_time_ms'] < 3000, "Tier 2 too slow"
assert results['tier3']['avg_response_time_ms'] < 4000, "Tier 3 too slow"

# Verify token usage per job
tier1_avg = results['tier1']['total_tokens'] / results['tier1']['successful']
tier2_avg = results['tier2']['total_tokens'] / results['tier2']['successful']
tier3_avg = results['tier3']['total_tokens'] / results['tier3']['successful']

assert 1500 <= tier1_avg <= 2000, f"Tier 1 tokens outside range: {tier1_avg}"
assert 1000 <= tier2_avg <= 1500, f"Tier 2 tokens outside range: {tier2_avg}"
assert 1500 <= tier3_avg <= 2000, f"Tier 3 tokens outside range: {tier3_avg}"
```

**Checklist**:
- [ ] All three tiers execute sequentially
- [ ] Total tokens ~5,500 per job (across all tiers)
- [ ] Total time is reasonable (< 10s per job)
- [ ] Success rate > 95%
- [ ] Database shows complete tier progression

---

### 7. Scheduler Deployment ✅

#### Option A: Command Line Execution

```bash
# Run as background process
nohup python -m modules.ai_job_description_analysis.sequential_batch_scheduler schedule > scheduler.log 2>&1 &

# Get process ID
echo $! > scheduler.pid

# Monitor logs
tail -f scheduler.log
```

#### Option B: Systemd Service (Production)

Create `/etc/systemd/system/gemini-scheduler.service`:

```ini
[Unit]
Description=Gemini Sequential Batch Scheduler
After=network.target postgresql.service

[Service]
Type=simple
User=your_app_user
WorkingDirectory=/path/to/workspace/.trees/gemini-prompts
Environment="PATH=/path/to/venv/bin"
Environment="PYTHONPATH=/path/to/workspace/.trees/gemini-prompts"
ExecStart=/path/to/venv/bin/python -m modules.ai_job_description_analysis.sequential_batch_scheduler schedule
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

Deploy:
```bash
sudo systemctl daemon-reload
sudo systemctl enable gemini-scheduler
sudo systemctl start gemini-scheduler
sudo systemctl status gemini-scheduler
```

**Checklist**:
- [ ] Scheduler starts without errors
- [ ] Logs show time window checks (every 5 minutes)
- [ ] Scheduler executes Tier 1 during 2:00-3:00 AM window
- [ ] Scheduler executes Tier 2 during 3:00-4:30 AM window
- [ ] Scheduler executes Tier 3 during 4:30-6:00 AM window
- [ ] No tier executes outside its time window
- [ ] Error handling works (continues after failures)

---

### 8. Monitoring Setup ✅

- [ ] **Database monitoring queries**

  ```sql
  -- Check tier completion rates
  SELECT
    COUNT(*) FILTER (WHERE tier_1_completed = TRUE) as tier1_complete,
    COUNT(*) FILTER (WHERE tier_2_completed = TRUE) as tier2_complete,
    COUNT(*) FILTER (WHERE tier_3_completed = TRUE) as tier3_complete,
    COUNT(*) as total_jobs
  FROM job_analysis_tiers;

  -- Check average response times
  SELECT
    AVG(tier_1_response_time_ms) as tier1_avg_ms,
    AVG(tier_2_response_time_ms) as tier2_avg_ms,
    AVG(tier_3_response_time_ms) as tier3_avg_ms
  FROM job_analysis_tiers
  WHERE tier_1_completed = TRUE;

  -- Check token usage
  SELECT
    AVG(tier_1_tokens_used) as tier1_avg_tokens,
    AVG(tier_2_tokens_used) as tier2_avg_tokens,
    AVG(tier_3_tokens_used) as tier3_avg_tokens,
    SUM(tier_1_tokens_used + tier_2_tokens_used + tier_3_tokens_used) as total_tokens
  FROM job_analysis_tiers
  WHERE tier_3_completed = TRUE;
  ```

- [ ] **Security monitoring**

  ```sql
  -- Check for injection attempts
  SELECT
    detection_type,
    severity,
    COUNT(*) as detection_count,
    MAX(detected_at) as last_detected
  FROM security_detections
  GROUP BY detection_type, severity
  ORDER BY detection_count DESC;

  -- Recent high-severity detections
  SELECT *
  FROM security_detections
  WHERE severity IN ('high', 'critical')
    AND detected_at > NOW() - INTERVAL '24 hours'
  ORDER BY detected_at DESC;
  ```

- [ ] **Set up alerting**
  - Alert if success rate < 90%
  - Alert if average response time > 5 seconds
  - Alert if token usage > 6,000 per job
  - Alert if high/critical security detections > 5 per day

---

## Post-Deployment Validation

### 9. 24-Hour Performance Check ✅

After 24 hours of operation:

- [ ] **Verify throughput**
  ```sql
  SELECT
    DATE(tier_1_timestamp) as date,
    COUNT(*) as jobs_analyzed
  FROM job_analysis_tiers
  WHERE tier_3_completed = TRUE
    AND tier_3_timestamp > NOW() - INTERVAL '24 hours'
  GROUP BY DATE(tier_1_timestamp);
  ```
  - Expected: 500-600 jobs/day (target: 545)

- [ ] **Verify token efficiency**
  ```sql
  SELECT
    AVG(tier_1_tokens_used + tier_2_tokens_used + tier_3_tokens_used) as avg_total_tokens
  FROM job_analysis_tiers
  WHERE tier_3_completed = TRUE
    AND tier_3_timestamp > NOW() - INTERVAL '24 hours';
  ```
  - Expected: ~5,500 tokens per job (31% reduction from 8,000)

- [ ] **Verify response times**
  ```sql
  SELECT
    AVG(tier_1_response_time_ms) as tier1_avg,
    AVG(tier_2_response_time_ms) as tier2_avg,
    AVG(tier_3_response_time_ms) as tier3_avg
  FROM job_analysis_tiers
  WHERE tier_3_completed = TRUE
    AND tier_3_timestamp > NOW() - INTERVAL '24 hours';
  ```
  - Expected: Tier 1 < 3s, Tier 2 < 3s, Tier 3 < 4s

- [ ] **Check error rates**
  ```sql
  SELECT
    COUNT(*) as total_attempts,
    COUNT(*) FILTER (WHERE tier_1_completed = TRUE) as tier1_success,
    COUNT(*) FILTER (WHERE tier_2_completed = TRUE) as tier2_success,
    COUNT(*) FILTER (WHERE tier_3_completed = TRUE) as tier3_success
  FROM job_analysis_tiers
  WHERE created_at > NOW() - INTERVAL '24 hours';
  ```
  - Expected: > 95% success rate for each tier

---

### 10. Security Validation ✅

- [ ] **Review security detections**
  ```sql
  SELECT
    detection_type,
    severity,
    COUNT(*) as count,
    AVG(LENGTH(text_sample)) as avg_sample_length
  FROM security_detections
  WHERE detected_at > NOW() - INTERVAL '7 days'
  GROUP BY detection_type, severity;
  ```

- [ ] **Verify no false positives on legitimate jobs**
  - Sample 10 jobs marked with security detections
  - Manually review job descriptions
  - Confirm detections are valid

- [ ] **Test injection protection**
  - Submit test job with injection attempt
  - Verify detection logged to security_detections table
  - Verify job still analyzed (non-destructive detection)

---

## Model Optimization (Optional)

### 11. Model Performance Testing ✅

Test alternative models for cost/performance optimization:

```python
from modules.ai_job_description_analysis.sequential_batch_scheduler import SequentialBatchScheduler

# Test configuration 1: All flash
scheduler1 = SequentialBatchScheduler(
    tier1_model='gemini-2.0-flash-001',
    tier2_model='gemini-2.0-flash-001',
    tier3_model='gemini-2.0-flash-001'
)
results1 = scheduler1.run_full_sequential_batch(tier1_max=10, tier2_max=10, tier3_max=10)

# Test configuration 2: Flash-lite for Tier 1, Pro for Tier 3
scheduler2 = SequentialBatchScheduler(
    tier1_model='gemini-2.0-flash-lite-001',
    tier2_model='gemini-2.0-flash-001',
    tier3_model='gemini-1.5-pro'
)
results2 = scheduler2.run_full_sequential_batch(tier1_max=10, tier2_max=10, tier3_max=10)

# Compare results
print("Configuration 1 (All Flash):")
print(f"  Total time: {results1['total_time_seconds']:.2f}s")
print(f"  Total tokens: {results1['summary']['total_tokens']}")

print("\nConfiguration 2 (Optimized):")
print(f"  Total time: {results2['total_time_seconds']:.2f}s")
print(f"  Total tokens: {results2['summary']['total_tokens']}")
```

**Checklist**:
- [ ] Test at least 3 model configurations
- [ ] Record response times for each tier
- [ ] Record token usage for each tier
- [ ] Compare quality of analysis (manual review of 10 jobs)
- [ ] Document optimal configuration

---

## Rollback Plan

### 12. Rollback Procedure ✅

If issues arise, rollback using these steps:

1. **Stop scheduler**
   ```bash
   sudo systemctl stop gemini-scheduler
   # Or kill process
   kill $(cat scheduler.pid)
   ```

2. **Unregister API routes**
   - Comment out `register_tiered_analysis_routes(app)` in app_modular.py
   - Restart Flask application

3. **Revert to monolithic analysis** (if needed)
   - Original analysis code is preserved in `ai_analyzer.py`
   - No changes were made to existing analysis functions
   - Tables `security_detections` and `job_analysis_tiers` can remain (no impact on existing code)

4. **Database cleanup** (optional)
   ```sql
   -- Reset tier completion flags (if needed)
   UPDATE job_analysis_tiers SET
     tier_1_completed = FALSE,
     tier_2_completed = FALSE,
     tier_3_completed = FALSE;

   -- Or drop new tables entirely
   DROP TABLE IF EXISTS security_detections;
   DROP TABLE IF EXISTS job_analysis_tiers;
   ```

---

## Success Criteria

### Final Validation ✅

System is ready for production when:

- [x] All 50+ tests pass (security + integration)
- [x] Database migrations applied successfully
- [x] API endpoints registered and responding
- [ ] Manual test execution successful (5-10 jobs)
- [ ] Full sequential batch test successful (10+ jobs)
- [ ] Token usage within target range (5,500 ± 500)
- [ ] Response times within target range (< 3s for T1/T2, < 4s for T3)
- [ ] Success rate > 95%
- [ ] Scheduler executes correctly during time windows
- [ ] No high/critical security detections on legitimate jobs
- [ ] 24-hour performance metrics meet targets

---

## Contact & Support

**Implementation Team**: Claude AI
**Documentation**: `/workspace/.trees/gemini-prompts/IMPLEMENTATION_PROGRESS.md`
**PRD**: `/workspace/.trees/gemini-prompts/tasks/prd-gemini-prompt-optimization.md`

**Key Files**:
- Tier 1 Analyzer: `/modules/ai_job_description_analysis/tier1_analyzer.py`
- Tier 2 Analyzer: `/modules/ai_job_description_analysis/tier2_analyzer.py`
- Tier 3 Analyzer: `/modules/ai_job_description_analysis/tier3_analyzer.py`
- Scheduler: `/modules/ai_job_description_analysis/sequential_batch_scheduler.py`
- API Routes: `/modules/ai_job_description_analysis/api_routes_tiered.py`
- Security Detector: `/modules/security/unpunctuated_text_detector.py`

---

**Deployment Date**: _______________
**Deployed By**: _______________
**Production Ready**: ⬜ YES  ⬜ NO
