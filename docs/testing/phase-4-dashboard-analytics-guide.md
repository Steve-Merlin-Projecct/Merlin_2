---
title: "Phase 4 Dashboard Analytics Guide"
type: guide
component: general
status: draft
tags: []
---

# Phase 4: Dashboard & Analytics Testing Guide
**Timeline:** Week 5 (3-4 working days)
**Goal:** Test user interfaces and analytics tracking systems

---

## Overview

Phase 4 focuses on testing the dashboard APIs that provide user interfaces and the analytics systems that track user engagement and system usage.

**Modules to Test:**
- `modules/dashboard_api.py` (125 lines, 0% coverage)
- `modules/dashboard_api_v2.py` (136 lines, 0% coverage)
- `modules/analytics/engagement_analytics.py` (118 lines, 0% coverage)
- `modules/analytics/engagement_analytics_api.py` (70 lines, 0% coverage)
- `modules/observability/metrics.py` (117 lines, 0% coverage)
- `modules/observability/logging_config.py` (64 lines, 0% coverage)

**Coverage Targets:**
- Dashboard APIs: 60% coverage (focus on critical paths)
- Analytics: 70% coverage
- Observability: 50% coverage (basic monitoring)

---

## Part A: Dashboard API Testing (2 days)

### 1. Dashboard API v1 Tests

**File:** `tests/unit/test_dashboard_api.py`

**What to Test:**

#### Endpoint Availability
```python
def test_dashboard_home_endpoint(client):
    """Test that dashboard home endpoint is accessible"""
    response = client.get('/dashboard')

    assert response.status_code == 200
    assert b'Dashboard' in response.data

def test_job_list_endpoint(client):
    """Test job listing endpoint"""
    response = client.get('/dashboard/jobs')

    assert response.status_code == 200
    assert response.content_type == 'application/json'

def test_application_status_endpoint(client):
    """Test application status endpoint"""
    response = client.get('/dashboard/applications')

    assert response.status_code == 200
    data = response.get_json()
    assert 'applications' in data
```

#### Data Retrieval
```python
def test_get_recent_jobs(client, test_db):
    """Test retrieving recent jobs"""
    # Add test jobs to database
    test_db.add_jobs([
        {"title": "Job 1", "company": "Company A", "created_at": "2025-10-10"},
        {"title": "Job 2", "company": "Company B", "created_at": "2025-10-11"},
        {"title": "Job 3", "company": "Company C", "created_at": "2025-10-12"}
    ])

    response = client.get('/dashboard/jobs/recent?limit=2')

    data = response.get_json()
    assert len(data['jobs']) == 2
    assert data['jobs'][0]['title'] == "Job 3"  # Most recent first

def test_get_application_statistics(client, test_db):
    """Test getting application statistics"""
    # Add test applications
    test_db.add_applications([
        {"status": "submitted", "job_id": 1},
        {"status": "submitted", "job_id": 2},
        {"status": "rejected", "job_id": 3},
        {"status": "interview", "job_id": 4}
    ])

    response = client.get('/dashboard/stats/applications')

    data = response.get_json()
    assert data['total'] == 4
    assert data['by_status']['submitted'] == 2
    assert data['by_status']['rejected'] == 1
    assert data['by_status']['interview'] == 1
```

#### Filtering and Search
```python
def test_filter_jobs_by_status(client, test_db):
    """Test filtering jobs by status"""
    response = client.get('/dashboard/jobs?status=open')

    data = response.get_json()
    assert all(job['status'] == 'open' for job in data['jobs'])

def test_search_jobs_by_title(client, test_db):
    """Test searching jobs by title"""
    response = client.get('/dashboard/jobs?search=Python Developer')

    data = response.get_json()
    assert all('python' in job['title'].lower() for job in data['jobs'])

def test_pagination(client, test_db):
    """Test pagination of results"""
    # Add many jobs
    test_db.add_jobs([{"title": f"Job {i}"} for i in range(50)])

    # Get first page
    response = client.get('/dashboard/jobs?page=1&per_page=10')
    data = response.get_json()

    assert len(data['jobs']) == 10
    assert data['page'] == 1
    assert data['total_pages'] == 5
    assert data['has_next'] is True
```

#### Error Handling
```python
def test_invalid_job_id_returns_404(client):
    """Test that invalid job ID returns 404"""
    response = client.get('/dashboard/jobs/999999')

    assert response.status_code == 404
    assert b'not found' in response.data.lower()

def test_missing_required_parameter(client):
    """Test handling of missing required parameters"""
    response = client.post('/dashboard/applications')  # Missing job_id

    assert response.status_code == 400
    data = response.get_json()
    assert 'error' in data
    assert 'job_id' in data['error'].lower()
```

