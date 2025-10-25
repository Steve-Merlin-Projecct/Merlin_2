---
title: "Prd Link Analytics Insights"
type: technical_doc
component: general
status: draft
tags: []
---

# Product Requirements Document: Link Analytics & Insights System

**Version:** 1.0
**Date:** October 9, 2025
**Status:** Draft
**Branch:** task/13-analytics
**Priority:** High

---

## Executive Summary

Transform the existing link tracking system from passive data collection into an active intelligence engine that measures application effectiveness and predicts outcomes. This system will close the loop between link clicks and application results, enabling data-driven optimization of job applications.

**Current State:** Link clicks are tracked but not analyzed for actionable insights.
**Target State:** Click data drives predictions, prioritization, and continuous improvement.

---

## Problem Statement

The system currently tracks:
- ✅ Link clicks (IP, timestamp, user agent, referrer)
- ✅ Link functions (LinkedIn, Calendly, Company_Website, Apply_Now)
- ✅ Click metadata (UTM parameters, session ID)

**But cannot answer:**
- ❌ Which applications are most likely to succeed?
- ❌ Which link types drive interviews/offers?
- ❌ How does employer engagement correlate with outcomes?
- ❌ What are the winning patterns to replicate?

---

## Success Criteria

**Phase 1 (MVP) - Weeks 1-2:**
1. Link clicks correlated with application outcomes (interview/offer rates)
2. Basic analytics API returns engagement-to-outcome data
3. Link function effectiveness ranked by conversion rate

**Phase 2 (Core) - Weeks 3-4:**
4. Behavioral metrics extracted (time-to-click, click sequences, engagement velocity)
5. Application health scores calculated based on engagement patterns
6. Historical data analysis identifies winning patterns

**Phase 3 (Intelligence) - Weeks 5-6:**
7. Predictive scoring model estimates application success probability
8. Automated prioritization of high-engagement applications
9. Feedback loop documented for future optimization

---

## Scope

### **In Scope:**
- Database schema extensions for engagement metrics
- SQL views for correlation analysis
- Analytics API endpoints for insights
- Behavioral metrics calculation (batch processing)
- Predictive scoring model (rules-based initially)
- Integration with existing workflow system

### **Out of Scope (Future Phases):**
- ⚠️ **Dashboard widgets** - Not needed yet, focus on API-first
- ⚠️ **Real-time alerts** - Batch processing sufficient for MVP
- ⚠️ **Click heatmaps** - Visual analytics deferred
- ⚠️ **A/B testing framework** - Requires stable baseline first
- ⚠️ **Optimization engine** - Manual analysis before automation
- ⚠️ **ML-based predictions** - Start with rules-based scoring

**Note:** Get the core analytics system running and validated before adding advanced features.

---

## Technical Requirements

### **Phase 1: Outcome Tracking (Weeks 1-2)**

#### 1.1 Database Schema Extensions

**Extend `job_applications` table:**
```sql
ALTER TABLE job_applications ADD COLUMN first_click_timestamp TIMESTAMP;
ALTER TABLE job_applications ADD COLUMN total_clicks INTEGER DEFAULT 0;
ALTER TABLE job_applications ADD COLUMN unique_click_sessions INTEGER DEFAULT 0;
ALTER TABLE job_applications ADD COLUMN most_clicked_link_function VARCHAR(100);
ALTER TABLE job_applications ADD COLUMN engagement_score INTEGER DEFAULT 0;
ALTER TABLE job_applications ADD COLUMN last_click_timestamp TIMESTAMP;
```

#### 1.2 Create Analytics Views

**View: `application_engagement_outcomes`**
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

**View: `link_function_effectiveness`**
```sql
CREATE VIEW link_function_effectiveness AS
SELECT
  lt.link_function,
  COUNT(DISTINCT lt.application_id) AS applications_with_link,
  COUNT(lc.click_id) AS total_clicks,
  COUNT(DISTINCT lc.click_id) / NULLIF(COUNT(DISTINCT lt.application_id), 0) AS avg_clicks_per_application,
  COUNT(DISTINCT CASE WHEN ja.status = 'interview' THEN ja.id END) AS interviews_generated,
  COUNT(DISTINCT CASE WHEN ja.status = 'offer' THEN ja.id END) AS offers_generated,
  ROUND(100.0 * COUNT(DISTINCT CASE WHEN ja.status = 'interview' THEN ja.id END) /
    NULLIF(COUNT(DISTINCT lt.application_id), 0), 2) AS interview_conversion_rate
FROM link_tracking lt
LEFT JOIN link_clicks lc ON lt.tracking_id = lc.tracking_id
LEFT JOIN job_applications ja ON lt.application_id = ja.id
WHERE lt.is_active = true
GROUP BY lt.link_function
ORDER BY interview_conversion_rate DESC;
```

