---
title: "Tracking Ingest Integration Guide"
type: guide
component: integration
status: draft
tags: []
---

# Tracking Ingest API Integration Guide

**Version:** 1.0.1 (Updated)
**Last Updated:** 2025-10-24
**Purpose:** External domain integration for steve-glen.com link tracker
**Production URL:** `https://merlin-sea-turtle-app-ckmbz.ondigitalocean.app`

---

## Overview

The Tracking Ingest API receives batched link tracking events from the steve-glen.com custom domain and stores them in the job application system's database.

**Use Case:**
When a recruiter clicks on a tracked link (LinkedIn profile, Calendly booking, etc.) hosted on steve-glen.com, the tracking parameters are captured and batched before being sent to this API endpoint for storage and analytics.

**Key Point:** This system handles all analytics matching internally using `tracking_id` → `job_id` → `application_id` relationships. steve-glen.com only needs to send basic click data.

---

## API Endpoint

### Production URL
```
https://merlin-sea-turtle-app-ckmbz.ondigitalocean.app/api/tracking-ingest/batch
```

### Local Development URL
```
http://localhost:5001/api/tracking-ingest/batch
```

---

## Authentication

All requests require API key authentication via HTTP header:

```
X-API-Key: Y-siA-PexOtwXceZk_E6ohfWJ8VVLHbl9k020WJ5O-fc-yay5HXXvHlG-FPxV65-
```

**How to get the API key:**
1. On the production server, check the `.env` file
2. Look for the `WEBHOOK_API_KEY` environment variable
3. Use this value in all API requests

**Example:**
```bash
curl -X POST https://merlin-sea-turtle-app-ckmbz.ondigitalocean.app/api/tracking-ingest/batch \
  -H "X-API-Key: Y-siA-PexOtwXceZk_E6ohfWJ8VVLHbl9k020WJ5O-fc-yay5HXXvHlG-FPxV65-" \
  -H "Content-Type: application/json" \
  -d @request.json
```

---

## Request Format (Simplified)

### Batch Endpoint: `POST /api/tracking-ingest/batch`

**Content-Type:** `application/json`

**Recommended Request Body:**
```json
{
  "events": [
    {
      "tracking_id": "dfsgzzpzpweeAFGJJEkdlfjoxbvnv",
      "clicked_at": "2025-10-22T14:30:00Z",
      "ip_address": "192.168.1.1",
      "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
      "click_source": "linkedin"
    },
    {
      "tracking_id": "AdjoEJogidjwqpsljdkjlsdkx",
      "clicked_at": "2025-10-22T14:35:00Z",
      "ip_address": "203.0.113.42",
      "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
      "click_source": "calendly"
    }
  ]
}
```

**Minimal Request (Only Required Field):**
```json
{
  "events": [
    {
      "tracking_id": "dfsgzzpzpweeAFGJJEkdlfjoxbvnv"
    }
  ]
}
```

### Field Specifications

| Field | Status | Type | Max Length | Description |
|-------|--------|------|------------|-------------|
| `events` | **Required** | array | 1-1000 items | Array of tracking events |
| `tracking_id` | **Required** | string | 100 chars | UUID from query parameter |
| `clicked_at` | **Recommended** | ISO 8601 string | - | Click timestamp (defaults to server time) |
| `ip_address` | **Recommended** | string | 45 chars | Client IP address (IPv4 or IPv6) |
| `user_agent` | **Recommended** | string | 500 chars | Browser user agent string |
| `click_source` | **Recommended** | string | 50 chars | From URL path ("linkedin", "calendly", etc.) |
| `referrer_url` | Optional (not needed) | string | 1000 chars | Analytics handled internally |
| `session_id` | Optional (not needed) | string | 100 chars | Single-click tracking is sufficient |
| `metadata` | Optional (not needed) | JSON object | - | Keep it simple |

**Why simplified?**
- This system already has full context through `tracking_id` → `job_id` → `application_id` relationships
- No need for `referrer_url` - analytics matching is done via database lookups
- No need for `session_id` - single-click tracking is sufficient
- No need for `metadata` - keep the integration simple


### Date Format

All datetime fields must use ISO 8601 format:
- `2025-10-22T14:30:00Z` (UTC timezone)
- `2025-10-22T14:30:00+00:00` (Explicit UTC)
- `2025-10-22T09:30:00-05:00` (With timezone offset)

---

## Response Format

### Success Response (200 OK)

All events processed successfully:

```json
{
  "success": true,
  "message": "Processed 2 events",
  "results": {
    "total_events": 2,
    "successful": 2,
    "failed": 0,
    "errors": []
  },
  "timestamp": "2025-10-22T14:40:00.123456Z"
}
```

### Partial Success Response (207 Multi-Status)

Some events failed:

```json
{
  "success": false,
  "message": "Processed 2 events",
  "warning": "1 events failed to process",
  "results": {
    "total_events": 2,
    "successful": 1,
    "failed": 1,
    "errors": [
      "Event 2: Invalid tracking_id format"
    ]
  },
  "timestamp": "2025-10-22T14:40:00.123456Z"
}
```

### Error Responses

#### 400 Bad Request (Validation Error)
```json
{
  "success": false,
  "error": "Validation Failed",
  "message": "One or more events failed validation",
  "validation_errors": [
    "Event 1: Missing required field: tracking_id",
    "Event 3: Invalid clicked_at format (must be ISO 8601 datetime)"
  ],
  "timestamp": "2025-10-22T14:40:00.123456Z"
}
```

#### 401 Unauthorized (Invalid API Key)
```json
{
  "success": false,
  "error": "Unauthorized",
  "message": "Valid API key required in X-API-Key header"
}
```

#### 500 Internal Server Error
```json
{
  "success": false,
  "error": "Internal Server Error",
  "message": "Failed to process tracking batch",
  "timestamp": "2025-10-22T14:40:00.123456Z"
}
```

---

## Rate Limiting

**Current Limits:**
- No explicit rate limiting implemented yet
- Batch size limited to 1000 events per request

**Recommendations for sending system:**
- Batch events in groups of 100-500 for optimal performance
- Implement exponential backoff for failed requests
- Cache events locally if API is unavailable

---

## Testing the Integration

### 1. Test Connection and Authentication

**Endpoint:** `POST /api/tracking-ingest/test`

```bash
curl -X POST https://merlin-sea-turtle-app-ckmbz.ondigitalocean.app/api/tracking-ingest/test \
  -H "X-API-Key: Y-siA-PexOtwXceZk_E6ohfWJ8VVLHbl9k020WJ5O-fc-yay5HXXvHlG-FPxV65-" \
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

### 2. Test with Sample Data (Simplified Format)

Create a test file `test-batch.json`:

```json
{
  "events": [
    {
      "tracking_id": "test-uuid-12345",
      "clicked_at": "2025-10-22T14:30:00Z",
      "ip_address": "192.168.1.1",
      "user_agent": "Mozilla/5.0 Test Agent",
      "click_source": "linkedin"
    }
  ]
}
```

Send the test:

```bash
curl -X POST https://merlin-sea-turtle-app-ckmbz.ondigitalocean.app/api/tracking-ingest/batch \
  -H "X-API-Key: Y-siA-PexOtwXceZk_E6ohfWJ8VVLHbl9k020WJ5O-fc-yay5HXXvHlG-FPxV65-" \
  -H "Content-Type: application/json" \
  -d @test-batch.json
```

### 3. Health Check (No Authentication Required)

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

---

## Integration Code Examples

### JavaScript/Node.js Example (Simplified)

```javascript
const API_URL = 'https://merlin-sea-turtle-app-ckmbz.ondigitalocean.app/api/tracking-ingest/batch';
const API_KEY = 'Y-siA-PexOtwXceZk_E6ohfWJ8VVLHbl9k020WJ5O-fc-yay5HXXvHlG-FPxV65-';

async function sendTrackingBatch(events) {
  try {
    const response = await fetch(API_URL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-API-Key': API_KEY
      },
      body: JSON.stringify({ events })
    });

    const result = await response.json();

    if (result.success) {
      console.log(`✅ Successfully sent ${result.results.successful} events`);
    } else {
      console.warn(`⚠️ Partial success: ${result.results.failed} failed`);
      console.error('Errors:', result.results.errors);
    }

    return result;
  } catch (error) {
    console.error('❌ Failed to send tracking batch:', error);
    throw error;
  }
}

// Example usage with simplified format
const eventQueue = [];

function trackClick(trackingId, clickData) {
  eventQueue.push({
    tracking_id: trackingId,
    clicked_at: new Date().toISOString(),
    ip_address: clickData.ip,
    user_agent: clickData.userAgent,
    click_source: clickData.source  // "linkedin", "calendly", etc.
    // Note: No referrer_url, session_id, or metadata needed!
  });

  // Send batch when queue reaches 100 events
  if (eventQueue.length >= 100) {
    sendTrackingBatch([...eventQueue]);
    eventQueue.length = 0;
  }
}

// Flush remaining events periodically
setInterval(() => {
  if (eventQueue.length > 0) {
    sendTrackingBatch([...eventQueue]);
    eventQueue.length = 0;
  }
}, 60000); // Every minute
```

### Python Example (Simplified)

```python
import requests
import json
from datetime import datetime
from typing import List, Dict

API_URL = 'https://merlin-sea-turtle-app-ckmbz.ondigitalocean.app/api/tracking-ingest/batch'
API_KEY = 'Y-siA-PexOtwXceZk_E6ohfWJ8VVLHbl9k020WJ5O-fc-yay5HXXvHlG-FPxV65-'

