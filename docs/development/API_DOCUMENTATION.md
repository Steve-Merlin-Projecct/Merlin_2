# API Documentation

**Version**: 2.16.5  
**Date**: July 28, 2025  
**Base URL**: `http://localhost:5000` (Development) | `https://your-domain.replit.app` (Production)

## Authentication

### API Key Authentication
Most endpoints require API key authentication via headers:

```bash
# Link Tracking API
curl -H "X-API-Key: your-link-tracking-api-key" \
     -X POST http://localhost:5000/api/link-tracking/create

# General API
curl -H "Authorization: Bearer your-webhook-api-key" \
     -X POST http://localhost:5000/api/ai/analyze-jobs
```

### Session Authentication
Admin dashboard endpoints use session-based authentication:

```bash
# Login to dashboard
curl -X POST http://localhost:5000/dashboard/authenticate \
     -d "password=jellyfish–lantern–kisses"
```

## Core API Endpoints

### 1. Link Tracking API (`/api/link-tracking/`)

#### Create Tracking Link
```http
POST /api/link-tracking/create
```

**Authentication**: Required (X-API-Key header)  
**Rate Limit**: 50 requests/hour per IP

**Request Body**:
```json
{
  "url": "https://example.com/job-posting",
  "function": "Job_Posting",
  "metadata": {
    "job_id": "123e4567-e89b-12d3-a456-426614174000",
    "company_name": "Tech Corp",
    "position": "Software Engineer"
  }
}
```

**Response**:
```json
{
  "status": "success",
  "tracking_id": "TRK_a1b2c3d4e5f6",
  "tracking_url": "http://localhost:5000/r/TRK_a1b2c3d4e5f6",
  "original_url": "https://example.com/job-posting",
  "function": "Job_Posting",
  "created_at": "2025-07-28T01:05:22Z"
}
```

**Status Codes**:
- `201`: Link created successfully
- `400`: Invalid input data
- `401`: Authentication required
- `429`: Rate limit exceeded

#### Get Link Analytics
```http
GET /api/link-tracking/analytics/{tracking_id}
```

**Response**:
```json
{
  "tracking_id": "TRK_a1b2c3d4e5f6",
  "original_url": "https://example.com/job-posting",
  "function": "Job_Posting",
  "total_clicks": 15,
  "unique_ips": 8,
  "first_click": "2025-07-28T02:15:30Z",
  "last_click": "2025-07-28T08:45:15Z",
  "click_details": [
    {
      "timestamp": "2025-07-28T02:15:30Z",
      "ip_address": "192.168.1.100",
      "user_agent": "Mozilla/5.0...",
      "referrer": "https://linkedin.com",
      "source": "direct"
    }
  ]
}
```

#### Link Redirect Handler
```http
GET /r/{tracking_id}
```

**Functionality**: Automatically records click and redirects to original URL  
**Response**: 302 Redirect to original URL

### 2. AI Job Analysis API (`/api/ai/`)

#### Analyze Jobs
```http
POST /api/ai/analyze-jobs
```

**Authentication**: Required (session-based)  
**Rate Limit**: 10 requests/minute

**Request Body**:
```json
{
  "job_ids": [
    "123e4567-e89b-12d3-a456-426614174000",
    "987fcdeb-51a2-43f1-b456-426614174999"
  ],
  "analysis_type": "comprehensive"
}
```

**Response**:
```json
{
  "status": "success",
  "batch_id": "batch_20250728_001",
  "jobs_analyzed": 2,
  "results": [
    {
      "job_id": "123e4567-e89b-12d3-a456-426614174000",
      "analysis": {
        "skills": [
          {"skill": "Python", "importance": 0.9},
          {"skill": "SQL", "importance": 0.8}
        ],
        "authenticity_score": 0.95,
        "ats_keywords": ["python", "sql", "backend", "api"],
        "industry_classification": "Technology",
        "compensation_analysis": {
          "currency": "CAD",
          "salary_range": "75000-95000"
        }
      }
    }
  ],
  "usage": {
    "tokens_used": 1250,
    "cost": 0.001875,
    "remaining_daily": 1498
  }
}
```

