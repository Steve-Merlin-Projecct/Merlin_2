# Tasks: Complete Calendly Integration

Based on Product Requirements Document: `prd-complete-calendly-integration.md`

**Total Estimated Time**: 10 hours
**Priority**: High
**Status**: Planning

## Relevant Files

### Existing Files to Modify
- `modules/content/document_generation/template_engine.py` - Add URL tracking integration
- `modules/content/document_generation/document_generator.py` - Pass job/application context
- `modules/content/document_generation/resume_generator.py` - Update constructor and generation
- `modules/content/document_generation/cover_letter_generator.py` - Update constructor and generation
- `modules/link_tracking/link_tracker.py` - Already complete, just import and use
- `modules/document_routes.py` - Update API endpoints to accept job_id/application_id

### New Files to Create
- `modules/user_management/candidate_profile_manager.py` - Centralized candidate data retrieval
- `tests/test_calendly_integration.py` - Unit tests for URL tracking
- `tests/integration/test_calendly_workflow.py` - End-to-end integration tests
- `docs/component_docs/calendly/calendly_integration_guide.md` - Usage documentation

### Reference Files (No Changes Needed)
- `database_tools/generated/models.py` - User model with calendly_url field
- `database_tools/generated/schemas.py` - Pydantic schemas
- `docs/component_docs/link_tracking/link_tracking_system.md` - LinkTracker documentation

## Implementation Plan

---

## Phase 1: Core Integration (4 hours)

### Parent Task 1: TemplateEngine URL Tracking
**Estimated Time**: 2 hours

- [ ] 1.1: Add URL tracking configuration
  - [ ] 1.1.1: Define `TRACKABLE_URL_VARIABLES = ['calendly_url', 'linkedin_url', 'portfolio_url']` constant
  - [ ] 1.1.2: Define `URL_VARIABLE_TO_FUNCTION` mapping dict
  - [ ] 1.1.3: Add `enable_url_tracking` configuration flag to TemplateEngine constructor

- [ ] 1.2: Implement URL detection logic in `substitute_variables()`
  - [ ] 1.2.1: Update method signature to accept `job_id`, `application_id`, `enable_url_tracking` parameters
  - [ ] 1.2.2: Add type hints: `Optional[str]` for IDs, `bool` for flag
  - [ ] 1.2.3: Add docstring with parameter descriptions
  - [ ] 1.2.4: Create loop through variables to detect URL variables
  - [ ] 1.2.5: Check if variable name in `TRACKABLE_URL_VARIABLES` list
  - [ ] 1.2.6: Branch logic: URL variable → call `_get_tracked_url()`, else → standard substitution

- [ ] 1.3: Create `_get_tracked_url()` private method
  - [ ] 1.3.1: Define method signature with parameters: `original_url`, `link_function`, `job_id`, `application_id`
  - [ ] 1.3.2: Add comprehensive docstring with examples
  - [ ] 1.3.3: Import LinkTracker at method level (lazy import for error handling)
  - [ ] 1.3.4: Initialize LinkTracker instance
  - [ ] 1.3.5: Call `tracker.create_tracked_link()` with all parameters
  - [ ] 1.3.6: Extract `redirect_url` from result dict
  - [ ] 1.3.7: Add try/except block around LinkTracker calls
  - [ ] 1.3.8: Implement fallback: return `original_url` on any exception
  - [ ] 1.3.9: Add logging: `logger.info()` for success, `logger.error()` for failures

- [ ] 1.4: Add caching mechanism for tracked URLs
  - [ ] 1.4.1: Create `_tracked_url_cache` instance variable (dict) in `__init__`
  - [ ] 1.4.2: Generate cache key: `f"{job_id}:{application_id}:{link_function}:{original_url}"`
  - [ ] 1.4.3: Check cache before calling LinkTracker
  - [ ] 1.4.4: Store result in cache after successful LinkTracker call
  - [ ] 1.4.5: Add cache TTL tracking (optional: use timestamp-based expiry)

### Parent Task 2: Document Generator Updates
**Estimated Time**: 1.5 hours

