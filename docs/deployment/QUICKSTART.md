---
title: Quick Start Guide
type: guide
created: 2024-10-15
modified: 2025-10-21
status: current
related: README.md, CLAUDE.md
---

# User Preferences Dashboard - Quick Start Guide

**5-Minute Setup and Testing Guide**

---

## Prerequisites Check

```bash
# 1. Database migration applied?
psql -U postgres -d local_Merlin_3 -c "\dt user_preference*"
# Should show: user_preference_scenarios, user_preference_models, job_preference_scores

# 2. Python dependencies installed?
python -c "import sklearn; print('✓ scikit-learn installed')"
python -c "import joblib; print('✓ joblib installed')"
```

If migrations not applied:
```bash
psql -U postgres -d local_Merlin_3 -f database_migrations/004_user_preferences_tables.sql
```

If dependencies missing:
```bash
pip install scikit-learn joblib
```

---

## Quick Test (5 Minutes)

### Step 1: Start Flask App
```bash
python app_modular.py
```

Should see:
```
 * Running on http://127.0.0.1:5000/
```

### Step 2: Open Browser
Navigate to: `http://localhost:5000/preferences/`

You should see:
- **Left Panel:** "Job Scenarios" with "Add Scenario" button
- **Right Panel:** "Model Status" showing "❌ Not Trained"
- Clean dark theme UI

### Step 3: Create First Scenario
1. Click **"Add Scenario"**
2. Enter name: "Local Job"
3. Fill in:
   - Salary: 75000
   - Commute: 20 minutes
   - Work Hours: 40
   - Work Arrangement: Hybrid
   - Career Growth: 7 (slider)
4. Scroll down to **"How acceptable is this job?"**
5. Set slider to **80/100**
6. Click **"Save All"**

Expected: Green toast notification "✓ Scenarios saved successfully!"

### Step 4: Add Two More Scenarios
**Scenario 2: "High Salary Remote"**
- Salary: 95000
- Commute: 0
- Work Hours: 45
- Arrangement: Remote
- Career Growth: 9
- Acceptance: **90/100**

**Scenario 3: "Minimum Acceptable"**
- Salary: 60000
- Commute: 30
- Work Hours: 40
- Arrangement: Onsite
- Career Growth: 5
- Acceptance: **50/100**

Click **"Save All"** after each.

### Step 5: Train Model
1. Click **"Train Model"** button in right panel
2. Wait ~100ms for training
3. You should see:
   - ✅ Model Trained (badge turns green)
   - Learned formula displayed
   - Feature importance bar chart appears
   - Trade-off chart appears
   - Job preview panel appears

Expected formula example:
```
Acceptance = 0.35×Salary + 0.28×Career_Growth - 0.22×Commute + ...
```

### Step 6: Test Job Preview
In **"Test Your Model"** panel (bottom right):
1. Enter:
   - Salary: 80000
   - Commute: 15
   - Work Hours: 40
   - Career Growth: 8
2. Click **"Evaluate Job"**

Expected:
- ✅ **APPLY** (green badge)
- Score: ~75-85/100
- Confidence: ~70-90%
- Explanation showing why

Try poor job:
- Salary: 50000
- Commute: 60
- Work Hours: 55
- Career Growth: 3

Expected: ❌ **SKIP** (red badge)

### Step 7: Explore Trade-offs
In **"Trade-off Explorer"** panel:
1. Select X-Axis: "Salary"
2. Select Y-Axis: "Commute Time Minutes"
3. View scatter plot showing your 3 scenarios
4. Points colored by acceptance score:
   - Green (90) = High salary remote
   - Light green (80) = Local job
   - Yellow (50) = Minimum acceptable

---

## Automated Test

```bash
# Run full integration test suite
python test_preferences_integration.py
```

