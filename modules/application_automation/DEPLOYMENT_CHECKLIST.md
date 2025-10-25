---
title: "Deployment Checklist"
type: technical_doc
component: application_automation
status: draft
tags: []
---

# Deployment Checklist
## Application Automation Module - MVP to Production

**Version:** 1.0.0
**Target Deployment:** Apify Cloud + Flask Backend
**Last Updated:** 2025-10-14

---

## Pre-Deployment Checklist

### 1. Code Readiness

#### 1.1 Code Review
- [ ] All code follows project standards (PEP 8, Black formatted)
- [ ] Comprehensive docstrings on all functions and classes
- [ ] No hardcoded secrets or credentials in code
- [ ] TODO comments documented for future enhancements
- [ ] Error handling comprehensive and graceful
- [ ] Logging statements appropriate (not too verbose, not too sparse)

#### 1.2 Testing
- [ ] Unit tests pass (>90% pass rate acceptable for MVP)
- [ ] Flask API endpoints tested and working
- [ ] Database operations verified
- [ ] Form mappings validated against real Indeed pages
- [ ] At least 1 successful end-to-end test completed

#### 1.3 Dependencies
- [ ] All dependencies listed in requirements.txt
- [ ] No conflicting dependency versions
- [ ] Playwright version pinned (currently 1.48.0)
- [ ] Apify SDK version pinned (currently >=2.0.0)

---

### 2. Infrastructure Setup

#### 2.1 Database
- [ ] Table `apify_application_submissions` created in production database
- [ ] Indexes created and verified
- [ ] Triggers created and tested
- [ ] Database backup taken before deployment
- [ ] Migration rollback script ready (if needed)

#### 2.2 Flask Backend
- [ ] Blueprint registered in `app_modular.py`
- [ ] API endpoints accessible
- [ ] Authentication middleware configured
- [ ] Rate limiting configured (if applicable)
- [ ] CORS configured correctly (if needed for frontend)

#### 2.3 Environment Variables
- [ ] `.env` file configured for production (or environment variables set)
  ```bash
  APIFY_TOKEN=<prod_token>
  APPLICATION_AUTOMATION_ACTOR_ID=<username>/<actor-name>
  WEBHOOK_API_KEY=<secure_key>
  FLASK_API_URL=<prod_url>
  STORAGE_BACKEND=local (or cloud provider)
  LOCAL_STORAGE_PATH=./storage/screenshots
  ```
- [ ] Secrets rotated from development values
- [ ] API keys have appropriate permissions
- [ ] Backup of production `.env` stored securely (encrypted)

---

### 3. Apify Actor Deployment

#### 3.1 Actor Repository Setup

**Option A: Deploy from Current Repository (Quick)**
```bash
# 1. Navigate to module directory
cd modules/application_automation

# 2. Initialize Apify project (if not already done)
apify init

# 3. Configure actor.json with production settings
# Edit .actor/actor.json

# 4. Test locally
apify run

# 5. Deploy to Apify
apify push
```

**Option B: Separate GitHub Repository (Recommended for Production)**
```bash
# 1. Create new GitHub repository
gh repo create apify-application-filler --public

# 2. Clone and setup
git clone https://github.com/yourusername/apify-application-filler
cd apify-application-filler

# 3. Copy Actor files from current repo
cp -r /workspace/.trees/apply-assistant/modules/application_automation/* ./

# 4. Remove Flask-specific files
rm -rf automation_api.py models.py tests/test_integration.py

# 5. Keep only Actor-related files:
# - actor_main.py
# - form_filler.py
# - data_fetcher.py
# - screenshot_manager.py
# - form_mappings/
# - .actor/
# - README.md (update for Actor-specific docs)

# 6. Initialize Apify
apify init

# 7. Push to GitHub
git add .
git commit -m "Initial Actor setup"
git push origin main

# 8. Deploy to Apify from GitHub
apify push
```

#### 3.2 Actor Configuration Checklist
- [ ] Actor name set correctly
- [ ] Actor description clear and accurate
- [ ] Input schema validated (`.actor/input_schema.json`)
- [ ] Dockerfile optimized (Playwright dependencies included)
- [ ] Memory allocation appropriate (recommend 2048MB minimum)
- [ ] Timeout set appropriately (recommend 600s / 10 minutes)
- [ ] Environment variables configured in Apify Console:
  - `FLASK_API_URL`
  - `WEBHOOK_API_KEY`
- [ ] Actor secrets configured (not in code):
  - API keys
  - Authentication tokens

