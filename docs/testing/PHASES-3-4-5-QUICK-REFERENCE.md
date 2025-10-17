# Phases 3, 4, & 5: Quick Reference Guide
**Path to 95% Coverage**

---

## Phase 3: Resilience & Storage (Week 4, 5-6 days)

### 🎯 Goal
Test failure recovery and storage systems

### 📦 Modules (714 lines to cover)
- `failure_recovery.py` (260 lines, 0% → 80%)
- `retry_strategy_manager.py` (210 lines, 0% → 80%)
- `data_consistency_validator.py` (244 lines, 0% → 80%)
- `local_storage.py` (104 lines, 22% → 70%)
- `google_drive_storage.py` (207 lines, 14% → 70%)
- `storage_factory.py` (71 lines, 38% → 70%)

### ✅ Deliverables
- [ ] 6 test files created (50+ tests)
- [ ] Resilience: 80% coverage
- [ ] Storage: 70% coverage
- [ ] 2 integration tests

### 📝 Key Tests
**Resilience:**
- Retry logic (exponential backoff, max attempts)
- Checkpoint creation/restoration
- Error classification
- Recovery strategies

**Storage:**
- File upload/download
- Metadata preservation
- Folder organization
- Error handling (disk full, permissions)
- Google Drive auth & quota

### ⚡ Quick Start
```bash
# Day 1-3: Resilience
cd tests/unit
touch test_failure_recovery_manager.py
touch test_retry_strategy_manager.py
touch test_data_consistency_validator.py

# Day 4-5: Storage
touch test_local_storage.py
touch test_google_drive_storage.py
touch test_storage_factory.py

# Day 6: Integration
cd tests/integration
touch test_resilience_with_storage.py
```

---

## Phase 4: Dashboard & Analytics (Week 5, 3-4 days)

### 🎯 Goal
Test user interfaces and tracking systems

### 📦 Modules (610 lines to cover)
- `dashboard_api.py` (125 lines, 0% → 60%)
- `dashboard_api_v2.py` (136 lines, 0% → 60%)
- `engagement_analytics.py` (118 lines, 0% → 70%)
- `engagement_analytics_api.py` (70 lines, 0% → 70%)
- `metrics.py` (117 lines, 0% → 50%)
- `logging_config.py` (64 lines, 0% → 50%)

### ✅ Deliverables
- [ ] 6 test files created (40+ tests)
- [ ] Dashboard APIs: 60% coverage
- [ ] Analytics: 70% coverage
- [ ] Observability: 50% coverage
- [ ] 2 integration tests

### 📝 Key Tests
**Dashboard:**
- Endpoint availability
- Data retrieval (jobs, applications)
- Filtering & search
- Pagination
- Real-time updates (WebSocket)

**Analytics:**
- Event tracking (job views, applications)
- Metrics calculation (DAU, conversion rate)
- Funnel analysis
- Report generation

**Observability:**
- Metrics recording (counter, gauge, histogram)
- Prometheus export
- Structured logging

### ⚡ Quick Start
```bash
# Day 1-2: Dashboard
cd tests/unit
touch test_dashboard_api.py
touch test_dashboard_api_v2.py

# Day 3: Analytics
touch test_engagement_analytics.py
touch test_engagement_analytics_api.py

# Day 4: Observability & Integration
touch test_observability_metrics.py
touch test_logging_config.py
cd tests/integration
touch test_dashboard_with_analytics.py
```

---

## Phase 5: Integration & E2E (Week 6, 5-6 days)

### 🎯 Goal
Fix integration tests & verify complete workflows

### 🔧 Fix Integration Tests (21 failures)
- [ ] Sequential batch workflow (19 tests)
- [ ] Calendly integration (1 test)
- [ ] Link tracking (1 test)

### 🚀 Create E2E Tests (4 workflows)
- [ ] Complete application (scrape → analyze → generate → send)
- [ ] Document generation (template → data → validate → store)
- [ ] Batch processing (import → analyze → rank)
- [ ] Email workflow (generate → send → track)

### 🔄 CI/CD Pipeline
- [ ] GitHub Actions workflow
- [ ] PostgreSQL service
- [ ] Coverage reporting (Codecov)
- [ ] Pre-commit hooks
- [ ] Status badges

### ✅ Deliverables
- [ ] All 21 integration tests passing
- [ ] 4 E2E test files (12+ tests)
- [ ] CI/CD pipeline operational
- [ ] **95% coverage achieved**

### 📝 Key Fixes
**Time-Dependent Tests:**
```python
with patch('datetime.datetime') as mock:
    mock.now.return_value = datetime(2025, 10, 12, 9, 0)
```

**Database State:**
```python
@pytest.fixture
def test_db_with_jobs():
    db = get_test_database()
    db.bulk_insert("jobs", test_data)
    yield db
    db.clear_all_tables()
```

**External Services:**
```python
@pytest.fixture
def mock_gemini():
    with patch('GeminiClient') as mock:
        mock.analyze.return_value = {...}
        yield mock
```

