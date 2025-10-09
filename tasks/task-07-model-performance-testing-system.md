# Task 07: Model Performance Testing & Optimization System

**Related PRD**: `prd-gemini-prompt-optimization.md`
**Phase**: Post-MVP Enhancement
**Priority**: Medium-High
**Estimated Effort**: 1 week

---

## Objective

Build an automated system that periodically tests different Gemini models across all three tiers to identify the optimal model for each tier based on:
- Response quality/accuracy
- Response time
- Token usage
- Cost (if moving to paid tier)

This enables **dynamic model optimization** - automatically using the best model for each tier's specific needs.

---

## Background

### Model Selection Challenge

Currently using `gemini-2.0-flash-001` for all tiers, but different tiers have different complexity requirements:

**Tier 1 (Core)**: Mostly extraction & classification
- Skills extraction (pattern matching)
- Industry classification (categorization)
- Structured data parsing

**Tier 2 (Enhanced)**: Moderate reasoning
- Stress analysis (interpretation)
- Red flag detection (pattern + context)
- Cultural fit assessment

**Tier 3 (Strategic)**: Complex reasoning
- Prestige analysis (subjective judgment)
- Cover letter insights (creative strategy)
- Competitive positioning (strategic thinking)

### Hypothesis

- **Tier 1** might work well with `gemini-2.0-flash-lite-001` (2-3x faster, same accuracy for extraction)
- **Tier 2** needs balanced model like `gemini-2.0-flash-001` (current)
- **Tier 3** might benefit from `gemini-1.5-pro` (better reasoning for strategic insights)

---

## Requirements

### Functional Requirements

1. **Automated Model Testing**
   - Run weekly model comparison tests
   - Test all available models against same job set
   - Compare across accuracy, speed, cost metrics
   - Generate performance reports

2. **Model Registry**
   - Track all available Gemini models
   - Store model capabilities and tier suitability
   - Track performance history over time
   - Support A/B testing new models

3. **Performance Metrics**
   - **Accuracy**: Compare analysis results against golden dataset
   - **Speed**: Measure response time (p50, p95, p99)
   - **Consistency**: Check result variance across multiple runs
   - **Cost**: Calculate token usage per model

4. **Automated Model Selection**
   - Recommend optimal model per tier
   - Support manual override
   - Gradual rollout (shadow mode → partial → full)
   - Automatic rollback if quality degrades

5. **Alerting & Monitoring**
   - Alert if model performance degrades
   - Track model switches and reasons
   - Monitor cost implications
   - Quality assurance dashboards

---

## Technical Specification

### System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   Model Testing System                       │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌─────────────┐      ┌──────────────┐      ┌────────────┐  │
│  │   Golden    │      │    Model     │      │  Test      │  │
│  │   Dataset   │─────▶│   Testing    │─────▶│  Results   │  │
│  │ (100 jobs)  │      │   Engine     │      │  Database  │  │
│  └─────────────┘      └──────────────┘      └────────────┘  │
│                              │                      │         │
│                              │                      │         │
│                              ▼                      ▼         │
│                       ┌──────────────┐      ┌────────────┐  │
│                       │  Performance │      │  Reporting │  │
│                       │   Analyzer   │─────▶│   Engine   │  │
│                       └──────────────┘      └────────────┘  │
│                              │                      │         │
│                              ▼                      ▼         │
│                       ┌──────────────┐      ┌────────────┐  │
│                       │    Model     │      │ Email/Slack│  │
│                       │  Recommender │      │   Alerts   │  │
│                       └──────────────┘      └────────────┘  │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

---

### Database Schema

#### Table: `model_registry`

```sql
CREATE TABLE model_registry (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    model_name VARCHAR(100) NOT NULL UNIQUE,
    model_family VARCHAR(50), -- 'gemini-2.0', 'gemini-1.5', etc.
    tier VARCHAR(20), -- 'free', 'paid'
    capabilities JSONB, -- {reasoning: 8, speed: 9, extraction: 10}
    cost_per_1k_input DECIMAL(10, 6),
    cost_per_1k_output DECIMAL(10, 6),
    is_active BOOLEAN DEFAULT TRUE,
    added_at TIMESTAMP DEFAULT NOW(),
    metadata JSONB
);

-- Initial models
INSERT INTO model_registry (model_name, model_family, tier, capabilities) VALUES
('gemini-2.0-flash-lite-001', 'gemini-2.0', 'free', '{"reasoning": 6, "speed": 10, "extraction": 9}'),
('gemini-2.0-flash-001', 'gemini-2.0', 'free', '{"reasoning": 8, "speed": 9, "extraction": 9}'),
('gemini-1.5-flash', 'gemini-1.5', 'free', '{"reasoning": 7, "speed": 8, "extraction": 8}'),
('gemini-1.5-pro', 'gemini-1.5', 'free', '{"reasoning": 9, "speed": 6, "extraction": 8}');
```

