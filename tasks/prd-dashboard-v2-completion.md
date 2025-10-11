# PRD: Dashboard V2 Completion - Database Integration & Jobs View
**Version:** 1.0
**Date:** October 11, 2025
**Status:** In Progress
**Priority:** High

---

## 1. Executive Summary

Complete the Dashboard V2 by fixing critical database migration schema issues and connecting the Jobs view to real API endpoints. This will enable the dashboard to function with real data and achieve 80%+ performance improvements through database optimizations.

### Goals
1. Fix database migration schema compatibility issues
2. Successfully run all database migrations for performance optimization
3. Connect Jobs view to real API endpoints with live data
4. Ensure dashboard is fully operational with real database integration

### Success Metrics
- All 3 database migrations run successfully without errors
- Dashboard overview loads in <50ms (80% improvement from current ~250ms)
- Jobs view displays real data from database
- Zero schema-related errors in application logs

---

## 2. Background & Context

### Current State
- **Frontend**: 100% complete with beautiful Alpine.js interface
- **Backend APIs**: 100% complete with optimized endpoints
- **Real-time**: SSE integration working
- **Database Migrations**: Created but blocked by schema compatibility issues

### Problem Statement
Database migration files reference columns that don't exist in the actual PostgreSQL schema:
- `jobs.priority_score` (doesn't exist)
- `jobs.salary_currency` (doesn't exist)
- `jobs.location` (doesn't exist)
- `jobs.experience_level` (doesn't exist)

The Jobs view (`frontend_templates/dashboard_jobs.html`) currently uses mock data and needs to be connected to real API endpoints.

### Impact
- Dashboard performance remains at V1 levels (~250ms load time)
- No caching benefits from materialized views
- Jobs view shows static mock data instead of real job postings
- Pre-computed aggregations unavailable

---

## 3. Requirements

### Functional Requirements

#### FR1: Database Schema Audit
- Audit actual PostgreSQL schema for `jobs`, `job_applications`, `companies` tables
- Document all existing columns and their data types
- Identify discrepancies between migration files and actual schema

#### FR2: Migration File Updates
- Update `001_dashboard_optimization_indexes.sql` to use only existing columns
- Update `002_dashboard_materialized_views.sql` to match actual schema
- Update `003_dashboard_aggregation_tables.sql` with correct column references
- Ensure all SQL is valid and executable

#### FR3: Migration Execution
- Run migration runner script: `python run_dashboard_migrations.py`
- Verify all indexes created successfully
- Verify materialized views created
- Verify aggregation tables populated with data

#### FR4: Jobs API Endpoint
- Create `/api/v2/dashboard/jobs` endpoint in `modules/dashboard_api_v2.py`
- Support filtering: All, Eligible, Not Eligible, Already Applied
- Return job data with: title, company, location, salary, status, match_score, posted_date
- Implement pagination for large result sets

#### FR5: Jobs View Integration
- Update `frontend_templates/dashboard_jobs.html` to fetch from real API
- Remove mock data
- Connect filters to API query parameters
- Handle loading states and errors

### Non-Functional Requirements

#### NFR1: Performance
- Dashboard overview endpoint must respond in <50ms after migrations
- Jobs API must respond in <100ms for filtered queries
- Materialized views must refresh automatically or on-demand

#### NFR2: Data Integrity
- Migrations must not modify existing data
- All migrations must be reversible (rollback capability)
- No data loss during migration process

#### NFR3: Error Handling
- Migration script must validate SQL before execution
- Provide clear error messages for schema mismatches
- Jobs API must handle empty results gracefully

#### NFR4: Maintainability
- Document all schema assumptions in migration files
- Add inline comments explaining complex queries
- Update API documentation with new Jobs endpoint

---

## 4. Technical Approach

### Phase 1: Database Schema Audit
**Tools:** PostgreSQL `\d+` commands, SQLAlchemy inspector
**Deliverable:** Schema documentation file

**Steps:**
1. Connect to PostgreSQL database
2. Run `\d+ jobs` to get full table structure
3. Run `\d+ job_applications` for applications table
4. Run `\d+ companies` for companies table
5. Document all columns, types, constraints, indexes
6. Compare with migration file assumptions
7. Create schema mapping document

### Phase 2: Migration File Corrections
**Files to Update:**
- `database_migrations/001_dashboard_optimization_indexes.sql`
- `database_migrations/002_dashboard_materialized_views.sql`
- `database_migrations/003_dashboard_aggregation_tables.sql`

**Strategy:**
1. Replace non-existent columns with actual column names
2. Remove indexes/views referencing missing columns
3. Adjust aggregation logic to use available data
4. Add comments documenting column mappings
5. Test SQL syntax in PostgreSQL console

### Phase 3: Migration Execution
**Tool:** `run_dashboard_migrations.py`

**Steps:**
1. Backup database (safety measure)
2. Run migration script with verbose logging
3. Verify each migration completes successfully
4. Check created indexes: `\di`
5. Check materialized views: `\dv`
6. Check aggregation tables: `\dt`
7. Test dashboard overview API performance

### Phase 4: Jobs API Implementation
**File:** `modules/dashboard_api_v2.py`

**Endpoint Specification:**
```
GET /api/v2/dashboard/jobs
Query Parameters:
  - filter: 'all' | 'eligible' | 'not_eligible' | 'applied' (default: 'all')
  - page: integer (default: 1)
  - per_page: integer (default: 20, max: 100)

Response:
{
  "success": true,
  "jobs": [
    {
      "id": integer,
      "title": string,
      "company": string,
      "location": string | null,
      "salary_min": integer | null,
      "salary_max": integer | null,
      "status": string,
      "match_score": float | null,
      "posted_date": string (ISO 8601),
      "applied_date": string | null (ISO 8601),
      "url": string
    }
  ],
  "pagination": {
    "page": integer,
    "per_page": integer,
    "total": integer,
    "pages": integer
  }
}
```

**Implementation:**
1. Create route handler with authentication
2. Build SQLAlchemy query with filters
3. Add pagination logic
4. Format response with proper error handling
5. Add caching with TTL

### Phase 5: Jobs View Integration
**File:** `frontend_templates/dashboard_jobs.html`

**Changes:**
1. Remove mock data array
2. Add `fetchJobs(filter)` function to fetch from API
3. Update filter buttons to call `fetchJobs` with parameter
4. Add loading spinner during fetch
5. Handle empty results with user-friendly message
6. Handle errors with retry option
7. Update job card rendering to use real data fields

---

## 5. Task Breakdown

### Parent Task 1: Database Schema Audit & Documentation
**Estimated Time:** 1 hour
**Dependencies:** None
**Deliverable:** `docs/database-schema-actual.md`

### Parent Task 2: Fix Database Migration Files
**Estimated Time:** 2 hours
**Dependencies:** Task 1
**Deliverable:** Corrected SQL files

### Parent Task 3: Execute Database Migrations
**Estimated Time:** 1 hour
**Dependencies:** Task 2
**Deliverable:** Successful migration execution

### Parent Task 4: Implement Jobs API Endpoint
**Estimated Time:** 2 hours
**Dependencies:** Task 3 (for optimal performance)
**Deliverable:** Working `/api/v2/dashboard/jobs` endpoint

### Parent Task 5: Connect Jobs View to Real API
**Estimated Time:** 1 hour
**Dependencies:** Task 4
**Deliverable:** Jobs view with live data

### Parent Task 6: Testing & Validation
**Estimated Time:** 1 hour
**Dependencies:** Tasks 3, 4, 5
**Deliverable:** Test results and validation report

---

## 6. Testing Strategy

### Unit Tests
- Test Jobs API endpoint with various filters
- Test pagination logic
- Test empty result handling
- Test authentication enforcement

### Integration Tests
- Test dashboard overview with migrated database
- Test Jobs view end-to-end with real API
- Test filter interactions
- Test performance benchmarks

### Performance Tests
- Benchmark dashboard overview response time (target: <50ms)
- Benchmark Jobs API response time (target: <100ms)
- Verify materialized view refresh performance
- Test with realistic data volume

### Validation Tests
- Verify all migrations applied successfully
- Verify indexes created correctly
- Verify materialized views contain expected data
- Verify Jobs view displays accurate data

---

## 7. Risk Assessment

### High Risk
**Risk:** Database migrations fail due to unforeseen schema issues
**Mitigation:** Database backup before migration, thorough schema audit, test migrations in safe environment

**Risk:** Performance improvements not realized due to incorrect query optimization
**Mitigation:** Benchmark before/after, review query execution plans, optimize materialized view refresh strategy

### Medium Risk
**Risk:** Jobs API returns incorrect data due to filter logic errors
**Mitigation:** Comprehensive testing with various filter combinations, validate against database directly

**Risk:** Frontend integration breaks existing functionality
**Mitigation:** Preserve fallback to mock data during development, test all user interactions

### Low Risk
**Risk:** Migration script fails to parse complex SQL
**Mitigation:** Pre-validate SQL in PostgreSQL console, improve migration parser error handling

---

## 8. Success Criteria

### Must Have
- ✅ All 3 database migrations execute successfully
- ✅ Dashboard overview loads in <50ms
- ✅ Jobs API returns real data with all filters working
- ✅ Jobs view displays live data from database
- ✅ No schema-related errors in logs

### Should Have
- ✅ Materialized views refresh automatically
- ✅ Jobs API supports pagination
- ✅ Performance benchmarks documented
- ✅ API documentation updated

### Nice to Have
- ✅ Migration rollback scripts created
- ✅ Performance monitoring dashboard
- ✅ Additional filters for jobs (date range, salary range)

---

## 9. Dependencies

### Technical Dependencies
- PostgreSQL database accessible and running
- Flask application with `modules/dashboard_api_v2.py`
- SQLAlchemy ORM configured
- Existing dashboard authentication system

### External Dependencies
- None (all components internal to system)

---

## 10. Timeline

| Task | Duration | Start | Dependencies |
|------|----------|-------|--------------|
| Schema Audit | 1 hour | Immediate | None |
| Fix Migrations | 2 hours | After audit | Task 1 |
| Execute Migrations | 1 hour | After fixes | Task 2 |
| Jobs API | 2 hours | Parallel w/ Task 3 | Task 1 |
| Jobs View Integration | 1 hour | After API | Task 4 |
| Testing & Validation | 1 hour | After all | Tasks 3,4,5 |

**Total Estimated Time:** 8 hours
**Target Completion:** Same session

---

## 11. Documentation Requirements

### Code Documentation
- Inline comments in migration SQL files
- Docstrings for Jobs API functions
- Comments in Jobs view JavaScript

### API Documentation
- Update `docs/dashboard-v2-features.md` with Jobs endpoint
- Add request/response examples
- Document filter options and pagination

### User Documentation
- Update dashboard user guide with Jobs view functionality
- Document filter options for end users

---

## 12. Rollback Plan

### If Migrations Fail
1. Restore database from backup
2. Review migration error logs
3. Fix schema compatibility issues
4. Re-test migrations in isolated environment

### If Performance Degrades
1. Rollback to dashboard V1 route
2. Investigate query execution plans
3. Optimize materialized view definitions
4. Re-apply migrations with corrections

### If Jobs API Has Issues
1. Return 503 Service Unavailable temporarily
2. Fix API logic errors
3. Re-deploy corrected version
4. Fallback to mock data in frontend if needed

---

## 13. Post-Completion Checklist

- [ ] All database migrations applied successfully
- [ ] Dashboard overview performance <50ms verified
- [ ] Jobs API functional with all filters
- [ ] Jobs view displaying real data
- [ ] Performance benchmarks documented
- [ ] API documentation updated
- [ ] Code committed to version control
- [ ] Integration tests passing
- [ ] User acceptance testing completed
- [ ] Handoff documentation updated

---

## 14. Appendix

### Related Documents
- `DASHBOARD_V2_HANDOFF.md` - Original handoff document
- `docs/dashboard-v2-status.md` - Implementation status
- `docs/dashboard-v2-features.md` - Feature documentation
- `docs/discovery-findings-dashboard-redesign.md` - Discovery findings

### Migration Files
- `database_migrations/001_dashboard_optimization_indexes.sql`
- `database_migrations/002_dashboard_materialized_views.sql`
- `database_migrations/003_dashboard_aggregation_tables.sql`
- `run_dashboard_migrations.py`

### Key Implementation Files
- `modules/dashboard_api_v2.py` - Backend API
- `frontend_templates/dashboard_v2.html` - Main dashboard
- `frontend_templates/dashboard_jobs.html` - Jobs view
- `static/css/dashboard_v2.css` - Styling

---

**Document Version History**
- v1.0 (2025-10-11): Initial PRD creation for dashboard completion
