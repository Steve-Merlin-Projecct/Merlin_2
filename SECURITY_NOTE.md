# Security Note - API Key Management

**Date:** 2025-10-24
**Importance:** 🔐 CRITICAL

---

## ⚠️ API Key Security

### Where API Keys Are Stored

**✅ SECURE (Intentional):**
- `steve-glen-com-handoff/STEVE_GLEN_API_KEY.md` - **This file is MEANT to contain the key** for sharing with steve-glen.com team
- This folder should be shared securely (encrypted email, secure file transfer, private git repo)

**✅ NO KEYS (Secure):**
- All Python code files (`.py`) - Use environment variables only
- All documentation outside handoff folder - Use placeholders only
- `.env.example` - Template with placeholders

**❌ NEVER COMMIT:**
- `.env` file with actual keys
- Any file with real API keys outside the handoff folder

---

## 🔒 How API Keys Are Secured

### In Code

Production code uses environment variables:

```python
# ✅ CORRECT - No hardcoded keys
API_KEY = os.getenv('STEVE_GLEN_TRACKING_API_KEY') or os.getenv('WEBHOOK_API_KEY')

if not API_KEY:
    logger.warning("API key not configured")
    return False
```

```python
# ❌ WRONG - Never do this
API_KEY = 'actual-key-here'  # NEVER hardcode keys!
```

### In Documentation

Documentation uses placeholders:

```bash
# ✅ CORRECT - Placeholder
curl -H "X-API-Key: YOUR_API_KEY_HERE"

# ✅ CORRECT - Reference to secure location
# Get API key from: steve-glen-com-handoff/STEVE_GLEN_API_KEY.md
```

```bash
# ❌ WRONG - Never put real keys in docs
curl -H "X-API-Key: actual-secret-key-here-never-do-this"
```

---

## 📋 Checklist Before Committing

Before you `git add` or `git commit`:

- [ ] Check: No API keys in `.py` files (use `git grep -E '[A-Za-z0-9_-]{40,}'`)
- [ ] Check: No API keys in documentation outside `steve-glen-com-handoff/`
- [ ] Check: `.env` file is in `.gitignore`
- [ ] Check: Only `.env.example` is committed (with placeholders)
- [ ] Verify: `steve-glen-com-handoff/` folder handling plan

---

## 🔐 API Key Locations

### Production (DigitalOcean)
```bash
# Set in DigitalOcean App Platform
# Settings → Environment Variables → Edit
STEVE_GLEN_TRACKING_API_KEY=<actual-key>
```

### Local Development
```bash
# Add to .env file (gitignored)
echo "WEBHOOK_API_KEY=<actual-key>" >> .env

# Or export in terminal
export WEBHOOK_API_KEY='<actual-key>'
```

### Testing (Local)
```bash
# Add to .env file (if testing locally)
echo "STEVE_GLEN_TRACKING_API_KEY=<actual-key>" >> .env

# Get key from: steve-glen-com-handoff/STEVE_GLEN_API_KEY.md
```

**Note:** For production deployment, testing happens on the production server after deployment.

---

## 🚨 What To Do If Key Is Exposed

If an API key is accidentally committed to a public repository or otherwise exposed:

1. **Immediately rotate the key:**
   ```bash
   # Generate new key
   python -c "import secrets; print(secrets.token_urlsafe(48))"
   # Example output: NewRandomKey123...
   ```

2. **Update production:**
   - DigitalOcean → Settings → Environment Variables
   - Replace `STEVE_GLEN_TRACKING_API_KEY` with new value

3. **Update local:**
   - Update `.env` file
   - Update `steve-glen-com-handoff/STEVE_GLEN_API_KEY.md`

4. **Notify steve-glen.com team** of the new key

5. **Clean git history** (if needed):
   ```bash
   # Remove from git history (use with caution)
   git filter-branch --force --index-filter \
     'git rm --cached --ignore-unmatch <file-with-key>' \
     --prune-empty --tag-name-filter cat -- --all
   ```

---

## ✅ Best Practices

1. **Environment Variables**
   - Always use `os.getenv()` for keys
   - Never hardcode secrets in code

2. **Documentation**
   - Use placeholders: `YOUR_API_KEY_HERE`
   - Reference secure locations: "See STEVE_GLEN_API_KEY.md"

3. **Git**
   - Add `.env` to `.gitignore`
   - Use `.env.example` with placeholders
   - Review diffs before committing

4. **Handoff Folder**
   - `steve-glen-com-handoff/STEVE_GLEN_API_KEY.md` should contain real key
   - Share this folder securely (not via public channels)
   - Recommend deleting file after extracting key

5. **Production**
   - Use DigitalOcean's encrypted environment variables
   - Enable encryption checkbox
   - Rotate keys every 90-180 days

---

## 📁 .gitignore Configuration

Ensure these files are in `.gitignore`:

```gitignore
# Environment variables
.env
.env.local
.env.*.local

# API keys
*_API_KEY.txt
*_SECRET.txt
credentials.json

# Logs (may contain sensitive data)
*.log
```

---

## 🎯 Summary

**Secure API Key Handling:**
- ✅ Environment variables in code
- ✅ Placeholders in documentation
- ✅ Real keys ONLY in `steve-glen-com-handoff/STEVE_GLEN_API_KEY.md`
- ✅ `.env` file gitignored
- ✅ Production keys encrypted in DigitalOcean

**Before Every Commit:**
1. Search for keys: `git grep -E '[A-Za-z0-9_-]{40,}'`
2. Review diff: `git diff --cached`
3. Verify .gitignore includes `.env`
4. Confirm no secrets in staged files

---

**Security is critical!** 🔐

When in doubt, use environment variables and placeholders.
