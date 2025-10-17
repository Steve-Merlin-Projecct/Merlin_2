# Phase 5: Integration & End-to-End Testing Guide
**Timeline:** Week 6 (5-6 working days)
**Goal:** Fix integration tests and verify complete workflows work end-to-end

---

## Overview

Phase 5 is the final push to 95% coverage. We'll fix the 21 failing integration tests, create comprehensive end-to-end tests for critical workflows, and establish the CI/CD pipeline.

**Current Integration Test Failures:**
- Sequential batch workflow tests: 19 failures
- Calendly workflow integration: 1 failure
- Link tracking integration: 1 failure

**E2E Workflows to Test:**
- Complete job application workflow (scrape → analyze → generate → send)
- Document generation workflow (template → data → validation → storage)
- Batch processing workflow (multiple jobs → analysis → prioritization)
- Email application workflow (generate docs → validate → send → track)

---

## Part A: Fix Integration Tests (2-3 days)

### 1. Sequential Batch Workflow Tests

**File:** `tests/integration/test_sequential_batch_workflow.py`

**Current Issues:**
- 19 failures related to batch scheduler
- Tests expect specific time windows
- Database state issues

**Fixing Strategy:**

#### Step 1: Review Test Expectations
```python
# Read the test file to understand what's expected
def test_tier1_batch_execution():
    """Original test - understand what it's checking"""
    # Tests sequential batch processing for tier 1 jobs
    # Expects jobs to be analyzed in order
    # May depend on specific time windows
```

#### Step 2: Fix Time-Dependent Tests
```python
def test_tier1_batch_execution_fixed():
    """Fixed test with mocked time"""
    from unittest.mock import patch
    from datetime import datetime

    # Mock current time to be within tier1 window
    with patch('datetime.datetime') as mock_datetime:
        mock_datetime.now.return_value = datetime(2025, 10, 12, 9, 0)  # 9 AM

        scheduler = SequentialBatchScheduler()
        result = scheduler.run_tier1_batch(job_ids=[1, 2, 3])

        assert result['status'] == 'success'
        assert len(result['analyzed_jobs']) == 3

def test_no_active_tier_outside_windows_fixed():
    """Fixed test for time window detection"""
    with patch('datetime.datetime') as mock_datetime:
        # Set time to 2 AM (outside all windows)
        mock_datetime.now.return_value = datetime(2025, 10, 12, 2, 0)

        scheduler = SequentialBatchScheduler()
        active_tier = scheduler.get_active_tier()

        assert active_tier is None
```

#### Step 3: Fix Database Dependencies
```python
@pytest.fixture
def test_db_with_jobs():
    """Fixture that provides clean database with test jobs"""
    db = get_test_database()

    # Add test jobs
    jobs = [
        {"id": 1, "title": "Job 1", "status": "pending_analysis"},
        {"id": 2, "title": "Job 2", "status": "pending_analysis"},
        {"id": 3, "title": "Job 3", "status": "pending_analysis"}
    ]
    db.bulk_insert("jobs", jobs)

    yield db

    # Cleanup
    db.clear_all_tables()

def test_tier1_batch_execution_with_db(test_db_with_jobs):
    """Test with proper database setup"""
    scheduler = SequentialBatchScheduler(db=test_db_with_jobs)

    result = scheduler.run_tier1_batch()

    # Verify jobs were processed
    processed_jobs = test_db_with_jobs.query("SELECT * FROM jobs WHERE status = 'analyzed'")
    assert len(processed_jobs) >= 1
```

#### Step 4: Fix Service Dependencies
```python
@pytest.fixture
def mock_gemini_service():
    """Mock Gemini AI service for batch tests"""
    with patch('modules.ai_job_description_analysis.tier1_analyzer.GeminiClient') as mock:
        # Mock successful analysis response
        mock.return_value.analyze.return_value = {
            "match_score": 85,
            "analysis": "Good match",
            "recommendations": ["Apply soon"]
        }
        yield mock

def test_tier1_batch_execution_with_mock_services(test_db_with_jobs, mock_gemini_service):
    """Test with mocked external services"""
    scheduler = SequentialBatchScheduler(db=test_db_with_jobs)

    result = scheduler.run_tier1_batch()

    assert result['status'] == 'success'
    assert mock_gemini_service.called
```

**Checklist for Each Failing Test:**
- [ ] Identify what the test is checking
- [ ] Mock time-dependent operations
- [ ] Ensure clean database state
- [ ] Mock external services (Gemini AI, Apify)
- [ ] Fix assertions to match actual behavior
- [ ] Verify test passes consistently

