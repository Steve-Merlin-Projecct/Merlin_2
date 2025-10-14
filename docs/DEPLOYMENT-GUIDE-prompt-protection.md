# Deployment Guide: Prompt Protection System
**Production Deployment Checklist & Procedures**

---

## Pre-Deployment Checklist

### Code Review
- [ ] Review all changes in `ai_analyzer.py`
- [ ] Review all changes in `app_modular.py`
- [ ] Review all tier prompt files (tier1, tier2, tier3)
- [ ] Review `prompt_security_manager.py` implementation
- [ ] Verify all `# PROMPT_START` / `# PROMPT_END` markers present

### Testing
- [ ] Run unit tests: `pytest tests/test_prompt_protection_integration.py -v`
- [ ] Run manual test script: `python tools/test_prompt_protection.py`
- [ ] Verify all tests pass
- [ ] Test CLI tools functionality
- [ ] Verify no regressions in existing functionality

### Documentation
- [ ] Review implementation plan completeness
- [ ] Verify testing checklist accuracy
- [ ] Check all documentation updated
- [ ] Verify CLI tool usage instructions clear

### Environment
- [ ] Verify `GEMINI_API_KEY` environment variable set
- [ ] Verify `storage/` directory exists and writable
- [ ] Check disk space for log files
- [ ] Verify Python dependencies installed

---

## Deployment Steps

### Step 1: Backup Current State
```bash
# Backup current storage directory (if exists)
cp -r storage/ storage_backup_$(date +%Y%m%d_%H%M%S)/

# Backup current app files
cp app_modular.py app_modular.py.backup
cp modules/ai_job_description_analysis/ai_analyzer.py modules/ai_job_description_analysis/ai_analyzer.py.backup
```

### Step 2: Deploy Code Changes
```bash
# Pull latest changes from git (if using version control)
git pull origin main

# Or manually copy updated files
# Ensure all modified files are in place
```

### Step 3: Clear Old Storage (First Deployment Only)
```bash
# Remove any test/development hash registries
rm -f storage/prompt_hashes.json
rm -f storage/prompt_changes.jsonl
rm -f storage/security_incidents.jsonl
```

### Step 4: Start Application
```bash
# Start app (will register prompts on startup)
python app_modular.py

# Or if using systemd/supervisor
systemctl restart job-application-system
```

### Step 5: Verify Registration
```bash
# Check prompt protection status
python tools/check_prompt_protection.py

# Expected output:
# 🔐 PROMPT PROTECTION STATUS
# ================================================================================
#
# 📊 Total Registered Prompts: 3
#
# 📄 tier1_core_prompt
#    Hash: a3f9d2e8b4c7c9f1...
#    Registered: 2025-10-13T10:00:00.000000
#    Last Updated: 2025-10-13T10:00:00.000000
#    Updated By: system
```

### Step 6: Monitor Logs
```bash
# Watch application logs for any errors
tail -f logs/application.log

# Look for these messages:
# ✅ Prompt security manager initialized
# Registering Tier 1 core prompt...
# Registering Tier 2 enhanced prompt...
# Registering Tier 3 strategic prompt...
# ✅ All AI prompts registered and protected
```

### Step 7: Test Protection
```bash
# Run basic protection test
python tools/test_prompt_protection.py

# Expected: All tests pass
```

---

## Post-Deployment Validation

### Immediate Checks (First Hour)
- [ ] Verify app starts without errors
- [ ] Check all 3 prompts registered successfully
- [ ] Verify storage files created correctly
- [ ] Test one job analysis request (Tier 1)
- [ ] Check logs for any warnings or errors
- [ ] Verify no "⚠️ prompt was replaced" warnings (normal operation)

### Short-Term Monitoring (First 24 Hours)
- [ ] Monitor `storage/prompt_changes.jsonl` for unexpected entries
- [ ] Check `storage/security_incidents.jsonl` for any incidents
- [ ] Verify performance impact < 10ms (check logs)
- [ ] Test Tier 2 and Tier 3 analysis (if used)
- [ ] Review error logs for any new issues

### Long-Term Monitoring (First Week)
- [ ] Review audit log for patterns
- [ ] Check for any false positives (user changes detected as agent)
- [ ] Verify all legitimate user changes tracked correctly
- [ ] Monitor system performance metrics
- [ ] Review security incident log (should be empty unless attacked)

---

## Rollback Procedure

**If issues are detected, follow this rollback plan:**

### Quick Rollback (< 5 minutes)

**Option 1: Disable Validation (Keep System Running)**
```bash
# Edit ai_analyzer.py
# Comment out validation calls in _create_batch_analysis_prompt()

# In ai_analyzer.py line ~667-683:
# validated_prompt, was_replaced = self.security_mgr.validate_and_handle_prompt(...)
# Comment out the above, replace with:
validated_prompt = prompt  # TEMPORARY ROLLBACK

# Restart app
systemctl restart job-application-system
```

**Option 2: Full Rollback (Restore Previous Version)**
```bash
# Restore backup files
cp app_modular.py.backup app_modular.py
cp modules/ai_job_description_analysis/ai_analyzer.py.backup modules/ai_job_description_analysis/ai_analyzer.py

# Restart app
systemctl restart job-application-system
```

