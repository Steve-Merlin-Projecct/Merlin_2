---
title: "Future User Preferences Dashboard Integration"
type: reference
component: integration
status: draft
tags: []
---

# Future Task: User Preferences Dashboard Integration

**Priority:** High
**Estimated Time:** 12-16 hours
**Dependencies:** User preferences backend (COMPLETE)
**Target Worktree:** Dashboard development worktree

---

## Status

✅ **Backend Complete** - All API endpoints and regression models implemented
⏸️ **Frontend Pending** - Dashboard UI needs to be built

---

## What's Done

### Backend Implementation ✅
- Multi-variable regression engine (26 variables)
- Job evaluation API with confidence scoring
- Database schema with 3 tables
- Flask routes registered and tested
- Complete documentation

**Files Ready:**
- `modules/user_preferences/` - All backend logic
- `docs/dashboard-prd-user-preferences.md` - Complete PRD
- `docs/user-preferences-system.md` - Technical documentation
- `database_migrations/004_user_preferences_tables.sql` - Schema

---

## What Needs to Be Done

### 1. Dashboard UI Implementation

#### Phase 1: Scenario Input Interface (4-6 hours)
**Location:** `/preferences` route (already exists)

**Components to Build:**
- [ ] Scenario tabs (1-5 scenarios with add/delete)
- [ ] Form fields for all 26 variables:
  - **Core** (11): salary, job_stress, career_growth, commute, mission, industry, hours, flexibility, arrangement, title, prestige
  - **Job Characteristics** (4): job_type, company_size, team_size, management_responsibilities
  - **Benefits** (5): equity, vacation_days, benefits_quality, bonus_potential, professional_development
  - **Work-Life** (2): travel_percent, management_autonomy
  - **Culture** (3): product_stage, social_impact, diversity_culture
  - **Contract** (1): contract_length_months
- [ ] Acceptance score slider per scenario (0-100) ⭐ Most important
- [ ] Save/clear buttons
- [ ] Form validation and error handling

**UI Guidelines:**
- Group variables by category (accordion or tabs)
- Use sliders for 1-10 scales
- Number inputs for salary, days, etc.
- Dropdowns for categorical (job_type, company_size, work_arrangement)
- Tooltips explaining each variable
- Progressive disclosure (basic vs advanced fields)

#### Phase 2: Model Training Panel (2-3 hours)
**Components:**
- [ ] Model status indicator (trained/not trained)
- [ ] "Train Model" button with loading state
- [ ] Formula display (human-readable)
- [ ] Feature importance bar chart (Chart.js)
- [ ] Training statistics (R², scenario count, timestamp)

**API Integration:**
```javascript
// Save scenarios
POST /preferences/save
Body: { user_id, scenarios: [...] }

// Train model
POST /preferences/train
Body: { user_id }
Response: { formula, feature_importance, train_r2 }
```

#### Phase 3: Trade-off Visualization (4-6 hours)
**Components:**
- [ ] Factor pair dropdown (select which 2 variables to plot)
- [ ] 2D scatter plot with Chart.js or Plotly:
  - User scenarios as points (colored by acceptance score)
  - Learned acceptance boundary line/curve
  - Interactive hover tooltips
- [ ] Legend explaining colors

**Factor Pairs to Support:**
- Salary vs Commute
- Salary vs Work Hours
- Career Growth vs Commute
- Vacation Days vs Salary
- Management Responsibilities vs Salary
- (Allow user to select any combination)

**Boundary Calculation:**
- Generate grid of test points
- Evaluate each with trained model
- Find acceptance threshold contour
- Draw as line or filled region

#### Phase 4: Job Preview Panel (2-3 hours)
**Components:**
- [ ] Simplified job input form (key variables)
- [ ] "Evaluate" button (or real-time with debounce)
- [ ] Result display:
  - Acceptance score gauge (0-100)
  - Decision badge: ✅ APPLY or ❌ SKIP
  - Confidence meter
  - Explanation bullets (top 3 factors)

**API Integration:**
```javascript
POST /preferences/evaluate
Body: { user_id, job: {...} }
Response: { should_apply, acceptance_score, confidence, explanation }
```

---

## Technical Implementation Notes

### API Endpoints (Already Implemented)

All endpoints are in `modules/user_preferences/preference_routes.py`:

```
GET  /preferences/                    - Main page
POST /preferences/save                - Save scenarios
POST /preferences/train               - Train model
POST /preferences/evaluate            - Evaluate job
GET  /preferences/model-info          - Get model status
GET  /preferences/scenarios           - Load scenarios
POST /preferences/delete-scenarios    - Delete scenarios
GET  /preferences/top-jobs           - Get top-scored jobs
```