---

### 2. Calendly Workflow Tests

**File:** `tests/integration/test_calendly_workflow.py`

**Current Issue:**
- 1 failure in link tracking integration

**Fix Approach:**

```python
def test_create_tracked_link_integration_fixed():
    """Fixed test for creating tracked Calendly link"""
    from modules.link_tracking.link_tracker import LinkTracker

    tracker = LinkTracker()

    # Create tracked link
    tracked_url = tracker.create_tracked_link(
        original_url="https://calendly.com/user/meeting",
        job_id=123,
        application_id=456,
        link_type="calendly"
    )

    # Verify link was created
    assert tracked_url is not None
    assert "calendly.com" in tracked_url

    # Verify link can be retrieved
    link_info = tracker.get_link_info(tracked_url)
    assert link_info['job_id'] == 123
    assert link_info['application_id'] == 456
    assert link_info['link_type'] == "calendly"

def test_template_engine_calendly_integration():
    """Test Calendly URL integration with template engine"""
    from modules.content.document_generation.template_engine import TemplateEngine

    engine = TemplateEngine()

    # Process template with Calendly variable
    result = engine.process_template(
        template_content="Schedule interview: {{CALENDLY_URL}}",
        variables={"CALENDLY_URL": "https://calendly.com/user/meeting"},
        job_id=123,
        application_id=456
    )

    # Verify tracked link was inserted
    assert "calendly.com" in result
    # Link should be tracked (may have tracking parameter)
```

---

### 3. Link Tracking Integration Tests

**Review and Fix:**

```python
def test_link_click_tracking():
    """Test that link clicks are tracked"""
    from modules.link_tracking.link_tracker import LinkTracker

    tracker = LinkTracker()

    # Create tracked link
    tracked_url = tracker.create_tracked_link(
        original_url="https://example.com/job",
        job_id=123,
        application_id=456
    )

    # Simulate click
    response = tracker.record_click(tracked_url, user_agent="Test Browser")

    # Verify click was recorded
    assert response['status'] == 'success'

    # Verify analytics were updated
    clicks = tracker.get_link_clicks(tracked_url)
    assert len(clicks) == 1
    assert clicks[0]['user_agent'] == "Test Browser"
```

---

## Part B: End-to-End Tests (2-3 days)

### 1. Complete Job Application Workflow

**File:** `tests/e2e/test_complete_application_workflow.py`

**What to Test:**

```python
@pytest.mark.e2e
def test_full_application_workflow(test_app, test_db):
    """
    Test complete workflow: Scrape → Analyze → Generate → Send

    This is the most critical E2E test - it verifies the entire system works together.
    """

    # Step 1: Scrape job posting
    from modules.scraping.job_scraper import scrape_indeed_job

    job_url = "https://www.indeed.com/viewjob?jk=test_job_12345"
    job_data = scrape_indeed_job(job_url)

    assert job_data is not None
    assert 'title' in job_data
    assert 'company' in job_data
    assert 'description' in job_data

    # Save to database
    job_id = test_db.insert_job(job_data)
    assert job_id > 0

    # Step 2: Analyze job with AI
    from modules.ai_job_description_analysis.ai_analyzer import analyze_job

    analysis = analyze_job(job_id)

    assert analysis is not None
    assert 'match_score' in analysis
    assert analysis['match_score'] > 0
    assert 'key_requirements' in analysis

    # Step 3: Generate application documents
    from modules.content.document_generation.document_generator import generate_documents

    documents = generate_documents(
        job_id=job_id,
        document_types=['resume', 'cover_letter']
    )

    assert len(documents) == 2
    assert documents[0]['type'] == 'resume'
    assert documents[1]['type'] == 'cover_letter'
    assert all(doc['file_path'] for doc in documents)

    # Step 4: Send application via email
    from modules.email_integration.gmail_oauth_official import send_application_email

    email_result = send_application_email(
        to="hr@company.com",
        subject=f"Application for {job_data['title']}",
        body="Please find my application attached.",
        attachments=[doc['file_path'] for doc in documents],
        job_id=job_id
    )

    assert email_result['status'] == 'sent'
    assert 'message_id' in email_result

    # Step 5: Verify final database state
    application = test_db.get_application_by_job_id(job_id)

    assert application is not None
    assert application['status'] == 'submitted'
    assert application['email_sent_at'] is not None
    assert application['documents_generated'] == 2

    # Step 6: Verify analytics tracked everything
    from modules.analytics.engagement_analytics import get_events_for_job

    events = get_events_for_job(job_id)

    assert any(e['event_type'] == 'job_scraped' for e in events)
    assert any(e['event_type'] == 'job_analyzed' for e in events)
    assert any(e['event_type'] == 'documents_generated' for e in events)
    assert any(e['event_type'] == 'email_sent' for e in events)
```

