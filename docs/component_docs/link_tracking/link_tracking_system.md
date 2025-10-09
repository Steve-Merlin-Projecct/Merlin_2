---
title: Comprehensive Link Tracking System
status: production
version: 2.16.5
created: '2025-10-06'
updated: '2025-10-06'
author: Steve-Merlin-Projecct
type: reference
tags:
- link
- tracking
- system
---

# Comprehensive Link Tracking System

**Version**: 2.16.5  
**Implementation Date**: July 27, 2025  
**Status**: Production Ready with External Domain Integration

## Overview

The Link Tracking System provides comprehensive tracking and analytics for job-related links including LinkedIn profiles, Calendly scheduling, company websites, and application URLs. The system tracks job and application associations, multiple click events per link, and provides detailed analytics for application performance monitoring.

## System Architecture

### Core Components

#### 1. Database Layer
- **link_tracking table**: Stores tracked link metadata with job/application associations
- **link_clicks table**: Records individual click events with timestamps and user data
- **Comprehensive indexing**: Optimized for fast lookups and analytics queries

#### 2. API Layer
- **LinkTracker**: Core tracking functionality and database operations
- **LinkTrackingAPI**: REST API endpoints for external integration
- **LinkRedirectHandler**: URL redirection and click recording

#### 3. External Domain Integration
- **Redirect endpoints**: Handle URL redirection on external domains
- **Click recording**: Send click events back to main system
- **Analytics access**: Query link performance from external systems

## Database Schema

### link_tracking Table
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

### link_clicks Table
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

## Link Function Categories

### Standard User Link Functions
| Function | Purpose | Example URL |
|----------|---------|-------------|
| `LinkedIn` | Professional profile | linkedin.com/in/steve-glen |
| `Calendly` | Meeting scheduling | calendly.com/steve-glen/30min |
| `Portfolio` | Personal portfolio | steveglen.com |


### Link Type Categories
| Type | Description |
|------|-------------|
| `profile` | Personal/professional profiles |
| `job_posting` | Job-related content |
| `application` | Application process links |
| `document` | Document downloads |
| `external` | External websites |

## Core Functionality

### 1. Link Creation
```python
# Create tracked link with job/application association
result = link_tracker.create_tracked_link(
    original_url="https://linkedin.com/in/steve-glen",
    link_function="LinkedIn",
    job_id="550e8400-e29b-41d4-a716-446655440000",
    application_id="550e8400-e29b-41d4-a716-446655440001",
    link_type="profile",
    description="Professional LinkedIn profile"
)

# Returns tracking_id and redirect_url
tracking_id = result['tracking_id']  # lt_abc123def456
redirect_url = result['redirect_url']  # https://domain.com/track/lt_abc123def456
```

### 2. Click Recording
```python
# Record click event with comprehensive data
click_data = link_tracker.record_click(
    tracking_id="lt_abc123def456",
    ip_address="192.168.1.100",
    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    referrer_url="https://gmail.com",
    session_id="sess_xyz789",
    click_source="email",
    metadata={
        "utm_source": "email",
        "utm_medium": "application",
        "utm_campaign": "job_search"
    }
)
```

### 3. Analytics and Reporting
```python
# Get comprehensive link analytics
analytics = link_tracker.get_link_analytics(tracking_id)
# Returns: link_info, click_statistics, click_timeline

# Get job-level link summary
job_summary = link_tracker.get_job_link_summary(job_id)
# Returns: link_functions breakdown with click counts

# Generate performance report
report = link_tracker.get_link_performance_report(days=30)
# Returns: overall_statistics, function_performance, daily_trends
```

## API Endpoints

### Core API Endpoints

#### Create Tracked Link
```
POST /api/link-tracking/create
Body: {
  "original_url": "https://linkedin.com/in/steve-glen",
  "link_function": "LinkedIn",
  "job_id": "uuid",
  "application_id": "uuid",
  "link_type": "profile"
}
```

#### Record Click Event
```
POST /api/link-tracking/record-click
Body: {
  "tracking_id": "lt_abc123def456",
  "clicked_at": "2025-07-27T21:15:30Z",
  "ip_address": "192.168.1.100",
  "user_agent": "Mozilla/5.0...",
  "click_source": "email"
}
```

#### Get Link Analytics
```
GET /api/link-tracking/analytics/{tracking_id}
Response: {
  "link_info": {...},
  "click_statistics": {...},
  "click_timeline": [...]
}
```

### Redirect Endpoints
```
GET /track/{tracking_id}
Response: HTTP 302 Redirect to original URL (with click recording)

GET /track/health
Response: System health status
```

## External Domain Integration

### Required Information for External Domains

#### Essential Data for Receiving Links
```json
{
  "tracking_id": "lt_abc123def456",
  "original_url": "https://linkedin.com/in/steve-glen",
  "is_active": true,
  "link_function": "LinkedIn",
  "job_id": "uuid",
  "application_id": "uuid"
}
```

#### Essential Data for Sending Click Events
```json
{
  "tracking_id": "lt_abc123def456",
  "clicked_at": "2025-07-27T21:15:30Z",
  "ip_address": "192.168.1.100",
  "user_agent": "Mozilla/5.0...",
  "referrer_url": "https://gmail.com",
  "click_source": "email"
}
```

### Integration Methods

#### 1. API Integration (Recommended)
- Use REST API endpoints for all operations
- Requires API key authentication
- Supports rate limiting and error handling
- Ideal for external domains and microservices

#### 2. Direct Database Integration
- Direct PostgreSQL connection for high-performance scenarios
- Requires database credentials and network access
- Suitable for internal systems with database access

