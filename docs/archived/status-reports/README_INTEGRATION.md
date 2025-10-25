---
title: "Readme Integration"
type: technical_doc
component: integration
status: draft
tags: []
---

# Link Tracking Integration - Complete Summary

**Created:** 2025-10-22
**Purpose:** Receive click tracking data from steve-glen.com domain
**Production API:** `https://merlin-sea-turtle-app-ckmbz.ondigitalocean.app`

---

## What Was Built

### ✅ API Endpoint (Receiving System)

**Created:** `modules/link_tracking/tracking_ingest_api.py`

Endpoints:
- `POST /api/tracking-ingest/batch` - Receives batched click events from steve-glen.com
- `POST /api/tracking-ingest/test` - Test connection and authentication
- `GET /api/tracking-ingest/health` - Health check (no auth required)

**Features:**
- API key authentication using existing `WEBHOOK_API_KEY`
- Batch processing (up to 1000 events per request)
- Full input validation
- Error handling and logging
- Stores events in `link_clicks` database table

### ✅ Documentation

**For You (Deployment):**
- `DEPLOYMENT_CHECKLIST.md` - Step-by-step deployment guide
- `TRACKING_INGEST_SETUP.md` - Local testing instructions
- `test_tracking_ingest.py` - Automated test suite

**For steve-glen.com Team:**
- `QUICK_START_STEVE_GLEN_COM.md` - **START HERE** - Copy-paste integration guide
- `PRODUCTION_ENDPOINT_INFO.md` - Production endpoint details
- `STEVE_GLEN_COM_SETUP.md` - Complete integration documentation
- `docs/api/STEVE_GLEN_COM_INTEGRATION.md` - Technical implementation guide

**API Reference:**
- `docs/api/tracking-ingest-integration-guide.md` - Full API documentation
- `docs/api/tracking-ingest-request-template.json` - Request format template
- `docs/api/tracking-ingest-minimal-template.json` - Minimal request example

---

## How It Works

### System Flow

```
┌─────────────────────────────────────────────────────────────┐
│ 1. YOUR SYSTEM (Job Application System)                    │
│    Creates tracked links when generating resume/cover      │
├─────────────────────────────────────────────────────────────┤
│ • Generate UUID: "dfsgzzpzpweeAFGJJEkdlfjoxbvnv"          │
│ • Store in link_tracking table                             │
│ • Insert URL in document:                                  │
│   https://steve-glen.com/linkedin?uuid=dfsgzzp...          │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ 2. RECRUITER CLICKS LINK IN RESUME                         │
│    Browser requests:                                        │
│    https://steve-glen.com/linkedin?uuid=dfsgzzp...         │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ 3. STEVE-GLEN.COM (External Service)                       │
│    Captures tracking data and redirects                    │
├─────────────────────────────────────────────────────────────┤
│ • Extract UUID from query parameter                        │
│ • Capture: IP, user agent, referrer, timestamp            │
│ • Lookup destination: "https://linkedin.com/in/steveglen" │
│ • Redirect recruiter (HTTP 302)                            │
│ • Queue event for batching                                 │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ 4. STEVE-GLEN.COM SENDS BATCH TO YOUR API                 │
│    POST to production API endpoint                         │
├─────────────────────────────────────────────────────────────┤
│ POST https://merlin-sea-turtle-app-ckmbz                   │
│      .ondigitalocean.app/api/tracking-ingest/batch        │
│                                                             │
│ {                                                           │
│   "events": [{                                              │
│     "tracking_id": "dfsgzzpzpweeAFGJJEkdlfjoxbvnv",       │
│     "clicked_at": "2025-10-22T14:30:00Z",                 │
│     "ip_address": "203.0.113.42",                         │
│     "click_source": "linkedin"                             │
│   }]                                                        │
│ }                                                           │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ 5. YOUR SYSTEM STORES TRACKING DATA                        │
│    API validates and stores in database                    │
├─────────────────────────────────────────────────────────────┤
│ • Validate tracking_id and other fields                    │
│ • Insert into link_clicks table                            │
│ • Return success response                                  │
└─────────────────────────────────────────────────────────────┘
```

---

## URL Format

**What goes in resumes/cover letters:**
```
https://steve-glen.com/linkedin?uuid=dfsgzzpzpweeAFGJJEkdlfjoxbvnv
https://steve-glen.com/calendly?uuid=AdjoEJogidjwqpsljdkjlsdkx
```

**URL Components:**
- **Domain:** `steve-glen.com` (external tracking service)
- **Path:** `/linkedin`, `/calendly`, `/portfolio` (becomes `click_source`)
- **Query Param:** `?uuid=xxx` (the tracking ID from your database)

---

## Quick Start

### 1. Test Locally

```bash
# Start Flask server
python app_modular.py

# In another terminal, run tests
python test_tracking_ingest.py
```

**Expected:** All 6 tests pass ✅

### 2. Deploy to Production

```bash
# Merge to main branch
git checkout main
git merge task/03-create-api-connection-with-steve-glencom-domain-se
git push origin main

# DigitalOcean will auto-deploy
```

### 3. Test Production Endpoint