- [ ] 2.1: Update BaseGenerator class (if exists) or individual generators
  - [ ] 2.1.1: Read `modules/content/document_generation/document_generator.py` to understand structure
  - [ ] 2.1.2: Add `job_id` parameter to constructor signature
  - [ ] 2.1.3: Add `application_id` parameter to constructor signature
  - [ ] 2.1.4: Store as instance variables: `self.job_id = job_id`
  - [ ] 2.1.5: Store as instance variables: `self.application_id = application_id`
  - [ ] 2.1.6: Update all docstrings to document new parameters

- [ ] 2.2: Update ResumeGenerator
  - [ ] 2.2.1: Read `modules/content/document_generation/resume_generator.py`
  - [ ] 2.2.2: Add `job_id` and `application_id` to constructor
  - [ ] 2.2.3: Pass to parent class if inheritance used
  - [ ] 2.2.4: Update all `template_engine.substitute_variables()` calls to pass job_id/application_id
  - [ ] 2.2.5: Verify backward compatibility (None values work)

- [ ] 2.3: Update CoverLetterGenerator
  - [ ] 2.3.1: Read `modules/content/document_generation/cover_letter_generator.py`
  - [ ] 2.3.2: Add `job_id` and `application_id` to constructor (job_id may already exist)
  - [ ] 2.3.3: Update all `template_engine.substitute_variables()` calls
  - [ ] 2.3.4: Verify backward compatibility

- [ ] 2.4: Update API endpoints in document_routes.py
  - [ ] 2.4.1: Read `modules/document_routes.py` to find resume generation endpoint
  - [ ] 2.4.2: Update resume endpoint to accept `job_id` (optional) in request JSON
  - [ ] 2.4.3: Update resume endpoint to accept `application_id` (optional) in request JSON
  - [ ] 2.4.4: Pass both IDs to ResumeGenerator constructor
  - [ ] 2.4.5: Update cover letter endpoint similarly
  - [ ] 2.4.6: Add request validation for UUID format (if provided)
  - [ ] 2.4.7: Update API response to include tracking metadata

### Parent Task 3: Candidate Profile Manager
**Estimated Time**: 0.5 hours

- [ ] 3.1: Create CandidateProfileManager module
  - [ ] 3.1.1: Create file `modules/user_management/candidate_profile_manager.py`
  - [ ] 3.1.2: Add module docstring explaining purpose
  - [ ] 3.1.3: Import necessary dependencies: psycopg2, logging, typing
  - [ ] 3.1.4: Create CandidateProfileManager class

- [ ] 3.2: Implement database connection method
  - [ ] 3.2.1: Add `_get_db_connection()` method (similar to LinkTracker pattern)
  - [ ] 3.2.2: Use environment variables for DB credentials
  - [ ] 3.2.3: Return connection with RealDictCursor

- [ ] 3.3: Implement `get_candidate_info()` method
  - [ ] 3.3.1: Define method signature: `get_candidate_info(self, user_id: str) -> Dict[str, Any]`
  - [ ] 3.3.2: Write SQL query to select all fields from user_candidate_info
  - [ ] 3.3.3: Execute query with user_id parameter
  - [ ] 3.3.4: Fetch result as dict
  - [ ] 3.3.5: Add error handling for user not found
  - [ ] 3.3.6: Return dict with all candidate fields

- [ ] 3.4: Implement convenience methods
  - [ ] 3.4.1: Add `get_calendly_url(user_id)` method
  - [ ] 3.4.2: Add `get_linkedin_url(user_id)` method
  - [ ] 3.4.3: Add `get_portfolio_url(user_id)` method
  - [ ] 3.4.4: Each method returns `Optional[str]`

---

## Phase 2: Testing & Validation (3 hours)

### Parent Task 4: Unit Tests
**Estimated Time**: 2 hours

- [ ] 4.1: Create test file structure
  - [ ] 4.1.1: Create `tests/test_calendly_integration.py`
  - [ ] 4.1.2: Add imports: pytest, unittest.mock, TemplateEngine, LinkTracker
  - [ ] 4.1.3: Create TestTemplateEngineURLTracking class
  - [ ] 4.1.4: Add module-level fixtures for test data

