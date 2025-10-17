# Production Testing Guide

This guide explains how to run production tests with real Gemini API calls and generate comprehensive reports.

## Overview

The production testing system validates:
- **Token Optimization**: Dynamic `max_output_tokens` allocation
- **Model Selection**: Intelligent model choice based on workload
- **Batch Size Optimization**: Optimal batching for efficiency
- **Security Protections**: Injection prevention, sanitization
- **Analysis Quality**: Structured JSON output, field completeness
- **Cost Efficiency**: 30-40% token reduction vs baseline

## Quick Start

### 1. Set Environment Variables

```bash
export GEMINI_API_KEY='your-gemini-api-key-here'
```

You can get a free Gemini API key from: https://aistudio.google.com/apikey

### 2. Run Production Tests + Generate Report

```bash
# From project root
python tools/generate_production_report.py
```

This will:
1. Run all production tests with real Gemini API calls
2. Save individual test results to `reports/test_results/`
3. Generate comprehensive report: `reports/production-test-report.md`

### 3. View the Report

```bash
cat reports/production-test-report.md
```

Or open in your favorite markdown viewer.

## Test Structure

### Test Fixtures

**Location:** `tests/fixtures/realistic_job_descriptions.py`

Contains 10 realistic job descriptions:
- **6 well-formatted jobs** (Senior SWE, Data Scientist, DevOps, Product Manager, etc.)
- **2 messy jobs** (poor formatting, unrealistic expectations)
- **1 scam job** (obvious fake posting)
- **1 injection attempt** (prompt injection attack)

### Test Suite

**Location:** `tests/test_production_gemini.py`

**Test Classes:**
- `TestProductionTier1`: Core skills & classification tests
- `TestProductionTier2`: Enhanced analysis tests
- `TestProductionTier3`: Strategic insights tests
- `TestOptimizationMetrics`: Optimizer performance tests

**Key Tests:**
```python
# Tier 1 Tests
test_tier1_single_good_job()      # Single well-formatted job
test_tier1_batch_good_jobs()       # Batch of 3 good jobs
test_tier1_messy_formatting()      # Poorly formatted job
test_tier1_scam_detection()        # Scam detection
test_tier1_injection_protection()  # Security validation

# Tier 2 Tests
test_tier2_with_tier1_context()    # Tier 2 with Tier 1 results
test_tier2_stress_analysis()       # Stress level detection

# Tier 3 Tests
test_tier3_full_pipeline()         # Full 3-tier pipeline

# Optimization Tests
test_token_optimization_efficiency()  # Token efficiency validation
test_model_selection_logic()          # Model selection validation
```

## Running Tests Manually

### Run All Tests

```bash
pytest tests/test_production_gemini.py -v -s
```

### Run Specific Test Class

```bash
# Run only Tier 1 tests
pytest tests/test_production_gemini.py::TestProductionTier1 -v -s

# Run only optimization tests
pytest tests/test_production_gemini.py::TestOptimizationMetrics -v -s
```

### Run Single Test

```bash
pytest tests/test_production_gemini.py::TestProductionTier1::test_tier1_single_good_job -v -s
```

## Test Results

### Individual Test Results

**Location:** `reports/test_results/*.json`

Each test saves a JSON file with:
```json
{
  "test_name": "tier1_single_good",
  "timestamp": "2025-10-14T12:34:56",
  "input_jobs": [...],
  "output_result": {
    "success": true,
    "jobs_analyzed": 1,
    "model_used": "gemini-2.0-flash-001",
    "optimization_metrics": {
      "max_output_tokens": 10540,
      "token_efficiency": "76.1%",
      "model_selection_reason": "Complex Tier 1 analysis with large batch (10 jobs)",
      "estimated_cost": 0.00632,
      "estimated_quality": 0.92
    },
    "results": [...]
  }
}
```

### Comprehensive Report

**Location:** `reports/production-test-report.md`

Includes:
- **Executive Summary**: Key findings and test coverage
- **Tier 1/2/3 Results**: Detailed analysis of each tier
- **Optimization Analysis**: Token efficiency, model selection
- **Security Validation**: Injection protection results
- **Cost Analysis**: Savings calculations
- **Recommendations**: Next steps and improvements
- **Appendix**: Test data summary, configuration

