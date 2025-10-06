# Archived Test Files - July 28, 2025

This directory contains test files that are no longer actively used in the project but are preserved for historical reference and potential future needs.

## Archive Structure

### `/apify_integration/`
Legacy tests for Apify Indeed scraper integration:
- `test_apify_security.py` - Security testing for Apify integration
- `test_apify_simple.py` - Basic Apify API testing
- `test_apify_with_user_input.py` - Interactive Apify testing
- `test_apify_working.py` - Working Apify integration tests

### `/step_implementations/`
Implementation-specific tests for development phases:
- `test_step_2_1_implementation.py` - User preferences system testing
- `test_step_2_2_implementation.py` - Workflow orchestration testing  
- `test_step_2_3_implementation.py` - Failure recovery mechanism testing
- `test_steve_glen_job_eligibility.py` - Job matching algorithm testing

### `/feature_specific/`
Completed feature tests that served their development purpose:
- `test_csv_template_mapping.py` - CSV content mapping system tests
- `test_document_generation_integration.py` - Document generation pipeline tests
- `test_email_application_system.py` - Email automation workflow tests
- `test_complete_application_workflow.py` - End-to-end application tests
- `test_link_tracking_security.py` - Link tracking security validation
- `test_end_to_end_security_assessment.py` - Comprehensive security testing

### `/development_debug/`
Development and debugging utilities:
- `test_complete_pipeline.py` - Pipeline integration testing
- `test_downstream_activities.py` - Activity flow testing
- `test_pure_gemini_api.py` - Direct Gemini API testing

### `/legacy_tests_directory/`
Complete archived `tests/` directory with all historical test files and supporting materials.

## Archive Reason

These files were archived on July 28, 2025, as part of project cleanup following:
- Completion of major feature implementations
- Achievement of 41.7% end-to-end test success rate
- Successful resolution of authentication and API routing issues
- Transition to production-ready testing with `test_end_to_end_workflow.py` and `test_api_endpoints.py`

## Active Testing

Current testing is maintained through:
- `test_end_to_end_workflow.py` - Comprehensive system validation
- `test_api_endpoints.py` - API routing and connectivity verification
- `test_results_end_to_end_workflow.json` - Latest test results and metrics

## Recovery

If any of these tests need to be restored:
1. Copy the relevant file back to the project root
2. Update imports and dependencies as needed
3. Verify compatibility with current system architecture