# User Preferences System

**Version:** 1.0.0
**Created:** 2025-10-12
**Status:** Active

## Overview

Multi-variable regression-based system that learns user job preferences from 1-5 example scenarios and evaluates job opportunities automatically.

## Problem Statement

Users need to communicate their job acceptance criteria to the system, but:
- Job desirability involves trade-offs between multiple factors (salary, commute, hours, growth, etc.)
- Users can't easily articulate mathematical weights for each factor
- Simple threshold-based rules don't capture nuanced preferences
- Preferences may vary by context (local vs. remote, high salary vs. short commute)

## Solution

**Preference Learning System:** Users provide 1-5 example scenarios of jobs they find acceptable, rate each scenario (0-100), and the system uses regression to infer trade-offs and generate an acceptance formula.

### Key Features

1. **Flexible Variable Support** - Handle any combination of 11 preference variables
2. **Missing Data Handling** - Works when users don't specify all variables
3. **Scenario-Based Learning** - Learn from examples, not explicit rules
4. **Automatic Formula Generation** - Mathematical model inferred from scenarios
5. **Job Scoring** - Evaluate new jobs automatically with confidence scores

## Architecture

### Components

```
modules/user_preferences/
├── preference_regression.py    # Multi-variable regression engine
├── job_scorer.py               # Job evaluation against preferences
├── preference_db.py            # Database operations
├── preference_routes.py        # Flask web interface
└── __init__.py
```

### Database Schema

**Tables:**
- `user_preference_scenarios` - User's 1-5 input scenarios
- `user_preference_models` - Trained regression models (serialized)
- `job_preference_scores` - Cached job evaluation results

See: `database_migrations/004_user_preferences_tables.sql`

### Supported Preference Variables (26 total)

#### Core Compensation & Work (11 variables)
| Variable | Type | Description |
|----------|------|-------------|
| `salary` | numeric | Annual salary |
| `job_stress` | 1-10 | Estimated stress level (lower is better) |
| `career_growth` | 1-10 | Growth opportunity |
| `commute_time_minutes` | numeric | Commute time (lower is better) |
| `mission_match` | 1-10 | Mission alignment |
| `industry_preference` | 1-10 | Industry match |
| `work_hours_per_week` | numeric | Expected hours (lower is better) |
| `work_hour_flexibility` | 1-10 | Schedule flexibility |
| `work_arrangement` | 1-3 | 1=onsite, 2=hybrid, 3=remote |
| `job_title_match` | 1-10 | Title match |
| `company_prestige` | 1-10 | Company reputation |

#### Job Characteristics (4 variables)
| Variable | Type | Description |
|----------|------|-------------|
| `job_type` | 1-3 | 1=part-time, 2=contract, 3=full-time |
| `company_size` | 1-5 | 1=startup, 2=small, 3=medium, 4=large, 5=enterprise |
| `team_size` | numeric | Number of people on team |
| `management_responsibilities` | 1-10 | 1=no supervision, 10=large team management |

#### Benefits & Compensation (5 variables)
| Variable | Type | Description |
|----------|------|-------------|
| `equity_offered` | 1-10 | Stock options/equity quality |
| `vacation_days` | numeric | Days per year |
| `benefits_quality` | 1-10 | Health, dental, vision quality |
| `bonus_potential` | 0-100 | Percent of salary |
| `professional_development` | 1-10 | Training budget, conference attendance |

#### Work-Life Balance (2 variables)
| Variable | Type | Description |
|----------|------|-------------|
| `travel_percent` | 0-100 | Percent time traveling (lower is better) |
| `management_autonomy` | 1-10 | 1=micromanaged, 10=autonomous |

#### Impact & Culture (3 variables)
| Variable | Type | Description |
|----------|------|-------------|
| `product_stage` | 1-10 | 1=early/greenfield, 10=mature/maintenance |
| `social_impact` | 1-10 | Social/environmental impact |
| `diversity_culture` | 1-10 | D&I culture quality |

