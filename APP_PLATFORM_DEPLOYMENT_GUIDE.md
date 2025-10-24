# Digital Ocean App Platform Deployment Guide

**App:** https://merlin-sea-turtle-app-ckmbz.ondigitalocean.app/
**Dashboard:** https://merlin-sea-turtle-app-ckmbz.ondigitalocean.app/dashboard
**App ID:** `0f18ac64-a3d0-4429-83f6-ea74d7ccb31e` ✅ Verified
**Database:** Digital Ocean Managed PostgreSQL (Toronto region)
**Status:** Ready to Deploy
**Security:** Production-hardened (bcrypt authentication, rate limiting, no debug mode)

---

## Step 1: App Platform Settings

### Access Your App

1. **Direct link:** https://cloud.digitalocean.com/apps/0f18ac64-a3d0-4429-83f6-ea74d7ccb31e

2. **Firewall Status:** ✅ Already configured for this App ID

---

## Step 2: Configure Environment Variables

### Navigate to App Settings

1. **Go to:** https://cloud.digitalocean.com/apps
2. **Click on your dashboard app**
3. **Click "Settings" tab** (top of page)
4. **Scroll to "App-Level Environment Variables"** section
5. **Click "Edit"** or "Add Variable"

---

### Add These Environment Variables

**Copy and paste these exactly:**

#### Database Configuration

```bash
DATABASE_URL=postgresql://doadmin:[REDACTED]@db-postgresql-merlin-tor1-52568-do-user-27870072-0.e.db.ondigitalocean.com:25060/defaultdb?sslmode=require
```

- **Type:** Encrypted (use the encrypt checkbox)
- **Scope:** All components

---

#### Flask Configuration

```bash
FLASK_ENV=production
```

- **Type:** Plain text
- **Scope:** All components

---

```bash
FLASK_DEBUG=False
```

- **Type:** Plain text
- **Scope:** All components

---

#### Dashboard Authentication

```bash
DASHBOARD_PASSWORD_HASH=$2b$12$DBrCObnfGjN8TMtNlUKg6egqOMk/xU8wtAGIstiwx1wtfnlYgHeOO
```

- **Type:** Encrypted
- **Scope:** All components
- **Note:** Bcrypt hash for dashboard authentication

---

#### Session Security

```bash
SESSION_SECRET=767d4fdf21f3d1ae8e7f5fc3629156a421623a249c13affb157393fcb29805f7
```

- **Type:** Encrypted
- **Scope:** All components

---

#### API Keys

```bash
WEBHOOK_API_KEY=LKi7BfXjnqKYzR9uBARMcQucamcsiI_vGtxgL5353StnU2bUtJtjWeRAEyi9-adu
```

- **Type:** Encrypted
- **Scope:** All components

---

```bash
MONITORING_API_KEY=a1-GcSN7fHq2OhB0HPLDU8LIrXVfT8GRK07B0lmlZcaRNV2H_4gLnngDWEVYW_ZF
```

- **Type:** Encrypted
- **Scope:** All components

---

```bash
GEMINI_API_KEY=AIzaSyDyi4qcstJ2xGfC9GpOWmuMeW2VjiHXKhs
```

- **Type:** Encrypted
- **Scope:** All components

---

### Optional but Recommended

```bash
LOG_LEVEL=INFO
```

```bash
STORAGE_BACKEND=local
```

```bash
APP_VERSION=4.5
```

---

## Step 3: Save and Deploy

1. **Click "Save"** at the bottom of the environment variables section

2. **App Platform will show:** "Your app will be rebuilt and redeployed"

3. **Click "Deploy"** or wait for automatic deployment

4. **Monitor deployment:**
   - Click "Runtime Logs" tab
   - Watch for successful startup messages
   - Look for: "Running on https://your-app.ondigitalocean.app"

---

## Step 4: Verify Deployment

### Check Application Health

1. **Wait for deployment to complete** (usually 2-5 minutes)

2. **Check app status:**
   - Should show: ✅ "Deployed"
   - Build status: ✅ "Success"

3. **Open your app URL:**
   ```
   https://your-app-name.ondigitalocean.app
   ```

---

### Test Dashboard Access

1. **Navigate to dashboard:**
   ```
   https://merlin-sea-turtle-app-ckmbz.ondigitalocean.app/dashboard
   ```

2. **You should see:** Login page (not auto-authenticated)

3. **Enter your dashboard password**

4. **Expected result:** ✅ Successfully logged in to dashboard

---

### Test Database Connection

1. **Once logged in**, check dashboard displays data

2. **Look for:**
   - Job listings
   - Application statistics
   - Recent activity
   - No database connection errors

3. **Check Runtime Logs** for database connection confirmation:
   ```
   Connected to Digital Ocean database
   Database: defaultdb
   Tables loaded: 32
   ```

---

## Step 5: Verify Security Features

### Authentication Check

- ✅ Dashboard requires login (no auto-authentication in production)
- ✅ Rate limiting active (5 attempts/minute on login)
- ✅ Bcrypt password hashing
- ✅ Session-based authentication

### Configuration Check

- ✅ `FLASK_DEBUG=False` (no debug mode in production)
- ✅ `FLASK_ENV=production` (production optimizations enabled)
- ✅ SSL/TLS database connection (`sslmode=require`)
- ✅ Encrypted environment variables

---

## Troubleshooting

### Deployment Failed

**Check Build Logs:**
1. Go to app → "Build Logs" tab
2. Look for error messages
3. Common issues:
   - Missing dependencies in `requirements.txt`
   - Python version mismatch
   - Import errors