#### Table: `model_test_runs`

```sql
CREATE TABLE model_test_runs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    test_name VARCHAR(200) NOT NULL,
    tier_tested INTEGER NOT NULL, -- 1, 2, or 3
    model_name VARCHAR(100) REFERENCES model_registry(model_name),
    test_dataset_version VARCHAR(50), -- 'golden_v1', 'golden_v2'
    jobs_tested INTEGER,

    -- Performance metrics
    avg_response_time_ms INTEGER,
    p95_response_time_ms INTEGER,
    p99_response_time_ms INTEGER,
    avg_tokens_used INTEGER,
    total_tokens_used INTEGER,

    -- Quality metrics
    accuracy_score DECIMAL(5, 2), -- 0-100
    consistency_score DECIMAL(5, 2), -- 0-100
    completeness_score DECIMAL(5, 2), -- 0-100

    -- Results
    test_status VARCHAR(50), -- 'completed', 'failed', 'running'
    test_started_at TIMESTAMP,
    test_completed_at TIMESTAMP,
    results_summary JSONB,

    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_model_test_runs_tier ON model_test_runs(tier_tested);
CREATE INDEX idx_model_test_runs_model ON model_test_runs(model_name);
CREATE INDEX idx_model_test_runs_created ON model_test_runs(created_at);
```

#### Table: `model_assignments`

```sql
CREATE TABLE model_assignments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tier INTEGER NOT NULL UNIQUE, -- 1, 2, or 3
    current_model VARCHAR(100) REFERENCES model_registry(model_name),
    previous_model VARCHAR(100),
    assignment_reason TEXT,
    assigned_at TIMESTAMP DEFAULT NOW(),
    assigned_by VARCHAR(100), -- 'auto', 'manual:username'

    -- Rollback info
    can_auto_rollback BOOLEAN DEFAULT TRUE,
    rollback_threshold_accuracy DECIMAL(5, 2), -- Auto-rollback if accuracy drops below this

    metadata JSONB
);

-- Initial assignments
INSERT INTO model_assignments (tier, current_model, assignment_reason, assigned_by) VALUES
(1, 'gemini-2.0-flash-001', 'Initial default model', 'system'),
(2, 'gemini-2.0-flash-001', 'Initial default model', 'system'),
(3, 'gemini-2.0-flash-001', 'Initial default model', 'system');
```

#### Table: `golden_dataset_jobs`

```sql
CREATE TABLE golden_dataset_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id UUID REFERENCES jobs(id),
    dataset_version VARCHAR(50) DEFAULT 'v1',

    -- Expected results for each tier (human-verified ground truth)
    tier1_expected_results JSONB,
    tier2_expected_results JSONB,
    tier3_expected_results JSONB,

    -- Metadata
    job_complexity VARCHAR(20), -- 'simple', 'moderate', 'complex'
    test_category VARCHAR(100), -- 'tech_startup', 'enterprise_corp', 'healthcare', etc.
    notes TEXT,

    added_at TIMESTAMP DEFAULT NOW(),
    verified_by VARCHAR(100)
);

CREATE INDEX idx_golden_dataset_version ON golden_dataset_jobs(dataset_version);
```

---

### Module Structure

**File**: `modules/ai_job_description_analysis/model_testing/`

```
model_testing/
├── __init__.py
├── test_engine.py          # Core testing logic
├── model_registry.py       # Model catalog and management
├── golden_dataset.py       # Golden dataset management
├── performance_analyzer.py # Metrics calculation
├── model_recommender.py    # Recommendation engine
└── scheduler.py            # Weekly test scheduling
```

---

### Core Testing Engine

**File**: `modules/ai_job_description_analysis/model_testing/test_engine.py`

