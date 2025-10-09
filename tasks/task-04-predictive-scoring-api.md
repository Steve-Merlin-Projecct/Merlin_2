# Task 04: Predictive Scoring & Health API

**Status:** Pending (Depends on Task 03)
**Priority:** Medium
**Estimated Time:** 4-5 hours
**Dependencies:** Task 01, Task 02, Task 03

---

## Objective

Build API endpoints that provide predictive health scores, outcome predictions, and recommended actions based on engagement analytics.

---

## Tasks

### 1. Create Prediction Engine Module

**File:** `modules/analytics/prediction_engine.py`

```python
class PredictionEngine:
    """
    Prediction engine for application outcomes based on engagement data
    """

    def get_application_health(self, application_id):
        """Get health score and prediction for application"""

    def predict_outcome(self, engagement_data):
        """Predict outcome based on engagement metrics"""

    def get_recommended_actions(self, application_id, health_score):
        """Generate recommended next steps"""

    def get_historical_comparison(self, engagement_pattern):
        """Compare to similar historical applications"""

    def get_high_priority_applications(self, limit=20):
        """Get applications requiring immediate attention"""
```

### 2. Implement Application Health Scoring

**Core Logic:**

```python
def get_application_health(self, application_id):
    """
    Calculate comprehensive health score for an application

    Returns:
        {
            'application_id': str,
            'engagement_score': int (0-100),
            'intent_score': int (0-100),
            'overall_health': str ('critical'|'low'|'moderate'|'good'|'excellent'),
            'predicted_outcome': str,
            'confidence': float (0-1),
            'reasons': [str],
            'recommended_actions': [str],
            'historical_comparison': dict
        }
    """

    # Get pre-calculated analytics
    analytics = get_link_click_analytics(application_id)

    # Determine overall health
    avg_score = (analytics.engagement_score + analytics.intent_score) / 2

    if avg_score >= 80:
        health = 'excellent'
        predicted_outcome = 'interview_likely'
        confidence = 0.75
    elif avg_score >= 60:
        health = 'good'
        predicted_outcome = 'interview_possible'
        confidence = 0.60
    elif avg_score >= 40:
        health = 'moderate'
        predicted_outcome = 'under_review'
        confidence = 0.45
    elif avg_score >= 20:
        health = 'low'
        predicted_outcome = 'minimal_interest'
        confidence = 0.30
    else:
        health = 'critical'
        predicted_outcome = 'no_interest'
        confidence = 0.20

    return {...}
```

### 3. Build Reasoning Engine

**Generate human-readable explanations:**

```python
def generate_reasons(self, analytics):
    """Generate list of reasons for health score"""
    reasons = []

    if analytics.engagement_score >= 70:
        if 'Calendly' in analytics.click_sequence:
            reasons.append("Calendly clicked (high intent signal)")
        if analytics.hours_to_first_click < 4:
            reasons.append(f"Quick response: clicked within {analytics.hours_to_first_click:.1f} hours")
        if analytics.total_click_events >= 3:
            reasons.append(f"{analytics.total_click_events} total clicks across {analytics.unique_functions_clicked} link types")

    if analytics.intent_score >= 70:
        if analytics.engagement_velocity > 2:
            reasons.append(f"High engagement velocity: {analytics.engagement_velocity:.1f} clicks/day")
        if 0 in analytics.click_days_of_week or 6 in analytics.click_days_of_week:
            reasons.append("Clicked during weekend (personal time investment)")

    return reasons
```

### 4. Build Recommendation Engine

```python
def get_recommended_actions(self, application_id, health_score, analytics):
    """Generate actionable recommendations"""
    actions = []

    if health_score >= 70:
        actions.append("Send personalized follow-up email within 24 hours")
        if 'Calendly' in analytics.click_sequence:
            actions.append("Prepare for potential interview request")
            actions.append("Review interview preparation materials")
        actions.append("Monitor for additional engagement signals")

    elif health_score >= 40:
        actions.append("Schedule follow-up check-in in 3-5 days")
        actions.append("Consider sending additional value-add content")

    else:
        actions.append("Mark as low priority for follow-up")
        actions.append("Focus efforts on higher-engagement applications")

    return actions
```

### 5. Implement Historical Comparison

```python
def get_historical_comparison(self, engagement_pattern):
    """
    Find similar applications from history and their outcomes
    """

    # Query applications with similar engagement patterns
    similar_apps = query_similar_patterns(
        engagement_score_range=(pattern.engagement_score - 10, pattern.engagement_score + 10),
        intent_score_range=(pattern.intent_score - 10, pattern.intent_score + 10),
        click_sequence_contains=pattern.click_sequence[:2]  # First 2 clicks
    )

    # Calculate outcome statistics
    total = len(similar_apps)
    interviews = len([a for a in similar_apps if a.status == 'interview'])
    offers = len([a for a in similar_apps if a.status == 'offer'])

    avg_time_to_interview = calculate_avg_time_to_interview(similar_apps)

    return {
        'similar_applications_count': total,
        'interview_rate': f"{(interviews/total)*100:.1f}%" if total > 0 else "N/A",
        'offer_rate': f"{(offers/total)*100:.1f}%" if total > 0 else "N/A",
        'avg_time_to_interview_days': avg_time_to_interview
    }
```