### Database Migration Required

Before dashboard implementation:
```bash
psql -U postgres -d local_Merlin_3 -f database_migrations/004_user_preferences_tables.sql
```

Creates 3 tables:
- `user_preference_scenarios` (30 columns)
- `user_preference_models` (stores trained models)
- `job_preference_scores` (evaluation cache)

### Frontend Technologies

**Recommended:**
- HTML/Jinja2 templates (existing pattern)
- Chart.js for visualizations (already used in dashboard)
- Alpine.js or vanilla JS for interactivity
- AJAX for API calls

**Alternative:**
- Plotly.js for advanced visualizations
- React/Vue if converting to SPA (more work)

---

## User Flow

1. **User arrives at `/preferences`**
   - Page loads existing scenarios (if any)
   - Shows model status (trained or not)

2. **User defines scenarios**
   - Fill out 1-5 scenario forms
   - Select which variables matter to them
   - Rate each scenario's acceptability (0-100)
   - Click "Save Scenarios"

3. **User trains model**
   - Click "Train Model" button
   - See formula and feature weights
   - View trade-off visualization

4. **User tests model**
   - Input hypothetical job details
   - See if model would recommend applying
   - Review explanation of decision

5. **System uses model automatically**
   - Scraping pipeline evaluates jobs
   - Only shows user jobs above threshold
   - Saves time by filtering bad matches

---

## Variable Categories for UI

### Basic (Always Show)
- salary
- commute_time_minutes
- work_hours_per_week
- work_arrangement
- career_growth

### Advanced (Collapsible)
- Job characteristics (4 variables)
- Benefits (5 variables)
- Work-life balance (2 variables)
- Culture (3 variables)
- All other core variables

---

## Testing Requirements

### Unit Tests
- Form validation logic
- API response handling
- Chart data preparation

### Integration Tests
- Save → Train → Evaluate workflow
- Error handling
- Data persistence

### User Acceptance Tests
- Can user define preferences in <5 minutes?
- Do visualizations make sense?
- Does training feel fast enough?

---

## Success Criteria

**Quantitative:**
- [ ] 90%+ users successfully train model
- [ ] <5 clicks to define and train
- [ ] <200ms API response time
- [ ] All 26 variables accessible in UI

**Qualitative:**
- [ ] Users understand what model learned
- [ ] Users trust model's decisions
- [ ] Visualizations feel intuitive
- [ ] Interface feels polished

---

## Out of Scope (Future Enhancements)

- Multi-user preference sharing
- Preference templates/presets
- Historical preference tracking
- Mobile app version
- Advanced ML explanations (SHAP values)
- A/B testing different models
- Active learning (system suggests scenarios)

---

## Files to Reference

**PRD:** `docs/dashboard-prd-user-preferences.md`
**Technical Guide:** `docs/user-preferences-system.md`
**Backend Code:** `modules/user_preferences/`
**Database Schema:** `database_migrations/004_user_preferences_tables.sql`
**API Tests:** Use `/preferences/model-info` to verify backend working

---

## Deployment Checklist

Before starting dashboard work:
- [ ] Verify backend merged to main
- [ ] Run database migration
- [ ] Verify API endpoints responding
- [ ] Install sklearn: `pip install scikit-learn joblib`
- [ ] Test API manually with curl/Postman

---

## Questions for Dashboard Team

1. **Chart Library:** Chart.js (simpler) or Plotly (more features)?
2. **Auto-save:** Implement draft saving or require explicit save?
3. **Mobile:** Stack panels vertically or separate mobile view?
4. **Integration:** Update existing `preferences.html` or create new route?
5. **Variable Grouping:** Tabs, accordion, or single long form?

---

## Estimated Timeline

**Week 1:**
- Days 1-2: Scenario input forms (all 26 variables)
- Day 3: Model training panel + feature importance chart
- Day 4: Save/train API integration + error handling

**Week 2:**
- Days 5-6: Trade-off visualization (2D charts)
- Day 7: Job preview panel
- Day 8: Testing + polish + documentation

**Total:** 8 development days (12-16 hours)

---

## Contact

**Backend Implementation:** Complete and documented
**Technical Questions:** See `docs/user-preferences-system.md`
**API Examples:** See `docs/dashboard-prd-user-preferences.md`

**Status:** Ready for dashboard worktree implementation
**Priority:** High (enables automatic job filtering)
**Complexity:** Medium (straightforward UI, complex visualization)