```python
"""
Model Testing Engine
Runs comparative tests across different Gemini models
"""

import logging
from typing import Dict, List
from datetime import datetime
from modules.database.database_manager import DatabaseManager
from modules.ai_job_description_analysis.tier1_analyzer import Tier1CoreAnalyzer

logger = logging.getLogger(__name__)


class ModelTestEngine:
    """
    Automated model testing engine

    Runs periodic tests comparing different models across tiers
    to identify optimal model assignments
    """

    def __init__(self):
        self.db = DatabaseManager()
        self.test_id = None

    def run_tier1_model_test(
        self,
        models_to_test: List[str],
        golden_dataset_version: str = 'v1',
        test_name: str = 'Weekly Tier 1 Model Comparison'
    ) -> Dict:
        """
        Test multiple models against Tier 1 golden dataset

        Args:
            models_to_test: List of model names to compare
            golden_dataset_version: Version of golden dataset to use
            test_name: Descriptive name for this test run

        Returns:
            Dict with test results and recommendations
        """
        logger.info(f"Starting Tier 1 model test: {test_name}")
        logger.info(f"Testing models: {models_to_test}")

        # Get golden dataset
        golden_jobs = self._get_golden_dataset(tier=1, version=golden_dataset_version)

        if len(golden_jobs) < 10:
            raise ValueError("Golden dataset must have at least 10 jobs")

        results = {}

        # Test each model
        for model_name in models_to_test:
            logger.info(f"Testing model: {model_name}")

            model_results = self._test_model_tier1(
                model_name=model_name,
                golden_jobs=golden_jobs,
                test_name=test_name
            )

            results[model_name] = model_results

            # Save test run to database
            self._save_test_run(
                tier=1,
                model_name=model_name,
                results=model_results,
                test_name=test_name,
                dataset_version=golden_dataset_version
            )

        # Analyze and recommend
        recommendation = self._analyze_and_recommend(tier=1, results=results)

        return {
            'test_name': test_name,
            'tier': 1,
            'models_tested': models_to_test,
            'results': results,
            'recommendation': recommendation,
            'timestamp': datetime.now().isoformat()
        }

    def _test_model_tier1(
        self,
        model_name: str,
        golden_jobs: List[Dict],
        test_name: str
    ) -> Dict:
        """
        Test a single model against Tier 1 golden dataset

        Returns performance metrics
        """
        # Initialize analyzer with specific model
        analyzer = Tier1CoreAnalyzer(model_override=model_name)

        response_times = []
        token_usage = []
        accuracy_scores = []

        for job in golden_jobs:
            try:
                start_time = datetime.now()

                # Run analysis
                result = analyzer.analyze_job(job)

                # Measure response time
                response_time = (datetime.now() - start_time).total_seconds() * 1000
                response_times.append(response_time)

                # Track token usage
                tokens_used = result.get('tokens_used', 0)
                token_usage.append(tokens_used)

                # Calculate accuracy (compare with expected results)
                expected = job.get('tier1_expected_results', {})
                actual = result.get('analysis', {})
                accuracy = self._calculate_accuracy(expected, actual, tier=1)
                accuracy_scores.append(accuracy)

            except Exception as e:
                logger.error(f"Model {model_name} failed on job {job.get('id')}: {e}")
                continue

        # Calculate aggregate metrics
        return {
            'jobs_tested': len(golden_jobs),
            'avg_response_time_ms': sum(response_times) / len(response_times) if response_times else 0,
            'p95_response_time_ms': self._percentile(response_times, 95),
            'p99_response_time_ms': self._percentile(response_times, 99),
            'avg_tokens_used': sum(token_usage) / len(token_usage) if token_usage else 0,
            'total_tokens_used': sum(token_usage),
            'accuracy_score': sum(accuracy_scores) / len(accuracy_scores) if accuracy_scores else 0,
            'consistency_score': self._calculate_consistency(accuracy_scores),
            'response_time_data': response_times,
            'accuracy_data': accuracy_scores
        }

    def _calculate_accuracy(self, expected: Dict, actual: Dict, tier: int) -> float:
        """
        Calculate accuracy score by comparing expected vs actual results

        Tier 1 accuracy factors:
        - Skills: Overlap of top skills (40%)
        - Authenticity: Match on is_authentic boolean (20%)
        - Industry: Match on primary industry (20%)
        - Structured data: Salary range, job type matches (20%)
        """
        if tier == 1:
            score = 0.0

            # Skills overlap (40%)
            expected_skills = set(s['skill'] for s in expected.get('skills_analysis', {}).get('top_skills', []))
            actual_skills = set(s['skill'] for s in actual.get('skills_analysis', {}).get('top_skills', []))

            if expected_skills and actual_skills:
                overlap = len(expected_skills & actual_skills) / len(expected_skills)
                score += overlap * 40

            # Authenticity match (20%)
            if expected.get('authenticity_check', {}).get('is_authentic') == actual.get('authenticity_check', {}).get('is_authentic'):
                score += 20

            # Industry match (20%)
            if expected.get('classification', {}).get('industry') == actual.get('classification', {}).get('industry'):
                score += 20

            # Structured data (20%)
            expected_salary = expected.get('structured_data', {}).get('salary_range', {})
            actual_salary = actual.get('structured_data', {}).get('salary_range', {})

            if expected_salary.get('min') == actual_salary.get('min'):
                score += 10
            if expected_salary.get('max') == actual_salary.get('max'):
                score += 10

            return score

        return 0.0  # Implement for Tier 2 & 3 similarly

    def _percentile(self, data: List[float], percentile: int) -> float:
        """Calculate percentile from list of values"""
        if not data:
            return 0.0
        sorted_data = sorted(data)
        index = int(len(sorted_data) * (percentile / 100))
        return sorted_data[min(index, len(sorted_data) - 1)]

    def _calculate_consistency(self, scores: List[float]) -> float:
        """Calculate consistency score (lower variance = higher consistency)"""
        if len(scores) < 2:
            return 100.0

        mean = sum(scores) / len(scores)
        variance = sum((x - mean) ** 2 for x in scores) / len(scores)
        std_dev = variance ** 0.5

        # Convert to 0-100 scale (lower std dev = higher consistency)
        consistency = max(0, 100 - std_dev)
        return consistency

    def _get_golden_dataset(self, tier: int, version: str = 'v1') -> List[Dict]:
        """Fetch golden dataset jobs from database"""
        # Implementation required
        pass

    def _save_test_run(self, tier: int, model_name: str, results: Dict, test_name: str, dataset_version: str):
        """Save test run results to database"""
        # Implementation required
        pass

    def _analyze_and_recommend(self, tier: int, results: Dict[str, Dict]) -> Dict:
        """
        Analyze test results and recommend optimal model

        Recommendation factors:
        - Accuracy (50% weight)
        - Speed (30% weight)
        - Cost (20% weight)
        """
        scores = {}

        for model_name, metrics in results.items():
            # Normalize metrics to 0-100 scale
            accuracy_norm = metrics['accuracy_score']  # Already 0-100

            # Speed: Faster is better (normalize to 0-100, where 100 = fastest)
            response_times = [m['avg_response_time_ms'] for m in results.values()]
            min_time = min(response_times)
            max_time = max(response_times)

            if max_time > min_time:
                speed_norm = 100 - ((metrics['avg_response_time_ms'] - min_time) / (max_time - min_time) * 100)
            else:
                speed_norm = 100

            # Cost: Lower tokens = better (normalize to 0-100, where 100 = lowest)
            token_counts = [m['avg_tokens_used'] for m in results.values()]
            min_tokens = min(token_counts)
            max_tokens = max(token_counts)

            if max_tokens > min_tokens:
                cost_norm = 100 - ((metrics['avg_tokens_used'] - min_tokens) / (max_tokens - min_tokens) * 100)
            else:
                cost_norm = 100

            # Weighted score
            total_score = (
                accuracy_norm * 0.5 +
                speed_norm * 0.3 +
                cost_norm * 0.2
            )

            scores[model_name] = {
                'total_score': total_score,
                'accuracy_score': accuracy_norm,
                'speed_score': speed_norm,
                'cost_score': cost_norm,
                'metrics': metrics
            }

        # Find best model
        best_model = max(scores.items(), key=lambda x: x[1]['total_score'])

        return {
            'recommended_model': best_model[0],
            'recommendation_score': best_model[1]['total_score'],
            'all_scores': scores,
            'reasoning': self._generate_recommendation_reasoning(best_model, scores)
        }

    def _generate_recommendation_reasoning(self, best_model: Tuple, all_scores: Dict) -> str:
        """Generate human-readable explanation for recommendation"""
        model_name, scores = best_model

        reasoning = f"Recommended {model_name} for Tier 1 based on:\n"
        reasoning += f"- Accuracy: {scores['accuracy_score']:.1f}/100\n"
        reasoning += f"- Speed: {scores['speed_score']:.1f}/100\n"
        reasoning += f"- Cost efficiency: {scores['cost_score']:.1f}/100\n"
        reasoning += f"\nOverall score: {scores['total_score']:.1f}/100"

        return reasoning
```

