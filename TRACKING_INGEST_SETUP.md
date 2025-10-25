# Tracking Ingest API Setup - Quick Start Guide

**Created:** 2025-10-22
**Purpose:** Receive link tracking data from steve-glen.com domain

---

## What Was Created

✅ **API Endpoint** to receive batched tracking events from your steve-glen.com link tracker
✅ **Authentication** using existing WEBHOOK_API_KEY
✅ **Database Integration** storing clicks in the `link_clicks` table
✅ **Comprehensive Documentation** with code examples for integration
✅ **Test Suite** to verify everything works

---

## Files Created

### 1. API Implementation
**File:** `modules/link_tracking/tracking_ingest_api.py`
- Main API endpoint: `POST /api/tracking-ingest/batch`
- Test endpoint: `POST /api/tracking-ingest/test`
- Health check: `GET /api/tracking-ingest/health`

### 2. Documentation
**File:** `docs/api/tracking-ingest-integration-guide.md`
- Complete integration guide with examples
- Error handling best practices
- JavaScript and Python code samples

### 3. Request Templates
**Files:**
- `docs/api/tracking-ingest-request-template.json` (Full example)
- `docs/api/tracking-ingest-minimal-template.json` (Minimal example)

### 4. Test Script
**File:** `test_tracking_ingest.py`
- Comprehensive test suite
- Run after starting the Flask server

---

## Quick Start - Testing Locally

### Step 1: Get Your API Key

Check your `.env` file for the `WEBHOOK_API_KEY`:

```bash
grep WEBHOOK_API_KEY .env
```

If not set, add it to your `.env` file:

```bash
echo "WEBHOOK_API_KEY=your_secure_key_here" >> .env
```

### Step 2: Start the Flask Server

```bash
python app_modular.py
```

Look for this line in the output:
```
Tracking Ingest API registered successfully
```

### Step 3: Run the Test Suite

In a new terminal:

```bash
# Make sure WEBHOOK_API_KEY is set in your environment
export WEBHOOK_API_KEY="your_key_here"

# Run the tests
python test_tracking_ingest.py
```

Expected output:
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

### Step 4: Test with curl

```bash
# Test health check (no auth)
curl http://localhost:5001/api/tracking-ingest/health

# Test authentication
curl -X POST http://localhost:5001/api/tracking-ingest/test \
  -H "X-API-Key: your_key_here" \
  -H "Content-Type: application/json"

# Send a test batch
curl -X POST http://localhost:5001/api/tracking-ingest/batch \
  -H "X-API-Key: your_key_here" \
  -H "Content-Type: application/json" \
  -d '{
    "events": [
      {
        "tracking_id": "test-123",
        "clicked_at": "2025-10-22T14:30:00Z",
        "ip_address": "192.168.1.1",
        "click_source": "test"
      }
    ]
  }'
```

---

## Production Deployment

### Step 1: Environment Variables

On your production server, ensure `WEBHOOK_API_KEY` is set:

```bash
# In your production .env file
WEBHOOK_API_KEY=your_production_api_key_here
```

### Step 2: Deploy Code

The API endpoint is now part of your Flask app and will be available at:

```
https://your-production-domain.com/api/tracking-ingest/batch
```

### Step 3: Configure steve-glen.com Domain

In your steve-glen.com link tracker system, configure:

**API Endpoint URL:**
```
https://your-production-domain.com/api/tracking-ingest/batch
```

**API Key Header:**
```
X-API-Key: your_production_api_key_here
```

**Request Format:**
Use the template from `docs/api/tracking-ingest-request-template.json`

---

## Expected Request Format

### Minimal (Only Required Field)

```json
{
  "events": [
    {
      "tracking_id": "linkedin-profile-abc123"
    }
  ]
}
```

### Full (All Optional Fields)

```json
{
  "events": [
    {
      "tracking_id": "linkedin-profile-abc123",
      "clicked_at": "2025-10-22T14:30:00Z",
      "ip_address": "192.168.1.1",
      "user_agent": "Mozilla/5.0...",
      "referrer_url": "https://indeed.com/job/xyz",
      "click_source": "linkedin",
      "session_id": "optional-uuid",
      "metadata": {
        "campaign": "fall-2025",
        "custom_field": "any_value"
      }
    }
  ]
}
```

