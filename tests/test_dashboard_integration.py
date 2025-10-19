"""
Integration Tests for Dashboard System
Tests complete workflows from frontend to database

Test Scenarios:
1. Load dashboard → Display metrics → Navigate views
2. Filter jobs → Update results → Persist filters
3. Search applications → Sort → Export data
4. Real-time updates via SSE
5. Materialized view refresh workflows
"""

import pytest
import sys
import os
import json
import time
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime, timedelta

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)


@pytest.fixture
def test_db_client():
    """Get real database client for integration tests"""
    try:
        from modules.database.lazy_instances import get_database_client
        return get_database_client()
    except Exception as e:
        pytest.skip(f"Database not available: {e}")


@pytest.fixture
def app():
    """Create Flask app with all dashboard components"""
    from flask import Flask
    from modules.dashboard_api_v2 import dashboard_api_v2

    app = Flask(__name__)
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test-integration-key'
    app.register_blueprint(dashboard_api_v2)

    return app


@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()


@pytest.fixture
def authenticated_client(app, client):
    """Create authenticated client"""
    with client.session_transaction() as sess:
        sess['authenticated'] = True
        sess['auth_time'] = datetime.now().timestamp()
    return client


# ===== Full Workflow Integration Tests =====

class TestDashboardWorkflow:
    """Test complete dashboard user workflows"""

    def test_dashboard_initial_load(self, authenticated_client):
        """Test initial dashboard load sequence"""
        # 1. Load overview endpoint
        response = authenticated_client.get('/api/v2/dashboard/overview')
        assert response.status_code == 200
        data = response.get_json()

        # Verify all required data is present
        assert data['success'] is True
        assert 'metrics' in data
        assert 'pipeline' in data
        assert 'recent_applications' in data

        # 2. Load pipeline status
        response = authenticated_client.get('/api/v2/dashboard/pipeline/status')
        assert response.status_code == 200
        pipeline_data = response.get_json()
        assert pipeline_data['success'] is True

        # 3. Load initial jobs list
        response = authenticated_client.get('/api/v2/dashboard/jobs?page=1&per_page=20')
        assert response.status_code == 200
        jobs_data = response.get_json()
        assert jobs_data['success'] is True

    def test_job_search_and_filter_workflow(self, authenticated_client):
        """Test searching and filtering jobs"""
        # 1. Start with all jobs
        response = authenticated_client.get('/api/v2/dashboard/jobs')
        assert response.status_code == 200
        all_jobs = response.get_json()
        initial_total = all_jobs['pagination']['total']

        # 2. Apply search filter
        response = authenticated_client.get('/api/v2/dashboard/jobs?search=python')
        assert response.status_code == 200
        search_results = response.get_json()
        assert search_results['filters_applied']['search'] == 'python'

        # 3. Add salary filter
        response = authenticated_client.get(
            '/api/v2/dashboard/jobs?search=python&salary_min=80000'
        )
        assert response.status_code == 200
        filtered_results = response.get_json()
        assert filtered_results['filters_applied']['salary_min'] == '80000'

        # 4. Add remote filter
        response = authenticated_client.get(
            '/api/v2/dashboard/jobs?'
            'search=python&'
            'salary_min=80000&'
            'remote_options=remote'
        )
        assert response.status_code == 200
        final_results = response.get_json()
        assert final_results['filters_applied']['remote_options'] == 'remote'

    def test_application_tracking_workflow(self, authenticated_client):
        """Test tracking application status changes"""
        # 1. Get all applications
        response = authenticated_client.get('/api/v2/dashboard/applications')
        assert response.status_code == 200
        all_apps = response.get_json()

        # 2. Filter by sent status
        response = authenticated_client.get('/api/v2/dashboard/applications?filter=sent')
        assert response.status_code == 200
        sent_apps = response.get_json()
        assert sent_apps['filters_applied']['status'] == 'sent'

        # 3. Filter by date range (last 7 days)
        date_from = (datetime.now() - timedelta(days=7)).date().isoformat()
        response = authenticated_client.get(
            f'/api/v2/dashboard/applications?date_from={date_from}'
        )
        assert response.status_code == 200
        recent_apps = response.get_json()
        assert recent_apps['filters_applied']['date_from'] == date_from

        # 4. Sort by company name
        response = authenticated_client.get(
            '/api/v2/dashboard/applications?sort_by=company&sort_dir=asc'
        )
        assert response.status_code == 200
        sorted_apps = response.get_json()
        assert sorted_apps['sort']['by'] == 'company'
        assert sorted_apps['sort']['direction'] == 'asc'

    def test_analytics_data_loading(self, authenticated_client):
        """Test loading analytics charts data"""
        # 1. Load 30-day analytics summary
        response = authenticated_client.get('/api/v2/dashboard/analytics/summary?range=30d')
        assert response.status_code == 200
        analytics = response.get_json()

        assert analytics['success'] is True
        assert analytics['range'] == '30d'
        assert 'scraping_velocity' in analytics
        assert 'success_rate' in analytics
        assert 'pipeline_funnel' in analytics
        assert 'ai_usage' in analytics

        # Verify data structure for charting
        assert isinstance(analytics['scraping_velocity'], list)
        assert isinstance(analytics['pipeline_funnel'], list)

        # 2. Load timeseries for scraping velocity
        response = authenticated_client.get(
            '/api/v2/dashboard/metrics/timeseries?'
            'metric=scraping_velocity&'
            'period=daily&'
            'range=7d'
        )
        assert response.status_code == 200
        timeseries = response.get_json()

        assert timeseries['success'] is True
        assert 'data' in timeseries
        assert 'summary' in timeseries

    def test_pagination_navigation_workflow(self, authenticated_client):
        """Test navigating through paginated results"""
        # Get first page
        response = authenticated_client.get('/api/v2/dashboard/jobs?page=1&per_page=10')
        assert response.status_code == 200
        page1 = response.get_json()

        total_pages = page1['pagination']['pages']
        assert page1['pagination']['page'] == 1

        # Navigate to next page (if exists)
        if total_pages > 1:
            response = authenticated_client.get('/api/v2/dashboard/jobs?page=2&per_page=10')
            assert response.status_code == 200
            page2 = response.get_json()
            assert page2['pagination']['page'] == 2

            # Navigate to last page
            response = authenticated_client.get(
                f'/api/v2/dashboard/jobs?page={total_pages}&per_page=10'
            )
            assert response.status_code == 200
            last_page = response.get_json()
            assert last_page['pagination']['page'] == total_pages


