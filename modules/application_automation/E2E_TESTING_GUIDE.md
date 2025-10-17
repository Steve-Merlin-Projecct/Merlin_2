# End-to-End Testing Guide
## Application Automation Module MVP

**Version:** 1.0.0
**Last Updated:** 2025-10-14
**Status:** MVP Complete - Ready for Testing

---

## Overview

This guide provides comprehensive instructions for testing the Application Automation module end-to-end, from Flask API calls to Apify Actor execution and database verification.

---

## Test Environment Setup

### Prerequisites

1. **Python Dependencies Installed**
   ```bash
   pip install -r requirements.txt
   ```

2. **Database Created**
   ```bash
   # Table apify_application_submissions should exist
   psql -U postgres -d local_Merlin_3 -c "\d apify_application_submissions"
   ```

3. **Environment Variables Set**
   ```bash
   # Required in .env file
   APIFY_TOKEN=your_apify_token
   APPLICATION_AUTOMATION_ACTOR_ID=username/actor-name (when deployed)
   WEBHOOK_API_KEY=your_api_key
   FLASK_API_URL=http://localhost:5000 (or your deployed URL)
   ```

4. **Flask Server Running**
   ```bash
   python app_modular.py
   # Should show: "Application Automation API registered successfully"
   ```

---

## Testing Phases

### Phase 1: Unit Tests (Isolated Components)

#### 1.1 Run Simple API Tests

```bash
# Test core functionality without full app initialization
python -m pytest modules/application_automation/tests/test_api_simple.py -v

# Expected Results:
# ✓ Input validation tests pass
# ✓ Database model tests pass
# ✓ Form mapping file exists and loads correctly
# ✓ Screenshot manager initializes
```

**Test Coverage:**
- Input validation logic
- Form mapping structure
- Database model functionality
- Component initialization

#### 1.2 Test Form Mappings

```bash
# Verify Indeed form mappings are valid JSON
python -c "import json; print(json.load(open('modules/application_automation/form_mappings/indeed.json'))['form_types'].keys())"

# Expected Output:
# dict_keys(['standard_indeed_apply', 'indeed_quick_apply'])
```

#### 1.3 Test Database Connectivity

```bash
# Test database connection and table exists
python -c "
from modules.database.database_client import DatabaseClient
db = DatabaseClient()
result = db.execute_read('SELECT COUNT(*) FROM apify_application_submissions')
print(f'Table exists. Row count: {result[0][0]}')
"
```

---

### Phase 2: Flask API Integration Tests

#### 2.1 Test Health/Info Endpoint (if exists)

```bash
curl -X GET http://localhost:5000/api/application-automation/health \
  -H "X-API-Key: $WEBHOOK_API_KEY"
```

#### 2.2 Test Trigger Automation Endpoint

```bash
# Trigger automation for a job
curl -X POST http://localhost:5000/api/application-automation/trigger \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $WEBHOOK_API_KEY" \
  -d '{
    "job_id": "test_job_001",
    "application_id": "test_app_001"
  }'

# Expected Response (202 Accepted or 200 OK):
# {
#   "success": true,
#   "message": "Automation triggered",
#   "submission_id": "uuid-here",
#   "actor_run_id": "run_id_here"
# }
```

#### 2.3 Test Record Submission Endpoint

```bash
# Record a submission result (simulating Actor callback)
curl -X POST http://localhost:5000/api/application-automation/submissions \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $WEBHOOK_API_KEY" \
  -d '{
    "job_id": "test_job_002",
    "actor_run_id": "test_run_123",
    "status": "submitted",
    "form_platform": "indeed",
    "form_type": "standard_indeed_apply",
    "fields_filled": ["full_name", "email", "resume"],
    "submission_confirmed": true,
    "confirmation_message": "Application submitted successfully",
    "screenshot_urls": ["/storage/test_screenshot.jpg"]
  }'

# Expected Response (201 Created):
# {
#   "success": true,
#   "submission_id": "uuid-here"
# }
```

#### 2.4 Test Get Submission Endpoint

```bash
# Get submission by ID (replace with actual UUID from previous step)
SUBMISSION_ID="your-submission-uuid-here"

curl -X GET "http://localhost:5000/api/application-automation/submissions/$SUBMISSION_ID" \
  -H "X-API-Key: $WEBHOOK_API_KEY"

# Expected Response (200 OK):
# {
#   "success": true,
#   "data": {
#     "submission_id": "uuid",
#     "job_id": "test_job_002",
#     "status": "submitted",
#     ...
#   }
# }
```

#### 2.5 Test List Submissions Endpoint

```bash
# List all submissions
curl -X GET "http://localhost:5000/api/application-automation/submissions" \
  -H "X-API-Key: $WEBHOOK_API_KEY"

# With filters
curl -X GET "http://localhost:5000/api/application-automation/submissions?status=submitted&form_platform=indeed" \
  -H "X-API-Key: $WEBHOOK_API_KEY"

# Expected Response (200 OK):
# {
#   "success": true,
#   "data": [...],
#   "count": 5
# }
```

