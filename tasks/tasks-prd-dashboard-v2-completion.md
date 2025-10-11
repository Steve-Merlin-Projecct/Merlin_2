# Task List: Dashboard V2 Completion - Database Integration & Jobs View
**PRD Reference:** `tasks/prd-dashboard-v2-completion.md`
**Version:** 1.0
**Date:** October 11, 2025
**Status:** In Progress

---

## Parent Tasks Overview

| ID | Parent Task | Estimated Time | Status | Dependencies |
|----|-------------|----------------|--------|--------------|
| 1.0 | Database Schema Audit & Documentation | 1 hour | 🔄 Not Started | None |
| 2.0 | Fix Database Migration Files | 2 hours | ⏳ Pending | 1.0 |
| 3.0 | Execute Database Migrations | 1 hour | ⏳ Pending | 2.0 |
| 4.0 | Implement Jobs API Endpoint | 2 hours | ⏳ Pending | 1.0 |
| 5.0 | Connect Jobs View to Real API | 1 hour | ⏳ Pending | 4.0 |
| 6.0 | Testing & Validation | 1 hour | ⏳ Pending | 3.0, 4.0, 5.0 |

**Total Estimated Time:** 8 hours

---

## Task 1.0: Database Schema Audit & Documentation
**Status:** 🔄 Not Started
**Priority:** High (Blocking)
**Estimated Time:** 1 hour
**Dependencies:** None

### Objective
Audit the actual PostgreSQL database schema to identify all existing columns and data types in the `jobs`, `job_applications`, and `companies` tables. Document discrepancies with migration file assumptions.

### Deliverables
- `docs/database-schema-actual.md` - Complete schema documentation
- Column mapping between assumed vs actual schema
- List of non-existent columns to remove from migrations

### Subtasks

#### 1.1: Connect to PostgreSQL Database
- **Description:** Establish connection to PostgreSQL database
- **Command:** `psql -h localhost -U <user> -d local_Merlin_3`
- **Validation:** Successfully connected to database
- **Status:** ⏳ Pending

#### 1.2: Audit Jobs Table Schema
- **Description:** Extract complete schema for `jobs` table
- **Command:** `\d+ jobs`
- **Output:** Document all columns, types, constraints, indexes
- **Validation:** All columns documented
- **Status:** ⏳ Pending

#### 1.3: Audit Job Applications Table Schema
- **Description:** Extract complete schema for `job_applications` table
- **Command:** `\d+ job_applications`
- **Output:** Document all columns, types, constraints, indexes
- **Validation:** All columns documented
- **Status:** ⏳ Pending

#### 1.4: Audit Companies Table Schema
- **Description:** Extract complete schema for `companies` table
- **Command:** `\d+ companies`
- **Output:** Document all columns, types, constraints, indexes
- **Validation:** All columns documented
- **Status:** ⏳ Pending

