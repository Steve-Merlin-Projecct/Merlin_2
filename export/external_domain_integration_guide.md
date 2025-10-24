---
title: "External Domain Integration Guide"
type: guide
component: integration
status: draft
tags: []
---

# External Domain Link Tracking Integration Guide

**Version**: 2.16.5  
**Date**: July 27, 2025  
**Purpose**: Integration guide for implementing link tracking and redirect functionality on external domains

## Overview

This guide provides the minimum required information for implementing link tracking and redirect functionality on an external domain that communicates with the main job application system database.

## Database Schema Requirements

### Primary Tables

#### link_tracking Table
```sql
CREATE TABLE link_tracking (
    tracking_id VARCHAR(100) PRIMARY KEY,
    job_id UUID,
    application_id UUID,
    link_function VARCHAR(50) NOT NULL,
    link_type VARCHAR(50) NOT NULL,
    original_url VARCHAR(1000) NOT NULL,
    redirect_url VARCHAR(1000) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(100) DEFAULT 'system',
    is_active BOOLEAN DEFAULT TRUE,
    description TEXT
);
```

#### link_clicks Table
```sql
CREATE TABLE link_clicks (
    click_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tracking_id VARCHAR(100) NOT NULL,
    clicked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ip_address INET,
    user_agent TEXT,
    referrer_url VARCHAR(1000),
    session_id VARCHAR(100),
    click_source VARCHAR(50),
    metadata JSONB DEFAULT '{}'
);
```

## Minimum Required Information for External Domain

### 1. Receiving Links from Main System

When your external domain receives tracked links from the main job application system, you need these essential data points:

#### Essential Link Data Structure
```json
{
  "tracking_id": "lt_abc123def456",
  "original_url": "https://linkedin.com/in/steve-glen",
  "redirect_url": "https://yourdomain.com/track/lt_abc123def456",
  "link_function": "LinkedIn",
  "link_type": "profile",
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "application_id": "550e8400-e29b-41d4-a716-446655440001",
  "is_active": true,
  "created_at": "2025-07-27T21:00:00Z"
}
```

#### Required Fields for External Processing
| Field | Type | Required | Purpose |
|-------|------|----------|---------|
| `tracking_id` | string | Yes | Unique identifier for the link |
| `original_url` | string | Yes | Destination URL for redirect |
| `is_active` | boolean | Yes | Whether link is still trackable |

#### Optional Fields for Enhanced Functionality
| Field | Type | Purpose |
|-------|------|---------|
| `job_id` | UUID | Associate clicks with specific job |
| `application_id` | UUID | Associate clicks with application |
| `link_function` | string | Categorize link purpose (LinkedIn, Calendly, etc.) |
| `link_type` | string | Type classification (profile, job_posting, etc.) |
| `description` | string | Human-readable link description |

### 2. API Endpoints for Receiving Links

#### GET Link Information
```
GET /api/link-tracking/analytics/{tracking_id}
```

**Response Structure:**
```json
{
  "link_info": {
    "tracking_id": "lt_abc123def456",
    "original_url": "https://linkedin.com/in/steve-glen",
    "link_function": "LinkedIn",
    "link_type": "profile",
    "job_id": "550e8400-e29b-41d4-a716-446655440000",
    "application_id": "550e8400-e29b-41d4-a716-446655440001",
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
  }
}
```

## Minimum Required Information for Sending Data

### 1. Recording Click Events

When a user clicks a tracked link on your external domain, you must send this information back to the main system:

#### Required Click Data Structure
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

#### Essential Fields for Click Tracking
| Field | Type | Required | Purpose |
|-------|------|----------|---------|
| `tracking_id` | string | Yes | Links click to original tracked link |
| `clicked_at` | timestamp | Yes | When the click occurred |

#### Recommended Fields for Analytics
| Field | Type | Purpose |
|-------|------|---------|
| `ip_address` | string | User identification and geographic analysis |
| `user_agent` | string | Browser/device identification |
| `referrer_url` | string | Traffic source analysis |
| `session_id` | string | User session tracking |
| `click_source` | string | Categorize traffic source |

### 2. API Endpoint for Sending Click Data

