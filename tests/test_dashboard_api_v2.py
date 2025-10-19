"""
Comprehensive Unit Tests for Dashboard API V2
Tests all endpoints, filters, pagination, error handling, and edge cases

Test Coverage:
- /api/v2/dashboard/overview - Main dashboard endpoint
- /api/v2/dashboard/jobs - Jobs listing with filters
- /api/v2/dashboard/applications - Applications listing with filters
- /api/v2/dashboard/analytics/summary - Analytics data
- /api/v2/dashboard/metrics/timeseries - Time series metrics
- /api/v2/dashboard/pipeline/status - Pipeline status
"""

import pytest
import sys
import os
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime, timedelta
from flask import Flask, session

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)


@pytest.fixture
def app():
    """Create Flask test app with dashboard API v2 blueprint"""
    from modules.dashboard_api_v2 import dashboard_api_v2

    app = Flask(__name__)
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test-secret-key'
    app.register_blueprint(dashboard_api_v2)

    return app


@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()


@pytest.fixture
def authenticated_client(app, client):
    """Create authenticated test client"""
    with client.session_transaction() as sess:
        sess['authenticated'] = True
        sess['auth_time'] = datetime.now().timestamp()
    return client


@pytest.fixture
def mock_db_session():
    """Mock database session with common test data"""
    session = MagicMock()

    # Mock overview query result
    overview_result = MagicMock()
    overview_result.jobs_24h = 25
    overview_result.jobs_7d = 150
    overview_result.jobs_prev_24h = 20
    overview_result.jobs_prev_7d = 120
    overview_result.total_jobs = 500
    overview_result.analyzed_24h = 20
    overview_result.analyzed_7d = 140
    overview_result.analyzed_prev_24h = 15
    overview_result.apps_24h = 5
    overview_result.apps_7d = 30
    overview_result.apps_prev_24h = 4
    overview_result.apps_success_7d = 25
    overview_result.apps_total_7d = 30
    overview_result.raw_count = 500
    overview_result.cleaned_count = 450
    overview_result.analyzed_count = 400
    overview_result.eligible_count = 100
    overview_result.applied_count = 30

    # Mock recent applications
    app_row = MagicMock()
    app_row.application_id = "app-123"
    app_row.job_title = "Senior Python Developer"
    app_row.company_name = "Tech Corp"
    app_row.application_status = "sent"
    app_row.created_at = datetime.now()
    app_row.documents_sent = ["resume.pdf", "cover_letter.pdf"]
    app_row.tone_coherence_score = 8.5

    # Mock job row for jobs endpoint
    job_row = MagicMock()
    job_row.id = 1
    job_row.job_title = "Senior Python Developer"
    job_row.salary_low = 80000
    job_row.salary_high = 120000
    job_row.compensation_currency = "USD"
    job_row.salary_period = "yearly"
    job_row.location = "Remote"
    job_row.remote_options = "remote"
    job_row.job_type = "full-time"
    job_row.seniority_level = "senior"
    job_row.eligibility_flag = True
    job_row.application_status = "not_applied"
    job_row.posted_date = datetime.now()
    job_row.primary_source_url = "https://example.com/job"
    job_row.created_at = datetime.now()
    job_row.company_name = "Tech Corp"
    job_row.company_url = "https://example.com"
    job_row.application_id = None
    job_row.application_date = None
    job_row.app_status = None

    def mock_execute(query, params=None):
        """Custom mock execute that returns different data based on query"""
        mock_result = MagicMock()

        # Check query string to determine what to return
        query_str = str(query)

        if 'application_summary_mv' in query_str:
            mock_result.fetchall.return_value = [app_row]
            mock_result.fetchone.return_value = app_row
            mock_result.scalar.return_value = 1
        elif 'jobs j' in query_str or 'FROM jobs' in query_str:
            mock_result.fetchall.return_value = [job_row]
            mock_result.fetchone.return_value = job_row
            mock_result.scalar.return_value = 1
        else:
            # Default to overview result
            mock_result.fetchall.return_value = [app_row]
            mock_result.fetchone.return_value = overview_result
            mock_result.scalar.return_value = 100

        return mock_result

    session.execute = mock_execute

    return session


@pytest.fixture
def mock_db_client(mock_db_session):
    """Mock database client"""
    with patch('modules.dashboard_api_v2.get_database_client') as mock_get_db:
        mock_client = MagicMock()
        mock_client.get_session.return_value.__enter__ = lambda self: mock_db_session
        mock_client.get_session.return_value.__exit__ = lambda self, *args: None
        mock_get_db.return_value = mock_client
        yield mock_client


