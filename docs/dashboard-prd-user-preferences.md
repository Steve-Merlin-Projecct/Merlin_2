---
title: "Dashboard Prd User Preferences"
type: reference
component: general
status: draft
tags: []
---

# Product Requirements Document: User Preferences Dashboard

**Version:** 1.0.0
**Created:** 2025-10-12
**Target Worktree:** Dashboard development worktree
**Status:** Ready for implementation

---

## Executive Summary

Interactive dashboard interface for users to define job preferences through example scenarios and visualize learned acceptance criteria in real-time.

## Problem Statement

Users need to communicate complex job acceptance criteria involving trade-offs between salary, commute, work hours, career growth, and other factors. Current `preferences.html` is designed for the old package-based system and doesn't support the new regression-based learning.

## Solution

Rebuild preferences dashboard to support:
1. **Scenario-based input** - Users define 1-5 example acceptable jobs
2. **Real-time regression** - System learns trade-offs as scenarios are added
3. **Visual feedback** - 2D charts show learned acceptance boundaries
4. **Job preview** - Test acceptance prediction on hypothetical jobs

---

## User Stories

### Core Functionality

**US-1: Define Preference Scenarios**
> As a user, I want to describe 1-5 example jobs I find acceptable, so the system learns my preferences.

**Acceptance Criteria:**
- Form supports all 11 preference variables (see spec below)
- Can save 1-5 scenarios with unique names
- Each scenario has acceptance score slider (0-100)
- Missing variables are optional (handled gracefully)
- Visual feedback when scenarios saved

---

**US-2: Train Preference Model**
> As a user, I want to train my preference model from my scenarios, so the system can evaluate jobs automatically.

**Acceptance Criteria:**
- "Train Model" button triggers training
- Loading indicator during training (~100ms)
- Success message shows formula and R² score
- Feature importance displayed visually
- Training errors shown with actionable messages

---

**US-3: Visualize Trade-offs**
> As a user, I want to see how my preferences trade off factors against each other, so I understand what the system learned.

**Acceptance Criteria:**
- 2D charts show factor pairs (e.g., Salary vs. Commute)
- User scenarios plotted as colored points
- Acceptance boundary line/curve displayed
- Dropdown to select which factor pair to view
- Chart updates in real-time as scenarios change

---

**US-4: Preview Job Acceptance**
> As a user, I want to test my model on hypothetical jobs, so I can validate it learned correctly.

**Acceptance Criteria:**
- Form to input job variables
- Real-time acceptance prediction
- Score, decision (accept/reject), and confidence shown
- Explanation of which factors influenced decision
- Can iterate on test jobs quickly

---

## Technical Specifications

### Frontend Components

#### 1. Scenario Manager
**Location:** Left panel, 60% width

**Elements:**
- Scenario tabs (1-5) with add/delete buttons
- Per-scenario form fields:
  - Text input: Scenario name (e.g., "Local Job")
  - Number input: Salary ($)
  - Range slider: Job stress (1-10, inverted: lower is better)
  - Range slider: Career growth (1-10)
  - Number input: Commute time (minutes)
  - Range slider: Mission match (1-10)
  - Range slider: Industry preference (1-10)
  - Number input: Work hours per week
  - Range slider: Work hour flexibility (1-10)
  - Select dropdown: Work arrangement (onsite/hybrid/remote)
  - Range slider: Job title match (1-10)
  - Range slider: Company prestige (1-10)
  - **Range slider: Acceptance score (0-100) ⭐ Most important**
- Save scenarios button
- Clear all button

**Behavior:**
- Variables default to middle values (5/10, 40 hours, etc.)
- Can leave fields empty (optional variables)
- Real-time validation (salary > 0, scores 1-10, etc.)
- Scenarios saved to database on "Save" click

#### 2. Model Training Panel
**Location:** Top of right panel, 40% width

**Elements:**
- Current model status indicator:
  - ❌ Not trained
  - ✅ Trained (timestamp, R² score)
- "Train Model" button (primary action)
- Formula display (human-readable)
- Feature importance bar chart

**Behavior:**
- Button disabled if < 1 scenario
- AJAX call to `/preferences/train`
- Loading spinner during training
- Success: Update status, show formula
- Error: Display message (e.g., "Need at least 1 complete scenario")

