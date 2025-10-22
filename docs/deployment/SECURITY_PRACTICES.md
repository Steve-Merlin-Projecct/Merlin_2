# Security Best Practices - Production Deployment
**Critical Security Guidelines for Digital Ocean Deployment**

---

## 🔒 Overview

This document outlines mandatory security practices for protecting sensitive credentials, database passwords, API keys, and other secrets in both development and production environments.

**Last Updated**: 2025-10-22
**Applies To**: All Merlin Job Application System deployments

---

## 🚨 Critical Rules - NEVER VIOLATE

### Rule 1: NEVER Commit Secrets to Git

**Prohibited Actions:**
- ❌ NEVER commit `.env` files to Git
- ❌ NEVER commit `.env.production` files to Git
- ❌ NEVER commit database passwords in code
- ❌ NEVER commit API keys in code
- ❌ NEVER commit OAuth credentials (`credentials.json`, `token.json`)
- ❌ NEVER commit SSH keys or certificates
- ❌ NEVER hardcode passwords in source code
- ❌ NEVER commit files with actual production values

**Verification:**
```bash
# Check .gitignore includes sensitive files
grep -E "^\.env$|credentials.*\.json|token.*\.json" .gitignore

# Scan for accidentally committed secrets (before commit)
git diff --cached | grep -iE "password|api_key|secret_key|token"

# Check Git history for leaked secrets
git log -p | grep -iE "AVNS_|password.*=.*[a-zA-Z0-9]{20}"
```

---

### Rule 2: Use Environment Variables for ALL Secrets

**Required Approach:**

```python
# ✅ CORRECT - Use environment variables
import os
database_password = "REPLACE_WITH_ACTUAL_PASSWORD"
api_key = os.environ.get('GEMINI_API_KEY')

# ❌ WRONG - Hardcoded secrets
database_password = "REPLACE_WITH_ACTUAL_PASSWORD"
api_key = "REPLACE_WITH_ACTUAL_KEY"  # NEVER DO THIS
```

**Environment Variable Sources:**
- **Local Development**: `.env` file (gitignored)
- **CI/CD**: GitHub Secrets
- **Production**: Digital Ocean App Platform environment variables

---

### Rule 3: Use GitHub Secrets for CI/CD

**Setup:**

1. **Navigate to Repository Settings**
   - GitHub repo → Settings → Secrets and variables → Actions

2. **Add Required Secrets** (mark as "Secret" = encrypted at rest):
   - `DATABASE_URL` - Production database connection string
   - `WEBHOOK_API_KEY` - API authentication key
   - `SECRET_KEY` - Flask session encryption key
   - `GEMINI_API_KEY` - Google Gemini AI key
   - `APIFY_API_TOKEN` - Job scraping service token
   - `GMAIL_CREDENTIALS_JSON` - Base64-encoded OAuth credentials
   - `GOOGLE_DRIVE_CREDENTIALS_JSON` - Base64-encoded OAuth credentials

3. **Reference in GitHub Actions**:
   ```yaml
   # .github/workflows/deploy-digitalocean.yml
   env:
     DATABASE_URL: ${{ secrets.DATABASE_URL }}
     GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
   ```

**Security Benefits:**
- ✅ Encrypted at rest
- ✅ Encrypted in transit
- ✅ Audit logging of access
- ✅ No secrets in workflow logs
- ✅ Scoped to repository only

---

### Rule 4: Use App Platform Environment Variables for Production

**Setup in Digital Ocean:**

1. **App Platform Console** → Your App → Settings → App-Level Environment Variables
2. Click **"Add Variable"** for each secret
3. **Mark as "Encrypt"** (checkbox) for sensitive values
4. Use `${database-name.DATABASE_URL}` syntax for linked resources