**Assertions:**
- Each step completes successfully
- Data flows correctly between steps
- Database state is consistent
- Analytics tracking works
- No errors in any component

---

### 2. Document Generation Workflow

**File:** `tests/e2e/test_document_generation_workflow.py`

```python
@pytest.mark.e2e
def test_complete_document_generation(test_app, test_db, tmp_path):
    """
    Test: Template Selection → Data Population → Validation → Storage
    """

    # Step 1: Load template
    from modules.content.document_generation.template_engine import TemplateEngine

    engine = TemplateEngine()
    template_path = "templates/resume_professional.docx"

    # Step 2: Prepare data
    job_data = {
        "title": "Senior Python Developer",
        "company": "Tech Corp",
        "requirements": ["Python", "Django", "PostgreSQL"]
    }

    user_data = {
        "name": "John Doe",
        "email": "john@example.com",
        "skills": ["Python", "Django", "PostgreSQL", "Docker"]
    }

    # Step 3: Generate document
    document = engine.generate_document(
        template_path=template_path,
        job_data=job_data,
        user_data=user_data
    )

    assert document is not None
    assert isinstance(document, bytes)

    # Step 4: Validate document
    from modules.content.document_generation.content_validator import validate_document

    validation = validate_document(document)

    assert validation['is_valid'] is True
    assert validation['has_required_sections'] is True
    assert validation['word_count'] > 200

    # Step 5: Security scan
    from modules.content.document_generation.docx_security_scanner import scan_document

    scan_result = scan_document(document)

    assert scan_result['is_safe'] is True
    assert len(scan_result['threats']) == 0

    # Step 6: Store document
    from modules.storage.storage_factory import StorageFactory

    storage = StorageFactory().get_default_storage()
    file_id = storage.store(
        content=document,
        filename="resume_john_doe.docx",
        metadata={"job_id": 123, "type": "resume"}
    )

    assert file_id is not None

    # Step 7: Verify retrieval
    retrieved_document = storage.retrieve(file_id)
    assert retrieved_document == document

    # Step 8: Verify metadata
    metadata = storage.get_metadata(file_id)
    assert metadata['job_id'] == 123
    assert metadata['type'] == "resume"
```

---

### 3. Batch Processing Workflow

**File:** `tests/e2e/test_batch_processing_workflow.py`

```python
@pytest.mark.e2e
def test_batch_job_analysis(test_app, test_db):
    """
    Test: Bulk Job Import → Batch Analysis → Priority Ranking
    """

    # Step 1: Import multiple jobs
    from modules.scraping.batch_scraper import scrape_job_batch

    job_urls = [
        "https://indeed.com/viewjob?jk=job_001",
        "https://indeed.com/viewjob?jk=job_002",
        "https://indeed.com/viewjob?jk=job_003",
        "https://indeed.com/viewjob?jk=job_004",
        "https://indeed.com/viewjob?jk=job_005"
    ]

    scraped_jobs = scrape_job_batch(job_urls)
    assert len(scraped_jobs) == 5

    # Save to database
    job_ids = [test_db.insert_job(job) for job in scraped_jobs]

    # Step 2: Batch analyze with AI
    from modules.ai_job_description_analysis.batch_analyzer import analyze_batch

    analyses = analyze_batch(job_ids)

    assert len(analyses) == 5
    assert all('match_score' in a for a in analyses)

    # Step 3: Rank by priority
    from modules.ai_job_description_analysis.sequential_batch_scheduler import prioritize_jobs

    prioritized = prioritize_jobs(job_ids)

    assert len(prioritized) == 5
    # Should be sorted by match score (descending)
    scores = [p['match_score'] for p in prioritized]
    assert scores == sorted(scores, reverse=True)

    # Step 4: Verify top candidates are flagged
    top_jobs = test_db.query(
        "SELECT * FROM jobs WHERE priority = 'high' ORDER BY match_score DESC LIMIT 2"
    )

    assert len(top_jobs) == 2
    assert all(job['match_score'] >= 80 for job in top_jobs)

    # Step 5: Verify analytics
    from modules.analytics.engagement_analytics import get_batch_processing_metrics

    metrics = get_batch_processing_metrics()

    assert metrics['jobs_processed'] == 5
    assert metrics['average_processing_time_ms'] < 60000  # Under 1 minute
```