#### 1.5: Identify Schema Discrepancies
- **Description:** Compare migration file assumptions with actual schema
- **Check For:**
  - `jobs.priority_score` (assumed to exist, likely doesn't)
  - `jobs.salary_currency` (assumed to exist, likely doesn't)
  - `jobs.location` (assumed to exist, likely doesn't)
  - `jobs.experience_level` (assumed to exist, likely doesn't)
- **Output:** List of missing columns and available alternatives
- **Status:** ⏳ Pending

#### 1.6: Create Schema Documentation File
- **Description:** Write comprehensive schema documentation
- **File:** `docs/database-schema-actual.md`
- **Contents:**
  - Full table schemas with column names, types, constraints
  - Existing indexes
  - Foreign key relationships
  - Column mapping (assumed → actual)
  - Recommendations for migration updates
- **Status:** ⏳ Pending

#### 1.7: Identify Alternative Columns
- **Description:** Find actual columns to use instead of non-existent ones
- **Examples:**
  - If no `location`, check for `city`, `state`, `country`, `remote_type`
  - If no `salary_currency`, check salary fields structure
  - If no `priority_score`, check for `match_score`, `ranking`, etc.
- **Output:** Column substitution mapping
- **Status:** ⏳ Pending

---

## Task 2.0: Fix Database Migration Files
**Status:** ⏳ Pending
**Priority:** High (Blocking)
**Estimated Time:** 2 hours
**Dependencies:** Task 1.0

### Objective
Update all three database migration SQL files to reference only existing columns from the actual schema. Remove references to non-existent columns and adjust queries accordingly.

### Deliverables
- Corrected `database_migrations/001_dashboard_optimization_indexes.sql`
- Corrected `database_migrations/002_dashboard_materialized_views.sql`
- Corrected `database_migrations/003_dashboard_aggregation_tables.sql`
- SQL syntax validated in PostgreSQL console

### Subtasks

#### 2.1: Backup Original Migration Files
- **Description:** Create backups before making changes
- **Commands:**
  ```bash
  cp database_migrations/001_dashboard_optimization_indexes.sql database_migrations/001_dashboard_optimization_indexes.sql.backup
  cp database_migrations/002_dashboard_materialized_views.sql database_migrations/002_dashboard_materialized_views.sql.backup
  cp database_migrations/003_dashboard_aggregation_tables.sql database_migrations/003_dashboard_aggregation_tables.sql.backup
  ```
- **Validation:** Backup files exist
- **Status:** ⏳ Pending

#### 2.2: Review Migration 001 (Indexes)
- **Description:** Identify all column references in index definitions
- **File:** `database_migrations/001_dashboard_optimization_indexes.sql`
- **Check:** Indexes on non-existent columns
- **Status:** ⏳ Pending

#### 2.3: Fix Migration 001 (Indexes)
- **Description:** Update index definitions to use actual columns
- **Actions:**
  - Remove indexes on non-existent columns
  - Add indexes on commonly queried actual columns
  - Update comments to reflect changes
- **Validation:** SQL syntax check in psql
- **Status:** ⏳ Pending

#### 2.4: Review Migration 002 (Materialized Views)
- **Description:** Identify all column references in materialized view queries
- **File:** `database_migrations/002_dashboard_materialized_views.sql`
- **Check:** SELECT clauses with non-existent columns
- **Status:** ⏳ Pending

#### 2.5: Fix Migration 002 (Materialized Views)
- **Description:** Update materialized view definitions
- **Actions:**
  - Replace non-existent columns with actual columns
  - Adjust JOIN conditions if needed
  - Update aggregation logic
  - Add comments documenting changes
- **Validation:** SQL syntax check in psql
- **Status:** ⏳ Pending

#### 2.6: Review Migration 003 (Aggregation Tables)
- **Description:** Identify all column references in aggregation queries
- **File:** `database_migrations/003_dashboard_aggregation_tables.sql`
- **Check:** INSERT statements with non-existent columns
- **Status:** ⏳ Pending

#### 2.7: Fix Migration 003 (Aggregation Tables)
- **Description:** Update aggregation table creation and population
- **Actions:**
  - Replace non-existent columns with actual columns
  - Adjust GROUP BY clauses
  - Update aggregation functions
  - Add comments documenting changes
- **Validation:** SQL syntax check in psql
- **Status:** ⏳ Pending

#### 2.8: Validate All SQL Syntax
- **Description:** Test each migration SQL in PostgreSQL console
- **Commands:**
  ```bash
  psql -h localhost -U <user> -d local_Merlin_3 < database_migrations/001_dashboard_optimization_indexes.sql
  # (in test/staging environment, not production)
  ```
- **Validation:** No syntax errors
- **Status:** ⏳ Pending

#### 2.9: Document Migration Changes
- **Description:** Update migration file headers with change log
- **Add to each file:**
  - Date of correction
  - List of columns removed/replaced
  - Rationale for changes
- **Status:** ⏳ Pending

---

## Task 3.0: Execute Database Migrations
**Status:** ⏳ Pending
**Priority:** High
**Estimated Time:** 1 hour
**Dependencies:** Task 2.0

### Objective
Run the corrected database migrations to create indexes, materialized views, and aggregation tables. Verify successful execution and validate created database objects.

### Deliverables
- Successfully executed migrations (all 3)
- Verified indexes created
- Verified materialized views created
- Verified aggregation tables populated
- Migration execution log

### Subtasks

#### 3.1: Backup Database
- **Description:** Create database backup before running migrations
- **Command:** `pg_dump -h localhost -U <user> local_Merlin_3 > backup_pre_migration_$(date +%Y%m%d_%H%M%S).sql`
- **Validation:** Backup file created and non-empty
- **Status:** ⏳ Pending

#### 3.2: Review Migration Runner Script
- **Description:** Verify migration runner is configured correctly
- **File:** `run_dashboard_migrations.py`
- **Check:**
  - Database connection settings
  - Migration file paths
  - Error handling logic
- **Status:** ⏳ Pending

#### 3.3: Run Migration 001 (Indexes)
- **Description:** Execute index creation migration
- **Command:** `python run_dashboard_migrations.py` (or execute migration 001)
- **Expected:** Indexes created successfully
- **Validation:** Check for errors in output
- **Status:** ⏳ Pending

#### 3.4: Verify Indexes Created
- **Description:** Confirm indexes exist in database
- **Command:** `\di` in psql (list indexes)
- **Expected:** New dashboard optimization indexes visible
- **Validation:** Index names match migration file
- **Status:** ⏳ Pending

#### 3.5: Run Migration 002 (Materialized Views)
- **Description:** Execute materialized view creation migration
- **Command:** Continue with migration 002
- **Expected:** Materialized views created successfully
- **Validation:** Check for errors in output
- **Status:** ⏳ Pending

#### 3.6: Verify Materialized Views Created
- **Description:** Confirm materialized views exist
- **Command:** `\dm` in psql (list materialized views)
- **Expected:** Dashboard materialized views visible
- **Validation:** View names match migration file
- **Status:** ⏳ Pending

#### 3.7: Refresh Materialized Views
- **Description:** Populate materialized views with data
- **Command:** `REFRESH MATERIALIZED VIEW <view_name>;` for each view
- **Expected:** Views contain data
- **Validation:** `SELECT COUNT(*) FROM <view_name>;` returns > 0
- **Status:** ⏳ Pending

#### 3.8: Run Migration 003 (Aggregation Tables)
- **Description:** Execute aggregation table creation and population
- **Command:** Continue with migration 003
- **Expected:** Aggregation tables created and populated
- **Validation:** Check for errors in output
- **Status:** ⏳ Pending

#### 3.9: Verify Aggregation Tables Populated
- **Description:** Confirm aggregation tables contain data
- **Command:** `\dt` in psql (list tables), then query tables
- **Expected:** Dashboard aggregation tables visible with data
- **Validation:** `SELECT COUNT(*) FROM <table_name>;` returns > 0
- **Status:** ⏳ Pending

#### 3.10: Test Dashboard Performance
- **Description:** Benchmark dashboard overview endpoint
- **Command:** `curl -w "@curl-format.txt" -o /dev/null -s http://localhost:5001/api/v2/dashboard/overview`
- **Expected:** Response time <50ms
- **Validation:** Performance improvement documented
- **Status:** ⏳ Pending

---

## Task 4.0: Implement Jobs API Endpoint
**Status:** ⏳ Pending
**Priority:** High
**Estimated Time:** 2 hours
**Dependencies:** Task 1.0 (schema knowledge)

### Objective
Create a new API endpoint `/api/v2/dashboard/jobs` that returns real job data from the database with filtering and pagination support.

### Deliverables
- Working `/api/v2/dashboard/jobs` endpoint
- Support for filters: all, eligible, not_eligible, applied
- Pagination support (page, per_page parameters)
- Authentication enforcement
- Caching implementation

### Subtasks

#### 4.1: Design API Response Schema
- **Description:** Define the exact JSON structure for Jobs API response
- **Schema:**
  ```json
  {
    "success": true,
    "jobs": [...],
    "pagination": {...},
    "filter": "all"
  }
  ```
- **Document:** Add to PRD appendix
- **Status:** ⏳ Pending

#### 4.2: Create Jobs API Route Handler
- **Description:** Add route to `modules/dashboard_api_v2.py`
- **Route:** `@dashboard_api_v2_bp.route('/jobs', methods=['GET'])`
- **Authentication:** Use existing decorator
- **Status:** ⏳ Pending

#### 4.3: Implement Request Parameter Parsing
- **Description:** Extract and validate query parameters
- **Parameters:**
  - `filter`: string, default 'all', allowed values: all, eligible, not_eligible, applied
  - `page`: integer, default 1, min 1
  - `per_page`: integer, default 20, min 1, max 100
- **Validation:** Return 400 for invalid parameters
- **Status:** ⏳ Pending

#### 4.4: Build Base SQLAlchemy Query
- **Description:** Construct query to fetch jobs with related data
- **Tables:** `jobs`, `job_applications`, `companies`
- **Joins:** LEFT JOIN to companies, LEFT JOIN to job_applications
- **Select:** All necessary fields based on actual schema
- **Status:** ⏳ Pending

#### 4.5: Implement Filter Logic
- **Description:** Add WHERE clauses based on filter parameter
- **Filters:**
  - `all`: No additional filter
  - `eligible`: WHERE job_applications.id IS NULL AND jobs.is_eligible = TRUE
  - `not_eligible`: WHERE jobs.is_eligible = FALSE
  - `applied`: WHERE job_applications.id IS NOT NULL
- **Status:** ⏳ Pending

#### 4.6: Implement Pagination
- **Description:** Add LIMIT and OFFSET to query
- **Logic:**
  - Calculate offset: `(page - 1) * per_page`
  - Add LIMIT and OFFSET to query
  - Count total results for pagination metadata
- **Status:** ⏳ Pending

#### 4.7: Format Response Data
- **Description:** Transform SQLAlchemy results to JSON format
- **Formatting:**
  - Convert dates to ISO 8601 strings
  - Handle NULL values appropriately
  - Calculate match_score if available
  - Format salary information
- **Status:** ⏳ Pending

#### 4.8: Add Error Handling
- **Description:** Implement try-catch for database errors
- **Error Cases:**
  - Database connection failure
  - Invalid query syntax
  - Timeout errors
- **Response:** Return 500 with error message
- **Status:** ⏳ Pending

#### 4.9: Implement Caching
- **Description:** Add caching layer to Jobs API
- **Cache Key:** Include filter and page in key
- **TTL:** 60 seconds (configurable)
- **Use:** `@cached` decorator or manual cache check
- **Status:** ⏳ Pending

#### 4.10: Test Jobs API Endpoint
- **Description:** Manual testing of API with various parameters
- **Test Cases:**
  - GET /api/v2/dashboard/jobs (default parameters)
  - GET /api/v2/dashboard/jobs?filter=eligible
  - GET /api/v2/dashboard/jobs?page=2&per_page=10
  - GET /api/v2/dashboard/jobs?filter=applied
- **Validation:** Correct data returned, proper pagination
- **Status:** ⏳ Pending

#### 4.11: Update API Documentation
- **Description:** Document the Jobs API endpoint
- **File:** `docs/dashboard-v2-features.md`
- **Include:**
  - Endpoint URL and method
  - Request parameters
  - Response schema
  - Example requests and responses
  - Error codes
- **Status:** ⏳ Pending

---

## Task 5.0: Connect Jobs View to Real API
**Status:** ⏳ Pending
**Priority:** High
**Estimated Time:** 1 hour
**Dependencies:** Task 4.0

### Objective
Update the Jobs view HTML to fetch real data from the Jobs API endpoint, replacing mock data with live database information.

### Deliverables
- Updated `frontend_templates/dashboard_jobs.html`
- Mock data removed
- API integration working
- Loading states implemented
- Error handling implemented

### Subtasks

#### 5.1: Backup Original Jobs View
- **Description:** Create backup of current Jobs view file
- **Command:** `cp frontend_templates/dashboard_jobs.html frontend_templates/dashboard_jobs.html.backup`
- **Validation:** Backup file exists
- **Status:** ⏳ Pending

#### 5.2: Remove Mock Data
- **Description:** Delete the mock jobs array from Alpine.js data
- **File:** `frontend_templates/dashboard_jobs.html`
- **Find:** `jobs: [...]` array with 6 mock jobs
- **Replace:** `jobs: []`
- **Status:** ⏳ Pending

#### 5.3: Create fetchJobs Function
- **Description:** Add function to fetch jobs from API
- **Function:**
  ```javascript
  async fetchJobs(filter = 'all') {
    this.loading = true;
    this.error = null;
    try {
      const response = await fetch(`/api/v2/dashboard/jobs?filter=${filter}`);
      if (!response.ok) throw new Error('Failed to fetch jobs');
      const data = await response.json();
      this.jobs = data.jobs;
      this.pagination = data.pagination;
      this.currentFilter = filter;
    } catch (error) {
      this.error = error.message;
    } finally {
      this.loading = false;
    }
  }
  ```
- **Status:** ⏳ Pending

#### 5.4: Add Loading State Variables
- **Description:** Add loading and error state to Alpine.js data
- **Variables:**
  - `loading: false`
  - `error: null`
  - `pagination: {}`
  - `currentFilter: 'all'`
- **Status:** ⏳ Pending

#### 5.5: Update Filter Buttons
- **Description:** Connect filter buttons to fetchJobs function
- **Find:** Filter button click handlers
- **Update:** Call `fetchJobs('eligible')`, `fetchJobs('not_eligible')`, etc.
- **Status:** ⏳ Pending

#### 5.6: Add Loading Spinner
- **Description:** Display loading indicator during data fetch
- **HTML:**
  ```html
  <div x-show="loading" class="loading-spinner">
    Loading jobs...
  </div>
  ```
- **CSS:** Style loading spinner to match dashboard theme
- **Status:** ⏳ Pending

#### 5.7: Add Error Message Display
- **Description:** Show error message if API call fails
- **HTML:**
  ```html
  <div x-show="error" class="error-message">
    <p x-text="error"></p>
    <button @click="fetchJobs(currentFilter)">Retry</button>
  </div>
  ```
- **Status:** ⏳ Pending

#### 5.8: Add Empty State
- **Description:** Display message when no jobs match filter
- **HTML:**
  ```html
  <div x-show="!loading && jobs.length === 0" class="empty-state">
    No jobs found for this filter.
  </div>
  ```
- **Status:** ⏳ Pending

#### 5.9: Update Job Card Rendering
- **Description:** Ensure job cards use correct field names from API
- **Check:** Match field names with API response schema
- **Update:** Any mismatches (e.g., `job.match_score` vs `job.matchScore`)
- **Status:** ⏳ Pending

#### 5.10: Add Initial Data Load
- **Description:** Fetch jobs when page loads
- **Add:** `x-init="fetchJobs('all')"` to Alpine.js component
- **Validation:** Jobs load automatically on page load
- **Status:** ⏳ Pending

#### 5.11: Test Jobs View End-to-End
- **Description:** Manual testing of Jobs view in browser
- **Test Cases:**
  - Page loads and fetches jobs
  - Filter buttons work correctly
  - Loading spinner appears during fetch
  - Error handling works (test by stopping Flask)
  - Empty state displays when no results
- **Validation:** All interactions work smoothly
- **Status:** ⏳ Pending

---

## Task 6.0: Testing & Validation
**Status:** ⏳ Pending
**Priority:** High
**Estimated Time:** 1 hour
**Dependencies:** Tasks 3.0, 4.0, 5.0

### Objective
Comprehensive testing and validation of all implemented features. Verify performance improvements, data accuracy, and user experience.

### Deliverables
- Test execution results
- Performance benchmark results
- Validation report documenting success criteria
- Updated documentation with findings

### Subtasks

#### 6.1: Test Database Migration Success
- **Description:** Verify all database objects created correctly
- **Checks:**
  - Indexes exist: `\di` in psql
  - Materialized views exist: `\dm` in psql
  - Aggregation tables exist: `\dt` in psql
  - No migration errors in logs
- **Validation:** All objects present
- **Status:** ⏳ Pending

#### 6.2: Benchmark Dashboard Overview Performance
- **Description:** Measure dashboard overview API response time
- **Tool:** `curl` with timing, or browser DevTools
- **Command:** `curl -w "%{time_total}\n" -o /dev/null -s http://localhost:5001/api/v2/dashboard/overview`
- **Target:** <50ms response time
- **Validation:** Performance improvement documented
- **Status:** ⏳ Pending

#### 6.3: Test Jobs API with All Filters
- **Description:** Test Jobs API with each filter option
- **Test Cases:**
  - `GET /api/v2/dashboard/jobs?filter=all`
  - `GET /api/v2/dashboard/jobs?filter=eligible`
  - `GET /api/v2/dashboard/jobs?filter=not_eligible`
  - `GET /api/v2/dashboard/jobs?filter=applied`
- **Validation:** Correct results for each filter
- **Status:** ⏳ Pending

#### 6.4: Test Jobs API Pagination
- **Description:** Test pagination logic with various parameters
- **Test Cases:**
  - `GET /api/v2/dashboard/jobs?page=1&per_page=10`
  - `GET /api/v2/dashboard/jobs?page=2&per_page=10`
  - `GET /api/v2/dashboard/jobs?per_page=50`
- **Validation:** Correct page data returned, pagination metadata accurate
- **Status:** ⏳ Pending

#### 6.5: Test Jobs API Error Handling
- **Description:** Test API error responses
- **Test Cases:**
  - Invalid filter value
  - Invalid page number (negative, zero)
  - Invalid per_page (exceeds max)
  - Unauthenticated request
- **Validation:** Appropriate error codes and messages
- **Status:** ⏳ Pending

#### 6.6: Test Jobs View User Interactions
- **Description:** Test all user interactions in Jobs view
- **Test Cases:**
  - Page loads correctly
  - All filter buttons work
  - Job cards display correctly
  - Loading spinner appears during fetch
  - Error handling works (disconnect database)
  - Empty state shows when no results
- **Validation:** Smooth user experience, no console errors
- **Status:** ⏳ Pending

#### 6.7: Verify Data Accuracy
- **Description:** Verify Jobs API returns accurate data
- **Method:**
  - Query database directly for a specific job
  - Request same job via API
  - Compare field values
- **Validation:** API data matches database exactly
- **Status:** ⏳ Pending

#### 6.8: Test Caching Functionality
- **Description:** Verify caching is working for Jobs API
- **Method:**
  - Make first request, note response time
  - Make second identical request, note response time
  - Verify second request is faster (cache hit)
- **Validation:** Cache reduces response time
- **Status:** ⏳ Pending

#### 6.9: Cross-Browser Testing
- **Description:** Test Jobs view in multiple browsers
- **Browsers:** Chrome, Firefox, Safari (if available)
- **Validation:** Consistent behavior across browsers
- **Status:** ⏳ Pending

#### 6.10: Mobile Responsiveness Testing
- **Description:** Test Jobs view on mobile viewport
- **Tool:** Browser DevTools device emulation
- **Validation:** Layout adapts correctly, all features work on mobile
- **Status:** ⏳ Pending

#### 6.11: Create Validation Report
- **Description:** Document all test results
- **File:** `docs/dashboard-v2-completion-validation.md`
- **Include:**
  - Test results summary (pass/fail)
  - Performance benchmarks
  - Known issues (if any)
  - Success criteria verification
  - Screenshots/examples
- **Status:** ⏳ Pending

#### 6.12: Update DASHBOARD_V2_HANDOFF.md
- **Description:** Update handoff document with completion status
- **Updates:**
  - Mark Phase 4 (Database Optimization) as complete
  - Update "Jobs view connected to real API" as complete
  - Add performance benchmark results
  - Update known issues section
- **Status:** ⏳ Pending

---

## Progress Tracking

### Completion Status by Parent Task
- [ ] Task 1.0: Database Schema Audit & Documentation (0/7 subtasks)
- [ ] Task 2.0: Fix Database Migration Files (0/9 subtasks)
- [ ] Task 3.0: Execute Database Migrations (0/10 subtasks)
- [ ] Task 4.0: Implement Jobs API Endpoint (0/11 subtasks)
- [ ] Task 5.0: Connect Jobs View to Real API (0/11 subtasks)
- [ ] Task 6.0: Testing & Validation (0/12 subtasks)

### Overall Progress
**0/60 subtasks completed (0%)**

---

## Success Criteria Checklist

### Must Have
- [ ] All 3 database migrations execute successfully
- [ ] Dashboard overview loads in <50ms
- [ ] Jobs API returns real data with all filters working
- [ ] Jobs view displays live data from database
- [ ] No schema-related errors in logs

### Should Have
- [ ] Materialized views refresh automatically
- [ ] Jobs API supports pagination
- [ ] Performance benchmarks documented
- [ ] API documentation updated

### Nice to Have
- [ ] Migration rollback scripts created
- [ ] Performance monitoring dashboard
- [ ] Additional filters for jobs (date range, salary range)

---

## Notes & Blockers

### Current Blockers
- None (ready to start)

### Risk Mitigation
- Database backup before migrations
- Backup files before editing
- Test SQL syntax before running migrations
- Comprehensive error handling in API

### Communication
- Update task status after each subtask completion
- Document any unexpected issues immediately
- Create detailed validation report at end

---

**Task List Version History**
- v1.0 (2025-10-11): Initial task list creation