#### 1.3 Analytics API Endpoints

**New module:** `modules/analytics/engagement_analytics.py`

**Endpoints:**
- `GET /api/analytics/engagement-summary` - Overall engagement metrics
- `GET /api/analytics/engagement-to-outcome` - Correlation between clicks and outcomes
- `GET /api/analytics/link-function-effectiveness` - Performance by link type
- `GET /api/analytics/application-engagement/<application_id>` - Single application details

**Response Format:**
```json
{
  "total_applications": 150,
  "applications_with_clicks": 89,
  "engagement_rate": 59.3,
  "avg_clicks_per_application": 3.2,
  "outcomes": {
    "no_engagement": {"count": 61, "interview_rate": 2.1},
    "low_engagement": {"count": 45, "interview_rate": 8.9},
    "high_engagement": {"count": 44, "interview_rate": 18.2}
  },
  "link_effectiveness": [
    {"function": "Calendly", "interview_rate": 22.5, "total_clicks": 112},
    {"function": "LinkedIn", "interview_rate": 15.8, "total_clicks": 245},
    {"function": "Apply_Now", "interview_rate": 9.3, "total_clicks": 178}
  ]
}
```

---

### **Phase 2: Behavioral Analytics (Weeks 3-4)**

#### 2.1 New Table: `link_click_analytics`

```sql
CREATE TABLE link_click_analytics (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  application_id UUID REFERENCES job_applications(id),
  job_id UUID REFERENCES jobs(id),

  -- Timing metrics
  time_to_first_click INTERVAL,
  hours_to_first_click NUMERIC,
  time_between_first_last_click INTERVAL,

  -- Sequence metrics
  click_sequence TEXT[], -- Array of link_function in order clicked
  unique_functions_clicked INTEGER,
  total_click_events INTEGER,

  -- Pattern metrics
  peak_click_hour INTEGER, -- 0-23
  click_days_of_week INTEGER[], -- Array of day numbers
  engagement_velocity NUMERIC, -- Clicks per day

  -- Calculated scores
  engagement_score INTEGER,
  intent_score INTEGER,

  -- Metadata
  calculated_at TIMESTAMP DEFAULT NOW(),
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_analytics_application ON link_click_analytics(application_id);
CREATE INDEX idx_analytics_engagement_score ON link_click_analytics(engagement_score);
```

#### 2.2 Batch Analytics Processor

**New module:** `modules/analytics/batch_processor.py`

**Functionality:**
- Nightly batch job (cron: `0 2 * * *`) calculates metrics for all applications
- On-demand calculation for specific applications via API
- Updates `link_click_analytics` table with computed metrics

**Calculations:**
```python
def calculate_engagement_metrics(application_id):
    """Calculate behavioral metrics for an application"""

    # Get all clicks for application
    clicks = get_application_clicks(application_id)

    metrics = {
        'time_to_first_click': clicks[0].clicked_at - application.created_at,
        'click_sequence': [c.link_function for c in clicks],
        'unique_functions_clicked': len(set(c.link_function for c in clicks)),
        'total_click_events': len(clicks),
        'peak_click_hour': mode([c.clicked_at.hour for c in clicks]),
        'engagement_velocity': len(clicks) / days_since_application
    }

    return metrics
```

#### 2.3 Analytics API Extension

**New endpoints:**
- `GET /api/analytics/behavioral-patterns` - Aggregate behavioral insights
- `GET /api/analytics/click-sequences` - Common successful click patterns
- `GET /api/analytics/timing-analysis` - Time-to-engagement analysis

---

### **Phase 3: Predictive Scoring (Weeks 5-6)**

#### 3.1 Engagement Scoring Model