### Field Descriptions

| Field | Required | Description |
|-------|----------|-------------|
| `tracking_id` | **Yes** | Unique identifier for the tracked link |
| `clicked_at` | No | ISO 8601 timestamp (defaults to server time) |
| `ip_address` | No | Client IP address |
| `user_agent` | No | Browser user agent string |
| `referrer_url` | No | HTTP Referer header |
| `click_source` | No | Source identifier (e.g., "linkedin", "calendly") |
| `session_id` | No | Optional session tracking ID |
| `metadata` | No | Custom JSON object for additional data |

---

## Integration Code Examples

### JavaScript Example (for steve-glen.com)

```javascript
const API_URL = 'https://your-production-domain.com/api/tracking-ingest/batch';
const API_KEY = 'your_api_key_here';

async function sendTrackingBatch(events) {
  const response = await fetch(API_URL, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-API-Key': API_KEY
    },
    body: JSON.stringify({ events })
  });

  return await response.json();
}

// Usage
const events = [
  {
    tracking_id: 'linkedin-abc123',
    clicked_at: new Date().toISOString(),
    ip_address: '192.168.1.1',
    click_source: 'linkedin'
  }
];

sendTrackingBatch(events);
```

### Python Example

```python
import requests

API_URL = 'https://your-production-domain.com/api/tracking-ingest/batch'
API_KEY = 'your_api_key_here'

def send_tracking_batch(events):
    headers = {
        'Content-Type': 'application/json',
        'X-API-Key': API_KEY
    }
    response = requests.post(API_URL, headers=headers, json={'events': events})
    return response.json()

# Usage
events = [
    {
        'tracking_id': 'linkedin-abc123',
        'clicked_at': '2025-10-22T14:30:00Z',
        'ip_address': '192.168.1.1',
        'click_source': 'linkedin'
    }
]

send_tracking_batch(events)
```

---

## Troubleshooting

### Issue: "Could not register Tracking Ingest API"

**Solution:** Check the Flask server logs for import errors. Ensure all dependencies are installed.

### Issue: 401 Unauthorized

**Solution:** Verify the `X-API-Key` header matches the `WEBHOOK_API_KEY` in your `.env` file.

### Issue: 400 Bad Request

**Solution:** Check the request format. At minimum, you need:
```json
{
  "events": [
    {"tracking_id": "some-id"}
  ]
}
```

### Issue: Events not appearing in database

**Solution:**
1. Check if the `link_clicks` table exists in your database
2. Verify database connection is working
3. Check server logs for database errors

---

## Database Schema

Events are stored in the `link_clicks` table:

```sql
CREATE TABLE link_clicks (
    click_id UUID PRIMARY KEY,
    tracking_id VARCHAR(100) REFERENCES link_tracking(tracking_id),
    clicked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ip_address VARCHAR(45),
    user_agent TEXT,
    referrer_url VARCHAR(1000),
    session_id VARCHAR(100),
    click_source VARCHAR(50),
    metadata JSON
);
```

---

## API Endpoints Summary

| Endpoint | Method | Auth Required | Purpose |
|----------|--------|---------------|---------|
| `/api/tracking-ingest/health` | GET | No | Health check |
| `/api/tracking-ingest/test` | POST | Yes | Test connection |
| `/api/tracking-ingest/batch` | POST | Yes | Receive tracking events |

---

## Next Steps

1. ✅ Test locally using `test_tracking_ingest.py`
2. ✅ Verify events are being stored in database
3. ✅ Deploy to production
4. ✅ Configure steve-glen.com to send events to production endpoint
5. ✅ Monitor logs for any errors
6. ✅ Verify tracking data is flowing correctly

---

## Additional Resources

- **Full Integration Guide:** `docs/api/tracking-ingest-integration-guide.md`
- **Request Templates:** `docs/api/tracking-ingest-*.json`
- **Test Script:** `test_tracking_ingest.py`
- **API Code:** `modules/link_tracking/tracking_ingest_api.py`

---

## Support

For issues or questions:
1. Check the integration guide: `docs/api/tracking-ingest-integration-guide.md`
2. Review server logs for error messages
3. Test with the `/health` and `/test` endpoints first
4. Verify API key is correct in both systems

---

**Status:** ✅ Ready for testing and deployment
