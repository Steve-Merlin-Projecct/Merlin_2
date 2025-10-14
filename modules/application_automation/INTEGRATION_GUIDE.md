# Application Automation - Integration Guide

## Quick Start (5 Steps)

### Step 1: Install Dependencies

```bash
# Install Python packages
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium
```

### Step 2: Run Database Migration

```bash
# Using psql
psql -U your_user -d your_database < modules/application_automation/migrations/001_create_application_submissions.sql

# Or using Python
python -c "
from modules.database.database_manager import DatabaseManager
db = DatabaseManager()
with open('modules/application_automation/migrations/001_create_application_submissions.sql') as f:
    db.execute_raw_sql(f.read())
print('Migration complete!')
"
```

### Step 3: Configure Environment Variables

Add to your `.env` file:

```bash
# Apify Configuration (get token from https://console.apify.com/)
APIFY_TOKEN=apify_api_xxxxxxxxxxxxxxxxxxxxx

# Actor ID (after deploying to Apify)
APPLICATION_AUTOMATION_ACTOR_ID=your-username/application-automation

# Flask API URL (for Actor to call back)
FLASK_API_URL=https://your-api-domain.com

# API Key (already exists in your .env)
WEBHOOK_API_KEY=your_existing_api_key
```

### Step 4: Register Flask Blueprint

Edit `/workspace/.trees/apply-assistant/app_modular.py`:

```python
# Add import at top
from modules.application_automation.automation_api import automation_api

# Add blueprint registration (around line 120, with other blueprints)
app.register_blueprint(automation_api)
```

### Step 5: Deploy Apify Actor

```bash
# Navigate to module
cd modules/application_automation

# Install Apify CLI if not already installed
npm install -g apify-cli

# Login to Apify
apify login

# Initialize Apify project (one time)
# The .actor/ directory already has the configuration

# Deploy to Apify
apify push

# Note the Actor ID and update .env:
# APPLICATION_AUTOMATION_ACTOR_ID=your-username/application-automation
```

## Verification

### Test Database

```bash
psql -U your_user -d your_database -c "
SELECT table_name, column_name, data_type
FROM information_schema.columns
WHERE table_name = 'application_submissions'
ORDER BY ordinal_position;
"
```

Expected output: Table with 20 columns including submission_id, job_id, status, etc.

### Test Flask Endpoints

```bash
# Start Flask app
python app_modular.py

# In another terminal, test trigger endpoint
curl -X POST http://localhost:5000/api/application-automation/trigger \
  -H "X-API-Key: your_api_key" \
  -H "Content-Type: application/json" \
  -d '{
    "job_id": "test_job_123",
    "application_id": "test_app_456"
  }'

# Expected response:
# {
#   "success": true,
#   "actor_run_id": "run_xyz...",
#   "actor_status": "RUNNING",
#   "submission_id": "uuid...",
#   "message": "Application automation started"
# }
```

### Test Actor Locally (Optional)

```bash
# Set environment variables
export WEBHOOK_API_KEY=your_api_key
export FLASK_API_URL=http://localhost:5000

# Run actor locally
cd modules/application_automation
python actor_main.py

# Note: This requires Apify Actor input to be provided
# See README.md for full local testing example
```

## Usage Examples

### Trigger Automation from Python

```python
import requests

def trigger_application_automation(job_id, application_id):
    """Trigger application automation via API"""
    url = "https://your-api.com/api/application-automation/trigger"
    headers = {
        "X-API-Key": "your_api_key",
        "Content-Type": "application/json"
    }
    payload = {
        "job_id": job_id,
        "application_id": application_id
    }

    response = requests.post(url, json=payload, headers=headers)
    return response.json()

# Usage
result = trigger_application_automation("job_123", "app_456")
print(f"Actor run ID: {result['actor_run_id']}")
print(f"Submission ID: {result['submission_id']}")
```

### Check Submission Status

```python
def get_submission_status(submission_id):
    """Get submission details"""
    url = f"https://your-api.com/api/application-automation/submissions/{submission_id}"
    headers = {"X-API-Key": "your_api_key"}

    response = requests.get(url, headers=headers)
    data = response.json()

    return {
        "status": data["data"]["status"],
        "confirmed": data["data"]["submission_confirmed"],
        "fields_filled": data["data"]["fields_filled"],
        "screenshots": data["data"]["screenshot_urls"]
    }

# Usage
status = get_submission_status("submission_uuid")
print(f"Status: {status['status']}")
print(f"Confirmed: {status['confirmed']}")
```

### List Pending Reviews

```python
def get_pending_reviews():
    """Get submissions pending review"""
    url = "https://your-api.com/api/application-automation/submissions"
    headers = {"X-API-Key": "your_api_key"}
    params = {"status": "submitted", "limit": 50}

    response = requests.get(url, headers=headers, params=params)
    data = response.json()

    return data["data"]

# Usage
pending = get_pending_reviews()
for submission in pending:
    print(f"Job: {submission['job_id']}")
    print(f"Submitted: {submission['submitted_at']}")
    print(f"Screenshots: {len(submission['screenshot_urls'])}")
    print("---")
```

## Troubleshooting

### Error: "Apify client not configured"

**Problem**: APIFY_TOKEN not set or invalid

