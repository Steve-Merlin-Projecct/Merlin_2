# Product Requirements Document: Complete Calendly Integration

## Document Information
**Version**: 1.0
**Date**: October 9, 2025
**Status**: Planning
**Priority**: High
**Related Documents**:
- `prd-variable-substitution-system.md`
- `tasks-prd-variable-substitution-system.md`
- `docs/component_docs/link_tracking/link_tracking_system.md`

## Executive Summary

Complete the Calendly integration by connecting the existing link tracking infrastructure with the template engine to enable automatic conversion of `{{calendly_url}}` template variables into tracked redirect URLs during document generation. This is the final 30% of work needed to achieve end-to-end Calendly tracking in job application documents.

## Current State Analysis

### ✅ What's Already Built (70% Complete)

#### 1. Database Schema
- `user_candidate_info.calendly_url` column exists (VARCHAR 500)
- Stores original Calendly scheduling URLs
- SQLAlchemy models auto-generated and current
- Migration: `migration_20250912_130825.py`

#### 2. Link Tracking System (Production Ready v2.16.5)
- Core `LinkTracker` class with full Calendly support
- `link_tracking` table with job/application associations
- `link_clicks` table for analytics
- REST API endpoints for link creation and click recording
- Redirect handler with click capture
- Analytics and reporting system

#### 3. Template System Foundation
- `TemplateEngine` supports `<<variable_name>>` format
- Basic variable substitution working
- `{{calendly_url}}` variable defined in PRD

### ❌ What's Missing (30% Remaining)

1. **Integration Layer**: No connection between TemplateEngine and LinkTracker
2. **Automatic URL Conversion**: Templates use original URLs, not tracked versions
3. **Job/Application Context**: LinkTracker not receiving job/application IDs during document generation
4. **Testing**: No integration tests for Calendly-specific workflows
5. **Documentation**: Missing usage examples for complete workflow

## Business Requirements

### Objectives
1. Enable automatic click tracking for all Calendly links in application documents
2. Maintain zero manual intervention - system generates tracked links automatically
3. Preserve original URL functionality as fallback
4. Track which jobs/applications generate Calendly clicks
5. Provide analytics on scheduling link engagement

### Success Criteria
- [ ] 100% of generated documents contain tracked Calendly URLs
- [ ] Click events successfully recorded with job/application context
- [ ] Original Calendly functionality preserved (meetings can be scheduled)
- [ ] Analytics dashboard shows Calendly-specific metrics
- [ ] Zero errors in production document generation
- [ ] Response time < 200ms for URL tracking generation

## Technical Requirements

### Component 1: TemplateEngine Enhancement

**File**: `modules/content/document_generation/template_engine.py`

#### Current Behavior
```python
# Simplified current implementation
def substitute_variables(template_text, variables):
    for key, value in variables.items():
        template_text = template_text.replace(f"{{{{{key}}}}}", value)
    return template_text
```

#### Required Behavior
```python
# Enhanced implementation needed
def substitute_variables(template_text, variables, job_id=None, application_id=None):
    # 1. Detect URL variables (calendly_url, linkedin_url, portfolio_url)
    # 2. For URL variables, call LinkTracker to generate tracked version
    # 3. Replace template variable with tracked URL
    # 4. For non-URL variables, use existing logic
    pass
```

#### Specific Requirements
1. **URL Detection**
   - Identify variables ending in `_url` pattern
   - Maintain whitelist: `calendly_url`, `linkedin_url`, `portfolio_url`
   - Ignore non-trackable URLs (internal links, etc.)

2. **LinkTracker Integration**
   - Import `LinkTracker` class
   - Initialize tracker with database connection
   - Call `create_tracked_link()` with appropriate parameters
   - Handle errors gracefully (fallback to original URL)

3. **Context Passing**
   - Accept `job_id` parameter (UUID, optional)
   - Accept `application_id` parameter (UUID, optional)
   - Pass context to LinkTracker for association tracking
   - Default to None if context unavailable

4. **Caching Strategy**
   - Cache tracked URLs for same job/application/original_url combination
   - Prevent duplicate tracking entries for same context
   - Implement 24-hour cache TTL

#### Implementation Details

**Method Signature**
```python
def substitute_variables(
    self,
    template_text: str,
    variables: Dict[str, str],
    job_id: Optional[str] = None,
    application_id: Optional[str] = None,
    enable_url_tracking: bool = True
) -> str:
    """
    Substitute template variables with values, converting URLs to tracked versions.

    Args:
        template_text: Template content with {{variable}} markers
        variables: Dict mapping variable names to values
        job_id: Optional job UUID for tracking context
        application_id: Optional application UUID for tracking context
        enable_url_tracking: Flag to disable tracking (for testing/debugging)

    Returns:
        Template text with all variables substituted
    """
```

