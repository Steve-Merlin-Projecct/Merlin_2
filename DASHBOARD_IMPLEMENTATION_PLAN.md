# Dashboard Enhancements - Detailed Implementation Plan

**Worktree:** dashboard-enhancements---fix-blocked-migrations-co
**Generated:** 2025-10-17
**Total Estimated Time:** 35-40 hours

---

## Executive Summary

This implementation plan breaks down the dashboard enhancements task into 8 major phases with clear dependencies, complexity ratings, and parallel work opportunities. The project builds upon an existing Dashboard V2 foundation (Alpine.js + Custom CSS) that is 100% complete for frontend and backend APIs but requires database migration fixes and additional views.

**Current State:**
- ✅ Dashboard V2 frontend complete (main dashboard, jobs view)
- ✅ Optimized API endpoints complete (80%+ performance improvement potential)
- ✅ Real-time SSE integration complete
- ✅ Caching layer complete
- ⚠️ Database migrations blocked by schema mismatch
- ❌ Additional views incomplete (Applications, Analytics, Schema)
- ❌ Search/filter functionality basic
- ❌ Export functionality missing
- ❌ PWA features missing
- ❌ Testing incomplete (23% coverage)

---

## Table of Contents

1. [Dependency Analysis](#dependency-analysis)
2. [Task Breakdown by Phase](#task-breakdown-by-phase)
3. [Recommended Implementation Order](#recommended-implementation-order)
4. [Parallel Work Opportunities](#parallel-work-opportunities)
5. [Risk Factors](#risk-factors)
6. [Success Criteria](#success-criteria)

---

## Dependency Analysis

### Dependency Tree

```
Phase 1: Fix Blocked Migrations (CRITICAL BLOCKER)
    └── Required for: Performance optimizations, production deployment
    └── Blocks: None (can work on frontend in parallel)
    └── Dependencies: Database access, schema inspection

Phase 2: Complete Dashboard Views
    ├── Applications View
    │   └── Depends on: Dashboard API v2 (✅ complete)
    ├── Analytics View
    │   └── Depends on: Chart.js integration, timeseries API (✅ complete)
    └── Schema Visualization
        └── Depends on: Database schema metadata

Phase 3: Search & Filters
    ├── Backend API endpoints
    │   └── Depends on: Dashboard API v2 structure
    └── Frontend UI components
        └── Depends on: Dashboard views (Phase 2)

Phase 4: Export Functionality
    └── Depends on: Dashboard views (Phase 2), API endpoints

Phase 5: PWA Features
    └── Depends on: All frontend views complete (Phase 2)
    └── Independent of: Backend optimizations

Phase 6: Hybrid Detection (AI-powered field detection)
    └── Depends on: Database migrations (Phase 1)
    └── Can run in parallel with: Frontend work (Phases 2-5)

Phase 7: Testing & Quality Assurance
    └── Depends on: All features implemented
    └── Can start in parallel: Unit tests as features are built

Phase 8: Production Deployment
    └── Depends on: All phases complete, tests passing
```

### Critical Path

**Longest path (determines minimum project duration):**
```
Phase 1 (Migrations) → Phase 6 (Hybrid Detection) → Phase 7 (Testing) → Phase 8 (Deployment)
Estimated: 4h + 8h + 10h + 6h = 28 hours minimum
```

### Parallel Work Opportunities

- **Track A (Backend):** Phase 1 → Phase 6 → Testing
- **Track B (Frontend):** Phase 2 → Phase 3 → Phase 4 → Phase 5 → Testing
- **Track C (Quality):** Testing can start immediately for existing code

---

## Task Breakdown by Phase

### Phase 1: Fix Blocked Migrations 🚨 CRITICAL

**Complexity:** Medium
**Estimated Time:** 3-4 hours
**Priority:** HIGHEST
**Dependencies:** None (blocking others)
**Can Parallel With:** Phase 2 (frontend work)

#### Subtasks

1. **Audit Database Schema** (30 min)
   - Connect to PostgreSQL: `local_Merlin_3`
   - Inspect tables: `jobs`, `job_applications`, `companies`, `analyzed_jobs`
   - Document actual column names vs. migration assumptions
   - Identify columns: compensation_currency (not salary_currency), seniority_level (not experience_level), synthesized location

2. **Fix Migration Files** (90 min)
   - Update `001_dashboard_optimization_indexes.sql`
     - Remove references to `priority_score`
     - Fix column names (seniority_level, compensation_currency)
     - Verify all indexed columns exist
   - Update `002_dashboard_materialized_views.sql`
     - Fix salary_currency → compensation_currency
     - Fix experience_level → seniority_level
     - Synthesize location from office_city, office_province, office_country
     - Use NULL placeholder for priority_score
   - Update `003_dashboard_aggregation_tables.sql`
     - Align all column references with actual schema
     - Update aggregation queries

3. **Test Migrations Safely** (45 min)
   - Create backup: `pg_dump -h localhost -U postgres local_Merlin_3 > backup_$(date +%Y%m%d).sql`
   - Run migrations: `python database_migrations/run_migrations.py`
   - Verify indexes created: Query `pg_indexes` table
   - Verify materialized views created: Query `pg_matviews` table
   - Test refresh functions work

4. **Backfill Aggregation Data** (30 min)
   - Run backfill scripts included in migration 003
   - Verify data populated in aggregation tables
   - Test dashboard API with real data

**Files Modified:**
- `database_migrations/001_dashboard_optimization_indexes.sql`
- `database_migrations/002_dashboard_materialized_views.sql`
- `database_migrations/003_dashboard_aggregation_tables.sql`

**Success Criteria:**
- ✅ All migrations run without errors
- ✅ Indexes created and verified
- ✅ Materialized views populated
- ✅ Dashboard API performance improved (250ms → <50ms)

**Known Issues:**
- Migration 002 already has fixes for some fields (lines 40-47)
- Need to verify if compensation_currency exists or if it's another field
- May need to handle NULL values gracefully

---

### Phase 2: Complete Dashboard Views 📊

**Complexity:** Medium-High
**Estimated Time:** 7-9 hours
**Priority:** HIGH
**Dependencies:** Dashboard API v2 (✅ complete)
**Can Parallel With:** Phase 1, Phase 3

#### Subtask 2.1: Applications View (2-3 hours)

**File:** `frontend_templates/dashboard_applications.html`

**Current State:** Basic structure exists with mock data loader

**Implementation:**
1. **Create API Endpoint** (45 min)
   - File: `modules/dashboard_api_v2.py`
   - Endpoint: `GET /api/v2/dashboard/applications`
   - Query: Fetch from `job_applications` table with joins to `jobs` and `companies`
   - Response: List of applications with job details, status, dates
   - Pagination: Support `?page=1&limit=50`
   - Filters: Support `?status=sent&date_from=2025-01-01`

2. **Update Frontend** (60 min)
   - Replace mock data fetch with real API call
   - Add timeline visualization (vertical timeline with status transitions)
   - Add status badges (sent, pending, rejected, interview, offer)
   - Add date filters (last 7 days, last 30 days, custom range)
   - Add status filters (all, sent, pending, etc.)
   - Add company filter (dropdown of companies)

3. **Enhance UI** (30 min)
   - Add application detail cards with expandable sections
   - Show documents sent (resume, cover letter)
   - Show email sent timestamp and recipient
   - Show response tracking (first_response_received_at, response_type)
   - Add tone metrics display (coherence, jump, travel scores)

**Success Criteria:**
- ✅ Fetches real application data
- ✅ Timeline visualization works
- ✅ Filters work correctly
- ✅ Responsive on mobile

#### Subtask 2.2: Analytics View (3-4 hours)

**File:** `frontend_templates/dashboard_analytics.html`

**Current State:** Basic structure with Chart.js imported, mock data

**Implementation:**
1. **Chart.js Integration** (90 min)
   - Create 4 charts:
     - **Applications Over Time:** Line chart (daily/weekly/monthly)
     - **Application Status:** Doughnut chart (sent, pending, rejected, etc.)
     - **Success Rate Trend:** Line chart (weekly success rate)
     - **Job Sources:** Bar chart (top job boards/sources)
   - Configure responsive charts
   - Add chart interactions (tooltips, legends, zoom)

2. **API Integration** (60 min)
   - Fetch from `/api/v2/dashboard/metrics/timeseries`
   - Support metrics: scraping_velocity, analysis_rate, application_rate, success_rate
   - Support periods: hourly, daily, weekly, monthly
   - Support ranges: 7d, 30d, 90d, 1y
   - Cache chart data client-side

3. **Stats Cards** (30 min)
   - Total jobs scraped
   - Total applications sent
   - Success rate (percentage)
   - Average response time
   - Fetch from `/api/v2/dashboard/overview`

4. **Recent Activity Feed** (30 min)
   - Show last 20 events (scraped, analyzed, applied)
   - Real-time updates via SSE
   - Timestamp formatting

**Success Criteria:**
- ✅ All 4 charts render correctly
- ✅ Charts update with real data
- ✅ Stats cards show accurate metrics
- ✅ Activity feed shows recent events
- ✅ Responsive on mobile

#### Subtask 2.3: Database Schema Visualization (2 hours)

**File:** `frontend_templates/dashboard_schema.html` (new)

**Implementation:**
1. **Create API Endpoint** (30 min)
   - File: `modules/dashboard_api_v2.py`
   - Endpoint: `GET /api/v2/dashboard/schema`
   - Query: Use SQLAlchemy inspector to get table metadata
   - Response: JSON with tables, columns, relationships, indexes

2. **Build Interactive Schema** (90 min)
   - Use D3.js or vis.js for graph visualization
   - Show tables as nodes
   - Show relationships as edges
   - Click table to see columns
   - Click column to see details (type, nullable, default, foreign keys)
   - Color-code by table type (jobs, applications, companies, etc.)
   - Add search to find tables/columns
   - Add zoom/pan controls

**Success Criteria:**
- ✅ Schema loads from database
- ✅ Interactive visualization works
- ✅ Click interactions show details
- ✅ Search finds tables/columns

**Files Created:**
- `frontend_templates/dashboard_applications.html` (enhanced)
- `frontend_templates/dashboard_analytics.html` (enhanced)
- `frontend_templates/dashboard_schema.html` (new)
- Updated `modules/dashboard_api_v2.py` with new endpoints

---

### Phase 3: Search & Filters 🔍

**Complexity:** Medium
**Estimated Time:** 4-5 hours
**Priority:** MEDIUM
**Dependencies:** Phase 2 (dashboard views)
**Can Parallel With:** Phase 4

#### Subtask 3.1: Backend Search API (2 hours)

**File:** `modules/dashboard_api_v2.py`

**Implementation:**
1. **Global Search Endpoint** (60 min)
   - Endpoint: `POST /api/v2/dashboard/search`
   - Full-text search across:
     - Job titles
     - Company names
     - Job descriptions
     - Locations
   - Use PostgreSQL `ts_vector` for full-text search
   - Support fuzzy matching with `pg_trgm`
   - Return results with relevance score
   - Pagination support

2. **Advanced Filter Endpoint** (60 min)
   - Endpoint: `GET /api/v2/dashboard/jobs/filter`
   - Filter parameters:
     - Salary range: `?salary_min=80000&salary_max=120000`
     - Location: `?location=Toronto`
     - Remote: `?remote=yes`
     - Job type: `?job_type=full-time`
     - Seniority: `?seniority=senior`
     - Application status: `?status=not_applied`
     - Date range: `?posted_after=2025-01-01`
     - Eligibility: `?eligible=true`
   - Combine multiple filters with AND logic
   - Support sorting: `?sort=salary_high&order=desc`

#### Subtask 3.2: Frontend Search UI (2-3 hours)

**Files:** All dashboard views

**Implementation:**
1. **Global Search Bar** (60 min)
   - Add to navigation header
   - Autocomplete as user types
   - Show results in dropdown
   - Navigate to job detail on click
   - Keyboard navigation (arrow keys, enter)

2. **Advanced Filter Panel** (90 min)
   - Collapsible sidebar/modal
   - Salary range slider
   - Location multiselect (from database)
   - Remote checkbox
   - Job type radio buttons
   - Seniority multiselect
   - Status multiselect
   - Date range picker
   - "Apply Filters" button
   - "Clear Filters" button

3. **Save Filter Presets** (30 min)
   - Save current filters as preset
   - Store in localStorage
   - Quick load from saved presets
   - Delete presets
   - Examples: "Remote $100k+", "Toronto Senior Roles"

**Success Criteria:**
- ✅ Global search works across all content
- ✅ Advanced filters narrow results correctly
- ✅ Multiple filters combine properly
- ✅ Filter presets save and load
- ✅ UI responsive and intuitive

---

### Phase 4: Export Functionality 📥

**Complexity:** Low-Medium
**Estimated Time:** 2-3 hours
**Priority:** MEDIUM
**Dependencies:** Phase 2 (dashboard views)
**Can Parallel With:** Phase 3, Phase 5

#### Subtask 4.1: Backend Export API (90 min)

**File:** `modules/dashboard_api_v2.py`

**Implementation:**
1. **CSV Export Endpoints** (45 min)
   - `GET /api/v2/dashboard/export/jobs?format=csv`
   - `GET /api/v2/dashboard/export/applications?format=csv`
   - `GET /api/v2/dashboard/export/analytics?format=csv`
   - Use Python `csv` module
   - Stream large files with chunked responses
   - Set proper Content-Disposition headers
   - Support filtering (export only visible results)

2. **JSON Export Endpoints** (45 min)
   - Same endpoints with `?format=json`
   - Pretty-printed JSON with indentation
   - Include metadata (export date, filter criteria, count)
   - Support nested objects for full data model

#### Subtask 4.2: Frontend Export UI (60-90 min)

**Implementation:**
1. **Export Buttons** (30 min)
   - Add to each view (Jobs, Applications, Analytics)
   - Download icon button in header
   - Dropdown for format selection (CSV, JSON)
   - Show loading spinner during export
   - Auto-download file

2. **Export Options Modal** (30 min)
   - Choose fields to include
   - Choose date range
   - Apply current filters to export
   - Show estimated file size
   - Preview first 10 rows

3. **Bulk Export** (30 min)
   - Export all data button in settings
   - Generate zip file with all CSVs
   - Include README with export metadata
   - Email download link for large exports

**Success Criteria:**
- ✅ CSV export works for all views
- ✅ JSON export works for all views
- ✅ Exports respect active filters
- ✅ Files download correctly
- ✅ Large exports don't timeout

**Files Modified:**
- `modules/dashboard_api_v2.py` (new endpoints)
- `frontend_templates/dashboard_jobs.html` (export button)
- `frontend_templates/dashboard_applications.html` (export button)
- `frontend_templates/dashboard_analytics.html` (export button)

---

### Phase 5: PWA Features 📱

**Complexity:** Medium
**Estimated Time:** 3-4 hours
**Priority:** LOW
**Dependencies:** Phase 2 (all views complete)
**Can Parallel With:** Phase 3, Phase 4, Phase 6

#### Subtask 5.1: PWA Manifest (45 min)

**File:** `static/manifest.json` (new)

**Implementation:**
```json
{
  "name": "Job Application Dashboard",
  "short_name": "JobDash",
  "description": "AI-powered job application tracking",
  "start_url": "/dashboard",
  "display": "standalone",
  "background_color": "#0a0a0a",
  "theme_color": "#00d9ff",
  "icons": [
    {
      "src": "/static/icons/icon-192.png",
      "sizes": "192x192",
      "type": "image/png"
    },
    {
      "src": "/static/icons/icon-512.png",
      "sizes": "512x512",
      "type": "image/png"
    }
  ],
  "orientation": "portrait",
  "categories": ["productivity", "business"]
}
```

1. Generate icons (192x192, 512x512)
2. Add manifest link to all HTML files
3. Test manifest validation

#### Subtask 5.2: Service Worker (120 min)

**File:** `static/sw.js` (new)

**Implementation:**
1. **Cache Strategy** (60 min)
   - Cache-first for static assets (CSS, JS, images)
   - Network-first for API calls with fallback
   - Stale-while-revalidate for dashboard data
   - Version-based cache invalidation

2. **Offline Support** (60 min)
   - Cache dashboard HTML
   - Cache recent job data
   - Show offline indicator
   - Queue actions for when back online
   - Sync when connection restored

3. **Background Sync** (optional)
   - Periodic background sync for new jobs
   - Show notification for new eligible jobs

#### Subtask 5.3: Installation Prompt (45 min)

**Implementation:**
1. **Add to Home Screen Banner** (30 min)
   - Detect if installable
   - Show custom install prompt after 3 visits
   - "Add to Home Screen" button
   - Remember if user dismissed

2. **App Installation** (15 min)
   - Test on Chrome (desktop + mobile)
   - Test on Safari (iOS)
   - Test on Firefox
   - Verify standalone mode works

**Success Criteria:**
- ✅ PWA installable on all browsers
- ✅ Works offline with cached data
- ✅ Service worker caches properly
- ✅ Install prompt shows correctly
- ✅ Standalone mode works (no browser UI)

**Files Created:**
- `static/manifest.json`
- `static/sw.js`
- `static/icons/icon-192.png`
- `static/icons/icon-512.png`

**Files Modified:**
- All HTML templates (add manifest link, SW registration)

---

### Phase 6: Hybrid Detection (AI-powered field detection fallback) 🤖

**Complexity:** High
**Estimated Time:** 8-10 hours
**Priority:** MEDIUM
**Dependencies:** Phase 1 (database migrations)
**Can Parallel With:** Phase 2, 3, 4, 5

#### Background

The system currently relies on structured API responses and database schema. Hybrid detection adds AI-powered field extraction as a fallback when structured data is missing or when scraping from sources without APIs.

#### Subtask 6.1: Design AI Detection System (90 min)

**Planning:**
1. Identify fields that often have missing data:
   - Salary range (often unstructured: "$80k-$100k/year")
   - Location (various formats: "Toronto, ON", "Remote (Canada)", "Hybrid - Vancouver")
   - Job type (full-time, part-time, contract)
   - Seniority (junior, mid, senior, lead)
   - Remote options
   - Benefits/perks

2. Choose detection strategy:
   - **Option A:** Use Gemini AI for extraction (slower, more accurate)
   - **Option B:** Use regex + NLP (faster, less accurate)
   - **Hybrid:** Regex first, AI fallback for complex cases

3. Design fallback pipeline:
   ```
   Structured Data Available? → Yes → Use structured data
                             ↓ No
   Try regex extraction → Success? → Yes → Use regex result
                       ↓ No
   Send to Gemini AI → Extract fields → Update database
   ```

#### Subtask 6.2: Implement Regex-Based Detection (2 hours)

**File:** `modules/ai_job_description_analysis/field_detector.py` (new)

**Implementation:**
1. **Salary Detection** (45 min)
   - Regex patterns:
     - "$80k - $100k" / "$80,000-$100,000"
     - "80-100k" / "80000-100000"
     - "Competitive salary"
   - Extract: salary_low, salary_high, compensation_currency
   - Handle: yearly, hourly, ranges, keywords

2. **Location Detection** (30 min)
   - Extract from patterns:
     - "Toronto, ON, Canada"
     - "Remote (US only)"
     - "Hybrid - Vancouver"
   - Determine: office_city, office_province, office_country, remote_options

3. **Job Type & Seniority Detection** (45 min)
   - Keywords for job_type: "full-time", "part-time", "contract", "internship"
   - Keywords for seniority: "junior", "senior", "lead", "principal", "staff"
   - Context-aware matching (avoid false positives)

#### Subtask 6.3: Implement AI-Based Detection (3 hours)

**File:** `modules/ai_job_description_analysis/ai_field_extractor.py` (new)

**Implementation:**
1. **Gemini Prompt Design** (60 min)
   ```python
   prompt = """
   Extract structured data from this job posting. Return JSON only.

   Job Posting:
   {job_description}

   Extract:
   {
     "salary_low": <number or null>,
     "salary_high": <number or null>,
     "compensation_currency": "USD|CAD|null",
     "location": {
       "city": "string or null",
       "province": "string or null",
       "country": "string or null"
     },
     "remote_options": "remote|hybrid|onsite|null",
     "job_type": "full-time|part-time|contract|internship|null",
     "seniority_level": "junior|mid|senior|lead|principal|null"
   }

   Rules:
   - Return null if field not mentioned
   - Normalize all values to categories above
   - Salary in annual amount if possible
   """
   ```

2. **API Integration** (60 min)
   - Use existing Gemini client from `ai_job_description_analysis`
   - Add field extraction endpoint
   - Handle API errors gracefully
   - Cache results to avoid re-extraction
   - Rate limit to avoid excessive API costs

3. **Validation & Normalization** (60 min)
   - Validate JSON response structure
   - Normalize values to database enums
   - Handle edge cases (conflicting data)
   - Log extraction confidence scores
   - Store raw extraction in JSON field for debugging

#### Subtask 6.4: Integrate Hybrid Detection Pipeline (2-3 hours)

**File:** `modules/ai_job_description_analysis/hybrid_detector.py` (new)

**Implementation:**
1. **Pipeline Orchestrator** (90 min)
   ```python
   def detect_fields(job_data: dict) -> dict:
       """Hybrid detection pipeline with structured → regex → AI fallback"""

       # Step 1: Use structured data if available
       if has_structured_data(job_data):
           return extract_structured(job_data)

       # Step 2: Try regex extraction
       regex_results = regex_detector.extract(job_data['description'])
       if is_confident(regex_results):
           return regex_results

       # Step 3: Fallback to AI extraction
       ai_results = ai_detector.extract(job_data['description'])
       return merge_results(regex_results, ai_results)
   ```

2. **Batch Processing** (60 min)
   - Process existing jobs with missing fields
   - SQL query: `SELECT * FROM jobs WHERE salary_low IS NULL OR location IS NULL`
   - Batch size: 50 jobs
   - Progress tracking
   - Error handling and retry logic

3. **API Endpoint** (30 min)
   - Endpoint: `POST /api/v2/jobs/{job_id}/detect-fields`
   - Trigger detection on-demand
   - Return detected fields for review before saving
   - Allow manual override

#### Subtask 6.5: Testing & Validation (90 min)

**Implementation:**
1. **Test Cases** (60 min)
   - Test regex detection on 20 sample job postings
   - Test AI detection on 10 complex postings
   - Test fallback pipeline
   - Measure accuracy vs. ground truth
   - Benchmark API costs (tokens used)

2. **Integration Testing** (30 min)
   - Test with existing job ingestion pipeline
   - Verify database updates correctly
   - Check for race conditions
   - Monitor performance impact

**Success Criteria:**
- ✅ Regex detection >80% accuracy on simple cases
- ✅ AI detection >90% accuracy on complex cases
- ✅ Pipeline completes in <30s per job
- ✅ No API errors or timeouts
- ✅ Database correctly updated

**Files Created:**
- `modules/ai_job_description_analysis/field_detector.py` (regex)
- `modules/ai_job_description_analysis/ai_field_extractor.py` (AI)
- `modules/ai_job_description_analysis/hybrid_detector.py` (pipeline)
- `tests/test_hybrid_detection.py` (tests)

**Files Modified:**
- `modules/dashboard_api_v2.py` (new endpoint)
- Job ingestion pipeline (integrate detection)

---

### Phase 7: Testing & Quality Assurance 🧪

**Complexity:** Medium-High
**Estimated Time:** 10-12 hours
**Priority:** HIGH
**Dependencies:** All feature phases (1-6)
**Can Parallel With:** Start unit tests during implementation

#### Current State
- Coverage: 23% (2,587/11,230 lines)
- Tests passing: 239/298 (80.2%)
- Integration tests: 9/30 (30%)
- Deferred comprehensive testing plan exists

#### Subtask 7.1: Dashboard-Specific Unit Tests (3 hours)

**File:** `tests/test_dashboard_api_v2.py` (new)

**Implementation:**
1. **API Endpoint Tests** (90 min)
   - Test `/api/v2/dashboard/overview`
   - Test `/api/v2/dashboard/metrics/timeseries`
   - Test `/api/v2/dashboard/pipeline/status`
   - Test `/api/v2/dashboard/applications`
   - Test `/api/v2/dashboard/jobs/filter`
   - Test `/api/v2/dashboard/search`
   - Test `/api/v2/dashboard/export`
   - Mock database queries
   - Test error handling (DB down, invalid params)
   - Test authentication required

2. **Caching Tests** (45 min)
   - Test cache hit/miss
   - Test TTL expiration
   - Test cache invalidation
   - Test concurrent access

3. **Real-time SSE Tests** (45 min)
   - Test SSE connection establishment
   - Test event broadcasting
   - Test heartbeat
   - Test auto-reconnect

#### Subtask 7.2: Frontend Integration Tests (3 hours)

**File:** `tests/integration/test_dashboard_frontend.py` (new)

**Implementation:**
1. **Playwright E2E Tests** (120 min)
   - Install Playwright: `pip install playwright`
   - Test dashboard login
   - Test main dashboard loads
   - Test jobs view loads and filters
   - Test applications view loads
   - Test analytics charts render
   - Test search functionality
   - Test export downloads
   - Test PWA installation

2. **Visual Regression Tests** (60 min)
   - Capture screenshots of all views
   - Compare against baseline
   - Test responsive breakpoints
   - Test dark theme consistency

#### Subtask 7.3: Database Migration Tests (90 min)

**File:** `tests/test_dashboard_migrations.py` (new)

**Implementation:**
1. **Migration Execution Tests** (45 min)
   - Test migrations run without errors
   - Test rollback works
   - Test idempotency (can run multiple times)
   - Test on empty database
   - Test on database with data

2. **Performance Tests** (45 min)
   - Benchmark queries before/after migrations
   - Verify <50ms response time for overview endpoint
   - Test materialized view refresh time
   - Test under load (100+ concurrent requests)

#### Subtask 7.4: Hybrid Detection Tests (2 hours)

**File:** `tests/test_hybrid_detection.py`

**Implementation:**
1. **Regex Detection Tests** (60 min)
   - 20 test cases for salary extraction
   - 15 test cases for location extraction
   - 10 test cases for job type/seniority
   - Edge cases and false positives

2. **AI Detection Tests** (60 min)
   - Mock Gemini API responses
   - Test JSON parsing
   - Test error handling
   - Test rate limiting
   - Test cost tracking

#### Subtask 7.5: Code Quality & Security (3-4 hours)

**Implementation:**
1. **Run Quality Tools** (60 min)
   - Black formatting: `black modules/ tests/`
   - Flake8 linting: `flake8 modules/ tests/`
   - Vulture dead code: `vulture modules/`
   - Fix all issues

2. **Security Audit** (90 min)
   - SQL injection review (parameterized queries)
   - XSS review (template escaping)
   - CSRF review (session tokens)
   - Authentication review (session management)
   - API key exposure review
   - Dependency vulnerabilities: `pip-audit`

3. **Accessibility Audit** (60 min)
   - Run Lighthouse accessibility scan
   - Fix contrast issues
   - Add ARIA labels
   - Test keyboard navigation
   - Test screen reader compatibility

4. **Browser Compatibility** (30 min)
   - Test on Chrome, Firefox, Safari, Edge
   - Test on iOS Safari, Chrome Mobile
   - Fix polyfills if needed

**Success Criteria:**
- ✅ Test coverage >80% for new dashboard code
- ✅ All tests passing
- ✅ No security vulnerabilities
- ✅ Accessibility score >90
- ✅ Works on all major browsers

**Files Created:**
- `tests/test_dashboard_api_v2.py`
- `tests/integration/test_dashboard_frontend.py`
- `tests/test_dashboard_migrations.py`
- `tests/test_hybrid_detection.py`

---

### Phase 8: Production Deployment 🚀

**Complexity:** Medium
**Estimated Time:** 6-8 hours
**Priority:** HIGHEST (after all features)
**Dependencies:** All phases complete, tests passing

#### Subtask 8.1: Pre-Deployment Checklist (90 min)

**Implementation:**
1. **Environment Configuration** (30 min)
   - Generate strong secrets: `python utils/security_key_generator.py`
   - Update `.env` with production values
   - Set `FLASK_ENV=production`
   - Set `FLASK_DEBUG=False`
   - Configure `DATABASE_URL` for production
   - Configure logging level to INFO

2. **Database Preparation** (30 min)
   - Create production database backup
   - Run migrations on production DB (test first on staging)
   - Verify indexes created
   - Verify materialized views populated
   - Set up automated materialized view refresh (cron job every 5 min)

3. **Static Asset Optimization** (30 min)
   - Minify CSS: `cssnano static/css/dashboard_v2.css`
   - Minify JavaScript (if any custom JS)
   - Optimize images (compress icons)
   - Enable gzip compression in nginx/Apache
   - Set cache headers for static assets (1 year)

#### Subtask 8.2: Server Configuration (2-3 hours)

**Implementation:**
1. **WSGI Server Setup** (60 min)
   - Install gunicorn: `pip install gunicorn`
   - Create `gunicorn_config.py`:
     ```python
     bind = "0.0.0.0:5000"
     workers = 4  # 2 * CPU cores
     worker_class = "gevent"  # For SSE support
     timeout = 120
     keepalive = 5
     accesslog = "logs/access.log"
     errorlog = "logs/error.log"
     ```
   - Test: `gunicorn -c gunicorn_config.py app_modular:app`

2. **Reverse Proxy Setup** (60 min)
   - nginx configuration:
     ```nginx
     server {
         listen 80;
         server_name yourdomain.com;

         location / {
             proxy_pass http://localhost:5000;
             proxy_set_header Host $host;
             proxy_set_header X-Real-IP $remote_addr;
             proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
             proxy_set_header X-Forwarded-Proto $scheme;
         }

         location /api/stream/ {
             proxy_pass http://localhost:5000;
             proxy_buffering off;  # SSE requires no buffering
             proxy_cache off;
             proxy_read_timeout 86400;
         }

         location /static/ {
             alias /path/to/static/;
             expires 1y;
             add_header Cache-Control "public, immutable";
         }
     }
     ```
   - Enable gzip compression
   - Set up SSL/TLS certificate (Let's Encrypt)

3. **Process Manager** (30 min)
   - systemd service file: `/etc/systemd/system/dashboard.service`
     ```ini
     [Unit]
     Description=Job Application Dashboard
     After=network.target postgresql.service

     [Service]
     User=www-data
     Group=www-data
     WorkingDirectory=/path/to/app
     Environment="PATH=/path/to/venv/bin"
     ExecStart=/path/to/venv/bin/gunicorn -c gunicorn_config.py app_modular:app
     Restart=always

     [Install]
     WantedBy=multi-user.target
     ```
   - Enable: `systemctl enable dashboard.service`
   - Start: `systemctl start dashboard.service`

#### Subtask 8.3: Monitoring & Logging (2 hours)

**Implementation:**
1. **Application Monitoring** (60 min)
   - Set up error tracking (Sentry or similar)
   - Set up performance monitoring (New Relic or DataDog)
   - Configure health check endpoint: `/health`
   - Set up uptime monitoring (UptimeRobot or Pingdom)

2. **Log Aggregation** (30 min)
   - Centralize logs (ELK stack or CloudWatch)
   - Rotate logs (logrotate configuration)
   - Set up log alerts for errors

3. **Database Monitoring** (30 min)
   - Monitor query performance (pg_stat_statements)
   - Set up slow query logging
   - Monitor materialized view refresh times
   - Set up disk space alerts

#### Subtask 8.4: Deployment Automation (90 min)

**Implementation:**
1. **Deployment Script** (60 min)
   - Create `deploy.sh`:
     ```bash
     #!/bin/bash
     # Pull latest code
     git pull origin main

     # Activate virtualenv
     source venv/bin/activate

     # Install dependencies
     pip install -r requirements.txt

     # Run migrations
     python database_migrations/run_migrations.py

     # Collect static files (if using Flask-Assets)
     # python manage.py collectstatic

     # Restart service
     sudo systemctl restart dashboard.service

     # Health check
     sleep 5
     curl -f http://localhost:5000/health || exit 1

     echo "Deployment successful!"
     ```
   - Make executable: `chmod +x deploy.sh`

2. **Rollback Plan** (30 min)
   - Document rollback procedure
   - Create `rollback.sh` script
   - Test rollback on staging

#### Subtask 8.5: Post-Deployment Validation (60 min)

**Checklist:**
- [ ] All pages load without errors
- [ ] Dashboard metrics show correct data
- [ ] Real-time updates work (SSE connected)
- [ ] Search and filters work
- [ ] Export downloads work
- [ ] PWA installable
- [ ] SSL certificate valid
- [ ] Performance <50ms for overview endpoint
- [ ] No console errors
- [ ] Mobile responsive
- [ ] Monitoring alerts configured
- [ ] Backup script running

**Success Criteria:**
- ✅ Application deployed and accessible
- ✅ All features working in production
- ✅ SSL/HTTPS enabled
- ✅ Monitoring and logging active
- ✅ Performance targets met
- ✅ No errors in logs

**Files Created:**
- `gunicorn_config.py`
- `deploy.sh`
- `rollback.sh`
- `/etc/systemd/system/dashboard.service`
- nginx configuration

---

## Recommended Implementation Order

### Week 1: Foundation (10-12 hours)

**Priority: Get core functionality working**

1. **Phase 1: Fix Migrations** (3-4h)
   - Day 1: Audit schema, fix migration files
   - Day 1: Test migrations, verify performance

2. **Phase 2.1: Applications View** (2-3h)
   - Day 2: Create API endpoint, update frontend

3. **Phase 2.2: Analytics View** (3-4h)
   - Day 2-3: Chart.js integration, API integration

**Deliverable:** Core dashboard views working with real data

### Week 2: Enhancement (12-15 hours)

**Priority: Add search, export, and hybrid detection**

4. **Phase 3: Search & Filters** (4-5h)
   - Day 4: Backend search API
   - Day 4-5: Frontend search UI

5. **Phase 4: Export Functionality** (2-3h)
   - Day 5: Backend export API, frontend UI

6. **Phase 6.1-6.3: Hybrid Detection** (5-7h)
   - Day 5-6: Regex detection, AI detection

**Deliverable:** Enhanced functionality (search, export, AI detection)

### Week 3: Polish & Deploy (13-16 hours)

**Priority: Quality, PWA, and production**

7. **Phase 2.3: Schema Visualization** (2h)
   - Day 7: Build interactive schema viewer

8. **Phase 5: PWA Features** (3-4h)
   - Day 7-8: Manifest, service worker, offline support

9. **Phase 6.4-6.5: Hybrid Detection Integration** (3-4h)
   - Day 8: Pipeline orchestrator, testing

10. **Phase 7: Testing & Quality** (4-6h)
    - Day 9: Unit tests, integration tests, security audit

11. **Phase 8: Production Deployment** (4-6h)
    - Day 9-10: Server setup, deployment, monitoring

**Deliverable:** Production-ready dashboard

---

## Parallel Work Opportunities

### Scenario 1: Solo Developer

**Sequential Order (minimize context switching):**
1. Phase 1 (migrations) → Phase 2 (views) → Phase 3 (search) → Phase 4 (export)
2. Phase 6 (hybrid detection) → Phase 5 (PWA)
3. Phase 7 (testing) → Phase 8 (deployment)

**Estimated Time:** 35-40 hours (4-5 weeks at 8h/week)

### Scenario 2: Parallel Tracks (if multiple developers)

**Track A (Backend Engineer):**
- Phase 1: Fix migrations (3-4h)
- Phase 6: Hybrid detection (8-10h)
- Phase 7.1, 7.3, 7.4: Backend tests (5-6h)
- Phase 8.1-8.2: Deployment prep (5-6h)
**Total: 21-26 hours**

**Track B (Frontend Engineer):**
- Phase 2: Complete views (7-9h)
- Phase 3.2: Search UI (2-3h)
- Phase 4.2: Export UI (1-2h)
- Phase 5: PWA features (3-4h)
- Phase 7.2, 7.5: Frontend tests, quality (5-6h)
**Total: 18-24 hours**

**Overlap/Integration:**
- Phase 3.1: Search API (backend) must complete before 3.2 (frontend)
- Phase 4.1: Export API (backend) must complete before 4.2 (frontend)
- Phase 8.3-8.5: Deployment execution (shared, 3-4h)

**Total Parallel Time:** ~24-30 hours (instead of 40h sequential)

### Scenario 3: Incremental Deployment

**Can deploy after each phase:**
1. After Phase 1+2: Deploy improved dashboard with views
2. After Phase 3+4: Deploy with search and export
3. After Phase 5+6: Deploy with PWA and AI detection
4. After Phase 7: Final production deployment

**Benefit:** Users get value sooner, risks spread out

---

## Risk Factors

### Technical Risks

#### Risk 1: Migration Failures (HIGH)
**Impact:** Dashboard won't achieve 80% performance improvement
**Probability:** Medium
**Mitigation:**
- Create database backup before migrations
- Test migrations on staging environment first
- Use generated SQLAlchemy models to verify schema
- Have rollback script ready
- Plan for manual schema fixes if automation fails

**Contingency:**
- Dashboard works without migrations (current state)
- Can manually create indexes one by one
- Can skip materialized views and use direct queries

#### Risk 2: AI Detection Costs (MEDIUM)
**Impact:** High Gemini API costs if used on all jobs
**Probability:** Medium
**Mitigation:**
- Use regex detection first (free)
- Only call AI for missing/complex fields
- Batch process with rate limiting
- Set budget alerts on Gemini API
- Cache results aggressively

**Contingency:**
- Disable AI detection if costs too high
- Use only regex detection
- Manual field entry for important jobs

#### Risk 3: PWA Browser Compatibility (LOW)
**Impact:** PWA features don't work on some browsers
**Probability:** Low
**Mitigation:**
- Progressive enhancement (works without PWA)
- Test on all major browsers early
- Use feature detection
- Provide graceful fallbacks

**Contingency:**
- PWA is optional enhancement
- Core dashboard works without it
- Can skip PWA features if problematic

#### Risk 4: SSE Connection Issues (MEDIUM)
**Impact:** Real-time updates don't work reliably
**Probability:** Medium
**Mitigation:**
- Implement auto-reconnect (already done)
- Test with different network conditions
- Add heartbeat mechanism (already done)
- Use long polling as fallback

**Contingency:**
- Disable SSE if unreliable
- Use periodic polling instead (every 30s)
- Manual refresh button

### Project Risks

#### Risk 5: Scope Creep (MEDIUM)
**Impact:** Project takes >40 hours
**Probability:** Medium
**Mitigation:**
- Strict adherence to this plan
- Time-box each phase
- Mark nice-to-haves as optional
- Get user approval before adding features

**Contingency:**
- Phase 5 (PWA) is optional
- Phase 6 (Hybrid Detection) can be deferred
- Phase 2.3 (Schema viz) can be deferred

#### Risk 6: Testing Time Underestimated (HIGH)
**Impact:** Phase 7 takes >12 hours
**Probability:** High
**Mitigation:**
- Write tests during implementation (not after)
- Use existing test fixtures
- Focus on critical paths first
- Automate where possible

**Contingency:**
- Minimum viable testing (80% coverage)
- Defer comprehensive testing (already deferred)
- Focus on integration tests over unit tests

#### Risk 7: Production Deployment Issues (MEDIUM)
**Impact:** Deployment delayed or failed
**Probability:** Medium
**Mitigation:**
- Test deployment on staging first
- Use deployment checklist
- Have rollback plan ready
- Schedule deployment during low-usage time

**Contingency:**
- Rollback to previous version
- Deploy only frontend first (no migrations)
- Gradual rollout (feature flags)

---

## Success Criteria

### Phase-Specific Criteria

**Phase 1: Migrations**
- [ ] All 3 migration files run without errors
- [ ] 8 indexes created successfully
- [ ] 1 materialized view created and populated
- [ ] Dashboard API response time <50ms (down from 250ms)
- [ ] No impact on existing functionality

**Phase 2: Views**
- [ ] Applications view shows real data with filters
- [ ] Analytics view renders 4 charts correctly
- [ ] Schema visualization interactive and accurate
- [ ] All views responsive on mobile
- [ ] No console errors

**Phase 3: Search & Filters**
- [ ] Global search returns relevant results in <500ms
- [ ] Advanced filters combine correctly (AND logic)
- [ ] Filter presets save and load
- [ ] Pagination works correctly
- [ ] No performance degradation

**Phase 4: Export**
- [ ] CSV export downloads correctly
- [ ] JSON export valid and complete
- [ ] Large exports (>1000 rows) don't timeout
- [ ] Exported data matches visible filters
- [ ] Files named descriptively

**Phase 5: PWA**
- [ ] PWA installable on Chrome, Safari, Firefox
- [ ] Works offline with cached data
- [ ] Service worker caches properly
- [ ] Install prompt appears correctly
- [ ] App behaves like native app

**Phase 6: Hybrid Detection**
- [ ] Regex detection >80% accuracy
- [ ] AI detection >90% accuracy
- [ ] Pipeline completes in <30s per job
- [ ] API costs <$0.01 per job
- [ ] Database fields updated correctly

**Phase 7: Testing**
- [ ] Test coverage >80% for dashboard code
- [ ] All tests passing (100%)
- [ ] No security vulnerabilities
- [ ] Accessibility score >90
- [ ] Browser compatibility verified

**Phase 8: Deployment**
- [ ] Application accessible at production URL
- [ ] SSL certificate valid
- [ ] All features working
- [ ] Monitoring active and alerting
- [ ] Performance targets met in production

### Overall Success Criteria

**Functionality:**
- ✅ All 8 task requirements implemented
- ✅ Dashboard loads in <2 seconds
- ✅ Real-time updates working
- ✅ Mobile-responsive
- ✅ Data accurate and complete

**Performance:**
- ✅ API response <50ms (dashboard overview)
- ✅ Page load <2s on 3G network
- ✅ No memory leaks
- ✅ Handles 100+ concurrent users

**Quality:**
- ✅ No critical bugs
- ✅ Test coverage >80%
- ✅ Code follows project standards
- ✅ Documentation complete
- ✅ Accessibility compliant

**User Experience:**
- ✅ Intuitive navigation
- ✅ Clear error messages
- ✅ Helpful loading states
- ✅ Consistent design
- ✅ Works offline (PWA)

---

## Appendix

### A. Technology Stack Summary

**Frontend:**
- Alpine.js 3.x (reactive data binding)
- Chart.js 4.4 (analytics visualizations)
- Custom CSS (glass morphism, cyberpunk theme)
- D3.js or vis.js (schema visualization)

**Backend:**
- Flask (web framework)
- PostgreSQL (database)
- SQLAlchemy (ORM)
- Gunicorn (WSGI server)
- nginx (reverse proxy)

**Real-time:**
- Server-Sent Events (SSE)
- In-memory event queue (upgradeable to Redis)

**AI/ML:**
- Google Gemini AI (field extraction)
- Python regex + NLP (pattern matching)

**DevOps:**
- systemd (process management)
- Let's Encrypt (SSL certificates)
- Sentry/DataDog (monitoring)

### B. File Structure Reference

```
workspace/
├── database_migrations/
│   ├── 001_dashboard_optimization_indexes.sql
│   ├── 002_dashboard_materialized_views.sql
│   ├── 003_dashboard_aggregation_tables.sql
│   └── run_migrations.py
├── frontend_templates/
│   ├── dashboard_v2.html (✅ complete)
│   ├── dashboard_jobs.html (✅ complete)
│   ├── dashboard_applications.html (🔨 needs API integration)
│   ├── dashboard_analytics.html (🔨 needs Chart.js integration)
│   └── dashboard_schema.html (❌ new)
├── modules/
│   ├── dashboard_api_v2.py (🔨 needs new endpoints)
│   ├── realtime/
│   │   └── sse_dashboard.py (✅ complete)
│   ├── cache/
│   │   └── simple_cache.py (✅ complete)
│   └── ai_job_description_analysis/
│       ├── field_detector.py (❌ new - regex)
│       ├── ai_field_extractor.py (❌ new - AI)
│       └── hybrid_detector.py (❌ new - pipeline)
├── static/
│   ├── css/
│   │   └── dashboard_v2.css (✅ complete)
│   ├── manifest.json (❌ new)
│   ├── sw.js (❌ new)
│   └── icons/ (❌ new)
├── tests/
│   ├── test_dashboard_api_v2.py (❌ new)
│   ├── test_dashboard_migrations.py (❌ new)
│   ├── test_hybrid_detection.py (❌ new)
│   └── integration/
│       └── test_dashboard_frontend.py (❌ new)
└── app_modular.py (✅ blueprints registered)
```

### C. Database Schema Quick Reference

**Key Tables:**
- `jobs` - Main jobs table (id, job_title, company_id, salary_low/high, seniority_level, etc.)
- `job_applications` - Application tracking (id, job_id, application_status, created_at, etc.)
- `companies` - Company information (id, name, domain, industry, size_range, etc.)
- `analyzed_jobs` - AI-analyzed job details (extends jobs with AI insights)

**Critical Fields for Migrations:**
- ✅ EXISTS: `seniority_level` (NOT experience_level)
- ✅ EXISTS: `compensation_currency` (NOT salary_currency)
- ❌ MISSING: `priority_score` (need NULL placeholder)
- ❌ MISSING: `location` (synthesize from office_city, office_province, office_country)

### D. API Endpoints Summary

**Existing (✅ Complete):**
- `GET /api/v2/dashboard/overview` - Main dashboard data
- `GET /api/v2/dashboard/metrics/timeseries` - Time-series metrics
- `GET /api/v2/dashboard/pipeline/status` - Pipeline status
- `GET /api/stream/dashboard` - SSE real-time updates

**To Create (❌ New):**
- `GET /api/v2/dashboard/applications` - Applications list
- `GET /api/v2/dashboard/jobs/filter` - Advanced job filtering
- `POST /api/v2/dashboard/search` - Global search
- `GET /api/v2/dashboard/export/{type}?format={csv|json}` - Export data
- `GET /api/v2/dashboard/schema` - Database schema metadata
- `POST /api/v2/jobs/{job_id}/detect-fields` - Trigger hybrid detection

### E. Time Tracking Template

Use this to track actual time vs. estimates:

| Phase | Task | Estimated | Actual | Variance | Notes |
|-------|------|-----------|--------|----------|-------|
| 1 | Schema Audit | 30m | | | |
| 1 | Fix Migrations | 90m | | | |
| 1 | Test Migrations | 45m | | | |
| 1 | Backfill Data | 30m | | | |
| 2.1 | Applications API | 45m | | | |
| 2.1 | Applications Frontend | 60m | | | |
| 2.1 | Applications UI Enhancement | 30m | | | |
| ... | ... | ... | ... | ... | ... |

**Total Estimated:** 35-40 hours
**Total Actual:** ___ hours
**Variance:** ___ hours

### F. Deployment Checklist

```
Pre-Deployment:
[ ] All tests passing
[ ] Code reviewed
[ ] Documentation updated
[ ] Secrets generated
[ ] Database backup created
[ ] Staging deployment successful

Deployment:
[ ] Migrations run successfully
[ ] Static assets optimized
[ ] WSGI server configured
[ ] Reverse proxy configured
[ ] SSL certificate installed
[ ] Process manager configured
[ ] Monitoring configured
[ ] Logs configured

Post-Deployment:
[ ] Health check passing
[ ] All pages load
[ ] Real-time updates working
[ ] Search working
[ ] Export working
[ ] PWA installable
[ ] Performance targets met
[ ] No errors in logs
[ ] Monitoring alerts triggered correctly
[ ] Rollback plan tested
```

---

## Implementation Notes

### Best Practices

1. **Commit frequently** - After each subtask completion
2. **Test as you go** - Don't wait until Phase 7
3. **Document decisions** - Update CLAUDE.md with new patterns
4. **Monitor performance** - Benchmark before/after each optimization
5. **User feedback** - Get user validation after each phase

### When to Ask for Help

- If database schema differs significantly from assumptions
- If Gemini API costs exceed $50
- If performance targets not met after migrations
- If critical tests failing consistently
- If deployment blocked by infrastructure issues

### When to Defer

- Phase 5 (PWA) if time constrained (low priority)
- Phase 6 (Hybrid Detection) if AI costs too high
- Phase 2.3 (Schema viz) if other views more critical
- Comprehensive testing (already deferred)

---

**END OF IMPLEMENTATION PLAN**

**Next Step:** Begin Phase 1 - Fix Blocked Migrations