**Key Assertions:**
- All endpoints return correct status codes
- Data is returned in expected format
- Filtering and search work correctly
- Pagination is implemented
- Errors are handled gracefully

---

### 2. Dashboard API v2 Tests

**File:** `tests/unit/test_dashboard_api_v2.py`

**What to Test:**

#### Enhanced Features
```python
def test_job_analytics_endpoint(client, test_db):
    """Test job analytics endpoint with aggregated data"""
    response = client.get('/api/v2/dashboard/analytics/jobs')

    data = response.get_json()
    assert 'total_jobs' in data
    assert 'jobs_by_status' in data
    assert 'jobs_by_company' in data
    assert 'match_score_distribution' in data

def test_application_timeline(client, test_db):
    """Test application timeline endpoint"""
    response = client.get('/api/v2/dashboard/applications/timeline')

    data = response.get_json()
    assert 'events' in data
    assert all('timestamp' in event for event in data['events'])
    assert all('event_type' in event for event in data['events'])

def test_success_rate_metrics(client, test_db):
    """Test success rate calculation"""
    # Add test applications with various outcomes
    test_db.add_applications([
        {"status": "offer", "job_id": 1},      # Success
        {"status": "offer", "job_id": 2},      # Success
        {"status": "interview", "job_id": 3},  # In progress
        {"status": "rejected", "job_id": 4},   # Failure
        {"status": "submitted", "job_id": 5}   # In progress
    ])

    response = client.get('/api/v2/dashboard/metrics/success_rate')

    data = response.get_json()
    assert data['offer_rate'] == 0.4  # 2 offers out of 5 total
    assert data['rejection_rate'] == 0.2  # 1 rejection out of 5 total
```

#### Real-time Updates
```python
def test_websocket_connection(ws_client):
    """Test WebSocket connection for real-time updates"""
    # Connect to WebSocket
    ws = ws_client.connect('/api/v2/dashboard/ws')

    # Trigger an event (e.g., new job posted)
    trigger_new_job_event(job_id=123)

    # Receive update via WebSocket
    message = ws.receive()
    data = json.loads(message)

    assert data['event'] == 'new_job'
    assert data['job_id'] == 123

def test_live_statistics_stream(ws_client):
    """Test live statistics streaming"""
    ws = ws_client.connect('/api/v2/dashboard/ws/stats')

    # Should receive periodic updates
    messages = []
    for _ in range(3):
        messages.append(json.loads(ws.receive()))

    assert len(messages) == 3
    assert all('timestamp' in msg for msg in messages)
```

#### Advanced Filtering
```python
def test_multi_criteria_filter(client, test_db):
    """Test filtering by multiple criteria"""
    response = client.get(
        '/api/v2/dashboard/jobs?'
        'status=open&'
        'min_salary=100000&'
        'location=remote&'
        'posted_within_days=7'
    )

    data = response.get_json()
    jobs = data['jobs']

    assert all(job['status'] == 'open' for job in jobs)
    assert all(job['salary_min'] >= 100000 for job in jobs)
    assert all('remote' in job['location'].lower() for job in jobs)

def test_date_range_filter(client, test_db):
    """Test filtering by date range"""
    response = client.get(
        '/api/v2/dashboard/applications?'
        'start_date=2025-10-01&'
        'end_date=2025-10-15'
    )

    data = response.get_json()
    applications = data['applications']

    assert all(
        '2025-10-01' <= app['created_at'][:10] <= '2025-10-15'
        for app in applications
    )
```

**Key Assertions:**
- Enhanced endpoints provide aggregated data
- Real-time updates work via WebSocket
- Advanced filtering is accurate
- Performance is acceptable (response time < 1s)

---

## Part B: Analytics Testing (1-2 days)

### 3. Engagement Analytics Tests

**File:** `tests/unit/test_engagement_analytics.py`

**What to Test:**

