---
title: "Deployment Checklist"
type: technical_doc
component: general
status: draft
tags: []
---

# Deployment Checklist - Tracking Ingest API

**Production Domain:** `https://merlin-sea-turtle-app-ckmbz.ondigitalocean.app`

**Current Status:** ⚠️ API not yet deployed to production (returns 404)

---

## Pre-Deployment Steps

### 1. ✅ Code Created (COMPLETED)

- [x] API endpoint created: `modules/link_tracking/tracking_ingest_api.py`
- [x] Blueprint registered in `app_modular.py`
- [x] Documentation written
- [x] Test suite created
- [x] Production domain configured in docs

### 2. Local Testing (DO THIS NEXT)

```bash
# Start local Flask server
python app_modular.py

# In another terminal, run tests
python test_tracking_ingest.py
```

**Expected Output:**
```
✅ PASS: Health Check
✅ PASS: Connection Test
✅ PASS: Invalid API Key
✅ PASS: Valid Batch
✅ PASS: Invalid Batch
✅ PASS: Minimal Event

Total: 6/6 tests passed
🎉 All tests passed!
```

If tests pass, proceed to deployment.

---

## Deployment Steps

### Step 1: Merge Code to Main Branch

This code is currently in a git worktree branch: `task/03-create-api-connection-with-steve-glencom-domain-se`

**Merge to main:**

```bash
# Make sure all changes are committed
git status

# Switch to main branch
git checkout main

# Merge the worktree branch
git merge task/03-create-api-connection-with-steve-glencom-domain-se

# Push to remote
git push origin main
```

### Step 2: Deploy to DigitalOcean

DigitalOcean App Platform should auto-deploy when you push to main.

**Verify deployment:**

1. Go to DigitalOcean dashboard
2. Navigate to your app: `merlin-sea-turtle-app-ckmbz`
3. Check deployment status
4. Wait for "Deployed successfully" message

**Manual deploy (if needed):**

```bash
# From DigitalOcean dashboard
# Click "Actions" → "Force Rebuild and Deploy"
```

### Step 3: Verify API is Live

```bash
# Test health endpoint (no auth)
curl https://merlin-sea-turtle-app-ckmbz.ondigitalocean.app/api/tracking-ingest/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "service": "tracking_ingest_api",
  "version": "1.0.0",
  "timestamp": "2025-10-22T14:40:00Z"
}
```

**If you get 404:** API not deployed yet, wait for deployment or check logs.

### Step 4: Test Authentication

```bash
# Get API key from production
# (SSH to server or check DigitalOcean environment variables)

# Test with API key
curl -X POST https://merlin-sea-turtle-app-ckmbz.ondigitalocean.app/api/tracking-ingest/test \
  -H "X-API-Key: YOUR_API_KEY_HERE" \
  -H "Content-Type: application/json"
```

**Expected Response:**
```json
{
  "success": true,
  "message": "API connection successful",
  "authenticated": true,
  "timestamp": "2025-10-22T14:40:00Z"
}
```

### Step 5: Send Test Batch

```bash
curl -X POST https://merlin-sea-turtle-app-ckmbz.ondigitalocean.app/api/tracking-ingest/batch \
  -H "X-API-Key: YOUR_API_KEY_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "events": [{
      "tracking_id": "test-deployment-123",
      "clicked_at": "2025-10-22T14:30:00Z",
      "ip_address": "192.168.1.1",
      "click_source": "test"
    }]
  }'
```

**Expected Response:**
```json
{
  "success": true,
  "message": "Processed 1 events",
  "results": {
    "total_events": 1,
    "successful": 1,
    "failed": 0,
    "errors": []
  },
  "timestamp": "2025-10-22T14:40:00Z"
}
```

### Step 6: Verify Database Storage

```bash
# SSH to production server
ssh your-production-server

# Connect to database
psql -d local_Merlin_3

# Check if event was stored
SELECT * FROM link_clicks WHERE tracking_id = 'test-deployment-123';
```

---

## Configuration on Production Server

### Environment Variables to Verify

Check that these are set in DigitalOcean App Platform:

```bash
# Required for API authentication
WEBHOOK_API_KEY=<your_secure_api_key>

# Database configuration (should already be set)
PGHOST=<your_database_host>
PGDATABASE=local_Merlin_3
PGUSER=postgres
PGPASSWORD=<your_database_password>
PGPORT=5432
```

