---
title: "Task 05 Workflow Integration"
type: process
component: integration
status: draft
tags: []
---

# Task 05: Workflow Integration & Automated Prioritization

**Status:** Pending (Depends on Task 04)
**Priority:** Medium
**Estimated Time:** 3-4 hours
**Dependencies:** Task 01, Task 02, Task 03, Task 04

---

## Objective

Integrate the analytics and prediction system with the existing workflow orchestrator to enable automated prioritization and intelligent follow-up triggers.

---

## Tasks

### 1. Update Workflow Manager

**File:** `modules/database/workflow_manager.py` or `modules/workflow/application_orchestrator.py`

Add methods to leverage analytics data:

```python
class WorkflowManager:

    def get_applications_for_followup(self, min_health_score=60):
        """Get applications that need follow-up based on engagement"""

    def prioritize_applications(self, application_ids):
        """Sort applications by engagement score and predicted outcome"""

    def trigger_intelligent_followup(self, application_id):
        """Trigger appropriate follow-up based on engagement pattern"""
```

### 2. Add Analytics-Based Triggers

**Create trigger conditions:**

```python
def check_engagement_triggers(application_id):
    """
    Check if application engagement warrants automated action

    Trigger Conditions:
    - High engagement score (>70): Send personalized follow-up
    - Calendly clicked: Prepare interview materials
    - Quick click (<2 hours): Flag for immediate attention
    - Weekend click: Note high personal interest
    """

    analytics = get_link_click_analytics(application_id)
    health = get_application_health(application_id)

    triggers = []

    if analytics.engagement_score >= 70:
        triggers.append({
            'type': 'high_engagement_followup',
            'priority': 'high',
            'action': 'send_personalized_email',
            'deadline': datetime.now() + timedelta(hours=24)
        })

    if 'Calendly' in analytics.click_sequence:
        triggers.append({
            'type': 'interview_preparation',
            'priority': 'high',
            'action': 'prepare_interview_materials',
            'deadline': datetime.now() + timedelta(hours=12)
        })

    if analytics.hours_to_first_click and analytics.hours_to_first_click < 2:
        triggers.append({
            'type': 'urgent_attention',
            'priority': 'critical',
            'action': 'flag_for_review',
            'deadline': datetime.now() + timedelta(hours=4)
        })

    return triggers
```

### 3. Create Priority Queue System

**File:** `modules/analytics/priority_queue.py`

```python
class ApplicationPriorityQueue:
    """
    Priority queue for managing application follow-ups
    """

    def add_to_queue(self, application_id, priority_score):
        """Add application to priority queue"""

    def get_next_applications(self, limit=10):
        """Get next applications to process, sorted by priority"""

    def update_priority(self, application_id):
        """Recalculate and update application priority"""

    def mark_processed(self, application_id):
        """Mark application as processed"""
```

**Database table:**
```sql
CREATE TABLE application_priority_queue (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  application_id UUID REFERENCES job_applications(id) ON DELETE CASCADE,
  priority_score INTEGER NOT NULL,
  engagement_score INTEGER,
  intent_score INTEGER,
  predicted_outcome VARCHAR(50),
  action_type VARCHAR(100),
  deadline TIMESTAMP,
  status VARCHAR(50) DEFAULT 'pending',
  processed_at TIMESTAMP,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_priority_queue_score ON application_priority_queue(priority_score DESC, deadline ASC);
CREATE INDEX idx_priority_queue_status ON application_priority_queue(status);
CREATE UNIQUE INDEX idx_priority_queue_app ON application_priority_queue(application_id) WHERE status = 'pending';
```

### 4. Build Automated Prioritization Service

**File:** `modules/analytics/auto_prioritization.py`