#### POST Click Event
```
POST /api/link-tracking/record-click
Content-Type: application/json
```

**Request Body:**
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
    "utm_medium": "application"
  }
}
```

**Response:**
```json
{
  "click_id": "550e8400-e29b-41d4-a716-446655440002",
  "tracking_id": "lt_abc123def456",
  "clicked_at": "2025-07-27T21:15:30Z",
  "click_source": "email",
  "status": "recorded"
}
```

## Implementation Examples

### 1. External Domain Redirect Handler (Minimal)

```javascript
// Minimal redirect handler for external domain
class LinkRedirectHandler {
  constructor(apiBaseUrl, apiKey) {
    this.apiBaseUrl = apiBaseUrl;
    this.apiKey = apiKey;
  }

  async handleRedirect(trackingId, request) {
    try {
      // Get original URL
      const linkData = await this.getLinkData(trackingId);
      
      if (!linkData || !linkData.is_active) {
        return this.renderErrorPage('Link not found or expired');
      }

      // Record click event
      await this.recordClick(trackingId, request);

      // Redirect to original URL
      return this.redirect(linkData.original_url);
      
    } catch (error) {
      console.error('Redirect error:', error);
      return this.renderErrorPage('Internal server error');
    }
  }

  async getLinkData(trackingId) {
    const response = await fetch(
      `${this.apiBaseUrl}/api/link-tracking/analytics/${trackingId}`,
      {
        headers: {
          'Authorization': `Bearer ${this.apiKey}`,
          'Content-Type': 'application/json'
        }
      }
    );
    
    if (response.ok) {
      const data = await response.json();
      return data.link_info;
    }
    return null;
  }

  async recordClick(trackingId, request) {
    const clickData = {
      tracking_id: trackingId,
      clicked_at: new Date().toISOString(),
      ip_address: this.getClientIP(request),
      user_agent: request.headers['user-agent'] || '',
      referrer_url: request.headers['referer'] || '',
      session_id: this.getSessionId(request),
      click_source: this.determineClickSource(request.headers['referer']),
      metadata: this.extractUTMParameters(request.url)
    };

    await fetch(`${this.apiBaseUrl}/api/link-tracking/record-click`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${this.apiKey}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(clickData)
    });
  }

  getClientIP(request) {
    return request.headers['x-forwarded-for']?.split(',')[0] ||
           request.headers['x-real-ip'] ||
           request.connection.remoteAddress;
  }

  determineClickSource(referrer) {
    if (!referrer) return 'direct';
    
    const referrerLower = referrer.toLowerCase();
    if (referrerLower.includes('gmail.com')) return 'email';
    if (referrerLower.includes('linkedin.com')) return 'linkedin';
    if (referrerLower.includes('indeed.com')) return 'indeed';
    return 'external';
  }

  extractUTMParameters(url) {
    const urlParams = new URLSearchParams(url.split('?')[1] || '');
    return {
      utm_source: urlParams.get('utm_source'),
      utm_medium: urlParams.get('utm_medium'),
      utm_campaign: urlParams.get('utm_campaign')
    };
  }
}
```

### 2. Database Direct Integration (Alternative)

If you prefer direct database access instead of API calls:

```python
# Python example for direct database integration
import psycopg2
from datetime import datetime
import uuid