- [ ] 4.2: Test URL detection and tracking
  - [ ] 4.2.1: Write `test_calendly_url_variable_detected()`
    - Mock LinkTracker
    - Verify it's called when {{calendly_url}} present
  - [ ] 4.2.2: Write `test_linkedin_url_variable_detected()`
  - [ ] 4.2.3: Write `test_portfolio_url_variable_detected()`
  - [ ] 4.2.4: Write `test_non_url_variables_ignored()`
    - Verify LinkTracker NOT called for {{first_name}}

- [ ] 4.3: Test tracked URL generation
  - [ ] 4.3.1: Write `test_tracked_url_format()`
    - Verify redirect_url contains /track/{tracking_id}
  - [ ] 4.3.2: Write `test_job_id_passed_to_tracker()`
    - Assert LinkTracker called with correct job_id
  - [ ] 4.3.3: Write `test_application_id_passed_to_tracker()`
  - [ ] 4.3.4: Write `test_link_function_mapping()`
    - Verify 'calendly_url' → 'Calendly' function name

- [ ] 4.4: Test error handling
  - [ ] 4.4.1: Write `test_fallback_on_tracker_failure()`
    - Mock LinkTracker to raise exception
    - Verify original URL used
  - [ ] 4.4.2: Write `test_fallback_on_db_connection_error()`
  - [ ] 4.4.3: Write `test_logging_on_error()`
    - Verify logger.error() called

- [ ] 4.5: Test caching mechanism
  - [ ] 4.5.1: Write `test_url_cached_on_second_call()`
    - Call substitute_variables() twice
    - Verify LinkTracker only called once
  - [ ] 4.5.2: Write `test_cache_key_includes_job_context()`
    - Different job_id → different cache entry

- [ ] 4.6: Test CandidateProfileManager
  - [ ] 4.6.1: Write `test_get_candidate_info_returns_all_fields()`
  - [ ] 4.6.2: Write `test_get_calendly_url_returns_correct_value()`
  - [ ] 4.6.3: Write `test_user_not_found_returns_none()`

### Parent Task 5: Integration Tests
**Estimated Time**: 1 hour

- [ ] 5.1: Create integration test file
  - [ ] 5.1.1: Create `tests/integration/test_calendly_workflow.py`
  - [ ] 5.1.2: Add database setup/teardown fixtures
  - [ ] 5.1.3: Create test user with calendly_url in database

- [ ] 5.2: End-to-end document generation tests
  - [ ] 5.2.1: Write `test_cover_letter_with_tracked_calendly_url()`
    - Generate actual cover letter
    - Parse output document
    - Verify tracked URL present (contains /track/)
  - [ ] 5.2.2: Write `test_resume_with_tracked_calendly_url()`
  - [ ] 5.2.3: Write `test_multiple_documents_same_job()`
    - Generate resume + cover letter for same job
    - Verify same tracking_id reused (if caching works)

- [ ] 5.3: Click tracking workflow test
  - [ ] 5.3.1: Write `test_click_recorded_in_database()`
    - Generate document with tracked URL
    - Extract tracking_id from URL
    - Simulate HTTP request to /track/{tracking_id}
    - Verify click recorded in link_clicks table
  - [ ] 5.3.2: Write `test_redirect_to_original_calendly_url()`
    - Verify redirect response contains original URL

- [ ] 5.4: Analytics validation
  - [ ] 5.4.1: Write `test_analytics_show_calendly_clicks()`
    - Generate document, simulate click
    - Query link analytics API
    - Verify click count = 1

---

## Phase 3: Error Handling & Production Readiness (2 hours)

### Parent Task 6: Comprehensive Error Handling
**Estimated Time**: 1 hour

- [ ] 6.1: Add error handling to TemplateEngine
  - [ ] 6.1.1: Wrap LinkTracker import in try/except ImportError
  - [ ] 6.1.2: Handle case where LinkTracker module not available
  - [ ] 6.1.3: Add specific exception handling for DatabaseConnectionError
  - [ ] 6.1.4: Add specific exception handling for InvalidURLError
  - [ ] 6.1.5: Create custom exception: TrackingUnavailableError