**Required Production Variables:**
```bash
# Deployment
DEPLOYMENT_PLATFORM=digitalocean  # Not sensitive
FLASK_ENV=production              # Not sensitive
FLASK_DEBUG=False                 # Not sensitive

# Database (encrypted)
DATABASE_URL=${merlin-postgres-prod.DATABASE_URL}  # Auto-injected, encrypted

# API Keys (encrypted)
WEBHOOK_API_KEY=***              # Mark as Secret ✅
SECRET_KEY=***                   # Mark as Secret ✅
GEMINI_API_KEY=***               # Mark as Secret ✅
APIFY_API_TOKEN=***              # Mark as Secret ✅

# OAuth (encrypted, base64-encoded)
GMAIL_CREDENTIALS_JSON=***       # Mark as Secret ✅
GOOGLE_DRIVE_CREDENTIALS_JSON=***  # Mark as Secret ✅

# User Info (not sensitive)
USER_EMAIL_ADDRESS=your@email.com
USER_DISPLAY_NAME=Steve Glen
```

**Security Features:**
- ✅ Encrypted at rest (when marked as "Encrypt")
- ✅ Not visible in logs
- ✅ Accessible only to your app
- ✅ Audit trail in Digital Ocean console

---

## 📂 File Protection Matrix

| File Type | Git | Docker Image | Production |
|-----------|-----|--------------|------------|
| `.env` | ❌ Excluded (.gitignore) | ❌ Excluded (.dockerignore) | ❌ Use env vars |
| `.env.production` | ❌ Excluded | ❌ Excluded | ❌ Use env vars |
| `.env.example` | ✅ Committed (no secrets) | ❌ Not needed | ❌ Not needed |
| `credentials.json` | ❌ Excluded | ❌ Excluded | ✅ Base64 in env var |
| `token.json` | ❌ Excluded | ❌ Excluded | ✅ Base64 in env var |
| `*.key`, `*.pem` | ❌ Excluded | ❌ Excluded | ❌ Never use |
| Source code (`*.py`) | ✅ Committed | ✅ Included | ✅ Included |

---

## 🔐 Database Password Security

### Current Database
**Connection String:**
```
postgresql://doadmin:REPLACE_WITH_ACTUAL_PASSWORD@host.example.com:25060/defaultdb?sslmode=require
```

### Mandatory Practices

**✅ DO:**
- Store in `DATABASE_URL_PRODUCTION` environment variable (local)
- Store in GitHub Secrets as `DATABASE_URL` (CI/CD)
- Store in App Platform environment variables as `DATABASE_URL` (production)
- Use `sslmode=require` for all connections
- Rotate password after initial setup (see Password Rotation section)

**❌ DON'T:**
- Never commit to Git
- Never hardcode in Python files
- Never include in Docker image
- Never share in public channels (Slack, email, etc.)
- Never log to console/files
- Never include in error messages

### Secure Storage Locations

**Local Development:**
```bash
# .env file (gitignored)
DATABASE_URL_PRODUCTION="postgresql://REPLACE_WITH_ACTUAL_CREDENTIALS"
```

**GitHub Secrets:**
- Name: `DATABASE_URL`
- Value: Full connection string (encrypted)

**App Platform:**
- Auto-injected when database is linked: `${merlin-postgres-prod.DATABASE_URL}`
- Marked as "Encrypt" ✅

---

## 🔄 Password Rotation Procedures

### When to Rotate Passwords

**Mandatory Rotation:**
- ⚠️ Password exposed in public forum/chat
- ⚠️ Password committed to Git (even if removed)
- ⚠️ Suspicious database access detected
- ⚠️ Team member with access leaves
- ⚠️ Security breach or incident

**Recommended Rotation:**
- 🔁 Every 90 days (quarterly)
- 🔁 After initial setup/testing
- 🔁 Before production launch
- 🔁 When best practices recommend

### How to Rotate Database Password

**Step 1: Reset Password in Digital Ocean**

1. Digital Ocean Dashboard → Databases → Your Database
2. **Settings** tab → **Security** section
3. Click **"Reset Password"**
4. **Copy new password** immediately
5. **Save securely** (password manager)

**Step 2: Update Environment Variables**

```bash
# Local development (.env file)
nano .env
# Update DATABASE_URL_PRODUCTION with new password

# GitHub Secrets
# 1. Go to Settings → Secrets → Actions
# 2. Edit DATABASE_URL secret
# 3. Paste new connection string

# Digital Ocean App Platform
# 1. Go to App → Settings → Environment Variables
# 2. If using linked database: password updates automatically
# 3. If using custom DATABASE_URL: edit and update password
# 4. Redeploy app (required for changes to take effect)
```

