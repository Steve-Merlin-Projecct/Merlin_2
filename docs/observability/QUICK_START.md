# Observability Quick Start Guide

## 5-Minute Setup

### Step 1: Configure Environment (Optional)

Add to `.env` file:

```bash
LOG_LEVEL=INFO          # DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FORMAT=human        # 'human' for dev, 'json' for production
LOG_FILE=               # Optional: /var/log/app.log
```

### Step 2: Update Your Module

Replace old logging:

```python
# ❌ OLD
import logging
logger = logging.getLogger(__name__)

# ✅ NEW
from modules.observability import get_logger
logger = get_logger(__name__)
```

That's it! You now have:
- ✅ Automatic request correlation
- ✅ Structured logging
- ✅ Performance tracking
- ✅ Context propagation

## Common Usage Patterns

### Basic Logging

```python
from modules.observability import get_logger

logger = get_logger(__name__)

logger.debug("Detailed diagnostic info")
logger.info("General information")
logger.warning("Warning message")
logger.error("Error occurred", exc_info=True)
logger.critical("Critical system error")
```

### Add Context to Logs

```python
logger.info(
    "Job scraping completed",
    extra={
        'job_count': 150,
        'source': 'indeed',
        'duration_ms': 1234
    }
)
```

### Track Performance

```python
from modules.observability import track_performance

@track_performance('job_analysis')
def analyze_job(job_id):
    # Your code here
    pass
```

### Record Custom Metrics

```python
from app_modular import metrics_collector

metrics_collector.record_custom_metric(
    'jobs_scraped',
    150,
    labels={'source': 'indeed'}
)
```

### Time Code Blocks

```python
from modules.observability import PerformanceTimer

with PerformanceTimer('database_query', logger):
    results = db.query(Job).all()
```

## Monitoring Endpoints

### Health Check

```bash
curl http://localhost:5001/health
```

### View Metrics

```bash
curl http://localhost:5001/metrics
```

## Request Tracing

Every request automatically includes:
- Unique correlation ID
- Performance metrics
- Error tracking

Access the context:

```python
from modules.observability import get_request_context

context = get_request_context()
print(f"Correlation ID: {context.correlation_id}")
```

## Debugging

### Trace a Request

```python
from modules.observability.debug_tools import LogAnalyzer

analyzer = LogAnalyzer()
analyzer.parse_json_log('app.log')

# Trace specific request
trace = analyzer.trace_request('correlation-id-here')
print(trace)
```

### Find Slow Operations

```python
slow_ops = analyzer.get_performance_issues(threshold_ms=1000)
for op in slow_ops:
    print(f"{op['operation']} took {op['duration_ms']}ms")
```

### Get Error Summary

```python
summary = analyzer.get_error_summary()
print(f"Total errors: {summary['total_errors']}")
```

## Log Output Examples

### Development (Human-Readable)

```
INFO     2025-10-10 15:30:45.123 [modules.scraping] Scraped 150 jobs | correlation_id=abc-123
```

### Production (JSON)

```json
{
  "timestamp": "2025-10-10T15:30:45.123Z",
  "level": "INFO",
  "logger": "modules.scraping",
  "message": "Scraped 150 jobs",
  "request": {
    "correlation_id": "abc-123",
    "method": "POST",
    "path": "/api/scrape"
  }
}
```

## Next Steps

- Read the [Complete Observability Guide](./OBSERVABILITY_GUIDE.md)
- Add custom health checks
- Set up log aggregation
- Configure alerting

## Need Help?

- Check `/health` endpoint for system status
- Check `/metrics` endpoint for performance data
- Review logs with correlation IDs
- Use debug tools for troubleshooting
