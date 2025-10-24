# Quick Start Guide for steve-glen.com Integration

**Production API Endpoint:** `https://merlin-sea-turtle-app-ckmbz.ondigitalocean.app`

---

## Copy-Paste Configuration for steve-glen.com

### Environment Variables

```bash
# API Endpoints
TRACKING_API_URL=https://merlin-sea-turtle-app-ckmbz.ondigitalocean.app/api/tracking-ingest/batch
LOOKUP_API_URL=https://merlin-sea-turtle-app-ckmbz.ondigitalocean.app/api/link-tracking/lookup

# Authentication (get this from production .env)
WEBHOOK_API_KEY=YOUR_API_KEY_HERE

# Batching Configuration
TRACKING_BATCH_SIZE=100
TRACKING_BATCH_INTERVAL_SECONDS=60
```

---

## Test the Connection

### 1. Health Check (No Auth Required)

```bash
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

### 2. Test Authentication

```bash
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

### 3. Send Test Batch

```bash
curl -X POST https://merlin-sea-turtle-app-ckmbz.ondigitalocean.app/api/tracking-ingest/batch \
  -H "X-API-Key: YOUR_API_KEY_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "events": [{
      "tracking_id": "test-uuid-12345",
      "clicked_at": "2025-10-22T14:30:00Z",
      "ip_address": "192.168.1.1",
      "user_agent": "Mozilla/5.0 Test",
      "click_source": "linkedin"
    }]
  }'
```

---

## JavaScript Implementation for steve-glen.com

### Full Click Handler Code