#### 2.6 Test Mark as Reviewed Endpoint

```bash
# Mark submission as reviewed
SUBMISSION_ID="your-submission-uuid-here"

curl -X PUT "http://localhost:5000/api/application-automation/submissions/$SUBMISSION_ID/review" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $WEBHOOK_API_KEY" \
  -d '{
    "reviewed_by": "test_user",
    "review_notes": "Verified submission looks correct"
  }'

# Expected Response (200 OK):
# {
#   "success": true,
#   "message": "Submission marked as reviewed"
# }
```

#### 2.7 Test Get Statistics Endpoint

```bash
# Get submission statistics
curl -X GET "http://localhost:5000/api/application-automation/stats" \
  -H "X-API-Key: $WEBHOOK_API_KEY"

# Expected Response (200 OK):
# {
#   "success": true,
#   "data": {
#     "total_submissions": 10,
#     "by_status": {...},
#     "by_platform": {...},
#     "confirmation_rate": 0.85
#   }
# }
```

---

### Phase 3: Database Verification

#### 3.1 Verify Table Structure

```bash
psql -U postgres -d local_Merlin_3 << 'SQL'
-- Check table exists
\d apify_application_submissions

-- Check indexes
\di apify_application_submissions*

-- Check triggers
SELECT tgname FROM pg_trigger WHERE tgrelid = 'apify_application_submissions'::regclass;
SQL
```

#### 3.2 Verify Data Integrity

```bash
psql -U postgres -d local_Merlin_3 << 'SQL'
-- Count submissions by status
SELECT status, COUNT(*) FROM apify_application_submissions GROUP BY status;

-- Count submissions by platform
SELECT form_platform, COUNT(*) FROM apify_application_submissions GROUP BY form_platform;

-- Check for recent submissions
SELECT submission_id, job_id, status, submitted_at
FROM apify_application_submissions
ORDER BY submitted_at DESC
LIMIT 5;

-- Verify trigger works (updated_at should change)
UPDATE apify_application_submissions
SET status = 'reviewed'
WHERE status = 'submitted'
LIMIT 1
RETURNING submission_id, updated_at;
SQL
```

---

### Phase 4: Apify Actor Testing (Local)

**Note:** Requires Playwright installed locally

#### 4.1 Test Actor Locally (Mock Mode)

```bash
# Navigate to module directory
cd modules/application_automation

# Create test input
cat > test_input.json << 'JSON'
{
  "job_id": "test_job_local_001",
  "application_id": "test_app_local_001",
  "flask_api_url": "http://host.docker.internal:5000",
  "api_key": "your_api_key_here",
  "mock_mode": true
}
JSON

# Run Actor main script locally
python actor_main.py

# Expected Output:
# - Actor initializes successfully
# - Fetches application data (or uses mock)
# - Simulates form filling
# - Captures screenshots
# - Reports results
```

#### 4.2 Test Individual Components

```bash
# Test Data Fetcher
python -c "
from modules.application_automation.data_fetcher import FlaskAPIClient
client = FlaskAPIClient('http://localhost:5000', 'your_api_key')
result = client.fetch_job_details('test_job_001')
print(result)
"

# Test Form Filler (dry run)
python -c "
from modules.application_automation.form_filler import FormFiller
filler = FormFiller()
# Would need mock Page object for full test
print('FormFiller initialized successfully')
"

# Test Screenshot Manager
python -c "
from modules.application_automation.screenshot_manager import ScreenshotManager
manager = ScreenshotManager()
print('ScreenshotManager initialized successfully')
"
```

---

### Phase 5: End-to-End Workflow Test

#### 5.1 Full Workflow Test (Manual)

**Prerequisites:**
- Real Indeed job posting with application link
- Resume and cover letter documents generated
- Flask API running
- Apify Actor deployed (or running locally)

**Steps:**

1. **Create Application Record**
   ```bash
   # Ensure job and application exist in database
   # Or trigger via your normal workflow
   ```

2. **Trigger Automation**
   ```bash
   curl -X POST http://localhost:5000/api/application-automation/trigger \
     -H "Content-Type: application/json" \
     -H "X-API-Key: $WEBHOOK_API_KEY" \
     -d '{
       "job_id": "real_job_id_here",
       "application_id": "real_app_id_here"
     }'
   ```

3. **Monitor Actor Execution**
   ```bash
   # If deployed to Apify:
   # Check Apify dashboard: https://console.apify.com/actors/runs

   # If running locally:
   # Watch logs in terminal
   ```

4. **Verify Submission**
   ```bash
   # Check database for new submission
   psql -U postgres -d local_Merlin_3 -c \
     "SELECT * FROM apify_application_submissions ORDER BY submitted_at DESC LIMIT 1;"
   ```

