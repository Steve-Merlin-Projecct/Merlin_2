---
title: "Readme"
type: technical_doc
component: analytics
status: draft
tags: []
---

# Analytics Module

**Version:** 1.0.0
**Status:** Phase 1 Complete (Basic Analytics API)
**Branch:** task/13-analytics

---

## Overview

The Analytics module transforms link tracking data into actionable insights by:
- Correlating link clicks with application outcomes (interviews, offers)
- Ranking link types by effectiveness/conversion rate
- Calculating engagement scores for applications
- Providing predictive health scores (planned Phase 3)

---

## Architecture

```
modules/analytics/
├── __init__.py                      # Module initialization
├── engagement_analytics.py          # Core analytics engine
├── engagement_analytics_api.py      # Flask API endpoints
├── batch_processor.py               # Behavioral metrics (Phase 2)
├── prediction_engine.py             # Predictive scoring (Phase 3)
└── README.md                        # This file
```

---

## Current Features (Phase 1)

### 1. Engagement Summary
Get overall metrics across all applications:
- Total applications and engagement rate
- Average clicks per application
- Time-to-first-click statistics
- Outcome breakdown by engagement level

### 2. Engagement-to-Outcome Correlation
Analyze how click behavior correlates with outcomes:
- Average clicks by application status
- Comparison of interview vs rejected applications
- Auto-generated insights

### 3. Link Function Effectiveness
Rank link types by conversion rate:
- Interview conversion rate per link type
- Average clicks per application
- Effectiveness ranking
- Actionable recommendations

### 4. Application-Specific Details
Get detailed engagement for individual applications:
- Click timeline with timestamps
- Link functions clicked
- Session information
- Time-to-engagement metrics

---

## API Endpoints

### Base URL: `/api/analytics`

#### `GET /engagement-summary`
Get overall engagement metrics

**Query Parameters:**
- `start_date` (optional): ISO format date
- `end_date` (optional): ISO format date
- `status` (optional): Filter by application status

**Example:**
```bash
curl -H "X-API-Key: $WEBHOOK_API_KEY" \
  "http://localhost:5000/api/analytics/engagement-summary?status=interview"
```

**Response:**
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
    "no_engagement": {"count": 61, "interview_rate": 2.1, "offer_rate": 0.5},
    "low_engagement": {"count": 45, "interview_rate": 8.9, "offer_rate": 2.2},
    "high_engagement": {"count": 44, "interview_rate": 18.2, "offer_rate": 6.8}
  }
}
```

---

#### `GET /engagement-to-outcome`
Get correlation between clicks and outcomes

**Example:**
```bash
curl -H "X-API-Key: $WEBHOOK_API_KEY" \
  http://localhost:5000/api/analytics/engagement-to-outcome
```

**Response:**
```json
{
  "correlations": [
    {
      "status": "offer",
      "applications": 12,
      "avg_clicks": 5.2,
      "avg_sessions": 3.1,
      "avg_hours_to_click": 4.2
    }
  ],
  "insights": [
    "Applications with 'interview' status have highest average engagement (4.8 clicks)"
  ]
}
```

---

#### `GET /link-function-effectiveness`
Rank link types by conversion rate

**Example:**
```bash
curl -H "X-API-Key: $WEBHOOK_API_KEY" \
  http://localhost:5000/api/analytics/link-function-effectiveness
```

**Response:**
```json
{
  "link_functions": [
    {
      "function": "Calendly",
      "applications_with_link": 145,
      "total_clicks": 312,
      "avg_clicks_per_application": 2.15,
      "interview_conversion_rate": 22.5,
      "effectiveness_rank": 1
    }
  ],
  "insights": [
    "Calendly links show highest conversion (22.5%) - ensure prominent placement"
  ]
}
```

---

#### `GET /application-engagement/<application_id>`
Get detailed engagement for specific application

**Example:**
```bash
curl -H "X-API-Key: $WEBHOOK_API_KEY" \
  http://localhost:5000/api/analytics/application-engagement/{uuid}
```

**Response:**
```json
{
  "engagement_summary": {
    "application_id": "uuid",
    "status": "interview",
    "total_clicks": 5,
    "unique_sessions": 3,
    "hours_to_first_click": 2.3,
    "clicked_functions": ["LinkedIn", "Calendly"]
  },
  "click_timeline": [
    {
      "clicked_at": "2025-10-08T14:23:00Z",
      "click_source": "email",
      "link_function": "LinkedIn"
    }
  ]
}
```

---

## Database Schema

### Extended Tables

**job_applications** (new columns):
- `first_click_timestamp`: Timestamp of first click
- `last_click_timestamp`: Timestamp of last click
- `total_clicks`: Total click count
- `unique_click_sessions`: Unique sessions
- `most_clicked_link_function`: Most popular link
- `engagement_score`: Calculated score (0-100)

### Views

**application_engagement_outcomes:**
Aggregates click data by application for outcome analysis

**link_function_effectiveness:**
Ranks link types by interview/offer conversion rate

---

## Setup & Installation

### 1. Run Database Migrations

```bash
# From project root
python database_migrations/run_migrations.py
```

This will:
1. Add engagement columns to `job_applications`
2. Create analytics SQL views
3. Backfill existing application data

### 2. Verify Installation

```bash
# Test health endpoint
curl http://localhost:5000/api/analytics/health

