# Calendly Integration API Documentation

**Version**: 4.2.0
**Last Updated**: October 9, 2025
**Status**: Production Ready

## Overview

This document describes the enhanced API endpoints that support automatic URL tracking for Calendly, LinkedIn, and Portfolio URLs in generated documents. The system automatically converts candidate URLs into tracked redirect URLs that provide click analytics and job/application association tracking.

## Table of Contents

- [Authentication](#authentication)
- [Enhanced Endpoints](#enhanced-endpoints)
  - [Resume Generation](#post-resume)
  - [Cover Letter Generation](#post-cover-letter)
- [Request Examples](#request-examples)
- [Response Format](#response-format)
- [Error Handling](#error-handling)
- [URL Tracking Behavior](#url-tracking-behavior)

---

## Authentication

All endpoints require valid API authentication:

```http
Content-Type: application/json
```

(Additional authentication may be required depending on deployment configuration)

---

## Enhanced Endpoints

### POST /resume

Generate a professional resume document with optional URL tracking.

#### Endpoint
```
POST /resume
```

#### Request Body (Enhanced)

```json
{
  "personal": {
    "full_name": "Steve Glen",
    "phone": "(780) 555-0123",
    "email": "1234.s.t.e.v.e.glen@gmail.com",
    "address": "Edmonton, AB, Canada"
  },
  "professional_summary": "Marketing professional with 10+ years experience...",
  "experience": [
    {
      "company": "Company Name",
      "title": "Marketing Manager",
      "start_date": "2020-01",
      "end_date": "Present",
      "description": "Led marketing initiatives..."
    }
  ],
  "education": [
    {
      "institution": "University Name",
      "degree": "Bachelor of Commerce",
      "field": "Marketing",
      "graduation_year": "2015"
    }
  ],
  "skills": {
    "technical": ["SEO", "Google Analytics", "Social Media Marketing"],
    "soft": ["Leadership", "Communication", "Strategic Planning"]
  },
  "target_position": "Marketing Manager",

  // NEW: Optional URL Tracking Parameters
  "job_id": "550e8400-e29b-41d4-a716-446655440000",        // Optional: UUID
  "application_id": "650e8400-e29b-41d4-a716-446655440001"  // Optional: UUID
}
```

#### New Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `job_id` | String (UUID) | No | Job posting identifier for URL tracking analytics. When provided, tracked URLs will be associated with this job. |
| `application_id` | String (UUID) | No | Application identifier for URL tracking analytics. When provided, tracked URLs will be associated with this application. |

#### Behavior

**Without tracking parameters** (`job_id` and `application_id` omitted):
- Document generated normally
- URL variables use original URLs (no tracking)
- Backward compatible with previous API versions

**With tracking parameters** (`job_id` and/or `application_id` provided):
- `{{calendly_url}}` → Tracked redirect URL (e.g., `http://domain.com/track/lt_calendly_abc123`)
- `{{linkedin_url}}` → Tracked redirect URL (e.g., `http://domain.com/track/lt_linkedin_xyz789`)
- `{{portfolio_url}}` → Tracked redirect URL (e.g., `http://domain.com/track/lt_portfolio_def456`)
- Click events recorded with job/application association
- Analytics available via Link Tracking API

#### Response

```json
{
  "success": true,
  "message": "Resume generated successfully",
  "filename": "resume_Steve_Glen_20251009_143022.docx",
  "file_path": "/storage/generated_documents/resume_Steve_Glen_20251009_143022.docx",
  "download_url": "/download/resume_Steve_Glen_20251009_143022.docx",
  "timestamp": "2025-10-09T14:30:22.123456"
}
```

---

### POST /cover-letter

Generate a professional cover letter with optional URL tracking.

#### Endpoint
```
POST /cover-letter
```

#### Request Body (Enhanced)

```json
{
  "personal": {
    "full_name": "Steve Glen",
    "phone": "(780) 555-0123",
    "email": "1234.s.t.e.v.e.glen@gmail.com",
    "address": "Edmonton, AB, Canada"
  },
  "recipient": {
    "name": "Jane Smith",
    "title": "Hiring Manager",
    "company": "Tech Company Inc"
  },
  "position": {
    "title": "Marketing Manager",
    "reference": "Job ID: MM-2025-001"
  },
  "content": {
    "opening_paragraph": "I am writing to express my interest...",
    "body_paragraphs": [
      "In my previous role...",
      "My experience includes...",
      "I am particularly excited about..."
    ],
    "closing_paragraph": "I look forward to the opportunity..."
  },
  "date": "2025-10-09",

  // NEW: Optional URL Tracking Parameters
  "job_id": "550e8400-e29b-41d4-a716-446655440000",        // Optional: UUID
  "application_id": "650e8400-e29b-41d4-a716-446655440001"  // Optional: UUID
}
```

#### New Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `job_id` | String (UUID) | No | Job posting identifier for URL tracking analytics |
| `application_id` | String (UUID) | No | Application identifier for URL tracking analytics |

#### Behavior

Same as resume endpoint - URL variables are automatically converted to tracked URLs when `job_id` and/or `application_id` are provided.

#### Response

```json
{
  "success": true,
  "message": "Cover letter generated successfully",
  "filename": "cover_letter_Steve_Glen_20251009_143045.docx",
  "file_path": "/storage/generated_documents/cover_letter_Steve_Glen_20251009_143045.docx",
  "download_url": "/download/cover_letter_Steve_Glen_20251009_143045.docx",
  "timestamp": "2025-10-09T14:30:45.123456"
}
```

---

## Request Examples

### Example 1: Generate Resume WITHOUT URL Tracking (Backward Compatible)

```bash
curl -X POST http://localhost:5000/resume \
  -H "Content-Type: application/json" \
  -d '{
    "personal": {
      "full_name": "Steve Glen",
      "phone": "(780) 555-0123",
      "email": "test@example.com",
      "address": "Edmonton, AB, Canada"
    },
    "professional_summary": "Experienced marketing professional...",
    "target_position": "Marketing Manager"
  }'
```

**Result**: Document generated with original Calendly URL (if present in template)

---

### Example 2: Generate Resume WITH URL Tracking

```bash
curl -X POST http://localhost:5000/resume \
  -H "Content-Type: application/json" \
  -d '{
    "personal": {
      "full_name": "Steve Glen",
      "phone": "(780) 555-0123",
      "email": "test@example.com",
      "address": "Edmonton, AB, Canada"
    },
    "professional_summary": "Experienced marketing professional...",
    "target_position": "Marketing Manager",
    "job_id": "550e8400-e29b-41d4-a716-446655440000",
    "application_id": "650e8400-e29b-41d4-a716-446655440001"
  }'
```

**Result**: Document generated with tracked Calendly URL (e.g., `http://domain.com/track/lt_calendly_abc123`)

---

### Example 3: Generate Cover Letter WITH URL Tracking

```bash
curl -X POST http://localhost:5000/cover-letter \
  -H "Content-Type: application/json" \
  -d '{
    "personal": {
      "full_name": "Steve Glen",
      "email": "test@example.com"
    },
    "recipient": {
      "name": "Hiring Manager",
      "company": "Tech Company Inc"
    },
    "position": {
      "title": "Marketing Manager"
    },
    "content": {
      "opening_paragraph": "I am excited to apply...",
      "body_paragraphs": ["My experience includes..."],
      "closing_paragraph": "I look forward to hearing from you."
    },
    "job_id": "550e8400-e29b-41d4-a716-446655440000",
    "application_id": "650e8400-e29b-41d4-a716-446655440001"
  }'
```

**Result**: Cover letter with tracked Calendly, LinkedIn, and Portfolio URLs

---

## Response Format

### Success Response

```json
{
  "success": true,
  "message": "Resume generated successfully",
  "filename": "resume_Steve_Glen_20251009_143022.docx",
  "file_path": "/storage/generated_documents/resume_Steve_Glen_20251009_143022.docx",
  "download_url": "/download/resume_Steve_Glen_20251009_143022.docx",
  "timestamp": "2025-10-09T14:30:22.123456"
}
```

### Error Response

```json
{
  "success": false,
  "error": "Error message describing what went wrong"
}
```

**HTTP Status Codes**:
- `200 OK` - Document generated successfully
- `400 Bad Request` - Invalid request format or missing required fields
- `500 Internal Server Error` - Server-side error during generation

---

## Error Handling

### Common Error Scenarios

#### 1. Invalid Content Type
```json
{
  "success": false,
  "error": "Invalid content type - JSON expected"
}
```
**Status**: 400
**Solution**: Set `Content-Type: application/json` header

#### 2. Empty Payload
```json
{
  "success": false,
  "error": "Empty payload - no resume data received"
}
```
**Status**: 400
**Solution**: Provide valid JSON data in request body

#### 3. Document Generation Failure
```json
{
  "success": false,
  "error": "Resume generation failed: [detailed error message]"
}
```
**Status**: 500
**Solution**: Check server logs for detailed error information

---

## URL Tracking Behavior

### Automatic URL Conversion

When `job_id` and/or `application_id` are provided, the system automatically:

1. **Detects URL variables** in template:
   - `{{calendly_url}}`
   - `{{linkedin_url}}`
   - `{{portfolio_url}}`

2. **Retrieves original URLs** from `user_candidate_info` table:
   ```sql
   SELECT calendly_url, linkedin_url, portfolio_url
   FROM user_candidate_info
   WHERE user_id = 'steve_glen'
   ```

3. **Creates tracked links** via LinkTracker:
   ```python
   tracker.create_tracked_link(
       original_url="https://calendly.com/steve-glen/30min",
       link_function="Calendly",
       job_id="550e8400-e29b-41d4-a716-446655440000",
       application_id="650e8400-e29b-41d4-a716-446655440001"
   )
   ```

4. **Substitutes in document**:
   - Original: `{{calendly_url}}`
   - Becomes: `http://localhost:5000/track/lt_calendly_abc123`

5. **Records clicks** when URL is accessed:
   - Inserts into `link_clicks` table
   - Captures: timestamp, IP, user agent, referrer
   - Redirects to original Calendly URL

### Caching Behavior

- **First Request**: Creates tracked URL and caches result
- **Subsequent Requests**: Returns cached URL for same `(job_id, application_id, url)` combination
- **Cache Key Format**: `{job_id}:{application_id}:{link_function}:{original_url}`
- **Benefits**: Prevents duplicate tracking entries, improves performance

### Fallback Behavior

If URL tracking fails for any reason:
- **System uses original URL** (no tracking)
- **Document generation continues** (no errors thrown)
- **Error logged** for monitoring

This ensures document generation never fails due to tracking issues.

---

## Link Tracking Analytics

After generating documents with tracked URLs, you can query analytics:

### Get Link Analytics
```bash
GET /api/link-tracking/analytics/{tracking_id}
```

**Response**:
```json
{
  "link_info": {
    "tracking_id": "lt_calendly_abc123",
    "original_url": "https://calendly.com/steve-glen/30min",
    "link_function": "Calendly",
    "job_id": "550e8400-e29b-41d4-a716-446655440000",
    "application_id": "650e8400-e29b-41d4-a716-446655440001"
  },
  "click_statistics": {
    "total_clicks": 5,
    "unique_sessions": 3,
    "first_click": "2025-10-09T15:00:00Z",
    "last_click": "2025-10-09T18:30:00Z"
  },
  "click_timeline": [
    {
      "clicked_at": "2025-10-09T15:00:00Z",
      "ip_address": "192.168.1.100",
      "click_source": "email"
    }
  ]
}
```

---

## Configuration

### Environment Variables

```bash
# Enable/disable URL tracking globally
ENABLE_URL_TRACKING=true

# Base URL for tracked links
BASE_REDIRECT_URL=http://localhost:5000/track
```

### Template Requirements

For URL tracking to work, templates must include URL variables:

```
Schedule a meeting: {{calendly_url}}
View my LinkedIn: {{linkedin_url}}
Visit my portfolio: {{portfolio_url}}
```

### Database Requirements

Candidate URLs must be configured in `user_candidate_info` table:

```sql
INSERT INTO user_candidate_info (user_id, calendly_url, linkedin_url, portfolio_url)
VALUES (
    'steve_glen',
    'https://calendly.com/steve-glen/30min',
    'https://linkedin.com/in/steve-glen',
    'https://steveglen.com'
);
```

---

## Migration Guide

### Updating from Previous API Version

No changes required! The enhanced API is **100% backward compatible**.

**Old Code (Still Works)**:
```javascript
const response = await fetch('/resume', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    personal: { full_name: 'Steve Glen', ...},
    professional_summary: '...'
  })
});
```

**New Code (With Tracking)**:
```javascript
const response = await fetch('/resume', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    personal: { full_name: 'Steve Glen', ...},
    professional_summary: '...',
    job_id: '550e8400-e29b-41d4-a716-446655440000',  // ADD THIS
    application_id: '650e8400-e29b-41d4-a716-446655440001'  // ADD THIS
  })
});
```

---

## Best Practices

1. **Always provide both `job_id` and `application_id`** for complete tracking
2. **Use UUIDs** for job_id and application_id (format: `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`)
3. **Configure candidate URLs** in database before generating documents
4. **Monitor analytics** to understand which jobs generate most engagement
5. **Test with tracking disabled** by setting `ENABLE_URL_TRACKING=false`

---

## Troubleshooting

### URLs not being tracked

**Symptom**: Documents contain original URLs instead of tracked URLs

**Possible Causes**:
1. `job_id` or `application_id` not provided in request
2. `ENABLE_URL_TRACKING` environment variable set to `false`
3. Template doesn't contain `{{calendly_url}}` variable
4. Candidate URLs not configured in database

**Solution**: Verify all requirements are met (see Configuration section)

### LinkTracker unavailable

**Symptom**: Documents generated but URLs are not tracked

**Behavior**: System automatically falls back to original URLs

**Action**: Check LinkTracker service health and database connectivity

---

## Related Documentation

- [Link Tracking System Documentation](../component_docs/link_tracking/link_tracking_system.md)
- [Calendly Integration Guide](../component_docs/calendly/calendly_integration_guide.md)
- [API Endpoint Reference](../../export/api_endpoint_reference.md)

---

**Document Version**: 1.0
**API Version**: 4.2.0
**Last Updated**: October 9, 2025
