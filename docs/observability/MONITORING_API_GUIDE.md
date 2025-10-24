---
title: "Monitoring Api Guide"
type: api_spec
component: general
status: draft
tags: []
---

# Monitoring API Guide

## Overview

The Monitoring API provides REST endpoints for querying logs, metrics, and system health from both development and production environments. It enables real-time monitoring, debugging, and observability.

## Features

- **Log Querying**: Search and filter application logs with flexible criteria
- **Error Tracking**: Query error logs and view error summaries
- **Request Tracing**: Trace complete request flows using correlation IDs
- **Health Checks**: Comprehensive system health monitoring with disk space alerts
- **Metrics Collection**: Performance metrics and resource usage
- **PII Scrubbing**: Automatic redaction of sensitive data in logs
- **Rate Limiting**: Protection against API abuse (60 requests/minute per key)
- **Async Logging**: Non-blocking I/O for improved performance
- **Configuration Validation**: Startup validation for correct configuration
- **CLI Tool**: Command-line interface for production log analysis

## API Endpoints

### Base URL

```
http://localhost:5001/api/monitoring
```

### Authentication

All endpoints (except `/health` and `/status`) require authentication via API key:

**Header:**
```
X-Monitoring-Key: your-api-key
```

**Query Parameter:**
```
?api_key=your-api-key
```

**Environment Variables:**
```bash
# API key for authentication
MONITORING_API_KEY=your-secret-key

# Development mode (bypass auth)
MONITORING_DEV_MODE=true
```

---

## Endpoints Reference

### 1. Query Logs

```
GET /api/monitoring/logs
```

Query application logs with filters.

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `level` | string | Filter by log level (DEBUG, INFO, WARNING, ERROR, CRITICAL) |
| `correlation_id` | string | Filter by correlation ID |
| `start_time` | ISO datetime | Start timestamp |
| `end_time` | ISO datetime | End timestamp |
| `search` | string | Search message text |
| `limit` | integer | Maximum results (default: 100) |
| `log_file` | string | Log file path (default: ./logs/app.log) |

**Example Request:**

```bash
curl "http://localhost:5001/api/monitoring/logs?level=ERROR&limit=50" \
  -H "X-Monitoring-Key: your-api-key"
```

**Example Response:**

```json
{
  "success": true,
  "count": 3,
  "logs": [
    {
      "timestamp": "2025-10-22T15:30:45.123Z",
      "level": "ERROR",
      "logger": "modules.database.connection",
      "message": "Database connection failed",
      "correlation_id": "abc-123-def",
      "metadata": {
        "exception": {
          "type": "ConnectionError",
          "message": "Connection refused"
        }
      }
    }
  ],
  "filters": {
    "level": "ERROR",
    "limit": 50
  }
}
```

---

### 2. Health Check

```
GET /api/monitoring/health
```

Comprehensive system health check (no authentication required).

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `detailed` | boolean | Include detailed checks (default: true) |

**Example Request:**

```bash
curl "http://localhost:5001/api/monitoring/health"
```

**Example Response:**

```json
{
  "overall_status": "healthy",
  "service": "Merlin Job Application System",
  "version": "4.4.1",
  "checks": {
    "application": {
      "status": "healthy",
      "message": "Application is running"
    },
    "logging": {
      "status": "healthy",
      "message": "Log directory writable: ./logs"
    },
    "disk_space": {
      "status": "healthy",
      "message": "Disk space OK: 5432.1MB free of 10240.0MB (53.0%)"
    },
    "database": {
      "status": "healthy",
      "message": "Database configured: Local"
    }
  },
  "resources": {
    "cpu_percent": 15.2,
    "memory_percent": 45.8,
    "disk_percent": 62.3
  },
  "disk_usage": {
    "path": "./logs",
    "total_mb": 10240.0,
    "used_mb": 4807.9,
    "free_mb": 5432.1,
    "used_percent": 47.0,
    "free_percent": 53.0,
    "status": "ok"
  },
  "rate_limit": {
    "capacity": 60,
    "remaining": 58,
    "refill_rate_per_second": 1.0,
    "requests_per_minute": 60,
    "next_refill_in": 1.0
  },
  "timestamp": "2025-10-22T15:30:45.123Z"
}
```

