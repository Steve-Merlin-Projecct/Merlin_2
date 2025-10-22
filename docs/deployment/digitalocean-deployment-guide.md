# Digital Ocean App Platform Deployment Guide
**Merlin Job Application System v4.4**

Complete step-by-step guide for deploying the Merlin Job Application System to Digital Ocean App Platform with managed PostgreSQL database and GitHub-based CI/CD.

---

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Architecture](#architecture)
4. [Step-by-Step Deployment](#step-by-step-deployment)
5. [Configuration](#configuration)
6. [Monitoring & Troubleshooting](#monitoring--troubleshooting)
7. [Cost Breakdown](#cost-breakdown)
8. [Rollback & Recovery](#rollback--recovery)

---

## Overview

### Deployment Strategy

**Digital Ocean App Platform** (Platform-as-a-Service)
- ✅ Automated deployments from GitHub
- ✅ Built-in SSL/HTTPS certificates
- ✅ Auto-scaling and load balancing
- ✅ Managed container hosting
- ✅ Zero-downtime deployments
- ✅ Integrated monitoring and logs

### Technology Stack

- **Application**: Python 3.11 Flask
- **WSGI Server**: Gunicorn (production-grade)
- **Database**: Digital Ocean Managed PostgreSQL 15/16
- **Container**: Docker (multi-stage build)
- **CI/CD**: GitHub Actions
- **SSL**: Automatic via Let's Encrypt

---

## Prerequisites

### Required Accounts & Access

- [ ] **Digital Ocean Account** with billing enabled
- [ ] **GitHub Repository** with admin access
- [ ] **Local Development Environment** with:
  - Docker installed
  - PostgreSQL client (`psql`) installed
  - Git configured
  - Python 3.11+

### Required Credentials

Gather these from your local `.env` file:

- [ ] `WEBHOOK_API_KEY`
- [ ] `SECRET_KEY`
- [ ] `GEMINI_API_KEY`
- [ ] `APIFY_API_TOKEN`
- [ ] `GMAIL_CREDENTIALS_JSON` (base64-encoded)
- [ ] `GOOGLE_DRIVE_CREDENTIALS_JSON` (base64-encoded)
- [ ] User profile information (email, phone, LinkedIn, etc.)

---

## Architecture

### Production Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                       Internet                               │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        │ HTTPS (SSL via Let's Encrypt)
                        │
┌───────────────────────▼─────────────────────────────────────┐
│          Digital Ocean App Platform                          │
│  ┌────────────────────────────────────────────────────┐     │
│  │  Merlin Flask Application (Docker Container)       │     │
│  │  - Gunicorn WSGI Server                            │     │
│  │  - Python 3.11                                     │     │
│  │  - Auto-scaling (1-3 instances)                    │     │
│  │  - Health checks (/health endpoint)                │     │
│  └────────────────────┬───────────────────────────────┘     │
│                       │                                      │
│                       │ Private Network                      │
│                       │                                      │
│  ┌────────────────────▼───────────────────────────────┐     │
│  │  Managed PostgreSQL Database Cluster               │     │
│  │  - Primary + Standby Nodes                         │     │
│  │  - Automated Backups (Daily)                       │     │
│  │  - SSL/TLS Required                                │     │
│  │  - Connection Pooling                              │     │
│  └────────────────────────────────────────────────────┘     │
└──────────────────────────────────────────────────────────────┘
                        │
                        │ Push to main branch
                        │
┌───────────────────────▼─────────────────────────────────────┐
│                    GitHub Repository                         │
│  - Source code                                               │
│  - GitHub Actions CI/CD                                      │
│  - Automatic deployment trigger                             │
└──────────────────────────────────────────────────────────────┘
```

### Data Flow

1. **Code Push**: Developer pushes to `main` branch on GitHub
2. **CI Pipeline**: GitHub Actions runs tests and quality checks
3. **Auto-Deploy**: App Platform detects push and pulls latest code
4. **Build**: App Platform builds Docker image from `Dockerfile`
5. **Deploy**: Rolling deployment with zero downtime
6. **Health Check**: App Platform verifies `/health` endpoint
7. **Traffic Routing**: New instances receive traffic, old instances terminated

---

## Step-by-Step Deployment

### Phase 1: Database Setup (15-20 minutes)

#### Step 1.1: Create Digital Ocean Managed PostgreSQL Database

1. **Log into Digital Ocean Dashboard**
   - Visit: https://cloud.digitalocean.com/databases

2. **Create Database Cluster**
   - Click **Create** → **Databases**
   - **Database Engine**: PostgreSQL
   - **Version**: 15 or 16 (recommended)
   - **Datacenter Region**: Choose closest to your users
     - North America: `NYC1`, `NYC3`, `SFO3`, `TOR1`
     - Europe: `LON1`, `FRA1`, `AMS3`
   - **Cluster Configuration**:
     - **Dev Database**: $15/month (1 GB RAM, 10 GB disk, 1 node)
     - **Production**: $55/month (2 GB RAM, 25 GB disk, 2 nodes)

3. **Configure Database**
   - **Database Cluster Name**: `merlin-postgres-prod`
   - **Database Name**: `merlin_prod` (or keep `defaultdb`)
   - **Tags**: `production`, `merlin`, `app-platform`

4. **Create Database**
   - Click **Create Database Cluster**
   - ⏱️ Wait 3-5 minutes for provisioning

5. **Capture Connection Details**

   Once provisioned, go to **Connection Details** tab:

   ```bash
   # Connection String (use this for DATABASE_URL)
   postgresql://doadmin:AVNS_xxxxxxxxxxxxx@db-postgresql-nyc1-12345-do-user-123456-0.db.ondigitalocean.com:25060/defaultdb?sslmode=require

   # Individual Components
   Host: db-postgresql-nyc1-12345-do-user-123456-0.db.ondigitalocean.com
   Port: 25060
   Username: doadmin
   Password: AVNS_xxxxxxxxxxxxx
   Database: defaultdb
   SSL Mode: require
   ```

   **⚠️ IMPORTANT**: Save these credentials securely. You'll need them for App Platform configuration.

6. **Configure Trusted Sources** (Optional)
   - Go to **Settings** tab
   - Under **Trusted Sources**, App Platform will auto-populate when linked
   - For manual access: Add your IP address for database migration

#### Step 1.2: Migrate Database Schema

**Option A: Using pg_dump (Recommended)**

```bash
# 1. Export schema from local database
pg_dump -h localhost \
        -U postgres \
        -d local_Merlin_3 \
        --schema-only \
        --no-owner \
        --no-acl \
        -f merlin_schema_export.sql

# 2. Review the exported schema (optional)
less merlin_schema_export.sql

# 3. Import to Digital Ocean managed database
# Replace connection string with your actual values
psql "postgresql://doadmin:PASSWORD@HOST:25060/defaultdb?sslmode=require" \
     -f merlin_schema_export.sql

# 4. Verify import
psql "postgresql://doadmin:PASSWORD@HOST:25060/defaultdb?sslmode=require" \
     -c "\dt"

# Expected output: List of all 32 tables
```

**Option B: Using Database Automation Tools**

```bash
# 1. Set DATABASE_URL to Digital Ocean managed database
export DATABASE_URL="postgresql://doadmin:PASSWORD@HOST:25060/defaultdb?sslmode=require"

# 2. Run schema generation (creates tables, indexes, constraints)
python database_tools/update_schema.py

# 3. Verify schema
python database_tools/validate_schema.py
```

**Option C: Restore from Backup**

```bash
# 1. Create full database dump (schema + data)
pg_dump -h localhost \
        -U postgres \
        -d local_Merlin_3 \
        --no-owner \
        --no-acl \
        -f merlin_full_backup.sql

# 2. Restore to Digital Ocean
psql "postgresql://doadmin:PASSWORD@HOST:25060/defaultdb?sslmode=require" \
     -f merlin_full_backup.sql
```

**Verification Checklist:**

```bash
# Connect to Digital Ocean database
psql "postgresql://doadmin:PASSWORD@HOST:25060/defaultdb?sslmode=require"

# Check table count (should be 32)
\dt

# Check specific critical tables
\d jobs
\d job_applications
\d user_profiles

# Verify data (if migrated)
SELECT COUNT(*) FROM jobs;
SELECT COUNT(*) FROM job_applications;

# Exit psql
\q
```

---

### Phase 2: GitHub Configuration (10-15 minutes)

#### Step 2.1: Set Up Repository Secrets

1. **Navigate to GitHub Repository**
   - Go to your repository on GitHub
   - Click **Settings** → **Secrets and variables** → **Actions**

2. **Add Repository Secrets**

   Click **New repository secret** for each:

   | Secret Name | Value | Description |
   |------------|-------|-------------|
   | `DATABASE_URL` | `postgresql://doadmin:...?sslmode=require` | From Step 1.1 |
   | `WEBHOOK_API_KEY` | From `.env` | API authentication |
   | `SECRET_KEY` | From `.env` or generate new | Flask session encryption |
   | `GEMINI_API_KEY` | From `.env` | Google Gemini AI |
   | `APIFY_API_TOKEN` | From `.env` | Job scraping service |
   | `GMAIL_CREDENTIALS_JSON` | Base64-encoded | See encoding below |
   | `GOOGLE_DRIVE_CREDENTIALS_JSON` | Base64-encoded | See encoding below |

3. **Encode OAuth Credentials**

   ```bash
   # Gmail credentials
   cat storage/gmail_credentials.json | base64 > gmail_creds_b64.txt
   # Copy contents of gmail_creds_b64.txt and paste as GMAIL_CREDENTIALS_JSON secret

   # Google Drive credentials
   cat storage/google_drive_credentials.json | base64 > gdrive_creds_b64.txt
   # Copy contents and paste as GOOGLE_DRIVE_CREDENTIALS_JSON secret
   ```

   **Note**: Tokens (gmail_token.json, google_drive_token.json) will be regenerated in production.

4. **Verify Secrets**
   - All secrets should show "Updated X seconds ago"
   - ✅ Total: 7 secrets configured

#### Step 2.2: Verify GitHub Actions Workflow

The workflow file `.github/workflows/deploy-digitalocean.yml` is already created. It will:

- Run code quality checks (Black, Flake8, Vulture)
- Execute test suite with PostgreSQL
- Perform security scans
- Build and validate Docker image
- Validate database schema documentation

**No action needed** - this runs automatically on push to `main`.

---

### Phase 3: App Platform Setup (20-30 minutes)

#### Step 3.1: Create App Platform Application

1. **Navigate to App Platform**
   - Digital Ocean Dashboard → **App Platform** → **Create App**

2. **Connect Source**
   - **Source**: GitHub
   - **Repository**: Select your `Merlin_2` repository
   - **Branch**: `main`
   - **Autodeploy**: ✅ Enable
   - Click **Next**

3. **Configure Resources**

   **Web Service Configuration:**
   - **Name**: `merlin-job-app`
   - **Source Directory**: `/` (root)
   - **Type**: Web Service
   - **Dockerfile Path**: `/Dockerfile`
   - **Build Command**: (leave default - Docker build)
   - **Run Command**: (leave default - uses CMD from Dockerfile)

   **HTTP Configuration:**
   - **HTTP Port**: `5001`
   - **HTTP Request Routes**: `/`
   - **Health Check Path**: `/health`
   - **Health Check Period**: 30 seconds
   - **Health Check Timeout**: 10 seconds
   - **Health Check Success Threshold**: 1
   - **Health Check Failure Threshold**: 3

4. **Configure Environment**

   Click **Edit** next to environment variables:

   | Variable | Value | Encrypt |
   |----------|-------|---------|
   | `DEPLOYMENT_PLATFORM` | `digitalocean` | No |
   | `FLASK_ENV` | `production` | No |
   | `FLASK_DEBUG` | `False` | No |
   | `LOG_LEVEL` | `INFO` | No |
   | `LOG_FORMAT` | `json` | No |
   | `DATABASE_URL` | `${merlin-postgres-prod.DATABASE_URL}` | Yes |
   | `WEBHOOK_API_KEY` | (from GitHub secret) | Yes |
   | `SECRET_KEY` | (from GitHub secret) | Yes |
   | `GEMINI_API_KEY` | (from GitHub secret) | Yes |
   | `APIFY_API_TOKEN` | (from GitHub secret) | Yes |
   | `GMAIL_CREDENTIALS_JSON` | (base64-encoded) | Yes |
   | `GOOGLE_DRIVE_CREDENTIALS_JSON` | (base64-encoded) | Yes |
   | `USER_EMAIL_ADDRESS` | `your.email@gmail.com` | No |
   | `USER_DISPLAY_NAME` | `Steve Glen` | No |
   | `USER_PHONE` | `(780) 555-0123` | No |
   | `USER_LOCATION` | `Edmonton, Alberta, Canada` | No |
   | `USER_LINKEDIN_URL` | `linkedin.com/in/steveglen` | No |
   | `ENABLE_URL_TRACKING` | `true` | No |
   | `BASE_REDIRECT_URL` | `https://merlin-job-app-xxxxx.ondigitalocean.app/track` | No |
   | `STORAGE_BACKEND` | `local` | No |
   | `LOCAL_STORAGE_PATH` | `/app/storage/generated_documents` | No |

   **💡 Tip**: Mark all API keys and credentials as "Encrypt" (Secret).

5. **Link Database**
   - Scroll to **Database** section
   - Click **Attach Database**
   - Select `merlin-postgres-prod`
   - **Connection String Variable**: App Platform will auto-inject as `${merlin-postgres-prod.DATABASE_URL}`
   - This automatically sets `DATABASE_URL` environment variable

6. **Choose Instance Size**

   | Tier | RAM | vCPU | Price/month | Recommended For |
   |------|-----|------|-------------|-----------------|
   | **Basic** | 512 MB | 1 | $5 | Development/Testing |
   | **Professional** | 1 GB | 1 | $12 | Production (Light) |
   | **Professional** | 2 GB | 2 | $24 | Production (Medium) |

   **Recommendation**: Start with **Professional 1GB ($12/month)** for production.

7. **Review Configuration**
   - **App Name**: `merlin-job-app`
   - **Region**: Same as database
   - **Resources**: 1 Web Service, 1 Database
   - **Monthly Cost**: ~$17-27/month (app + database)

8. **Create Resources**
   - Click **Create Resources**
   - ⏱️ Initial deployment: 5-10 minutes

#### Step 3.2: Monitor Initial Deployment

1. **Build Phase**
   - Watch build logs in real-time
   - Docker multi-stage build executes
   - Dependencies installed
   - Health checks configured

2. **Deploy Phase**
   - Container deployed to App Platform
   - Health check runs (`GET /health`)
   - Traffic routed to new instance

3. **Verify Deployment**

   Once status shows **"Deployed"**:

   ```bash
   # Get your App URL from Digital Ocean console
   # Format: https://merlin-job-app-xxxxx.ondigitalocean.app

   # Test health endpoint
   curl https://merlin-job-app-xxxxx.ondigitalocean.app/health

   # Expected response (status: 200)
   {
     "service": "Merlin Job Application System",
     "version": "4.4.0",
     "overall_status": "healthy",
     "checks": {
       "application": {"status": "healthy", "message": "Application is running"},
       "database": {"status": "healthy", "message": "Database configured: Digital Ocean"}
     }
   }

   # Test main endpoint
   curl https://merlin-job-app-xxxxx.ondigitalocean.app/

   # Test database connectivity
   curl https://merlin-job-app-xxxxx.ondigitalocean.app/api/db/health
   ```

---

### Phase 4: Domain Configuration (Optional, 15 minutes)

#### Step 4.1: Add Custom Domain

If you have a custom domain (e.g., `merlin.yourdomain.com`):

1. **App Platform Dashboard**
   - Go to your app → **Settings** → **Domains**
   - Click **Add Domain**

2. **Configure Domain**
   - **Domain**: `merlin.yourdomain.com`
   - **Type**: Subdomain
   - Click **Add Domain**

3. **Update DNS Records**

   Digital Ocean will provide DNS records to add:

   ```
   Type: CNAME
   Name: merlin
   Value: merlin-job-app-xxxxx.ondigitalocean.app
   TTL: 3600
   ```

   Add these records to your DNS provider (Namecheap, Cloudflare, etc.).

4. **SSL Certificate**
   - App Platform automatically provisions Let's Encrypt SSL
   - ⏱️ Wait 5-10 minutes for DNS propagation
   - Certificate auto-renews every 90 days

5. **Verify HTTPS**
   ```bash
   curl https://merlin.yourdomain.com/health
   ```

---

### Phase 5: CI/CD Workflow (5 minutes)

#### Step 5.1: Test Automated Deployment

1. **Make a Code Change**
   ```bash
   # In your local repository
   git checkout main

   # Make a trivial change (e.g., update version in CLAUDE.md)
   echo "# Test deployment" >> README_TEST.md

   git add README_TEST.md
   git commit -m "test: Verify Digital Ocean auto-deployment"
   git push origin main
   ```

2. **Monitor GitHub Actions**
   - Go to repository → **Actions** tab
   - Watch `Digital Ocean App Platform CI/CD` workflow
   - Verify all jobs pass:
     - ✅ Code Quality Checks
     - ✅ Security Scan
     - ✅ Run Test Suite
     - ✅ Build Docker Image
     - ✅ Validate Schema
     - ✅ Deployment Status

3. **Monitor App Platform Deployment**
   - Go to Digital Ocean → App Platform → Your App
   - Watch **Deployments** tab
   - App Platform detects push to `main`
   - Automatic build and deploy triggered
   - ⏱️ Deployment completes in 3-5 minutes

4. **Verify Updated Deployment**
   ```bash
   curl https://your-app.ondigitalocean.app/health
   # Check if timestamp reflects recent deployment
   ```

---

## Configuration

### Environment Variables Reference

See `.env.production.example` for complete list.

**Critical Variables:**

- `DATABASE_URL`: Auto-injected by App Platform when database is linked
- `DEPLOYMENT_PLATFORM=digitalocean`: Enables DO-specific configuration
- `FLASK_ENV=production`: Disables debug mode, enables optimizations
- `LOG_FORMAT=json`: Structured logging for App Platform log aggregation

### Storage Configuration

**Default: Local Filesystem** (10 GB limit, ephemeral)

```bash
STORAGE_BACKEND=local
LOCAL_STORAGE_PATH=/app/storage/generated_documents
```

**Recommended: Digital Ocean Spaces** (S3-compatible, unlimited, $5/month for 250 GB)

```bash
STORAGE_BACKEND=digitalocean_spaces
SPACES_REGION=nyc3
SPACES_BUCKET=merlin-documents
SPACES_ACCESS_KEY=your_access_key
SPACES_SECRET_KEY=your_secret_key
SPACES_ENDPOINT=https://nyc3.digitaloceanspaces.com
```

**To create Spaces:**
1. Digital Ocean → **Spaces Object Storage** → **Create Space**
2. Region: Match your app region
3. Name: `merlin-documents`
4. Generate API keys
5. Update environment variables in App Platform

### Scaling Configuration

**Horizontal Auto-Scaling:**

1. App Platform → Your App → **Settings** → **Scaling**
2. **Autoscaling**:
   - Min instances: 1
   - Max instances: 3
   - Target CPU: 80%
   - Target Memory: 80%

**Vertical Scaling:**

Upgrade instance size in **Settings** → **Resources** → **Edit** → Select larger tier

---

## Monitoring & Troubleshooting

### Viewing Logs

**App Platform Console:**
1. Go to your app → **Runtime Logs**
2. **Filter by**:
   - Component: `merlin-job-app`
   - Level: `ERROR`, `WARNING`, `INFO`
3. **Search**: Use keywords like "database", "error", "health"

**Real-time Logs (doctl CLI):**

```bash
# Install doctl CLI
brew install doctl  # macOS
# Or download from: https://docs.digitalocean.com/reference/doctl/

# Authenticate
doctl auth init

# Stream logs
doctl apps logs <app-id> --follow

# Get app ID
doctl apps list
```

### Common Issues

#### Issue 1: Health Check Failing

**Symptoms**: Deployment stuck at "Deploying", health check failures

**Diagnosis:**
```bash
# Check logs for errors
doctl apps logs <app-id> --type BUILD
doctl apps logs <app-id> --type RUN

# Common causes:
# - Port mismatch (ensure app listens on 5001 or $PORT)
# - Database connection failure
# - Missing environment variables
```

**Solution:**
```bash
# Verify health endpoint locally
docker build -t merlin-test .
docker run -p 5001:5001 -e DATABASE_URL="..." merlin-test
curl http://localhost:5001/health

# Check App Platform environment variables
# Settings → App-Level Environment Variables
```

#### Issue 2: Database Connection Errors

**Symptoms**: `psycopg2.OperationalError`, "could not connect to server"

**Diagnosis:**
```bash
# Check database status
doctl databases list

# Test connection from local machine
psql "$DATABASE_URL"
```

**Solution:**
- Verify `DATABASE_URL` is correctly set in App Platform
- Ensure database cluster is running
- Check **Trusted Sources** in database settings
- Verify `sslmode=require` is in connection string

#### Issue 3: Build Failures

**Symptoms**: Build phase fails, Docker errors

**Diagnosis:**
```bash
# Review build logs
# Common issues:
# - requirements.txt missing dependencies
# - Dockerfile syntax errors
# - Base image not found
```

**Solution:**
```bash
# Test Docker build locally
docker build -t merlin-local .

# Check requirements.txt is up to date
pip freeze > requirements.txt

# Verify Dockerfile path in App Platform settings
```

### Performance Monitoring

**Built-in Metrics:**
- CPU Usage
- Memory Usage
- Request Rate
- Response Time

**Access Metrics:**
1. App Platform → Your App → **Insights**
2. View graphs for:
   - CPU (target < 80%)
   - Memory (target < 80%)
   - HTTP requests/sec
   - Response time (target < 500ms)

**Alerts:**
1. **Settings** → **Alerts**
2. Configure notifications:
   - CPU > 90% for 5 minutes
   - Memory > 90% for 5 minutes
   - Health check failures > 3
   - Build failures

---

## Cost Breakdown

### Monthly Costs (Production)

| Resource | Tier | Price |
|----------|------|-------|
| **App Platform** | Professional 1GB | $12/month |
| **Managed PostgreSQL** | Dev (1GB RAM) | $15/month |
| **Container Registry** | Included | $0 |
| **Bandwidth** | First 1TB | $0 |
| **SSL Certificate** | Let's Encrypt | $0 |
| **Backups** | Daily automated | $0 |
| **Total** | | **~$27/month** |

### Cost Optimization

**Development/Staging:**
- Basic tier app: $5/month
- Dev database: $15/month
- **Total**: $20/month

**Production with Spaces:**
- Professional app: $12/month
- Standard database: $55/month
- Spaces (250GB): $5/month
- **Total**: $72/month

### Scaling Costs

| Scenario | App Tier | DB Tier | Monthly Cost |
|----------|----------|---------|--------------|
| **Light Traffic** | Basic ($5) | Dev ($15) | $20 |
| **Medium Traffic** | Professional 1GB ($12) | Dev ($15) | $27 |
| **High Traffic** | Professional 2GB ($24) | Standard ($55) | $79 |
| **Enterprise** | Pro 4GB ($48) + Autoscale | Business ($249) | $297+ |

---

## Rollback & Recovery

### Rollback to Previous Deployment

1. **App Platform Console**
   - Go to **Deployments** tab
   - Find previous successful deployment
   - Click **⋯** → **Redeploy**
   - Confirm rollback

2. **Rollback via GitHub**
   ```bash
   # Revert to previous commit
   git log --oneline  # Find commit to revert to
   git revert <commit-hash>
   git push origin main

   # App Platform auto-deploys previous version
   ```

### Database Backup & Restore

**Automated Backups:**
- Daily backups (last 7 days for Dev tier)
- Retained backups: 7 days (configurable)

**Manual Backup:**
```bash
# Create on-demand backup
doctl databases backups create <database-id>

# Or via pg_dump
pg_dump "$DATABASE_URL" > backup_$(date +%Y%m%d).sql
```

**Restore from Backup:**
1. Digital Ocean → Databases → Your DB → **Backups & Restore**
2. Select backup
3. Choose restore option:
   - **Restore to existing cluster** (overwrites data)
   - **Create new cluster from backup** (recommended)

---

## Post-Deployment Checklist

- [ ] Health endpoint returns 200: `https://your-app.ondigitalocean.app/health`
- [ ] Database connectivity verified: `/api/db/health`
- [ ] Main endpoint accessible: `/`
- [ ] Dashboard loads: `/dashboard`
- [ ] SSL certificate valid (HTTPS lock icon)
- [ ] Environment variables configured (check App Platform settings)
- [ ] Logs streaming correctly (no errors)
- [ ] GitHub Actions CI passing
- [ ] Auto-deployment working (test with code push)
- [ ] Database backups enabled
- [ ] Monitoring alerts configured
- [ ] Custom domain configured (if applicable)
- [ ] OAuth flows tested (Gmail, Google Drive)

---

## Additional Resources

### Documentation

- [Digital Ocean App Platform Docs](https://docs.digitalocean.com/products/app-platform/)
- [Managed PostgreSQL Docs](https://docs.digitalocean.com/products/databases/postgresql/)
- [doctl CLI Reference](https://docs.digitalocean.com/reference/doctl/)

### Support

- **Digital Ocean Support**: https://cloud.digitalocean.com/support
- **Community Forums**: https://www.digitalocean.com/community
- **Status Page**: https://status.digitalocean.com/

### Commands Cheatsheet

```bash
# View app logs
doctl apps logs <app-id> --follow

# List apps
doctl apps list

# Restart app
doctl apps update <app-id> --redeploy

# List databases
doctl databases list

# Create database backup
doctl databases backups create <db-id>

# View app metrics
doctl apps metrics <app-id>
```

---

**Deployment completed!** 🎉

Your Merlin Job Application System is now running on Digital Ocean App Platform with automated deployments, managed database, SSL, and monitoring.

**Next Steps:**
1. Monitor application performance and logs
2. Set up alerts for critical metrics
3. Configure custom domain (optional)
4. Test full application workflow
5. Plan for scaling based on traffic