```javascript
// ============================================================================
// steve-glen.com Link Tracker Integration
// Handles: https://steve-glen.com/linkedin?uuid=dfsgzzpzpweeAFGJJEkdlfjoxbvnv
// ============================================================================

const TRACKING_API_URL = 'https://merlin-sea-turtle-app-ckmbz.ondigitalocean.app/api/tracking-ingest/batch';
const LOOKUP_API_URL = 'https://merlin-sea-turtle-app-ckmbz.ondigitalocean.app/api/link-tracking/lookup';
const API_KEY = process.env.WEBHOOK_API_KEY;

// Queue for batching tracking events
const trackingQueue = [];
const retryQueue = [];

// ============================================================================
// Click Handler - Main Entry Point
// ============================================================================

async function handleClick(req, res) {
  try {
    // 1. Extract tracking data from request
    const trackingId = req.query.uuid;
    const clickSource = req.path.substring(1); // Remove leading /

    // 2. Validate UUID format
    if (!trackingId || !/^[a-zA-Z0-9-]{1,100}$/.test(trackingId)) {
      console.warn('Invalid UUID format:', trackingId);
      return res.status(400).send('Invalid tracking ID');
    }

    // 3. Capture tracking data (minimal required fields)
    const trackingEvent = {
      tracking_id: trackingId,
      clicked_at: new Date().toISOString(),
      ip_address: req.ip || req.connection.remoteAddress,
      user_agent: req.headers['user-agent'] || '',
      click_source: clickSource
      // Note: referrer_url not needed - analytics handled by main system
      // Note: session_id not needed - single-click tracking is sufficient
      // Note: metadata not needed - keep it simple
    };

    // 4. Add to batch queue (non-blocking)
    trackingQueue.push(trackingEvent);
    console.log(`Queued tracking event: ${trackingId} (${clickSource})`);

    // 5. Send batch if queue is full (async, don't wait)
    if (trackingQueue.length >= 100) {
      const batch = trackingQueue.splice(0, 100);
      sendTrackingBatch(batch).catch(err => {
        console.error('Batch send failed:', err);
        retryQueue.push(...batch);
      });
    }

    // 6. Lookup destination URL
    const destinationUrl = await lookupDestination(trackingId);

    if (!destinationUrl) {
      console.error(`Tracking ID not found: ${trackingId}`);
      return res.redirect('https://steveglen.com/404');
    }

    // 7. Redirect to destination
    console.log(`Redirecting ${trackingId} to ${destinationUrl}`);
    res.redirect(302, destinationUrl);

  } catch (error) {
    console.error('Click handler error:', error);
    res.status(500).send('Service temporarily unavailable');
  }
}

// ============================================================================
// Destination Lookup
// ============================================================================

async function lookupDestination(trackingId) {
  try {
    const response = await fetch(`${LOOKUP_API_URL}/${trackingId}`, {
      method: 'GET',
      headers: {
        'X-API-Key': API_KEY
      },
      timeout: 3000 // 3 second timeout
    });

    if (!response.ok) {
      console.error(`Lookup failed: ${response.status} ${response.statusText}`);
      return null;
    }

    const data = await response.json();
    return data.destination_url;

  } catch (error) {
    console.error('Lookup error:', error);
    return null;
  }
}

// ============================================================================
// Batch Sending
// ============================================================================

async function sendTrackingBatch(events) {
  if (!events || events.length === 0) {
    return;
  }

  try {
    console.log(`Sending batch of ${events.length} events to API...`);

    const response = await fetch(TRACKING_API_URL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-API-Key': API_KEY
      },
      body: JSON.stringify({ events }),
      timeout: 10000 // 10 second timeout
    });

    const result = await response.json();

    if (result.success) {
      console.log(`✅ Successfully sent ${result.results.successful} events`);
    } else {
      console.warn(`⚠️ Partial success: ${result.results.failed} events failed`);
      console.error('Failed events:', result.results.errors);
    }

    return result;

  } catch (error) {
    console.error('❌ Failed to send tracking batch:', error.message);
    throw error;
  }
}

// ============================================================================
// Periodic Batch Sender (runs every 60 seconds)
// ============================================================================

setInterval(() => {
  // Send any queued events
  if (trackingQueue.length > 0) {
    const batch = trackingQueue.splice(0, 500); // Max 500 per batch
    sendTrackingBatch(batch).catch(err => {
      console.error('Periodic batch send failed:', err);
      retryQueue.push(...batch);
    });
  }

  // Retry failed events
  if (retryQueue.length > 0) {
    const retryBatch = retryQueue.splice(0, 100);
    sendTrackingBatch(retryBatch).catch(err => {
      console.error('Retry failed, discarding events:', err);
    });
  }
}, 60000); // Every 60 seconds

// ============================================================================
// Express Route Setup
// ============================================================================

const express = require('express');
const app = express();

// Register all tracking routes
app.get('/linkedin', handleClick);
app.get('/calendly', handleClick);
app.get('/portfolio', handleClick);
app.get('/github', handleClick);
app.get('/website', handleClick);

// Health check
app.get('/health', (req, res) => {
  res.json({
    status: 'healthy',
    service: 'steve-glen.com link tracker',
    queue_size: trackingQueue.length,
    retry_queue_size: retryQueue.length
  });
});

// Start server
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`steve-glen.com link tracker running on port ${PORT}`);
  console.log(`Tracking API: ${TRACKING_API_URL}`);
  console.log(`Lookup API: ${LOOKUP_API_URL}`);
});

module.exports = { handleClick, sendTrackingBatch, lookupDestination };
```

---

## Expected URL Flow

### Example 1: LinkedIn Profile Click

**URL in Resume:**
```
https://steve-glen.com/linkedin?uuid=dfsgzzpzpweeAFGJJEkdlfjoxbvnv
```

**Flow:**
1. Recruiter clicks link
2. steve-glen.com receives request
3. Extracts: `tracking_id = "dfsgzzpzpweeAFGJJEkdlfjoxbvnv"`, `click_source = "linkedin"`
4. Queues tracking event
5. Calls lookup API: `GET https://merlin-sea-turtle-app-ckmbz.ondigitalocean.app/api/link-tracking/lookup/dfsgzzpzpweeAFGJJEkdlfjoxbvnv`
6. Receives: `{"destination_url": "https://linkedin.com/in/steveglen"}`
7. Redirects recruiter: `HTTP 302 → https://linkedin.com/in/steveglen`
8. Later, sends batch: `POST https://merlin-sea-turtle-app-ckmbz.ondigitalocean.app/api/tracking-ingest/batch`

