---
title: "Observability Guide"
type: guide
component: general
status: draft
tags: []
---

# Centralized Logging and Observability Guide

## Overview

The Merlin Job Application System includes a comprehensive centralized logging and observability system that provides:

- **Structured Logging**: Consistent JSON or human-readable log formats
- **Request Tracing**: Correlation IDs for tracking requests across services
- **Performance Metrics**: Automatic collection of request/response metrics
- **Debug Tools**: Log analysis, health checks, and diagnostic utilities

## Architecture

The observability system is located in `modules/observability/` and consists of:

```
modules/observability/
├── __init__.py           # Module exports
├── logging_config.py     # Logging configuration and formatters
├── context.py            # Request context and correlation tracking
├── middleware.py         # Flask middleware for automatic tracing
├── metrics.py            # Metrics collection and performance tracking
└── debug_tools.py        # Debugging and diagnostic utilities
```

## Quick Start

### 1. Basic Logger Usage

Replace existing logging imports with the centralized logger:

```python
# OLD
import logging
logger = logging.getLogger(__name__)

# NEW
from modules.observability import get_logger
logger = get_logger(__name__)
```

The logger automatically includes:
- Request correlation IDs
- Structured context
- Consistent formatting
- Performance data

### 2. Configuration

Configure logging via environment variables in `.env`:

```bash
# Log level: DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_LEVEL=INFO

# Format: 'human' for development, 'json' for production
LOG_FORMAT=human

# Optional: Log to file
LOG_FILE=/var/log/merlin/app.log
```

### 3. Application Integration

The observability system is automatically initialized in `app_modular.py`:

```python
from modules.observability import (
    configure_logging,
    get_logger,
    ObservabilityMiddleware,
    MetricsCollector
)

# Configure logging
configure_logging(
    level=os.environ.get('LOG_LEVEL', 'INFO'),
    format_type=os.environ.get('LOG_FORMAT', 'human'),
    log_file=os.environ.get('LOG_FILE'),
    enable_console=True
)

# Initialize middleware
metrics_collector = MetricsCollector(retention_hours=24)
ObservabilityMiddleware(app, metrics_collector=metrics_collector)
```

## Features

### Structured Logging

#### Human-Readable Format (Development)

```
INFO     2025-10-10 15:30:45.123 [modules.scraping.job_scraper] Scraping jobs from Indeed | correlation_id=abc-123 path=/api/scrape
```

#### JSON Format (Production)

```json
{
  "timestamp": "2025-10-10T15:30:45.123Z",
  "level": "INFO",
  "logger": "modules.scraping.job_scraper",
  "message": "Scraping jobs from Indeed",
  "source": {
    "file": "/app/modules/scraping/job_scraper.py",
    "line": 45,
    "function": "scrape_jobs"
  },
  "request": {
    "correlation_id": "abc-123",
    "method": "POST",
    "path": "/api/scrape",
    "user_id": "user_123",
    "ip_address": "192.168.1.1"
  }
}
```

### Request Tracing

Every request automatically gets:
- Unique correlation ID
- Request/response logging
- Performance tracking
- Error tracking

#### Correlation ID Flow

1. Client sends request (optionally with `X-Correlation-ID` header)
2. System generates correlation ID if not provided
3. All logs for that request include the correlation ID
4. Response includes `X-Correlation-ID` header

```python
# Correlation ID is automatically available in logs
logger.info("Processing job application")
# Output includes: correlation_id=abc-123

# Manually access context
from modules.observability import get_request_context
context = get_request_context()
print(f"Correlation ID: {context.correlation_id}")
```

### Performance Metrics

#### Automatic Request Metrics

The middleware automatically collects:
- Request count by endpoint
- Response time (min/max/avg)
- Status code distribution
- Error rates

#### Custom Metrics

```python
from modules.observability import MetricsCollector

# Get the global metrics collector (already initialized in app)
from app_modular import metrics_collector

# Record custom metrics
metrics_collector.record_custom_metric(
    'jobs_scraped',
    150,
    labels={'source': 'indeed', 'region': 'us'}
)

metrics_collector.record_custom_metric(
    'ai_tokens_used',
    5000,
    labels={'model': 'gemini', 'operation': 'job_analysis'}
)
```

#### Performance Decorators

```python
from modules.observability import track_performance

@track_performance('job_scraping_operation')
def scrape_jobs():
    # Function implementation
    pass
```

#### Performance Context Manager

```python
from modules.observability import PerformanceTimer

with PerformanceTimer('database_query', logger) as timer:
    # Database operations
    results = db.session.query(Job).all()

print(f"Query took {timer.duration_ms}ms")
```

### Debugging Tools

#### Log Analysis