# Should return:
# {"status": "healthy", "service": "engagement_analytics_api", "version": "1.0.0"}
```

### 3. Update Schema Documentation

```bash
python database_tools/update_schema.py
```

---

## Usage Examples

### Get Engagement Summary for Last 30 Days

```python
from datetime import datetime, timedelta

start_date = (datetime.now() - timedelta(days=30)).isoformat()

import requests
response = requests.get(
    "http://localhost:5000/api/analytics/engagement-summary",
    headers={"X-API-Key": os.environ["WEBHOOK_API_KEY"]},
    params={"start_date": start_date}
)

data = response.json()
print(f"Engagement rate: {data['summary']['engagement_rate']}%")
```

### Find Most Effective Link Type

```python
response = requests.get(
    "http://localhost:5000/api/analytics/link-function-effectiveness",
    headers={"X-API-Key": os.environ["WEBHOOK_API_KEY"]}
)

top_link = response.json()["link_functions"][0]
print(f"Top performing: {top_link['function']} at {top_link['interview_conversion_rate']}%")
```

---

## Roadmap

### ✅ Phase 1: Basic Analytics API (Current)
- Engagement summary endpoint
- Correlation analysis
- Link effectiveness ranking
- Application details endpoint

### 🔄 Phase 2: Behavioral Metrics (Next)
- `link_click_analytics` table
- Batch processor for metrics calculation
- Click sequence analysis
- Engagement scoring algorithm
- Pattern detection (time of day, device, velocity)

### 📋 Phase 3: Predictive Scoring (Future)
- Application health scoring
- Outcome prediction
- Recommended actions
- Historical comparison
- Priority queue for follow-ups

### 📋 Phase 4: Workflow Integration (Future)
- Auto-prioritization based on engagement
- Trigger follow-ups on high engagement
- Integration with email system
- Monitoring dashboard

---

## Dependencies

**Required:**
- Flask (web framework)
- psycopg2 (PostgreSQL adapter)
- Existing link tracking system (`modules/link_tracking/`)
- Database tables: `job_applications`, `link_tracking`, `link_clicks`

**Optional (Future Phases):**
- numpy/pandas (for advanced analytics)
- scikit-learn (for ML predictions)

---

## Testing

### Manual Testing

```bash
# Get summary
curl -H "X-API-Key: $WEBHOOK_API_KEY" \
  http://localhost:5000/api/analytics/engagement-summary

# Get correlation
curl -H "X-API-Key: $WEBHOOK_API_KEY" \
  http://localhost:5000/api/analytics/engagement-to-outcome

# Get link effectiveness
curl -H "X-API-Key: $WEBHOOK_API_KEY" \
  http://localhost:5000/api/analytics/link-function-effectiveness
```

### Unit Tests (Planned)

```bash
pytest tests/test_engagement_analytics.py
pytest tests/test_analytics_api.py
```

---

## Performance Considerations

**Database Views:**
- Indexed on key columns for fast aggregation
- Consider materializing views if dataset grows >10K applications

**API Response Times:**
- Current: ~50-200ms for summary endpoints
- Acceptable: <500ms (p95)
- If slower: Add caching layer (Redis)

**Query Optimization:**
- Use connection pooling (via SQLAlchemy)
- Limit result sets to relevant data
- Add indexes on frequently queried columns

---

## Security

**Authentication:**
- All endpoints require API key (via `X-API-Key` header)
- Uses existing security framework from link tracking module

**Rate Limiting:**
- To be added in Phase 2
- Recommended: 100 requests/hour per IP for analytics endpoints

**Data Privacy:**
- Click data includes IP addresses (currently stored)
- Consider anonymization for older data (>90 days)
- Comply with data retention policies

---

## Troubleshooting

### "Database connection failed"
Check environment variables:
```bash
echo $PGHOST $PGDATABASE $PGUSER $PGPASSWORD
```

### "View does not exist"
Run migrations:
```bash
python database_migrations/run_migrations.py
```

### "No data returned"
Verify link tracking is active and clicks are being recorded:
```sql
SELECT COUNT(*) FROM link_clicks;
SELECT COUNT(*) FROM job_applications WHERE total_clicks > 0;
```

---

## Contributing

When extending this module:

1. **Follow existing patterns** - Use similar structure to `engagement_analytics.py`
2. **Add tests** - Unit tests for all new functionality
3. **Update docs** - Keep this README current
4. **Run linters** - Black, Flake8 before committing
5. **Update schema** - Run `python database_tools/update_schema.py` after DB changes

---

## Support

**Documentation:**
- PRD: `/tasks/prd-link-analytics-insights.md`
- Task breakdown: `/tasks/task-01-*.md` through `/tasks/task-05-*.md`
- API docs: This README

**Issues:**
- Check existing tasks in `/tasks/` directory
- Review database migration logs
- Check Flask application logs

---

## License

Internal use only - Part of Automated Job Application System v4.2.0