**URL Tracking Logic**
```python
TRACKABLE_URL_VARIABLES = ['calendly_url', 'linkedin_url', 'portfolio_url']

def _get_tracked_url(
    self,
    original_url: str,
    link_function: str,
    job_id: Optional[str],
    application_id: Optional[str]
) -> str:
    """
    Generate tracked redirect URL using LinkTracker.

    Args:
        original_url: The actual destination URL
        link_function: Category ('Calendly', 'LinkedIn', 'Portfolio')
        job_id: Job UUID for association
        application_id: Application UUID for association

    Returns:
        Tracked redirect URL or original URL if tracking fails
    """
    try:
        from modules.link_tracking.link_tracker import LinkTracker

        tracker = LinkTracker()
        result = tracker.create_tracked_link(
            original_url=original_url,
            link_function=link_function,
            job_id=job_id,
            application_id=application_id,
            link_type='profile',
            description=f'{link_function} link for job application'
        )
        return result['redirect_url']
    except Exception as e:
        logger.error(f"URL tracking failed: {e}, using original URL")
        return original_url  # Graceful fallback
```

**Variable Name to Link Function Mapping**
```python
URL_VARIABLE_TO_FUNCTION = {
    'calendly_url': 'Calendly',
    'linkedin_url': 'LinkedIn',
    'portfolio_url': 'Portfolio'
}
```

### Component 2: Document Generator Integration

**Files**:
- `modules/content/document_generation/document_generator.py`
- `modules/content/document_generation/resume_generator.py`
- `modules/content/document_generation/cover_letter_generator.py`

#### Required Changes

**Pass Context to TemplateEngine**
```python
# Current pattern
rendered = self.template_engine.substitute_variables(template, variables)

# Required pattern
rendered = self.template_engine.substitute_variables(
    template=template,
    variables=variables,
    job_id=self.job_id,  # Must be available in generator
    application_id=self.application_id  # Must be available in generator
)
```

#### Specific Requirements
1. **Constructor Updates**
   - Add `job_id` parameter to all generator constructors
   - Add `application_id` parameter to all generator constructors
   - Store as instance variables for template engine calls

2. **API Endpoint Updates**
   - Update resume/cover letter generation endpoints
   - Accept `job_id` and `application_id` in request payload
   - Validate UUIDs before passing to generators

3. **Backward Compatibility**
   - Make job/application IDs optional parameters
   - System works without them (no tracking, uses original URLs)
   - No breaking changes to existing API contracts

### Component 3: Data Retrieval Layer

**File**: `modules/user_management/candidate_profile_manager.py` (NEW or enhance existing)

#### Purpose
Centralized module to retrieve candidate information including Calendly URL.

#### Required Methods

```python
class CandidateProfileManager:
    """Manages candidate personal information and URLs."""

    def get_candidate_info(self, user_id: str) -> Dict[str, Any]:
        """
        Retrieve all candidate information for document generation.

        Args:
            user_id: User identifier (default: 'steve_glen')

        Returns:
            Dict containing: first_name, last_name, email, phone,
            mailing_address, calendly_url, linkedin_url, portfolio_url
        """
        pass

    def get_calendly_url(self, user_id: str) -> Optional[str]:
        """Get original (non-tracked) Calendly URL for user."""
        pass

    def update_calendly_url(self, user_id: str, calendly_url: str) -> bool:
        """Update user's Calendly URL."""
        pass
```

#### Database Query
```sql
SELECT
    first_name,
    last_name,
    email,
    phone_number,
    mailing_address,
    calendly_url,
    linkedin_url,
    portfolio_url
FROM user_candidate_info
WHERE user_id = %s;
```

### Component 4: Error Handling & Logging

#### Requirements

1. **Graceful Degradation**
   - If LinkTracker fails, use original URL
   - Log error but don't crash document generation
   - Set flag in metadata indicating tracking unavailable

2. **Logging Strategy**
   ```python
   logger.info(f"Generated tracked Calendly URL: {tracking_id}")
   logger.warning(f"LinkTracker unavailable, using original URL")
   logger.error(f"Failed to create tracked link: {error_details}")
   ```

3. **Monitoring Metrics**
   - Track percentage of successful URL tracking operations
   - Alert if tracking success rate drops below 95%
   - Monitor LinkTracker API response times

### Component 5: Testing Requirements

#### Unit Tests

**File**: `tests/test_calendly_integration.py` (NEW)

