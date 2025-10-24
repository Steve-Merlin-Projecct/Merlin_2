---
title: "Database Schema Reference"
type: reference
component: database
status: draft
tags: []
---

# Link Tracking Database Schema Reference

**Version**: 2.16.5  
**Date**: July 27, 2025  
**Purpose**: Database schema reference for external domain integration

## Overview

This document provides the complete database schema for implementing link tracking functionality on external domains. The schema supports job associations, application tracking, and comprehensive click analytics.

## Core Tables

### 1. link_tracking Table

Primary table for storing tracked link metadata and associations.

```sql
CREATE TABLE link_tracking (
    tracking_id VARCHAR(100) PRIMARY KEY,
    job_id UUID NULL,
    application_id UUID NULL,
    link_function VARCHAR(50) NOT NULL,
    link_type VARCHAR(50) NOT NULL,
    original_url VARCHAR(1000) NOT NULL,
    redirect_url VARCHAR(1000) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(100) DEFAULT 'system',
    is_active BOOLEAN DEFAULT TRUE,
    description TEXT NULL,
    
    -- Foreign key constraints
    CONSTRAINT fk_link_tracking_job 
        FOREIGN KEY (job_id) REFERENCES jobs(id) ON DELETE SET NULL,
    CONSTRAINT fk_link_tracking_application 
        FOREIGN KEY (application_id) REFERENCES job_applications(id) ON DELETE SET NULL
);
```

#### Column Specifications

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `tracking_id` | VARCHAR(100) | NO | - | Unique identifier for the tracked link |
| `job_id` | UUID | YES | NULL | Associated job UUID |
| `application_id` | UUID | YES | NULL | Associated application UUID |
| `link_function` | VARCHAR(50) | NO | - | Function type (LinkedIn, Calendly, etc.) |
| `link_type` | VARCHAR(50) | NO | - | Category (profile, job_posting, etc.) |
| `original_url` | VARCHAR(1000) | NO | - | Destination URL |
| `redirect_url` | VARCHAR(1000) | NO | - | Tracking URL |
| `created_at` | TIMESTAMP | YES | CURRENT_TIMESTAMP | Link creation time |
| `created_by` | VARCHAR(100) | YES | 'system' | Creator identifier |
| `is_active` | BOOLEAN | YES | TRUE | Whether link is active |
| `description` | TEXT | YES | NULL | Human-readable description |

#### Indexes

```sql
CREATE INDEX idx_link_tracking_job_id ON link_tracking(job_id);
CREATE INDEX idx_link_tracking_application_id ON link_tracking(application_id);
CREATE INDEX idx_link_tracking_function ON link_tracking(link_function);
CREATE INDEX idx_link_tracking_active ON link_tracking(is_active);
CREATE INDEX idx_link_tracking_created_at ON link_tracking(created_at);
```

### 2. link_clicks Table

Table for recording individual click events on tracked links.

```sql
CREATE TABLE link_clicks (
    click_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tracking_id VARCHAR(100) NOT NULL,
    clicked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ip_address INET NULL,
    user_agent TEXT NULL,
    referrer_url VARCHAR(1000) NULL,
    session_id VARCHAR(100) NULL,
    click_source VARCHAR(50) NULL,
    metadata JSONB DEFAULT '{}',
    
    -- Foreign key constraint
    CONSTRAINT fk_link_clicks_tracking 
        FOREIGN KEY (tracking_id) REFERENCES link_tracking(tracking_id) ON DELETE CASCADE
);
```

#### Column Specifications

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `click_id` | UUID | NO | gen_random_uuid() | Unique click identifier |
| `tracking_id` | VARCHAR(100) | NO | - | Reference to tracked link |
| `clicked_at` | TIMESTAMP | YES | CURRENT_TIMESTAMP | Click timestamp |
| `ip_address` | INET | YES | NULL | Client IP address |
| `user_agent` | TEXT | YES | NULL | Browser user agent |
| `referrer_url` | VARCHAR(1000) | YES | NULL | Referring page URL |
| `session_id` | VARCHAR(100) | YES | NULL | User session identifier |
| `click_source` | VARCHAR(50) | YES | NULL | Click source category |
| `metadata` | JSONB | YES | '{}' | Additional click metadata |

#### Indexes

```sql
CREATE INDEX idx_link_clicks_tracking_id ON link_clicks(tracking_id);
CREATE INDEX idx_link_clicks_clicked_at ON link_clicks(clicked_at);
CREATE INDEX idx_link_clicks_source ON link_clicks(click_source);
CREATE INDEX idx_link_clicks_ip_address ON link_clicks(ip_address);
CREATE INDEX idx_link_clicks_session_id ON link_clicks(session_id);
```