**Disk Space Status Values:**
- `ok`: More than 100MB free
- `warning`: Less than 100MB but more than 50MB free
- `critical`: Less than 50MB free

---

### 3. Performance Metrics

```
GET /api/monitoring/metrics
```

Retrieve performance metrics and request statistics.

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `path` | string | Filter metrics for specific path |
| `minutes` | integer | Time window in minutes (default: 60) |

**Example Request:**

```bash
curl "http://localhost:5001/api/monitoring/metrics?path=/api/db/jobs&minutes=30" \
  -H "X-Monitoring-Key: your-api-key"
```

**Example Response:**

```json
{
  "success": true,
  "time_window_minutes": 30,
  "request_metrics": {
    "/api/db/jobs": {
      "total_requests": 150,
      "total_errors": 2,
      "avg_duration_ms": 125.5,
      "min_duration_ms": 45.2,
      "max_duration_ms": 450.8,
      "status_codes": {
        "200": 148,
        "500": 2
      },
      "methods": {
        "GET": 150
      }
    }
  },
  "custom_metrics": {
    "request_duration_ms": {
      "count": 150,
      "avg": 125.5,
      "min": 45.2,
      "max": 450.8,
      "sum": 18825.0
    }
  },
  "errors": {
    "total_errors": 2,
    "by_type": {
      "DatabaseError": 1,
      "ValidationError": 1
    },
    "by_path": {
      "/api/db/jobs": 2
    }
  }
}
```

---

### 4. Error Logs

```
GET /api/monitoring/errors
```

Query error logs and summaries.

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `minutes` | integer | Time window in minutes (default: 60) |
| `limit` | integer | Maximum error entries (default: 50) |
| `log_file` | string | Error log file path (default: ./logs/error.log) |

**Example Request:**

```bash
curl "http://localhost:5001/api/monitoring/errors?minutes=30&limit=100" \
  -H "X-Monitoring-Key: your-api-key"
```

**Example Response:**

```json
{
  "success": true,
  "time_window_minutes": 30,
  "total_errors": 5,
  "summary": {
    "total_errors": 5,
    "by_type": {
      "DatabaseError": {
        "count": 3,
        "example": "Connection pool exhausted"
      },
      "ValidationError": {
        "count": 2,
        "example": "Invalid email format"
      }
    }
  },
  "recent_errors": [
    {
      "timestamp": "2025-10-22T15:30:45.123Z",
      "logger": "modules.database.connection",
      "message": "Database connection failed",
      "correlation_id": "abc-123-def",
      "error_type": "DatabaseError",
      "error_message": "Connection refused"
    }
  ]
}
```

---

### 5. Request Trace

```
POST /api/monitoring/trace
```

Trace a specific request by correlation ID.

**Request Body:**

```json
{
  "correlation_id": "abc-123-def",
  "log_file": "./logs/app.log"  // optional
}
```

**Example Request:**

```bash
curl -X POST "http://localhost:5001/api/monitoring/trace" \
  -H "X-Monitoring-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{"correlation_id": "abc-123-def"}'
```

**Example Response:**

```json
{
  "success": true,
  "trace": {
    "correlation_id": "abc-123-def",
    "start_time": "2025-10-22T15:30:45.123Z",
    "end_time": "2025-10-22T15:30:46.456Z",
    "total_duration_ms": 1333.0,
    "total_events": 8,
    "timeline": [
      {
        "sequence": 0,
        "timestamp": "2025-10-22T15:30:45.123Z",
        "level": "INFO",
        "logger": "modules.observability.middleware",
        "message": "Incoming request: POST /api/db/jobs"
      },
      {
        "sequence": 1,
        "timestamp": "2025-10-22T15:30:45.234Z",
        "level": "INFO",
        "logger": "modules.database.crud",
        "message": "Fetching jobs from database",
        "elapsed_ms": 111.0
      }
    ]
  }
}
```

---

### 6. Monitoring Status

```
GET /api/monitoring/status
```

Get monitoring system status and configuration (no authentication required).

**Example Request:**

```bash
curl "http://localhost:5001/api/monitoring/status"
```

**Example Response:**

