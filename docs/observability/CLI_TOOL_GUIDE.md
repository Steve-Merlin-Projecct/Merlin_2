# Production Monitor CLI Tool Guide

## Overview

The Production Monitor CLI tool (`monitor_production.py`) provides a command-line interface for querying and analyzing logs from both local development and remote production environments.

## Installation

No installation required. The tool is located at:

```
/workspace/tools/monitor_production.py
```

### Dependencies

The tool requires:
- Python 3.11+
- `requests` library (included in requirements.txt)

## Quick Start

### 1. Set API Key

```bash
export MONITORING_API_KEY=your-secret-key
```

Or use the API key from your `.env` file (WEBHOOK_API_KEY).

### 2. Basic Commands

```bash
# Query recent errors
python tools/monitor_production.py logs --level ERROR --limit 50

# Search logs
python tools/monitor_production.py logs --search "database error"

# Check system health
python tools/monitor_production.py health

# View performance metrics
python tools/monitor_production.py metrics
```

## Commands Reference

### logs - Query Application Logs

Query and filter application logs.

**Syntax:**
```bash
python tools/monitor_production.py logs [OPTIONS]
```

**Options:**

| Option | Description | Example |
|--------|-------------|---------|
| `--level` | Filter by log level | `--level ERROR` |
| `--correlation-id` | Filter by correlation ID | `--correlation-id abc-123` |
| `--search` | Search message text | `--search "database"` |
| `--minutes` | Time window in minutes | `--minutes 60` |
| `--limit` | Maximum results | `--limit 100` |

**Examples:**

```bash
# Get last 50 errors
python tools/monitor_production.py logs --level ERROR --limit 50

# Search for database-related logs in last hour
python tools/monitor_production.py logs --search "database" --minutes 60

# Get all INFO logs from last 30 minutes
python tools/monitor_production.py logs --level INFO --minutes 30

# Find logs by correlation ID
python tools/monitor_production.py logs --correlation-id abc-123-def-456
```

**Output:**

```
Log Query Results
Total: 3 entries

ERROR    2025-10-22T15:30:45.123Z [modules.database.connection]
  Database connection failed
  Correlation ID: abc-123-def

ERROR    2025-10-22T15:31:12.456Z [modules.scraping.job_scraper]
  Failed to scrape jobs from Indeed
  Correlation ID: def-456-ghi

WARNING  2025-10-22T15:32:00.789Z [modules.ai_integration]
  API rate limit approaching
```

---

### errors - Query Error Logs

View error summaries and recent error logs.

**Syntax:**
```bash
python tools/monitor_production.py errors [OPTIONS]
```

**Options:**

| Option | Description | Example |
|--------|-------------|---------|
| `--minutes` | Time window (default: 60) | `--minutes 120` |
| `--limit` | Max error entries (default: 50) | `--limit 100` |

**Examples:**

```bash
# Get errors from last hour
python tools/monitor_production.py errors

# Get errors from last 2 hours
python tools/monitor_production.py errors --minutes 120

# Get last 100 error entries
python tools/monitor_production.py errors --limit 100
```

**Output:**

```
Error Summary
Total Errors: 5

By Type:
  DatabaseError: 3
  ValidationError: 2

Recent Errors:

ERROR 2025-10-22T15:30:45.123Z [modules.database.connection]
  Type: DatabaseError
  Database connection failed: Connection refused
```

---

### trace - Trace Request by Correlation ID

Trace a complete request flow through the system.

**Syntax:**
```bash
python tools/monitor_production.py trace <correlation-id>
```

**Examples:**

```bash
# Trace a specific request
python tools/monitor_production.py trace abc-123-def-456

# Trace a request from error logs
python tools/monitor_production.py errors --limit 1
# Copy correlation ID from output
python tools/monitor_production.py trace <copied-correlation-id>
```

**Output:**

```
Request Trace
Correlation ID: abc-123-def
Start Time: 2025-10-22T15:30:45.123Z
Total Duration: 1333.00ms

Timeline:

  0. INFO     Incoming request: POST /api/db/jobs
  1. INFO     Fetching jobs from database
     +111.00ms
  2. INFO     Processing 150 job records
     +234.56ms
  3. INFO     Applying filters and sorting
     +89.12ms
  4. INFO     Request completed: POST /api/db/jobs - 200
     +898.32ms
```

---

### health - System Health Check

Check system health and component status.

**Syntax:**
```bash
python tools/monitor_production.py health [OPTIONS]
```

**Options:**

| Option | Description |
|--------|-------------|
| `--simple` | Simple check without details |