```python
from modules.observability.debug_tools import LogAnalyzer

# Parse log file
analyzer = LogAnalyzer()
analyzer.parse_json_log('/var/log/merlin/app.log')

# Filter by level
errors = analyzer.filter_by_level('ERROR')

# Trace a specific request
trace = analyzer.trace_request('abc-123')
print(trace)

# Find slow operations
slow_ops = analyzer.get_performance_issues(threshold_ms=1000)

# Get error summary
summary = analyzer.get_error_summary()
```

#### Health Checks

```python
from modules.observability.debug_tools import HealthChecker

health = HealthChecker()

# Register custom health check
def check_database():
    try:
        db.session.execute('SELECT 1')
        return True, "Database is healthy"
    except Exception as e:
        return False, f"Database error: {str(e)}"

health.register_check('database', check_database)

# Run all checks
results = health.run_checks()
```

#### Debug Context

```python
from modules.observability.debug_tools import DebugContext

# Temporarily enable debug logging for a module
with DebugContext('modules.scraping'):
    # All logs from modules.scraping will be at DEBUG level
    scrape_jobs()
```

## Monitoring Endpoints

### Health Check: `/health`

```bash
curl http://localhost:5001/health
```

Response:
```json
{
  "overall_status": "healthy",
  "service": "Merlin Job Application System",
  "version": "4.3.1",
  "checks": {
    "application": {
      "status": "healthy",
      "message": "Application is running"
    },
    "database": {
      "status": "healthy",
      "message": "Database configured: Local"
    }
  },
  "timestamp": "2025-10-10T15:30:45.123Z"
}
```

### Metrics: `/metrics`

```bash
curl http://localhost:5001/metrics
```

Response:
```json
{
  "service": "Merlin Job Application System",
  "version": "4.3.1",
  "metrics": {
    "timestamp": "2025-10-10T15:30:45.123Z",
    "request_metrics": {
      "/api/scrape": {
        "total_requests": 150,
        "total_errors": 2,
        "avg_duration_ms": 234.5,
        "min_duration_ms": 120.0,
        "max_duration_ms": 890.0,
        "status_codes": {
          "200": 148,
          "500": 2
        },
        "methods": {
          "POST": 150
        }
      }
    },
    "custom_metrics": {
      "jobs_scraped": {
        "count": 10,
        "avg": 150.0,
        "sum": 1500
      }
    },
    "errors": {
      "total_errors": 2,
      "by_type": {
        "ConnectionError": 1,
        "TimeoutError": 1
      }
    }
  }
}
```

## Best Practices

### 1. Use the Centralized Logger

Always use `get_logger(__name__)` instead of `logging.getLogger()`:

```python
from modules.observability import get_logger
logger = get_logger(__name__)
```

### 2. Log at Appropriate Levels

- **DEBUG**: Detailed diagnostic information
- **INFO**: General informational messages
- **WARNING**: Warning messages (degraded functionality)
- **ERROR**: Error messages (functionality failed)
- **CRITICAL**: Critical errors (system failure)

```python
logger.debug("Detailed scraping parameters: %s", params)
logger.info("Successfully scraped 150 jobs from Indeed")
logger.warning("Rate limit approaching: 90% of quota used")
logger.error("Failed to connect to database", exc_info=True)
logger.critical("System out of memory - shutting down")
```

### 3. Include Context in Logs

```python
# Good - includes context
logger.info(
    "Job scraping completed",
    extra={
        'job_count': len(jobs),
        'source': 'indeed',
        'duration_ms': duration
    }
)

# Also good - using f-strings
logger.info(f"Scraped {len(jobs)} jobs from {source} in {duration}ms")
```

### 4. Use Performance Tracking

For any operation that might be slow:

```python
@track_performance('ai_job_analysis')
def analyze_job(job_description):
    # Analysis implementation
    pass
```

### 5. Record Custom Metrics

Track business-critical metrics:

```python
# Track application submissions
metrics_collector.record_custom_metric(
    'applications_sent',
    1,
    labels={'status': 'success', 'source': 'indeed'}
)

# Track AI usage
metrics_collector.record_custom_metric(
    'ai_api_calls',
    1,
    labels={'provider': 'gemini', 'operation': 'analysis'}
)
```

### 6. Handle Exceptions Properly

```python
try:
    scrape_jobs()
except Exception as e:
    logger.error(
        "Job scraping failed",
        exc_info=True,  # Includes full stack trace
        extra={
            'source': 'indeed',
            'error_type': type(e).__name__
        }
    )
    raise
```

## Production Deployment

### 1. Environment Configuration

Set production environment variables:

```bash
LOG_LEVEL=INFO
LOG_FORMAT=json
LOG_FILE=/var/log/merlin/app.log
```

### 2. Log Aggregation