```json
{
  "service": "Monitoring API",
  "version": "1.0.0",
  "endpoints": {
    "logs": "/api/monitoring/logs - Query application logs",
    "health": "/api/monitoring/health - System health check",
    "metrics": "/api/monitoring/metrics - Performance metrics",
    "errors": "/api/monitoring/errors - Error logs and summaries",
    "trace": "/api/monitoring/trace - Trace request by correlation ID",
    "status": "/api/monitoring/status - This endpoint"
  },
  "authentication": {
    "dev_mode": true,
    "api_key_required": false
  },
  "available_logs": [
    "./logs/app.log",
    "./logs/error.log"
  ]
}
```

---

## CLI Tool Usage

The `monitor_production.py` CLI tool provides a convenient interface for querying production logs.

### Installation

The CLI tool is located at `/workspace/tools/monitor_production.py` and requires no additional installation.

### Basic Usage

```bash
# Set API key
export MONITORING_API_KEY=your-secret-key

# Query recent errors
python tools/monitor_production.py logs --level ERROR --limit 50

# Search for specific text
python tools/monitor_production.py logs --search "database" --minutes 60

# Trace a request
python tools/monitor_production.py trace abc-123-def

# Check health
python tools/monitor_production.py health

# View metrics
python tools/monitor_production.py metrics --path /api/db/jobs
```

### CLI Commands

#### 1. Query Logs

```bash
python tools/monitor_production.py logs [OPTIONS]
```

**Options:**
- `--level {DEBUG,INFO,WARNING,ERROR,CRITICAL}` - Filter by log level
- `--correlation-id ID` - Filter by correlation ID
- `--search TEXT` - Search message text
- `--minutes N` - Time window in minutes
- `--limit N` - Maximum results (default: 100)

**Examples:**

```bash
# Recent errors
python tools/monitor_production.py logs --level ERROR --limit 50

# Search with time window
python tools/monitor_production.py logs --search "database" --minutes 30

# Find all logs for a correlation ID
python tools/monitor_production.py logs --correlation-id abc-123-def
```

#### 2. Query Errors

```bash
python tools/monitor_production.py errors [OPTIONS]
```

**Options:**
- `--minutes N` - Time window in minutes (default: 60)
- `--limit N` - Maximum error entries (default: 50)

**Example:**

```bash
python tools/monitor_production.py errors --minutes 120 --limit 100
```

#### 3. Trace Request

```bash
python tools/monitor_production.py trace <correlation-id>
```

**Example:**

```bash
python tools/monitor_production.py trace abc-123-def-456
```

#### 4. Health Check

```bash
python tools/monitor_production.py health [OPTIONS]
```

**Options:**
- `--simple` - Simple health check without details

**Example:**

```bash
python tools/monitor_production.py health
```

#### 5. Performance Metrics

```bash
python tools/monitor_production.py metrics [OPTIONS]
```

**Options:**
- `--path PATH` - Filter by specific path
- `--minutes N` - Time window in minutes (default: 60)

**Example:**

```bash
python tools/monitor_production.py metrics --path /api/db/jobs --minutes 30
```

### Remote Production Server

To query a remote production server:

```bash
python tools/monitor_production.py \
  --host https://production.example.com \
  --api-key your-production-key \
  logs --level ERROR
```

---

## PII Scrubbing

The observability system automatically redacts Personally Identifiable Information (PII) and sensitive data from logs to maintain security and compliance.

### Supported PII Patterns

The PII scrubber automatically detects and redacts:

| Data Type | Example Input | Redacted Output |
|-----------|---------------|-----------------|
| Email addresses | user@example.com | u***@***.com |
| Phone numbers | 123-456-7890 | ***-***-**** |
| API keys | sk_1234567890abcdef | sk_**** |
| Bearer tokens | Bearer xyz123... | Bearer **** |
| Database passwords | postgres://user:pass@host | postgres://user:****@host |
| URL passwords | ?password=secret | ?password=**** |
| SSN | 123-45-6789 | ***-**-**** |
| Credit cards | 4111-1111-1111-1111 | ****-****-****-1111 |
| JWT tokens | eyJhb... (long token) | ****.***.**** |

### Sensitive Field Names

