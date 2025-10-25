# Production Deployment Checklist

**Worktree**: create-securitydetections-table-in-production-data
**Date**: 2025-10-24
**Migration Tables**: `security_detections`, `job_analysis_tiers`

---

## Pre-Merge Checklist

Run this checklist **before merging** this worktree to main:

### ☐ 1. Verify Local Migrations

```bash
python database_tools/verify_production_migrations.py
```

**Expected Result:**
- ✓ All migrations applied to local database
- ✓ Schema automation completed
- ✓ Generated models/schemas updated

### ☐ 2. Test Local Functionality

```bash
# Test that new tables work locally
python -c "
from modules.database.database_manager import DatabaseManager
db = DatabaseManager()

# Test security_detections table
result = db.execute_query('SELECT COUNT(*) as count FROM security_detections;')
print(f'security_detections table: {result[0][\"count\"]} rows')

# Test job_analysis_tiers table
result = db.execute_query('SELECT COUNT(*) as count FROM job_analysis_tiers;')
print(f'job_analysis_tiers table: {result[0][\"count\"]} rows')

print('✓ Local tables functional')
"
```

### ☐ 3. Review Migration Files

Manually review each migration file before production deployment:

- [ ] `001_create_security_detections_table.sql`
- [ ] `002_create_job_analysis_tiers_table.sql`

**Check for:**
- ✓ No destructive operations (DROP, DELETE, TRUNCATE)
- ✓ Uses `CREATE TABLE IF NOT EXISTS`
- ✓ Proper indexes for performance
- ✓ Foreign keys reference existing tables
- ✓ Comments document table purpose

---

## Production Deployment

### ☐ 4. Connect to Production

**Option A: Whitelist Your IP** (Recommended for frequent deployments)

1. Get your public IP: `curl https://ifconfig.me`
2. Add to Digital Ocean:
   - Dashboard → Databases → merlin-tor1 → Settings → Trusted Sources
   - Add IP address with description: "Dev Environment - Temporary"

3. Test connection:
   ```bash
   python database_tools/verify_production_migrations.py
   ```

**Option B: Use Whitelisted Machine**

1. SSH to production server or whitelisted machine
2. Clone repo and checkout this worktree
3. Run deployment from there

### ☐ 5. Deploy to Production

**Automated Deployment** (if connected):

```bash
python database_tools/verify_production_migrations.py --apply-to-production
```

**Manual Deployment** (if using separate machine):

```bash
export DATABASE_URL="postgresql://doadmin:[REDACTED]@db-postgresql-merlin-tor1-52568-do-user-27870072-0.e.db.ondigitalocean.com:25060/defaultdb?sslmode=require"

psql "$DATABASE_URL" -f database_tools/migrations/001_create_security_detections_table.sql
psql "$DATABASE_URL" -f database_tools/migrations/002_create_job_analysis_tiers_table.sql
```

### ☐ 6. Verify Production Deployment

```bash
python database_tools/verify_production_migrations.py
```

**Expected Output:**
```
✓ READY TO MERGE - Production is up to date
```

### ☐ 7. Test Production Tables

```bash
# Connect to production and verify tables exist
psql "$DATABASE_URL" -c "\dt security_detections"
psql "$DATABASE_URL" -c "\dt job_analysis_tiers"

# Check row counts (should be 0 for new tables)
psql "$DATABASE_URL" -c "SELECT COUNT(*) FROM security_detections;"
psql "$DATABASE_URL" -c "SELECT COUNT(*) FROM job_analysis_tiers;"
```

---

## Post-Deployment

### ☐ 8. Update Documentation

- [ ] Verify `docs/database_schema.md` includes new tables
- [ ] Check `frontend_templates/database_schema.html` shows new tables
- [ ] Confirm `generated/models.py` has new table classes

### ☐ 9. Commit Generated Files

```bash
git status

# Should show:
# - frontend_templates/database_schema.html
# - generated/models.py
# - generated/schemas.py
# - generated/crud.py
# - generated/routes.py
# - docs/database_schema.md
# - docs/database_schema.json

# Commit if needed
git add -A
git commit -m "chore: Update schema automation after production deployment"
```

### ☐ 10. Clean Up Firewall (If Using Option A)

If you added a temporary IP to the firewall:

1. Digital Ocean Dashboard → Databases → Settings → Trusted Sources
2. Remove temporary development IP
3. Keep only permanent trusted sources

---

## Rollback Plan

If issues occur after production deployment:

### Drop Tables (Nuclear Option)

```sql
-- Connect to production
psql "$DATABASE_URL"

-- Drop tables in reverse dependency order
DROP TABLE IF EXISTS security_detections CASCADE;
DROP TABLE IF EXISTS job_analysis_tiers CASCADE;
```

### Restore from Backup

Digital Ocean provides automatic daily backups:

1. Digital Ocean Dashboard → Databases → Backups
2. Select backup before migration
3. Restore to point-in-time

---

## Sign-Off

**Deployed By**: _______________
**Date**: _______________
**Production Status**: ☐ Ready to Merge

---

## Next Steps After Merge

1. Delete worktree: `/tree close`
2. Monitor production for errors
3. Check application logs for database connection issues
4. Verify tiered analysis system works with new tables

---

**Related Documentation:**
- [Production Deployment Workflow](docs/production-deployment-workflow.md)
- [Database Schema Workflow](docs/database-schema-workflow.md)
- [Deployment Checklist](docs/deployment/DEPLOYMENT_CHECKLIST.md)
