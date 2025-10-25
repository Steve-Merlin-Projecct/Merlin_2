---
title: "Api Key Security"
type: api_spec
component: security
status: draft
tags: []
---

# API Key Security - Important Information

**Date:** 2025-10-24
**Issue:** Shared API key security concern

---

## ⚠️ **Current Situation: SHARED KEY**

The tracking ingest API currently uses `WEBHOOK_API_KEY`, which is **SHARED** across multiple APIs:

### APIs Using the Same Key

| API | Endpoint | Access Level |
|-----|----------|--------------|
| Tracking Ingest | `/api/tracking-ingest/*` | Write click data |
| Link Tracking | `/api/link-tracking/*` | Create/read links |
| AI Analysis | `/api/analyze/*` | Run AI analysis |
| Database | `/api/db/*` | Read/write database |
| Automation | `/api/automation/*` | Run automation |

**Risk:** If you share `WEBHOOK_API_KEY` with steve-glen.com, they get access to **ALL** these APIs!

---

## 🔒 **Solution: Dedicated API Key**

I've updated the code to support a **dedicated key** for tracking ingest.

### How It Works

```python
# Priority order:
1. TRACKING_INGEST_API_KEY  (if set - dedicated key)
2. WEBHOOK_API_KEY          (if not set - shared key, backward compatible)
```

### Two Deployment Options

---

## ✅ **Option 1: Dedicated Key (Recommended for Third-Party)**

**Use this if:** steve-glen.com is managed by someone else or you want security isolation.

### Step 1: Generate New Key

```bash
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

**Generated dedicated key:**
```
qPzN8vXwRjK_LmYtBnHsGuDpFrCaEoWxIkVhJfTyQlMeNdAgZcUiSbXvKwPnRm-u
```

### Step 2: Add to Production Environment

**In DigitalOcean App Platform:**
1. Go to your app settings
2. Environment Variables → Edit
3. Add new variable:
   - **Key:** `TRACKING_INGEST_API_KEY`
   - **Value:** `qPzN8vXwRjK_LmYtBnHsGuDpFrCaEoWxIkVhJfTyQlMeNdAgZcUiSbXvKwPnRm-u`
   - **Encrypt:** ✅ Yes
4. Save (app will redeploy)

**In .env file (local):**
```bash
# Add this line to your .env
TRACKING_INGEST_API_KEY=qPzN8vXwRjK_LmYtBnHsGuDpFrCaEoWxIkVhJfTyQlMeNdAgZcUiSbXvKwPnRm-u
```

### Step 3: Share with steve-glen.com

**Give them ONLY the dedicated key:**
```
TRACKING_INGEST_API_KEY=qPzN8vXwRjK_LmYtBnHsGuDpFrCaEoWxIkVhJfTyQlMeNdAgZcUiSbXvKwPnRm-u
```

**They configure:**
```bash
# steve-glen.com .env
TRACKING_API_URL=https://merlin-sea-turtle-app-ckmbz.ondigitalocean.app/api/tracking-ingest/batch
WEBHOOK_API_KEY=qPzN8vXwRjK_LmYtBnHsGuDpFrCaEoWxIkVhJfTyQlMeNdAgZcUiSbXvKwPnRm-u
```

### Benefits
- ✅ steve-glen.com can ONLY access tracking ingest API
- ✅ Cannot access database, AI, or automation APIs
- ✅ Can revoke steve-glen.com access without affecting other systems
- ✅ Follows principle of least privilege

---

## ✅ **Option 2: Shared Key (If You Control Both)**

**Use this if:** You control both this system AND steve-glen.com (it's your service).

### Configuration

**Do nothing!** The code falls back to `WEBHOOK_API_KEY` automatically.

**Share with steve-glen.com:**
```bash
WEBHOOK_API_KEY=Y-siA-PexOtwXceZk_E6ohfWJ8VVLHbl9k020WJ5O-fc-yay5HXXvHlG-FPxV65-
```

### When This is OK
- ✅ steve-glen.com is your own service
- ✅ You trust it with full API access
- ✅ Simpler management (one key for everything)

### Risk
- ⚠️ steve-glen.com can access ALL APIs
- ⚠️ Harder to audit which service is making which calls
- ⚠️ Can't revoke access selectively

---

## 📊 **Comparison**

| Feature | Dedicated Key | Shared Key |
|---------|--------------|------------|
| **Security Isolation** | ✅ Yes | ❌ No |
| **Least Privilege** | ✅ Yes | ❌ No |
| **Selective Revocation** | ✅ Yes | ❌ No |
| **Setup Complexity** | Medium | Low |
| **Audit Trail** | ✅ Clear | ⚠️ Mixed |
| **Use Case** | Third-party integration | Your own services |

---

## 🎯 **Recommendation**

### If steve-glen.com is:
- **Third-party service** → Use **Option 1: Dedicated Key**
- **Your own service** → Either option is fine

### Best Practice
**Always use dedicated keys for external integrations**, even if you trust them. It's:
- Easier to revoke access if needed
- Better for security audits
- Follows industry standards

---

## 🔄 **Migration Path**

If you're already using the shared key and want to switch:

### Step 1: Add Dedicated Key (Both Keys Work)
```bash
# Add to production environment
TRACKING_INGEST_API_KEY=qPzN8vXwRjK_LmYtBnHsGuDpFrCaEoWxIkVhJfTyQlMeNdAgZcUiSbXvKwPnRm-u

