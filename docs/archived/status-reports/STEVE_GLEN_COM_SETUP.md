---
title: "Steve Glen Com Setup"
type: technical_doc
component: general
status: draft
tags: []
---

# steve-glen.com Integration - Complete Setup Guide

**System Flow:** This system generates UUIDs → inserts them in resumes/cover letters → steve-glen.com tracks clicks → sends data back via API

---

## System Overview

```
┌──────────────────────────────────────────────────────────────────┐
│ 1. JOB APPLICATION SYSTEM (This System)                         │
│    Generates tracked links when creating resume/cover letter    │
├──────────────────────────────────────────────────────────────────┤
│ • Generate UUID: "dfsgzzpzpweeAFGJJEkdlfjoxbvnv"               │
│ • Store in link_tracking table:                                 │
│   - tracking_id: "dfsgzzpzpweeAFGJJEkdlfjoxbvnv"               │
│   - link_function: "LinkedIn"                                   │
│   - original_url: "https://linkedin.com/in/steveglen"          │
│   - redirect_url: "https://steve-glen.com/linkedin?uuid=..."   │
│ • Insert redirect_url into document template                    │
└──────────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────────┐
│ 2. DOCUMENT GENERATION                                           │
│    Resume/cover letter includes the tracked link                │
├──────────────────────────────────────────────────────────────────┤
│ LinkedIn: https://steve-glen.com/linkedin?uuid=dfsgz...         │
│ Calendly: https://steve-glen.com/calendly?uuid=AdjoE...         │
└──────────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────────┐
│ 3. RECRUITER CLICKS LINK                                         │
│    Browser requests: steve-glen.com/linkedin?uuid=...           │
└──────────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────────┐
│ 4. STEVE-GLEN.COM DOMAIN (External Service)                     │
│    Captures tracking data and redirects user                    │
├──────────────────────────────────────────────────────────────────┤
│ • Extract UUID from query: "dfsgzzpzpweeAFGJJEkdlfjoxbvnv"     │
│ • Capture: IP, user agent, referrer, timestamp                 │
│ • Determine click_source from path: "linkedin"                  │
│ • Lookup destination: "https://linkedin.com/in/steveglen"      │
│ • Redirect user with HTTP 302                                   │
│ • Queue event for batching                                      │
└──────────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────────┐
│ 5. STEVE-GLEN.COM BATCHES EVENTS                                │
│    Sends batches to this system's API                           │
├──────────────────────────────────────────────────────────────────┤
│ POST https://production-url.com/api/tracking-ingest/batch       │
│ {                                                                │
│   "events": [{                                                   │
│     "tracking_id": "dfsgzzpzpweeAFGJJEkdlfjoxbvnv",            │
│     "clicked_at": "2025-10-22T14:30:00Z",                      │
│     "ip_address": "203.0.113.42",                              │
│     "click_source": "linkedin"                                  │
│   }]                                                             │
│ }                                                                │
└──────────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────────┐
│ 6. JOB APPLICATION SYSTEM (This System)                         │
│    Receives and stores tracking data                            │
├──────────────────────────────────────────────────────────────────┤
│ • Validate tracking_id matches link_tracking table              │
│ • Insert into link_clicks table                                 │
│ • Return success response                                        │
└──────────────────────────────────────────────────────────────────┘
```

---

## Configuration Required

### 1. This System (Job Application System)

#### Update Redirect URL Format

**Current Code** (`modules/link_tracking/secure_link_tracker.py:134`):
```python
redirect_url = f"{self.base_redirect_url}/{tracking_id}"
# Creates: http://localhost:5000/track/dfsgzzpzpweeAFGJJEkdlfjoxbvnv
```

**Should Be Updated To:**
```python
# Map link_function to URL path
function_to_path = {
    'LinkedIn': 'linkedin',
    'Calendly': 'calendly',
    'Portfolio': 'portfolio',
    'GitHub': 'github',
    'Website': 'website'
}

path = function_to_path.get(link_function, 'link').lower()
redirect_url = f"{self.base_redirect_url}/{path}?uuid={tracking_id}"
# Creates: https://steve-glen.com/linkedin?uuid=dfsgzzpzpweeAFGJJEkdlfjoxbvnv
```