### Validate Rollback
```bash
# Check app starts successfully
curl http://localhost:5000/health

# Verify job analysis still works
# (test with a sample job request)

# Check logs for stability
tail -f logs/application.log
```

### Post-Rollback Analysis
- Document exact error/issue that triggered rollback
- Review logs for root cause
- Test fix in development environment
- Re-deploy with fix when ready

---

## Troubleshooting Common Issues

### Issue 1: Prompts Not Registering
**Symptom:** App starts but `storage/prompt_hashes.json` not created

**Solution:**
```bash
# Check for import errors
python -c "from modules.ai_job_description_analysis.prompt_security_manager import PromptSecurityManager; print('OK')"

# Check permissions
ls -la storage/
chmod 755 storage/

# Check logs for errors
grep "prompt" logs/application.log
```

### Issue 2: Hash Mismatch on Every Request
**Symptom:** Constant "⚠️ prompt was replaced" warnings

**Possible Causes:**
- Security token not being extracted correctly
- Prompt generation not deterministic
- Race condition in multi-threaded environment

**Solution:**
```bash
# Check security token extraction
python tools/test_prompt_protection.py

# Review prompt generation consistency
# (tokens should be stable across requests)

# If multi-threaded, ensure thread-safety
```

### Issue 3: Performance Degradation
**Symptom:** Requests slower than before deployment

**Solution:**
```bash
# Check validation overhead
# Add timing logs in ai_analyzer.py

import time
start = time.time()
validated_prompt, was_replaced = self.security_mgr.validate_and_handle_prompt(...)
logger.info(f"Validation took: {(time.time() - start) * 1000:.2f}ms")

# Expected: < 10ms
# If > 50ms, investigate hash computation or file I/O
```

### Issue 4: Storage Files Growing Too Large
**Symptom:** `prompt_changes.jsonl` > 100MB

**Solution:**
```bash
# Implement log rotation
# Add to cron job:
0 0 * * * /path/to/rotate_prompt_logs.sh

# rotate_prompt_logs.sh:
#!/bin/bash
cd /path/to/storage
mv prompt_changes.jsonl prompt_changes_$(date +%Y%m%d).jsonl
mv security_incidents.jsonl security_incidents_$(date +%Y%m%d).jsonl
# Keep last 30 days only
find . -name "prompt_changes_*.jsonl" -mtime +30 -delete
find . -name "security_incidents_*.jsonl" -mtime +30 -delete
```

---

## Security Considerations

### Access Control
- Restrict access to `storage/` directory (only app user)
- Protect `tools/update_prompt_hash.py` (admin only)
- Review audit logs regularly

### Monitoring & Alerts
Set up alerts for:
- Multiple security incidents in short time (> 5/hour)
- Unauthorized hash updates (change_source: agent)
- Storage directory issues (permissions, disk space)

### Regular Audits
**Weekly:**
- Review `prompt_changes.jsonl` for unexpected changes
- Check `security_incidents.jsonl` for attack attempts
- Verify all prompts still registered correctly

**Monthly:**
- Full security review of protection system
- Update hashes after any intentional prompt changes
- Review and archive old log files

---

## Performance Benchmarks

**Expected Performance:**
- Hash validation: < 5ms per request
- Token extraction: < 2ms per request
- Total overhead: < 10ms per request
- Memory impact: < 1MB additional

**Monitoring Commands:**
```bash
# Check response times
grep "Validation took" logs/application.log | tail -20

# Check memory usage
ps aux | grep python | grep app_modular

# Check storage file sizes
du -sh storage/*
```

---

## Success Metrics

**After 1 Week:**
- ✅ 0 unauthorized agent modifications detected (or proper replacement occurred)
- ✅ 100% of legitimate user changes tracked correctly
- ✅ No false positives (normal operations = no warnings)
- ✅ Performance impact < 10ms consistently
- ✅ No production incidents related to prompt protection

**After 1 Month:**
- ✅ System stable with no rollbacks required
- ✅ Audit log provides clear visibility into all changes
- ✅ Security incidents log empty (or only test/attack attempts)
- ✅ CLI tools used regularly for monitoring
- ✅ Team comfortable with hash update workflow

---

## Maintenance Schedule

**Daily:**
- Check for security incidents
- Monitor application logs

**Weekly:**
- Review audit log (`prompt_changes.jsonl`)
- Verify protection status (`python tools/check_prompt_protection.py`)

**Monthly:**
- Archive old log files
- Review and optimize storage usage
- Security audit of protection system

**Quarterly:**
- Full system review
- Update documentation based on lessons learned
- Optimize performance if needed

---

## Support & Contact

**For Issues:**
1. Check troubleshooting section above
2. Review logs in `logs/application.log`
3. Check audit logs in `storage/prompt_changes.jsonl`
4. Run diagnostic: `python tools/test_prompt_protection.py`

**Documentation:**
- Implementation Plan: `docs/IMPLEMENTATION-PLAN-prompt-protection.md`
- Testing Checklist: `docs/TESTING-CHECKLIST-prompt-protection.md`
- Reference Guide: `docs/prompt-protection-reference.md`
- Round-Trip Validation: `docs/round-trip-token-validation.md`

---

**Deployment Completed:** ___/___/_____
**Deployed By:** __________________
**Rollback Tested:** [ ] Yes [ ] No
**Sign-Off:** __________________