# Keep existing
WEBHOOK_API_KEY=Y-siA-PexOtwXceZk_E6ohfWJ8VVLHbl9k020WJ5O-fc-yay5HXXvHlG-FPxV65-
```

Both keys will work during transition!

### Step 2: Update steve-glen.com
```bash
# steve-glen.com switches to new key
WEBHOOK_API_KEY=qPzN8vXwRjK_LmYtBnHsGuDpFrCaEoWxIkVhJfTyQlMeNdAgZcUiSbXvKwPnRm-u
```

### Step 3: Monitor Logs
Check that steve-glen.com is using the new key successfully.

### Step 4: Optionally Rotate Old Key
Once steve-glen.com is on the new key, you can safely rotate `WEBHOOK_API_KEY` without affecting them.

---

## ✅ **Testing**

### Test Dedicated Key
```bash
# Using dedicated key
curl -X POST https://merlin-sea-turtle-app-ckmbz.ondigitalocean.app/api/tracking-ingest/test \
  -H "X-API-Key: qPzN8vXwRjK_LmYtBnHsGuDpFrCaEoWxIkVhJfTyQlMeNdAgZcUiSbXvKwPnRm-u" \
  -H "Content-Type: application/json"
```

### Test Shared Key (Fallback)
```bash
# Using shared key (if TRACKING_INGEST_API_KEY not set)
curl -X POST https://merlin-sea-turtle-app-ckmbz.ondigitalocean.app/api/tracking-ingest/test \
  -H "X-API-Key: Y-siA-PexOtwXceZk_E6ohfWJ8VVLHbl9k020WJ5O-fc-yay5HXXvHlG-FPxV65-" \
  -H "Content-Type: application/json"
```

Both should return:
```json
{
  "success": true,
  "message": "API connection successful",
  "authenticated": true
}
```

---

## 🔐 **Security Best Practices**

1. ✅ **Use dedicated keys for external integrations**
2. ✅ **Encrypt keys in DigitalOcean** (check "Encrypt" checkbox)
3. ✅ **Never commit keys to git**
4. ✅ **Rotate keys periodically** (every 90-180 days)
5. ✅ **Monitor for invalid key attempts** (check logs)
6. ✅ **Use HTTPS only** (DigitalOcean does this automatically)

---

## 📝 **Summary**

**Question:** Does the tracking ingest API have its own key?

**Current Answer:** No, it shares `WEBHOOK_API_KEY` with other APIs.

**Updated Answer:** Now supports dedicated `TRACKING_INGEST_API_KEY` with fallback to shared key.

**Recommended:** Use dedicated key for steve-glen.com:
```
TRACKING_INGEST_API_KEY=qPzN8vXwRjK_LmYtBnHsGuDpFrCaEoWxIkVhJfTyQlMeNdAgZcUiSbXvKwPnRm-u
```

---

**Next Steps:**
1. Decide: Dedicated key or shared key?
2. If dedicated: Add `TRACKING_INGEST_API_KEY` to production
3. Share appropriate key with steve-glen.com
4. Test both authentication methods