- [ ] 6.2: Add logging throughout workflow
  - [ ] 6.2.1: Add logger.info() when tracked URL successfully generated
  - [ ] 6.2.2: Add logger.warning() when falling back to original URL
  - [ ] 6.2.3: Add logger.error() with full traceback on failures
  - [ ] 6.2.4: Add logger.debug() for cache hits
  - [ ] 6.2.5: Include tracking_id, job_id, application_id in all log messages

- [ ] 6.3: Add monitoring metadata
  - [ ] 6.3.1: Create tracking_metadata dict in document generation response
  - [ ] 6.3.2: Include fields: tracking_enabled (bool), urls_tracked (int), tracking_failures (int)
  - [ ] 6.3.3: Return metadata in API response
  - [ ] 6.3.4: Add metrics endpoint: `/api/tracking/metrics` (optional)

- [ ] 6.4: Implement graceful degradation
  - [ ] 6.4.1: Ensure document generation NEVER fails due to tracking errors
  - [ ] 6.4.2: Add feature flag to completely disable tracking if needed
  - [ ] 6.4.3: Create environment variable: ENABLE_URL_TRACKING (default: true)
  - [ ] 6.4.4: Test document generation with tracking disabled

### Parent Task 7: Performance Optimization
**Estimated Time**: 1 hour

- [ ] 7.1: Implement async URL tracking (optional enhancement)
  - [ ] 7.1.1: Evaluate if URL generation causes performance issues
  - [ ] 7.1.2: Consider async/await pattern for LinkTracker calls
  - [ ] 7.1.3: Benchmark current performance (target: < 200ms)
  - [ ] 7.1.4: Decide if optimization needed

- [ ] 7.2: Database connection pooling verification
  - [ ] 7.2.1: Verify LinkTracker uses connection pooling
  - [ ] 7.2.2: Verify CandidateProfileManager uses connection pooling
  - [ ] 7.2.3: Test under load (100 concurrent document generations)

- [ ] 7.3: Cache optimization
  - [ ] 7.3.1: Add cache size limit (e.g., max 1000 entries)
  - [ ] 7.3.2: Implement LRU eviction if cache grows too large
  - [ ] 7.3.3: Add cache statistics logging
  - [ ] 7.3.4: Add cache clear method for testing

- [ ] 7.4: Performance testing
  - [ ] 7.4.1: Write performance test: generate 100 documents with tracking
  - [ ] 7.4.2: Measure p50, p95, p99 latency
  - [ ] 7.4.3: Verify no performance regression vs. non-tracked documents
  - [ ] 7.4.4: Document baseline metrics in PRD

---

## Phase 4: Documentation & Examples (1 hour)

### Parent Task 8: API Documentation
**Estimated Time**: 0.5 hours

- [ ] 8.1: Update API endpoint documentation
  - [ ] 8.1.1: Document new `job_id` parameter in resume generation endpoint
  - [ ] 8.1.2: Document new `application_id` parameter in resume generation endpoint
  - [ ] 8.1.3: Update cover letter endpoint documentation
  - [ ] 8.1.4: Add example requests showing URL tracking
  - [ ] 8.1.5: Add example responses with tracking_metadata

- [ ] 8.2: Create usage examples
  - [ ] 8.2.1: Write example: Generate cover letter with Calendly tracking
  - [ ] 8.2.2: Write example: Generate resume with all tracked URLs
  - [ ] 8.2.3: Write example: Query Calendly link analytics
  - [ ] 8.2.4: Add curl commands for easy testing

- [ ] 8.3: Update OpenAPI/Swagger spec (if exists)
  - [ ] 8.3.1: Check if API spec file exists
  - [ ] 8.3.2: Add new parameters to spec
  - [ ] 8.3.3: Regenerate API documentation

### Parent Task 9: User Documentation
**Estimated Time**: 0.5 hours