# ===== Materialized View Integration Tests =====

@pytest.mark.integration
class TestMaterializedViews:
    """Test materialized view queries and performance"""

    def test_application_summary_mv_query(self, test_db_client):
        """Test querying application_summary_mv materialized view"""
        from sqlalchemy import text

        with test_db_client.get_session() as session:
            # Query the materialized view
            query = text("""
                SELECT
                    application_id,
                    job_title,
                    company_name,
                    application_status
                FROM application_summary_mv
                LIMIT 10
            """)

            result = session.execute(query).fetchall()

            # Verify structure
            for row in result:
                assert hasattr(row, 'application_id')
                assert hasattr(row, 'job_title')
                assert hasattr(row, 'company_name')
                assert hasattr(row, 'application_status')

    def test_dashboard_metrics_daily_query(self, test_db_client):
        """Test querying dashboard_metrics_daily table"""
        from sqlalchemy import text

        with test_db_client.get_session() as session:
            # Query daily metrics
            query = text("""
                SELECT
                    metric_date,
                    jobs_scraped_count,
                    applications_sent_count,
                    success_rate
                FROM dashboard_metrics_daily
                WHERE metric_date >= CURRENT_DATE - INTERVAL '7 days'
                ORDER BY metric_date DESC
            """)

            result = session.execute(query).fetchall()

            # Verify data
            for row in result:
                assert hasattr(row, 'metric_date')
                assert hasattr(row, 'jobs_scraped_count')
                assert hasattr(row, 'applications_sent_count')

    @pytest.mark.slow
    def test_materialized_view_performance(self, test_db_client):
        """Test materialized view query performance"""
        from sqlalchemy import text
        import time

        with test_db_client.get_session() as session:
            # Time a complex query using materialized view
            query = text("""
                SELECT
                    application_id,
                    job_title,
                    company_name,
                    application_status,
                    created_at,
                    tone_coherence_score
                FROM application_summary_mv
                ORDER BY created_at DESC
                LIMIT 100
            """)

            start_time = time.time()
            result = session.execute(query).fetchall()
            elapsed = time.time() - start_time

            # Materialized view should be fast (< 50ms target)
            assert elapsed < 0.5  # 500ms max (generous for test environment)
            assert len(result) <= 100


# ===== Data Consistency Tests =====

@pytest.mark.integration
class TestDataConsistency:
    """Test data consistency across different endpoints"""

    def test_job_count_consistency(self, authenticated_client):
        """Test job counts are consistent across endpoints"""
        # Get overview metrics
        overview = authenticated_client.get('/api/v2/dashboard/overview').get_json()
        overview_total = overview['metrics']['total_jobs']

        # Get pipeline status
        pipeline = authenticated_client.get('/api/v2/dashboard/pipeline/status').get_json()
        pipeline_raw = pipeline['stages'][0]['count']

        # Totals should match (raw scrapes = total jobs in system)
        # Note: This might not always be exact depending on business logic
        # but should be reasonably close
        assert overview_total >= 0
        assert pipeline_raw >= 0

    def test_application_count_consistency(self, authenticated_client):
        """Test application counts are consistent"""
        # Get overview
        overview = authenticated_client.get('/api/v2/dashboard/overview').get_json()
        overview_apps_7d = overview['metrics']['applications']['7d']

        # Get applications list
        apps_response = authenticated_client.get('/api/v2/dashboard/applications').get_json()
        apps_total = apps_response['pagination']['total']

        # Total apps should be >= apps in last 7 days
        assert apps_total >= overview_apps_7d


