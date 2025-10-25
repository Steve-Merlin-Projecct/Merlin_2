---
title: "Steve Glen Api Key"
type: api_spec
component: general
status: draft
tags: []
---

# steve-glen.com Tracking API - Dedicated API Key

**Generated:** 2025-10-24
**Purpose:** Dedicated key for steve-glen.com tracking integration
**Key Name:** `STEVE_GLEN_TRACKING_API_KEY`

---

## 🔑 API Key

```
STEVE_GLEN_TRACKING_API_KEY=wR4kLmN7pQxS9vYzBcTgHjUiOeWqAsXdFrGhKnMbVlCxZaPoIuYtEwQsLkJnHmGf
```

**Security:**
- ✅ Dedicated key for tracking ingest API only
- ✅ Cannot access database, AI, or other APIs
- ✅ Can be revoked independently
- ✅ Follows least privilege principle

---

## 📝 Configuration

### Production (DigitalOcean)

1. Go to DigitalOcean App Platform
2. Your App → Settings → Environment Variables
3. Click **Edit**
4. Add new variable:
   - **Key:** `STEVE_GLEN_TRACKING_API_KEY`
   - **Value:** `wR4kLmN7pQxS9vYzBcTgHjUiOeWqAsXdFrGhKnMbVlCxZaPoIuYtEwQsLkJnHmGf`
   - **Encrypt:** ✅ Yes
5. Click **Save** (app will redeploy)

### Local Development (.env)

```bash
# Add to your .env file
STEVE_GLEN_TRACKING_API_KEY=wR4kLmN7pQxS9vYzBcTgHjUiOeWqAsXdFrGhKnMbVlCxZaPoIuYtEwQsLkJnHmGf
```

---

## 📤 Share with steve-glen.com Team

Send them this configuration:

```bash
# steve-glen.com .env configuration
TRACKING_API_URL=https://merlin-sea-turtle-app-ckmbz.ondigitalocean.app/api/tracking-ingest/batch
WEBHOOK_API_KEY=wR4kLmN7pQxS9vYzBcTgHjUiOeWqAsXdFrGhKnMbVlCxZaPoIuYtEwQsLkJnHmGf
```

**Note:** They use `WEBHOOK_API_KEY` as their variable name, but it's actually our dedicated key.

---

## ✅ Test the Key

### Health Check (No Auth)
```bash
curl https://merlin-sea-turtle-app-ckmbz.ondigitalocean.app/api/tracking-ingest/health
```

### Test Authentication
```bash
curl -X POST https://merlin-sea-turtle-app-ckmbz.ondigitalocean.app/api/tracking-ingest/test \
  -H "X-API-Key: wR4kLmN7pQxS9vYzBcTgHjUiOeWqAsXdFrGhKnMbVlCxZaPoIuYtEwQsLkJnHmGf" \
  -H "Content-Type: application/json"
```

Expected:
```json
{
  "success": true,
  "message": "API connection successful",
  "authenticated": true
}
```

### Send Test Batch
```bash
curl -X POST https://merlin-sea-turtle-app-ckmbz.ondigitalocean.app/api/tracking-ingest/batch \
  -H "X-API-Key: wR4kLmN7pQxS9vYzBcTgHjUiOeWqAsXdFrGhKnMbVlCxZaPoIuYtEwQsLkJnHmGf" \
  -H "Content-Type: application/json" \
  -d '{
    "events": [{
      "tracking_id": "test-123",
      "clicked_at": "2025-10-24T12:00:00Z",
      "ip_address": "192.168.1.1",
      "user_agent": "Test Agent",
      "click_source": "linkedin"
    }]
  }'
```

---

## 🔐 Security Features

**What this key CAN access:**
- ✅ `POST /api/tracking-ingest/batch` - Submit tracking events
- ✅ `POST /api/tracking-ingest/test` - Test connection
- ✅ `GET /api/tracking-ingest/health` - Health check (no auth needed anyway)

**What this key CANNOT access:**
- ❌ `/api/db/*` - Database operations
- ❌ `/api/analyze/*` - AI job analysis
- ❌ `/api/automation/*` - Application automation
- ❌ `/api/link-tracking/*` - Link management
- ❌ Any other API endpoints

**Security isolation achieved!** ✅

---

## 🔄 Key Rotation

To rotate this key in the future:

1. Generate new key: `python -c "import secrets; print(secrets.token_urlsafe(48))"`
2. Add new key to production (both keys work during transition)
3. Update steve-glen.com to use new key
4. Test steve-glen.com is using new key
5. Remove old key from production

---

## 📋 Deployment Checklist

- [ ] Add `STEVE_GLEN_TRACKING_API_KEY` to production DigitalOcean
- [ ] Add to local `.env` for testing
- [ ] Test with `/test` endpoint
- [ ] Share key with steve-glen.com team
- [ ] Verify steve-glen.com can connect
- [ ] Monitor logs for authentication attempts

---

## 🆘 Troubleshooting

**401 Unauthorized:**
- Check key matches exactly (no extra spaces)
- Verify `STEVE_GLEN_TRACKING_API_KEY` is set in production
- Check DigitalOcean app redeployed after adding key

**Still using old key?**
- Code falls back to `WEBHOOK_API_KEY` if `STEVE_GLEN_TRACKING_API_KEY` not set
- This is intentional for backward compatibility

**Need to revoke access?**
- Remove `STEVE_GLEN_TRACKING_API_KEY` from production
- steve-glen.com will get 401 errors
- Other APIs continue working with `WEBHOOK_API_KEY`

---

**Generated Key:** `wR4kLmN7pQxS9vYzBcTgHjUiOeWqAsXdFrGhKnMbVlCxZaPoIuYtEwQsLkJnHmGf`

**Keep this file secure!** Do not commit to public repositories.