### Example 2: Calendly Booking Click

**URL in Cover Letter:**
```
https://steve-glen.com/calendly?uuid=AdjoEJogidjwqpsljdkjlsdkx
```

**Same flow, different values:**
- `tracking_id = "AdjoEJogidjwqpsljdkjlsdkx"`
- `click_source = "calendly"`
- Redirects to: `https://calendly.com/steveglen/30min`

---

## Batch Request Format

**Endpoint:** `POST https://merlin-sea-turtle-app-ckmbz.ondigitalocean.app/api/tracking-ingest/batch`

**Headers:**
```
Content-Type: application/json
X-API-Key: YOUR_API_KEY_HERE
```

**Body:**
```json
{
  "events": [
    {
      "tracking_id": "dfsgzzpzpweeAFGJJEkdlfjoxbvnv",
      "clicked_at": "2025-10-22T14:30:00Z",
      "ip_address": "203.0.113.42",
      "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
      "click_source": "linkedin"
    }
  ]
}
```

**Note:** Only 5 fields needed! The main system handles analytics matching internally using the tracking_id.

---

## Monitoring & Troubleshooting

### Check API Health

```bash
curl https://merlin-sea-turtle-app-ckmbz.ondigitalocean.app/api/tracking-ingest/health
```

### Common Issues

**401 Unauthorized:**
- Check `WEBHOOK_API_KEY` matches production value
- Verify `X-API-Key` header is sent with every request

**404 Not Found (on lookup):**
- Tracking ID doesn't exist in database
- Redirect user to error page

**500 Internal Server Error:**
- Check API logs
- Verify database connectivity
- Check if `link_clicks` table exists

### View Logs

On production server:
```bash
# View recent API logs
tail -f /var/log/your-app/access.log

# Check for errors
grep "tracking-ingest" /var/log/your-app/error.log
```

---

## Production Deployment Checklist

### steve-glen.com Configuration

- [ ] Environment variables set:
  - [ ] `TRACKING_API_URL=https://merlin-sea-turtle-app-ckmbz.ondigitalocean.app/api/tracking-ingest/batch`
  - [ ] `LOOKUP_API_URL=https://merlin-sea-turtle-app-ckmbz.ondigitalocean.app/api/link-tracking/lookup`
  - [ ] `WEBHOOK_API_KEY=<value from production .env>`

- [ ] Code deployed:
  - [ ] Click handler routes (`/linkedin`, `/calendly`, etc.)
  - [ ] Batch sending logic
  - [ ] Periodic interval (60s)
  - [ ] Error handling and retry logic

- [ ] Testing:
  - [ ] Health check returns 200
  - [ ] Test endpoint returns authenticated
  - [ ] Sample batch sends successfully
  - [ ] Redirect flow works end-to-end

### Job Application System

- [ ] API endpoints deployed and accessible
- [ ] Health check responding: `curl https://merlin-sea-turtle-app-ckmbz.ondigitalocean.app/api/tracking-ingest/health`
- [ ] Test endpoint requires auth: `curl -X POST .../test`
- [ ] Database `link_clicks` table ready

---

## Get API Key

On your production server:

```bash
# SSH into production
ssh your-server

# Get API key
grep WEBHOOK_API_KEY /path/to/your/app/.env

# Output will be something like:
# WEBHOOK_API_KEY=abc123xyz789yourAPIkeyHere
```

Use this value in steve-glen.com's `WEBHOOK_API_KEY` environment variable.

---

## Support

If you encounter issues:

1. **Test health endpoint first:** `curl https://merlin-sea-turtle-app-ckmbz.ondigitalocean.app/api/tracking-ingest/health`
2. **Test authentication:** Use `/test` endpoint with API key
3. **Check API key:** Verify it matches production `.env`
4. **Review logs:** Check both steve-glen.com and production API logs
5. **Test with minimal request:** Just `tracking_id` field

---

**Production API:** `https://merlin-sea-turtle-app-ckmbz.ondigitalocean.app`

**Ready to integrate!** 🚀