### ⚡ Quick Start
```bash
# Day 1-2: Fix Integration Tests
cd tests/integration
# Review test_sequential_batch_workflow.py
# Fix time mocking, database state, service mocks

# Day 3-4: Create E2E Tests
cd tests/e2e
touch test_complete_application_workflow.py
touch test_document_generation_workflow.py
touch test_batch_processing_workflow.py
touch test_email_application_workflow.py

# Day 5: CI/CD Setup
mkdir -p .github/workflows
touch .github/workflows/tests.yml
touch .pre-commit-config.yaml

# Day 6: Final Verification
pytest tests/ --cov=modules --cov-report=html
open htmlcov/index.html  # Verify ≥95%
```

---

## Timeline Summary

```
Week 4: Phase 3 (Resilience & Storage)
├─ Day 1-3: Resilience tests (3 files, 30+ tests)
├─ Day 4-5: Storage tests (3 files, 20+ tests)
└─ Day 6:   Integration tests (2 scenarios)

Week 5: Phase 4 (Dashboard & Analytics)
├─ Day 1-2: Dashboard API tests (2 files, 20+ tests)
├─ Day 3:   Analytics tests (2 files, 15+ tests)
└─ Day 4:   Observability & integration (3 files, 10+ tests)

Week 6: Phase 5 (Integration & E2E)
├─ Day 1-2: Fix integration tests (21 fixes)
├─ Day 3-4: E2E workflow tests (4 files, 12+ tests)
├─ Day 5:   CI/CD pipeline setup
└─ Day 6:   Final verification & celebration 🎉
```

---

## Coverage Progress Tracker

```
Current:  23% (2,587 / 11,230 lines)
Target:   95% (10,669 / 11,230 lines)
Gap:      8,082 lines to cover

Phase 3:  +2,000 lines  (→ 41%)
Phase 4:  +1,500 lines  (→ 54%)
Phase 5:  +4,582 lines  (→ 95%)
```

---

## Essential Commands

### Run Tests
```bash
# Single phase
pytest tests/unit/test_failure_recovery_manager.py -v

# Full phase
pytest tests/unit/ -v
pytest tests/integration/ -v
pytest tests/e2e/ -v

# With coverage
pytest tests/ --cov=modules --cov-report=html
```

### Check Coverage
```bash
# Generate report
coverage report -m

# View in browser
open htmlcov/index.html

# Check specific module
coverage report --include="modules/resilience/*"
```

### CI/CD
```bash
# Install pre-commit
pre-commit install

# Run manually
pre-commit run --all-files

# Push to trigger CI
git push origin develop
```

---

## Success Criteria Checklist

### Phase 3
- [ ] 6 test files created
- [ ] 50+ tests written
- [ ] Resilience modules: ≥80% coverage
- [ ] Storage modules: ≥70% coverage
- [ ] All tests passing

### Phase 4
- [ ] 6 test files created
- [ ] 40+ tests written
- [ ] Dashboard APIs: ≥60% coverage
- [ ] Analytics: ≥70% coverage
- [ ] Observability: ≥50% coverage
- [ ] All tests passing

### Phase 5
- [ ] All 21 integration tests fixed
- [ ] 4 E2E test files created
- [ ] 12+ E2E tests written
- [ ] CI/CD pipeline operational
- [ ] **95% coverage achieved**
- [ ] All tests passing consistently

---

## Quick Tips

### Writing Tests
1. **Start simple** - Happy path first, edge cases later
2. **Mock external calls** - Don't hit real APIs
3. **Clean up** - Use fixtures with proper teardown
4. **Be explicit** - Clear assertions, descriptive names
5. **Test behavior** - Not implementation details

### Debugging Failures
1. **Read the error** - Full traceback has clues
2. **Use debugger** - Step through with pdb
3. **Check logs** - Often reveal root cause
4. **Isolate the issue** - Run single test
5. **Mock more** - Remove external dependencies

### Staying on Track
1. **Track daily progress** - Check off completed tests
2. **Don't skip hard tests** - They're usually important
3. **Ask for help early** - Don't spend hours stuck
4. **Celebrate small wins** - Each test passing counts
5. **Keep end goal in mind** - 95% coverage is achievable!

---

## Resources

**Full Guides:**
- Phase 3: `docs/testing/phase-3-resilience-storage-guide.md`
- Phase 4: `docs/testing/phase-4-dashboard-analytics-guide.md`
- Phase 5: `docs/testing/phase-5-integration-e2e-guide.md`

**Other Docs:**
- Testing Strategy: `docs/testing/testing-strategy.md`
- Comprehensive Report: `docs/testing/comprehensive-testing-report.md`
- Quick Summary: `docs/testing/TESTING-SUMMARY.md`

---

**Total Estimated Time:** 14-16 days
**Final Coverage Target:** ≥95%
**You've got this! 💪**