### 6. Create API Endpoints

**File:** `modules/analytics/prediction_api.py`

#### `GET /api/analytics/application-health/<application_id>`

Returns comprehensive health assessment for application.

**Response:**
```json
{
  "application_id": "uuid",
  "engagement_score": 78,
  "intent_score": 85,
  "overall_health": "good",
  "predicted_outcome": "interview_likely",
  "confidence": 0.68,
  "reasons": [
    "Calendly clicked within 2 hours (high intent)",
    "LinkedIn profile viewed (candidate research)",
    "3 total clicks across 2 link types"
  ],
  "recommended_actions": [
    "Send personalized follow-up email within 24 hours",
    "Prepare for potential interview request",
    "Monitor for additional engagement signals"
  ],
  "historical_comparison": {
    "similar_applications_count": 25,
    "interview_rate": "68.0%",
    "offer_rate": "24.0%",
    "avg_time_to_interview_days": 4.2
  },
  "calculated_at": "2025-10-09T14:32:00Z"
}
```

#### `POST /api/analytics/predict-outcome`

Predict outcome based on provided engagement data (for "what-if" scenarios).

**Request Body:**
```json
{
  "engagement_score": 75,
  "intent_score": 80,
  "click_sequence": ["LinkedIn", "Calendly"],
  "hours_to_first_click": 3.5
}
```

#### `GET /api/analytics/high-priority-applications`

Returns list of applications needing immediate attention.

**Query Params:**
- `limit` (default: 20)
- `min_score` (default: 60)

**Response:**
```json
{
  "high_priority_applications": [
    {
      "application_id": "uuid",
      "job_title": "Marketing Manager",
      "company": "Tech Corp",
      "engagement_score": 85,
      "intent_score": 90,
      "overall_health": "excellent",
      "predicted_outcome": "interview_likely",
      "confidence": 0.78,
      "last_click": "2025-10-09T12:45:00Z",
      "action_required": "Follow up within 24 hours"
    }
  ],
  "total_count": 12,
  "retrieved_at": "2025-10-09T14:32:00Z"
}
```

### 7. Register Prediction API Blueprint

Add to `app_modular.py`:

```python
# Register Prediction API
try:
    from modules.analytics.prediction_api import prediction_api_bp
    app.register_blueprint(prediction_api_bp)
    logger.info("Prediction API registered successfully")
except ImportError as e:
    logger.warning(f"Could not register Prediction API: {e}")
```

---

## Validation

- [ ] Health scores calculated correctly
- [ ] Predictions match expected outcomes for test data
- [ ] Recommended actions are relevant and actionable
- [ ] Historical comparison returns accurate statistics
- [ ] High-priority endpoint returns properly sorted list
- [ ] API authentication and rate limiting working
- [ ] Error handling for edge cases
- [ ] Unit tests passing
- [ ] API documentation complete

---

## Testing

**Test Cases:**

```python
def test_excellent_health_prediction():
    """Test prediction for high-engagement application"""

def test_poor_health_prediction():
    """Test prediction for no-engagement application"""

def test_recommended_actions_high_score():
    """Verify appropriate actions for high scores"""

def test_recommended_actions_low_score():
    """Verify appropriate actions for low scores"""

def test_historical_comparison():
    """Test similarity matching and statistics"""

def test_high_priority_filtering():
    """Test high-priority application selection"""
```

**Manual Testing:**
```bash
# Test application health
curl -H "X-API-Key: $WEBHOOK_API_KEY" \
  http://localhost:5000/api/analytics/application-health/{app_id}

# Test prediction
curl -X POST -H "X-API-Key: $WEBHOOK_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"engagement_score": 75, "intent_score": 80}' \
  http://localhost:5000/api/analytics/predict-outcome

# Test high-priority list
curl -H "X-API-Key: $WEBHOOK_API_KEY" \
  "http://localhost:5000/api/analytics/high-priority-applications?limit=10"
```

---

## Deliverables

1. `modules/analytics/prediction_engine.py` - Core prediction logic
2. `modules/analytics/prediction_api.py` - API endpoints
3. Tests: `tests/test_prediction_engine.py`
4. API documentation: `docs/api/prediction-endpoints.md`
5. Updated module README

---

## Notes

- Start with rules-based predictions, ML models later
- Confidence scores should be conservative
- Monitor prediction accuracy over time
- Log predictions vs actual outcomes for validation
- Consider adding prediction explanation API for transparency
