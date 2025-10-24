# System Startup Warnings - Script Testing Branch

**Captured:** October 9, 2025
**Source:** Flask application startup logs
**Status:** Critical configuration issues requiring attention

## Critical Errors

### 1. Missing Required Environment Variables
```
ERROR: Missing required environment variables:
  - DATABASE_URL
  - SECRET_KEY
  - WEBHOOK_API_KEY (present but weak)
```

**Impact:** Security and functionality compromised

### 2. Weak Security Secrets
```
WARNING: Weak secrets detected (less than 32 chars):
  - WEBHOOK_API_KEY
```

**Impact:** API security vulnerability

### 3. Temporary Session Key Generated
```
WARNING: Generated temporary session key - set SECRET_KEY environment variable
```

**Impact:** Sessions will not persist across server restarts

## Runtime Errors

### 4. AI Integration Failure
```
ERROR: Failed to get usage stats: GEMINI_API_KEY environment variable required
```

**Endpoint:** `/api/ai/usage-stats`
**Impact:** AI job analysis features unavailable

### 5. User Profile System Failure
```
ERROR: User profile system health check failed: DATABASE_URL environment variable not set
```

**Endpoint:** `/api/user-profile/health`
**Impact:** User profile features unavailable despite database being connected

### 6. Document Generation Template Missing
```
ERROR: Template not found: content_template_library/jinja_templates/resume/Accessible-MCS-Resume-Template-Bullet-Points_1751349781656_jinja_template_20250718_021104.docx
```

**Endpoint:** `/resume` (POST)
**Impact:** Resume generation fails

## Route Issues (404 Errors)

### 7. Missing API Routes
The following routes return 404:
- `/api/db/stats/applications` - Route doesn't exist
- `/api/user-profile/steve-glen` - Route doesn't exist
- `/api/workflow/process-application` - Route doesn't exist
- `/api/documents/resume` - Route doesn't exist
- `/api/email/oauth-status` - Wrong path (should be `/api/email/oauth/status`)

## Authentication Issues (401 Errors)

### 8. Protected Endpoints Requiring Auth
The following endpoints properly enforce authentication:
- `/api/db/statistics` - Requires valid WEBHOOK_API_KEY
- `/api/email/oauth/status` - Requires authentication
- `/api/workflow/status` - Requires authentication
- `/api/ai/usage-stats` - Requires authentication
- Link tracking endpoints - Require API key

**Note:** This is correct behavior, but tests need proper API keys

## Security Warnings

### 9. Link Tracking Security Events
```
WARNING: Security Event [AUTH_MISSING_API_KEY]: {'ip_address': '127.0.0.1'}
```

**Impact:** Expected behavior - security controls are working correctly

### 10. Invalid API Key Attempts
```
WARNING: Invalid API key provided for database access
```

**Impact:** Expected behavior - tests attempted access without proper credentials

## Development Server Warning

### 11. Production Server Warning
```
WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
```

**Impact:** Current setup is development-only. Need production WSGI server (Gunicorn/uWSGI)

## Summary

### Critical Issues (Must Fix)
1. ❌ Set `DATABASE_URL` environment variable
2. ❌ Set `SECRET_KEY` environment variable (32+ chars)
3. ❌ Strengthen `WEBHOOK_API_KEY` (32+ chars)
4. ❌ Set `GEMINI_API_KEY` for AI features
5. ❌ Fix document template paths

### Configuration Issues (Should Fix)
6. ⚠️ Verify and correct API route paths
7. ⚠️ Update test scripts with correct endpoint URLs
8. ⚠️ Document API authentication requirements

### Production Readiness (Future)
9. 🔄 Deploy with production WSGI server
10. 🔄 Configure proper logging
11. 🔄 Set up production database connection pooling

## Recommended Actions

### Immediate (Before Testing)
```bash
# 1. Generate secure secrets
python utils/security_key_generator.py

# 2. Create .env file from .env.example
cp .env.example .env

# 3. Edit .env and set:
#    - SECRET_KEY (from security_key_generator.py)
#    - WEBHOOK_API_KEY (from security_key_generator.py)
#    - GEMINI_API_KEY (from Google Cloud Console)
#    - DATABASE_URL (optional but recommended)

# 4. Verify template paths exist
ls -la content_template_library/jinja_templates/resume/
```

### Before Production Deployment
```bash
# 1. Use production WSGI server
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app_modular:app

# 2. Set FLASK_ENV=production
# 3. Disable FLASK_DEBUG=False
# 4. Configure proper logging
# 5. Set up SSL/TLS
```

## Notes

- Database connection IS working via individual parameters (host, port, name, password)
- Some modules expect `DATABASE_URL` as a single connection string
- Security framework is functioning correctly (401/403 responses are expected)
- Core infrastructure is solid - issues are primarily configuration-related