#### Contract-Specific (1 variable)
| Variable | Type | Description |
|----------|------|-------------|
| `contract_length_months` | numeric | For contract roles |

**Note:** All variables are optional - system adapts to provided data. Variables marked "lower is better" are automatically inverted during model training.

## Usage

### 1. Training Preference Model

```python
from modules.user_preferences import PreferenceRegression

# Define user scenarios
scenarios = [
    {
        'scenario_name': 'Local Edmonton Job',
        'salary': 70000,
        'commute_time_minutes': 20,
        'work_hours_per_week': 40,
        'career_growth': 7,
        'work_arrangement': 2,  # hybrid
        'vacation_days': 15,
        'management_responsibilities': 2,  # no supervision preferred
        'benefits_quality': 7,
        'professional_development': 8
    },
    {
        'scenario_name': 'High Salary Remote',
        'salary': 100000,
        'commute_time_minutes': 0,
        'work_hours_per_week': 45,
        'career_growth': 9,
        'work_arrangement': 3  # remote
    },
    {
        'scenario_name': 'Minimum Acceptable',
        'salary': 60000,
        'commute_time_minutes': 30,
        'work_hours_per_week': 40,
        'career_growth': 5
    }
]

# User rates each scenario (0-100)
acceptance_scores = [75, 90, 50]

# Train model
model = PreferenceRegression(user_id='steve_glen')
result = model.train_from_scenarios(scenarios, acceptance_scores)

print(result['formula'])  # Human-readable formula
print(result['feature_importance'])  # Variable weights
```

### 2. Evaluating Jobs

```python
from modules.user_preferences import JobScorer

scorer = JobScorer(user_id='steve_glen')

job = {
    'salary': 75000,
    'commute_time_minutes': 15,
    'work_hours_per_week': 40,
    'career_growth': 8,
    'work_arrangement': 2
}

evaluation = scorer.evaluate_job(job)

if evaluation['should_apply']:
    print(f"Apply! Score: {evaluation['acceptance_score']}")
    print(f"Reasons: {evaluation['explanation']}")
else:
    print(f"Skip. Score: {evaluation['acceptance_score']}")
```

### 3. Integration with Scraping Pipeline

```python
from modules.user_preferences import evaluate_job_for_user

# In scraping pipeline
for job in scraped_jobs:
    evaluation = evaluate_job_for_user('steve_glen', {
        'salary': job['salary_low'],
        'commute_time_minutes': calculate_commute(job['location']),
        'career_growth': estimate_growth(job['description']),
        # ... other variables
    })

    if evaluation['should_apply']:
        queue_for_application(job)
```

## Web Interface

### Endpoints

**Configuration Page:**
```
GET /preferences/
```
Shows current scenarios and model status.

**Save Scenarios:**
```
POST /preferences/save
Content-Type: application/json

{
  "user_id": "steve_glen",
  "scenarios": [
    {
      "scenario_name": "Local Job",
      "salary": 70000,
      "commute_time_minutes": 20,
      "acceptance_score": 75
    }
  ]
}
```

**Train Model:**
```
POST /preferences/train
Content-Type: application/json

{
  "user_id": "steve_glen"
}
```

**Evaluate Job:**
```
POST /preferences/evaluate
Content-Type: application/json

{
  "user_id": "steve_glen",
  "job": {
    "salary": 75000,
    "commute_time_minutes": 20,
    "career_growth": 8
  }
}
```

**Get Model Info:**
```
GET /preferences/model-info?user_id=steve_glen
```

## Technical Details

### Regression Models

**1-2 Scenarios:** Ridge regression (prevents overfitting with small data)
**3+ Scenarios:** Random Forest (captures non-linear relationships)

### Feature Normalization

- StandardScaler normalizes all features to comparable scale
- Inverse variables (stress, commute) are inverted so higher = better
- Missing variables default to neutral middle values