**Solution:**
- Verify `requirements.txt` includes: `bcrypt>=4.1.0`
- Check Python version in app spec matches project (3.11)

---

### Can't Access Dashboard

**Symptom:** 404 or "Page not found"

**Check:**
1. **URL is correct:**
   - Main app: `https://your-app.ondigitalocean.app`
   - Dashboard: `https://your-app.ondigitalocean.app/dashboard`

2. **App is running:**
   - Status should be "Deployed" not "Deploying"

3. **Routes are registered:**
   - Check Runtime Logs for: "Registered blueprint: dashboard"

---

### Authentication Not Working

**Symptom:** Password rejected or infinite login loop

**Check:**
1. **Password is correct** (verify you're using the correct dashboard password)

2. **Environment variable is set:**
   ```bash
   DASHBOARD_PASSWORD_HASH=$2b$12$DBrCObnfGjN8TMtNlUKg6egqOMk/xU8wtAGIstiwx1wtfnlYgHeOO
   ```

3. **bcrypt is installed:**
   - Check `requirements.txt` has: `bcrypt>=4.1.0`
   - Check Build Logs for successful bcrypt installation

**Runtime Logs should show:**
```
Dashboard authentication initialized
Using bcrypt password hashing
```

---

### Database Connection Failed

**Symptom:** Dashboard shows "Database connection error"

**Check:**

1. **Environment variable is set:**
   ```bash
   echo $DATABASE_URL
   ```
   Should output the connection string

2. **Firewall allows App Platform app:**
   - App ID in firewall: `0f18ac64-a3d0-4429-83f6-ea74d7ccb31e`
   - Should match your App Platform app ID

3. **SSL mode is enabled:**
   - Connection string must include: `?sslmode=require`

**Test from App Platform console:**
1. Go to app → Console tab
2. Run:
   ```bash
   python -c "import os; print(os.getenv('DATABASE_URL')[:50])"
   ```
3. Should show: `postgresql://doadmin:...`

---

### Rate Limiting Issues

**Symptom:** "Too many requests" on login

**This is expected!** Rate limiting is working correctly:
- **Limit:** 5 login attempts per minute
- **Limit:** 20 login attempts per hour

**Wait 1 minute** and try again, or use correct password.

---

## Post-Deployment Checklist

- [ ] App Platform shows "Deployed" status
- [ ] App URL accessible (https://merlin-sea-turtle-app-ckmbz.ondigitalocean.app)
- [ ] Dashboard login page appears (https://merlin-sea-turtle-app-ckmbz.ondigitalocean.app/dashboard)
- [ ] Password authentication works
- [ ] Dashboard displays data from database
- [ ] No errors in Runtime Logs
- [ ] Database connection confirmed in logs
- [ ] Security features verified (no debug mode, rate limiting active)

---

## Environment Variables Summary

Quick reference for all required variables:

| Variable | Value | Type |
|----------|-------|------|
| DATABASE_URL | postgresql://doadmin:AVNS_...?sslmode=require | Encrypted |
| FLASK_ENV | production | Plain |
| FLASK_DEBUG | False | Plain |
| DASHBOARD_PASSWORD_HASH | $2b$12$DBrCObnfGjN... | Encrypted |
| SESSION_SECRET | 767d4fdf21f3d1ae8e7f5fc3... | Encrypted |
| WEBHOOK_API_KEY | LKi7BfXjnqKYzR9uBARMcQuc... | Encrypted |
| MONITORING_API_KEY | a1-GcSN7fHq2OhB0HPLDU8LI... | Encrypted |
| GEMINI_API_KEY | AIzaSyDyi4qcstJ2xGfC9Gp... | Encrypted |

---

## Security Notes

### Production Security Features Active

✅ **Authentication:**
- Bcrypt password hashing (industry standard)
- Session-based authentication
- No auto-authentication bypass

✅ **Rate Limiting:**
- 5 login attempts per minute
- 20 login attempts per hour
- Prevents brute force attacks

✅ **Configuration:**
- Debug mode disabled (`FLASK_DEBUG=False`)
- Production environment (`FLASK_ENV=production`)
- Secure session management
- Encrypted environment variables

✅ **Database Security:**
- SSL/TLS required (`sslmode=require`)
- Managed database with automatic backups
- Firewall restricts access to App Platform only

---

## Dashboard Access

**App URL:** https://merlin-sea-turtle-app-ckmbz.ondigitalocean.app/
**Dashboard URL:** https://merlin-sea-turtle-app-ckmbz.ondigitalocean.app/dashboard

**Authentication:** Bcrypt password hashing with session management

---

## Support

**Digital Ocean Resources:**
- App Platform Docs: https://docs.digitalocean.com/products/app-platform/
- Environment Variables: https://docs.digitalocean.com/products/app-platform/how-to/use-environment-variables/
- Logs: https://docs.digitalocean.com/products/app-platform/how-to/view-logs/

**Database Resources:**
- Database Docs: https://docs.digitalocean.com/products/databases/postgresql/
- Firewall Rules: https://docs.digitalocean.com/products/databases/postgresql/how-to/secure/

---

## Next Steps After Deployment

1. **Test all dashboard features:**
   - Job listings page
   - Applications tracking
   - Analytics dashboard
   - Database schema viewer

2. **Monitor application:**
   - Review Runtime Logs regularly
   - Set up alerts for errors
   - Monitor database connection status

3. **Optional enhancements:**
   - Configure custom domain
   - Set up backup schedule
   - Add monitoring/alerting
   - Configure log aggregation

---

**Deployment Status:** Ready ✅
**Configuration:** Complete ✅
**Security:** Production-hardened ✅
**Database:** Connected and authorized ✅