#### 3. Trade-off Visualization
**Location:** Middle of right panel

**Elements:**
- Dropdown: Select factor pair
  - Salary vs. Commute
  - Salary vs. Work Hours
  - Career Growth vs. Commute
  - (All meaningful combinations)
- 2D scatter plot (Chart.js or Plotly):
  - X-axis: Factor 1
  - Y-axis: Factor 2
  - Points: User scenarios (colored by acceptance score)
  - Line/curve: Learned acceptance boundary
- Legend explaining colors

**Behavior:**
- Chart updates when scenarios change
- Chart updates after model training
- Hover shows scenario details
- Responsive to panel resize

#### 4. Job Preview Panel
**Location:** Bottom of right panel

**Elements:**
- Simplified job input form (key variables only):
  - Salary
  - Commute
  - Work hours
  - Career growth
  - Work arrangement
- "Evaluate" button
- Result display:
  - Acceptance score (0-100) with color gradient
  - Decision: ✅ APPLY or ❌ SKIP
  - Confidence meter (0-100%)
  - Explanation bullets (top 3 factors)

**Behavior:**
- Real-time evaluation on input change (debounced)
- Or explicit "Evaluate" button
- Requires trained model (disabled otherwise)
- AJAX call to `/preferences/evaluate`

---

### Backend Integration

#### API Endpoints (Already Implemented)

```
POST /preferences/save
- Save user scenarios to database

POST /preferences/train
- Train regression model from scenarios
- Returns: formula, feature_importance, training stats

POST /preferences/evaluate
- Evaluate job against trained model
- Returns: should_apply, acceptance_score, confidence, explanation

GET /preferences/model-info
- Get current model status and formula

GET /preferences/scenarios
- Load user's saved scenarios
```

#### Data Flow

1. **Page Load:**
   - GET `/preferences/scenarios` → Populate scenario forms
   - GET `/preferences/model-info` → Update model status panel

2. **Save Scenarios:**
   - User fills forms → Click "Save"
   - POST `/preferences/save` with scenario JSON
   - Success: Show confirmation toast

3. **Train Model:**
   - User clicks "Train Model"
   - POST `/preferences/train`
   - Success: Update formula display, feature chart, status
   - Generate visualization data for charts

4. **Preview Job:**
   - User inputs job variables → Click "Evaluate" (or auto)
   - POST `/preferences/evaluate` with job JSON
   - Success: Display score, decision, confidence, explanation

---

### Visualization Specifications

#### 2D Trade-off Chart

**Library:** Chart.js (already in use) or Plotly (more advanced)

**Data Structure:**
```javascript
{
  scenarios: [
    {x: 70000, y: 20, label: "Local Job", acceptance: 75, color: "green"},
    {x: 90000, y: 60, label: "High Salary", acceptance: 70, color: "yellow"},
    // ...
  ],
  boundary: [
    {x: 60000, y: 10, accepted: true},
    {x: 70000, y: 30, accepted: true},
    {x: 80000, y: 50, accepted: false},
    // Points to draw acceptance boundary line
  ]
}
```

**Chart Configuration:**
- Type: Scatter with line overlay
- Colors: Green (>75), Yellow (50-75), Red (<50)
- Axes: Labeled with variable names and units
- Responsive: True
- Animation: Smooth transitions

**Boundary Calculation:**
- Generate grid of (x, y) test points
- Evaluate each point using trained model
- Find acceptance threshold contour
- Draw as line or curve

#### Feature Importance Bar Chart

**Library:** Chart.js horizontal bar chart

**Data Structure:**
```javascript
{
  labels: ["Salary", "Career Growth", "Commute"],
  data: [35, 32, 28],  // Percentage weights
  colors: ["#4CAF50", "#2196F3", "#FFC107"]
}
```

---

### UI/UX Guidelines

#### Visual Design

- **Color Scheme:** Match existing dashboard theme
- **Acceptance Gradient:**
  - 80-100: Dark green (excellent)
  - 60-80: Light green (good)
  - 40-60: Yellow (borderline)
  - 20-40: Orange (poor)
  - 0-20: Red (reject)