# ===== Authentication Tests =====

class TestAuthentication:
    """Test authentication and authorization"""

    def test_requires_auth_unauthenticated(self, client):
        """Test that endpoints require authentication"""
        response = client.get('/api/v2/dashboard/overview')
        assert response.status_code == 401
        data = response.get_json()
        assert data['success'] is False
        assert 'Authentication required' in data['error']

    def test_debug_mode_auto_auth(self, app, client, mock_db_client):
        """Test that debug mode auto-authenticates"""
        app.debug = True
        response = client.get('/api/v2/dashboard/overview')
        # Should succeed (auto-authenticated)
        assert response.status_code == 200

    def test_authenticated_access(self, authenticated_client, mock_db_client):
        """Test authenticated users can access endpoints"""
        response = authenticated_client.get('/api/v2/dashboard/overview')
        assert response.status_code == 200


# ===== Dashboard Overview Tests =====

class TestDashboardOverview:
    """Test /api/v2/dashboard/overview endpoint"""

    def test_overview_success(self, authenticated_client, mock_db_client):
        """Test successful overview response"""
        response = authenticated_client.get('/api/v2/dashboard/overview')
        assert response.status_code == 200

        data = response.get_json()
        assert data['success'] is True
        assert 'metrics' in data
        assert 'pipeline' in data
        assert 'recent_applications' in data
        assert 'meta' in data

    def test_overview_metrics_structure(self, authenticated_client, mock_db_client):
        """Test metrics data structure"""
        response = authenticated_client.get('/api/v2/dashboard/overview')
        data = response.get_json()

        metrics = data['metrics']
        assert 'scrapes' in metrics
        assert 'analyzed' in metrics
        assert 'applications' in metrics
        assert 'success_rate' in metrics

        # Check scrapes has 24h and 7d data
        assert '24h' in metrics['scrapes']
        assert '7d' in metrics['scrapes']
        assert 'trend_24h' in metrics['scrapes']
        assert 'trend_7d' in metrics['scrapes']

    def test_overview_pipeline_structure(self, authenticated_client, mock_db_client):
        """Test pipeline data structure"""
        response = authenticated_client.get('/api/v2/dashboard/overview')
        data = response.get_json()

        pipeline = data['pipeline']
        assert 'stages' in pipeline
        assert 'conversion_rate' in pipeline
        assert 'bottleneck' in pipeline

        # Check stages
        stages = pipeline['stages']
        assert len(stages) == 5
        stage_ids = [s['id'] for s in stages]
        assert stage_ids == ['raw', 'cleaned', 'analyzed', 'eligible', 'applied']

    def test_overview_recent_applications(self, authenticated_client, mock_db_client):
        """Test recent applications data"""
        response = authenticated_client.get('/api/v2/dashboard/overview')
        data = response.get_json()

        apps = data['recent_applications']
        assert isinstance(apps, list)
        if len(apps) > 0:
            app = apps[0]
            assert 'id' in app
            assert 'job_title' in app
            assert 'company_name' in app
            assert 'status' in app

    def test_overview_trend_calculation(self, authenticated_client, mock_db_client):
        """Test trend calculations are correct"""
        response = authenticated_client.get('/api/v2/dashboard/overview')
        data = response.get_json()

        # Trend should be: ((25 - 20) / 20) * 100 = 25%
        assert data['metrics']['scrapes']['trend_24h'] == 25.0

    def test_overview_error_handling(self, authenticated_client):
        """Test error handling when database fails"""
        with patch('modules.dashboard_api_v2.get_database_client') as mock_get_db:
            mock_get_db.side_effect = Exception("Database connection failed")

            response = authenticated_client.get('/api/v2/dashboard/overview')
            assert response.status_code == 500
            data = response.get_json()
            assert data['success'] is False
            assert 'error' in data


# ===== Jobs Endpoint Tests =====

