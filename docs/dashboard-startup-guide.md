---
title: "Dashboard Startup Guide"
type: guide
component: general
status: draft
tags: []
---

# Dashboard Startup Guide

Version: 4.3.2
Last Updated: 2025-10-12

## Overview

This guide provides comprehensive instructions for starting the Flask dashboard application, including troubleshooting common issues and understanding the validation pipeline.

## Table of Contents

1. [Quick Start](#quick-start)
2. [Startup Scripts](#startup-scripts)
3. [Environment Requirements](#environment-requirements)
4. [Database Requirements](#database-requirements)
5. [Troubleshooting](#troubleshooting)
6. [Health Check Endpoint](#health-check-endpoint)
7. [Git Worktree Considerations](#git-worktree-considerations)

---

## Quick Start

### Standard Startup

```bash
# From project root
python scripts/start_dashboard.py
```

This will:
1. Validate environment variables
2. Check database connectivity
3. Verify port availability
4. Start Flask application on port 5001

### Check-Only Mode

Run validation without starting the application:

```bash
python scripts/start_dashboard.py --check-only
```

### Production Mode

Run with debug disabled and no reloader:

```bash
python scripts/start_dashboard.py --production
```

### Custom Port

```bash
python scripts/start_dashboard.py --port 8080
```

---

## Startup Scripts

### `scripts/start_dashboard.py`

**Smart application launcher** that runs a validation pipeline before starting Flask.

**Options:**
- `--check-only`: Run validation checks without starting the app
- `--skip-db-check`: Skip database connectivity check
- `--production`: Run in production mode (debug=False)
- `--port PORT`: Specify port (default: 5001)
- `--host HOST`: Specify host (default: 0.0.0.0)

**Examples:**
```bash
# Development mode with all checks
python scripts/start_dashboard.py

# Production mode on different port
python scripts/start_dashboard.py --production --port 8080

# Skip database check (useful if DB not ready yet)
python scripts/start_dashboard.py --skip-db-check

# Validation only (don't start app)
python scripts/start_dashboard.py --check-only
```

### `scripts/validate_environment.py`

**Environment validation script** that checks for required environment variables and files.

**Checks:**
- Required environment variables (PGPASSWORD, etc.)
- Optional environment variables with defaults
- Required files (app_modular.py, templates, etc.)
- Required directories (modules/, frontend_templates/, etc.)
- .env file accessibility (especially important in git worktrees)

**Usage:**
```bash
python scripts/validate_environment.py
```

**Exit codes:**
- 0: All validation checks passed
- 1: One or more validation checks failed

### `scripts/check_database.py`

**Database connectivity checker** that tests actual PostgreSQL connection.

**Checks:**
- Database configuration loading
- PostgreSQL connection
- Simple query execution (SELECT 1)
- PostgreSQL version retrieval

**Usage:**
```bash
python scripts/check_database.py
```

**Exit codes:**
- 0: Database connection successful
- 1: Database connection failed

### `scripts/setup_worktree_env.sh`

**Git worktree environment setup** that handles .env file accessibility in worktrees.

**What it does:**
- Detects if running in a git worktree
- Finds .env file in parent workspace
- Creates symlink to parent .env (recommended)
- Or copies .env to worktree (with warning comment)

**Usage:**
```bash
# Create symlink (recommended)
./scripts/setup_worktree_env.sh

# Copy file instead
./scripts/setup_worktree_env.sh --copy
```

---

## Environment Requirements

### Required Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `PGPASSWORD` | PostgreSQL database password | `your_secure_password` |

### Optional Environment Variables (with defaults)

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_NAME` | `local_Merlin_3` | PostgreSQL database name |
| `DATABASE_HOST` | `localhost` | Database host (auto-detected for Docker) |
| `DATABASE_PORT` | `5432` | Database port |
| `DATABASE_USER` | `postgres` | Database user |
| `LOG_LEVEL` | `INFO` | Logging level (DEBUG, INFO, WARNING, ERROR) |
| `LOG_FORMAT` | `human` | Log format (`human` or `json`) |

### Environment File (.env)

Create a `.env` file in the project root with your environment variables:

```bash
# Database Configuration
PGPASSWORD=your_database_password
DATABASE_NAME=local_Merlin_3

# Optional
LOG_LEVEL=INFO
LOG_FORMAT=human
```

**Important:** The `.env` file is gitignored and should never be committed to version control.

---

## Database Requirements

### PostgreSQL Installation

The dashboard requires a running PostgreSQL instance.

**Check if PostgreSQL is running:**
```bash
# SystemD (Ubuntu/Debian)
sudo systemctl status postgresql

# Init.d (older systems)
sudo service postgresql status

# macOS
brew services list | grep postgresql
```

**Start PostgreSQL if not running:**
```bash
# SystemD
sudo systemctl start postgresql

# Init.d
sudo service postgresql start

# macOS
brew services start postgresql
```

### Database Setup

1. **Create database:**
```bash
sudo -u postgres createdb local_Merlin_3
```

2. **Verify connection:**
```bash
psql -h localhost -U postgres -d local_Merlin_3
```

3. **Set password (if needed):**
```bash
sudo -u postgres psql -c "ALTER USER postgres PASSWORD 'your_password';"
```

### Connection Detection

The application automatically detects the environment:

- **Docker Container**: Uses `host.docker.internal` or container environment variables
- **Local Development**: Uses `localhost` with `.env` file settings

You can override with explicit `DATABASE_URL`:
```bash
DATABASE_URL=postgresql://user:password@host:port/database
```

---

## Troubleshooting

### Common Issues

#### 1. Dashboard Not Visible

**Symptom:** Can't access dashboard at http://localhost:5001

**Solutions:**
```bash
# Run validation checks
python scripts/start_dashboard.py --check-only

# Check if Flask is running
lsof -i :5001

# Check firewall rules
sudo ufw status
```

#### 2. Environment Variables Not Found

**Symptom:** `PGPASSWORD` not set error

**Solutions:**
```bash
# Check if .env file exists
ls -la .env

# For git worktrees, setup environment
./scripts/setup_worktree_env.sh

# Verify environment variables are loaded
python -c "import os; print(os.environ.get('PGPASSWORD'))"
```

#### 3. Database Connection Failed

**Symptom:** PostgreSQL connection refused

**Solutions:**
```bash
# Check PostgreSQL is running
sudo systemctl status postgresql

# Check connection parameters
python scripts/check_database.py

# Verify PostgreSQL is listening
sudo netstat -tulpn | grep 5432

# Check pg_hba.conf for authentication
sudo cat /etc/postgresql/*/main/pg_hba.conf
```

#### 4. Port Already in Use

**Symptom:** Port 5001 already in use

**Solutions:**
```bash
# Find process using port
lsof -i :5001

# Kill process (if safe)
kill -9 <PID>

# Or use different port
python scripts/start_dashboard.py --port 8080
```

#### 5. Template Files Not Found

**Symptom:** Template rendering errors

**Solutions:**
```bash
# Verify templates exist
ls frontend_templates/dashboard_v2.html
ls frontend_templates/dashboard_login.html

# Check from correct directory
pwd  # Should be project root

# Verify template folder in Flask config
python -c "from app_modular import app; print(app.template_folder)"
```

### Diagnostic Commands

Run these commands to diagnose issues:

```bash
# Full environment validation
python scripts/validate_environment.py

# Database connectivity check
python scripts/check_database.py

# Check with validation only
python scripts/start_dashboard.py --check-only

# Check PostgreSQL version
psql --version

# Check Python version
python --version

# List all environment variables
env | grep DATABASE
env | grep PGPASSWORD
```

---

## Health Check Endpoint

The application provides a comprehensive health check endpoint at `/health`.

### Accessing Health Check

```bash
# From command line
curl http://localhost:5001/health

# In browser
open http://localhost:5001/health
```

### Health Check Response

```json
{
  "service": "Merlin Job Application System",
  "version": "4.3.2",
  "overall_status": "healthy",
  "checks": {
    "application": {
      "status": "healthy",
      "message": "Application is running"
    },
    "database": {
      "status": "healthy",
      "message": "Database configured: Local - localhost:5432/local_Merlin_3 - Connection verified"
    },
    "environment": {
      "status": "healthy",
      "message": "Required environment variables present"
    },
    "templates": {
      "status": "healthy",
      "message": "All critical templates present (2 checked)"
    }
  },
  "timestamp": "2025-10-12T10:30:45.123456",
  "check_duration_ms": 45.67,
  "uptime_seconds": 123.45,
  "uptime_human": "2m 3s",
  "environment": {
    "python_version": "3.11.0",
    "flask_debug": true,
    "host": "localhost:5001"
  }
}
```

### Status Codes

- **200**: All health checks passed (healthy)
- **503**: One or more health checks failed (unhealthy)

### Using Health Checks for Monitoring

```bash
# Simple health check script
#!/bin/bash
response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5001/health)
if [ $response -eq 200 ]; then
    echo "Dashboard is healthy"
else
    echo "Dashboard is unhealthy (status: $response)"
fi
```

---

## Git Worktree Considerations

### What are Git Worktrees?

Git worktrees create separate working directories for different branches. The dashboard startup system handles this gracefully.

### Worktree Structure

```
/workspace/                      # Main workspace
├── .env                         # Environment file (here!)
└── .trees/                      # Worktrees directory
    └── dashboard-completion/    # This worktree
        ├── app_modular.py
        └── .env → ../../.env    # Symlink to parent
```

### Setting Up Environment in Worktrees

**Option 1: Automatic Setup (Recommended)**
```bash
./scripts/setup_worktree_env.sh
```

This creates a symlink from the worktree to the parent workspace .env file. All worktrees share the same environment configuration.

**Option 2: Copy Environment File**
```bash
./scripts/setup_worktree_env.sh --copy
```

This copies the .env file to the worktree. Changes here won't affect other worktrees.

### Should I Work on Dashboard in Main Branch?

**No, you don't need to!**

The startup system is designed to work seamlessly in both:
- **Main workspace** (`/workspace/`)
- **Git worktrees** (`/workspace/.trees/*/`)

**Best practices:**
1. Use worktrees for feature branches (you're already doing this!)
2. Run `./scripts/setup_worktree_env.sh` once per worktree
3. Use `python scripts/start_dashboard.py` from any branch
4. The system auto-detects and handles environment differences

**Benefits of using worktrees for dashboard work:**
- Isolate changes to feature branch
- Easy to switch contexts without losing work
- Can have multiple instances running (different ports)
- Clean separation of concerns

---

## Advanced Usage

### Running Multiple Instances

You can run multiple dashboard instances on different ports:

```bash
# Terminal 1: Development instance
python scripts/start_dashboard.py --port 5001

# Terminal 2: Testing instance
python scripts/start_dashboard.py --port 5002
```

### Production Deployment

For production environments:

```bash
# Use production mode
python scripts/start_dashboard.py --production --port 80

# Or use a production WSGI server (recommended)
gunicorn -w 4 -b 0.0.0.0:80 app_modular:app
```

### Docker Deployment

The application automatically detects Docker environments and adjusts database connection parameters.

```bash
# Docker Compose
docker-compose up

# Manual Docker run
docker run -p 5001:5001 \
  -e PGPASSWORD=your_password \
  -e DATABASE_HOST=host.docker.internal \
  your-image-name
```

---

## Integration with Development Workflow

### Pre-commit Hook

Consider adding a pre-commit hook to validate environment:

```bash
#!/bin/bash
# .git/hooks/pre-commit

python scripts/validate_environment.py --check-only
if [ $? -ne 0 ]; then
    echo "Environment validation failed. Commit aborted."
    exit 1
fi
```

### CI/CD Pipeline

```yaml
# Example GitHub Actions workflow
jobs:
  test:
    steps:
      - name: Validate Environment
        run: python scripts/validate_environment.py

      - name: Check Database
        run: python scripts/check_database.py

      - name: Health Check
        run: |
          python scripts/start_dashboard.py &
          sleep 5
          curl -f http://localhost:5001/health || exit 1
```

---

## Related Documentation

- [Architecture Overview](../docs/architecture/system-overview.md)
- [Database Configuration Guide](../docs/database-connection-guide.md)
- [Environment Setup](../docs/setup/)
- [API Documentation](../docs/api/)

---

## Support

If you encounter issues not covered in this guide:

1. Run full diagnostics: `python scripts/start_dashboard.py --check-only`
2. Check health endpoint: `curl http://localhost:5001/health`
3. Review application logs
4. Check PostgreSQL logs: `sudo tail -f /var/log/postgresql/*.log`

---

**Document Version:** 1.0.0
**Application Version:** 4.3.2
**Last Updated:** 2025-10-12
