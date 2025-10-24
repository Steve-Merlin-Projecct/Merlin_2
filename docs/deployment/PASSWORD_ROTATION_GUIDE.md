---
title: "Password Rotation Guide"
type: guide
component: general
status: draft
tags: []
---

# Database Password Rotation - Quick Reference Guide

**Current Database:** `db-postgresql-merlin-tor1-52568`
**Connection:** `postgresql://REPLACE_WITH_DB_CREDENTIALS@...`

⚠️ **This password should be rotated after initial setup and every 90 days**

---

## 🔄 Quick Rotation Steps (15 minutes)

### Step 1: Reset Password in Digital Ocean (2 min)

1. **Digital Ocean Dashboard** → **Databases** → `db-postgresql-merlin-tor1-52568`
2. Click **"Settings"** tab
3. Scroll to **"Reset Database Password"** section
4. Click **"Reset Password"**
5. **Copy the new password immediately** (shown once)
6. Save in password manager

**New connection string format:**
```
postgresql://doadmin:NEW_PASSWORD_HERE@db-postgresql-merlin-tor1-52568-do-user-2787072-0.e.db.ondigitalocean.com:25060/defaultdb?sslmode=require
```

---

### Step 2: Update Local Development (2 min)

```bash
# Edit .env file
nano .env

# Update this line with new password:
DATABASE_URL_PRODUCTION="postgresql://doadmin:NEW_PASSWORD@db-postgresql-merlin-tor1-52568-do-user-2787072-0.e.db.ondigitalocean.com:25060/defaultdb?sslmode=require"

# Save and exit (Ctrl+X, Y, Enter)

# Test connection
psql "$DATABASE_URL_PRODUCTION" -c "SELECT version();"
```

---

### Step 3: Update GitHub Secrets (3 min)

1. **GitHub Repository** → **Settings** → **Secrets and variables** → **Actions**
2. Find **`DATABASE_URL`** secret
3. Click **"Update"** (pencil icon)
4. Paste new connection string
5. Click **"Update secret"**

**Verify:**
```bash
# Trigger CI workflow to test new credentials
git commit --allow-empty -m "test: Verify database password update"
git push origin main

# Check GitHub Actions → Recent workflow run → Should pass
```

---

### Step 4: Update App Platform (3 min)

**Option A: Using Linked Database (Recommended - Auto-updates)**

If database is linked in App Platform:
1. **App Platform** → Your App → **Settings** → **App-Level Environment Variables**
2. Find `DATABASE_URL` set to: `${merlin-postgres-prod.DATABASE_URL}`
3. **No action needed** - automatically updates when password resets!
4. **Skip to Step 5**

**Option B: Manual DATABASE_URL**

If using custom `DATABASE_URL` string:
1. **App Platform** → Your App → **Settings** → **App-Level Environment Variables**
2. Click **"Edit"** on `DATABASE_URL` variable
3. Paste new connection string
4. Mark as **"Encrypt"** ✅
5. Click **"Save"**
6. App Platform will automatically redeploy (5-8 minutes)

---

### Step 5: Verify Production Deployment (5 min)

**Wait for redeployment** (if using manual DATABASE_URL):
- App Platform → **Deployments** tab
- Wait for status: **"Deployed"** ✅

**Test production connection:**
```bash
# Set your app URL
export APP_URL="https://merlin-job-app-xxxxx.ondigitalocean.app"

# Test health endpoint (includes database check)
curl $APP_URL/health

# Expected response:
# {
#   "overall_status": "healthy",
#   "checks": {
#     "database": {"status": "healthy", ...}
#   }
# }

# Test database API
curl $APP_URL/api/db/health

# Expected: {"status": "connected", ...}
```

**Check logs for errors:**
```bash
# View recent logs
doctl apps logs <app-id> --type RUN | tail -100

# Search for database errors
doctl apps logs <app-id> | grep -i "database\|connection\|authentication"

# Should see: "Database configured: Digital Ocean"
```

---

## 📋 Rotation Checklist

Complete this checklist every time you rotate the password:

- [ ] **Step 1**: Reset password in Digital Ocean ✅
- [ ] **Step 1**: New password saved in password manager ✅
- [ ] **Step 2**: Local `.env` file updated ✅
- [ ] **Step 2**: Local connection tested successfully ✅
- [ ] **Step 3**: GitHub Secrets `DATABASE_URL` updated ✅
- [ ] **Step 3**: CI workflow tested (optional) ✅
- [ ] **Step 4**: App Platform environment variable updated ✅
- [ ] **Step 4**: App redeployment completed (if needed) ✅
- [ ] **Step 5**: Production health endpoint returns healthy ✅
- [ ] **Step 5**: Production database API accessible ✅
- [ ] **Step 5**: No database errors in logs ✅
- [ ] **Record rotation**: Date and reason documented below ✅

---

## 📝 Rotation History

| Date | Reason | Updated By | Verified |
|------|--------|------------|----------|
| 2025-10-22 | Initial setup | [Your Name] | ✅ |
| YYYY-MM-DD | Quarterly rotation | | |
| YYYY-MM-DD | Security incident | | |

**Next scheduled rotation:** [90 days from last rotation]

---

## 🚨 Emergency Rotation (Compromised Password)

If password is exposed or compromised:

### Immediate Actions (within 30 minutes)

1. **Reset password immediately** (Step 1 above)
2. **Update all environments in parallel**:
   ```bash
   # Update local .env
   nano .env  # Update DATABASE_URL_PRODUCTION

   # Update GitHub Secrets
   # (Use GitHub web UI - faster than CLI)

   # Update App Platform
   # (Use Digital Ocean web UI)
   ```

3. **Force redeploy App Platform**:
   - App Platform → Your App → **Actions** dropdown → **Force Redeploy**
   - Faster than waiting for auto-deploy

4. **Monitor for unauthorized access**:
   ```sql
   -- Check recent connections (if you have access)
   SELECT * FROM pg_stat_activity
   WHERE datname = 'defaultdb'
   ORDER BY backend_start DESC
   LIMIT 20;
   ```

5. **Review Digital Ocean database logs**:
   - Database cluster → **Logs & Queries** tab
   - Look for suspicious queries or connection attempts

6. **Document incident**:
   - How was it exposed?
   - Who was notified?
   - What actions were taken?
   - Prevention measures added?

---

## 🔐 Security Best Practices

**DO:**
- ✅ Rotate every 90 days (quarterly)
- ✅ Rotate after initial setup/testing
- ✅ Rotate if exposure suspected
- ✅ Use password manager for storage
- ✅ Test connections after rotation
- ✅ Document all rotations
- ✅ Keep old password until new one verified

**DON'T:**
- ❌ Share password in Slack/email
- ❌ Commit password to Git
- ❌ Hardcode password in code
- ❌ Use same password across environments
- ❌ Skip verification step
- ❌ Forget to update all three locations

---

## 🛠️ Troubleshooting

**"Connection refused" after rotation:**
```bash
# Verify new password is correct
psql "postgresql://doadmin:NEW_PASSWORD@db-postgresql-merlin-tor1-52568-do-user-2787072-0.e.db.ondigitalocean.com:25060/defaultdb?sslmode=require"

# If connection works locally but not in production:
# 1. Check App Platform environment variables updated
# 2. Verify app redeployed after env var change
# 3. Check logs: doctl apps logs <app-id>
```

**"Authentication failed" error:**
```bash
# Common causes:
# 1. Typo in password
# 2. Old password still cached
# 3. Environment variable not reloaded

# Solution:
# 1. Copy password again from Digital Ocean (avoid typing)
# 2. Force redeploy app
# 3. Clear local environment: unset DATABASE_URL_PRODUCTION, then re-export
```

**App Platform not using new password:**
```bash
# Force update:
# 1. Edit DATABASE_URL environment variable (even if unchanged)
# 2. Add a space, remove it, save
# 3. This triggers redeployment
# OR
# 1. Actions dropdown → Force Redeploy
```

---

## 📞 Support

**Digital Ocean Database Issues:**
- Dashboard → Databases → Your Cluster → **Open Support Ticket**
- Include: Cluster ID, timestamp, error message

**Application Connection Issues:**
- Check: `docs/deployment/SECURITY_PRACTICES.md`
- Check: `docs/deployment/digitalocean-deployment-guide.md` (Troubleshooting section)

---

**Last Updated:** 2025-10-22
**Next Review:** 2026-01-22 (or after next rotation)
