---
title: "Task 02 Analytics Api Foundation"
type: api_spec
component: general
status: draft
tags: []
---

# Task 02: Analytics API Foundation - Phase 1

**Status:** Pending (Depends on Task 01)
**Priority:** High
**Estimated Time:** 4-5 hours
**Dependencies:** Task 01 (Database Schema Extensions)

---

## Objective

Create the analytics API module with core endpoints for engagement summary, outcome correlation, and link effectiveness analysis.

---

## Tasks

### 1. Create Module Structure

```
modules/analytics/
├── __init__.py
├── engagement_analytics.py      # Core analytics logic
├── engagement_analytics_api.py  # Flask blueprint with endpoints
└── README.md                     # Module documentation
```

### 2. Implement Core Analytics Engine

**File:** `modules/analytics/engagement_analytics.py`

**Key Classes/Functions:**
```python
class EngagementAnalytics:
    """Core analytics engine for link tracking insights"""

    def get_engagement_summary(self, start_date=None, end_date=None, status=None):
        """Get overall engagement metrics across applications"""

    def get_engagement_to_outcome_correlation(self):
        """Analyze correlation between engagement and outcomes"""

    def get_link_function_effectiveness(self):
        """Rank link types by conversion rate"""

    def get_application_engagement_details(self, application_id):
        """Get detailed engagement data for a specific application"""
```

### 3. Create API Blueprint

**File:** `modules/analytics/engagement_analytics_api.py`

**Endpoints:**

#### `GET /api/analytics/engagement-summary`
- Query params: `start_date`, `end_date`, `status`
- Returns: Overall engagement metrics
- Auth: Required (API key)
- Rate limit: 100/hour

#### `GET /api/analytics/engagement-to-outcome`
- Returns: Correlation data between clicks and outcomes
- Auth: Required (API key)
- Rate limit: 100/hour

#### `GET /api/analytics/link-function-effectiveness`
- Returns: Performance ranking by link type
- Auth: Required (API key)
- Rate limit: 100/hour

#### `GET /api/analytics/application-engagement/<application_id>`
- Returns: Detailed engagement for single application
- Auth: Required (API key)
- Rate limit: 200/hour

### 4. Implement Response Formats

**Engagement Summary Response:**
```json
{
  "summary": {
    "total_applications": 150,
    "applications_with_clicks": 89,
    "engagement_rate": 59.3,
    "avg_clicks_per_application": 3.2,
    "avg_hours_to_first_click": 12.4
  },
  "outcomes": {
    "no_engagement": {
      "count": 61,
      "interview_rate": 2.1,
      "offer_rate": 0.5
    },
    "low_engagement": {
      "count": 45,
      "interview_rate": 8.9,
      "offer_rate": 2.2
    },
    "high_engagement": {
      "count": 44,
      "interview_rate": 18.2,
      "offer_rate": 6.8
    }
  },
  "time_period": {
    "start_date": "2025-01-01",
    "end_date": "2025-10-09"
  }
}
```

**Link Effectiveness Response:**
```json
{
  "link_functions": [
    {
      "function": "Calendly",
      "applications_with_link": 145,
      "total_clicks": 312,
      "avg_clicks_per_application": 2.15,
      "interview_conversion_rate": 22.5,
      "offer_conversion_rate": 8.3,
      "effectiveness_rank": 1
    },
    {
      "function": "LinkedIn",
      "applications_with_link": 150,
      "total_clicks": 245,
      "avg_clicks_per_application": 1.63,
      "interview_conversion_rate": 15.8,
      "offer_conversion_rate": 5.2,
      "effectiveness_rank": 2
    }
  ],
  "insights": [
    "Calendly links show highest conversion - ensure prominent placement",
    "LinkedIn clicks indicate research phase - follow up within 24h"
  ]
}
```

### 5. Add Security & Validation

- API key authentication using existing security framework
- Rate limiting using existing security controls
- Input validation for query parameters
- Error handling with appropriate HTTP status codes

### 6. Register Blueprint in Main App

**File:** `app_modular.py`

```python
# Register Analytics API
try:
    from modules.analytics.engagement_analytics_api import engagement_analytics_bp
    app.register_blueprint(engagement_analytics_bp)
    logger.info("Analytics API registered successfully")
except ImportError as e:
    logger.warning(f"Could not register Analytics API: {e}")
```

---

## Validation

- [ ] All endpoints return valid JSON responses
- [ ] Authentication required and working
- [ ] Rate limiting enforced
- [ ] Query parameter filtering works correctly
- [ ] Error handling returns appropriate status codes
- [ ] API documentation complete
- [ ] Unit tests written and passing
- [ ] Integration tests with database views

---

## Testing

**Manual Testing:**
```bash
# Test engagement summary
curl -H "X-API-Key: $WEBHOOK_API_KEY" \
  http://localhost:5000/api/analytics/engagement-summary

# Test with filters
curl -H "X-API-Key: $WEBHOOK_API_KEY" \
  "http://localhost:5000/api/analytics/engagement-summary?status=interview"

# Test link effectiveness
curl -H "X-API-Key: $WEBHOOK_API_KEY" \
  http://localhost:5000/api/analytics/link-function-effectiveness

# Test application details
curl -H "X-API-Key: $WEBHOOK_API_KEY" \
  http://localhost:5000/api/analytics/application-engagement/{application_id}
```

**Unit Tests:**
- Test analytics calculations with mock data
- Test date range filtering
- Test status filtering
- Test error handling for invalid inputs

---

## Deliverables

1. `modules/analytics/engagement_analytics.py` - Core logic
2. `modules/analytics/engagement_analytics_api.py` - API endpoints
3. `modules/analytics/__init__.py` - Module initialization
4. `modules/analytics/README.md` - Documentation
5. Unit tests in `tests/test_analytics_api.py`
6. API documentation in `docs/api/analytics-endpoints.md`

---

## Notes

- Use existing database connection pooling
- Leverage SQLAlchemy ORM where appropriate
- Cache expensive queries (consider redis for future)
- Log all API access for audit trail
- Use existing security patterns from link_tracking module