#### Get Usage Statistics
```http
GET /api/ai/usage-stats
```

**Response**:
```json
{
  "current_usage": {
    "requests_today": 47,
    "daily_limit": 1500,
    "requests_this_month": 892,
    "monthly_budget": "$50.00"
  },
  "cost_tracking": {
    "today": "$0.03",
    "this_month": "$1.24",
    "projected_monthly": "$2.65"
  }
}
```

### 3. Job Scraping API (`/api/scraping/`)

#### Start Job Scrape
```http
POST /api/scraping/start-scrape
```

**Authentication**: Required (session-based)  
**Rate Limit**: 5 requests/hour

**Request Body**:
```json
{
  "search_terms": ["Software Engineer", "Python Developer"],
  "location": "Edmonton, AB",
  "max_results": 100,
  "filters": {
    "salary_min": 65000,
    "job_type": ["full-time", "contract"],
    "remote_ok": true
  }
}
```

**Response**:
```json
{
  "status": "started",
  "scrape_id": "scrape_20250728_001",
  "estimated_cost": "$0.50",
  "estimated_duration": "2-5 minutes",
  "job_count_estimate": 100
}
```

#### Get Scrape Status
```http
GET /api/scraping/status/{scrape_id}
```

**Response**:
```json
{
  "scrape_id": "scrape_20250728_001",
  "status": "completed",
  "progress": 100,
  "jobs_found": 87,
  "jobs_processed": 87,
  "cost": "$0.44",
  "started_at": "2025-07-28T01:00:00Z",
  "completed_at": "2025-07-28T01:03:45Z"
}
```

### 4. Document Generation API (`/api/documents/`)

#### Generate Resume
```http
POST /api/documents/resume
```

**Authentication**: Required (session-based)

**Request Body**:
```json
{
  "job_id": "123e4567-e89b-12d3-a456-426614174000",
  "template": "harvard_mcs",
  "csv_mapping": "steve_glen_marketing_specialist.csv",
  "customizations": {
    "highlight_skills": ["Python", "Data Analysis"],
    "target_keywords": ["marketing", "analytics", "strategy"]
  }
}
```

**Response**:
```json
{
  "status": "success",
  "document_id": "doc_20250728_001",
  "file_path": "storage/resumes/steve_glen_resume_20250728.docx",
  "download_url": "/api/documents/download/doc_20250728_001",
  "metadata": {
    "pages": 1,
    "word_count": 389,
    "template_used": "harvard_mcs",
    "generated_at": "2025-07-28T01:05:22Z"
  }
}
```

#### Generate Cover Letter
```http
POST /api/documents/cover-letter
```

**Request Body**:
```json
{
  "job_id": "123e4567-e89b-12d3-a456-426614174000",
  "template": "professional_standard",
  "recipient": {
    "company_name": "Tech Corp",
    "hiring_manager": "Jane Smith",
    "department": "Engineering"
  }
}
```

### 5. Email Integration API (`/api/email/`)

#### Send Application Email
```http
POST /api/email/send-application
```

**Authentication**: Required (session-based)  
**Rate Limit**: 20 requests/hour

**Request Body**:
```json
{
  "job_id": "123e4567-e89b-12d3-a456-426614174000",
  "recipient_email": "hr@techcorp.com",
  "subject": "Application for Software Engineer Position",
  "documents": [
    "doc_20250728_001",  // Resume
    "doc_20250728_002"   // Cover letter
  ],
  "custom_message": "I am excited to apply for this position..."
}
```

**Response**:
```json
{
  "status": "sent",
  "message_id": "msg_gmail_abc123",
  "sent_at": "2025-07-28T01:06:15Z",
  "recipient": "hr@techcorp.com",
  "attachments": [
    "steve_glen_resume_20250728.docx",
    "steve_glen_cover_letter_20250728.docx"
  ]
}
```

