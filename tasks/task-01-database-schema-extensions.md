# Task 01: Database Schema Extensions for Link Analytics

**Status:** Ready to Start
**Priority:** High
**Estimated Time:** 2-3 hours
**Dependencies:** None

---

## Objective

Extend the `job_applications` table with engagement metrics fields to support link analytics and create SQL views for correlation analysis.

---

## Tasks

### 1. Extend job_applications Table

Add the following columns to track engagement metrics:

```sql
ALTER TABLE job_applications ADD COLUMN first_click_timestamp TIMESTAMP;
ALTER TABLE job_applications ADD COLUMN total_clicks INTEGER DEFAULT 0;
ALTER TABLE job_applications ADD COLUMN unique_click_sessions INTEGER DEFAULT 0;
ALTER TABLE job_applications ADD COLUMN most_clicked_link_function VARCHAR(100);
ALTER TABLE job_applications ADD COLUMN engagement_score INTEGER DEFAULT 0;
ALTER TABLE job_applications ADD COLUMN last_click_timestamp TIMESTAMP;
```

### 2. Create Analytics Views

#### View: application_engagement_outcomes

```sql
CREATE VIEW application_engagement_outcomes AS
SELECT
  ja.id AS application_id,
  ja.status,
  ja.created_at AS application_date,
  COUNT(lc.click_id) AS total_clicks,
  COUNT(DISTINCT lc.session_id) AS unique_sessions,
  MIN(lc.clicked_at) AS first_click_timestamp,
  MAX(lc.clicked_at) AS last_click_timestamp,
  EXTRACT(EPOCH FROM (MIN(lc.clicked_at) - ja.created_at))/3600 AS hours_to_first_click,
  ARRAY_AGG(DISTINCT lt.link_function ORDER BY lt.link_function) AS clicked_functions,
  MODE() WITHIN GROUP (ORDER BY lt.link_function) AS most_clicked_function
FROM job_applications ja
LEFT JOIN link_tracking lt ON ja.id = lt.application_id
LEFT JOIN link_clicks lc ON lt.tracking_id = lc.tracking_id
GROUP BY ja.id, ja.status, ja.created_at;
```

#### View: link_function_effectiveness

```sql
CREATE VIEW link_function_effectiveness AS
SELECT
  lt.link_function,
  COUNT(DISTINCT lt.application_id) AS applications_with_link,
  COUNT(lc.click_id) AS total_clicks,
  ROUND(COUNT(lc.click_id)::NUMERIC / NULLIF(COUNT(DISTINCT lt.application_id), 0), 2) AS avg_clicks_per_application,
  COUNT(DISTINCT CASE WHEN ja.status = 'interview' THEN ja.id END) AS interviews_generated,
  COUNT(DISTINCT CASE WHEN ja.status = 'offer' THEN ja.id END) AS offers_generated,
  ROUND(100.0 * COUNT(DISTINCT CASE WHEN ja.status IN ('interview', 'offer') THEN ja.id END) /
    NULLIF(COUNT(DISTINCT lt.application_id), 0), 2) AS interview_conversion_rate
FROM link_tracking lt
LEFT JOIN link_clicks lc ON lt.tracking_id = lc.tracking_id
LEFT JOIN job_applications ja ON lt.application_id = ja.id
WHERE lt.is_active = true
GROUP BY lt.link_function
ORDER BY interview_conversion_rate DESC NULLS LAST;
```

### 3. Create Migration Script

Create `database_migrations/add_engagement_metrics.sql` with all DDL statements.

### 4. Backfill Existing Data

Create a data population script to calculate engagement metrics for existing applications:

```sql
-- Backfill engagement metrics for existing applications
UPDATE job_applications ja
SET
  first_click_timestamp = subq.first_click,
  last_click_timestamp = subq.last_click,
  total_clicks = subq.total_clicks,
  unique_click_sessions = subq.unique_sessions
FROM (
  SELECT
    lt.application_id,
    MIN(lc.clicked_at) AS first_click,
    MAX(lc.clicked_at) AS last_click,
    COUNT(lc.click_id) AS total_clicks,
    COUNT(DISTINCT lc.session_id) AS unique_sessions
  FROM link_tracking lt
  LEFT JOIN link_clicks lc ON lt.tracking_id = lc.tracking_id
  WHERE lt.application_id IS NOT NULL
  GROUP BY lt.application_id
) subq
WHERE ja.id = subq.application_id;
```

---

## Validation

- [ ] All columns added successfully
- [ ] Views created without errors
- [ ] Views return data for existing applications
- [ ] Backfill script updates existing records
- [ ] No performance degradation on job_applications queries
- [ ] Run automated schema documentation update: `python database_tools/update_schema.py`

---

## Deliverables

1. Migration SQL file: `database_migrations/add_engagement_metrics.sql`
2. Backfill script: `database_migrations/backfill_engagement_data.sql`
3. Validation queries to verify data integrity
4. Updated database schema documentation

---

## Notes

- Test on development database before production
- Create database backup before running migrations
- Monitor query performance on large datasets
- Document any assumptions about data quality
