#!/usr/bin/env python3
"""Check database schema for migration issues"""

import os
import psycopg2
from psycopg2 import sql

# Determine host based on environment
host = 'host.docker.internal' if os.path.exists('/.dockerenv') else 'localhost'
print(f"Using database host: {host}\n")

# Database connection
conn = psycopg2.connect(
    host=host,
    database='local_Merlin_3',
    user='postgres',
    password='goldmember',
    port='5432'
)

cursor = conn.cursor()

# Check jobs table schema
print("=" * 80)
print("JOBS TABLE SCHEMA:")
print("=" * 80)

cursor.execute("""
    SELECT column_name, data_type, is_nullable, column_default
    FROM information_schema.columns
    WHERE table_name = 'jobs'
    ORDER BY ordinal_position
""")

columns = cursor.fetchall()
for col in columns:
    print(f"  {col[0]:30s} {col[1]:20s} {col[2]:5s} {col[3] or ''}")

print("\n" + "=" * 80)
print("CHECKING FOR MIGRATION COLUMN ISSUES:")
print("=" * 80)

# Check for columns referenced in migrations
columns_to_check = [
    ('jobs', 'priority_score'),
    ('jobs', 'salary_currency'),
    ('jobs', 'compensation_currency'),
    ('jobs', 'location'),
    ('jobs', 'office_city'),
    ('jobs', 'office_province'),
    ('jobs', 'office_country'),
    ('jobs', 'experience_level'),
    ('jobs', 'seniority_level')
]

existing_columns = {col[0] for col in columns}

for table, column in columns_to_check:
    exists = column in existing_columns
    status = "✓ EXISTS" if exists else "✗ MISSING"
    print(f"  {table}.{column:30s} {status}")

print("\n" + "=" * 80)
print("CHECKING EXISTING MATERIALIZED VIEWS:")
print("=" * 80)

cursor.execute("""
    SELECT matviewname
    FROM pg_matviews
    WHERE schemaname = 'public'
""")

matviews = cursor.fetchall()
if matviews:
    for mv in matviews:
        print(f"  - {mv[0]}")
else:
    print("  No materialized views found")

print("\n" + "=" * 80)
print("CHECKING EXISTING AGGREGATION TABLES:")
print("=" * 80)

cursor.execute("""
    SELECT tablename
    FROM pg_tables
    WHERE schemaname = 'public'
    AND tablename LIKE 'dashboard_metrics_%'
""")

agg_tables = cursor.fetchall()
if agg_tables:
    for table in agg_tables:
        print(f"  - {table[0]}")
else:
    print("  No aggregation tables found")

cursor.close()
conn.close()

print("\n" + "=" * 80)
print("SCHEMA CHECK COMPLETE")
print("=" * 80)