#### Update Environment Variable

**File:** `.env`

**Current:**
```bash
BASE_REDIRECT_URL=http://localhost:5000/track
```

**Update To:**
```bash
BASE_REDIRECT_URL=https://steve-glen.com
```

**For Production (.env on server):**
```bash
BASE_REDIRECT_URL=https://steve-glen.com
WEBHOOK_API_KEY=your_production_api_key_here
```

---

### 2. steve-glen.com Domain Configuration

#### Required: UUID → Destination URL Lookup

steve-glen.com needs to know where to redirect each UUID. Two approaches:

##### **Option A: Query This System's API (Recommended)**

steve-glen.com calls an API endpoint to get the destination URL:

**Create New Endpoint in This System:**
```python
# modules/link_tracking/link_tracking_api.py

@link_tracking_api_bp.route("/lookup/<tracking_id>", methods=["GET"])
def lookup_destination(tracking_id: str):
    """
    Get destination URL for a tracking ID
    Used by steve-glen.com to perform redirects
    """
    from modules.database.database_manager import DatabaseManager

    db = DatabaseManager()

    query = """
        SELECT original_url, link_function, is_active
        FROM link_tracking
        WHERE tracking_id = %s
    """

    result = db.execute_query(query, (tracking_id,))

    if not result or len(result) == 0:
        return jsonify({"error": "Tracking ID not found"}), 404

    row = result[0]

    if not row[2]:  # is_active
        return jsonify({"error": "Link is inactive"}), 410

    return jsonify({
        "tracking_id": tracking_id,
        "destination_url": row[0],
        "link_function": row[1]
    }), 200
```

