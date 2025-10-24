---
title: "Api Endpoint Reference"
type: api_spec
component: general
status: draft
tags: []
---

# Link Tracking API Endpoint Reference

**Version**: 2.16.5  
**Date**: July 27, 2025  
**Base URL**: `https://automated-job-application-system.replit.app`

## Authentication

All API requests require authentication:

```http
Authorization: Bearer YOUR_API_KEY
Content-Type: application/json
```

## Core API Endpoints

### 1. Record Click Event

**Endpoint**: `POST /api/link-tracking/record-click`

Record a click event when a user clicks a tracked link.

**Request Body**:
```json
{
  "tracking_id": "lt_abc123def456",
  "clicked_at": "2025-07-27T21:15:30Z",
  "ip_address": "192.168.1.100",
  "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
  "referrer_url": "https://gmail.com",
  "session_id": "sess_xyz789",
  "click_source": "email",
  "metadata": {
    "utm_source": "email",
    "utm_medium": "application",
    "utm_campaign": "job_search"
  }
}
```

**Response** (201 Created):
```json
{
  "click_id": "550e8400-e29b-41d4-a716-446655440002",
  "tracking_id": "lt_abc123def456",
  "clicked_at": "2025-07-27T21:15:30Z",
  "click_source": "email",
  "status": "recorded"
}
```

### 2. Get Link Information

**Endpoint**: `GET /api/link-tracking/analytics/{tracking_id}`

Get comprehensive information about a tracked link.

**Response** (200 OK):
```json
{
  "link_info": {
    "tracking_id": "lt_abc123def456",
    "job_id": "550e8400-e29b-41d4-a716-446655440000",
    "application_id": "550e8400-e29b-41d4-a716-446655440001",
    "link_function": "LinkedIn",
    "link_type": "profile",
    "original_url": "https://linkedin.com/in/steve-glen",
    "redirect_url": "https://yourdomain.com/track/lt_abc123def456",
    "created_at": "2025-07-27T21:00:00Z",
    "is_active": true,
    "description": "Professional LinkedIn profile"
  },
  "click_statistics": {
    "total_clicks": 15,
    "unique_sessions": 8,
    "first_click": "2025-07-27T21:00:00Z",
    "last_click": "2025-07-27T21:30:00Z",
    "clicks_24h": 5,
    "clicks_7d": 15
  },
  "click_timeline": [
    {
      "clicked_at": "2025-07-27T21:30:00Z",
      "click_source": "email",
      "ip_address": "192.168.1.100"
    }
  ]
}
```

### 3. Create Tracked Link

**Endpoint**: `POST /api/link-tracking/create`

Create a new tracked link with job/application association.

**Request Body**:
```json
{
  "original_url": "https://linkedin.com/in/steve-glen",
  "link_function": "LinkedIn",
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "application_id": "550e8400-e29b-41d4-a716-446655440001",
  "link_type": "profile",
  "description": "Professional LinkedIn profile"
}
```

**Response** (201 Created):
```json
{
  "tracking_id": "lt_abc123def456",
  "redirect_url": "https://yourdomain.com/track/lt_abc123def456",
  "original_url": "https://linkedin.com/in/steve-glen",
  "link_function": "LinkedIn",
  "link_type": "profile",
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "application_id": "550e8400-e29b-41d4-a716-446655440001",
  "created_at": "2025-07-27T21:00:00Z"
}
```

### 4. Get Job Links Summary

**Endpoint**: `GET /api/link-tracking/job/{job_id}/links`

Get all tracked links associated with a specific job.

**Response** (200 OK):
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "link_functions": [
    {
      "link_function": "LinkedIn",
      "link_type": "profile",
      "link_count": 1,
      "total_clicks": 15,
      "unique_sessions": 8,
      "first_click": "2025-07-27T21:00:00Z",
      "last_click": "2025-07-27T21:30:00Z"
    },
    {
      "link_function": "Calendly",
      "link_type": "networking",
      "link_count": 1,
      "total_clicks": 5,
      "unique_sessions": 3,
      "first_click": "2025-07-27T21:05:00Z",
      "last_click": "2025-07-27T21:25:00Z"
    }
  ],
  "total_links": 2,
  "total_clicks": 20,
  "unique_sessions": 11
}
```

### 5. Get Application Links Summary

**Endpoint**: `GET /api/link-tracking/application/{application_id}/links`

Get all tracked links for a specific application.

**Response** (200 OK):
```json
{
  "application_id": "550e8400-e29b-41d4-a716-446655440001",
  "tracked_links": [
    {
      "link_function": "LinkedIn",
      "tracking_id": "lt_abc123def456",
      "original_url": "https://linkedin.com/in/steve-glen",
      "description": "Professional LinkedIn profile",
      "click_count": 15,
      "first_click": "2025-07-27T21:00:00Z",
      "last_click": "2025-07-27T21:30:00Z"
    }
  ],
  "total_tracked_links": 1,
  "total_clicks": 15
}
```

### 6. Create Application Link Package

**Endpoint**: `POST /api/link-tracking/application/create-links`

Create standard tracked links for a complete job application.

**Request Body**:
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "application_id": "550e8400-e29b-41d4-a716-446655440001",
  "job_data": {
    "company_website": "https://company.com",
    "apply_url": "https://company.com/apply",
    "job_url": "https://indeed.com/job/123"
  }
}
```

