# Production Endpoint Configuration

**For steve-glen.com Link Tracker Integration**

---

## API Endpoint URL

```
https://merlin-sea-turtle-app-ckmbz.ondigitalocean.app/api/tracking-ingest/batch
```

**Production Domain:** `https://merlin-sea-turtle-app-ckmbz.ondigitalocean.app`

---

## API Authentication

**Header Name:** `X-API-Key`

**API Key Value:** (Get from your production `.env` file)

```bash
# On your production server, run:
grep WEBHOOK_API_KEY .env
```

This will output something like:
```
WEBHOOK_API_KEY=your_actual_api_key_here
```

Use the value after the `=` sign.

---

## Request Format Template

Copy this template to your steve-glen.com link tracker system:

```json
{
  "events": [
    {
      "tracking_id": "string (required)",
      "clicked_at": "ISO 8601 datetime (optional)",
      "ip_address": "string (optional)",
      "user_agent": "string (optional)",
      "referrer_url": "string (optional)",
      "click_source": "string (optional)",
      "session_id": "string (optional)",
      "metadata": {
        "any_custom_field": "any_value"
      }
    }
  ]
}
```

---

## Example Request with curl

```bash
curl -X POST https://merlin-sea-turtle-app-ckmbz.ondigitalocean.app/api/tracking-ingest/batch \
  -H "X-API-Key: YOUR_API_KEY_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "events": [
      {
        "tracking_id": "dfsgzzpzpweeAFGJJEkdlfjoxbvnv",
        "clicked_at": "2025-10-22T14:30:00Z",
        "ip_address": "192.168.1.1",
        "user_agent": "Mozilla/5.0...",
        "referrer_url": "https://indeed.com",
        "click_source": "linkedin"
      }
    ]
  }'
```

---

## Testing the Connection

### 1. Health Check (No Auth Required)

```bash
curl https://merlin-sea-turtle-app-ckmbz.ondigitalocean.app/api/tracking-ingest/health
```

Expected Response:
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

Expected Response:
```json
{
  "success": true,
  "message": "API connection successful",
  "authenticated": true,
  "timestamp": "2025-10-22T14:40:00Z"
}
```

---

## Rate Limits

- **Current:** No rate limiting (unlimited requests)
- **Batch Size:** Maximum 1000 events per request
- **Recommendation:** Send batches of 100-500 events for optimal performance

---

## Error Responses

### 401 Unauthorized (Invalid API Key)
```json
{
  "success": false,
  "error": "Unauthorized",
  "message": "Valid API key required in X-API-Key header"
}
```

**Fix:** Check that your `X-API-Key` header matches the production `WEBHOOK_API_KEY`.

### 400 Bad Request (Validation Error)
```json
{
  "success": false,
  "error": "Validation Failed",
  "message": "One or more events failed validation",
  "validation_errors": [
    "Event 1: Missing required field: tracking_id"
  ]
}
```

**Fix:** Ensure all events have at least a `tracking_id` field.

---

## Summary Checklist

**Information needed for steve-glen.com configuration:**

- [ ] **Production URL:** `https://merlin-sea-turtle-app-ckmbz.ondigitalocean.app/api/tracking-ingest/batch`
- [ ] **API Key:** Value from `WEBHOOK_API_KEY` in production `.env`
- [ ] **Request Format:** Use template from this document
- [ ] **Test Connection:** Verify `/health` and `/test` endpoints work

---

## Quick Reference

| Item | Value |
|------|-------|
| **Endpoint** | `POST /api/tracking-ingest/batch` |
| **Auth Header** | `X-API-Key` |
| **Content Type** | `application/json` |
| **Required Field** | `tracking_id` |
| **Batch Limit** | 1000 events max |
| **Health Check** | `GET /api/tracking-ingest/health` |

---

**Next Step:** Provide this information to the steve-glen.com link tracker system configuration.