### Confidence Scoring

Confidence = distance from acceptance threshold / 50

- High confidence: Score far from threshold (clear accept/reject)
- Low confidence: Score near threshold (borderline case)

### Model Persistence

- Models serialized to PostgreSQL using `pickle`
- One active model per user at a time
- Job scores cached to avoid recomputation

## Dashboard Integration

### Product Requirements Document

**Location:** Create in dashboard worktree
**Status:** Specification ready

**Required Features:**

1. **Scenario Input Interface**
   - Form for 1-5 scenarios with all 11 variables
   - Sliders for 1-10 scales
   - Number inputs for salary, hours, commute
   - Acceptance score slider (0-100) per scenario
   - Save/delete scenario management

2. **Real-Time Visualization**
   - 2D trade-off charts (e.g., Salary vs. Commute)
   - Show user scenarios as points
   - Display learned acceptance boundary
   - Interactive: click factor pairs to view different charts

3. **Formula Display**
   - Human-readable formula generated from model
   - Feature importance bar chart
   - Training statistics (R², scenario count)

4. **Job Evaluation Preview**
   - Test job input form
   - Real-time acceptance prediction
   - Explanation of decision factors

**Integration Points:**
- Use existing Flask routes (`/preferences/*`)
- Call JavaScript from existing `preferences.html` template
- Extend with AJAX for real-time updates

## Testing

Run tests:
```bash
python -c "
from modules.user_preferences import PreferenceRegression

model = PreferenceRegression('test_user')
scenarios = [
    {'salary': 70000, 'commute_time_minutes': 20, 'career_growth': 7},
    {'salary': 90000, 'commute_time_minutes': 60, 'career_growth': 8},
    {'salary': 60000, 'commute_time_minutes': 10, 'career_growth': 6}
]
acceptance_scores = [75, 70, 85]

result = model.train_from_scenarios(scenarios, acceptance_scores)
print('✓ Model trained:', result['model_type'])
print('✓ Formula:', model.get_formula_display())
"
```

## Migration Guide

### From Old `preference_packages.py` System

**Old system:** Hardcoded scenario packages (Local Edmonton, Regional Alberta, Remote)
**New system:** User-defined regression-based learning

**Migration steps:**
1. Keep old system for backward compatibility
2. Add preference model training UI to dashboard
3. Allow users to opt-in to new system
4. Eventually deprecate package system

**Advantages of new system:**
- User-specific (not hardcoded for "Steve Glen")
- Learns from examples (not manual rules)
- Handles any combination of variables
- More accurate trade-off inference

## Performance Considerations

- **Training:** ~100ms for 3 scenarios (acceptable for on-demand training)
- **Prediction:** ~10ms per job (fast enough for pipeline integration)
- **Caching:** Job scores cached in database to avoid recomputation
- **Batch Evaluation:** Use `evaluate_job_batch()` for multiple jobs

## Future Enhancements

1. **Active Learning:** Suggest scenarios for user to rate to improve model
2. **Explanation Improvements:** Better natural language explanations
3. **Multi-User Defaults:** Learn from aggregated user preferences
4. **Confidence Calibration:** Improve confidence score accuracy
5. **Model Versioning:** Track model changes over time
6. **A/B Testing:** Compare user-defined vs. system-suggested preferences

## Troubleshooting

**Issue:** Model not loading
**Solution:** Check that model was trained and saved to database

**Issue:** Low confidence scores
**Solution:** Add more diverse scenarios or increase scenario count

**Issue:** Unexpected acceptance decisions
**Solution:** Review feature importance and add scenarios to clarify trade-offs

**Issue:** Missing sklearn dependency
**Solution:** `pip install scikit-learn joblib` (added to requirements.txt)

## References

- Code: `modules/user_preferences/`
- Database: `database_migrations/004_user_preferences_tables.sql`
- Tests: `tests/test_user_preferences.py`
- Frontend: `frontend_templates/preferences.html`
