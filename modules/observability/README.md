# Observability Module

Centralized logging, tracing, and monitoring for the Merlin Job Application System.

## Quick Start

```python
from modules.observability import get_logger

logger = get_logger(__name__)
logger.info("Hello, observability!")
```

## Features

- 📊 **Structured Logging**: JSON or human-readable formats
- 🔍 **Request Tracing**: Automatic correlation IDs
- ⚡ **Performance Metrics**: Request timing and custom metrics
- 🐛 **Debug Tools**: Log analysis and health checks

## Module Structure

```
modules/observability/
├── __init__.py           # Public exports
├── logging_config.py     # Logging setup and formatters
├── context.py            # Request context and correlation
├── middleware.py         # Flask middleware integration
├── metrics.py            # Metrics collection
└── debug_tools.py        # Debugging utilities
```

## Usage

### Basic Logging

```python
from modules.observability import get_logger

logger = get_logger(__name__)

logger.debug("Debug message")
logger.info("Info message")
logger.warning("Warning message")
logger.error("Error message", exc_info=True)
```

### Performance Tracking

```python
from modules.observability import track_performance

@track_performance('operation_name')
def my_function():
    # Function code
    pass
```

### Custom Metrics

```python
from app_modular import metrics_collector

metrics_collector.record_custom_metric(
    'jobs_scraped',
    150,
    labels={'source': 'indeed'}
)
```

### Request Context

```python
from modules.observability import get_request_context

context = get_request_context()
print(f"Correlation ID: {context.correlation_id}")
```

## Configuration

Set via environment variables:

- `LOG_LEVEL`: DEBUG, INFO, WARNING, ERROR, CRITICAL
- `LOG_FORMAT`: 'human' or 'json'
- `LOG_FILE`: Optional file path

## Documentation

- [Comprehensive Guide](../../docs/observability/OBSERVABILITY_GUIDE.md)
- [Quick Start](../../docs/observability/QUICK_START.md)

## Monitoring Endpoints

- `/health` - Health check with diagnostics
- `/metrics` - Performance metrics and statistics

## Examples

### Flask Route with Tracing

```python
from flask import Blueprint
from modules.observability import get_logger

logger = get_logger(__name__)
bp = Blueprint('example', __name__)

@bp.route('/api/example')
def example():
    logger.info("Processing request")
    # Correlation ID automatically included in logs
    return {'status': 'success'}
```

### Performance Timer

```python
from modules.observability import PerformanceTimer

with PerformanceTimer('database_query', logger):
    results = db.query(Job).all()
```

### Log Analysis

```python
from modules.observability.debug_tools import LogAnalyzer

analyzer = LogAnalyzer()
analyzer.parse_json_log('app.log')

# Trace request
trace = analyzer.trace_request('correlation-id')

# Find slow operations
slow = analyzer.get_performance_issues(threshold_ms=1000)
```

## Integration

The observability system is automatically initialized in `app_modular.py`:

```python
from modules.observability import (
    configure_logging,
    ObservabilityMiddleware,
    MetricsCollector
)

# Configure logging
configure_logging(level='INFO', format_type='human')

# Initialize middleware
metrics_collector = MetricsCollector()
ObservabilityMiddleware(app, metrics_collector=metrics_collector)
```

## Dependencies

- `python-json-logger>=3.2.1` - JSON log formatting

## Best Practices

1. Always use `get_logger(__name__)` for consistent logging
2. Add context with `extra={}` parameter
3. Use `track_performance()` for critical functions
4. Record custom metrics for business operations
5. Include `exc_info=True` when logging errors
6. Use correlation IDs for request tracing

## Testing

```bash
# Install dependencies
pip install -r requirements.txt

# Run app and test endpoints
curl http://localhost:5001/health
curl http://localhost:5001/metrics
```
