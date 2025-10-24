# PENDING: Production Migration Deployment

**Status**: ⚠️ Awaiting Production Deployment
**Priority**: High
**Created**: 2025-10-24
**Worktree**: create-securitydetections-table-in-production-data
**Estimated Time**: 15 minutes

---

## Context

The `security_detections` and `job_analysis_tiers` tables have been:
- ✅ Created in local development database
- ✅ Tested and verified locally
- ✅ Generated SQLAlchemy models/schemas/routes
- ✅ Documented in schema automation
- ⚠️ **NOT YET DEPLOYED TO PRODUCTION**

---

## Outstanding Tasks

### Task 1: Deploy Migrations to Production Database

**What**: Apply 2 migration files to Digital Ocean production database

**Migrations Needed**:
1. `database_tools/migrations/001_create_security_detections_table.sql`
   - Creates `security_detections` table (10 columns, 5 indexes)
   - Purpose: Logs LLM injection attempts, unpunctuated text streams

2. `database_tools/migrations/002_create_job_analysis_tiers_table.sql`
   - Creates `job_analysis_tiers` table (19 columns, 7 indexes)
   - Purpose: Tracks 3-tier sequential batch analysis workflow

**Why**: These tables are referenced by code that will be deployed when this worktree merges:
- `modules/ai_job_description_analysis/tier1_analyzer.py`
- `modules/ai_job_description_analysis/tier2_analyzer.py`
- `modules/ai_job_description_analysis/tier3_analyzer.py`
- `modules/ai_job_description_analysis/sequential_batch_scheduler.py`
- `modules/security/unpunctuated_text_detector.py`

**Impact if Not Deployed**:
- ❌ Tiered analysis system will fail with "table does not exist" errors
- ❌ Security detection logging will fail
- ❌ Production application errors

---

## How to Deploy

### Pre-Deployment: Verify Status

```bash
# Run from repository root
python database_tools/verify_production_migrations.py
```

This will show:
- Current production migration status
- Which migrations need deployment
- Deployment instructions

### Option A: Automated Deployment (Recommended)

**Prerequisites**:
- IP address whitelisted on Digital Ocean database firewall
- Production database credentials in `.env` file

**Steps**:

1. Whitelist your IP:
   - Get IP: `curl https://ifconfig.me`
   - Digital Ocean Dashboard → Databases → merlin-tor1 → Settings → Trusted Sources
   - Add IP with description: "Temporary - Migration Deployment"

2. Run automated deployment:
   ```bash
   python database_tools/verify_production_migrations.py --apply-to-production
   ```

3. Verify deployment:
   ```bash
   python database_tools/verify_production_migrations.py
   # Should show: "✓ READY TO MERGE - Production is up to date"
   ```

4. Remove temporary IP from firewall

### Option B: Manual Deployment

**From a whitelisted machine**:

```bash
# Set production connection
export DATABASE_URL="postgresql://doadmin:[REDACTED]@db-postgresql-merlin-tor1-52568-do-user-27870072-0.e.db.ondigitalocean.com:25060/defaultdb?sslmode=require"

# Apply migrations
psql "$DATABASE_URL" -f database_tools/migrations/001_create_security_detections_table.sql
psql "$DATABASE_URL" -f database_tools/migrations/002_create_job_analysis_tiers_table.sql

# Verify tables created
psql "$DATABASE_URL" -c "\dt security_detections"
psql "$DATABASE_URL" -c "\dt job_analysis_tiers"
```

### Option C: Via Digital Ocean Console

1. Digital Ocean Dashboard → Databases → merlin-tor1 → Console
2. Copy/paste contents of migration files
3. Execute SQL
4. Verify tables created

---

## Post-Deployment Checklist

After production deployment:

- [ ] Run verification script to confirm deployment
- [ ] Check table row counts (should be 0 for new tables)
- [ ] Monitor application logs for database errors
- [ ] Test tiered analysis API endpoints
- [ ] Update this task status to COMPLETED

---

## Verification Commands

**Check Production Tables Exist**:
```bash
psql "$DATABASE_URL" -c "
SELECT table_name,
       (SELECT count(*) FROM information_schema.columns
        WHERE table_name = t.table_name) as column_count
FROM information_schema.tables t
WHERE table_schema = 'public'
  AND table_name IN ('security_detections', 'job_analysis_tiers');
"
```

**Expected Output**:
```
        table_name        | column_count
--------------------------+--------------
 security_detections      |           10
 job_analysis_tiers       |           19
```

---

## Related Documentation

- **Deployment Workflow**: `docs/production-deployment-workflow.md`
- **Deployment Checklist**: `database_tools/PRODUCTION_DEPLOYMENT_CHECKLIST.md`
- **Migration Files**: `database_tools/migrations/`
- **Verification Script**: `database_tools/verify_production_migrations.py`

---

## Timeline

**Recommended Deployment Window**: Before next production release
**Urgency**: Deploy before merging this worktree OR ensure deployment happens immediately after merge
**Risk**: Medium - New code depends on these tables

---

## Success Criteria

✅ Verification script shows: "✓ READY TO MERGE - Production is up to date"
✅ Both tables exist in production database
✅ No application errors related to missing tables
✅ Tiered analysis endpoints functional

---

## Notes for Future Deployment

- Digital Ocean database firewall only allows whitelisted IPs
- Production credentials are in `/workspace/.env` (gitignored)
- SSL mode is required: `sslmode=require`
- Migrations use `CREATE TABLE IF NOT EXISTS` - safe to re-run
- Automated verification system handles connectivity issues gracefully

---

**Deployment Status**: ⬜ NOT DEPLOYED
**Deployed By**: _______________
**Deployment Date**: _______________
**Verified By**: _______________
