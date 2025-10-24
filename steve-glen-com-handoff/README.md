# steve-glen.com Tracking API Integration Package

**Generated:** 2025-10-24
**Purpose:** Complete integration package for steve-glen.com team

---

## 📦 What's Inside

This folder contains everything needed to integrate steve-glen.com with the tracking API.

### 🚀 Start Here

**1. `QUICK_START_STEVE_GLEN_COM.md`** ⭐ **READ THIS FIRST**
- Complete integration guide
- System overview and flow diagram
- JavaScript implementation examples
- Configuration instructions
- Testing procedures

### 🔑 API Key

**2. `STEVE_GLEN_API_KEY.md`** 🔐 **SENSITIVE - PROTECT THIS FILE**
- Dedicated API key for tracking ingest
- Environment variable configuration
- Security features explained
- Test commands with authentication

**Key:** `STEVE_GLEN_TRACKING_API_KEY=wR4kLmN7pQxS9vYzBcTgHjUiOeWqAsXdFrGhKnMbVlCxZaPoIuYtEwQsLkJnHmGf`

### 📚 Reference Documentation

**3. `api-reference/` folder**
- `tracking-ingest-integration-guide.md` - Full API specification
- `tracking-ingest-request-template.json` - Complete request example
- `tracking-ingest-minimal-template.json` - Minimal request example

---

## ✅ Quick Setup (3 Steps)

### Step 1: Add API Key to Environment

```bash
# Add to steve-glen.com .env file
TRACKING_API_URL=https://merlin-sea-turtle-app-ckmbz.ondigitalocean.app/api/tracking-ingest/batch
WEBHOOK_API_KEY=wR4kLmN7pQxS9vYzBcTgHjUiOeWqAsXdFrGhKnMbVlCxZaPoIuYtEwQsLkJnHmGf
```

### Step 2: Test Connection

```bash
curl -X POST https://merlin-sea-turtle-app-ckmbz.ondigitalocean.app/api/tracking-ingest/test \
  -H "X-API-Key: wR4kLmN7pQxS9vYzBcTgHjUiOeWqAsXdFrGhKnMbVlCxZaPoIuYtEwQsLkJnHmGf" \
  -H "Content-Type: application/json"
```

Expected: `{"success": true, "authenticated": true}`

### Step 3: Integrate Code

See `QUICK_START_STEVE_GLEN_COM.md` for complete implementation.

---

## 🔍 API Overview

**Endpoint:** `POST /api/tracking-ingest/batch`
**Authentication:** `X-API-Key` header (see STEVE_GLEN_API_KEY.md)
**Format:** JSON batch of click events

**Minimal Request:**
```json
{
  "events": [
    {
      "tracking_id": "dfsgzzpzpweeAFGJJEkdlfjoxbvnv",
      "clicked_at": "2025-10-24T12:00:00Z",
      "ip_address": "192.168.1.1",
      "user_agent": "Mozilla/5.0...",
      "click_source": "linkedin"
    }
  ]
}
```

Only **5 fields** required:
- `tracking_id` - UUID from query parameter
- `clicked_at` - ISO 8601 timestamp
- `ip_address` - Client IP
- `user_agent` - Client user agent
- `click_source` - Source identifier (linkedin, calendly, etc.)

---

## 🎯 Integration Flow

1. **Client clicks tracked link:**
   ```
   https://steve-glen.com/linkedin?uuid=dfsgzzpzpweeAFGJJEkdlfjoxbvnv
   ```

2. **steve-glen.com captures:**
   - UUID from query parameter → `tracking_id`
   - Timestamp → `clicked_at`
   - Client IP → `ip_address`
   - User agent → `user_agent`
   - Route path → `click_source` (linkedin, calendly, etc.)

3. **steve-glen.com redirects client to destination**

4. **steve-glen.com batches events and sends to API:**
   ```
   POST /api/tracking-ingest/batch
   ```

---

## 📋 File Details

| File | Purpose | Size |
|------|---------|------|
| `README.md` | This file - overview and navigation | - |
| `QUICK_START_STEVE_GLEN_COM.md` | Primary integration guide | 12 KB |
| `STEVE_GLEN_API_KEY.md` | API key and configuration | 4 KB |
| `api-reference/tracking-ingest-integration-guide.md` | Full API specification | 14 KB |
| `api-reference/tracking-ingest-request-template.json` | Complete request example | 600 B |
| `api-reference/tracking-ingest-minimal-template.json` | Minimal request example | 87 B |

---

## 🆘 Support

**Production URL:**
```
https://merlin-sea-turtle-app-ckmbz.ondigitalocean.app
```

**Health Check (No Auth):**
```bash
curl https://merlin-sea-turtle-app-ckmbz.ondigitalocean.app/api/tracking-ingest/health
```

**Available Endpoints:**
- `GET /api/tracking-ingest/health` - Health check (no auth)
- `POST /api/tracking-ingest/test` - Test authentication
- `POST /api/tracking-ingest/batch` - Submit tracking events

---

## 🔐 Security Notes

**This API key is dedicated to tracking ingest only:**
- ✅ Can access: `/api/tracking-ingest/*` endpoints
- ❌ Cannot access: Database, AI, automation, or other APIs
- ✅ Can be revoked independently without affecting other services
- ✅ Follows principle of least privilege

**Keep `STEVE_GLEN_API_KEY.md` secure:**
- Do not commit to public repositories
- Store in environment variables
- Rotate periodically (instructions in file)

---

**Ready to integrate!** 🚀

Start with: `QUICK_START_STEVE_GLEN_COM.md`