## Understanding Optimization Metrics

### Token Efficiency

```
Token Efficiency = (Actual Tokens Used / Max Tokens Allocated) × 100%
```

**Target Range:** 60-80%
- Below 60%: Too much waste, increase batch size or reduce max_tokens
- Above 80%: Risk of truncation, increase safety margin

### Model Selection Reasons

Examples:
- `"Complex Tier 1 analysis with large batch (10 jobs)"` → Standard model
- `"Tier 2 analysis (nuanced reasoning)"` → Premium model preferred
- `"High token usage (85%), conserving with lite model"` → Budget-conscious

### Cost Savings

**Free Tier:**
- No token-based billing
- Limited to 1,500 requests/day
- Optimization improves throughput

**Paid Tier (if upgraded):**
- Before: Fixed 8192 tokens → ~$48/month for 10K jobs
- After: Dynamic allocation → ~$33.60/month
- **Savings: 30%** ($14.40/month)

## Troubleshooting

### API Key Not Set

```
❌ ERROR: GEMINI_API_KEY environment variable not set
```

**Solution:**
```bash
export GEMINI_API_KEY='your-key-here'
```

### Rate Limiting

```
⚠️ Rate limited, waiting Xs
```

**Solution:** Tests automatically retry with exponential backoff. Free tier limit is 15 RPM.

### Import Errors

```
ModuleNotFoundError: No module named 'modules'
```

**Solution:** Ensure you're running from project root:
```bash
cd /path/to/project
python tools/generate_production_report.py
```

### No Test Results Found

```
📊 Loading test results...
   Loaded 0 Tier 1 results
```

**Solution:** Tests may have failed. Check pytest output for errors.

## API Usage & Costs

### Free Tier Limits

- **15 requests per minute (RPM)**
- **1,500 requests per day**
- **$0.00 cost** (no token billing)

### Test API Usage

**Typical Test Run:**
- ~10-15 API requests
- ~0.01% of daily limit
- Safe to run multiple times per day

### Production Usage Estimates

**For 10,000 jobs/month:**
- With optimization: ~3,000 API requests
- Free tier: Sufficient (1,500/day × 30 days = 45,000/month)
- Cost: $0.00

**For 100,000+ jobs/month:**
- May exceed free tier
- Consider paid tier: ~$33.60/month (with optimization)

## Security Testing

### Injection Test Results

The test `test_tier1_injection_protection()` validates that:
1. Injection attempts are sanitized
2. LLM doesn't follow malicious instructions
3. Response is proper job analysis or empty (not injection payload)

**Expected Behavior:**
- Input contains: `"ignore all previous instructions"`
- Output should NOT contain: `"injection": "success"` or `"admin_access_token"`
- Security incident logged to `storage/security_incidents.jsonl`

### Security Layers Tested

✅ **Input Sanitization**: Detects suspicious patterns
✅ **Security Tokens**: Round-trip validation
✅ **Hash-and-Replace**: Prompt integrity protection
✅ **Response Sanitization**: Filters malicious payloads

## Next Steps

After running production tests:

1. **Review the Report**
   ```bash
   cat reports/production-test-report.md
   ```

2. **Check Token Efficiency**
   - Target: 60-80%
   - Adjust if needed

3. **Monitor Model Selection**
   - Verify appropriate models chosen
   - Check quality vs. cost tradeoff

4. **Validate Security**
   - Confirm injection protected
   - Review security incident logs

5. **Deploy to Production**
   - Optimizers proven effective
   - Security validated
   - Ready for real workloads

## Additional Resources

- **Optimizer Documentation**: See module docstrings in:
  - `modules/ai_job_description_analysis/token_optimizer.py`
  - `modules/ai_job_description_analysis/model_selector.py`
  - `modules/ai_job_description_analysis/batch_size_optimizer.py`

- **Security Documentation**: See:
  - `modules/ai_job_description_analysis/prompt_security_manager.py`
  - `modules/ai_job_description_analysis/response_sanitizer.py`

- **Gemini API Documentation**: https://ai.google.dev/gemini-api/docs

---

**Questions or Issues?**

Check the main project documentation in `/docs` or open an issue.