#### Event Tracking
```python
def test_track_job_view(analytics):
    """Test tracking job view event"""
    analytics.track_event(
        event_type='job_view',
        user_id='user_123',
        job_id=456,
        metadata={'source': 'dashboard'}
    )

    events = analytics.get_events(event_type='job_view', user_id='user_123')
    assert len(events) == 1
    assert events[0]['job_id'] == 456

def test_track_application_submission(analytics):
    """Test tracking application submission"""
    analytics.track_event(
        event_type='application_submit',
        user_id='user_123',
        job_id=456,
        metadata={'documents': ['resume', 'cover_letter']}
    )

    events = analytics.get_events(event_type='application_submit')
    assert len(events) == 1
    assert 'documents' in events[0]['metadata']

def test_track_document_generation(analytics):
    """Test tracking document generation"""
    analytics.track_event(
        event_type='document_generated',
        user_id='user_123',
        metadata={
            'document_type': 'resume',
            'template': 'professional',
            'generation_time_ms': 1250
        }
    )

    events = analytics.get_events(event_type='document_generated')
    assert events[0]['metadata']['generation_time_ms'] == 1250
```

#### Metrics Calculation
```python
def test_calculate_daily_active_users(analytics, test_db):
    """Test calculating daily active users"""
    # Add test events for different users
    analytics.track_event('job_view', user_id='user_1')
    analytics.track_event('job_view', user_id='user_2')
    analytics.track_event('job_view', user_id='user_1')  # Duplicate user

    dau = analytics.calculate_daily_active_users(date='2025-10-12')
    assert dau == 2  # Only unique users

def test_calculate_conversion_rate(analytics, test_db):
    """Test calculating conversion rate (views -> applications)"""
    # Track views
    for i in range(10):
        analytics.track_event('job_view', user_id=f'user_{i}', job_id=123)

    # Track applications (3 out of 10 viewers applied)
    for i in range(3):
        analytics.track_event('application_submit', user_id=f'user_{i}', job_id=123)

    conversion_rate = analytics.calculate_conversion_rate(
        from_event='job_view',
        to_event='application_submit',
        job_id=123
    )

    assert conversion_rate == 0.3  # 30%

def test_calculate_average_time_to_apply(analytics, test_db):
    """Test calculating average time from view to application"""
    import time

    # User views job
    analytics.track_event('job_view', user_id='user_1', job_id=123)

    # Wait and then apply (simulate)
    time.sleep(2)  # 2 seconds

    analytics.track_event('application_submit', user_id='user_1', job_id=123)

    avg_time = analytics.calculate_average_time_to_apply(job_id=123)

    assert 1.5 <= avg_time <= 2.5  # Around 2 seconds
```

#### Aggregation and Reporting
```python
def test_generate_daily_report(analytics, test_db):
    """Test generating daily analytics report"""
    # Add various events
    analytics.track_event('job_view', user_id='user_1')
    analytics.track_event('job_view', user_id='user_2')
    analytics.track_event('application_submit', user_id='user_1')

    report = analytics.generate_daily_report(date='2025-10-12')

    assert report['total_events'] == 3
    assert report['unique_users'] == 2
    assert report['applications'] == 1
    assert report['views'] == 2

def test_generate_funnel_analysis(analytics, test_db):
    """Test generating funnel analysis"""
    # Create complete funnel for some users
    for user_id in ['user_1', 'user_2']:
        analytics.track_event('job_view', user_id=user_id, job_id=123)
        analytics.track_event('application_submit', user_id=user_id, job_id=123)
        analytics.track_event('email_sent', user_id=user_id, job_id=123)

    # Only view for others
    for user_id in ['user_3', 'user_4', 'user_5']:
        analytics.track_event('job_view', user_id=user_id, job_id=123)

    funnel = analytics.generate_funnel_analysis(
        job_id=123,
        steps=['job_view', 'application_submit', 'email_sent']
    )

    assert funnel['job_view']['count'] == 5
    assert funnel['application_submit']['count'] == 2
    assert funnel['email_sent']['count'] == 2
    assert funnel['application_submit']['conversion_rate'] == 0.4  # 40%
```

**Key Assertions:**
- Events are tracked correctly
- Metrics calculations are accurate
- Time-based calculations work
- Reports aggregate data correctly

---

### 4. Analytics API Tests

**File:** `tests/unit/test_engagement_analytics_api.py`

**What to Test:**

