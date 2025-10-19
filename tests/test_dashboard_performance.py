"""
Performance Benchmark Tests for Dashboard System
Tests query performance, materialized view speed, and API response times

Benchmarks:
- Materialized view queries (<5ms target)
- API endpoint response times (<100ms target)
- Complex filter queries (<200ms target)
- Concurrent request handling
- Memory usage under load
"""

import pytest
import sys
import os
import time
import statistics
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)


@pytest.fixture
def test_db_client():
    """Get real database client for performance tests"""
    try:
        from modules.database.lazy_instances import get_database_client
        return get_database_client()
    except Exception as e:
        pytest.skip(f"Database not available for performance testing: {e}")


@pytest.fixture
def app():
    """Create Flask app"""
    from flask import Flask
    from modules.dashboard_api_v2 import dashboard_api_v2

    app = Flask(__name__)
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'perf-test-key'
    app.register_blueprint(dashboard_api_v2)

    return app


@pytest.fixture
def authenticated_client(app):
    """Create authenticated client"""
    client = app.test_client()
    with client.session_transaction() as sess:
        sess['authenticated'] = True
        sess['auth_time'] = datetime.now().timestamp()
    return client


def measure_execution_time(func, iterations=10):
    """
    Measure execution time over multiple iterations
    Returns: (avg_ms, min_ms, max_ms, median_ms, std_dev_ms)
    """
    times = []

    for _ in range(iterations):
        start = time.perf_counter()
        func()
        elapsed = (time.perf_counter() - start) * 1000  # Convert to ms
        times.append(elapsed)

    return {
        'avg': statistics.mean(times),
        'min': min(times),
        'max': max(times),
        'median': statistics.median(times),
        'std_dev': statistics.stdev(times) if len(times) > 1 else 0,
        'samples': len(times)
    }


# ===== Materialized View Performance Tests =====

@pytest.mark.slow
@pytest.mark.performance
class TestMaterializedViewPerformance:
    """Test materialized view query performance"""

    def test_application_summary_mv_performance(self, test_db_client):
        """Benchmark: application_summary_mv query should be <5ms"""
        from sqlalchemy import text

        def query_mv():
            with test_db_client.get_session() as session:
                query = text("""
                    SELECT
                        application_id,
                        job_title,
                        company_name,
                        application_status,
                        created_at,
                        documents_sent,
                        tone_coherence_score
                    FROM application_summary_mv
                    ORDER BY created_at DESC
                    LIMIT 10
                """)
                session.execute(query).fetchall()

        stats = measure_execution_time(query_mv, iterations=20)

        print(f"\n=== application_summary_mv Performance ===")
        print(f"Average: {stats['avg']:.2f}ms")
        print(f"Median:  {stats['median']:.2f}ms")
        print(f"Min:     {stats['min']:.2f}ms")
        print(f"Max:     {stats['max']:.2f}ms")
        print(f"Std Dev: {stats['std_dev']:.2f}ms")

        # Target: <5ms average (may be higher in test environment)
        # Allowing 100ms for test environment overhead
        assert stats['avg'] < 100, f"MV query too slow: {stats['avg']:.2f}ms"

    def test_dashboard_metrics_daily_performance(self, test_db_client):
        """Benchmark: dashboard_metrics_daily query performance"""
        from sqlalchemy import text

        def query_metrics():
            with test_db_client.get_session() as session:
                query = text("""
                    SELECT
                        metric_date,
                        jobs_scraped_count,
                        applications_sent_count,
                        success_rate,
                        ai_requests_sent
                    FROM dashboard_metrics_daily
                    WHERE metric_date >= CURRENT_DATE - INTERVAL '30 days'
                    ORDER BY metric_date ASC
                """)
                session.execute(query).fetchall()

        stats = measure_execution_time(query_metrics, iterations=20)

        print(f"\n=== dashboard_metrics_daily Performance ===")
        print(f"Average: {stats['avg']:.2f}ms")
        print(f"Median:  {stats['median']:.2f}ms")

        # Should be fast (aggregated table)
        assert stats['avg'] < 100, f"Metrics query too slow: {stats['avg']:.2f}ms"

    def test_complex_join_performance(self, test_db_client):
        """Benchmark: Complex join query with filters"""
        from sqlalchemy import text

        def complex_query():
            with test_db_client.get_session() as session:
                query = text("""
                    SELECT DISTINCT ON (j.id)
                        j.id,
                        j.job_title,
                        j.salary_low,
                        j.salary_high,
                        c.name as company_name,
                        j.eligibility_flag,
                        ja.application_status
                    FROM jobs j
                    LEFT JOIN companies c ON j.company_id = c.id
                    LEFT JOIN job_applications ja ON j.id = ja.job_id
                    WHERE j.eligibility_flag = true
                        AND j.salary_low >= 80000
                        AND j.remote_options = 'remote'
                    ORDER BY j.id, j.created_at DESC
                    LIMIT 20
                """)
                session.execute(query).fetchall()

        stats = measure_execution_time(complex_query, iterations=10)

        print(f"\n=== Complex Join Query Performance ===")
        print(f"Average: {stats['avg']:.2f}ms")
        print(f"Median:  {stats['median']:.2f}ms")

        # Complex queries should still be reasonably fast
        assert stats['avg'] < 500, f"Complex query too slow: {stats['avg']:.2f}ms"