---

### 4. Email Application Workflow

**File:** `tests/e2e/test_email_application_workflow.py`

```python
@pytest.mark.e2e
def test_email_application_with_tracking(test_app, test_db):
    """
    Test: Generate Docs → Validate → Attach → Send → Track Opens
    """

    job_id = 123

    # Step 1: Generate documents
    from modules.content.document_generation.document_generator import generate_documents

    documents = generate_documents(
        job_id=job_id,
        document_types=['resume', 'cover_letter']
    )

    assert len(documents) == 2

    # Step 2: Generate email content with tracked links
    from modules.email_integration.dynamic_email_generator import generate_email_content

    email_content = generate_email_content(
        job_id=job_id,
        include_calendly=True,
        include_portfolio=True
    )

    assert 'calendly.com' in email_content['body']
    assert 'portfolio_url' in email_content

    # Step 3: Validate email content
    from modules.email_integration.email_validator import validate_email

    validation = validate_email(
        to="hr@company.com",
        subject=email_content['subject'],
        body=email_content['body']
    )

    assert validation['is_valid'] is True

    # Step 4: Send email
    from modules.email_integration.gmail_oauth_official import send_email

    result = send_email(
        to="hr@company.com",
        subject=email_content['subject'],
        body=email_content['body'],
        attachments=[doc['file_path'] for doc in documents]
    )

    assert result['status'] == 'sent'
    message_id = result['message_id']

    # Step 5: Verify link tracking is active
    from modules.link_tracking.link_tracker import get_tracked_links_for_job

    tracked_links = get_tracked_links_for_job(job_id)

    assert len(tracked_links) >= 2  # Calendly + Portfolio
    assert all(link['status'] == 'active' for link in tracked_links)

    # Step 6: Simulate link click
    calendly_link = [l for l in tracked_links if 'calendly' in l['url']][0]

    from modules.link_tracking.link_redirect_handler import handle_click

    click_result = handle_click(calendly_link['tracking_id'])

    assert click_result['redirect_url'] == calendly_link['original_url']

    # Step 7: Verify analytics
    from modules.analytics.engagement_analytics import get_email_metrics

    metrics = get_email_metrics(message_id)

    assert metrics['sent'] is True
    assert metrics['links_clicked'] == 1
    assert 'calendly' in metrics['clicked_links'][0]
```

---

## Part C: CI/CD Pipeline Setup (1 day)

### 1. GitHub Actions Workflow

**File:** `.github/workflows/tests.yml`

```yaml
name: Test Suite

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  unit-tests:
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: test_password
          POSTGRES_DB: test_db
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Cache dependencies
        uses: actions/cache@v3
        with:
          path: ~/.cache/pip
          key: ${{ runner.os }}-pip-${{ hashFiles('requirements.txt') }}

      - name: Install dependencies
        run: |
          pip install --upgrade pip
          pip install -r requirements.txt
          pip install -r requirements-test.txt

      - name: Run unit tests
        env:
          DATABASE_URL: postgresql://postgres:test_password@localhost:5432/test_db
          WEBHOOK_API_KEY: test_api_key
        run: |
          pytest tests/unit/ -v --cov=modules --cov-report=xml --cov-report=term

      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml
          flags: unittests

  integration-tests:
    runs-on: ubuntu-latest
    needs: unit-tests

    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: test_password
          POSTGRES_DB: test_db
        ports:
          - 5432:5432

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r requirements-test.txt

      - name: Run integration tests
        env:
          DATABASE_URL: postgresql://postgres:test_password@localhost:5432/test_db
        run: |
          pytest tests/integration/ -v --cov=modules --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml
          flags: integration

  e2e-tests:
    runs-on: ubuntu-latest
    needs: integration-tests

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r requirements-test.txt

      - name: Run E2E tests
        run: |
          pytest tests/e2e/ -v --tb=short

  quality-checks:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install black flake8 vulture

      - name: Run Black
        run: black --check modules/ tests/

      - name: Run Flake8
        run: flake8 modules/ tests/ --max-line-length=100

      - name: Run Vulture (dead code detection)
        run: vulture modules/ --min-confidence 80
```

### 2. Pre-commit Hooks

**File:** `.pre-commit-config.yaml`

```yaml
repos:
  - repo: local
    hooks:
      - id: pytest-check
        name: pytest-check
        entry: pytest tests/unit/ -x
        language: system
        pass_filenames: false
        always_run: true

      - id: black
        name: black
        entry: black
        language: system
        types: [python]

      - id: flake8
        name: flake8
        entry: flake8
        language: system
        types: [python]
        args: [--max-line-length=100]
```