#### API Endpoints
```python
def test_track_event_endpoint(client):
    """Test event tracking API endpoint"""
    response = client.post('/api/analytics/events', json={
        'event_type': 'job_view',
        'user_id': 'user_123',
        'job_id': 456,
        'metadata': {'source': 'email_link'}
    })

    assert response.status_code == 201
    data = response.get_json()
    assert 'event_id' in data

def test_get_metrics_endpoint(client):
    """Test metrics retrieval endpoint"""
    response = client.get('/api/analytics/metrics/dau?date=2025-10-12')

    assert response.status_code == 200
    data = response.get_json()
    assert 'daily_active_users' in data
    assert isinstance(data['daily_active_users'], int)

def test_get_report_endpoint(client):
    """Test report generation endpoint"""
    response = client.get(
        '/api/analytics/reports/daily?'
        'start_date=2025-10-01&'
        'end_date=2025-10-07'
    )

    assert response.status_code == 200
    data = response.get_json()
    assert 'reports' in data
    assert len(data['reports']) == 7  # 7 days
```

#### Authentication
```python
def test_analytics_endpoint_requires_auth(client):
    """Test that analytics endpoints require authentication"""
    response = client.get('/api/analytics/metrics/dau')  # No auth

    assert response.status_code == 401

def test_analytics_with_valid_token(client):
    """Test analytics access with valid token"""
    token = get_valid_analytics_token()

    response = client.get(
        '/api/analytics/metrics/dau',
        headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == 200
```

#### Rate Limiting
```python
def test_analytics_rate_limiting(client):
    """Test that analytics API has rate limiting"""
    token = get_valid_analytics_token()

    # Make many requests quickly
    responses = []
    for _ in range(150):  # Assume limit is 100/minute
        responses.append(client.get(
            '/api/analytics/metrics/dau',
            headers={'Authorization': f'Bearer {token}'}
        ))

    # Some should be rate limited
    rate_limited = [r for r in responses if r.status_code == 429]
    assert len(rate_limited) > 0
```

**Key Assertions:**
- API endpoints work correctly
- Authentication is enforced
- Rate limiting is applied
- Responses are properly formatted

---

## Part C: Observability Testing (1 day)

### 5. Metrics Tests

**File:** `tests/unit/test_observability_metrics.py`

**What to Test:**

#### Metric Recording
```python
def test_record_counter_metric():
    """Test recording counter metric"""
    metrics = MetricsCollector()

    metrics.increment('api.requests.total', labels={'endpoint': '/jobs'})
    metrics.increment('api.requests.total', labels={'endpoint': '/jobs'})
    metrics.increment('api.requests.total', labels={'endpoint': '/jobs'})

    value = metrics.get_counter('api.requests.total', labels={'endpoint': '/jobs'})
    assert value == 3

def test_record_gauge_metric():
    """Test recording gauge metric"""
    metrics = MetricsCollector()

    metrics.set_gauge('system.memory.usage', 1024 * 1024 * 512)  # 512 MB

    value = metrics.get_gauge('system.memory.usage')
    assert value == 1024 * 1024 * 512

def test_record_histogram_metric():
    """Test recording histogram metric"""
    metrics = MetricsCollector()

    # Record response times
    for time_ms in [100, 150, 200, 250, 300]:
        metrics.observe_histogram('api.response_time.ms', time_ms)

    stats = metrics.get_histogram_stats('api.response_time.ms')
    assert stats['count'] == 5
    assert stats['mean'] == 200
    assert 100 <= stats['p50'] <= 200  # Median
    assert 250 <= stats['p95'] <= 300  # 95th percentile
```

#### Metric Export
```python
def test_export_prometheus_format():
    """Test exporting metrics in Prometheus format"""
    metrics = MetricsCollector()

    metrics.increment('requests_total', labels={'method': 'GET'})
    metrics.set_gauge('memory_usage_bytes', 1024)

    prometheus_output = metrics.export_prometheus()

    assert 'requests_total{method="GET"} 1' in prometheus_output
    assert 'memory_usage_bytes 1024' in prometheus_output

def test_export_json_format():
    """Test exporting metrics in JSON format"""
    metrics = MetricsCollector()

    metrics.increment('api_calls', labels={'service': 'gemini'})

    json_output = metrics.export_json()
    data = json.loads(json_output)

    assert 'counters' in data
    assert any(m['name'] == 'api_calls' for m in data['counters'])
```

**Key Assertions:**
- Metrics are recorded correctly
- Different metric types work (counter, gauge, histogram)
- Export formats are correct
- Labels are preserved

---

### 6. Logging Configuration Tests

**File:** `tests/unit/test_logging_config.py`

**What to Test:**