#### Check OAuth Status
```http
GET /api/email/oauth-status
```

**Response**:
```json
{
  "status": "authenticated",
  "email": "1234.S.t.e.v.e.Glen@gmail.com",
  "token_expires": "2025-08-27T01:05:22Z",
  "quotas": {
    "daily_send_limit": 100,
    "sent_today": 5,
    "remaining": 95
  }
}
```

### 6. Database API (`/api/db/`)

#### Get Job Information
```http
GET /api/db/jobs/{job_id}
```

**Authentication**: Required (API key)

**Response**:
```json
{
  "job": {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "title": "Software Engineer",
    "company": {
      "id": "456e7890-e12b-34c5-d678-901234567890",
      "name": "Tech Corp",
      "location": "Edmonton, AB"
    },
    "salary_min": 75000,
    "salary_max": 95000,
    "salary_currency": "CAD",
    "work_arrangement": "hybrid",
    "status": "analyzed",
    "analysis_completed": true,
    "created_at": "2025-07-28T00:30:00Z"
  }
}
```

#### Get Application Statistics
```http
GET /api/db/stats/applications
```

**Response**:
```json
{
  "total_applications": 45,
  "pending": 12,
  "sent": 28,
  "responded": 5,
  "success_rate": 0.11,
  "average_response_time": "3.2 days",
  "last_24_hours": {
    "applications_sent": 3,
    "responses_received": 1
  }
}
```

### 7. User Preferences API (`/api/user-profile/`)

#### Get User Profile
```http
GET /api/user-profile/steve-glen
```

**Response**:
```json
{
  "user": {
    "id": "steve_glen_001",
    "name": "Steve Glen",
    "location": "Edmonton, AB, Canada",
    "work_arrangement": "hybrid",
    "target_titles": [
      "Marketing Specialist",
      "Digital Marketing Coordinator",
      "Communications Specialist"
    ]
  },
  "preference_packages": [
    {
      "name": "Local Edmonton",
      "salary_range": "65000-85000",
      "currency": "CAD",
      "commute_max": "30 minutes",
      "remote_days": 2
    }
  ]
}
```

#### Update User Preferences
```http
PUT /api/user-profile/steve-glen/preferences
```

**Request Body**:
```json
{
  "salary_min": 70000,
  "salary_max": 90000,
  "preferred_industries": ["Marketing", "Technology", "Communications"],
  "work_arrangement": "hybrid",
  "remote_days_preferred": 3
}
```

### 8. Workflow API (`/api/workflow/`)

#### Process Complete Application Workflow
```http
POST /api/workflow/process-application
```

**Authentication**: Required (session-based)  
**Rate Limit**: 5 requests/hour

**Request Body**:
```json
{
  "job_id": "123e4567-e89b-12d3-a456-426614174000",
  "auto_send": false,
  "review_required": true
}
```

**Response**:
```json
{
  "status": "processing",
  "workflow_id": "wf_20250728_001",
  "steps": [
    {"step": "job_analysis", "status": "completed"},
    {"step": "document_generation", "status": "in_progress"},
    {"step": "email_preparation", "status": "pending"},
    {"step": "application_sending", "status": "pending"}
  ],
  "estimated_completion": "2025-07-28T01:10:00Z"
}
```

## Error Handling

### Standard Error Format
```json
{
  "error": "Detailed error message",
  "code": "ERROR_CODE",
  "details": {
    "field": "specific_field_with_error",
    "value": "problematic_value"
  },
  "timestamp": "2025-07-28T01:05:22Z"
}
```

