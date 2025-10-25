---
title: "Quick Deploy"
type: technical_doc
component: general
status: draft
tags: []
---

# Quick Deploy - Copy/Paste Guide

**App:** https://merlin-sea-turtle-app-ckmbz.ondigitalocean.app/
**Dashboard:** https://merlin-sea-turtle-app-ckmbz.ondigitalocean.app/dashboard
**App ID:** `0f18ac64-a3d0-4429-83f6-ea74d7ccb31e` ✅ Verified

## Step 1: App Settings

---

## Step 2: Add Environment Variables

**Go to:** Your App → Settings → App-Level Environment Variables → Edit

**Copy/paste these (mark all as Encrypted except FLASK_ENV, FLASK_DEBUG):**

```
DATABASE_URL=postgresql://doadmin:[REDACTED]@db-postgresql-merlin-tor1-52568-do-user-27870072-0.e.db.ondigitalocean.com:25060/defaultdb?sslmode=require

FLASK_ENV=production

FLASK_DEBUG=False

DASHBOARD_PASSWORD_HASH=$2b$12$DBrCObnfGjN8TMtNlUKg6egqOMk/xU8wtAGIstiwx1wtfnlYgHeOO

SESSION_SECRET=767d4fdf21f3d1ae8e7f5fc3629156a421623a249c13affb157393fcb29805f7

WEBHOOK_API_KEY=LKi7BfXjnqKYzR9uBARMcQucamcsiI_vGtxgL5353StnU2bUtJtjWeRAEyi9-adu

MONITORING_API_KEY=a1-GcSN7fHq2OhB0HPLDU8LIrXVfT8GRK07B0lmlZcaRNV2H_4gLnngDWEVYW_ZF

GEMINI_API_KEY=AIzaSyDyi4qcstJ2xGfC9GpOWmuMeW2VjiHXKhs
```

---

## Step 3: Save and Deploy

1. Click "Save"
2. App will automatically redeploy (2-5 minutes)
3. Wait for "Deployed" status

---

## Step 4: Test

**Dashboard URL:** https://merlin-sea-turtle-app-ckmbz.ondigitalocean.app/dashboard

**Expected:**
- ✅ Login page appears
- ✅ Password authentication works
- ✅ Dashboard displays data from database

---

## If Issues

**Can't login?**
- Verify password is correct
- Wait 1 minute if rate limited (5 attempts/minute max)

**No data showing?**
- Check Runtime Logs for database errors
- Verify database connection in logs

**Need help?** Tell me the error message from Runtime Logs