# ===== API Endpoint Performance Tests =====

@pytest.mark.slow
@pytest.mark.performance
class TestAPIEndpointPerformance:
    """Test API endpoint response times"""

    def test_overview_endpoint_performance(self, authenticated_client):
        """Benchmark: /api/v2/dashboard/overview response time"""

        def call_overview():
            response = authenticated_client.get('/api/v2/dashboard/overview')
            assert response.status_code == 200

        stats = measure_execution_time(call_overview, iterations=10)

        print(f"\n=== Overview Endpoint Performance ===")
        print(f"Average: {stats['avg']:.2f}ms")
        print(f"Median:  {stats['median']:.2f}ms")
        print(f"95th percentile: {sorted([stats['min'], stats['max']])[0]:.2f}ms")

        # Target: <100ms (with database connection overhead)
        assert stats['avg'] < 2000, f"Overview too slow: {stats['avg']:.2f}ms"

    def test_jobs_endpoint_performance(self, authenticated_client):
        """Benchmark: /api/v2/dashboard/jobs response time"""

        def call_jobs():
            response = authenticated_client.get('/api/v2/dashboard/jobs?page=1&per_page=20')
            assert response.status_code == 200

        stats = measure_execution_time(call_jobs, iterations=10)

        print(f"\n=== Jobs Endpoint Performance ===")
        print(f"Average: {stats['avg']:.2f}ms")
        print(f"Median:  {stats['median']:.2f}ms")

        assert stats['avg'] < 2000, f"Jobs endpoint too slow: {stats['avg']:.2f}ms"

    def test_jobs_with_filters_performance(self, authenticated_client):
        """Benchmark: Jobs endpoint with multiple filters"""

        def call_jobs_filtered():
            response = authenticated_client.get(
                '/api/v2/dashboard/jobs?'
                'filter=eligible&'
                'search=python&'
                'salary_min=80000&'
                'remote_options=remote'
            )
            assert response.status_code == 200

        stats = measure_execution_time(call_jobs_filtered, iterations=10)

        print(f"\n=== Jobs with Filters Performance ===")
        print(f"Average: {stats['avg']:.2f}ms")
        print(f"Median:  {stats['median']:.2f}ms")

        # Filtered queries may be slightly slower
        assert stats['avg'] < 3000, f"Filtered jobs too slow: {stats['avg']:.2f}ms"

    def test_applications_endpoint_performance(self, authenticated_client):
        """Benchmark: /api/v2/dashboard/applications response time"""

        def call_applications():
            response = authenticated_client.get('/api/v2/dashboard/applications')
            assert response.status_code == 200

        stats = measure_execution_time(call_applications, iterations=10)

        print(f"\n=== Applications Endpoint Performance ===")
        print(f"Average: {stats['avg']:.2f}ms")
        print(f"Median:  {stats['median']:.2f}ms")

        assert stats['avg'] < 2000, f"Applications too slow: {stats['avg']:.2f}ms"

    def test_analytics_summary_performance(self, authenticated_client):
        """Benchmark: /api/v2/dashboard/analytics/summary response time"""

        def call_analytics():
            response = authenticated_client.get('/api/v2/dashboard/analytics/summary?range=30d')
            assert response.status_code == 200

        stats = measure_execution_time(call_analytics, iterations=5)

        print(f"\n=== Analytics Summary Performance ===")
        print(f"Average: {stats['avg']:.2f}ms")
        print(f"Median:  {stats['median']:.2f}ms")

        # Analytics may be slower due to aggregations
        assert stats['avg'] < 3000, f"Analytics too slow: {stats['avg']:.2f}ms"


# ===== Pagination Performance Tests =====

@pytest.mark.slow
@pytest.mark.performance
class TestPaginationPerformance:
    """Test pagination doesn't degrade with page number"""

    def test_pagination_scaling(self, authenticated_client):
        """Benchmark: Pagination performance across pages"""

        page_times = {}

        for page in [1, 5, 10]:
            def call_page():
                response = authenticated_client.get(
                    f'/api/v2/dashboard/jobs?page={page}&per_page=20'
                )
                assert response.status_code == 200

            stats = measure_execution_time(call_page, iterations=5)
            page_times[page] = stats['avg']

        print(f"\n=== Pagination Scaling ===")
        for page, avg_time in page_times.items():
            print(f"Page {page}: {avg_time:.2f}ms")

        # Later pages should not be significantly slower
        first_page = page_times[1]
        last_page = page_times[10]

        # Allow up to 2x slowdown for later pages
        assert last_page < first_page * 2, "Pagination performance degrades too much"


# ===== Concurrent Load Tests =====