**Step 3: Redeploy Application**

```bash
# App Platform auto-redeploys when env vars change
# Or manually trigger:
# App Platform → Your App → Actions → Force Redeploy
```

**Step 4: Verify Connections**

```bash
# Test from local machine
psql "$DATABASE_URL_PRODUCTION"

# Test App Platform health endpoint
curl https://your-app.ondigitalocean.app/health

# Check for database errors in logs
doctl apps logs <app-id> | grep -i "database\|connection"
```

---

## 🔑 API Key Management

### Google Gemini API Key

**Current Status:** Stored in `.env` file (local)

**Security Requirements:**
- ✅ Store in `GEMINI_API_KEY` environment variable
- ✅ Add to GitHub Secrets (for CI/CD)
- ✅ Add to App Platform (for production)
- ✅ Rotate if exposed or quarterly
- ❌ Never commit to Git
- ❌ Never include in error messages or logs

**Rotation Process:**
1. Google AI Studio → API Keys → Create new key
2. Update environment variables (local, GitHub, App Platform)
3. Test integration
4. Revoke old key

### Apify API Token

**Security Requirements:**
- ✅ Store in `APIFY_API_TOKEN` environment variable
- ✅ Add to GitHub Secrets
- ✅ Add to App Platform environment variables
- ❌ Never expose in client-side code
- ❌ Never log token value

**Rotation Process:**
1. Apify Console → Settings → API Tokens → Create new token
2. Update environment variables everywhere
3. Test scraping functionality
4. Revoke old token

### Flask Secret Keys

**SECRET_KEY and SESSION_SECRET:**

**Generation:**
```bash
# Generate new secret key (64 characters)
python -c "import secrets; print(secrets.token_hex(32))"

# Generate session secret (64 characters)
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

**Security Requirements:**
- ✅ Unique per environment (dev, staging, production)
- ✅ Minimum 32 characters
- ✅ Cryptographically random
- ✅ Rotate every 90 days or after exposure
- ❌ Never reuse across environments
- ❌ Never use weak/predictable values

---

## 🔐 OAuth Credentials (Gmail, Google Drive)

### Secure Handling

**Storage Format:**
- Local: JSON files in `storage/` directory (gitignored)
- CI/CD: Base64-encoded in GitHub Secrets
- Production: Base64-encoded in App Platform environment variables

**Base64 Encoding:**
```bash
# Encode credentials
cat storage/gmail_credentials.json | base64 > gmail_creds_b64.txt

# Decode in application (automatic)
import os
import base64
import json

creds_b64 = os.environ.get('GMAIL_CREDENTIALS_JSON')
creds_json = base64.b64decode(creds_b64).decode('utf-8')
credentials = json.loads(creds_json)
```

**Security Requirements:**
- ✅ Never commit `credentials.json` or `token.json` to Git
- ✅ Store base64-encoded in environment variables (production)
- ✅ Use OAuth 2.0 (never store passwords)
- ✅ Revoke tokens if compromised
- ❌ Never share credentials files
- ❌ Never expose client secrets in logs

**Rotation/Revocation:**
1. Google Cloud Console → APIs & Services → Credentials
2. Delete compromised credentials
3. Create new OAuth 2.0 Client ID
4. Download new credentials
5. Update environment variables
6. Re-authenticate (generates new token)

---

## 📊 Security Monitoring

### Audit Checklist (Weekly)

- [ ] Review GitHub Actions logs for exposed secrets
- [ ] Check App Platform logs for authentication failures
- [ ] Verify no `.env` files in Git history
- [ ] Confirm all secrets marked as "Encrypt" in App Platform
- [ ] Review database access logs (Digital Ocean console)
- [ ] Check for unauthorized API usage (Gemini, Apify dashboards)
- [ ] Verify SSL certificates valid (App Platform auto-renews)

### Automated Security Scans

**GitHub Actions includes:**
- ✅ Safety (dependency vulnerability scanning)
- ✅ Bandit (Python security linting)
- ✅ Code quality checks

**Additional Tools (Optional):**
```bash
# Scan for secrets in Git history
pip install detect-secrets
detect-secrets scan