```bash
# Health check (no auth)
curl https://merlin-sea-turtle-app-ckmbz.ondigitalocean.app/api/tracking-ingest/health

# Test auth (replace YOUR_API_KEY)
curl -X POST https://merlin-sea-turtle-app-ckmbz.ondigitalocean.app/api/tracking-ingest/test \
  -H "X-API-Key: YOUR_API_KEY" \
  -H "Content-Type: application/json"
```

### 4. Share with steve-glen.com Team

**Send them:**
- `QUICK_START_STEVE_GLEN_COM.md` (main integration guide)
- Production URL: `https://merlin-sea-turtle-app-ckmbz.ondigitalocean.app`
- API Key from production `.env` (WEBHOOK_API_KEY)

---

## Configuration for steve-glen.com

### Environment Variables They Need

```bash
TRACKING_API_URL=https://merlin-sea-turtle-app-ckmbz.ondigitalocean.app/api/tracking-ingest/batch
LOOKUP_API_URL=https://merlin-sea-turtle-app-ckmbz.ondigitalocean.app/api/link-tracking/lookup
WEBHOOK_API_KEY=<same as your production key>
```

### Request Format They'll Send

```json
{
  "events": [
    {
      "tracking_id": "dfsgzzpzpweeAFGJJEkdlfjoxbvnv",
      "clicked_at": "2025-10-22T14:30:00Z",
      "ip_address": "203.0.113.42",
      "user_agent": "Mozilla/5.0...",
      "referrer_url": "https://indeed.com/job/123",
      "click_source": "linkedin"
    }
  ]
}
```

**Only `tracking_id` is required.** All other fields are optional.

---

## Files Created

### API Implementation
- `modules/link_tracking/tracking_ingest_api.py` - Main API endpoint
- `app_modular.py` - Updated to register new blueprint (line 239-245)

### Testing
- `test_tracking_ingest.py` - Comprehensive test suite

### Documentation
- `DEPLOYMENT_CHECKLIST.md` - Deployment steps
- `QUICK_START_STEVE_GLEN_COM.md` - Integration guide for steve-glen.com
- `PRODUCTION_ENDPOINT_INFO.md` - Production endpoint details
- `STEVE_GLEN_COM_SETUP.md` - Complete integration documentation
- `TRACKING_INGEST_SETUP.md` - Local testing guide
- `docs/api/tracking-ingest-integration-guide.md` - Full API reference
- `docs/api/STEVE_GLEN_COM_INTEGRATION.md` - Technical implementation
- `docs/api/tracking-ingest-request-template.json` - Request template
- `docs/api/tracking-ingest-minimal-template.json` - Minimal request

---

## Database Schema

Events are stored in the existing `link_clicks` table:

```sql
CREATE TABLE link_clicks (
    click_id UUID PRIMARY KEY,
    tracking_id VARCHAR(100),  -- From steve-glen.com URL
    clicked_at TIMESTAMP,       -- When recruiter clicked
    ip_address VARCHAR(45),     -- Recruiter's IP
    user_agent TEXT,            -- Recruiter's browser
    referrer_url VARCHAR(1000), -- Where they came from
    session_id VARCHAR(100),    -- Optional session tracking
    click_source VARCHAR(50),   -- "linkedin", "calendly", etc.
    metadata JSON               -- Additional tracking data
);
```

---

## Next Steps

### Phase 1: Deployment (You)
1. ✅ Code is ready
2. ⏳ Run local tests
3. ⏳ Merge to main branch
4. ⏳ Deploy to DigitalOcean
5. ⏳ Test production endpoint
6. ⏳ Get production API key

### Phase 2: Integration (steve-glen.com Team)
1. ⏳ Receive integration documentation
2. ⏳ Configure environment variables
3. ⏳ Implement click handler code
4. ⏳ Test connection
5. ⏳ Test end-to-end flow
6. ⏳ Deploy to production

### Phase 3: Verification (Both)
1. ⏳ Create test tracked link
2. ⏳ Click link manually
3. ⏳ Verify redirect works
4. ⏳ Check tracking data received
5. ⏳ Monitor for issues

---

## Support

### For Deployment Issues
- See: `DEPLOYMENT_CHECKLIST.md`
- Check DigitalOcean logs
- Verify environment variables

### For Integration Issues
- See: `QUICK_START_STEVE_GLEN_COM.md`
- Test with `/health` and `/test` endpoints
- Verify API key matches production

### For API Questions
- See: `docs/api/tracking-ingest-integration-guide.md`
- Check request format templates
- Review error responses

---

## Production Information

**Endpoint:** `https://merlin-sea-turtle-app-ckmbz.ondigitalocean.app/api/tracking-ingest/batch`

**Authentication:** `X-API-Key` header with `WEBHOOK_API_KEY` value

**Rate Limits:** None (currently unlimited)

**Batch Size:** Max 1000 events per request (recommend 100-500)

**Status:** ⚠️ Not yet deployed (returns 404)

---

## Testing Checklist

- [ ] Local tests pass (run `test_tracking_ingest.py`)
- [ ] Health endpoint accessible
- [ ] Test endpoint requires authentication
- [ ] Batch endpoint validates input
- [ ] Events stored in database
- [ ] Production endpoint live
- [ ] steve-glen.com can connect
- [ ] End-to-end flow works

---

**Ready for deployment!** 🚀

Start with: `DEPLOYMENT_CHECKLIST.md`