5. **Review Screenshots**
   ```bash
   # Check storage for screenshots
   ls -lh storage/screenshots/

   # Or via API
   curl -X GET "http://localhost:5000/api/application-automation/submissions/SUBMISSION_ID" \
     -H "X-API-Key: $WEBHOOK_API_KEY" | jq '.data.screenshot_urls'
   ```

6. **Mark as Reviewed**
   ```bash
   curl -X PUT "http://localhost:5000/api/application-automation/submissions/SUBMISSION_ID/review" \
     -H "Content-Type: application/json" \
     -H "X-API-Key: $WEBHOOK_API_KEY" \
     -d '{
       "reviewed_by": "your_username",
       "review_notes": "Verified submission"
     }'
   ```

---

## Test Results Documentation

### Expected Test Pass Rates

| Test Phase | Expected Pass Rate | Notes |
|------------|-------------------|-------|
| Phase 1: Unit Tests | 90-100% | Core logic, isolated |
| Phase 2: API Tests | 95-100% | Requires Flask running |
| Phase 3: Database Tests | 100% | Requires DB setup |
| Phase 4: Actor Tests | 80-90% | May fail if deps missing |
| Phase 5: E2E Tests | 70-80% | Depends on real Indeed sites |

### Known Limitations (MVP)

1. **Playwright Installation**: Requires system dependencies
2. **Indeed Site Changes**: Form selectors may break if Indeed updates HTML
3. **CAPTCHA Handling**: Not implemented - manual intervention required
4. **Multi-page Forms**: Only single-page forms supported
5. **Custom Questions**: Generic handling only

---

## Troubleshooting

### Common Issues

#### Issue: "Table does not exist"
```bash
# Solution: Run migration
psql -U postgres -d local_Merlin_3 -f modules/application_automation/migrations/001_create_application_submissions.sql
```

#### Issue: "API Key authentication failed"
```bash
# Solution: Verify API key in .env
echo $WEBHOOK_API_KEY
# Ensure it matches between Flask and Actor
```

#### Issue: "Module 'playwright' not found"
```bash
# Solution: Install Playwright
pip install playwright
playwright install chromium
```

#### Issue: "Cannot connect to Flask API"
```bash
# Solution: Verify Flask is running and accessible
curl http://localhost:5000/health
# If behind proxy, check FLASK_API_URL uses correct host
```

#### Issue: "Form selectors not found"
```bash
# Solution: Check if Indeed site structure changed
# Update form_mappings/indeed.json with new selectors
# Run Actor in debug mode to see actual HTML
```

---

## Success Criteria

### MVP Test Pass Criteria

✅ **Phase 1**: At least 8/12 unit tests pass
✅ **Phase 2**: All API endpoints return correct status codes
✅ **Phase 3**: Database operations complete without errors
✅ **Phase 4**: Actor initializes and runs without crashes
✅ **Phase 5**: At least 1 successful end-to-end application submission

### Production Readiness Criteria

- [ ] All unit tests pass (100%)
- [ ] All API tests pass (100%)
- [ ] End-to-end test succeeds on 3+ different Indeed jobs
- [ ] Error handling tested with invalid inputs
- [ ] Screenshot capture works consistently
- [ ] Database triggers and constraints verified
- [ ] Actor deployed to Apify and accessible
- [ ] Documentation complete and accurate

---

## Test Summary Template

```markdown
# Test Run Summary

**Date:** YYYY-MM-DD
**Tester:** Your Name
**Environment:** Local / Staging / Production

## Results

### Phase 1: Unit Tests
- Tests Run: X/12
- Passed: X
- Failed: X
- Skipped: X

### Phase 2: Flask API Tests
- Endpoints Tested: X/7
- Passed: X
- Failed: X

### Phase 3: Database Tests
- Operations Tested: X
- All Passed: Yes/No

### Phase 4: Actor Tests
- Components Tested: X
- Working: X
- Issues: X

### Phase 5: E2E Test
- Attempted: Yes/No
- Successful: Yes/No
- Notes: ...

## Issues Found
1. Issue description
2. Issue description

## Recommendations
1. Recommendation
2. Recommendation
```

---

## Next Steps After Testing

1. **Document Test Results**: Fill out test summary template
2. **Fix Critical Issues**: Address any blocking bugs
3. **Update Form Mappings**: Refine selectors based on real testing
4. **Deploy to Apify**: Push Actor to Apify platform
5. **Production Testing**: Test with real job applications (carefully!)
6. **User Acceptance**: Have user review and approve workflow
7. **Monitor**: Watch first few real submissions closely

---

## Additional Resources

- **Apify Documentation**: https://docs.apify.com
- **Playwright Documentation**: https://playwright.dev/python
- **Flask Testing**: https://flask.palletsprojects.com/en/latest/testing/
- **pytest Documentation**: https://docs.pytest.org

---

**End of Testing Guide**