---

## Implementation Tasks

### Task 7.1: Database Schema & Models
- [ ] Create `model_registry` table
- [ ] Create `model_test_runs` table
- [ ] Create `model_assignments` table
- [ ] Create `golden_dataset_jobs` table
- [ ] Add database migrations
- [ ] Create ORM models

### Task 7.2: Golden Dataset Creation
- [ ] Select 100 diverse jobs (tech, healthcare, finance, etc.)
- [ ] Manually analyze and create "ground truth" results for Tier 1
- [ ] Store in `golden_dataset_jobs` table
- [ ] Version control (v1, v2, etc.)
- [ ] Document dataset characteristics

### Task 7.3: Model Testing Engine
- [ ] Implement `ModelTestEngine` class
- [ ] Implement `_test_model_tier1()` method
- [ ] Implement accuracy calculation logic
- [ ] Implement performance metrics collection
- [ ] Add error handling and logging

### Task 7.4: Model Recommender
- [ ] Implement weighted scoring algorithm
- [ ] Generate human-readable recommendations
- [ ] Add manual override capability
- [ ] Implement A/B testing support

### Task 7.5: Scheduler & Automation
- [ ] Weekly automated test scheduler
- [ ] Email/Slack reporting
- [ ] Auto-update model assignments (with approval)
- [ ] Rollback mechanism if quality degrades