**Rules-based scoring algorithm:**

```python
def calculate_engagement_score(application_id):
    """
    Calculate engagement score (0-100) based on click behavior
    Higher score = higher likelihood of success
    """
    score = 0
    clicks = get_application_clicks(application_id)

    if not clicks:
        return 0

    # Base points for any engagement
    score += 10

    # LinkedIn profile view: +25 points (employer researching candidate)
    if 'LinkedIn' in click_functions:
        score += 25

    # Calendly click: +40 points (highest intent signal)
    if 'Calendly' in click_functions:
        score += 40

    # Multiple clicks on same link: +5 per repeat (interest/sharing)
    repeat_clicks = len(clicks) - len(set(click_functions))
    score += min(repeat_clicks * 5, 15)  # Cap at 15

    # Quick response (within 4 hours): +30 points (urgency)
    if time_to_first_click < timedelta(hours=4):
        score += 30

    # Weekend click: +20 points (personal time = high interest)
    if first_click_day in [5, 6]:  # Saturday, Sunday
        score += 20

    # Multiple link types clicked: +10 per additional type
    score += (unique_functions_clicked - 1) * 10

    return min(score, 100)  # Cap at 100
```

#### 3.2 Prediction API

**New endpoints:**
- `GET /api/analytics/application-health/<application_id>` - Current health score & prediction
- `POST /api/analytics/predict-outcome` - Predict outcome based on engagement data
- `GET /api/analytics/high-priority-applications` - Applications needing immediate follow-up

**Response Format:**
```json
{
  "application_id": "uuid",
  "engagement_score": 78,
  "intent_score": 85,
  "predicted_outcome": "interview_likely",
  "confidence": 0.68,
  "reasons": [
    "Calendly clicked within 2 hours (high intent)",
    "LinkedIn profile viewed (candidate research)",
    "3 total clicks across 2 link types"
  ],
  "recommended_actions": [
    "Send personalized follow-up email within 24 hours",
    "Prepare for potential interview request"
  ],
  "historical_comparison": {
    "similar_engagement_patterns": 25,
    "interview_rate": "68%",
    "avg_time_to_interview": "4.2 days"
  }
}
```

#### 3.3 Workflow Integration

**Automatic prioritization:**
- Applications with engagement_score > 70 flagged as "high_priority"
- Integration with existing workflow system to trigger follow-ups
- Update application status based on engagement patterns

---

## Data Models

### **Engagement Metrics**

| Field | Type | Description |
|-------|------|-------------|
| `application_id` | UUID | Foreign key to job_applications |
| `engagement_score` | INTEGER | 0-100 score based on click behavior |
| `intent_score` | INTEGER | 0-100 score indicating employer interest level |
| `time_to_first_click` | INTERVAL | Time from application to first click |
| `click_sequence` | TEXT[] | Ordered array of link functions clicked |
| `unique_functions_clicked` | INTEGER | Count of distinct link types |
| `total_click_events` | INTEGER | Total number of clicks |
| `engagement_velocity` | NUMERIC | Clicks per day since application |

### **Link Effectiveness**

| Metric | Calculation | Purpose |
|--------|-------------|---------|
| `interview_conversion_rate` | (Interviews / Applications with Clicks) × 100 | Measure link effectiveness |
| `avg_clicks_per_application` | Total Clicks / Applications | Gauge employer engagement level |
| `time_to_engagement` | Median hours to first click | Understand response timing |
| `multi_touch_rate` | (Apps with 3+ clicks / Total Apps) × 100 | Identify deep engagement |

---

## API Specifications

### **Core Analytics Endpoints**

#### `GET /api/analytics/engagement-summary`
**Description:** Overall engagement metrics across all applications
**Authentication:** Required (API key)
**Rate Limit:** 100 requests/hour

**Query Parameters:**
- `start_date` (optional): Filter applications from date
- `end_date` (optional): Filter applications to date
- `status` (optional): Filter by application status

**Response:** See Phase 1.3 response format

---