class TestJobsEndpoint:
    """Test /api/v2/dashboard/jobs endpoint"""

    def test_jobs_basic_fetch(self, authenticated_client, mock_db_client):
        """Test basic jobs fetch without filters"""
        response = authenticated_client.get('/api/v2/dashboard/jobs')
        assert response.status_code == 200

        data = response.get_json()
        assert data['success'] is True
        assert 'jobs' in data
        assert 'pagination' in data
        assert 'filters_applied' in data

    def test_jobs_pagination(self, authenticated_client, mock_db_client):
        """Test pagination parameters"""
        response = authenticated_client.get('/api/v2/dashboard/jobs?page=2&per_page=10')
        assert response.status_code == 200

        data = response.get_json()
        assert data['pagination']['page'] == 2
        assert data['pagination']['per_page'] == 10

    def test_jobs_pagination_limits(self, authenticated_client, mock_db_client):
        """Test pagination limits (max 100, min 1)"""
        # Test max limit
        response = authenticated_client.get('/api/v2/dashboard/jobs?per_page=200')
        data = response.get_json()
        assert data['pagination']['per_page'] <= 100

        # Test min limit
        response = authenticated_client.get('/api/v2/dashboard/jobs?per_page=0')
        data = response.get_json()
        assert data['pagination']['per_page'] >= 1

    def test_jobs_filter_by_status(self, authenticated_client, mock_db_client):
        """Test filtering by status"""
        filters = ['all', 'eligible', 'not_eligible', 'applied']

        for filter_type in filters:
            response = authenticated_client.get(f'/api/v2/dashboard/jobs?filter={filter_type}')
            assert response.status_code == 200
            data = response.get_json()
            assert data['filters_applied']['filter'] == filter_type

    def test_jobs_invalid_filter(self, authenticated_client, mock_db_client):
        """Test invalid filter parameter"""
        response = authenticated_client.get('/api/v2/dashboard/jobs?filter=invalid')
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
        assert 'Invalid filter' in data['error']

    def test_jobs_search_query(self, authenticated_client, mock_db_client):
        """Test search functionality"""
        response = authenticated_client.get('/api/v2/dashboard/jobs?search=python')
        assert response.status_code == 200
        data = response.get_json()
        assert data['filters_applied']['search'] == 'python'

    def test_jobs_salary_filters(self, authenticated_client, mock_db_client):
        """Test salary range filters"""
        response = authenticated_client.get('/api/v2/dashboard/jobs?salary_min=80000&salary_max=150000')
        assert response.status_code == 200
        data = response.get_json()
        assert data['filters_applied']['salary_min'] == '80000'
        assert data['filters_applied']['salary_max'] == '150000'

    def test_jobs_remote_filter(self, authenticated_client, mock_db_client):
        """Test remote options filter"""
        response = authenticated_client.get('/api/v2/dashboard/jobs?remote_options=remote')
        assert response.status_code == 200
        data = response.get_json()
        assert data['filters_applied']['remote_options'] == 'remote'

    def test_jobs_job_type_filter(self, authenticated_client, mock_db_client):
        """Test job type filter"""
        response = authenticated_client.get('/api/v2/dashboard/jobs?job_type=full-time')
        assert response.status_code == 200
        data = response.get_json()
        assert data['filters_applied']['job_type'] == 'full-time'

    def test_jobs_seniority_filter(self, authenticated_client, mock_db_client):
        """Test seniority level filter"""
        response = authenticated_client.get('/api/v2/dashboard/jobs?seniority_level=senior')
        assert response.status_code == 200
        data = response.get_json()
        assert data['filters_applied']['seniority_level'] == 'senior'

    def test_jobs_posted_within_filter(self, authenticated_client, mock_db_client):
        """Test posted within date filter"""
        for period in ['24h', '7d', '30d']:
            response = authenticated_client.get(f'/api/v2/dashboard/jobs?posted_within={period}')
            assert response.status_code == 200
            data = response.get_json()
            assert data['filters_applied']['posted_within'] == period

    def test_jobs_combined_filters(self, authenticated_client, mock_db_client):
        """Test combining multiple filters"""
        response = authenticated_client.get(
            '/api/v2/dashboard/jobs?'
            'filter=eligible&'
            'search=python&'
            'salary_min=80000&'
            'remote_options=remote&'
            'posted_within=7d'
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data['filters_applied']['filter'] == 'eligible'
        assert data['filters_applied']['search'] == 'python'
        assert data['filters_applied']['salary_min'] == '80000'

    def test_jobs_invalid_page_parameter(self, authenticated_client, mock_db_client):
        """Test invalid page parameter handling"""
        response = authenticated_client.get('/api/v2/dashboard/jobs?page=abc')
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False


# ===== Applications Endpoint Tests =====

class TestApplicationsEndpoint:
    """Test /api/v2/dashboard/applications endpoint"""

    def test_applications_basic_fetch(self, authenticated_client, mock_db_client):
        """Test basic applications fetch"""
        response = authenticated_client.get('/api/v2/dashboard/applications')
        assert response.status_code == 200

        data = response.get_json()
        assert data['success'] is True
        assert 'applications' in data
        assert 'pagination' in data
        assert 'filters_applied' in data
        assert 'sort' in data

    def test_applications_status_filter(self, authenticated_client, mock_db_client):
        """Test filtering by application status"""
        statuses = ['all', 'sent', 'pending', 'failed']

        for status in statuses:
            response = authenticated_client.get(f'/api/v2/dashboard/applications?filter={status}')
            assert response.status_code == 200
            data = response.get_json()
            assert data['filters_applied']['status'] == status

    def test_applications_search(self, authenticated_client, mock_db_client):
        """Test search across job title and company"""
        response = authenticated_client.get('/api/v2/dashboard/applications?search=developer')
        assert response.status_code == 200
        data = response.get_json()
        assert data['filters_applied']['search'] == 'developer'

    def test_applications_company_filter(self, authenticated_client, mock_db_client):
        """Test company name filter"""
        response = authenticated_client.get('/api/v2/dashboard/applications?company=tech')
        assert response.status_code == 200
        data = response.get_json()
        assert data['filters_applied']['company'] == 'tech'

    def test_applications_date_range(self, authenticated_client, mock_db_client):
        """Test date range filters"""
        date_from = '2024-01-01'
        date_to = '2024-12-31'

        response = authenticated_client.get(
            f'/api/v2/dashboard/applications?date_from={date_from}&date_to={date_to}'
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data['filters_applied']['date_from'] == date_from
        assert data['filters_applied']['date_to'] == date_to

    def test_applications_score_range(self, authenticated_client, mock_db_client):
        """Test coherence score range filters"""
        response = authenticated_client.get('/api/v2/dashboard/applications?score_min=7.0&score_max=10.0')
        assert response.status_code == 200
        data = response.get_json()
        assert data['filters_applied']['score_min'] == '7.0'
        assert data['filters_applied']['score_max'] == '10.0'

    def test_applications_sorting(self, authenticated_client, mock_db_client):
        """Test sorting options"""
        sort_fields = ['date', 'company', 'status', 'score']
        sort_dirs = ['asc', 'desc']

        for field in sort_fields:
            for direction in sort_dirs:
                response = authenticated_client.get(
                    f'/api/v2/dashboard/applications?sort_by={field}&sort_dir={direction}'
                )
                assert response.status_code == 200
                data = response.get_json()
                assert data['sort']['by'] == field
                assert data['sort']['direction'] == direction

    def test_applications_invalid_sort_field(self, authenticated_client, mock_db_client):
        """Test invalid sort field defaults to 'date'"""
        response = authenticated_client.get('/api/v2/dashboard/applications?sort_by=invalid')
        assert response.status_code == 200
        data = response.get_json()
        assert data['sort']['by'] == 'date'  # Should default

    def test_applications_invalid_sort_direction(self, authenticated_client, mock_db_client):
        """Test invalid sort direction defaults to 'desc'"""
        response = authenticated_client.get('/api/v2/dashboard/applications?sort_dir=invalid')
        assert response.status_code == 200
        data = response.get_json()
        assert data['sort']['direction'] == 'desc'  # Should default


# ===== Analytics Endpoint Tests =====

class TestAnalyticsEndpoint:
    """Test /api/v2/dashboard/analytics/summary endpoint"""

    def test_analytics_summary_success(self, authenticated_client, mock_db_client):
        """Test successful analytics summary response"""
        response = authenticated_client.get('/api/v2/dashboard/analytics/summary')
        assert response.status_code == 200

        data = response.get_json()
        assert data['success'] is True
        assert 'scraping_velocity' in data
        assert 'success_rate' in data
        assert 'pipeline_funnel' in data
        assert 'ai_usage' in data
        assert 'summary' in data

    def test_analytics_time_ranges(self, authenticated_client, mock_db_client):
        """Test different time range parameters"""
        ranges = ['7d', '30d', '90d']

        for time_range in ranges:
            response = authenticated_client.get(f'/api/v2/dashboard/analytics/summary?range={time_range}')
            assert response.status_code == 200
            data = response.get_json()
            assert data['range'] == time_range

    def test_analytics_pipeline_funnel_structure(self, authenticated_client, mock_db_client):
        """Test pipeline funnel data structure"""
        response = authenticated_client.get('/api/v2/dashboard/analytics/summary')
        data = response.get_json()

        funnel = data['pipeline_funnel']
        assert len(funnel) == 5

        for stage in funnel:
            assert 'stage' in stage
            assert 'count' in stage
            assert 'color' in stage

    def test_analytics_conversion_rates(self, authenticated_client, mock_db_client):
        """Test conversion rates calculation"""
        response = authenticated_client.get('/api/v2/dashboard/analytics/summary')
        data = response.get_json()

        conversion_rates = data['conversion_rates']
        assert isinstance(conversion_rates, list)

        if len(conversion_rates) > 0:
            rate = conversion_rates[0]
            assert 'from_stage' in rate
            assert 'to_stage' in rate
            assert 'rate' in rate
            assert 0 <= rate['rate'] <= 100

    def test_analytics_summary_stats(self, authenticated_client, mock_db_client):
        """Test summary statistics"""
        response = authenticated_client.get('/api/v2/dashboard/analytics/summary')
        data = response.get_json()

        summary = data['summary']
        assert 'total_jobs_scraped' in summary
        assert 'total_applications' in summary
        assert 'avg_success_rate' in summary
        assert 'total_ai_requests' in summary
        assert 'overall_conversion_rate' in summary


# ===== Timeseries Metrics Tests =====

class TestTimeseriesMetrics:
    """Test /api/v2/dashboard/metrics/timeseries endpoint"""

    def test_timeseries_basic(self, authenticated_client, mock_db_client):
        """Test basic timeseries response"""
        response = authenticated_client.get('/api/v2/dashboard/metrics/timeseries')
        assert response.status_code == 200

        data = response.get_json()
        assert data['success'] is True
        assert 'metric' in data
        assert 'period' in data
        assert 'range' in data
        assert 'data' in data
        assert 'summary' in data

    def test_timeseries_metric_types(self, authenticated_client, mock_db_client):
        """Test different metric types"""
        metrics = ['scraping_velocity', 'application_success', 'ai_usage']

        for metric in metrics:
            response = authenticated_client.get(f'/api/v2/dashboard/metrics/timeseries?metric={metric}')
            assert response.status_code == 200
            data = response.get_json()
            assert data['metric'] == metric

    def test_timeseries_periods(self, authenticated_client, mock_db_client):
        """Test daily vs hourly periods"""
        for period in ['daily', 'hourly']:
            response = authenticated_client.get(f'/api/v2/dashboard/metrics/timeseries?period={period}')
            assert response.status_code == 200
            data = response.get_json()
            assert data['period'] == period

    def test_timeseries_time_ranges(self, authenticated_client, mock_db_client):
        """Test different time ranges"""
        for time_range in ['24h', '7d', '30d']:
            response = authenticated_client.get(f'/api/v2/dashboard/metrics/timeseries?range={time_range}')
            assert response.status_code == 200
            data = response.get_json()
            assert data['range'] == time_range

    def test_timeseries_summary_stats(self, authenticated_client, mock_db_client):
        """Test summary statistics in timeseries"""
        response = authenticated_client.get('/api/v2/dashboard/metrics/timeseries')
        data = response.get_json()

        summary = data['summary']
        assert 'total' in summary
        assert 'average' in summary
        assert 'peak' in summary
        assert 'low' in summary


# ===== Pipeline Status Tests =====

class TestPipelineStatus:
    """Test /api/v2/dashboard/pipeline/status endpoint"""

    def test_pipeline_status_success(self, authenticated_client, mock_db_client):
        """Test successful pipeline status response"""
        response = authenticated_client.get('/api/v2/dashboard/pipeline/status')
        assert response.status_code == 200

        data = response.get_json()
        assert data['success'] is True
        assert 'stages' in data
        assert 'health' in data
        assert 'applications_today' in data
        assert 'queue_size' in data

    def test_pipeline_stages_structure(self, authenticated_client, mock_db_client):
        """Test pipeline stages structure"""
        response = authenticated_client.get('/api/v2/dashboard/pipeline/status')
        data = response.get_json()

        stages = data['stages']
        assert len(stages) == 5

        for stage in stages:
            assert 'id' in stage
            assert 'name' in stage
            assert 'count' in stage
            assert 'processing' in stage
            assert 'health' in stage


# ===== Edge Cases and Error Handling =====

class TestEdgeCases:
    """Test edge cases and error handling"""

    def test_empty_results(self, authenticated_client):
        """Test handling of empty result sets"""
        with patch('modules.dashboard_api_v2.get_database_client') as mock_get_db:
            mock_session = MagicMock()
            mock_session.execute.return_value.fetchall.return_value = []
            mock_session.execute.return_value.scalar.return_value = 0

            mock_client = MagicMock()
            mock_client.get_session.return_value.__enter__ = lambda self: mock_session
            mock_client.get_session.return_value.__exit__ = lambda self, *args: None
            mock_get_db.return_value = mock_client

            response = authenticated_client.get('/api/v2/dashboard/jobs')
            assert response.status_code == 200
            data = response.get_json()
            assert data['pagination']['total'] == 0
            assert len(data['jobs']) == 0

    def test_division_by_zero_in_trends(self, authenticated_client):
        """Test trend calculation with zero previous values"""
        with patch('modules.dashboard_api_v2.get_database_client') as mock_get_db:
            mock_session = MagicMock()

            # Create result with zero previous values
            result = MagicMock()
            result.jobs_24h = 10
            result.jobs_prev_24h = 0  # Division by zero scenario
            result.jobs_7d = 50
            result.jobs_prev_7d = 0
            result.total_jobs = 100
            result.analyzed_24h = 5
            result.analyzed_7d = 40
            result.analyzed_prev_24h = 0
            result.apps_24h = 2
            result.apps_7d = 15
            result.apps_prev_24h = 0
            result.apps_success_7d = 10
            result.apps_total_7d = 15
            result.raw_count = 100
            result.cleaned_count = 90
            result.analyzed_count = 80
            result.eligible_count = 30
            result.applied_count = 15

            mock_session.execute.return_value.fetchone.return_value = result
            mock_session.execute.return_value.fetchall.return_value = []

            mock_client = MagicMock()
            mock_client.get_session.return_value.__enter__ = lambda self: mock_session
            mock_client.get_session.return_value.__exit__ = lambda self, *args: None
            mock_get_db.return_value = mock_client

            response = authenticated_client.get('/api/v2/dashboard/overview')
            assert response.status_code == 200
            data = response.get_json()

            # Trend should be 0.0 when previous is 0
            assert data['metrics']['scrapes']['trend_24h'] == 0.0

    def test_database_connection_error(self, authenticated_client):
        """Test handling of database connection errors"""
        with patch('modules.dashboard_api_v2.get_database_client') as mock_get_db:
            mock_get_db.side_effect = ConnectionError("Cannot connect to database")

            response = authenticated_client.get('/api/v2/dashboard/overview')
            assert response.status_code == 500
            data = response.get_json()
            assert data['success'] is False
            assert 'error' in data

    def test_sql_execution_error(self, authenticated_client):
        """Test handling of SQL execution errors"""
        with patch('modules.dashboard_api_v2.get_database_client') as mock_get_db:
            mock_session = MagicMock()
            mock_session.execute.side_effect = Exception("SQL syntax error")

            mock_client = MagicMock()
            mock_client.get_session.return_value.__enter__ = lambda self: mock_session
            mock_client.get_session.return_value.__exit__ = lambda self, *args: None
            mock_get_db.return_value = mock_client

            response = authenticated_client.get('/api/v2/dashboard/overview')
            assert response.status_code == 500
            data = response.get_json()
            assert data['success'] is False


# ===== Performance Tests =====

class TestPerformance:
    """Test performance characteristics"""

    @pytest.mark.slow
    def test_overview_response_time(self, authenticated_client, mock_db_client):
        """Test overview endpoint responds within acceptable time"""
        import time

        start = time.time()
        response = authenticated_client.get('/api/v2/dashboard/overview')
        elapsed = time.time() - start

        assert response.status_code == 200
        assert elapsed < 1.0  # Should respond in under 1 second with mocks

    @pytest.mark.slow
    def test_jobs_pagination_performance(self, authenticated_client, mock_db_client):
        """Test pagination doesn't cause significant overhead"""
        import time

        # Test multiple pages
        times = []
        for page in range(1, 6):
            start = time.time()
            response = authenticated_client.get(f'/api/v2/dashboard/jobs?page={page}')
            elapsed = time.time() - start
            times.append(elapsed)
            assert response.status_code == 200

        # Average time should be consistent
        avg_time = sum(times) / len(times)
        assert avg_time < 1.0  # Should be fast with mocks


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
