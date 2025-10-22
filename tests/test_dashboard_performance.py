#!/usr/bin/env python3
"""
Test dashboard performance improvements after migration fixes
"""

import os
import time
import psycopg2
import json
from datetime import datetime, timedelta

# Determine host based on environment
host = 'host.docker.internal' if os.path.exists('/.dockerenv') else 'localhost'

# Database connection
conn = psycopg2.connect(
    host=host,
    database='local_Merlin_3',
    user='postgres',
    password='goldmember',
    port='5432'
)

def time_query(cursor, query, description):
    """Time a query execution"""
    start = time.time()
    cursor.execute(query)
    results = cursor.fetchall()
    elapsed = (time.time() - start) * 1000  # Convert to milliseconds
    return elapsed, len(results)

print("=" * 80)
print("DASHBOARD PERFORMANCE TESTING")
print("=" * 80)

cursor = conn.cursor()

# Test 1: Recent Applications Query (OLD vs NEW)
print("\n1. RECENT APPLICATIONS QUERY")
print("-" * 40)

# OLD: Direct JOIN query
old_query = """
    SELECT
        ja.id,
        ja.created_at,
        ja.application_status,
        j.job_title,
        j.salary_low,
        j.salary_high,
        c.name as company_name
    FROM job_applications ja
    LEFT JOIN jobs j ON ja.job_id = j.id
    LEFT JOIN companies c ON j.company_id = c.id
    WHERE ja.created_at >= NOW() - INTERVAL '30 days'
    ORDER BY ja.created_at DESC
    LIMIT 20
"""

# NEW: Materialized view query
new_query = """
    SELECT
        application_id,
        created_at,
        application_status,
        job_title,
        salary_low,
        salary_high,
        company_name
    FROM application_summary_mv
    WHERE created_at >= NOW() - INTERVAL '30 days'
    ORDER BY created_at DESC
    LIMIT 20
"""

old_time, old_count = time_query(cursor, old_query, "Direct JOIN")
new_time, new_count = time_query(cursor, new_query, "Materialized View")

improvement = ((old_time - new_time) / old_time) * 100 if old_time > 0 else 0

print(f"  OLD (Direct JOIN):      {old_time:8.2f}ms ({old_count} rows)")
print(f"  NEW (Materialized View): {new_time:8.2f}ms ({new_count} rows)")
print(f"  IMPROVEMENT:            {improvement:8.1f}% faster")

# Test 2: Dashboard Metrics Query
print("\n2. DASHBOARD METRICS AGGREGATION")
print("-" * 40)

# Test if aggregation tables work
metrics_query = """
    SELECT
        metric_date,
        jobs_scraped_count,
        applications_sent_count,
        success_rate
    FROM dashboard_metrics_daily
    WHERE metric_date >= CURRENT_DATE - INTERVAL '7 days'
    ORDER BY metric_date DESC
"""

try:
    metrics_time, metrics_count = time_query(cursor, metrics_query, "Aggregation Table")
    print(f"  Aggregation Query:      {metrics_time:8.2f}ms ({metrics_count} rows)")
    if metrics_count == 0:
        print("  Note: No aggregated data yet - needs backfill")
except Exception as e:
    print(f"  Error: {e}")

# Test 3: Company Statistics Query
print("\n3. COMPANY STATISTICS QUERY")
print("-" * 40)

company_stats_query = """
    SELECT
        company_name,
        COUNT(*) as application_count,
        COUNT(DISTINCT job_id) as unique_jobs,
        AVG(salary_high) as avg_salary_high
    FROM application_summary_mv
    WHERE company_name IS NOT NULL
    GROUP BY company_name
    ORDER BY application_count DESC
    LIMIT 10
"""

stats_time, stats_count = time_query(cursor, company_stats_query, "Company Stats")
print(f"  Company Stats Query:    {stats_time:8.2f}ms ({stats_count} companies)")

# Test 4: Status Distribution Query
print("\n4. STATUS DISTRIBUTION QUERY")
print("-" * 40)

status_query = """
    SELECT
        application_status,
        COUNT(*) as count
    FROM application_summary_mv
    GROUP BY application_status
    ORDER BY count DESC
"""

status_time, status_count = time_query(cursor, status_query, "Status Distribution")
print(f"  Status Distribution:    {status_time:8.2f}ms ({status_count} statuses)")

# Test 5: Test Index Usage
print("\n5. INDEX USAGE ANALYSIS")
print("-" * 40)

cursor.execute("""
    SELECT
        schemaname,
        tablename,
        indexname,
        idx_scan,
        idx_tup_read,
        idx_tup_fetch
    FROM pg_stat_user_indexes
    WHERE schemaname = 'public'
    AND tablename IN ('jobs', 'job_applications', 'application_summary_mv')
    AND idx_scan > 0
    ORDER BY idx_scan DESC
    LIMIT 10
""")

print("  Most Used Indexes:")
for row in cursor.fetchall():
    print(f"    - {row[2]:40s} Scans: {row[3]:6d}")

# Performance Summary
print("\n" + "=" * 80)
print("PERFORMANCE SUMMARY")
print("=" * 80)

total_old_time = old_time
total_new_time = new_time + stats_time + status_time
overall_improvement = ((total_old_time - total_new_time) / total_old_time * 100) if total_old_time > 0 else 0

print(f"\nQuery Performance Improvements:")
print(f"  • Recent Applications:  {improvement:5.1f}% faster")
print(f"  • Query Time:          {old_time:6.2f}ms → {new_time:6.2f}ms")

if new_time < 50:
    print(f"\n✓ EXCELLENT: Dashboard queries execute in under 50ms")
    print(f"  This meets performance requirements for responsive UI")
elif new_time < 100:
    print(f"\n✓ GOOD: Dashboard queries execute in under 100ms")
    print(f"  Acceptable performance for most use cases")
else:
    print(f"\n⚠ WARNING: Dashboard queries take {new_time:.2f}ms")
    print(f"  Consider additional optimization")

# Test refresh function
print("\n" + "=" * 80)
print("TESTING REFRESH FUNCTION")
print("=" * 80)

try:
    start = time.time()
    cursor.execute("SELECT refresh_application_summary()")
    refresh_time = (time.time() - start) * 1000
    print(f"✓ Materialized view refresh completed in {refresh_time:.2f}ms")
except Exception as e:
    print(f"✗ Refresh failed: {e}")

cursor.close()
conn.close()

print("\n" + "=" * 80)
print("✓ PERFORMANCE TESTING COMPLETE")
print("=" * 80)