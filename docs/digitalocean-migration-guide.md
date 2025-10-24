---
title: "Digitalocean Migration Guide"
type: guide
component: general
status: draft
tags: []
---

# DigitalOcean Managed PostgreSQL Migration Guide

**Date:** 2025-10-21
**Version:** 4.3.2
**Target:** DigitalOcean Managed Database (PostgreSQL)

---

## Overview

This guide provides a complete checklist for migrating the Merlin Job Application System from local/Docker PostgreSQL to DigitalOcean Managed Database.

**Migration Readiness:** ✅ All code changes complete. System ready for migration.

---

## Pre-Migration Checklist

### ✅ Code Changes (COMPLETED)

All necessary code changes have been implemented:

1. ✅ **SSL/TLS Support** - Added in `database_config.py`
2. ✅ **Flexible Connection Pool** - Environment-configurable in `database_client.py`
3. ✅ **Connection String Builder** - Supports managed database parameters
4. ✅ **Health Monitoring** - `/api/db/health` endpoint tracks pool utilization
5. ✅ **Error Handling** - Robust retry logic and error codes
6. ✅ **Query Timeout** - 30s timeout prevents runaway queries

### 📋 DigitalOcean Setup Required

#### 1. Create DigitalOcean Managed Database

**Recommended Plan:**
- **Basic Plan ($15/mo):** 1GB RAM, 10GB storage, 25 connections
- **Professional Plan ($60/mo):** 4GB RAM, 38GB storage, 97 connections
- **Choose based on:** Expected concurrent users and connection pool needs

**Configuration:**
1. Go to DigitalOcean Console → Databases → Create Database
2. Choose **PostgreSQL** (version 14+ recommended)
3. Select datacenter region (closest to your users)
4. Choose database plan based on needs
5. Name your database cluster (e.g., `merlin-production-db`)

#### 2. Download SSL Certificate

DigitalOcean provides a CA certificate for secure connections:

```bash
# From DigitalOcean Console → Database → Settings
# Download CA certificate → Save as:
./storage/certificates/digitalocean-ca-certificate.crt
```

⚠️ **IMPORTANT:** Add certificate path to `.gitignore` to avoid committing

#### 3. Get Connection Details

From DigitalOcean Console → Database → Connection Details:

```
Host: your-db-cluster.db.ondigitalocean.com
Port: 25060
Database: defaultdb (or custom name)
User: doadmin (or custom user)
Password: [generated password]
```

---

## Environment Variables Configuration

### Required Environment Variables

Update your `.env` file or production environment with:

```bash
# =============================================================================
# DigitalOcean Managed PostgreSQL Configuration
# =============================================================================

# Option 1: Use full connection string (RECOMMENDED)
DATABASE_URL=postgresql://doadmin:YOUR_PASSWORD@your-cluster.db.ondigitalocean.com:25060/defaultdb?sslmode=require

# Option 2: Use individual components
DATABASE_HOST=your-cluster.db.ondigitalocean.com
DATABASE_PORT=25060
DATABASE_NAME=defaultdb
DATABASE_USER=doadmin
DATABASE_PASSWORD=YOUR_PASSWORD_HERE

# SSL/TLS Configuration (REQUIRED for DigitalOcean)
DATABASE_SSL_MODE=require
DATABASE_SSL_ROOT_CERT=./storage/certificates/digitalocean-ca-certificate.crt

# Connection Pool Configuration (adjust based on your plan)
# Basic Plan (25 connections): Use pool_size=5, max_overflow=10 (total: 15)
# Professional Plan (97 connections): Use pool_size=20, max_overflow=30 (total: 50)
DATABASE_POOL_SIZE=5
DATABASE_MAX_OVERFLOW=10
DATABASE_POOL_TIMEOUT=30
DATABASE_POOL_RECYCLE=300
```

### Connection Pool Sizing Guidelines

**Formula:** `total_app_connections < (database_max_connections * 0.8)`

**DigitalOcean Connection Limits by Plan:**
- **Basic ($15/mo):** 25 connections → Use pool=5, overflow=10 (15 total)
- **Professional ($60/mo):** 97 connections → Use pool=20, overflow=30 (50 total)
- **Business ($290/mo):** 197 connections → Use pool=40, overflow=80 (120 total)

**Reserve 20% for:**
- Manual admin connections
- Monitoring tools
- Backup operations
- Emergency access

---

## SSL/TLS Configuration Details

### SSL Modes Explained

```bash
# Choose appropriate SSL mode:

# sslmode=disable  ❌ NOT RECOMMENDED - No encryption
DATABASE_SSL_MODE=disable

# sslmode=require  ✅ RECOMMENDED - Encrypted, doesn't verify server
DATABASE_SSL_MODE=require

# sslmode=verify-ca  ✅ BEST - Encrypted, verifies CA certificate
DATABASE_SSL_MODE=verify-ca

# sslmode=verify-full  🔒 MAXIMUM - Encrypted, verifies CA + hostname
DATABASE_SSL_MODE=verify-full
```