#### 3.3 Actor Testing on Apify Platform
- [ ] Test run executed successfully on Apify
- [ ] Actor completes without errors
- [ ] Logs show expected behavior
- [ ] Screenshots uploaded to Key-Value Store
- [ ] Results pushed to Dataset
- [ ] Webhook callback to Flask works (if configured)

---

### 4. Integration Testing

#### 4.1 Flask → Apify Integration
- [ ] Trigger endpoint successfully calls Apify Actor
- [ ] Actor Run ID returned and stored
- [ ] Actor completes and reports back to Flask
- [ ] Submission record created in database
- [ ] Screenshots accessible via Flask API

#### 4.2 Apify → Flask Integration
- [ ] Actor can reach Flask API from Apify infrastructure
- [ ] API key authentication works
- [ ] Data fetcher retrieves job details correctly
- [ ] Data fetcher retrieves applicant profile correctly
- [ ] Documents (resume, cover letter) downloaded successfully

#### 4.3 Database Integration
- [ ] Submission records created correctly
- [ ] Status updates work (pending → submitted → reviewed)
- [ ] Timestamps accurate (UTC)
- [ ] JSON fields (screenshot_urls, fields_filled) parse correctly
- [ ] Queries performant (indexes working)

---

### 5. Security Audit

#### 5.1 Authentication & Authorization
- [ ] All API endpoints require authentication
- [ ] API keys are strong (>32 characters)
- [ ] API keys stored securely (Apify Secrets, not in code)
- [ ] Rate limiting configured to prevent abuse
- [ ] No default/test credentials in production

#### 5.2 Data Protection
- [ ] No PII logged in plain text
- [ ] Sensitive data encrypted in transit (HTTPS)
- [ ] Database credentials not exposed
- [ ] Screenshots contain no unintended sensitive data
- [ ] Error messages don't leak system information

#### 5.3 Input Validation
- [ ] All API inputs validated
- [ ] SQL injection prevention (parameterized queries)
- [ ] XSS prevention (input sanitization)
- [ ] File upload validation (if applicable)
- [ ] JSON schema validation for Actor inputs

---

### 6. Monitoring & Logging

#### 6.1 Logging Setup
- [ ] Application logs configured
- [ ] Log level set appropriately (INFO for production)
- [ ] Sensitive data redacted from logs
- [ ] Log rotation configured
- [ ] Logs centralized (if using log aggregation service)

#### 6.2 Monitoring Setup
- [ ] Apify Actor runs monitored via Apify Console
- [ ] Flask API health endpoint available
- [ ] Database connection monitoring
- [ ] Error rate monitoring
- [ ] Success rate tracking (submission confirmations)

#### 6.3 Alerting
- [ ] Critical error alerts configured
- [ ] Actor failure notifications setup
- [ ] Database connection failure alerts
- [ ] Unusual activity detection (optional)

---

### 7. Documentation

#### 7.1 Technical Documentation
- [ ] README.md updated with deployment instructions
- [ ] API documentation complete (endpoints, parameters, responses)
- [ ] Architecture diagram updated
- [ ] Database schema documented
- [ ] Form mapping documentation updated

#### 7.2 Operational Documentation
- [ ] Deployment checklist completed (this document)
- [ ] Rollback procedure documented
- [ ] Troubleshooting guide created
- [ ] Incident response plan (optional, but recommended)

#### 7.3 User Documentation
- [ ] User guide for reviewing submissions
- [ ] FAQ for common issues
- [ ] Contact information for support

---

### 8. Backup & Recovery

#### 8.1 Backup Strategy
- [ ] Database backup schedule configured
- [ ] Code backed up to Git repository (GitHub)
- [ ] Environment configuration documented securely
- [ ] Screenshots backup strategy (if critical)

#### 8.2 Recovery Plan
- [ ] Rollback script prepared
- [ ] Database restore procedure tested
- [ ] Actor redeployment procedure documented
- [ ] Service degradation plan (manual fallback process)

---

### 9. Performance Testing

#### 9.1 Load Testing (Optional for MVP, Recommended for Production)
- [ ] Test with multiple concurrent submissions
- [ ] Verify database performance under load
- [ ] Check Actor scaling behavior
- [ ] Monitor memory usage during runs

#### 9.2 Optimization
- [ ] Database indexes optimized for common queries
- [ ] Actor memory allocation appropriate
- [ ] Screenshot compression configured
- [ ] Unnecessary logging removed

---

### 10. Go-Live Checklist

