---
title: "Api Documentation"
type: api_spec
component: general
status: draft
tags: []
---

# API Documentation - Automated Job Application System

**Version:** 4.2.0
**Last Updated:** October 9, 2025

## Overview

This document provides comprehensive documentation for all API endpoints in the Automated Job Application System.

## Base URL

```
Development: http://localhost:5000
Production: [To be configured]
```

## Authentication

Most API endpoints require authentication using one of the following methods:

### 1. API Key Authentication
```bash
X-API-Key: <your-webhook-api-key>
```

### 2. Session Authentication
- Dashboard endpoints use session-based authentication
- Login via `/dashboard/authenticate`

### 3. Bearer Token (Link Tracking)
```bash
Authorization: Bearer <api-key>
```

---

## Core Endpoints

### Health & Status

#### `GET /health`
**Description:** System health check
**Authentication:** None
**Response:**
```json
{
  "status": "healthy",
  "service": "Merlin Job Application System",
  "version": "4.2.0"
}
```

#### `GET /`
**Description:** Service information and available endpoints
**Authentication:** None
**Response:** JSON with service details and endpoint documentation

---

## Database API (`/api/db/*`)

### `GET /api/db/health`
**Description:** Database health check
**Authentication:** None
**Response:**
```json
{
  "status": "healthy",
  "database_connected": true,
  "total_jobs": 6,
  "success_rate": 50.0,
  "timestamp": "2025-10-09T01:47:51.187712"
}
```

### `GET /api/db/jobs`
**Description:** List jobs with optional filtering
**Authentication:** API Key required
**Query Parameters:**
- `limit` (optional): Number of jobs to return (default: 20)
- `status` (optional): Filter by status
- `document_type` (optional): Filter by document type
- `search` (optional): Search term for title/author/filename

### `GET /api/db/jobs/<job_id>`
**Description:** Get specific job by ID
**Authentication:** API Key required

### `GET /api/db/settings`
**Description:** Get application settings
**Authentication:** API Key required

### `GET /api/db/raw-scrapes`
**Description:** Get raw job scrape data
**Authentication:** API Key required

---

## AI Analysis API (`/api/ai/*`)

### `GET /api/ai/health`
**Description:** AI service health check
**Authentication:** None

### `GET /api/ai/usage-stats`
**Description:** Get AI usage statistics
**Authentication:** API Key required
**Requirements:** GEMINI_API_KEY environment variable

### `POST /api/ai/analyze-jobs`
**Description:** Analyze job postings with AI
**Authentication:** API Key required

### `GET /api/ai/analysis-results/<job_id>`
**Description:** Get analysis results for specific job
**Authentication:** API Key required

---

## Email Integration API (`/api/email/*`)

### `GET /api/email/oauth/status`
**Description:** Gmail OAuth authentication status
**Authentication:** None (Returns public status)
**Response:**
```json
{
  "status": "unknown",
  "email": "unknown"
}
```

### `GET /api/email/setup-guide`
**Description:** Gmail OAuth setup instructions
**Authentication:** None

### `POST /api/email/test`
**Description:** Send test email
**Authentication:** API Key required

### `POST /api/email/send-job-application`
**Description:** Send job application with attachments
**Authentication:** API Key required

---

## Link Tracking API (`/api/link-tracking/*`)

### `GET /api/link-tracking/health`
**Description:** Link tracking service health check
**Authentication:** None
**Response:**
```json
{
  "service": "link_tracking_api",
  "status": "healthy",
  "version": "2.16.5"
}
```

### `POST /api/link-tracking/create`
**Description:** Create new tracked link
**Authentication:** API Key required (`X-API-Key` header)
**Request Body:**
```json
{
  "url": "https://example.com/job",
  "function": "Job_Posting",
  "metadata": {
    "job_id": "uuid",
    "company_name": "Company",
    "position": "Position"
  }
}
```

### `GET /api/link-tracking/analytics/<tracking_id>`
**Description:** Get analytics for tracked link
**Authentication:** API Key required

### `GET /r/<tracking_id>`
**Description:** Redirect endpoint (tracks click and redirects)
**Authentication:** None

---

## Workflow API (`/api/workflow/*`)

### `GET /api/workflow/status`
**Description:** Current workflow scheduling status
**Authentication:** API Key required

### `GET /api/workflow/next-phase`
**Description:** Next scheduled workflow phase
**Authentication:** API Key required

### `GET /api/workflow/schedule-summary`
**Description:** Complete workflow schedule
**Authentication:** API Key required

---

## Document Generation API

### `POST /resume`
**Description:** Generate resume document
**Authentication:** Session required
**Request Body:**
```json
{
  "job_id": "uuid",
  "template": "harvard_mcs",
  "customizations": {
    "highlight_skills": ["Python", "Flask"],
    "target_keywords": ["software", "engineer"]
  }
}
```

### `POST /cover-letter`
**Description:** Generate cover letter document
**Authentication:** Session required

### `GET /download/<filename>`
**Description:** Download generated document
**Authentication:** Session required