def send_tracking_batch(events: List[Dict]) -> Dict:
    """Send batched tracking events to the ingest API."""
    headers = {
        'Content-Type': 'application/json',
        'X-API-Key': API_KEY
    }

    payload = {'events': events}

    try:
        response = requests.post(API_URL, headers=headers, json=payload)
        response.raise_for_status()

        result = response.json()

        if result['success']:
            print(f"✅ Successfully sent {result['results']['successful']} events")
        else:
            print(f"⚠️ Partial success: {result['results']['failed']} failed")
            print(f"Errors: {result['results']['errors']}")

        return result

    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to send tracking batch: {e}")
        raise

# Example usage with simplified format
events = [
    {
        'tracking_id': 'dfsgzzpzpweeAFGJJEkdlfjoxbvnv',
        'clicked_at': datetime.utcnow().isoformat() + 'Z',
        'ip_address': '192.168.1.1',
        'user_agent': 'Mozilla/5.0...',
        'click_source': 'linkedin'
        # No referrer_url, session_id, or metadata!
    }
]

send_tracking_batch(events)
```

---

## Error Handling Best Practices

### 1. Implement Retry Logic with Exponential Backoff

```javascript
async function sendWithRetry(events, maxRetries = 3) {
  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      return await sendTrackingBatch(events);
    } catch (error) {
      if (attempt === maxRetries) throw error;

      // Exponential backoff: 1s, 2s, 4s
      const delay = Math.pow(2, attempt - 1) * 1000;
      await new Promise(resolve => setTimeout(resolve, delay));
    }
  }
}
```

### 2. Queue Failed Events for Later

```javascript
const failedEventsQueue = [];

async function sendWithQueueing(events) {
  try {
    const result = await sendTrackingBatch(events);

    if (!result.success) {
      failedEventsQueue.push(...events);
    }
  } catch (error) {
    // Network error - queue all events
    failedEventsQueue.push(...events);
  }
}
```

---

## FAQ

### Q: What fields are actually required?

**A:** Only `tracking_id` is required. However, we strongly recommend sending `clicked_at`, `ip_address`, `user_agent`, and `click_source` for better analytics.

### Q: Why don't you need referrer_url?

**A:** The system already knows the full context through database relationships. When you send `tracking_id`, the system can lookup the associated `job_id`, `application_id`, company name, job title, and application date. The `referrer_url` doesn't add meaningful analytics value.

### Q: Can I still send referrer_url, session_id, or metadata?

**A:** Yes! The API accepts these fields as optional. However, they're not needed and add unnecessary complexity to the integration.

### Q: What timezone should I use for `clicked_at`?

**A:** Always use UTC (Coordinated Universal Time). Format as ISO 8601 with 'Z' suffix: `2025-10-22T14:30:00Z`

### Q: What's the maximum batch size?

**A:** Current limit is 1000 events per request. For optimal performance, send batches of 100-500 events.

---

## Production Deployment Checklist

- [ ] **Environment Variables Set**
  - [ ] `WEBHOOK_API_KEY` configured on production server
  - [ ] API key securely stored (not in code repository)

- [ ] **Sending System Configuration**
  - [ ] API endpoint URL updated to production URL
  - [ ] API key configured in sending system
  - [ ] Batch size optimized (100-500 events recommended)
  - [ ] Error handling and retry logic implemented
  - [ ] Using simplified request format (5 fields)

- [ ] **Testing**
  - [ ] Health check endpoint accessible
  - [ ] Test connection endpoint returns 200 with valid API key
  - [ ] Sample batch successfully processed
  - [ ] Invalid API key returns 401 Unauthorized
  - [ ] Malformed requests return 400 Bad Request

- [ ] **Monitoring**
  - [ ] Server logs monitored for errors
  - [ ] Database storage verified (check `link_clicks` table)
  - [ ] API response times acceptable (<500ms for 100 events)

---

## Related Documentation

- **steve-glen.com Integration Guide:** `QUICK_START_STEVE_GLEN_COM.md` (copy-paste code examples)
- **Request Templates:** `docs/api/tracking-ingest-request-template.json`
- **Deployment Guide:** `DEPLOYMENT_CHECKLIST.md`
- **Quick Start:** `START_HERE.md` (navigation & overview)

---

## Changelog

### Version 1.0.1 (2025-10-24)
- Simplified recommended request format to 5 fields
- Removed referrer_url, session_id, metadata from recommended fields
- Updated production URL to DigitalOcean domain
- Added API key to examples
- Clarified that analytics matching is handled internally

### Version 1.0.0 (2025-10-22)
- Initial release
- Batch ingest endpoint
- API key authentication
- Input validation
- Health check and test endpoints