### Task 7.6: Dashboard & Reporting
- [ ] Model performance comparison charts
- [ ] Historical trend analysis
- [ ] Cost projection calculator
- [ ] Export test results

---

## Test Schedule

**Weekly Testing (Sunday 1:00 AM):**
```
1:00 AM: Run Tier 1 model comparison
├─ Test: gemini-2.0-flash-lite-001 (speed champion)
├─ Test: gemini-2.0-flash-001 (current default)
├─ Test: gemini-1.5-flash (stable baseline)
└─ Test: gemini-1.5-pro (accuracy champion)

1:30 AM: Run Tier 2 model comparison
├─ Test: gemini-2.0-flash-001 (current)
└─ Test: gemini-1.5-flash (alternative)

2:00 AM: Run Tier 3 model comparison
├─ Test: gemini-2.0-flash-001 (current)
└─ Test: gemini-1.5-pro (high reasoning)

2:30 AM: Analyze results and generate report
3:00 AM: Email/Slack summary with recommendations
```

---

## Success Metrics

- [ ] Automated weekly tests running successfully
- [ ] 100-job golden dataset created and validated
- [ ] Model recommendations generated with >80% confidence
- [ ] 2+ model switches identified that improve performance
- [ ] Performance tracking dashboard operational

---

## Expected Outcomes

Based on testing, we anticipate:

**Tier 1**: Switch to `gemini-2.0-flash-lite-001`
- **Speed**: 2x faster (0.5-1s vs 1-3s)
- **Accuracy**: ~95% (acceptable for extraction tasks)
- **Cost**: Same (free tier)

**Tier 2**: Keep `gemini-2.0-flash-001`
- Balanced reasoning + speed needed

**Tier 3**: Upgrade to `gemini-1.5-pro`
- **Reasoning**: 15% better strategic insights
- **Speed**: 1.5x slower (acceptable for overnight batch)
- **Cost**: Same (free tier)

**Net Impact**:
- Tier 1: 2x faster = more jobs processed per hour
- Tier 3: Better quality = improved cover letter guidance
- Overall: Same cost, better performance

---

## Deliverables

1. Database schema for model testing system
2. Golden dataset (100 jobs with ground truth)
3. `ModelTestEngine` implementation
4. Weekly scheduler
5. Reporting dashboard
6. Documentation

---

## Timeline

- **Week 1**: Database schema + golden dataset creation
- **Week 2**: Test engine implementation
- **Week 3**: Scheduler + automation
- **Week 4**: Dashboard + first production test run

**Total**: 1 month