## Enum Values and Constants

### Link Functions

Standard link function values:

```sql
-- Common link_function values
'LinkedIn'         -- Professional profile links
'Calendly'         -- Meeting scheduling links
'Company_Website'  -- Company homepage
'Apply_Now'        -- Direct application links
'Job_Posting'      -- Original job listing
'Portfolio'        -- Personal portfolio
'GitHub'           -- Code repository
'Resume'           -- Resume document
'Cover_Letter'     -- Cover letter document
'References'       -- Professional references
```

### Link Types

Standard link type categories:

```sql
-- Common link_type values
'profile'          -- Personal/professional profiles
'job_posting'      -- Job-related content
'application'      -- Application process links
'networking'       -- Professional networking
'document'         -- Document downloads
'external'         -- External websites
'internal'         -- Internal system links
```

### Click Sources

Standard click source categories:

```sql
-- Common click_source values
'email'            -- Email clients (Gmail, Outlook)
'dashboard'        -- Application dashboard
'linkedin'         -- LinkedIn platform
'indeed'           -- Indeed job board
'direct'           -- Direct URL access
'external'         -- Other external websites
'api'              -- API-generated clicks
'test'             -- Testing/development
```

## Data Relationships

### Primary Relationships

```
jobs (1) → (0..n) link_tracking
job_applications (1) → (0..n) link_tracking
link_tracking (1) → (0..n) link_clicks
```

### Relationship Details

#### Jobs to Link Tracking
- One job can have multiple tracked links
- Links can exist without job association (job_id = NULL)
- Deleting job sets link_tracking.job_id to NULL

#### Applications to Link Tracking
- One application can have multiple tracked links
- Links can exist without application association (application_id = NULL)
- Deleting application sets link_tracking.application_id to NULL

#### Link Tracking to Link Clicks
- One tracked link can have many click events
- Deleting tracked link removes all associated clicks (CASCADE)
- Each click must have a valid tracking_id

## Sample Data

### Sample link_tracking Records

```sql
INSERT INTO link_tracking (
    tracking_id, job_id, application_id, link_function, 
    link_type, original_url, redirect_url, description
) VALUES 
(
    'lt_linkedin_001',
    '550e8400-e29b-41d4-a716-446655440000',
    '550e8400-e29b-41d4-a716-446655440001',
    'LinkedIn',
    'profile',
    'https://linkedin.com/in/steve-glen',
    'https://yourdomain.com/track/lt_linkedin_001',
    'Professional LinkedIn profile'
),
(
    'lt_calendly_002',
    '550e8400-e29b-41d4-a716-446655440000',
    '550e8400-e29b-41d4-a716-446655440001',
    'Calendly',
    'networking',
    'https://calendly.com/steve-glen/30min',
    'https://yourdomain.com/track/lt_calendly_002',
    'Schedule interview meeting'
);
```

### Sample link_clicks Records

```sql
INSERT INTO link_clicks (
    tracking_id, clicked_at, ip_address, user_agent, 
    referrer_url, session_id, click_source, metadata
) VALUES 
(
    'lt_linkedin_001',
    '2025-07-27 21:15:30',
    '192.168.1.100',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'https://gmail.com',
    'sess_abc123',
    'email',
    '{"utm_source": "email", "utm_medium": "application"}'::jsonb
),
(
    'lt_calendly_002',
    '2025-07-27 21:20:15',
    '192.168.1.101',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
    'https://linkedin.com',
    'sess_xyz789',
    'linkedin',
    '{"utm_campaign": "networking"}'::jsonb
);
```

## Common Queries

### 1. Get Link Information for Redirect

```sql
SELECT 
    original_url,
    is_active,
    job_id,
    application_id,
    link_function
FROM link_tracking 
WHERE tracking_id = $1 AND is_active = TRUE;
```

### 2. Record Click Event

```sql
INSERT INTO link_clicks (
    tracking_id, clicked_at, ip_address, user_agent,
    referrer_url, session_id, click_source, metadata
) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
RETURNING click_id, clicked_at;
```

### 3. Get Link Analytics

```sql
SELECT 
    lt.*,
    COUNT(lc.click_id) as total_clicks,
    COUNT(DISTINCT lc.session_id) as unique_sessions,
    MIN(lc.clicked_at) as first_click,
    MAX(lc.clicked_at) as last_click
FROM link_tracking lt
LEFT JOIN link_clicks lc ON lt.tracking_id = lc.tracking_id
WHERE lt.tracking_id = $1
GROUP BY lt.tracking_id;
```

### 4. Get Job Link Summary