- [ ] 9.1: Create Calendly integration guide
  - [ ] 9.1.1: Create `docs/component_docs/calendly/calendly_integration_guide.md`
  - [ ] 9.1.2: Add overview section explaining the integration
  - [ ] 9.1.3: Add setup instructions (setting calendly_url in database)
  - [ ] 9.1.4: Add usage examples with screenshots (if applicable)
  - [ ] 9.1.5: Add troubleshooting section

- [ ] 9.2: Update CLAUDE.md
  - [ ] 9.2.1: Update Calendly integration status to "Complete"
  - [ ] 9.2.2: Add completion date
  - [ ] 9.2.3: Reference new documentation files
  - [ ] 9.2.4: Update system architecture section if needed

- [ ] 9.3: Create troubleshooting guide
  - [ ] 9.3.1: Add section: "Calendly URL not appearing in documents"
  - [ ] 9.3.2: Add section: "Tracking not working (original URL shown)"
  - [ ] 9.3.3: Add section: "Clicks not recorded"
  - [ ] 9.3.4: Add section: "Performance issues with tracking"
  - [ ] 9.3.5: Include diagnostic queries and commands

- [ ] 9.4: Update master changelog
  - [ ] 9.4.1: Add entry in `docs/changelogs/master-changelog.md`
  - [ ] 9.4.2: Document completion date
  - [ ] 9.4.3: List key features added
  - [ ] 9.4.4: Reference PRD and tasks files

---

## Verification & Acceptance

### Parent Task 10: Final Validation
**Estimated Time**: Included in testing phases

- [ ] 10.1: Functional validation
  - [ ] 10.1.1: Generate cover letter via API, verify tracked Calendly URL present
  - [ ] 10.1.2: Click tracked URL in browser, verify redirect works
  - [ ] 10.1.3: Check link_clicks table, verify click recorded
  - [ ] 10.1.4: Query analytics API, verify metrics shown
  - [ ] 10.1.5: Generate document without job_id, verify backward compatibility

- [ ] 10.2: Technical validation
  - [ ] 10.2.1: All unit tests pass (pytest tests/test_calendly_integration.py)
  - [ ] 10.2.2: All integration tests pass
  - [ ] 10.2.3: No performance regression (run performance tests)
  - [ ] 10.2.4: No new linting errors (black, flake8, vulture)
  - [ ] 10.2.5: Database migrations clean (no manual schema changes)

- [ ] 10.3: Documentation validation
  - [ ] 10.3.1: All documentation files created and complete
  - [ ] 10.3.2: API examples tested and working
  - [ ] 10.3.3: CLAUDE.md updated
  - [ ] 10.3.4: Changelog entry added

- [ ] 10.4: Production readiness checklist
  - [ ] 10.4.1: Error handling tested (simulate LinkTracker failures)
  - [ ] 10.4.2: Logging verified (check log output for tracked URLs)
  - [ ] 10.4.3: Monitoring setup (if applicable)
  - [ ] 10.4.4: Rollback plan documented
  - [ ] 10.4.5: Feature flag tested (ENABLE_URL_TRACKING=false)

---

## Success Metrics (Track After Implementation)

- [ ] 11.1: Adoption metric - 100% of generated documents use tracked URLs
- [ ] 11.2: Reliability metric - 99.9% tracking success rate
- [ ] 11.3: Performance metric - < 200ms URL generation time (p95)
- [ ] 11.4: Engagement metric - Baseline Calendly click rate established
- [ ] 11.5: Error metric - Zero production document generation failures

---

## Notes

- **Dependency**: All phases depend on Phase 1 (Core Integration) being complete
- **Testing Strategy**: Write tests alongside implementation, not after
- **Backward Compatibility**: Critical - existing workflows must continue working
- **Feature Flag**: ENABLE_URL_TRACKING environment variable for safety
- **Rollback Plan**: Disable feature flag if issues arise in production

## Related Files

- PRD: `tasks/prd-complete-calendly-integration.md`
- Link Tracking Docs: `docs/component_docs/link_tracking/link_tracking_system.md`
- Variable Substitution PRD: `tasks/prd-variable-substitution-system.md`