#### 10.1 Final Verification
- [ ] All above checklist items completed
- [ ] Stakeholder approval received
- [ ] Maintenance window scheduled (if needed)
- [ ] Communication sent to users (if applicable)

#### 10.2 Deployment Steps
1. [ ] **Database Migration**
   ```bash
   # Run migration script
   psql -U $PGUSER -d $DATABASE_NAME -f migrations/001_create_application_submissions.sql

   # Verify table created
   psql -U $PGUSER -d $DATABASE_NAME -c "\d apify_application_submissions"
   ```

2. [ ] **Deploy Flask Changes**
   ```bash
   # Pull latest code
   git pull origin main

   # Restart Flask application
   systemctl restart flask-app  # or your restart command

   # Verify blueprint registered
   curl http://localhost:5000/health
   ```

3. [ ] **Deploy Apify Actor**
   ```bash
   # From Actor directory
   apify push

   # Note the Actor URL
   # Update APPLICATION_AUTOMATION_ACTOR_ID in Flask .env
   ```

4. [ ] **Smoke Test**
   ```bash
   # Trigger test automation
   curl -X POST https://your-api.com/api/application-automation/trigger \
     -H "Content-Type: application/json" \
     -H "X-API-Key: $WEBHOOK_API_KEY" \
     -d '{"job_id": "test_job_prod", "application_id": "test_app_prod"}'

   # Verify in Apify Console
   # Verify in database
   psql -U $PGUSER -d $DATABASE_NAME -c \
     "SELECT * FROM apify_application_submissions WHERE job_id='test_job_prod';"
   ```

5. [ ] **Monitor Initial Runs**
   - Watch Apify Actor logs for first 3-5 runs
   - Check database for correct data
   - Verify screenshots are captured
   - Check for any errors or warnings

#### 10.3 Post-Deployment
- [ ] Monitor system for 24 hours
- [ ] Review logs for unexpected errors
- [ ] Verify success rate acceptable (>70% for MVP)
- [ ] Collect user feedback
- [ ] Document any issues encountered

---

### 11. Rollback Plan

#### 11.1 Rollback Triggers
Roll back if:
- Critical bugs causing data corruption
- Success rate <30%
- System instability or crashes
- Security vulnerabilities discovered

#### 11.2 Rollback Steps
1. [ ] **Stop New Submissions**
   ```bash
   # Disable Actor or remove trigger endpoint temporarily
   ```

2. [ ] **Revert Flask Changes**
   ```bash
   git checkout <previous_commit>
   systemctl restart flask-app
   ```

3. [ ] **Revert Database Changes** (if necessary)
   ```bash
   psql -U $PGUSER -d $DATABASE_NAME << 'SQL'
   BEGIN;
   DROP TRIGGER IF EXISTS trigger_update_apify_application_submissions_updated_at
     ON apify_application_submissions;
   DROP FUNCTION IF EXISTS update_apify_application_submissions_updated_at();
   DROP TABLE IF EXISTS apify_application_submissions CASCADE;
   COMMIT;
   SQL
   ```

4. [ ] **Revert Apify Actor**
   ```bash
   # Revert to previous Actor version in Apify Console
   # Or deploy previous version
   apify push --version-number <previous_version>
   ```

5. [ ] **Verify Rollback**
   - System returns to previous stable state
   - No data loss or corruption
   - Users notified of rollback (if applicable)

---

### 12. Success Metrics

#### 12.1 MVP Success Criteria (First 30 Days)
- [ ] At least 10 successful applications submitted
- [ ] Success rate >70%
- [ ] Zero critical bugs
- [ ] User feedback positive
- [ ] No security incidents

#### 12.2 Production Success Criteria (First 90 Days)
- [ ] 100+ successful applications
- [ ] Success rate >80%
- [ ] Form mappings updated as needed (Indeed changes)
- [ ] User satisfaction >4/5
- [ ] Ready for additional platforms (Greenhouse, Lever)

---

## Deployment Sign-Off

| Role | Name | Signature | Date |
|------|------|-----------|------|
| **Developer** | ____________ | ____________ | ______ |
| **Tech Lead** | ____________ | ____________ | ______ |
| **Product Owner** | ____________ | ____________ | ______ |
| **DevOps** | ____________ | ____________ | ______ |

---

## Post-Deployment Notes

**Deployment Date:** __________________
**Deployed By:** __________________
**Deployment Result:** Success / Partial / Failed
**Issues Encountered:**
-
-

**Follow-Up Actions:**
-
-

---

**End of Deployment Checklist**