Fields with these names in their keys are automatically redacted to `****`:
- password, passwd, pwd
- secret, token, api_key, apikey
- access_token, refresh_token, auth_token
- bearer, oauth, authorization
- private_key, encryption_key, session_key
- ssn, social_security
- credit_card, card_number, cvv, pin

### Configuration

PII scrubbing is enabled by default. To customize:

```python
from modules.observability import configure_logging

configure_logging(
    level='INFO',
    format_type='json',
    enable_pii_scrubbing=True  # Enable PII scrubbing (default)
)
```

To use a custom scrubber:

```python
from modules.observability import PIIScrubber

# Custom configuration
scrubber = PIIScrubber(
    scrub_emails=True,
    scrub_phones=True,
    scrub_api_keys=True,
    scrub_passwords=True,
    scrub_ssn=False,  # Disable SSN scrubbing
    scrub_credit_cards=True,
    additional_sensitive_fields=['employee_id', 'salary']
)

# Use in code
data = {"email": "user@example.com", "salary": "100000"}
clean_data = scrubber.scrub_dict(data)
# Result: {"email": "u***@***.com", "salary": "****"}
```

---

## Rate Limiting

All monitoring API endpoints (except `/health` and `/status`) are protected by rate limiting to prevent abuse and ensure fair resource allocation.

### Default Limits

- **Rate**: 60 requests per minute per API key
- **Burst**: 60 requests (same as rate)
- **Key**: Based on API key or IP address if no key provided

### Rate Limit Headers

All responses include rate limit information in headers:

```
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1634567890
```

### Rate Limit Exceeded Response

When rate limit is exceeded, the API returns HTTP 429:

```json
{
  "error": "Rate limit exceeded",
  "message": "Too many requests. Please retry after 15 seconds.",
  "retry_after": 15,
  "limit": 60,
  "window": "1 minute"
}
```

**Response Headers:**
```
HTTP/1.1 429 Too Many Requests
Retry-After: 15
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1634567905
```

### Health Endpoint Rate Limiting

The `/health` endpoint uses IP-based rate limiting (no API key required) to allow public health checks while preventing abuse.

### Configuration

Rate limiting is automatically initialized at application startup. To customize:

```python
from modules.observability import init_rate_limiter

# Custom rate limits
limiter = init_rate_limiter(
    app,
    requests_per_minute=120,  # Increase to 120 requests/minute
    burst_size=150           # Allow burst of 150 requests
)
```

To check current rate limit status:

```bash
curl "http://localhost:5001/api/monitoring/health" \
  -H "X-Monitoring-Key: your-api-key"
```

The response includes a `rate_limit` section showing your current usage.

---

## Async Logging

The observability system uses asynchronous logging with QueueHandler to prevent I/O operations from blocking request processing.

### How It Works

1. **QueueHandler**: Log records are placed in an in-memory queue (max 10,000 items)
2. **Background Thread**: A QueueListener runs in a separate thread to process the queue
3. **File I/O**: All file operations happen in the background thread
4. **Non-Blocking**: Request handlers never wait for log writes

### Benefits

- **Performance**: No blocking I/O in request handlers
- **Throughput**: Higher request throughput under load
- **Reliability**: Queue prevents log loss during brief I/O delays
- **Safety**: Queue size limit prevents memory exhaustion

### Configuration

Async logging is enabled by default:

```python
from modules.observability import configure_logging

configure_logging(
    level='INFO',
    format_type='json',
    enable_async_logging=True,  # Enable async logging (default)
    queue_size=10000            # Max queue size (default: 10000)
)
```

### Graceful Shutdown

The system automatically flushes all pending logs on shutdown:

```python
from modules.observability import shutdown_logging

# Manually flush and shutdown (usually automatic)
shutdown_logging()
```

The shutdown handler is automatically registered with `atexit` and will run when:
- Application exits normally
- SIGTERM/SIGINT received
- Python interpreter shuts down

---

## Configuration Validation

The observability system validates configuration at startup to catch errors early and provide clear error messages.

### Validation Checks

At startup, the system validates:

1. **LOG_LEVEL**: Must be DEBUG, INFO, WARNING, ERROR, or CRITICAL
2. **LOG_FORMAT**: Must be 'json' or 'human'
3. **Log Directory**: Must exist and be writable (created if missing)
4. **Disk Space**: Must have at least 100MB free in log directory
5. **API Key**: MONITORING_API_KEY or WEBHOOK_API_KEY should be set
6. **Rotation Settings**: Max file size and backup count must be reasonable

### Validation Errors

If validation fails, the application exits immediately with a clear error message:

```
Configuration validation failed: Invalid LOG_LEVEL: 'INVALID'. Must be one of: CRITICAL, DEBUG, ERROR, INFO, WARNING
```

### Warnings

Non-critical issues generate warnings but don't stop startup:

```
Configuration warning: Low disk space in './logs': 75.5MB free (15.2%)
```

### Manual Validation

You can manually validate configuration:

```python
from modules.observability import validate_configuration, ConfigurationError

try:
    results = validate_configuration(
        require_api_key=True,
        check_disk_space=True
    )
    print(f"Configuration valid: {results}")
except ConfigurationError as e:
    print(f"Configuration error: {e}")
```

### Environment Variables

The validator checks these environment variables:

```bash
# Required for operation
LOG_LEVEL=INFO                    # Log level (default: INFO)
LOG_FORMAT=json                   # Format type (default: human)

# Optional configuration
LOG_DIR=/var/log/merlin          # Log directory (default: ./logs)
LOG_MAX_BYTES=10485760           # Max file size (default: 10MB)
LOG_BACKUP_COUNT=5               # Backup files (default: 5)

# API authentication
MONITORING_API_KEY=secret-key     # API key for monitoring endpoints
WEBHOOK_API_KEY=secret-key        # Alternative API key
MONITORING_DEV_MODE=false         # Bypass auth in dev (default: false)
```

---

## Configuration

### Environment Variables

```bash
# Logging configuration
LOG_LEVEL=INFO                    # Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
LOG_FORMAT=json                   # Output format (human/json)
LOG_DIR=/var/log/merlin          # Log directory

# Monitoring API
MONITORING_API_KEY=secret-key     # API key for authentication
MONITORING_DEV_MODE=false         # Development mode (bypass auth)

# File rotation
LOG_MAX_BYTES=10485760           # Max log file size (10MB default)
LOG_BACKUP_COUNT=5               # Number of backup files (5 default)

# Advanced features
ENABLE_ASYNC_LOGGING=true        # Use async logging (true default)
ENABLE_PII_SCRUBBING=true        # Enable PII scrubbing (true default)
QUEUE_SIZE=10000                 # Async queue size (10000 default)
```

### Production Setup

For production deployment on Digital Ocean:

1. **Set environment variables:**

```bash
export LOG_LEVEL=INFO
export LOG_FORMAT=json
export LOG_DIR=/var/log/merlin
export MONITORING_API_KEY=your-secure-key
export MONITORING_DEV_MODE=false
```

2. **Create log directory:**

```bash
sudo mkdir -p /var/log/merlin
sudo chown -R appuser:appuser /var/log/merlin
```

3. **Configure log rotation:**

The application automatically rotates logs when they reach 10MB (configurable).
Manual logrotate configuration (optional):

```
/var/log/merlin/*.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    create 0644 appuser appuser
    sharedscripts
    postrotate
        systemctl reload merlin-app
    endscript
}
```

---

## Integration Examples

### Python Integration

```python
import requests

# Query logs
response = requests.get(
    'http://localhost:5001/api/monitoring/logs',
    headers={'X-Monitoring-Key': 'your-api-key'},
    params={'level': 'ERROR', 'limit': 50}
)
logs = response.json()

# Trace request
response = requests.post(
    'http://localhost:5001/api/monitoring/trace',
    headers={'X-Monitoring-Key': 'your-api-key'},
    json={'correlation_id': 'abc-123-def'}
)
trace = response.json()
```

### JavaScript Integration

```javascript
// Query logs
fetch('http://localhost:5001/api/monitoring/logs?level=ERROR&limit=50', {
  headers: {
    'X-Monitoring-Key': 'your-api-key'
  }
})
.then(response => response.json())
.then(data => console.log(data));

// Check health
fetch('http://localhost:5001/api/monitoring/health')
  .then(response => response.json())
  .then(data => console.log(data.overall_status));
```