**For DigitalOcean:** Use `require` or `verify-ca` with CA certificate

### Certificate Setup

```bash
# Create certificates directory
mkdir -p ./storage/certificates

# Download DigitalOcean CA certificate
# From: DigitalOcean Console → Database → Settings → CA Certificate
# Save to: ./storage/certificates/digitalocean-ca-certificate.crt

# Verify certificate is valid
openssl x509 -in ./storage/certificates/digitalocean-ca-certificate.crt -text -noout

# Add to .gitignore
echo "storage/certificates/*.crt" >> .gitignore
```

---

## Data Migration Steps

### Step 1: Export Current Database

```bash
# Export schema and data from local PostgreSQL
pg_dump -h localhost -U postgres -d local_Merlin_3 \
  --clean --if-exists --create \
  -f merlin_backup_$(date +%Y%m%d).sql

# Verify backup file size
ls -lh merlin_backup_*.sql
```

### Step 2: Import to DigitalOcean

```bash
# Set DigitalOcean connection details
export PGHOST=your-cluster.db.ondigitalocean.com
export PGPORT=25060
export PGUSER=doadmin
export PGPASSWORD=YOUR_PASSWORD
export PGDATABASE=defaultdb
export PGSSLMODE=require

# Import backup to DigitalOcean
psql < merlin_backup_20251021.sql

# Verify import
psql -c "\dt"  # List tables
psql -c "SELECT COUNT(*) FROM jobs;"  # Check data
```

### Step 3: Test Connection

```bash
# Test connection with new environment variables
python -c "
from modules.database.lazy_instances import get_database_client
client = get_database_client()
print('✅ Connected!' if client.test_connection() else '❌ Failed')
"
```

---

## Post-Migration Verification

### 1. Run Health Check

```bash
# Test health endpoint
curl http://localhost:5000/api/db/health

# Expected response:
{
  "status": "healthy",
  "database_connected": true,
  "connection_pool": {
    "size": 5,
    "checked_in": 4,
    "checked_out": 1,
    "utilization_percent": 6.67,
    "status": "healthy"
  }
}
```

### 2. Verify SSL Connection

```python
# Check SSL is enabled
from modules.database.lazy_instances import get_database_client
from sqlalchemy import text

client = get_database_client()
with client.get_session() as session:
    result = session.execute(text("SHOW ssl"))
    print(f"SSL: {result.fetchone()[0]}")  # Should be "on"
```

### 3. Run Integration Tests

```bash
# Run database integration tests
pytest tests/integration/test_db_connection.py -v

# Run full test suite
pytest tests/ -v --tb=short
```

### 4. Monitor Connection Pool

```bash
# Monitor pool utilization over time
watch -n 5 'curl -s http://localhost:5000/api/db/health | jq .connection_pool'
```

---

## Performance Tuning

### Connection Pool Optimization

Based on your workload, adjust pool settings:

```bash
# For HIGH TRAFFIC (many concurrent requests):
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=30

# For LOW TRAFFIC (background tasks):
DATABASE_POOL_SIZE=5
DATABASE_MAX_OVERFLOW=10

# For BURST TRAFFIC (occasional spikes):
DATABASE_POOL_SIZE=10
DATABASE_MAX_OVERFLOW=20
```

### Query Timeout Adjustment

```bash
# Default: 30 seconds
# Adjust if you have known slow queries:

# For complex analytics (increase):
DATABASE_QUERY_TIMEOUT=60  # 60 seconds

# For strict real-time (decrease):
DATABASE_QUERY_TIMEOUT=10  # 10 seconds
```

**Note:** Query timeout is set in `database_client.py:66` via `statement_timeout`

---

## Monitoring & Alerts

### DigitalOcean Metrics

Monitor in DigitalOcean Console → Database → Metrics:

- **CPU Usage:** Keep < 80%
- **Memory Usage:** Keep < 85%
- **Connection Count:** Keep < 80% of limit
- **Disk Usage:** Keep < 80%

### Application-Level Monitoring

```bash
# Set up alerts for high pool utilization
# Check: /api/db/health → connection_pool.utilization_percent

# Alert thresholds:
# WARNING:  utilization > 75%
# CRITICAL: utilization > 90%
```

### Recommended Monitoring Tools

- **DigitalOcean Monitoring:** Built-in metrics and alerts
- **Datadog:** Application performance monitoring
- **Sentry:** Error tracking and alerting
- **Prometheus + Grafana:** Custom metrics dashboards

---

## Rollback Plan

If migration fails, revert to local database:

```bash
# 1. Stop application
sudo systemctl stop merlin-app

# 2. Restore old environment variables
cp .env.backup .env

# 3. Restart application
sudo systemctl start merlin-app

# 4. Verify local connection
curl http://localhost:5000/api/db/health
```