#### Interactions

- **Auto-save:** Optional (can implement draft saving)
- **Undo/Redo:** Not required for MVP
- **Keyboard Shortcuts:** Not required for MVP
- **Mobile Responsive:** Yes, stack panels vertically

#### Accessibility

- Proper ARIA labels on sliders
- Keyboard navigation support
- Color-blind friendly palette (use patterns + colors)
- Screen reader announcements for dynamic updates

---

### Error Handling

**Scenario Validation:**
- Salary must be > 0
- Scores must be 1-10
- Acceptance score required (0-100)
- Show inline error messages

**Training Errors:**
- "Need at least 1 complete scenario"
- "Acceptance score required for all scenarios"
- "Training failed: [technical error]"

**Evaluation Errors:**
- "Model not trained yet - train first"
- "Invalid job data"
- Network errors with retry button

---

## Implementation Phases

### Phase 1: Core Functionality (MVP)
- [ ] Scenario input forms (all 11 variables)
- [ ] Save scenarios to database
- [ ] Train model button + status display
- [ ] Formula display
- [ ] Feature importance chart
- [ ] Basic 2D visualization (1 factor pair)
- [ ] Job preview panel with evaluation

**Estimated:** 8-12 hours

### Phase 2: Enhanced Visualization
- [ ] Multiple factor pair options in dropdown
- [ ] Acceptance boundary overlay on charts
- [ ] Interactive scenario points (hover details)
- [ ] Chart animations

**Estimated:** 4-6 hours

### Phase 3: Polish
- [ ] Auto-save drafts
- [ ] Better error messages
- [ ] Loading states
- [ ] Mobile responsive
- [ ] Accessibility improvements

**Estimated:** 4-6 hours

---

## Testing Requirements

### Unit Tests
- JavaScript validation logic
- Chart data preparation functions
- API response handling

### Integration Tests
- Full workflow: Add scenarios → Train → Evaluate
- API endpoint integration
- Data persistence

### User Acceptance Tests
- Can a user define preferences in < 5 minutes?
- Do visualizations make sense to non-technical users?
- Does model training feel fast enough (<1 second)?

---

## Success Metrics

**Quantitative:**
- 90%+ of users successfully train a model
- < 5 clicks to define and train preferences
- < 200ms API response time for evaluation

**Qualitative:**
- Users understand what the model learned
- Users trust the model's decisions
- Visualizations feel intuitive

---

## Out of Scope

- Multi-user preference sharing
- Preference templates/presets
- Historical preference tracking
- Mobile app version
- Advanced ML explanations (SHAP values, etc.)

---

## Dependencies

**Backend:** Already implemented (`modules/user_preferences/`)
**Frontend:** Existing `preferences.html` (needs rebuild)
**Database:** Migration `004_user_preferences_tables.sql` (needs to run)

---

## Deployment Notes

1. Run database migration:
   ```bash
   psql -U postgres -d local_Merlin_3 -f database_migrations/004_user_preferences_tables.sql
   ```

2. Install Python dependencies (already in requirements.txt):
   ```bash
   pip install scikit-learn joblib
   ```

3. Register blueprint (already done in `app_modular.py`)

4. Deploy updated `preferences.html` template

---

## Questions for Dashboard Team

1. **Chart Library:** Prefer Chart.js (simpler) or Plotly (more features)?
2. **Auto-save:** Implement draft saving or require explicit save?
3. **Mobile:** Stack panels vertically or separate mobile view?
4. **Integration:** Update existing `preferences.html` or create new route?

---

## Appendix: Example Scenario Data

```json
{
  "scenario_name": "Ideal Local Job",
  "salary": 75000,
  "job_stress": 4,
  "career_growth": 8,
  "commute_time_minutes": 15,
  "mission_match": 9,
  "industry_preference": 8,
  "work_hours_per_week": 40,
  "work_hour_flexibility": 7,
  "work_arrangement": 2,
  "job_title_match": 8,
  "company_prestige": 7,
  "acceptance_score": 85
}
```

---

**Status:** Ready for dashboard worktree implementation
**Contact:** See `docs/user-preferences-system.md` for technical details