**How to check in DigitalOcean:**
1. Go to your app in DigitalOcean dashboard
2. Click "Settings" tab
3. Scroll to "Environment Variables"
4. Verify `WEBHOOK_API_KEY` is set

**If not set, add it:**
1. Click "Edit" on Environment Variables
2. Add: `WEBHOOK_API_KEY = your_secure_key_here`
3. Click "Save"
4. App will redeploy automatically

---

## Post-Deployment: Configure steve-glen.com

### Provide This Information

Send to the steve-glen.com development team:

**1. Production API Endpoint:**
```
https://merlin-sea-turtle-app-ckmbz.ondigitalocean.app/api/tracking-ingest/batch
```

**2. Lookup Endpoint (for getting destination URLs):**
```
https://merlin-sea-turtle-app-ckmbz.ondigitalocean.app/api/link-tracking/lookup/{tracking_id}
```

**3. API Key:**
```
(Get from production environment variables)
```

**4. Integration Code:**
```
See: QUICK_START_STEVE_GLEN_COM.md
```

**5. Request Format Template:**
```
See: docs/api/tracking-ingest-request-template.json
```

---

## Troubleshooting

### Issue: 404 Not Found

**Possible causes:**
- Code not merged to main branch
- Deployment not complete
- App not redeployed after merge

**Solution:**
1. Check git: `git log --oneline -10` (verify merge commit exists)
2. Check DigitalOcean deployment status
3. Force rebuild if needed

### Issue: 500 Internal Server Error

**Possible causes:**
- Database connection issues
- Missing environment variables
- Import errors

**Solution:**
1. Check DigitalOcean logs: App → Runtime Logs
2. Look for Python errors
3. Verify database connectivity
4. Check all imports are installed

### Issue: "Could not register Tracking Ingest API"

**Possible causes:**
- Import error in `tracking_ingest_api.py`
- Missing dependencies

**Solution:**
1. Check logs for import errors
2. Verify `modules/link_tracking/tracking_ingest_api.py` exists
3. Check dependencies in `requirements.txt`

### Issue: Events Not Storing in Database

**Possible causes:**
- `link_clicks` table doesn't exist
- Database permissions issue
- Invalid tracking_id format

**Solution:**
1. Verify table exists: `\dt link_clicks`
2. Check database user has INSERT permissions
3. Review API error logs

---

## Monitoring

### Check API Health

```bash
# Set up monitoring script
watch -n 60 'curl -s https://merlin-sea-turtle-app-ckmbz.ondigitalocean.app/api/tracking-ingest/health | jq .'
```

### View Recent Clicks

```sql
-- Connect to production database
psql -d local_Merlin_3

-- View recent clicks
SELECT
  tracking_id,
  click_source,
  clicked_at,
  ip_address
FROM link_clicks
ORDER BY clicked_at DESC
LIMIT 20;
```

### Check API Logs

```bash
# DigitalOcean App Platform
# Go to: App → Runtime Logs
# Filter for: "tracking-ingest"
```

---

## Success Criteria

- [ ] **Local Tests Pass:** All 6 tests in `test_tracking_ingest.py` pass
- [ ] **Code Merged:** Changes merged to main branch
- [ ] **Deployed:** DigitalOcean shows "Deployed successfully"
- [ ] **Health Check:** `/health` endpoint returns 200 OK
- [ ] **Authentication:** `/test` endpoint requires valid API key
- [ ] **Batch Processing:** `/batch` endpoint accepts and stores events
- [ ] **Database Storage:** Events appear in `link_clicks` table
- [ ] **Documentation:** steve-glen.com team has integration details

---

## Timeline

**Estimated Time to Production:**
- Local testing: 15 minutes
- Code merge: 5 minutes
- DigitalOcean deployment: 5-10 minutes (automatic)
- Production testing: 10 minutes
- steve-glen.com configuration: 1-2 hours

**Total:** ~30 minutes for deployment, then hand off to steve-glen.com team

---

## Next Steps After Deployment

1. ✅ Verify API is live and responding
2. ✅ Get production API key
3. ✅ Share integration details with steve-glen.com team
4. ✅ Monitor initial click events
5. ✅ Verify end-to-end flow works
6. ✅ Set up monitoring/alerting

---

**Current Status:** Ready for local testing → deployment

**Contact:** Check `QUICK_START_STEVE_GLEN_COM.md` for steve-glen.com integration details
