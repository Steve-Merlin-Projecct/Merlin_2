# Task 03: Behavioral Metrics Table & Batch Processor

**Status:** Pending (Depends on Task 02)
**Priority:** High
**Estimated Time:** 5-6 hours
**Dependencies:** Task 01, Task 02

---

## Objective

Create the `link_click_analytics` table to store behavioral metrics and implement a batch processor to calculate and populate these metrics.

---

## Tasks

### 1. Create link_click_analytics Table

**Migration File:** `database_migrations/create_link_click_analytics.sql`

```sql
CREATE TABLE link_click_analytics (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  application_id UUID REFERENCES job_applications(id) ON DELETE CASCADE,
  job_id UUID REFERENCES jobs(id) ON DELETE SET NULL,

  -- Timing metrics
  time_to_first_click INTERVAL,
  hours_to_first_click NUMERIC(10,2),
  time_between_first_last_click INTERVAL,
  hours_between_first_last_click NUMERIC(10,2),

  -- Sequence metrics
  click_sequence TEXT[], -- Array of link_function in order clicked
  unique_functions_clicked INTEGER DEFAULT 0,
  total_click_events INTEGER DEFAULT 0,

  -- Pattern metrics
  peak_click_hour INTEGER, -- 0-23
  click_days_of_week INTEGER[], -- Array of day numbers (0=Sunday)
  engagement_velocity NUMERIC(10,4), -- Clicks per day

  -- Calculated scores
  engagement_score INTEGER DEFAULT 0,
  intent_score INTEGER DEFAULT 0,

  -- Metadata
  calculated_at TIMESTAMP DEFAULT NOW(),
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),

  -- Constraints
  CONSTRAINT valid_peak_hour CHECK (peak_click_hour >= 0 AND peak_click_hour <= 23),
  CONSTRAINT valid_engagement_score CHECK (engagement_score >= 0 AND engagement_score <= 100),
  CONSTRAINT valid_intent_score CHECK (intent_score >= 0 AND intent_score <= 100)
);

-- Indexes for performance
CREATE INDEX idx_analytics_application ON link_click_analytics(application_id);
CREATE INDEX idx_analytics_job ON link_click_analytics(job_id);
CREATE INDEX idx_analytics_engagement_score ON link_click_analytics(engagement_score DESC);
CREATE INDEX idx_analytics_intent_score ON link_click_analytics(intent_score DESC);
CREATE INDEX idx_analytics_calculated_at ON link_click_analytics(calculated_at);

-- Unique constraint to prevent duplicate analytics records
CREATE UNIQUE INDEX idx_analytics_unique_application ON link_click_analytics(application_id);

COMMENT ON TABLE link_click_analytics IS 'Pre-calculated behavioral metrics for link click analysis';
```

### 2. Create Batch Processor Module

**File:** `modules/analytics/batch_processor.py`

**Key Functions:**

```python
class BatchAnalyticsProcessor:
    """
    Batch processor for calculating behavioral metrics
    """

    def process_all_applications(self, limit=None):
        """Process all applications needing analytics calculation"""

    def process_application(self, application_id):
        """Calculate and store metrics for a single application"""

    def calculate_timing_metrics(self, application_id, clicks):
        """Calculate time-based metrics"""

    def calculate_sequence_metrics(self, clicks):
        """Calculate click sequence patterns"""

    def calculate_pattern_metrics(self, clicks):
        """Calculate behavioral patterns"""

    def calculate_engagement_score(self, application_id, metrics):
        """Calculate engagement score (0-100)"""

    def calculate_intent_score(self, metrics):
        """Calculate intent score (0-100)"""
```

### 3. Implement Scoring Algorithms