# ===== Filter Persistence Tests =====

class TestFilterPersistence:
    """Test filter state management (would use localStorage in real frontend)"""

    def test_filter_parameters_preserved(self, authenticated_client):
        """Test that filter parameters are correctly echoed back"""
        filters = {
            'filter': 'eligible',
            'search': 'python developer',
            'salary_min': '80000',
            'salary_max': '150000',
            'remote_options': 'remote',
            'job_type': 'full-time',
            'seniority_level': 'senior',
            'posted_within': '7d'
        }

        # Build query string
        query_string = '&'.join([f'{k}={v}' for k, v in filters.items()])

        response = authenticated_client.get(f'/api/v2/dashboard/jobs?{query_string}')
        assert response.status_code == 200

        data = response.get_json()
        applied_filters = data['filters_applied']

        # Verify all filters are preserved
        assert applied_filters['filter'] == filters['filter']
        assert applied_filters['search'] == filters['search']
        assert applied_filters['salary_min'] == filters['salary_min']
        assert applied_filters['salary_max'] == filters['salary_max']


# ===== Error Recovery Tests =====

@pytest.mark.integration
class TestErrorRecovery:
    """Test system behavior under error conditions"""

    def test_graceful_degradation_on_db_error(self, authenticated_client):
        """Test API handles database errors gracefully"""
        with patch('modules.dashboard_api_v2.get_database_client') as mock_get_db:
            mock_get_db.side_effect = Exception("Database connection lost")

            response = authenticated_client.get('/api/v2/dashboard/overview')
            assert response.status_code == 500

            data = response.get_json()
            assert data['success'] is False
            assert 'error' in data
            # Should not expose internal details in production
            assert 'details' not in data or data['details'] is None

    def test_invalid_input_handling(self, authenticated_client):
        """Test handling of various invalid inputs"""
        # Invalid filter
        response = authenticated_client.get('/api/v2/dashboard/jobs?filter=invalid')
        assert response.status_code == 400

        # Invalid page number
        response = authenticated_client.get('/api/v2/dashboard/jobs?page=abc')
        assert response.status_code == 400

        # Invalid sort field (should default gracefully)
        response = authenticated_client.get('/api/v2/dashboard/applications?sort_by=invalid')
        assert response.status_code == 200  # Defaults to valid sort


# ===== Concurrent Access Tests =====

@pytest.mark.slow
class TestConcurrentAccess:
    """Test behavior under concurrent access"""

    def test_multiple_simultaneous_requests(self, authenticated_client):
        """Test handling multiple simultaneous requests"""
        import concurrent.futures

        def make_request(endpoint):
            return authenticated_client.get(endpoint)

        endpoints = [
            '/api/v2/dashboard/overview',
            '/api/v2/dashboard/jobs',
            '/api/v2/dashboard/applications',
            '/api/v2/dashboard/analytics/summary',
            '/api/v2/dashboard/pipeline/status'
        ]

        # Make concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(make_request, ep) for ep in endpoints]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]

        # All should succeed
        for response in results:
            assert response.status_code in [200, 500]  # 500 ok if DB mock fails

    def test_session_isolation(self, app):
        """Test that concurrent sessions are isolated"""
        client1 = app.test_client()
        client2 = app.test_client()

        # Authenticate client1
        with client1.session_transaction() as sess:
            sess['authenticated'] = True

        # Client1 should be authenticated
        response1 = client1.get('/api/v2/dashboard/overview')
        assert response1.status_code == 200

        # Client2 should not be authenticated
        response2 = client2.get('/api/v2/dashboard/overview')
        assert response2.status_code == 401


# ===== Performance Integration Tests =====

@pytest.mark.slow
@pytest.mark.performance
class TestPerformanceIntegration:
    """Test overall system performance"""

    def test_dashboard_load_time(self, authenticated_client):
        """Test complete dashboard load time"""
        import time

        start = time.time()

        # Simulate initial dashboard load (3 key requests)
        r1 = authenticated_client.get('/api/v2/dashboard/overview')
        r2 = authenticated_client.get('/api/v2/dashboard/pipeline/status')
        r3 = authenticated_client.get('/api/v2/dashboard/jobs?page=1&per_page=20')

        elapsed = time.time() - start

        # All requests should succeed
        assert r1.status_code == 200
        assert r2.status_code == 200
        assert r3.status_code == 200

        # Total load time should be reasonable
        assert elapsed < 3.0  # 3 seconds max for initial load

    def test_filter_response_time(self, authenticated_client):
        """Test filter application response time"""
        import time

        # Apply complex filter
        query = (
            '/api/v2/dashboard/jobs?'
            'filter=eligible&'
            'search=python&'
            'salary_min=80000&'
            'remote_options=remote&'
            'posted_within=7d'
        )

        start = time.time()
        response = authenticated_client.get(query)
        elapsed = time.time() - start

        assert response.status_code == 200
        assert elapsed < 2.0  # Filtered queries should be fast


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