# Scan for hardcoded passwords
pip install truffleHog
truffleHog --regex --entropy=True .

# Dependency audit
safety check --json
```

---

## 🚨 Incident Response

### If Secrets Are Exposed

**Immediate Actions (within 1 hour):**

1. **Assess Exposure**
   - Where was it exposed? (Git, chat, email, public forum)
   - Who has access?
   - How long was it exposed?

2. **Rotate Credentials Immediately**
   - Database password → Reset in Digital Ocean
   - API keys → Revoke and regenerate
   - OAuth tokens → Revoke in Google Cloud Console
   - Flask secrets → Generate new keys

3. **Update All Environments**
   - Local `.env` files
   - GitHub Secrets
   - App Platform environment variables
   - Team member machines

4. **Verify No Unauthorized Access**
   - Check database access logs
   - Review API usage metrics
   - Check for unexpected deployments
   - Review application logs for anomalies

5. **Git History Cleanup (if committed)**
   ```bash
   # Remove from latest commit
   git reset HEAD~1
   git add .  # Re-add without sensitive files
   git commit -m "Remove sensitive data"

   # Remove from entire history (use with caution)
   git filter-branch --force --index-filter \
     'git rm --cached --ignore-unmatch .env' \
     --prune-empty --tag-name-filter cat -- --all

   # Force push (coordinate with team first!)
   git push origin --force --all
   ```

6. **Document Incident**
   - What was exposed
   - How it happened
   - Actions taken
   - Lessons learned
   - Prevention measures added

---

## ✅ Security Compliance Checklist

### Pre-Deployment Verification

Before deploying to production, verify:

- [ ] `.gitignore` includes `.env`, `.env.production`, `credentials*.json`, `token*.json`
- [ ] `.dockerignore` excludes all sensitive files
- [ ] No secrets hardcoded in Python source files
- [ ] All API keys stored in environment variables
- [ ] GitHub Secrets configured for CI/CD
- [ ] App Platform environment variables configured
- [ ] Database password stored securely (not in code)
- [ ] `sslmode=require` in database connection string
- [ ] Flask `SECRET_KEY` is cryptographically random
- [ ] OAuth credentials base64-encoded
- [ ] `FLASK_DEBUG=False` in production
- [ ] Security scanning enabled in CI/CD pipeline

### Post-Deployment Verification

After deploying:

- [ ] Verify environment variables loaded correctly
- [ ] Test database connection with SSL
- [ ] Confirm no secrets in application logs
- [ ] Check GitHub Actions logs for exposed values
- [ ] Verify App Platform "Encrypt" checkboxes enabled
- [ ] Test OAuth flows work in production
- [ ] Confirm API rate limits configured
- [ ] Review Digital Ocean access logs

---

## 📚 Additional Resources

**Digital Ocean Security:**
- [App Platform Security Best Practices](https://docs.digitalocean.com/products/app-platform/how-to/manage-environment-variables/)
- [Managed Database Security](https://docs.digitalocean.com/products/databases/postgresql/how-to/secure/)

**GitHub Security:**
- [Encrypted Secrets](https://docs.github.com/en/actions/security-guides/encrypted-secrets)
- [Security Hardening for Actions](https://docs.github.com/en/actions/security-guides/security-hardening-for-github-actions)

**Python Security:**
- [OWASP Python Security](https://owasp.org/www-project-python-security/)
- [Bandit Security Linter](https://bandit.readthedocs.io/)

---

## 🔒 Summary

**Never commit secrets. Always use environment variables. Rotate regularly.**

- ✅ `.env` files gitignored
- ✅ `.dockerignore` excludes sensitive files
- ✅ GitHub Secrets for CI/CD
- ✅ App Platform encrypted environment variables
- ✅ Database password rotation procedures documented
- ✅ API key management practices defined
- ✅ OAuth credentials base64-encoded
- ✅ Incident response procedures ready
- ✅ Security monitoring checklist provided

**Questions or Security Concerns?** Review this document and update as needed.

**Last Reviewed:** 2025-10-22
**Next Review Due:** 2026-01-22 (Quarterly)