**Engagement Score (0-100):**
```python
def calculate_engagement_score(self, application_id, metrics):
    """
    Rules-based engagement scoring
    Higher score = higher likelihood of success
    """
    score = 0

    # Base points for any engagement
    if metrics['total_click_events'] > 0:
        score += 10

    # LinkedIn profile view: +25 points
    if 'LinkedIn' in metrics['click_sequence']:
        score += 25

    # Calendly click: +40 points (highest intent)
    if 'Calendly' in metrics['click_sequence']:
        score += 40

    # Multiple clicks on same link: +5 per repeat (max 15)
    repeat_clicks = metrics['total_click_events'] - metrics['unique_functions_clicked']
    score += min(repeat_clicks * 5, 15)

    # Quick response (within 4 hours): +30 points
    if metrics['hours_to_first_click'] and metrics['hours_to_first_click'] < 4:
        score += 30

    # Weekend click: +20 points (personal time = interest)
    weekend_clicks = [day for day in metrics['click_days_of_week'] if day in [0, 6]]
    if weekend_clicks:
        score += 20

    # Multiple link types: +10 per additional type
    if metrics['unique_functions_clicked'] > 1:
        score += (metrics['unique_functions_clicked'] - 1) * 10

    return min(score, 100)
```

**Intent Score (0-100):**
```python
def calculate_intent_score(self, metrics):
    """
    Score indicating employer's level of interest
    Based on timing and click patterns
    """
    score = 0

    # Very quick response (< 2 hours): 50 points
    if metrics['hours_to_first_click'] and metrics['hours_to_first_click'] < 2:
        score += 50
    elif metrics['hours_to_first_click'] and metrics['hours_to_first_click'] < 8:
        score += 30

    # High click velocity: 30 points
    if metrics['engagement_velocity'] and metrics['engagement_velocity'] > 2:
        score += 30
    elif metrics['engagement_velocity'] and metrics['engagement_velocity'] > 1:
        score += 15

    # Calendly (booking intent): 40 points
    if 'Calendly' in metrics['click_sequence']:
        score += 40

    # Multiple sessions (repeat visits): 20 points
    if metrics['total_click_events'] > 3:
        score += 20

    return min(score, 100)
```

### 4. Create Batch Job Script

**File:** `scripts/run_analytics_batch.py`

```python
#!/usr/bin/env python3
"""
Batch job to calculate link click analytics
Run nightly via cron: 0 2 * * * /path/to/run_analytics_batch.py
"""

import logging
from modules.analytics.batch_processor import BatchAnalyticsProcessor

logger = logging.getLogger(__name__)

def main():
    processor = BatchAnalyticsProcessor()

    logger.info("Starting analytics batch processing...")

    results = processor.process_all_applications()

    logger.info(f"Batch processing complete: {results}")

    return results

if __name__ == '__main__':
    main()
```

### 5. Add On-Demand API Endpoint

**Endpoint:** `POST /api/analytics/calculate/<application_id>`

Trigger analytics calculation for specific application without waiting for batch job.

---

## Validation

- [ ] Table created with all columns and indexes
- [ ] Batch processor calculates metrics correctly
- [ ] Scoring algorithms produce expected results
- [ ] Performance acceptable for large datasets (1000+ applications)
- [ ] On-demand calculation endpoint works
- [ ] Batch job script runs successfully
- [ ] Database schema documentation updated

---

## Testing

**Unit Tests:**
```python
def test_calculate_engagement_score():
    """Test engagement score calculation"""

def test_calculate_intent_score():
    """Test intent score calculation"""

def test_timing_metrics():
    """Test timing calculations"""

def test_sequence_metrics():
    """Test click sequence analysis"""
```

**Integration Tests:**
- Run batch processor on test dataset
- Verify metrics stored correctly
- Test with various click patterns
- Validate score ranges (0-100)

**Performance Tests:**
- Time batch processing for 1000 applications
- Monitor database load during batch job
- Verify index usage in queries

---

## Deliverables

1. Migration: `database_migrations/create_link_click_analytics.sql`
2. Module: `modules/analytics/batch_processor.py`
3. Script: `scripts/run_analytics_batch.py`
4. Tests: `tests/test_batch_processor.py`
5. Documentation: Update `modules/analytics/README.md`
6. Cron job configuration documentation

---

## Notes

- Run batch job during low-traffic hours (2 AM suggested)
- Monitor execution time and optimize if needed
- Consider incremental processing (only new/updated applications)
- Log processing statistics for monitoring
- Handle edge cases (no clicks, deleted applications, etc.)