**Solution**:
```bash
# Get token from https://console.apify.com/account/integrations
export APIFY_TOKEN=apify_api_xxxxxxxxxxxxxxxxxxxxx

# Or add to .env file
echo "APIFY_TOKEN=apify_api_xxxxxxxxxxxxxxxxxxxxx" >> .env
```

### Error: "Failed to trigger automation"

**Problem**: Actor ID incorrect or Actor not published

**Solution**:
1. Deploy Actor to Apify: `apify push`
2. Make Actor public or get correct ID
3. Update APPLICATION_AUTOMATION_ACTOR_ID in .env

### Error: "Unauthorized - Invalid API key"

**Problem**: API key mismatch

**Solution**:
```bash
# Ensure same key in all places:
# 1. Flask .env file: WEBHOOK_API_KEY=xxx
# 2. Apify Actor secrets: WEBHOOK_API_KEY=xxx
# 3. API request header: X-API-Key: xxx
```

### Error: "Table application_submissions does not exist"

**Problem**: Database migration not run

**Solution**:
```bash
psql -U user -d database < modules/application_automation/migrations/001_create_application_submissions.sql
```

### Error: "Form field not found"

**Problem**: Indeed changed their form structure

**Solution**:
1. Run with headless=False to see form visually
2. Inspect form elements in browser
3. Update form_mappings/indeed.json with new selectors
4. Test again

## Monitoring

### Check Actor Runs

```bash
# Via Apify Console
# Visit: https://console.apify.com/actors/runs

# Or via API
curl -H "Authorization: Bearer $APIFY_TOKEN" \
  https://api.apify.com/v2/acts/your-username/application-automation/runs
```

### Check Database Stats

```sql
-- Recent submissions
SELECT
    status,
    form_platform,
    COUNT(*) as count,
    AVG(CASE WHEN submission_confirmed THEN 1.0 ELSE 0.0 END)::numeric(5,2) as confirmation_rate
FROM application_submissions
WHERE submitted_at >= NOW() - INTERVAL '7 days'
GROUP BY status, form_platform
ORDER BY count DESC;

-- Pending reviews
SELECT
    COUNT(*) as pending_count,
    MIN(submitted_at) as oldest_submission
FROM application_submissions
WHERE status IN ('submitted', 'failed')
  AND reviewed_at IS NULL;

-- Success rate by day
SELECT
    DATE(submitted_at) as date,
    COUNT(*) as total,
    COUNT(*) FILTER (WHERE status = 'submitted') as successful,
    COUNT(*) FILTER (WHERE status = 'failed') as failed
FROM application_submissions
WHERE submitted_at >= NOW() - INTERVAL '30 days'
GROUP BY DATE(submitted_at)
ORDER BY date DESC;
```

### Check Screenshots

```python
from modules.application_automation.screenshot_manager import ScreenshotManager

# List screenshots for application
manager = ScreenshotManager()
screenshots = manager.list_screenshots(application_id="app_123")
print(f"Found {len(screenshots)} screenshots")

# Get screenshot content
screenshot_data = manager.get_screenshot("app_123_pre_submit_20251014_120530.jpg")
print(f"Screenshot size: {len(screenshot_data)} bytes")
```

## Security Checklist

- [ ] APIFY_TOKEN stored as environment variable (not hardcoded)
- [ ] WEBHOOK_API_KEY is strong and unique
- [ ] API endpoints require authentication
- [ ] HTTPS enabled for production
- [ ] Rate limiting configured
- [ ] Sensitive data not logged
- [ ] Database connection secure
- [ ] Apify Secrets used for sensitive Actor config

## Performance Tips

1. **Batch Processing**: Trigger multiple applications with delays
   ```python
   import time
   for job_id in job_ids:
       trigger_application_automation(job_id, f"app_{job_id}")
       time.sleep(5)  # Rate limit: 5 seconds between triggers
   ```

2. **Monitor Actor Usage**: Check Apify credits
   ```bash
   curl -H "Authorization: Bearer $APIFY_TOKEN" \
     https://api.apify.com/v2/users/me
   ```

3. **Screenshot Storage**: Configure cleanup
   ```python
   # In screenshot_manager.py, implement cleanup_old_screenshots()
   manager.cleanup_old_screenshots(days_old=30)
   ```

## Next Steps

1. **Test with Real Jobs**: Start with 2-3 test applications
2. **Monitor Results**: Check screenshots and confirmation rates
3. **Review Errors**: Analyze failed submissions
4. **Optimize Selectors**: Update form_mappings if needed
5. **Scale Gradually**: Increase volume as confidence grows

## Support

For issues or questions:
1. Check logs: Flask app logs and Apify Actor logs
2. Review screenshots: Check pre/post submission screenshots
3. Check database: Query application_submissions table
4. Review code: Comprehensive inline documentation available
5. Consult README.md: Detailed troubleshooting guide

## Rollback

If you need to rollback the integration:

```bash
# 1. Remove blueprint registration from app_modular.py
# 2. Drop database table
psql -U user -d database -c "
DROP TRIGGER IF EXISTS trigger_update_application_submissions_updated_at ON application_submissions;
DROP FUNCTION IF EXISTS update_application_submissions_updated_at();
DROP TABLE IF EXISTS application_submissions CASCADE;
"

# 3. Remove from Apify (optional)
apify delete
```

---

**Ready to integrate!** Follow the 5 steps above and you'll be automating Indeed applications in minutes.