**Response** (201 Created):
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "application_id": "550e8400-e29b-41d4-a716-446655440001",
  "tracked_links": {
    "LinkedIn": "https://yourdomain.com/track/lt_linkedin123",
    "Calendly": "https://yourdomain.com/track/lt_calendly456",
    "Company_Website": "https://yourdomain.com/track/lt_company789",
    "Apply_Now": "https://yourdomain.com/track/lt_apply012",
    "Job_Posting": "https://yourdomain.com/track/lt_jobpost345"
  },
  "total_links": 5
}
```

### 7. Generate Performance Report

**Endpoint**: `GET /api/link-tracking/report?days=30`

Generate comprehensive link performance analytics.

**Query Parameters**:
- `days` (optional): Number of days to include (default: 30)

**Response** (200 OK):
```json
{
  "report_period": {
    "start_date": "2025-06-27T21:00:00Z",
    "end_date": "2025-07-27T21:00:00Z",
    "days": 30
  },
  "overall_statistics": {
    "total_links": 150,
    "jobs_with_links": 25,
    "applications_with_links": 20,
    "total_clicks": 450
  },
  "function_performance": [
    {
      "link_function": "LinkedIn",
      "link_count": 25,
      "total_clicks": 200,
      "avg_clicks_per_link": 8.0
    },
    {
      "link_function": "Calendly",
      "link_count": 25,
      "total_clicks": 100,
      "avg_clicks_per_link": 4.0
    }
  ],
  "daily_trends": [
    {
      "click_date": "2025-07-27",
      "clicks": 45
    }
  ]
}
```

### 8. Deactivate Link

**Endpoint**: `POST /api/link-tracking/deactivate/{tracking_id}`

Deactivate a tracked link to stop tracking clicks.

**Response** (200 OK):
```json
{
  "message": "Link deactivated successfully",
  "tracking_id": "lt_abc123def456",
  "deactivated_at": "2025-07-27T21:30:00Z"
}
```

## Redirect Endpoints (External Domain)

### 1. Link Redirect Handler

**Endpoint**: `GET /track/{tracking_id}`

Handle link redirect and record click event.

**Example URL**: `https://yourdomain.com/track/lt_abc123def456`

**Response**: HTTP 302 Redirect to original URL

### 2. Health Check

**Endpoint**: `GET /track/health`

Check redirect system health.

**Response** (200 OK):
```json
{
  "status": "healthy",
  "service": "link_redirect_handler",
  "version": "2.16.5"
}
```

## Required Request Headers

### Standard Headers
```http
Content-Type: application/json
Authorization: Bearer YOUR_API_KEY
User-Agent: ExternalDomain/1.0
```

### Optional Analytics Headers
```http
X-Forwarded-For: 192.168.1.100
X-Real-IP: 192.168.1.100
Referer: https://gmail.com
```

## Error Response Formats

### 400 Bad Request
```json
{
  "error": "Missing required field: tracking_id",
  "required_fields": ["tracking_id", "clicked_at"],
  "timestamp": "2025-07-27T21:30:00Z"
}
```

### 401 Unauthorized
```json
{
  "error": "Invalid API key",
  "message": "Please provide a valid authorization token",
  "timestamp": "2025-07-27T21:30:00Z"
}
```

### 404 Not Found
```json
{
  "error": "Link not found or expired",
  "tracking_id": "lt_abc123def456",
  "timestamp": "2025-07-27T21:30:00Z"
}
```

### 500 Internal Server Error
```json
{
  "error": "Internal server error",
  "message": "Database connection failed",
  "request_id": "req_xyz789",
  "timestamp": "2025-07-27T21:30:00Z"
}
```

## Rate Limiting

### API Rate Limits
- **Click Recording**: 1000 requests/minute per IP
- **Analytics**: 100 requests/minute per API key
- **Link Creation**: 50 requests/minute per API key

### Rate Limit Headers
```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 995
X-RateLimit-Reset: 1648834800
```

### Rate Limit Exceeded Response
```json
{
  "error": "Rate limit exceeded",
  "limit": 1000,
  "window": "1 minute",
  "retry_after": 60,
  "timestamp": "2025-07-27T21:30:00Z"
}
```

## Database Connection Info (Alternative)

For direct database integration instead of API:

```
Host: automated-job-application-system-db.replit.app
Database: job_application_system
User: link_tracking_user
Password: [provided_separately]
Port: 5432
SSL: require
```

### Required Tables Access
- `link_tracking` (read)
- `link_clicks` (write)

### Required Permissions
```sql
GRANT SELECT ON link_tracking TO link_tracking_user;
GRANT INSERT ON link_clicks TO link_tracking_user;
```