#### `GET /api/analytics/link-function-effectiveness`
**Description:** Performance ranking of link types
**Authentication:** Required (API key)
**Rate Limit:** 100 requests/hour

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
      "offer_conversion_rate": 8.3
    }
  ],
  "recommendations": [
    "Calendly links show highest conversion - ensure prominent placement",
    "LinkedIn clicks indicate research phase - follow up within 24h"
  ]
}
```

---

#### `GET /api/analytics/application-health/<application_id>`
**Description:** Health score and prediction for specific application
**Authentication:** Required (API key)
**Rate Limit:** 200 requests/hour

**Response:** See Phase 3.2 response format

---

## Implementation Plan

### **Week 1: Database & Foundation**
- [ ] Run database migrations for schema extensions
- [ ] Create SQL views for correlation analysis
- [ ] Write data population scripts for existing records
- [ ] Test data integrity and relationships

### **Week 2: Analytics API - Phase 1**
- [ ] Create `modules/analytics/` package structure
- [ ] Implement `engagement_analytics.py` module
- [ ] Build API endpoints for engagement summary
- [ ] Write unit tests for correlation calculations
- [ ] Document API endpoints

### **Week 3: Behavioral Metrics**
- [ ] Create `link_click_analytics` table
- [ ] Build batch processor for metrics calculation
- [ ] Implement behavioral metrics calculations
- [ ] Schedule nightly batch job
- [ ] Test with historical data

### **Week 4: Analytics API - Phase 2**
- [ ] Extend API with behavioral endpoints
- [ ] Add click sequence analysis
- [ ] Implement timing analysis
- [ ] Performance testing and optimization
- [ ] Update API documentation

### **Week 5: Predictive Scoring**
- [ ] Build engagement scoring algorithm
- [ ] Implement intent scoring model
- [ ] Create prediction API endpoints
- [ ] Validate predictions against historical data
- [ ] Document scoring methodology

### **Week 6: Integration & Testing**
- [ ] Integrate with workflow system
- [ ] Implement automatic prioritization
- [ ] End-to-end testing with real data
- [ ] Performance benchmarking
- [ ] Final documentation and handoff

---

## Success Metrics

**System Performance:**
- Analytics API response time < 200ms (p95)
- Batch processing completes in < 5 minutes for 1000 applications
- 99.9% uptime for analytics endpoints

**Business Impact:**
- Identify top 3 link types by conversion rate
- Predict application outcomes with >60% accuracy
- Reduce wasted follow-up effort by 40% through prioritization

**Data Quality:**
- 100% of applications have engagement metrics calculated
- Historical data backfilled for 6+ months
- Zero data integrity errors in correlation views

---

## Future Enhancements (Not in Current Scope)

**After MVP validation:**
1. **Dashboard Widgets** - Visual analytics interface
2. **Real-time Alerts** - Immediate notifications for high-engagement
3. **Click Heatmaps** - Visual representation of click patterns
4. **A/B Testing Framework** - Experiment with link variations
5. **Optimization Engine** - Automated content/placement optimization
6. **ML-based Predictions** - Machine learning models for higher accuracy
7. **Employer Journey Mapping** - Multi-touch attribution across sessions
8. **Comparative Analysis** - Benchmark against industry standards

**Note:** These features require a stable, validated analytics foundation first. Focus on getting the core system running and proving value before expanding.

---

## Dependencies

**Required:**
- Existing link tracking system (modules/link_tracking/)
- PostgreSQL database with link_tracking and link_clicks tables
- Workflow system (modules/workflow/)
- Job applications table with status tracking

**Optional:**
- Email integration (for follow-up automation)
- Dashboard system (for future visualization)

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Insufficient historical data | Low prediction accuracy | Start with rules-based scoring, collect more data |
| Complex SQL queries slow | Poor API performance | Use materialized views, implement caching |
| Correlation != causation | Misleading insights | Document assumptions, validate with manual analysis |
| Scope creep to "nice-to-have" features | Delayed MVP | Strict adherence to phased approach, defer optimizations |

---

## Notes

- **API-first approach:** Build robust APIs before adding UI layers
- **Validate before optimize:** Prove value with manual analysis before automation
- **Incremental rollout:** Test with subset of applications before full deployment
- **Documentation priority:** API docs must be complete before deployment
- **Data privacy:** Ensure click data handling complies with privacy policies

---

## Approval

- [ ] Technical review complete
- [ ] Database schema approved
- [ ] API specifications validated
- [ ] Implementation timeline confirmed
- [ ] Ready to begin development