#### Log Configuration
```python
def test_configure_logging():
    """Test that logging is configured correctly"""
    from modules.observability.logging_config import configure_logging

    configure_logging(level='INFO')

    logger = logging.getLogger('test_logger')
    assert logger.level == logging.INFO

def test_log_to_file(tmp_path):
    """Test logging to file"""
    log_file = tmp_path / "app.log"

    configure_logging(log_file=str(log_file))

    logger = logging.getLogger('test')
    logger.info("Test message")

    assert log_file.exists()
    assert "Test message" in log_file.read_text()

def test_structured_logging():
    """Test structured logging with JSON format"""
    configure_logging(format='json')

    logger = logging.getLogger('test')

    with captured_logs() as logs:
        logger.info("Test event", extra={'user_id': 123, 'action': 'login'})

    log_entry = json.loads(logs[0])
    assert log_entry['message'] == "Test event"
    assert log_entry['user_id'] == 123
    assert log_entry['action'] == 'login'
```

**Key Assertions:**
- Logging is configured correctly
- Log levels work
- File logging works
- Structured logging produces valid JSON

---

## Integration Tests

**File:** `tests/integration/test_dashboard_with_analytics.py`

### End-to-End Dashboard Scenarios

```python
def test_job_view_tracked_in_analytics(client, analytics):
    """Test that viewing a job via dashboard is tracked"""
    # View job through dashboard
    response = client.get('/dashboard/jobs/123')
    assert response.status_code == 200

    # Verify analytics event was recorded
    events = analytics.get_events(event_type='job_view')
    assert len(events) == 1
    assert events[0]['job_id'] == 123

def test_dashboard_displays_real_analytics(client, test_db, analytics):
    """Test that dashboard displays real analytics data"""
    # Generate some activity
    for i in range(5):
        analytics.track_event('job_view', user_id=f'user_{i}', job_id=123)

    # View dashboard analytics page
    response = client.get('/dashboard/analytics')
    data = response.get_json()

    assert data['total_job_views'] == 5
    assert 'job_123' in data['popular_jobs']
```

---

## Quick Implementation Checklist

### Day 1: Dashboard API v1
- [ ] Create `test_dashboard_api.py`
- [ ] Test endpoint availability (3-4 tests)
- [ ] Test data retrieval (3-4 tests)
- [ ] Test filtering and search (3-4 tests)
- [ ] Test error handling (2-3 tests)
- [ ] Run tests, aim for 60%+ coverage

### Day 2: Dashboard API v2
- [ ] Create `test_dashboard_api_v2.py`
- [ ] Test enhanced features (3-4 tests)
- [ ] Test real-time updates (2-3 tests)
- [ ] Test advanced filtering (2-3 tests)
- [ ] Run tests, aim for 60%+ coverage

### Day 3: Analytics
- [ ] Create `test_engagement_analytics.py`
- [ ] Test event tracking (3-4 tests)
- [ ] Test metrics calculation (3-4 tests)
- [ ] Test aggregation (2-3 tests)
- [ ] Create `test_engagement_analytics_api.py`
- [ ] Test API endpoints (3-4 tests)
- [ ] Run tests, aim for 70%+ coverage

### Day 4: Observability & Integration
- [ ] Create `test_observability_metrics.py`
- [ ] Test metric recording (3-4 tests)
- [ ] Create `test_logging_config.py`
- [ ] Test logging setup (2-3 tests)
- [ ] Create `test_dashboard_with_analytics.py`
- [ ] Test integration scenarios (2-3 tests)
- [ ] Run full test suite
- [ ] Verify coverage targets met

---

## Success Criteria

**Unit Tests:**
- [ ] 6 test files created
- [ ] Minimum 40 tests written
- [ ] Dashboard APIs: ≥60% coverage
- [ ] Analytics: ≥70% coverage
- [ ] Observability: ≥50% coverage
- [ ] All tests passing

**Integration Tests:**
- [ ] Dashboard-analytics integration verified
- [ ] Real-time updates working
- [ ] Metrics accurately reflect activity

---

## Common Pitfalls to Avoid

1. **Don't test UI rendering** - Test API responses, not HTML
2. **Don't hardcode dates** - Use relative dates or fixtures
3. **Clean up test data** - Reset analytics between tests
4. **Mock time-dependent operations** - Use freezegun or similar
5. **Don't test third-party libraries** - Mock Prometheus, etc.
6. **Keep WebSocket tests simple** - Test basic connectivity only
7. **Handle async operations** - Use proper async test utilities

---

**Estimated Time:** 3-4 days
**Difficulty:** Medium-Low
**Dependencies:** Phase 1 complete
**Next:** Phase 5 (Integration & E2E Testing)