JSON logs can be sent to:
- **ELK Stack** (Elasticsearch, Logstash, Kibana)
- **Splunk**
- **Datadog**
- **CloudWatch Logs** (AWS)
- **Stackdriver** (GCP)

### 3. Monitoring Integration

The `/metrics` endpoint can be scraped by:
- Prometheus
- Datadog
- New Relic
- Custom monitoring tools

### 4. Alerting

Set up alerts based on:
- Error rates: `metrics.errors.total_errors > threshold`
- Performance: `metrics.request_metrics[path].avg_duration_ms > threshold`
- Health checks: `health.overall_status == "unhealthy"`

## Troubleshooting

### Request Tracing

To trace a specific request through the system:

```python
from modules.observability.debug_tools import analyze_correlation_chain

# Analyze a request
analysis = analyze_correlation_chain(
    '/var/log/merlin/app.log',
    'correlation-id-here'
)

print(analysis)
```

### Finding Performance Issues

```python
from modules.observability.debug_tools import LogAnalyzer

analyzer = LogAnalyzer()
analyzer.parse_json_log('/var/log/merlin/app.log')

# Find operations slower than 1 second
slow_ops = analyzer.get_performance_issues(threshold_ms=1000)
for op in slow_ops:
    print(f"{op['operation']} took {op['duration_ms']}ms")
```

### Error Analysis

```python
# Get error summary from logs
summary = analyzer.get_error_summary()
print(f"Total errors: {summary['total_errors']}")
for error_type, data in summary['by_type'].items():
    print(f"{error_type}: {data['count']} occurrences")
    print(f"  Example: {data['example']}")
```

## Migration Guide

### Updating Existing Modules

1. Replace logging imports:
   ```python
   # OLD
   import logging
   logger = logging.getLogger(__name__)

   # NEW
   from modules.observability import get_logger
   logger = get_logger(__name__)
   ```

2. Add performance tracking to critical functions:
   ```python
   from modules.observability import track_performance

   @track_performance()
   def critical_function():
       pass
   ```

3. Record custom metrics for business operations:
   ```python
   from app_modular import metrics_collector

   metrics_collector.record_custom_metric('operation_name', value)
   ```

## Examples

### Complete Module Example

```python
"""
Job Scraping Module with Observability
"""

from modules.observability import get_logger, track_performance
from modules.observability.metrics import PerformanceTimer
from app_modular import metrics_collector

logger = get_logger(__name__)

@track_performance('job_scraping')
def scrape_jobs(source: str, limit: int = 100):
    """
    Scrape jobs from a source with full observability.
    """
    logger.info(
        f"Starting job scraping from {source}",
        extra={'source': source, 'limit': limit}
    )

    try:
        # Database query with timing
        with PerformanceTimer('database_fetch', logger):
            existing_jobs = fetch_existing_jobs()

        # API call with timing
        with PerformanceTimer('api_scrape', logger):
            new_jobs = call_scraping_api(source, limit)

        # Record metrics
        metrics_collector.record_custom_metric(
            'jobs_scraped',
            len(new_jobs),
            labels={'source': source}
        )

        logger.info(
            f"Successfully scraped {len(new_jobs)} jobs from {source}",
            extra={'job_count': len(new_jobs), 'source': source}
        )

        return new_jobs

    except Exception as e:
        logger.error(
            f"Job scraping failed for {source}",
            exc_info=True,
            extra={'source': source, 'error': str(e)}
        )

        metrics_collector.record_custom_metric(
            'scraping_errors',
            1,
            labels={'source': source, 'error_type': type(e).__name__}
        )

        raise
```

### Flask Route Example

```python
from flask import Blueprint, jsonify, request
from modules.observability import get_logger, get_request_context

logger = get_logger(__name__)
bp = Blueprint('jobs', __name__)

@bp.route('/api/jobs', methods=['POST'])
def create_job():
    """Create job with automatic request tracing."""
    # Context is automatically created by middleware
    context = get_request_context()

    logger.info(
        "Creating new job",
        extra={'correlation_id': context.correlation_id}
    )

    try:
        data = request.get_json()

        # Business logic
        job = create_job_record(data)

        logger.info(
            f"Job created successfully: {job.id}",
            extra={'job_id': job.id}
        )

        return jsonify({'id': job.id}), 201

    except Exception as e:
        logger.error(
            "Job creation failed",
            exc_info=True,
            extra={'error': str(e)}
        )
        return jsonify({'error': str(e)}), 500
```

## Summary

The centralized logging and observability system provides:

✅ **Automatic request tracing** with correlation IDs
✅ **Structured logging** in human or JSON format
✅ **Performance metrics** for all requests
✅ **Custom metrics** for business operations
✅ **Debug tools** for troubleshooting
✅ **Health checks** for monitoring
✅ **Production-ready** log aggregation support

Start using it by importing `get_logger(__name__)` in your modules!
