---
title: "Security Setup Instructions"
type: technical_doc
component: security
status: draft
tags: []
---

# Security Setup Instructions
**Optional but Recommended Pre-Commit Hook**

---

## 🔒 Install Git Pre-Commit Security Hook

This hook prevents accidentally committing secrets, credentials, and sensitive files.

### Installation (1 minute)

```bash
# Navigate to repository root
cd /workspace/.trees/migration-to-digit-ocean

# Copy pre-commit hook to Git hooks directory
cp .git-hooks/pre-commit-security-check.sh .git/hooks/pre-commit

# Make executable
chmod +x .git/hooks/pre-commit

# Test it works
.git/hooks/pre-commit
```

### What It Does

The pre-commit hook automatically:

- ✅ Blocks commits containing `.env` files
- ✅ Blocks commits containing `credentials.json` or `token.json`
- ✅ Scans for hardcoded passwords, API keys, database URLs
- ✅ Detects Digital Ocean managed database passwords (`AVNS_...`)
- ✅ Detects Google API keys (`AIzaSy...`)
- ✅ Warns about large files (potential binary secrets)
- ✅ Verifies `.gitignore` configuration

### Example Usage

```bash
# Attempt to commit .env file (will be blocked)
git add .env
git commit -m "Add config"

# Output:
# 🔒 Running security pre-commit checks...
# ❌ ERROR: Attempting to commit .env file!
# Found: .env
# COMMIT BLOCKED

# Attempt to commit hardcoded password (will be blocked)
# Edit file with: password = "REPLACE_WITH_ACTUAL_PASSWORD"
git add myfile.py
git commit -m "Update config"

# Output:
# ⚠️  WARNING: Potential secret detected!
# Pattern: password\s*=\s*['"][^'"]{8,}['"]
# COMMIT BLOCKED
```

### Bypass Hook (Emergency Only)

```bash
# If you need to bypass (use with extreme caution)
git commit --no-verify -m "message"

# ⚠️ Only use --no-verify if you're certain no secrets are included
```

---

## 📋 Security Checklist (Use Before Every Commit)

Manual review before committing:

- [ ] No `.env` files in commit
- [ ] No `credentials.json` or `token.json` files
- [ ] No hardcoded passwords or API keys
- [ ] No database connection strings with passwords
- [ ] All secrets use environment variables
- [ ] `.gitignore` includes all sensitive file patterns
- [ ] Reviewed `git diff` for accidental secrets

---

## 🛠️ Troubleshooting

**Hook not running:**
```bash
# Verify hook is installed
ls -la .git/hooks/pre-commit

# Verify executable permissions
chmod +x .git/hooks/pre-commit

# Test manually
.git/hooks/pre-commit
```

**False positive:**
```bash
# If hook incorrectly flags safe code:
# 1. Review the flagged content carefully
# 2. Ensure it's not a real secret
# 3. Use --no-verify as last resort (document why)
# 4. Update hook pattern if needed
```

---

## 📚 Related Documentation

- **Comprehensive Security Guide**: `docs/deployment/SECURITY_PRACTICES.md`
- **Password Rotation**: `docs/deployment/PASSWORD_ROTATION_GUIDE.md`
- **Deployment Guide**: `docs/deployment/digitalocean-deployment-guide.md`

---

**Recommendation:** Install this hook on all developer machines working with production code.