### Common Error Codes
- `AUTHENTICATION_REQUIRED`: API key missing or invalid
- `RATE_LIMIT_EXCEEDED`: Too many requests from IP
- `VALIDATION_ERROR`: Input data validation failed
- `RESOURCE_NOT_FOUND`: Requested resource doesn't exist
- `INTERNAL_ERROR`: Server-side processing error
- `SERVICE_UNAVAILABLE`: External service temporarily unavailable

## Rate Limiting

### Default Limits
| Endpoint Category | Requests | Window | Scope |
|------------------|----------|--------|-------|
| Link Tracking Create | 50 | 1 hour | Per IP |
| Link Analytics | 100 | 1 hour | Per IP |
| Link Redirects | 200 | 1 hour | Per IP |
| AI Analysis | 10 | 1 minute | Per session |
| Job Scraping | 5 | 1 hour | Per session |
| Document Generation | 20 | 1 hour | Per session |
| Email Sending | 20 | 1 hour | Per session |

### Rate Limit Headers
```http
X-RateLimit-Limit: 50
X-RateLimit-Remaining: 23
X-RateLimit-Reset: 1642867200
X-RateLimit-Window: 3600
```

## Security Considerations

### Input Validation
All endpoints perform comprehensive input validation:
- URL validation for link tracking
- SQL injection prevention through parameterized queries
- XSS prevention through input sanitization
- Command injection pattern detection

### Security Headers
All responses include security headers:
```http
Content-Security-Policy: default-src 'self'
X-Frame-Options: DENY
X-Content-Type-Options: nosniff
X-XSS-Protection: 1; mode=block
Strict-Transport-Security: max-age=31536000
```

### Audit Logging
All API access is logged with:
- Request timestamp and IP address
- Authentication status and user identification
- Request parameters (sanitized)
- Response status and processing time
- Security events and validation failures

## Testing Endpoints

### Health Check
```http
GET /health
```

**Response**:
```json
{
  "status": "healthy",
  "version": "2.16.5",
  "database": "connected",
  "external_services": {
    "gmail": "authenticated",
    "gemini": "available",
    "apify": "available"
  },
  "timestamp": "2025-07-28T01:05:22Z"
}
```

### Security Test
```http
GET /api/security/test
```

**Response**:
```json
{
  "security_rating": "7.5/10",
  "last_assessment": "2025-07-28T01:00:00Z",
  "tests_passed": 10,
  "tests_failed": 2,
  "compliance": "OWASP Top 10 Partial"
}
```

## SDK and Integration Examples

### Python Integration
```python
import requests

class JobApplicationAPI:
    def __init__(self, base_url, api_key):
        self.base_url = base_url
        self.headers = {'X-API-Key': api_key}
    
    def create_tracking_link(self, url, function, metadata=None):
        response = requests.post(
            f"{self.base_url}/api/link-tracking/create",
            headers=self.headers,
            json={
                'url': url,
                'function': function,
                'metadata': metadata or {}
            }
        )
        return response.json()

# Usage
api = JobApplicationAPI('http://localhost:5000', 'your-api-key')
tracking = api.create_tracking_link(
    'https://company.com/job', 
    'Job_Posting',
    {'position': 'Software Engineer'}
)
```

### JavaScript Integration
```javascript
class JobApplicationAPI {
    constructor(baseUrl, apiKey) {
        this.baseUrl = baseUrl;
        this.headers = {'X-API-Key': apiKey};
    }
    
    async createTrackingLink(url, functionType, metadata = {}) {
        const response = await fetch(`${this.baseUrl}/api/link-tracking/create`, {
            method: 'POST',
            headers: {
                ...this.headers,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                url: url,
                function: functionType,
                metadata: metadata
            })
        });
        return await response.json();
    }
}

// Usage
const api = new JobApplicationAPI('http://localhost:5000', 'your-api-key');
const tracking = await api.createTrackingLink(
    'https://company.com/job',
    'Job_Posting',
    {position: 'Software Engineer'}
);
```

---

This API documentation provides comprehensive coverage of all system endpoints with security-first design and practical integration examples.