---
title: "Digitalocean Quick Start"
type: technical_doc
component: general
status: draft
tags: []
---

# Digital Ocean Deployment - Quick Start Guide
**TL;DR Checklist - Follow these steps in order**

---

## ⚡ Quick Overview

**Total Time**: 1.5-2 hours
**Cost**: ~$27/month (App Platform + Database)
**Difficulty**: Intermediate

**What You Get:**
- Production Flask app on Digital Ocean App Platform
- Managed PostgreSQL database with automated backups
- Auto-deployment from GitHub (push to `main` = deploy)
- Built-in SSL/HTTPS
- Health checks and monitoring

---

## 📋 Pre-Flight Checklist

Before starting, ensure you have:

- [ ] Digital Ocean account with billing enabled
- [ ] GitHub repository admin access
- [ ] Local `.env` file with all credentials
- [ ] PostgreSQL client (`psql`) installed locally
- [ ] Docker installed locally (for testing)

---

## 🚀 Deployment Steps

### Step 1: Create Database (15 min)

1. **Digital Ocean Dashboard** → **Databases** → **Create Database Cluster**
2. Configure:
   - Database: **PostgreSQL 15 or 16**
   - Region: **Choose closest to users** (NYC1, SFO3, TOR1)
   - Plan: **Dev Database ($15/mo)** ✅ Recommended
   - Name: `merlin-postgres-prod`
3. **Create** → Wait 3-5 minutes
4. **Copy connection string**:
   ```
   postgresql://doadmin:PASSWORD@HOST:25060/defaultdb?sslmode=require
   ```

### Step 2: Migrate Database (10 min)

**Option A: Schema Only**
```bash
# Export schema
pg_dump -h localhost -U postgres -d local_Merlin_3 \
  --schema-only --no-owner --no-acl -f schema_export.sql

# Import to Digital Ocean
psql "YOUR_DATABASE_URL_HERE" -f schema_export.sql

# Verify
psql "YOUR_DATABASE_URL_HERE" -c "\dt"
```

**Option B: Schema + Data (Automated)**
```bash
export DATABASE_URL_PRODUCTION="YOUR_DATABASE_URL_HERE"
python scripts/migrate_to_digitalocean.py --full-migration
```

### Step 3: GitHub Secrets (10 min)

GitHub repo → **Settings** → **Secrets and variables** → **Actions**

Add these secrets:

| Secret Name | Get From |
|-------------|----------|
| `DATABASE_URL` | Step 1 connection string |
| `WEBHOOK_API_KEY` | `.env` file |
| `SECRET_KEY` | `.env` or generate new |
| `GEMINI_API_KEY` | `.env` file |
| `APIFY_API_TOKEN` | `.env` file |
| `GMAIL_CREDENTIALS_JSON` | `cat storage/gmail_credentials.json \| base64` |
| `GOOGLE_DRIVE_CREDENTIALS_JSON` | `cat storage/google_drive_credentials.json \| base64` |

### Step 4: Create App (20 min)

1. **App Platform** → **Create App**
2. **Source**: GitHub → Your repository → Branch: `main` → **Autodeploy: ✅**
3. **Web Service**:
   - Name: `merlin-job-app`
   - Dockerfile: `/Dockerfile`
   - Port: `5001`
   - Health Check: `/health`
4. **Environment Variables** → Add:

```bash
DEPLOYMENT_PLATFORM=digitalocean
FLASK_ENV=production
FLASK_DEBUG=False
LOG_LEVEL=INFO
LOG_FORMAT=json
DATABASE_URL=${merlin-postgres-prod.DATABASE_URL}
WEBHOOK_API_KEY=<from_github_secret>
SECRET_KEY=<from_github_secret>
GEMINI_API_KEY=<from_github_secret>
APIFY_API_TOKEN=<from_github_secret>
GMAIL_CREDENTIALS_JSON=<base64_encoded>
GOOGLE_DRIVE_CREDENTIALS_JSON=<base64_encoded>
USER_EMAIL_ADDRESS=your.email@gmail.com
USER_DISPLAY_NAME=Steve Glen
USER_PHONE=(780) 555-0123
USER_LOCATION=Edmonton, Alberta, Canada
USER_LINKEDIN_URL=linkedin.com/in/steveglen
STORAGE_BACKEND=local
LOCAL_STORAGE_PATH=/app/storage/generated_documents
```

5. **Link Database**: Attach `merlin-postgres-prod`
6. **Instance Size**: **Professional 1GB ($12/mo)** ✅ Recommended
7. **Create Resources** → Wait 5-10 minutes

### Step 5: Verify Deployment (5 min)

Once status shows **"Deployed"**:

```bash
# Your app URL (from Digital Ocean console)
export APP_URL="https://merlin-job-app-xxxxx.ondigitalocean.app"

# Test health
curl $APP_URL/health
# Expected: {"overall_status": "healthy", ...}

# Test main endpoint
curl $APP_URL/

# Test database
curl $APP_URL/api/db/health
```

### Step 6: Test Auto-Deploy (5 min)

```bash
# Make a test change
echo "# Deployment test" >> README.md
git add README.md
git commit -m "test: Verify auto-deployment"
git push origin main

# Watch:
# 1. GitHub Actions → Actions tab (CI runs)
# 2. Digital Ocean → App Platform → Deployments tab (auto-deploy)
```

---

## ✅ Verification Checklist

After deployment, verify:

- [ ] Health endpoint returns 200 OK
- [ ] Database connectivity works
- [ ] Dashboard loads at `/dashboard`
- [ ] SSL certificate is valid (HTTPS)
- [ ] Logs show no errors
- [ ] GitHub Actions CI passes
- [ ] Auto-deployment works
- [ ] Environment variables are set

---

## 🔧 Common Issues

**Health check failing?**
```bash
# Check logs
doctl apps logs <app-id> --follow

# Verify DATABASE_URL is set
# App Platform → Settings → Environment Variables
```

**Can't connect to database?**
```bash
# Test connection locally
psql "YOUR_DATABASE_URL"

# Verify sslmode=require is in URL
# Check database cluster is running
```

**Build failing?**
```bash
# Test Docker build locally
docker build -t merlin-test .
docker run -p 5001:5001 merlin-test

# Check requirements.txt is current
pip freeze > requirements.txt
```

---

## 📊 Costs

| Resource | Tier | Price/mo |
|----------|------|----------|
| App Platform | Professional 1GB | $12 |
| PostgreSQL | Dev (1GB) | $15 |
| SSL | Included | $0 |
| Backups | Automated | $0 |
| **Total** | | **$27** |

---

## 📚 Full Documentation

For detailed information:
- **Complete Guide**: `docs/deployment/digitalocean-deployment-guide.md`
- **Environment Template**: `.env.production.example`
- **Migration Script**: `scripts/migrate_to_digitalocean.py`

---

## 🆘 Need Help?

**Digital Ocean Support**: https://cloud.digitalocean.com/support
**Status Page**: https://status.digitalocean.com/
**Deployment Guide**: `docs/deployment/digitalocean-deployment-guide.md`

---

**Ready? Start with Step 1!** ⬆️