class LinkTracker:
    def __init__(self, db_connection_string):
        self.db_conn = db_connection_string
    
    def get_original_url(self, tracking_id):
        with psycopg2.connect(self.db_conn) as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT original_url, is_active
                    FROM link_tracking
                    WHERE tracking_id = %s
                """, (tracking_id,))
                
                result = cursor.fetchone()
                if result and result[1]:  # is_active
                    return result[0]  # original_url
                return None
    
    def record_click(self, tracking_id, click_data):
        with psycopg2.connect(self.db_conn) as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO link_clicks (
                        click_id, tracking_id, clicked_at, ip_address,
                        user_agent, referrer_url, session_id, click_source, metadata
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    str(uuid.uuid4()),
                    tracking_id,
                    datetime.now(),
                    click_data.get('ip_address'),
                    click_data.get('user_agent'),
                    click_data.get('referrer_url'),
                    click_data.get('session_id'),
                    click_data.get('click_source', 'direct'),
                    click_data.get('metadata', {})
                ))
                conn.commit()
```

## Authentication Requirements

### API Authentication
All API requests must include authentication:

```http
Authorization: Bearer YOUR_API_KEY
Content-Type: application/json
```

### Database Authentication (if using direct connection)
```
Host: your-main-system-db-host
Database: job_application_system
User: link_tracking_user
Password: [secure_password]
Port: 5432
```

## Link Function Categories

Standard link functions you should expect:

| Function | Purpose | Typical URL Pattern |
|----------|---------|-------------------|
| `LinkedIn` | Professional profile | linkedin.com/in/username |
| `Calendly` | Meeting scheduling | calendly.com/username |
| `Company_Website` | Company homepage | company.com |
| `Apply_Now` | Direct application | company.com/apply |
| `Job_Posting` | Original job listing | indeed.com/job/id |

## Click Source Categories

Standard click sources for analytics:

| Source | Description |
|--------|-------------|
| `email` | Gmail, Outlook, email clients |
| `dashboard` | Main application dashboard |
| `linkedin` | LinkedIn platform |
| `indeed` | Indeed job board |
| `direct` | Direct URL access |
| `external` | Other external websites |

## Error Handling

### Common Error Responses

#### Link Not Found (404)
```json
{
  "error": "Link not found or expired",
  "tracking_id": "lt_abc123def456",
  "timestamp": "2025-07-27T21:30:00Z"
}
```

#### Invalid Request (400)
```json
{
  "error": "Missing required field: tracking_id",
  "required_fields": ["tracking_id", "clicked_at"],
  "timestamp": "2025-07-27T21:30:00Z"
}
```

#### Server Error (500)
```json
{
  "error": "Internal server error",
  "message": "Database connection failed",
  "timestamp": "2025-07-27T21:30:00Z"
}
```

## Security Considerations

### Required Security Measures
1. **HTTPS Only**: All communications must use HTTPS
2. **API Key Protection**: Secure API key storage and rotation
3. **Input Validation**: Validate all incoming tracking IDs and click data
4. **Rate Limiting**: Implement rate limiting to prevent abuse
5. **IP Filtering**: Consider IP whitelisting for database connections

### Data Privacy
- Store minimal user data (IP addresses can be anonymized)
- Respect DNT (Do Not Track) headers
- Implement GDPR compliance for EU users
- Provide opt-out mechanisms

## Testing and Validation

### Test Cases for External Domain

1. **Valid Link Redirect**
   - Input: Valid tracking_id
   - Expected: Successful redirect + click recorded

2. **Invalid Link Handling**
   - Input: Non-existent tracking_id
   - Expected: Error page displayed

3. **Inactive Link Handling**
   - Input: Deactivated tracking_id
   - Expected: Error page displayed

4. **Click Recording**
   - Input: Valid click data
   - Expected: Click recorded in database

### Sample Test Data
```json
{
  "test_tracking_id": "lt_test123456789",
  "test_original_url": "https://linkedin.com/in/steve-glen",
  "test_click_data": {
    "tracking_id": "lt_test123456789",
    "clicked_at": "2025-07-27T21:30:00Z",
    "ip_address": "192.168.1.100",
    "user_agent": "Mozilla/5.0 Test Browser",
    "click_source": "test"
  }
}
```

## Performance Considerations

### Optimization Tips
1. **Database Indexing**: Ensure tracking_id has proper index
2. **Caching**: Cache frequently accessed link data
3. **Async Processing**: Record clicks asynchronously when possible
4. **Connection Pooling**: Use connection pooling for database access
5. **CDN**: Use CDN for redirect endpoints if needed

### Expected Load
- Click recording: < 100ms response time
- Link resolution: < 50ms response time
- Database operations: Optimize for read-heavy workload

## Support and Troubleshooting

### Debug Information to Collect
- Tracking ID
- Timestamp of click
- User IP address
- Browser user agent
- Referrer URL
- Error messages

### Monitoring Metrics
- Click recording success rate
- Average redirect response time
- Database connection health
- API error rate

### Contact Information
For integration support, provide logs with:
- Tracking ID
- Timestamp
- Error message
- Request headers
- Response status