```python
class AutoPrioritizationService:
    """
    Automatically prioritize applications based on analytics
    """

    def run_prioritization(self):
        """
        Run prioritization for all active applications
        Updates priority queue based on latest analytics
        """

    def calculate_priority_score(self, application_id):
        """
        Calculate overall priority score (0-100)

        Factors:
        - Engagement score (40%)
        - Intent score (40%)
        - Time sensitivity (10%)
        - Application status (10%)
        """

    def identify_urgent_actions(self):
        """Find applications requiring immediate action"""
```

### 5. Create API Endpoints

**File:** `modules/analytics/workflow_integration_api.py`

#### `GET /api/analytics/priority-queue`

Get prioritized list of applications for processing.

**Response:**
```json
{
  "priority_queue": [
    {
      "application_id": "uuid",
      "priority_score": 92,
      "job_title": "Senior Marketing Manager",
      "company": "Tech Corp",
      "engagement_score": 85,
      "intent_score": 90,
      "action_type": "high_engagement_followup",
      "deadline": "2025-10-10T14:00:00Z",
      "recommended_action": "Send personalized follow-up email"
    }
  ],
  "total_pending": 15
}
```

#### `POST /api/analytics/process-triggers`

Manually trigger analytics-based workflow actions.

#### `GET /api/analytics/workflow-suggestions/<application_id>`

Get workflow suggestions for specific application.

### 6. Add Event Listeners

**Hook into existing click tracking:**

```python
# In modules/link_tracking/link_tracker.py

def record_click(self, tracking_id, ...):
    """Record click and trigger analytics updates"""

    # Existing click recording logic
    click_data = ...

    # NEW: Trigger analytics recalculation
    if application_id:
        trigger_analytics_update(application_id)
        check_engagement_triggers(application_id)

    return click_data
```

### 7. Create Monitoring Dashboard Queries

**File:** `modules/analytics/monitoring_queries.py`

```python
def get_prioritization_stats():
    """Get statistics on automated prioritization"""
    return {
        'total_in_queue': count_pending(),
        'high_priority': count_by_priority('high'),
        'overdue_actions': count_overdue(),
        'avg_processing_time': calculate_avg_processing_time()
    }
```

---

## Validation

- [ ] Applications automatically added to priority queue
- [ ] Priority scores calculated correctly
- [ ] Triggers fire on appropriate engagement events
- [ ] Queue ordering is correct (priority + deadline)
- [ ] Integration doesn't break existing workflow
- [ ] Performance acceptable with large datasets
- [ ] API endpoints return correct data
- [ ] Event listeners working properly

---

## Testing

**Integration Tests:**

```python
def test_high_engagement_triggers_priority():
    """Test that high engagement adds to priority queue"""

def test_priority_score_calculation():
    """Verify priority score formula"""

def test_queue_ordering():
    """Test queue returns applications in correct order"""

def test_trigger_conditions():
    """Test all trigger conditions fire correctly"""

def test_event_listener_integration():
    """Test click events trigger analytics updates"""
```

**Manual Testing:**
```bash
# Get priority queue
curl -H "X-API-Key: $WEBHOOK_API_KEY" \
  http://localhost:5000/api/analytics/priority-queue

# Trigger processing
curl -X POST -H "X-API-Key: $WEBHOOK_API_KEY" \
  http://localhost:5000/api/analytics/process-triggers

# Get workflow suggestions
curl -H "X-API-Key: $WEBHOOK_API_KEY" \
  http://localhost:5000/api/analytics/workflow-suggestions/{app_id}
```

---

## Deliverables

1. Database migration: `database_migrations/create_priority_queue.sql`
2. Module: `modules/analytics/priority_queue.py`
3. Module: `modules/analytics/auto_prioritization.py`
4. API: `modules/analytics/workflow_integration_api.py`
5. Tests: `tests/test_workflow_integration.py`
6. Documentation: Update workflow documentation with analytics integration

---

## Notes

- Start with manual triggering, then add automation
- Monitor system load from event listeners
- Consider rate limiting for analytics recalculation
- Log all automated decisions for audit trail
- Ensure existing workflow patterns not disrupted
- Plan for scaling (queue size, processing frequency)