---

## Dashboard API (`/api/dashboard/*`)

### `GET /api/dashboard/stats`
**Description:** Dashboard statistics
**Authentication:** Session required

### `GET /api/dashboard/applications`
**Description:** List applications
**Authentication:** Session required

### `GET /api/dashboard/application/<application_id>`
**Description:** Get specific application
**Authentication:** Session required

### `POST /dashboard/authenticate`
**Description:** Authenticate to dashboard
**Authentication:** None
**Request Body:**
```json
{
  "password": "dashboard-password"
}
```

---

## User Profile API (`/api/user-profile/*`)

### `GET /api/user-profile/<user_id>`
**Description:** Get user profile and preferences
**Authentication:** API Key required
**Requirements:** DATABASE_URL environment variable

### `GET /api/user-profile/health`
**Description:** User profile service health
**Authentication:** None

---

## Scraping API (`/api/scraper/*`)

### `POST /api/process-scrapes`
**Description:** Process raw scrapes into cleaned records
**Authentication:** Dashboard auth required
**Request Body:**
```json
{
  "batch_size": 100
}
```

### `GET /api/pipeline-stats`
**Description:** Get scraping pipeline statistics
**Authentication:** Dashboard auth required

### `POST /api/intelligent-scrape`
**Description:** Trigger intelligent job scraping
**Authentication:** Dashboard auth required
**Request Body:**
```json
{
  "user_id": "steve_glen",
  "max_jobs_per_package": 30
}
```

---

## Copywriting Evaluator API (`/api/copywriting-evaluator/*`)

### `GET /api/copywriting-evaluator/health`
**Description:** Copywriting evaluator service health
**Authentication:** None

### `POST /api/copywriting-evaluator/pipeline/start`
**Description:** Start copywriting evaluation pipeline
**Authentication:** API Key required

### `GET /api/copywriting-evaluator/statistics`
**Description:** Get evaluation statistics
**Authentication:** API Key required

---

## Frontend Routes

### `GET /dashboard`
**Description:** Main dashboard interface
**Authentication:** Session required (redirects to login if not authenticated)

### `GET /workflow`
**Description:** Workflow visualization
**Authentication:** Session required

### `GET /database-schema`
**Description:** Database schema visualization
**Authentication:** Session required

### `GET /demo`
**Description:** Job application system demonstration
**Authentication:** Session required

### `GET /preferences`
**Description:** User job preferences configuration
**Authentication:** Session required

### `GET /copywriting-evaluator-dashboard`
**Description:** Copywriting evaluator dashboard
**Authentication:** Session required

---

## Error Responses

### Standard Error Format
```json
{
  "error": "Error message description",
  "status": "error_type"
}
```

### HTTP Status Codes
- `200 OK` - Successful request
- `201 Created` - Resource created successfully
- `400 Bad Request` - Invalid request parameters
- `401 Unauthorized` - Authentication required or invalid
- `403 Forbidden` - Insufficient permissions
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server error

---

## Rate Limiting

Default rate limits (configurable via environment):
- Per Minute: 60 requests
- Per Hour: 1000 requests

---

## Missing/Non-Existent Routes

The following routes were referenced in tests but do not exist:

### ❌ `/api/db/stats/applications`
**Expected:** Application statistics
**Actual:** Route not registered
**Alternative:** Use `/api/db/health` or `/api/dashboard/stats`

### ❌ `/api/documents/resume`
**Expected:** Resume generation endpoint
**Actual:** Route not registered
**Alternative:** Use `/resume` (POST)

### ❌ `/api/workflow/process-application`
**Expected:** Process job application workflow
**Actual:** Route not registered
**Alternative:** Use existing workflow endpoints or implement

---

## Environment Variables Required

### Critical
- `WEBHOOK_API_KEY` - API authentication (min 32 chars)
- `SECRET_KEY` - Flask session encryption and CSRF protection (min 32 chars)
- `PGPASSWORD` / `DATABASE_PASSWORD` - Database password
- `DATABASE_URL` - Full database connection string

### Optional
- `GEMINI_API_KEY` - For AI features
- `APIFY_API_TOKEN` - For job scraping
- `LINK_TRACKING_API_KEY` - For link tracking

---

## Testing Endpoints

Use the provided test scripts:

```bash
# System verification
python tests/test_system_verification.py

# API endpoint testing
python tests/test_api_endpoints.py

# End-to-end workflow
python tests/test_end_to_end_workflow.py
```

---

## Notes

1. **Authentication Methods:** Different endpoints use different auth methods (API key, session, or none)
2. **Environment Dependencies:** Some endpoints require specific environment variables
3. **Template Paths:** Document generation requires templates in `content_template_library/jinja_templates/`
4. **Database Connection:** Most features require active PostgreSQL connection

---

**For More Information:**
- System Test Report: `SYSTEM_TEST_REPORT.md`
- Testing Summary: `TESTING_SUMMARY.md`
- Environment Setup: `STARTUP_WARNINGS.md`