### 3. Coverage Badge

**File:** `README.md` (update)

```markdown
# Automated Job Application System

![Tests](https://github.com/username/repo/actions/workflows/tests.yml/badge.svg)
![Coverage](https://codecov.io/gh/username/repo/branch/main/graph/badge.svg)
![Python](https://img.shields.io/badge/python-3.11-blue.svg)

## Test Coverage

- **Overall:** 95%+ coverage
- **Unit Tests:** 90%+ coverage
- **Integration Tests:** 85%+ coverage
```

---

## Quick Implementation Checklist

### Day 1-2: Fix Integration Tests
- [ ] Review all 21 failing integration tests
- [ ] Fix sequential batch workflow tests (19 tests)
  - [ ] Mock time-dependent operations
  - [ ] Fix database state issues
  - [ ] Mock external services
- [ ] Fix Calendly workflow test (1 test)
- [ ] Fix link tracking test (1 test)
- [ ] Verify all integration tests pass

### Day 3-4: Create E2E Tests
- [ ] Create `test_complete_application_workflow.py`
  - [ ] Test scrape → analyze → generate → send
- [ ] Create `test_document_generation_workflow.py`
  - [ ] Test template → data → validation → storage
- [ ] Create `test_batch_processing_workflow.py`
  - [ ] Test bulk import → batch analysis → ranking
- [ ] Create `test_email_application_workflow.py`
  - [ ] Test generate → validate → send → track
- [ ] Run all E2E tests
- [ ] Fix any failures

### Day 5: CI/CD Setup
- [ ] Create `.github/workflows/tests.yml`
- [ ] Set up PostgreSQL service for tests
- [ ] Configure coverage reporting
- [ ] Add Codecov integration
- [ ] Create pre-commit hooks
- [ ] Test CI/CD pipeline
- [ ] Add status badges to README

### Day 6: Final Verification
- [ ] Run full test suite locally
- [ ] Verify coverage is ≥95%
- [ ] Run CI/CD pipeline on GitHub
- [ ] Fix any remaining issues
- [ ] Document known limitations
- [ ] Create release notes

---

## Success Criteria

**Integration Tests:**
- [ ] All 21 integration tests passing
- [ ] No flaky tests (pass 10 times in a row)
- [ ] Integration test coverage ≥85%

**E2E Tests:**
- [ ] At least 4 complete workflow tests
- [ ] All critical paths covered
- [ ] E2E tests stable and reliable

**CI/CD:**
- [ ] GitHub Actions workflow running
- [ ] Tests run on every PR
- [ ] Coverage reported automatically
- [ ] Pre-commit hooks installed

**Overall:**
- [ ] **95%+ code coverage achieved**
- [ ] All tests passing consistently
- [ ] Documentation complete
- [ ] CI/CD pipeline operational

---

## Common Pitfalls to Avoid

1. **Don't skip flaky test investigation** - Fix them, don't ignore
2. **Don't hardcode credentials in CI** - Use GitHub Secrets
3. **Don't make E2E tests too brittle** - Mock external services
4. **Don't test implementation details** - Test behavior
5. **Handle timing issues** - Use explicit waits, not sleep()
6. **Clean up resources** - Close connections, delete temp files
7. **Don't rely on test execution order** - Each test independent

---

## Tips for Success

1. **Start with failing tests** - Understand why they fail
2. **Fix one at a time** - Don't try to fix everything at once
3. **Use debugger** - Step through failing tests
4. **Check logs** - Often reveal root cause
5. **Mock aggressively** - Don't rely on external services
6. **Keep E2E simple** - Test happy path primarily
7. **Document assumptions** - Make test expectations clear

---

**Estimated Time:** 5-6 days
**Difficulty:** Medium-High
**Dependencies:** Phases 1-4 complete
**Outcome:** 95% coverage achieved, production-ready test suite

---

## Final Validation

Before declaring success:

```bash
# Run full test suite
pytest tests/ -v

# Check coverage
pytest tests/ --cov=modules --cov-report=html
open htmlcov/index.html

# Verify coverage is ≥95%
grep "TOTAL" htmlcov/index.html

# Run tests 10 times (check for flaky tests)
for i in {1..10}; do pytest tests/ -x || break; done

# Run CI/CD pipeline
git push origin develop
# Watch GitHub Actions

# Celebrate! 🎉
```

Once all checks pass, you've achieved **95% operational test coverage**!