---

## Common Issues & Solutions

### Issue 1: SSL Connection Failed

**Error:** `SSL connection has been closed unexpectedly`

**Solution:**
```bash
# Verify CA certificate path
ls -la ./storage/certificates/digitalocean-ca-certificate.crt

# Check SSL mode
echo $DATABASE_SSL_MODE  # Should be "require" or "verify-ca"

# Test connection manually
psql "postgresql://user:pass@host:port/db?sslmode=require"
```

### Issue 2: Connection Pool Exhausted

**Error:** `QueuePool limit of size 10 overflow 20 reached`

**Solution:**
```bash
# Increase pool limits
DATABASE_POOL_SIZE=15
DATABASE_MAX_OVERFLOW=25

# Or reduce application concurrency
# Check for connection leaks in code
```

### Issue 3: Query Timeout

**Error:** `canceling statement due to statement timeout`

**Solution:**
```bash
# Identify slow query in logs
grep "statement timeout" logs/app.log

# Optimize query or increase timeout
# For specific slow queries, use @log_query_performance decorator
```

### Issue 4: Max Connections Exceeded

**Error:** `FATAL: remaining connection slots are reserved`

**Solution:**
```bash
# Check current connections
psql -c "SELECT count(*) FROM pg_stat_activity;"

# Reduce pool size
DATABASE_POOL_SIZE=5
DATABASE_MAX_OVERFLOW=10

# Or upgrade DigitalOcean plan for more connections
```

---

## Security Checklist

- [ ] SSL/TLS enabled (`DATABASE_SSL_MODE=require`)
- [ ] CA certificate downloaded and secured
- [ ] Database password stored in environment variables (not code)
- [ ] `.env` file added to `.gitignore`
- [ ] Firewall configured (DigitalOcean Trusted Sources)
- [ ] Database backups enabled (DigitalOcean automatic backups)
- [ ] Connection pooling configured (prevents connection exhaustion)
- [ ] Query timeout enabled (prevents runaway queries)

---

## Production Deployment Checklist

### Before Deployment

- [ ] Backup current database
- [ ] Test connection to DigitalOcean database
- [ ] Update environment variables
- [ ] Configure connection pool for your plan
- [ ] Download and configure SSL certificate
- [ ] Run integration tests
- [ ] Set up monitoring alerts

### During Deployment

- [ ] Put application in maintenance mode
- [ ] Stop application
- [ ] Update environment variables
- [ ] Start application with new config
- [ ] Verify health endpoint
- [ ] Test critical user flows

### After Deployment

- [ ] Monitor connection pool utilization
- [ ] Check application logs for errors
- [ ] Verify SSL connections
- [ ] Test backup/restore procedures
- [ ] Document any issues encountered
- [ ] Update runbook with learnings

---

## Cost Optimization

### Right-Sizing Your Database

**Start Small, Scale Up:**

1. **Start:** Basic Plan ($15/mo, 25 connections)
2. **Monitor:** Connection pool utilization, CPU, memory
3. **Upgrade if:**
   - Pool utilization consistently > 75%
   - CPU usage > 80%
   - Memory usage > 85%

### Scaling Guidelines

```
Users     | Connections Needed | Recommended Plan
----------|-------------------|------------------
< 100     | 15-25            | Basic ($15/mo)
100-500   | 25-50            | Professional ($60/mo)
500-2000  | 50-100           | Business ($290/mo)
2000+     | 100+             | Custom cluster
```

---

## Additional Resources

### DigitalOcean Documentation

- [Managed PostgreSQL Overview](https://docs.digitalocean.com/products/databases/postgresql/)
- [Connection Pools](https://docs.digitalocean.com/products/databases/postgresql/how-to/manage-connection-pools/)
- [SSL Connections](https://docs.digitalocean.com/products/databases/postgresql/how-to/secure-connections/)
- [Monitoring](https://docs.digitalocean.com/products/databases/postgresql/how-to/monitor-metrics/)

### Project Documentation

- `docs/database-connection-guide.md` - Connection architecture
- `docs/database-robustness-improvements.md` - Recent improvements
- `modules/database/database_config.py` - Configuration code
- `modules/database/database_client.py` - Connection pooling

---

## Summary

**Required Changes for Migration:**

1. ✅ **Code:** Already updated with SSL support and flexible pooling
2. 📝 **Environment Variables:** Update `.env` with DigitalOcean details
3. 🔐 **SSL Certificate:** Download from DigitalOcean and configure path
4. ⚙️ **Connection Pool:** Adjust based on your plan limits
5. 📊 **Monitoring:** Set up alerts for pool utilization

**Estimated Migration Time:** 1-2 hours

**Zero Downtime?** Possible with blue-green deployment (not covered here)

**Rollback Time:** < 5 minutes

---

**Ready to Migrate?** Follow the steps above and you're good to go! 🚀