Expected output:
```
============================================================
USER PREFERENCES DASHBOARD INTEGRATION TESTS
============================================================

TEST 1: Save Scenarios
Status: 200
✅ Scenarios saved successfully

TEST 2: Train Model
📊 Model Details:
  Model Type: RandomForestRegressor
  R² Score: 0.87
✅ Model trained successfully

TEST 3: Evaluate Job - Good Job
📈 Evaluation:
  Should Apply: True
  Acceptance Score: 78/100
✅ Job evaluated - Result: APPLY

TEST 4: Evaluate Job - Poor Job
📈 Evaluation:
  Should Apply: False
  Acceptance Score: 32/100
✅ Job evaluated - Result: SKIP

TEST 5: Get Model Info
✅ Model info retrieved successfully

============================================================
✅ ALL TESTS PASSED!
============================================================
```

---

## Troubleshooting

### Issue: Database tables not found
**Error:** `relation "user_preference_scenarios" does not exist`

**Solution:**
```bash
psql -U postgres -d local_Merlin_3 -f database_migrations/004_user_preferences_tables.sql
```

### Issue: Scikit-learn import error
**Error:** `ModuleNotFoundError: No module named 'sklearn'`

**Solution:**
```bash
pip install scikit-learn joblib
```

### Issue: Page shows old UI (8 static scenarios)
**Problem:** Old preferences.html still loaded

**Solution:**
```bash
# Verify new file exists
ls -lh frontend_templates/preferences.html
# Should be ~900 lines (new) not 1064 lines (old)

# If wrong file:
mv frontend_templates/preferences_old.html frontend_templates/preferences_backup.html
# Ensure preferences.html is the new ML-based version
```

### Issue: Charts not rendering
**Problem:** Chart.js CDN not loading

**Solution:**
- Check browser console (F12)
- Verify internet connection (CDN: cdn.jsdelivr.net)
- Or download Chart.js locally and update script src

### Issue: "Train Model" button disabled
**Problem:** No scenarios saved yet

**Solution:**
- Add at least 1 scenario
- Click "Save All"
- Button should enable

### Issue: API endpoints returning 500 error
**Problem:** Backend module not loaded

**Solution:**
```bash
# Verify blueprint registered in app_modular.py
grep "preference_bp" app_modular.py

# Should see:
# from modules.user_preferences import preference_bp
# app.register_blueprint(preference_bp)
```

---

## Verification Checklist

After setup, verify:

- [ ] Database tables exist (3 tables)
- [ ] Flask app runs without errors
- [ ] `/preferences/` page loads
- [ ] Can add/remove scenarios
- [ ] Can save scenarios (toast notification)
- [ ] Can train model (formula appears)
- [ ] Feature importance chart renders
- [ ] Trade-off scatter plot renders
- [ ] Can evaluate test jobs
- [ ] Integration tests pass

---

## Next Steps

1. **Read Full Documentation:**
   - `docs/user-preferences-dashboard-complete.md`
   - `docs/user-preferences-system.md`

2. **Customize for Your Use Case:**
   - Add more variables to UI (expand VARIABLES definition)
   - Adjust acceptance threshold (currently 50)
   - Customize colors/styling

3. **Integrate with Pipeline:**
   - Use trained model in job scraping
   - Filter jobs automatically
   - Track acceptance decisions

---

## Support

**Documentation:**
- Full implementation: `docs/user-preferences-dashboard-complete.md`
- Backend API: `modules/user_preferences/preference_routes.py`
- PRD: `docs/dashboard-prd-user-preferences.md`

**Code Locations:**
- Frontend: `frontend_templates/preferences.html`
- Backend: `modules/user_preferences/`
- Tests: `test_preferences_integration.py`

**Common Questions:**
- Q: Can I add more variables?
  - A: Yes! Backend supports 26, UI shows 13. Add more to VARIABLES definition.

- Q: How accurate is the model?
  - A: Depends on scenario quality. More diverse scenarios = better accuracy.

- Q: Can I export my scenarios?
  - A: Not yet - deferred to Phase 2. Data in PostgreSQL database.

---

**Status:** ✅ Ready for use - Follow steps above to test in 5 minutes!