```sql
SELECT 
    lt.link_function,
    COUNT(DISTINCT lt.tracking_id) as link_count,
    COUNT(lc.click_id) as total_clicks,
    COUNT(DISTINCT lc.session_id) as unique_sessions
FROM link_tracking lt
LEFT JOIN link_clicks lc ON lt.tracking_id = lc.tracking_id
WHERE lt.job_id = $1 AND lt.is_active = TRUE
GROUP BY lt.link_function
ORDER BY total_clicks DESC;
```

### 5. Get Click Timeline

```sql
SELECT 
    clicked_at,
    click_source,
    ip_address,
    referrer_url,
    metadata
FROM link_clicks
WHERE tracking_id = $1
ORDER BY clicked_at DESC
LIMIT 50;
```

## Performance Optimization

### Recommended Indexes

```sql
-- Primary performance indexes
CREATE INDEX idx_link_tracking_job_active ON link_tracking(job_id, is_active);
CREATE INDEX idx_link_tracking_app_active ON link_tracking(application_id, is_active);
CREATE INDEX idx_link_clicks_tracking_time ON link_clicks(tracking_id, clicked_at);

-- Analytics indexes
CREATE INDEX idx_link_clicks_source_time ON link_clicks(click_source, clicked_at);
CREATE INDEX idx_link_clicks_session_tracking ON link_clicks(session_id, tracking_id);

-- Composite indexes for common queries
CREATE INDEX idx_link_tracking_composite ON link_tracking(is_active, link_function, created_at);
```

### Query Optimization Tips

1. **Use specific WHERE clauses**: Always filter by `is_active = TRUE` for active links
2. **Limit result sets**: Use LIMIT for pagination and large datasets
3. **Index foreign keys**: Ensure job_id and application_id are indexed
4. **Partition by date**: Consider partitioning link_clicks by clicked_at for large datasets

### Storage Considerations

- **link_tracking**: Estimated 50-100 bytes per record
- **link_clicks**: Estimated 200-500 bytes per record depending on metadata
- **Retention**: Consider archiving clicks older than 2 years
- **Compression**: Enable PostgreSQL compression for TEXT/JSONB fields

## Security Considerations

### Data Access Control

```sql
-- Create read-only user for external domains
CREATE USER link_tracker_readonly WITH PASSWORD 'secure_password';
GRANT SELECT ON link_tracking TO link_tracker_readonly;

-- Create insert-only user for click recording
CREATE USER click_recorder WITH PASSWORD 'secure_password';
GRANT SELECT ON link_tracking TO click_recorder;
GRANT INSERT ON link_clicks TO click_recorder;
```

### Data Privacy

```sql
-- Anonymize IP addresses after 90 days
UPDATE link_clicks 
SET ip_address = NULL 
WHERE clicked_at < NOW() - INTERVAL '90 days';

-- Create anonymized view for analytics
CREATE VIEW link_analytics_view AS
SELECT 
    tracking_id,
    clicked_at,
    click_source,
    CASE WHEN clicked_at > NOW() - INTERVAL '90 days' 
         THEN ip_address 
         ELSE NULL END as ip_address
FROM link_clicks;
```

## Backup and Maintenance

### Regular Maintenance Tasks

```sql
-- Clean up old clicks (optional, based on retention policy)
DELETE FROM link_clicks 
WHERE clicked_at < NOW() - INTERVAL '2 years';

-- Update statistics for query optimization
ANALYZE link_tracking;
ANALYZE link_clicks;

-- Reindex for performance
REINDEX TABLE link_tracking;
REINDEX TABLE link_clicks;
```

### Backup Strategy

1. **Daily backups**: Full database backup including both tables
2. **Real-time replication**: Consider read replicas for analytics
3. **Point-in-time recovery**: Enable WAL archiving for PostgreSQL
4. **Export for analytics**: Regular exports to data warehouse

## Migration Scripts

### Initial Setup

```sql
-- Run this script to set up link tracking tables
BEGIN;

-- Create tables
CREATE TABLE link_tracking (...);  -- Full schema above
CREATE TABLE link_clicks (...);    -- Full schema above

-- Create indexes
CREATE INDEX idx_link_tracking_job_id ON link_tracking(job_id);
-- ... all other indexes

-- Create constraints
ALTER TABLE link_tracking ADD CONSTRAINT fk_link_tracking_job 
    FOREIGN KEY (job_id) REFERENCES jobs(id) ON DELETE SET NULL;
-- ... other constraints

COMMIT;
```

### Version Upgrades

```sql
-- Example: Adding new column for enhanced tracking
ALTER TABLE link_clicks ADD COLUMN browser_fingerprint VARCHAR(64);
CREATE INDEX idx_link_clicks_fingerprint ON link_clicks(browser_fingerprint);
```