## Click Source Analytics

### Automatic Source Detection
The system automatically categorizes click sources based on referrer URLs:

| Source | Detection Logic | Description |
|--------|-----------------|-------------|
| `email` | gmail.com, outlook.com | Email clients |
| `linkedin` | linkedin.com | LinkedIn platform |
| `indeed` | indeed.com | Indeed job board |
| `dashboard` | main system domain | Application dashboard |
| `direct` | no referrer | Direct URL access |
| `external` | other domains | External websites |

### Custom Source Tracking
```python
# Override automatic detection with custom source
link_tracker.record_click(
    tracking_id="lt_abc123def456",
    click_source="custom_source",  # Manual override
    metadata={"custom_data": "value"}
)
```

## Performance Features

### Database Optimization
- **Strategic indexing**: Optimized for common query patterns
- **Composite indexes**: Multi-column indexes for complex queries
- **Query optimization**: Efficient JOIN operations and aggregations

### Caching Strategy
- **Link data caching**: Cache frequently accessed link information
- **Analytics caching**: Cache aggregated statistics for performance
- **Connection pooling**: Efficient database connection management

### Rate Limiting
- **API rate limits**: Prevent abuse and ensure system stability
- **Click recording**: 1000 requests/minute per IP
- **Analytics queries**: 100 requests/minute per API key

## Security Features

### Authentication and Authorization
- **API key authentication**: Secure access to all endpoints
- **Role-based access**: Different permissions for different operations
- **IP filtering**: Optional IP whitelisting for database connections

### Data Privacy
- **IP anonymization**: Automatic IP anonymization after 90 days
- **GDPR compliance**: Support for data deletion and privacy rights
- **DNT support**: Respect Do Not Track headers when configured

### Input Validation
- **URL validation**: Ensure valid URLs and prevent injection attacks
- **Data sanitization**: Clean all input data before storage
- **XSS prevention**: Protect against cross-site scripting attacks

## Monitoring and Analytics

### Key Metrics Tracked
- **Total clicks**: Overall click volume across all links
- **Unique sessions**: Distinct user sessions clicking links
- **Click sources**: Traffic source distribution
- **Function performance**: Performance by link function type
- **Geographic data**: Click distribution by IP location
- **Temporal patterns**: Click timing and frequency analysis

### Reporting Capabilities
- **Real-time analytics**: Live click tracking and statistics
- **Historical reports**: Trend analysis over time periods
- **Function comparison**: Performance comparison between link types
- **Job-level insights**: Link performance per job application
- **Application tracking**: Complete application link lifecycle

### Alert System
- **High traffic alerts**: Notification for unusual click volume
- **Error rate monitoring**: Track and alert on redirect failures
- **Performance degradation**: Monitor response times and database health

## Integration Examples

### Standard Job Application Link Package
```python
# Create complete link package for job application
tracked_links = link_tracker.create_job_application_links(
    application_id="550e8400-e29b-41d4-a716-446655440001",
)

# Returns dictionary of tracked URLs:
# {
#   "LinkedIn": "https://domain.com/track/lt_linkedin123",
#   "Calendly": "https://domain.com/track/lt_calendly456",
# }
```

### Email Template Integration
```html
<!-- Email template with tracked links -->
<p>Hi there,</p>
<p>I'm interested in the Marketing Manager position. Here are my professional details:</p>
<ul>
  <li><a href="{{tracked_links.LinkedIn}}">LinkedIn Profile</a></li>
  <li><a href="{{tracked_links.Portfolio}}">Portfolio Website</a></li>
  <li><a href="{{tracked_links.Calendly}}">Schedule a Meeting</a></li>
</ul>
<p>You can also view the <a href="{{tracked_links.Job_Posting}}">original job posting</a>.</p>
```

## Future Enhancements

### Planned Features
1. **Advanced Analytics**: Machine learning insights on click patterns
2. **A/B Testing**: Compare different link strategies
3. **Heatmap Analytics**: Visual representation of click patterns
4. **Conversion Tracking**: Track clicks to application outcomes
5. **Custom Domains**: Support for branded tracking domains
6. **Real-time Webhooks**: Push notifications for click events

### Technical Improvements
1. **Global CDN**: Reduce redirect latency worldwide
2. **Advanced Caching**: Redis-based caching for high performance
3. **Event Streaming**: Real-time event processing with Kafka
4. **Data Warehouse**: Integration with analytics platforms
5. **Mobile SDK**: Native mobile app integration

## Troubleshooting

### Common Issues

#### Link Not Redirecting
- **Check tracking_id**: Verify tracking ID exists and is active
- **Database connectivity**: Ensure database connection is working
- **URL validation**: Confirm original URL is valid and accessible

#### Missing Click Data
- **API authentication**: Verify API key is valid and has permissions
- **Network connectivity**: Check connection to main system
- **Rate limiting**: Ensure not hitting rate limits

#### Performance Issues
- **Database indexing**: Verify all indexes are properly created
- **Query optimization**: Check for slow queries and optimize
- **Connection pooling**: Ensure proper database connection management

### Debug Information
When reporting issues, include:
- Tracking ID
- Timestamp of issue
- Error messages
- Request/response headers
- User agent and IP address

## Related Documentation

- [External Domain Integration Guide](../../../export/external_domain_integration_guide.md)
- [API Endpoint Reference](../../../export/api_endpoint_reference.md)
- [Database Schema Reference](../../../export/database_schema_reference.md)
- [Job Application System Architecture](../application_workflow/application_orchestrator.md)