**Examples:**

```bash
# Detailed health check
python tools/monitor_production.py health

# Simple health check
python tools/monitor_production.py health --simple
```

**Output:**

```
System Health
Overall Status: HEALTHY

Component Checks:

✓ application     Application is running
✓ logging        Log directory writable: ./logs
✓ database       Database configured: Local
```

---

### metrics - Performance Metrics

View performance metrics and request statistics.

**Syntax:**
```bash
python tools/monitor_production.py metrics [OPTIONS]
```

**Options:**

| Option | Description | Example |
|--------|-------------|---------|
| `--path` | Filter by path | `--path /api/db/jobs` |
| `--minutes` | Time window (default: 60) | `--minutes 30` |

**Examples:**

```bash
# Get all metrics from last hour
python tools/monitor_production.py metrics

# Get metrics for specific endpoint
python tools/monitor_production.py metrics --path /api/db/jobs

# Get metrics from last 30 minutes
python tools/monitor_production.py metrics --minutes 30
```

**Output:**

```
Performance Metrics

Request Metrics:

/api/db/jobs
  Requests: 150
  Avg Duration: 125.50ms
  Errors: 2

/api/scraping/scrape
  Requests: 45
  Avg Duration: 2345.67ms
  Errors: 1

Custom Metrics:

request_duration_ms: count=195, avg=456.78, max=3456.12

Errors: 3
```

---

## Global Options

These options apply to all commands:

| Option | Description | Example |
|--------|-------------|---------|
| `--host` | Server base URL | `--host https://prod.example.com` |
| `--api-key` | API key for auth | `--api-key your-secret-key` |

**Examples:**

```bash
# Query production server
python tools/monitor_production.py \
  --host https://production.example.com \
  --api-key prod-secret-key \
  logs --level ERROR

# Query staging server
python tools/monitor_production.py \
  --host https://staging.example.com \
  health
```

---

## Common Workflows

### 1. Investigating Production Errors

```bash
# Step 1: Check error summary
python tools/monitor_production.py --host https://prod.example.com errors

# Step 2: Get detailed error logs
python tools/monitor_production.py --host https://prod.example.com \
  logs --level ERROR --limit 10

# Step 3: Trace a specific failing request
python tools/monitor_production.py --host https://prod.example.com \
  trace <correlation-id-from-error>
```

### 2. Performance Investigation

```bash
# Step 1: Check overall metrics
python tools/monitor_production.py metrics

# Step 2: Identify slow endpoints
python tools/monitor_production.py metrics --path /api/db/jobs

# Step 3: Search for slow operations
python tools/monitor_production.py logs --search "completed in" --limit 50
```

### 3. Debugging Specific Issue

```bash
# Search for error messages
python tools/monitor_production.py logs --search "connection refused"

# Get context with time window
python tools/monitor_production.py logs \
  --search "connection refused" \
  --minutes 120

# Trace complete request flow
python tools/monitor_production.py trace <correlation-id>
```

### 4. Daily Health Check

```bash
#!/bin/bash
# daily_health_check.sh

echo "=== Daily Health Check ==="
echo ""

# Check system health
echo "System Health:"
python tools/monitor_production.py --host https://prod.example.com health --simple
echo ""

# Check error rate
echo "Error Summary (Last 24 hours):"
python tools/monitor_production.py --host https://prod.example.com \
  errors --minutes 1440
echo ""

# Check performance
echo "Performance Metrics:"
python tools/monitor_production.py --host https://prod.example.com \
  metrics --minutes 1440
```

---

## Environment Configuration

### Local Development

```bash
# .env file
MONITORING_API_KEY=local-dev-key
MONITORING_DEV_MODE=true
```

```bash
# Query local logs
python tools/monitor_production.py logs --level ERROR
```

### Production

```bash
# Set production credentials
export MONITORING_API_KEY=production-secret-key
export PROD_URL=https://production.example.com

# Query production logs
python tools/monitor_production.py --host $PROD_URL logs --level ERROR
```

### Multiple Environments

```bash
# Create aliases for different environments
alias monitor-local="python tools/monitor_production.py"
alias monitor-staging="python tools/monitor_production.py --host https://staging.example.com --api-key $STAGING_KEY"
alias monitor-prod="python tools/monitor_production.py --host https://production.example.com --api-key $PROD_KEY"

# Use aliases
monitor-local logs --level ERROR
monitor-staging health
monitor-prod errors --minutes 60
```

---

## Output Formatting

The CLI tool uses colored output for better readability:

- 🔴 **RED**: Errors and critical issues
- 🟡 **YELLOW**: Warnings and performance issues
- 🟢 **GREEN**: Info and successful operations
- 🔵 **CYAN**: Debug information and correlation IDs

### Redirecting Output

For scripting or saving output:

```bash
# Save to file (colors removed automatically)
python tools/monitor_production.py logs --level ERROR > errors.txt

# Pipe to other tools
python tools/monitor_production.py errors | grep "DatabaseError"

# JSON output (use API directly)
curl -s "http://localhost:5001/api/monitoring/logs?level=ERROR" \
  -H "X-Monitoring-Key: your-key" | jq '.logs'
```

---

## Troubleshooting

### Connection Refused

**Problem:** Can't connect to server

**Solution:**
```bash
# Check if server is running
curl http://localhost:5001/health

# Check firewall/network
ping production.example.com
```

### Unauthorized

**Problem:** API key rejected

**Solution:**
```bash
# Check API key
echo $MONITORING_API_KEY

# Set correct API key
export MONITORING_API_KEY=correct-key

# Or use dev mode locally
export MONITORING_DEV_MODE=true
```

### No Logs Found

**Problem:** Empty results

**Solution:**
```bash
# Check available log files
curl http://localhost:5001/api/monitoring/status | jq '.available_logs'

# Increase time window
python tools/monitor_production.py logs --minutes 1440  # Last 24 hours

# Check log directory
ls -la logs/
```

---

## Advanced Usage

### Custom Scripts

```python
#!/usr/bin/env python3
# custom_monitor.py

import sys
sys.path.insert(0, '/workspace/tools')
from monitor_production import ProductionMonitor

# Initialize monitor
monitor = ProductionMonitor(
    base_url='https://production.example.com',
    api_key='your-key'
)

# Query errors
errors = monitor.query_errors(minutes=60)
if errors.get('total_errors', 0) > 10:
    print("ALERT: High error rate!")

    # Get recent errors
    for error in errors['recent_errors'][:5]:
        print(f"  {error['timestamp']}: {error['message']}")
```

### Monitoring Script

```bash
#!/bin/bash
# monitor_health.sh

set -e

API_KEY="${MONITORING_API_KEY}"
HOST="${PROD_URL:-http://localhost:5001}"

# Check health
STATUS=$(python tools/monitor_production.py --host $HOST health --simple 2>&1 | grep "Overall Status")

if echo "$STATUS" | grep -q "UNHEALTHY"; then
    echo "ALERT: System is unhealthy!"

    # Get error details
    python tools/monitor_production.py --host $HOST errors --minutes 30

    # Send alert (example)
    # curl -X POST https://alerts.example.com/webhook \
    #   -d "System unhealthy: $STATUS"

    exit 1
fi

echo "System is healthy"
```

---

## Integration with Other Tools

### Cron Jobs

```cron
# Check health every 5 minutes
*/5 * * * * /workspace/tools/monitor_health.sh

# Daily error summary
0 9 * * * python /workspace/tools/monitor_production.py --host https://prod.example.com errors --minutes 1440 > /tmp/daily-errors.txt
```

### CI/CD Pipeline

```yaml
# .github/workflows/monitor.yml
name: Production Monitoring

on:
  schedule:
    - cron: '0 */6 * * *'  # Every 6 hours

jobs:
  monitor:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2

      - name: Check Production Health
        env:
          MONITORING_API_KEY: ${{ secrets.MONITORING_API_KEY }}
        run: |
          python tools/monitor_production.py \
            --host https://production.example.com \
            health

      - name: Check Error Rate
        run: |
          ERRORS=$(python tools/monitor_production.py \
            --host https://production.example.com \
            errors --minutes 360 | grep "Total Errors" | awk '{print $3}')

          if [ "$ERRORS" -gt 50 ]; then
            echo "High error rate: $ERRORS"
            exit 1
          fi
```

---

## Tips and Best Practices

1. **Use Correlation IDs**: Always trace issues using correlation IDs for complete context
2. **Time Windows**: Adjust time windows based on log volume (shorter for high traffic)
3. **Save Queries**: Create aliases or scripts for frequently used queries
4. **Automate Monitoring**: Set up cron jobs or CI/CD for regular health checks
5. **Export Data**: Use JSON output for integration with other tools

---

## See Also

- [Monitoring API Guide](MONITORING_API_GUIDE.md) - Complete API documentation
- [Observability Guide](OBSERVABILITY_GUIDE.md) - System observability overview
- [Quick Start](QUICK_START.md) - Getting started guide
