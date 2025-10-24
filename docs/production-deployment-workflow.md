# Production Deployment Workflow

**Version**: 1.0
**Created**: 2025-10-24
**Purpose**: Automated verification and deployment of database migrations to production

---

## Overview

This system ensures database migrations are properly tested locally and safely deployed to production before merging worktrees.

## Workflow Phases

### Phase 1: Development (Local Worktree)

During development in a worktree:

1. Create migration SQL files in `database_tools/migrations/`
2. Apply migrations to local database
3. Run schema automation: `python database_tools/update_schema.py`
4. Test migrations locally

### Phase 2: Pre-Merge Verification

**Before merging a worktree**, run the verification system:

```bash
python database_tools/verify_production_migrations.py
```

This script will:
- ✓ Verify all local migrations are applied
- ✓ Check production database connectivity
- ✓ Identify which migrations need production deployment
- ✓ Generate deployment instructions

**Expected Output:**

```
======================================================================
VERIFICATION SUMMARY
======================================================================
Local migrations:  ✓
Production access: ⚠️

⚠️  LOCAL OK - Production deployment pending (firewall/access issue)
======================================================================
```

### Phase 3: Production Deployment

#### Option A: From Whitelisted Machine

If your machine has production database access:

```bash
python database_tools/verify_production_migrations.py --apply-to-production
```

This will automatically apply all missing migrations to production.

#### Option B: Manual Deployment

If you don't have direct access:

1. Copy migration files to a machine with production access
2. Run migrations manually:

```bash
# Set production DATABASE_URL from .env
export DATABASE_URL="postgresql://doadmin:password@host:25060/defaultdb?sslmode=require"

# Apply each migration
psql "$DATABASE_URL" -f database_tools/migrations/001_create_security_detections_table.sql
psql "$DATABASE_URL" -f database_tools/migrations/002_create_job_analysis_tiers_table.sql
```

3. Verify migrations applied:

```bash
python database_tools/verify_production_migrations.py
```

### Phase 4: Post-Deployment Verification

After production deployment:

```bash
python database_tools/verify_production_migrations.py
```

**Expected Output:**

```
======================================================================
VERIFICATION SUMMARY
======================================================================
Local migrations:  ✓
Production access: ✓

✓ READY TO MERGE - Production is up to date
======================================================================
```

---

## Integration with Worktree Workflow

### Manual Integration (Current)

Before running `/tree close` or merging:

1. Run verification: `python database_tools/verify_production_migrations.py`
2. Deploy to production if needed
3. Verify production is up to date
4. Then proceed with merge

### Automated Integration (Future)

Add to `.claude/commands/tree-close.md`:

```bash
# Before closing worktree, verify production readiness
python database_tools/verify_production_migrations.py

# If migrations pending, prompt user:
# "⚠️ Production migrations pending. Deploy before merging? (y/n)"
```

---

## Firewall Configuration

### Digital Ocean Database Firewall

The production database firewall only allows connections from whitelisted IPs.

**To Add Your IP:**

1. **Via Dashboard:**
   - Go to: https://cloud.digitalocean.com/databases
   - Select your database
   - Settings → Trusted Sources
   - Click "Add Trusted Source"
   - Add your current public IP

2. **Via API (Automated):**
   ```python
   # Using DIGITALOCEAN_API_TOKEN from .env
   # TODO: Create automated firewall management script
   ```

---

## Migration File Conventions

### File Naming

```
<number>_<descriptive_name>.sql

Examples:
001_create_security_detections_table.sql
002_create_job_analysis_tiers_table.sql
003_add_user_preferences_columns.sql
```

### File Structure

```sql
-- Migration: <filename>
-- Date: <YYYY-MM-DD>
-- Purpose: <description>
-- Part of: <feature/project name>

-- Create tables
CREATE TABLE IF NOT EXISTS table_name (...);

-- Create indexes
CREATE INDEX idx_name ON table_name(column);

-- Add comments
COMMENT ON TABLE table_name IS 'Description';
```

---

## Troubleshooting

### "Connection refused/timeout"

**Cause:** Development environment IP not whitelisted on production firewall

**Solution:**
1. Add your IP to Digital Ocean database firewall (see Firewall Configuration above)
2. Or deploy from a whitelisted machine
3. Or use Digital Ocean console proxy

### "Production configuration not found"

**Cause:** Missing `.env` file with production credentials

**Solution:**
Ensure `/workspace/.env` exists with:
```bash
DATABASE_HOST=db-postgresql-...ondigitalocean.com
DATABASE_PORT=25060
DATABASE_NAME=defaultdb
DATABASE_USER=doadmin
PGPASSWORD=<password>
```

### "Migration already applied" (False Positive)

**Cause:** Migration detection regex issue

**Solution:**
Check migration file manually:
```bash
psql "$DATABASE_URL" -c "\dt table_name"
```

---

## Security Notes

1. **Never commit `.env` file** - It's in `.gitignore`
2. **Rotate credentials if exposed** - Use Digital Ocean dashboard
3. **Use SSL for production** - `sslmode=require` is mandatory
4. **Audit migration files** - Review before production deployment
5. **Backup before migrations** - Digital Ocean provides automated backups

---

## Related Documentation

- [Database Schema Workflow](database-schema-workflow.md)
- [Database Connection Guide](database-connection-guide.md)
- [Digital Ocean Database Setup](setup/digital-ocean-database.md)

---

## Changelog

### 2025-10-24
- ✓ Created production migration verification system
- ✓ Added automated local/production comparison
- ✓ Generated deployment instructions
- ✓ Integrated with worktree workflow documentation