### Shell Script Integration

```bash
#!/bin/bash

API_KEY="your-api-key"
BASE_URL="http://localhost:5001"

# Query recent errors
curl -s "${BASE_URL}/api/monitoring/errors?minutes=60" \
  -H "X-Monitoring-Key: ${API_KEY}" | jq '.total_errors'

# Check if healthy
STATUS=$(curl -s "${BASE_URL}/api/monitoring/health" | jq -r '.overall_status')
if [ "$STATUS" != "healthy" ]; then
  echo "System unhealthy!"
  exit 1
fi
```

---

## Troubleshooting

### Common Issues

#### 1. "Log file not found"

**Problem:** Log files haven't been created yet.

**Solution:**
```bash
# Create log directory
mkdir -p logs

# Start application to generate logs
python app_modular.py
```

#### 2. "Unauthorized"

**Problem:** API key not set or incorrect.

**Solution:**
```bash
# Set API key
export MONITORING_API_KEY=your-secret-key

# Or use development mode
export MONITORING_DEV_MODE=true
```

#### 3. "No logs found for correlation_id"

**Problem:** Correlation ID doesn't exist or logs have been rotated.

**Solution:**
- Verify correlation ID is correct
- Check if logs have been rotated out (check backup files)
- Search in older log files: `./logs/app.log.1`, `./logs/app.log.2`, etc.

### Debugging

Enable debug logging for monitoring API:

```python
import logging
logging.getLogger('modules.observability.monitoring_api').setLevel(logging.DEBUG)
```

---

## Security Considerations

1. **API Key Protection:**
   - Never commit API keys to version control
   - Use strong, randomly generated keys
   - Rotate keys regularly
   - Use different keys for dev/staging/production

2. **Log Sanitization:**
   - PII scrubbing is enabled by default
   - Automatically redacts emails, phones, API keys, passwords, etc.
   - Restrict access to monitoring endpoints
   - Use HTTPS in production
   - Review and customize scrubbing patterns for your data

3. **Rate Limiting:**
   - Rate limiting is automatically applied (60 requests/minute)
   - Monitor for suspicious access patterns
   - Set up alerts for repeated failures
   - Customize limits based on your needs

4. **PII Protection:**
   - PII scrubbing is automatically enabled
   - Review scrubbed patterns match your data
   - Add custom sensitive field names if needed
   - Test that sensitive data is properly redacted

---

## Performance Considerations

1. **Log File Size:**
   - Monitor log file growth
   - Adjust rotation settings as needed
   - Consider archiving old logs to cold storage

2. **Query Performance:**
   - Large log files may slow down queries
   - Use time filters to limit search scope
   - Consider log aggregation tools for production

3. **Metrics Retention:**
   - Default retention: 24 hours
   - Adjust based on monitoring needs
   - Export metrics to external systems for long-term storage

---

## Best Practices

1. **Correlation IDs:**
   - Always include correlation IDs in requests
   - Use correlation IDs to trace issues
   - Pass correlation IDs between services

2. **Log Levels:**
   - Use appropriate log levels
   - ERROR: Application errors requiring attention
   - WARNING: Potential issues
   - INFO: Important business events
   - DEBUG: Detailed debugging information

3. **Monitoring:**
   - Set up health check alerts
   - Monitor error rates
   - Track performance metrics
   - Review logs regularly

4. **Production:**
   - Always use JSON format in production
   - Enable file rotation
   - Set up external log aggregation
   - Monitor disk space (automatic alerts at < 100MB)
   - Enable async logging for better performance
   - Enable PII scrubbing for compliance
   - Set strong API keys for monitoring endpoints

5. **Testing:**
   - Run tests with: `pytest tests/test_observability.py`
   - Verify PII scrubbing is working correctly
   - Test rate limiting under load
   - Validate configuration before deployment

---

## Additional Resources

- [Observability Guide](OBSERVABILITY_GUIDE.md) - Comprehensive observability documentation
- [Quick Start](QUICK_START.md) - Quick setup guide
- [Flask Documentation](https://flask.palletsprojects.com/) - Flask framework docs
- [Python Logging](https://docs.python.org/3/library/logging.html) - Python logging docs
