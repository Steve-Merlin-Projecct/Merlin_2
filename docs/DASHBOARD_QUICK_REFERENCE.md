---
title: "Dashboard Quick Reference"
type: reference
component: general
status: draft
tags: []
---

# Dashboard Quick Reference

**Last Updated:** 2025-10-22
**App:** https://merlin-sea-turtle-app-ckmbz.ondigitalocean.app/
**Dashboard:** https://merlin-sea-turtle-app-ckmbz.ondigitalocean.app/dashboard

---

## Dashboard URLs

| URL | Description |
|-----|-------------|
| `/dashboard` | Main dashboard (V2) |
| `/dashboard/jobs` | Browse all jobs |
| `/dashboard/applications` | Track applications |
| `/dashboard/analytics` | Performance metrics |
| `/dashboard/schema` | Database schema view |
| `/dashboard/v1` | Legacy dashboard |

---

## API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/dashboard/authenticate` | POST | Login |
| `/dashboard/logout` | POST | Logout |
| `/api/v2/dashboard/overview` | GET | Dashboard data |
| `/api/stream/dashboard` | GET | Real-time updates (SSE) |
| `/health` | GET | Health check |

---

## Environment Variables (Production)

### Required
```bash
WEBHOOK_API_KEY=<generate-with-security-tool>
SESSION_SECRET=<generate-with-security-tool>
DATABASE_URL=postgresql://user:pass@host:port/db
```

### Recommended
```bash
FLASK_ENV=production
FLASK_DEBUG=False
LOG_LEVEL=INFO
LOG_FORMAT=json
DEPLOYMENT_PLATFORM=digitalocean
```

### Optional
```bash
LOG_FILE=/var/log/merlin/app.log
CORS_ORIGINS=https://your-domain.com
```

---

## Security Key Generation

```bash
python utils/security_key_generator.py
```

---

## Database Configuration

### Priority Order
1. `DATABASE_URL` (highest - recommended for production)
2. Individual components (`DATABASE_HOST`, `DATABASE_PORT`, etc.)
3. Fallback defaults

### Current (Docker Dev)
```
Host: host.docker.internal
Port: 5432
Database: local_Merlin_3
User: postgres
Password: $PGPASSWORD
```

---

## Quick Start (Local)

```bash
# 1. Set environment variables
export PGPASSWORD=your_db_password
export DATABASE_NAME=local_Merlin_3

# 2. Start application
python app_modular.py

# 3. Access dashboard
open http://localhost:5000/dashboard

# 4. Login with dashboard password
```

---

## Quick Start (Production - Digital Ocean)

```bash
# 1. Set environment variables in Digital Ocean console
DEPLOYMENT_PLATFORM=digitalocean
DATABASE_URL=${merlin-postgres-prod.DATABASE_URL}
WEBHOOK_API_KEY=<generated-key>
SESSION_SECRET=<generated-secret>
FLASK_ENV=production
FLASK_DEBUG=False

# 2. Deploy app

# 3. Verify health
curl https://your-app.ondigitalocean.app/health

# 4. Access dashboard
open https://your-app.ondigitalocean.app/dashboard
```

---

## Troubleshooting

### Issue: "Authentication required" error
**Solution:** Login with dashboard password

### Issue: Database connection fails
**Solution:** Check `DATABASE_URL` or `PGPASSWORD` is set correctly

### Issue: Dashboard loads but no data
**Solution:** Verify `/api/v2/dashboard/overview` endpoint works

### Issue: SSE connection fails
**Solution:** Check `/api/stream/dashboard` is accessible (CORS, firewall)

### Issue: "Weak secrets" warning
**Solution:** Run `python utils/security_key_generator.py` and set keys

---

## File Locations

| Component | Path |
|-----------|------|
| Main App | `app_modular.py` |
| Dashboard V2 Template | `frontend_templates/dashboard_v2.html` |
| Dashboard API | `modules/dashboard_api.py` |
| Dashboard API V2 | `modules/dashboard_api_v2.py` |
| SSE Streaming | `modules/realtime/sse_dashboard.py` |
| Database Config | `modules/database/database_config.py` |
| Security Tools | `utils/security_key_generator.py` |

---

## Testing

### Run Integration Tests
```bash
pytest tests/test_dashboard_integration.py -v
```

### Run End-to-End Tests
```bash
pytest tests/test_end_to_end_workflow.py -v
```

### Run Standalone Demo
```bash
python scripts/dashboard_standalone.py
# Password: demo
# URL: http://localhost:5001/dashboard
```

---

## Monitoring

### Health Check
```bash
curl http://localhost:5000/health
```

### Expected Response
```json
{
  "status": "healthy",
  "service": "Merlin Job Application System",
  "version": "4.5.1",
  "database": "connected",
  "timestamp": "2025-10-22T..."
}
```

---

## Support Documentation

- **Full Verification Report:** `PRODUCTION_DASHBOARD_VERIFICATION_REPORT.md`
- **Deployment Guide:** `docs/deployment/DEPLOYMENT_GUIDE.md`
- **Database Connection Guide:** `docs/database-connection-guide.md`
- **Quick Start Guide:** `QUICKSTART.md`

---

## Contact Information

For issues or questions:
1. Check verification report for detailed status
2. Review troubleshooting section above
3. Check application logs: `LOG_LEVEL=DEBUG python app_modular.py`