**steve-glen.com Usage:**
```javascript
async function handleClick(req, res) {
  const trackingId = req.query.uuid;

  // Query the job application system API
  const response = await fetch(
    `https://production-url.com/api/link-tracking/lookup/${trackingId}`
  );

  const data = await response.json();

  if (!response.ok) {
    return res.redirect('https://steveglen.com/404');
  }

  // Redirect to destination
  res.redirect(302, data.destination_url);
}
```

##### **Option B: Sync Database Table to steve-glen.com**

Replicate the `link_tracking` table to steve-glen.com's database:

```sql
-- On steve-glen.com database
CREATE TABLE url_mappings (
    tracking_id VARCHAR(100) PRIMARY KEY,
    destination_url VARCHAR(1000) NOT NULL,
    link_function VARCHAR(50),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Sync Method 1: API Webhook** (when link is created, notify steve-glen.com)

**Sync Method 2: Periodic Sync** (every 5 minutes, sync new links)

---

## steve-glen.com Implementation

### Click Handler Code

```javascript
// Server: steve-glen.com
// Handles requests like: https://steve-glen.com/linkedin?uuid=dfsgzzpzpweeAFGJJEkdlfjoxbvnv

const TRACKING_API_URL = 'https://production-url.com/api/tracking-ingest/batch';
const LOOKUP_API_URL = 'https://production-url.com/api/link-tracking/lookup';
const API_KEY = process.env.WEBHOOK_API_KEY;

// Queue for batching events
const trackingQueue = [];

async function handleClick(req, res) {
  const trackingId = req.query.uuid;
  const clickSource = req.path.substring(1); // Remove leading /

  // Validate UUID format
  if (!trackingId || !/^[a-zA-Z0-9-]{1,100}$/.test(trackingId)) {
    return res.status(400).send('Invalid tracking ID');
  }

  // Capture tracking data
  const trackingEvent = {
    tracking_id: trackingId,
    clicked_at: new Date().toISOString(),
    ip_address: req.ip || req.connection.remoteAddress,
    user_agent: req.headers['user-agent'],
    referrer_url: req.headers['referer'] || req.headers['referrer'],
    click_source: clickSource,
    session_id: req.sessionID, // If using express-session
    metadata: {
      host: req.headers.host,
      protocol: req.protocol
    }
  };

  // Add to batch queue
  trackingQueue.push(trackingEvent);

  // Send batch if queue is full
  if (trackingQueue.length >= 100) {
    sendTrackingBatch(trackingQueue.splice(0, 100));
  }

  // Lookup destination URL
  try {
    const response = await fetch(`${LOOKUP_API_URL}/${trackingId}`);

    if (!response.ok) {
      console.error(`Tracking ID not found: ${trackingId}`);
      return res.redirect('https://steveglen.com/404');
    }

    const data = await response.json();

    // Redirect to destination
    res.redirect(302, data.destination_url);

  } catch (error) {
    console.error('Error looking up destination:', error);
    res.status(500).send('Service temporarily unavailable');
  }
}

async function sendTrackingBatch(events) {
  try {
    const response = await fetch(TRACKING_API_URL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-API-Key': API_KEY
      },
      body: JSON.stringify({ events })
    });

    const result = await response.json();

    if (result.success) {
      console.log(`✅ Sent ${events.length} events successfully`);
    } else {
      console.error(`⚠️ ${result.results.failed} events failed`);
    }
  } catch (error) {
    console.error('Failed to send tracking batch:', error);
    // Store failed events for retry
    retryQueue.push(...events);
  }
}

// Periodic batch sending (every 60 seconds)
setInterval(() => {
  if (trackingQueue.length > 0) {
    const batch = trackingQueue.splice(0, 500);
    sendTrackingBatch(batch);
  }
}, 60000);

// Express route setup
app.get('/linkedin', handleClick);
app.get('/calendly', handleClick);
app.get('/portfolio', handleClick);
app.get('/github', handleClick);
app.get('/website', handleClick);
```

---

## Data Flow Example

### Creating a Tracked Link

**In This System:**
```python
from modules.link_tracking.secure_link_tracker import SecureLinkTracker

tracker = SecureLinkTracker()

result = tracker.create_tracked_link(
    original_url="https://linkedin.com/in/steveglen",
    link_function="LinkedIn",
    job_id="550e8400-e29b-41d4-a716-446655440000",
    application_id="660e8400-e29b-41d4-a716-446655440001",
    link_type="profile",
    description="LinkedIn profile for job application"
)

print(result)
# {
#   "tracking_id": "dfsgzzpzpweeAFGJJEkdlfjoxbvnv",
#   "redirect_url": "https://steve-glen.com/linkedin?uuid=dfsgzzpzpweeAFGJJEkdlfjoxbvnv",
#   "original_url": "https://linkedin.com/in/steveglen",
#   "created_at": "2025-10-22T14:30:00Z"
# }
```

**Database Record Created:**
```sql
-- link_tracking table
INSERT INTO link_tracking (
  tracking_id,
  job_id,
  application_id,
  link_function,
  link_type,
  original_url,
  redirect_url,
  is_active
) VALUES (
  'dfsgzzpzpweeAFGJJEkdlfjoxbvnv',
  '550e8400-e29b-41d4-a716-446655440000',
  '660e8400-e29b-41d4-a716-446655440001',
  'LinkedIn',
  'profile',
  'https://linkedin.com/in/steveglen',
  'https://steve-glen.com/linkedin?uuid=dfsgzzpzpweeAFGJJEkdlfjoxbvnv',
  true
);
```

### Recruiter Clicks Link

**URL in Resume:**
```
https://steve-glen.com/linkedin?uuid=dfsgzzpzpweeAFGJJEkdlfjoxbvnv
```

**steve-glen.com receives request:**
```javascript
// req.path = '/linkedin'
// req.query.uuid = 'dfsgzzpzpweeAFGJJEkdlfjoxbvnv'

// 1. Extract tracking_id
const trackingId = 'dfsgzzpzpweeAFGJJEkdlfjoxbvnv';

// 2. Capture tracking data
{
  tracking_id: 'dfsgzzpzpweeAFGJJEkdlfjoxbvnv',
  clicked_at: '2025-10-22T14:30:15Z',
  ip_address: '203.0.113.42',
  user_agent: 'Mozilla/5.0...',
  referrer_url: 'https://indeed.com/job/12345',
  click_source: 'linkedin'
}

// 3. Lookup destination
// GET https://production-url.com/api/link-tracking/lookup/dfsgzzpzpweeAFGJJEkdlfjoxbvnv
// Response: { destination_url: 'https://linkedin.com/in/steveglen' }

// 4. Redirect
// HTTP 302 → https://linkedin.com/in/steveglen
```

### Tracking Data Sent Back

**steve-glen.com batches and sends:**
```bash
POST https://production-url.com/api/tracking-ingest/batch
X-API-Key: your_api_key_here
Content-Type: application/json

{
  "events": [{
    "tracking_id": "dfsgzzpzpweeAFGJJEkdlfjoxbvnv",
    "clicked_at": "2025-10-22T14:30:15Z",
    "ip_address": "203.0.113.42",
    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "referrer_url": "https://indeed.com/job/12345",
    "click_source": "linkedin"
  }]
}
```

**This System stores in database:**
```sql
-- link_clicks table
INSERT INTO link_clicks (
  click_id,
  tracking_id,
  clicked_at,
  ip_address,
  user_agent,
  referrer_url,
  click_source
) VALUES (
  '770e8400-e29b-41d4-a716-446655440002',
  'dfsgzzpzpweeAFGJJEkdlfjoxbvnv',
  '2025-10-22 14:30:15',
  '203.0.113.42',
  'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
  'https://indeed.com/job/12345',
  'linkedin'
);
```

---

## Testing Checklist

### Phase 1: Local Testing (This System)

- [ ] **Update redirect URL generation**
  - [ ] Modify `secure_link_tracker.py` to use steve-glen.com format
  - [ ] Update `.env`: `BASE_REDIRECT_URL=https://steve-glen.com`
  - [ ] Test link creation: verify redirect_url format

- [ ] **Create lookup endpoint**
  - [ ] Add `/api/link-tracking/lookup/<tracking_id>` endpoint
  - [ ] Test with sample tracking_id
  - [ ] Verify returns destination URL

- [ ] **Test ingest API**
  - [ ] Run `python test_tracking_ingest.py`
  - [ ] Verify all tests pass
  - [ ] Check database for stored clicks

### Phase 2: steve-glen.com Integration

- [ ] **Configure environment**
  - [ ] Set `TRACKING_API_URL` (production ingest endpoint)
  - [ ] Set `LOOKUP_API_URL` (production lookup endpoint)
  - [ ] Set `WEBHOOK_API_KEY` (same as this system)

- [ ] **Implement click handler**
  - [ ] Create route handlers for `/linkedin`, `/calendly`, etc.
  - [ ] Extract UUID from query parameter
  - [ ] Capture tracking data
  - [ ] Queue events for batching

- [ ] **Test redirect flow**
  - [ ] Create test link: `https://steve-glen.com/linkedin?uuid=test123`
  - [ ] Verify lookup API is called
  - [ ] Verify redirect to destination
  - [ ] Check tracking data queued

### Phase 3: End-to-End Testing

- [ ] **Create tracked link in this system**
- [ ] **Manually visit steve-glen.com URL**
- [ ] **Verify redirect works**
- [ ] **Wait for batch to send**
- [ ] **Check `link_clicks` table for event**

### Phase 4: Production Deployment

- [ ] **Deploy to production server**
- [ ] **Update production `.env`**
- [ ] **Test production endpoints**
- [ ] **Monitor logs for errors**

---

## Required API Endpoints Summary

| Endpoint | Purpose | Used By |
|----------|---------|---------|
| `POST /api/tracking-ingest/batch` | Receive tracking events | steve-glen.com → This system |
| `GET /api/link-tracking/lookup/<id>` | Get destination URL | steve-glen.com queries |
| `GET /api/tracking-ingest/health` | Health check | Monitoring |
| `POST /api/tracking-ingest/test` | Test connection | Initial setup |

---

## Next Steps

1. **Update This System**
   - Modify redirect URL generation in `secure_link_tracker.py`
   - Create lookup endpoint (or confirm existing one works)
   - Update `.env` with steve-glen.com URL

2. **Provide steve-glen.com Team**
   - API endpoint URLs (production)
   - API key (WEBHOOK_API_KEY)
   - Request/response format documentation
   - Click handler implementation code

3. **Test Integration**
   - Create test links
   - Verify end-to-end flow
   - Monitor for errors

---

**Ready for implementation!**