```python
class TestCalendlyIntegration:

    def test_template_engine_creates_tracked_url(self):
        """Verify TemplateEngine calls LinkTracker for calendly_url."""
        pass

    def test_tracked_url_contains_tracking_id(self):
        """Verify generated URL has format /track/{tracking_id}."""
        pass

    def test_original_url_fallback_on_error(self):
        """Verify original URL used if LinkTracker fails."""
        pass

    def test_job_application_context_passed(self):
        """Verify job_id and application_id passed to LinkTracker."""
        pass

    def test_non_url_variables_unaffected(self):
        """Verify name/email variables still work normally."""
        pass
```

#### Integration Tests

**File**: `tests/integration/test_calendly_workflow.py` (NEW)

```python
class TestCalendlyWorkflow:

    def test_end_to_end_cover_letter_generation(self):
        """Generate cover letter and verify tracked Calendly URL included."""
        pass

    def test_click_recording_works(self):
        """Simulate click on tracked URL, verify analytics recorded."""
        pass

    def test_multiple_documents_same_job(self):
        """Verify same tracking ID reused for same job context."""
        pass
```

#### Manual Test Cases

1. **Test Case 1: Cover Letter Generation**
   - Input: Job with valid job_id, candidate with Calendly URL
   - Expected: Generated cover letter contains `/track/{tracking_id}` URL
   - Verify: Clicking URL redirects to actual Calendly page
   - Verify: Click recorded in `link_clicks` table

2. **Test Case 2: Missing Calendly URL**
   - Input: Candidate without calendly_url in database
   - Expected: Template variable replaced with empty string or placeholder
   - Verify: Document generation doesn't fail

3. **Test Case 3: LinkTracker Unavailable**
   - Input: Simulate database connection failure
   - Expected: Original Calendly URL used as fallback
   - Verify: Error logged, document still generated

## Implementation Plan

### Phase 1: Core Integration (Priority: High)
**Estimated Time**: 4 hours

- [ ] 1.1: Enhance TemplateEngine with URL detection logic
- [ ] 1.2: Implement _get_tracked_url() method with LinkTracker integration
- [ ] 1.3: Add job_id/application_id parameters to substitute_variables()
- [ ] 1.4: Update all document generators to pass context parameters
- [ ] 1.5: Create CandidateProfileManager for data retrieval

### Phase 2: Testing & Validation (Priority: High)
**Estimated Time**: 3 hours

- [ ] 2.1: Write unit tests for TemplateEngine URL tracking
- [ ] 2.2: Write integration tests for end-to-end workflow
- [ ] 2.3: Manual testing with real Calendly account
- [ ] 2.4: Verify click tracking and analytics work correctly

### Phase 3: Error Handling & Production Readiness (Priority: Medium)
**Estimated Time**: 2 hours

- [ ] 3.1: Implement comprehensive error handling
- [ ] 3.2: Add logging and monitoring
- [ ] 3.3: Create fallback mechanisms
- [ ] 3.4: Performance testing (URL generation < 200ms)

### Phase 4: Documentation & Examples (Priority: Medium)
**Estimated Time**: 1 hour

- [ ] 4.1: Update API documentation with new parameters
- [ ] 4.2: Create usage examples for Calendly workflow
- [ ] 4.3: Add troubleshooting guide
- [ ] 4.4: Update CLAUDE.md with Calendly integration status

**Total Estimated Time**: 10 hours

## API Changes

### Resume Generation Endpoint

**Before**:
```http
POST /api/generate-resume
{
  "user_id": "steve_glen",
  "template_name": "professional_resume"
}
```

**After**:
```http
POST /api/generate-resume
{
  "user_id": "steve_glen",
  "template_name": "professional_resume",
  "job_id": "550e8400-e29b-41d4-a716-446655440000",  # NEW: Optional
  "application_id": "650e8400-e29b-41d4-a716-446655440001"  # NEW: Optional
}
```

### Cover Letter Generation Endpoint

**Before**:
```http
POST /api/generate-cover-letter
{
  "user_id": "steve_glen",
  "job_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**After**:
```http
POST /api/generate-cover-letter
{
  "user_id": "steve_glen",
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "application_id": "650e8400-e29b-41d4-a716-446655440001"  # NEW: Optional
}
```

**Note**: `job_id` already exists in cover letter endpoint, just needs to be passed to TemplateEngine.

## Data Flow Diagram

```
[User Request]
    ↓
[Document Generator API]
    ↓ (calls with job_id, application_id)
[Resume/CoverLetter Generator]
    ↓ (retrieves candidate info)
[CandidateProfileManager]
    ↓ (gets calendly_url from DB)
[Database: user_candidate_info]
    ↓ (calendly_url returned)
[TemplateEngine.substitute_variables()]
    ↓ (detects calendly_url variable)
[TemplateEngine._get_tracked_url()]
    ↓ (creates tracked link)
[LinkTracker.create_tracked_link()]
    ↓ (stores in DB with job/app context)
[Database: link_tracking]
    ↓ (returns redirect_url)