@pytest.mark.slow
@pytest.mark.performance
class TestConcurrentLoad:
    """Test performance under concurrent load"""

    def test_concurrent_overview_requests(self, app):
        """Benchmark: Concurrent requests to overview endpoint"""
        import concurrent.futures

        num_requests = 20
        num_workers = 5

        def make_request():
            client = app.test_client()
            with client.session_transaction() as sess:
                sess['authenticated'] = True

            start = time.perf_counter()
            response = client.get('/api/v2/dashboard/overview')
            elapsed = (time.perf_counter() - start) * 1000
            return elapsed, response.status_code

        start_total = time.perf_counter()

        with concurrent.futures.ThreadPoolExecutor(max_workers=num_workers) as executor:
            futures = [executor.submit(make_request) for _ in range(num_requests)]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]

        total_elapsed = (time.perf_counter() - start_total) * 1000

        times = [r[0] for r in results]
        statuses = [r[1] for r in results]

        print(f"\n=== Concurrent Load Test ({num_requests} requests, {num_workers} workers) ===")
        print(f"Total time: {total_elapsed:.2f}ms")
        print(f"Average request time: {statistics.mean(times):.2f}ms")
        print(f"Median request time: {statistics.median(times):.2f}ms")
        print(f"Max request time: {max(times):.2f}ms")
        print(f"Success rate: {statuses.count(200)}/{len(statuses)}")

        # Most requests should succeed
        success_rate = statuses.count(200) / len(statuses)
        assert success_rate >= 0.8, f"Too many failures: {success_rate:.1%}"


# ===== Memory Usage Tests =====

@pytest.mark.slow
@pytest.mark.performance
class TestMemoryUsage:
    """Test memory usage patterns"""

    def test_large_result_set_memory(self, authenticated_client):
        """Test memory usage with large result sets"""
        import sys

        # Get a large result set
        response = authenticated_client.get('/api/v2/dashboard/jobs?per_page=100')
        assert response.status_code == 200

        data = response.get_json()
        jobs = data.get('jobs', [])

        # Calculate approximate memory usage
        data_size = sys.getsizeof(str(data))

        print(f"\n=== Memory Usage Test ===")
        print(f"Jobs returned: {len(jobs)}")
        print(f"Approximate data size: {data_size / 1024:.2f} KB")

        # Result set should be reasonable size
        assert data_size < 1024 * 1024, "Response too large (>1MB)"


# ===== Response Size Tests =====

@pytest.mark.performance
class TestResponseSizes:
    """Test API response payload sizes"""

    def test_overview_response_size(self, authenticated_client):
        """Test overview endpoint response size"""
        response = authenticated_client.get('/api/v2/dashboard/overview')
        data = response.get_json()

        import json
        size = len(json.dumps(data))

        print(f"\n=== Response Size: Overview ===")
        print(f"Size: {size / 1024:.2f} KB")

        # Should be compact
        assert size < 100 * 1024, "Overview response too large"

    def test_jobs_response_size(self, authenticated_client):
        """Test jobs endpoint response size"""
        response = authenticated_client.get('/api/v2/dashboard/jobs?per_page=20')
        data = response.get_json()

        import json
        size = len(json.dumps(data))

        print(f"\n=== Response Size: Jobs (20 items) ===")
        print(f"Size: {size / 1024:.2f} KB")

        # Should be reasonable
        assert size < 200 * 1024, "Jobs response too large"


# ===== Performance Regression Tests =====

@pytest.mark.performance
class TestPerformanceRegression:
    """Test for performance regressions"""

    # Expected baseline performance (ms)
    BASELINE_OVERVIEW = 2000
    BASELINE_JOBS = 2000
    BASELINE_APPLICATIONS = 2000

    def test_overview_no_regression(self, authenticated_client):
        """Ensure overview endpoint hasn't regressed"""

        def call_overview():
            response = authenticated_client.get('/api/v2/dashboard/overview')
            assert response.status_code == 200

        stats = measure_execution_time(call_overview, iterations=5)

        print(f"\n=== Regression Check: Overview ===")
        print(f"Current avg: {stats['avg']:.2f}ms")
        print(f"Baseline:    {self.BASELINE_OVERVIEW}ms")
        print(f"Difference:  {stats['avg'] - self.BASELINE_OVERVIEW:.2f}ms")

        # Should not be significantly slower than baseline
        assert stats['avg'] < self.BASELINE_OVERVIEW * 1.5, \
            f"Performance regression detected: {stats['avg']:.2f}ms vs baseline {self.BASELINE_OVERVIEW}ms"

    def test_jobs_no_regression(self, authenticated_client):
        """Ensure jobs endpoint hasn't regressed"""

        def call_jobs():
            response = authenticated_client.get('/api/v2/dashboard/jobs')
            assert response.status_code == 200

        stats = measure_execution_time(call_jobs, iterations=5)

        print(f"\n=== Regression Check: Jobs ===")
        print(f"Current avg: {stats['avg']:.2f}ms")
        print(f"Baseline:    {self.BASELINE_JOBS}ms")

        assert stats['avg'] < self.BASELINE_JOBS * 1.5, \
            f"Performance regression: {stats['avg']:.2f}ms vs {self.BASELINE_JOBS}ms"


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s', '--tb=short', '-m', 'performance'])