[TemplateEngine]
    ↓ (substitutes {{calendly_url}} with redirect_url)
[Generated Document with Tracked URL]
```

## Click Tracking Flow

```
[User Clicks Link in Email/Cover Letter]
    ↓
[Redirect Handler: /track/{tracking_id}]
    ↓ (looks up original URL)
[Database: link_tracking]
    ↓ (records click event)
[Database: link_clicks]
    ↓ (redirects to original Calendly URL)
[Calendly Scheduling Page]
```

## Analytics & Reporting

### Available Metrics After Implementation

1. **Link Performance**
   - Total Calendly link clicks across all applications
   - Click-through rate per job posting
   - Time to first click after application sent
   - Unique users clicking scheduling links

2. **Job-Level Insights**
   - Which jobs generate most Calendly clicks
   - Correlation between clicks and interview invitations
   - Click source breakdown (email client, LinkedIn, direct)

3. **Application Funnel**
   - Applications sent → Calendly clicks → Meetings scheduled
   - Conversion rate optimization
   - A/B testing different link placements

### Dashboard Queries

```sql
-- Calendly click summary by job
SELECT
    lt.job_id,
    paj.job_title,
    paj.company_name,
    COUNT(lc.click_id) as total_clicks,
    COUNT(DISTINCT lc.session_id) as unique_sessions,
    MIN(lc.clicked_at) as first_click,
    MAX(lc.clicked_at) as last_click
FROM link_tracking lt
JOIN link_clicks lc ON lt.tracking_id = lc.tracking_id
JOIN pre_analyzed_jobs paj ON lt.job_id = paj.id
WHERE lt.link_function = 'Calendly'
GROUP BY lt.job_id, paj.job_title, paj.company_name
ORDER BY total_clicks DESC;
```

## Security Considerations

1. **URL Validation**
   - Verify Calendly URLs match expected format
   - Prevent injection of malicious URLs
   - Sanitize all URL parameters

2. **Rate Limiting**
   - Prevent abuse of URL tracking generation
   - Implement rate limits on link creation API
   - Monitor for unusual tracking patterns

3. **Data Privacy**
   - No PII in tracking URLs
   - IP anonymization after 90 days (already implemented)
   - GDPR compliance for click data

## Risks & Mitigation

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| LinkTracker service unavailable | Documents use untracked URLs | Low | Graceful fallback to original URLs |
| Database connection failure | URL tracking fails | Low | Cache recent tracked URLs, retry logic |
| Performance degradation | Slow document generation | Medium | Implement caching, async URL generation |
| Breaking existing workflows | Production documents fail | Low | Extensive testing, backward compatibility |
| Calendly URL format changes | Redirects break | Low | URL validation, error monitoring |

## Acceptance Criteria

### Functional Requirements
- [ ] Cover letters include tracked Calendly URLs
- [ ] Resumes include tracked Calendly URLs
- [ ] Clicks are recorded with job/application context
- [ ] Original Calendly functionality preserved (meetings can be scheduled)
- [ ] Analytics dashboard shows Calendly metrics

### Technical Requirements
- [ ] All unit tests pass (100% coverage for new code)
- [ ] All integration tests pass
- [ ] No performance regression (document generation < 2s)
- [ ] URL tracking generation < 200ms
- [ ] Error rate < 0.1% in production

### Documentation Requirements
- [ ] API documentation updated with new parameters
- [ ] Usage examples created
- [ ] Troubleshooting guide written
- [ ] CLAUDE.md updated with completion status

## Success Metrics (30 Days Post-Launch)

1. **Adoption**: 100% of generated documents use tracked URLs
2. **Reliability**: 99.9% tracking success rate
3. **Performance**: < 200ms URL generation time (p95)
4. **Engagement**: Baseline established for Calendly click rate
5. **Zero Production Errors**: No document generation failures due to tracking

## Future Enhancements (Out of Scope)

1. **Multi-User Support**: Extend beyond Steve Glen to multiple users
2. **Custom Tracking Domains**: Branded URLs (steveglen.com/meet)
3. **Advanced Analytics**: ML insights on click patterns
4. **A/B Testing**: Test different Calendly link placements
5. **Webhook Integration**: Calendly event notifications back to system

## Related Documentation

- [Link Tracking System Documentation](../docs/component_docs/link_tracking/link_tracking_system.md)
- [External Domain Integration Guide](../export/external_domain_integration_guide.md)
- [Variable Substitution PRD](./prd-variable-substitution-system.md)
- [Variable Substitution Tasks](./tasks-prd-variable-substitution-system.md)

## Approval & Sign-off

**Document Owner**: Development Team
**Stakeholder**: Steve Glen
**Approval Date**: [Pending]
**Implementation Start**: [Pending Approval]

---

**End of Document**
