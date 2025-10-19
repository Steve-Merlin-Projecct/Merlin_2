# Discovery: Multi-Page Form Navigation
**Feature:** Multi-page application form navigation with state tracking and validation
**Created:** 2025-10-17
**Status:** Discovery Complete

---

## 1. Requirements Summary

**Core Requirement:** Enable form_filler.py to navigate through multi-page application forms (e.g., Indeed's multi-step applications) with:
- Automatic page detection and navigation
- Form state checkpointing (resume on failure)
- Validation error detection and retry logic
- Screenshot capture per page
- Database tracking of progress

**Business Value:**
- **Coverage increase:** 60-70% of applications are multi-page
- **Automation completeness:** MVP currently can only handle single-page forms
- **Reliability:** Checkpoint system prevents data loss on errors

---

## 2. Current System Analysis

### Existing Components (from codebase search)

**FormFiller (`form_filler.py`):**
- ✅ Single-page form filling works well
- ✅ Field detection with multiple selector strategies
- ✅ Screenshot capture (pre/post submit)
- ✅ Document upload (resume, cover letter)
- ❌ No multi-page navigation logic
- ❌ No state persistence/recovery
- ❌ No validation error detection

**Database Model (`models.py`):**
```python
class ApplicationSubmission(Base):
    submission_id = UUID
    job_id = String
    status = String  # 'submitted', 'failed', 'pending', 'reviewed'
    fields_filled = JSON  # Array of field names filled
    screenshot_urls = JSON
    error_details = JSON
    # Missing: checkpoint_data, current_page, validation_errors
```

**Form Mappings (`form_mappings/indeed.json`):**
- ✅ Detailed selectors for standard Indeed forms
- ✅ Submit button selectors
- ✅ Confirmation indicators
- ❌ No multi-page navigation patterns
- ❌ No "Next"/"Continue" button selectors
- ❌ No validation error selectors

**Screenshot Manager (`screenshot_manager.py`):**
- ✅ Handles pre_submit, post_submit, error screenshots
- ✅ Storage backend integration
- ⚠️ Needs extension for per-page screenshots

---

## 3. Technical Architecture

### New Components Required

**1. PageNavigator (`page_navigator.py`)**
```python
class PageNavigator:
    """
    Handles multi-page form detection and navigation

    Responsibilities:
    - Detect current page number
    - Find Next/Continue/Submit buttons
    - Navigate to next page
    - Detect final page (submission page)
    - Handle page transitions and loading
    """

    async def detect_current_page(page: Page) -> int
    async def find_navigation_button(page: Page) -> Tuple[Element, str]  # (button, type)
    async def navigate_to_next(page: Page) -> bool
    async def is_final_page(page: Page) -> bool
    async def wait_for_page_transition(page: Page, timeout: int)
```

**2. FormStateManager (`form_state_manager.py`)**
```python
class FormStateManager:
    """
    Manages form filling state and checkpointing

    Responsibilities:
    - Save progress after each page
    - Load checkpoint on retry
    - Clear checkpoint on completion
    - Track page-specific filled fields
    """

    async def save_checkpoint(
        submission_id: str,
        page_num: int,
        fields_filled: List[str],
        metadata: Dict
    ) -> bool

    async def load_checkpoint(submission_id: str) -> Optional[CheckpointData]
    async def clear_checkpoint(submission_id: str) -> bool
    async def update_page_progress(submission_id: str, page_num: int)
```

**3. ValidationHandler (`validation_handler.py`)**
```python
class ValidationHandler:
    """
    Detects and handles form validation errors

    Responsibilities:
    - Detect error messages on page
    - Parse which fields failed validation
    - Extract error messages
    - Suggest field corrections
    - Retry failed fields
    """

    async def check_for_errors(page: Page) -> List[ValidationError]
    async def get_error_fields(page: Page) -> List[str]
    async def extract_error_message(element: Element) -> str
    async def retry_field(page: Page, field_name: str, correction: str)
```

---

## 4. Database Schema Updates

**Add to `ApplicationSubmission` model:**
```sql
ALTER TABLE apify_application_submissions
ADD COLUMN checkpoint_data JSONB DEFAULT '{}',
ADD COLUMN current_page INTEGER DEFAULT 1,
ADD COLUMN total_pages INTEGER,
ADD COLUMN pages_completed INTEGER[] DEFAULT '{}',
ADD COLUMN validation_errors JSONB DEFAULT '[]',
ADD COLUMN navigation_history JSONB DEFAULT '[]';

CREATE INDEX idx_checkpoint_data ON apify_application_submissions USING gin(checkpoint_data);
```

**Checkpoint Data Structure:**
```json
{
  "current_page": 2,
  "total_pages": 3,
  "pages_completed": [1],
  "page_1_fields": ["full_name", "email", "phone"],
  "page_2_fields": ["resume", "cover_letter"],
  "last_screenshot": "screenshot_page_2_pre.png",
  "timestamp": "2025-10-17T10:30:00Z"
}
```

---

## 5. Enhanced Form Mappings

**Extend `indeed.json` with multi-page patterns:**
```json
{
  "platform": "indeed",
  "multipage_support": {
    "detection": {
      "indicators": [
        "presence of pagination dots",
        "step counter (e.g., 'Step 2 of 3')",
        "progress bar element"
      ]
    },
    "navigation_buttons": {
      "next": {
        "selectors": [
          "button:has-text('Next')",
          "button:has-text('Continue')",
          "button[id*='continue' i]",
          "button.ia-continueButton",
          "button[type='button'][class*='next']"
        ]
      },
      "submit": {
        "selectors": [
          "button:has-text('Submit application')",
          "button:has-text('Apply now')",
          "button[type='submit']"
        ]
      }
    },
    "validation_errors": {
      "error_container_selectors": [
        ".error-message",
        "[role='alert']",
        ".field-error",
        ".ia-FieldError"
      ],
      "field_error_selectors": [
        "input.error + .error-message",
        ".field-error-text",
        "span[class*='error']"
      ]
    },
    "page_groups": {
      "page_1_basic_info": ["full_name", "email", "phone", "location"],
      "page_2_experience": ["resume", "cover_letter", "years_experience"],
      "page_3_questions": ["screening_questions", "additional_info"],
      "page_4_review": ["review_confirmation"]
    }
  }
}
```

---

## 6. Implementation Workflow Changes

**Current Single-Page Flow:**
```
1. Navigate to URL
2. Detect form type
3. Fill all fields
4. Submit
5. Verify
6. Screenshot
```

**New Multi-Page Flow:**
```
1. Navigate to URL
2. Detect form type (single vs multi-page)
3. IF multi-page:
   a. Check for existing checkpoint
   b. Resume from checkpoint OR start fresh
   c. LOOP through pages:
      i.   Detect current page
      ii.  Fill page fields
      iii. Screenshot page
      iv.  Save checkpoint
      v.   Check for validation errors
      vi.  IF errors: retry fields
      vii. Find navigation button (Next/Submit)
      viii. Navigate
      ix.  Wait for page load
   d. On final page: submit
   e. Verify submission
   f. Clear checkpoint
4. ELSE: (single-page flow unchanged)
```

---

## 7. Edge Cases & Considerations

### Detected Challenges:

**1. Page Detection Ambiguity**
- Problem: Hard to detect total number of pages upfront
- Solution: Track dynamically, increment as we discover new pages

**2. Conditional Pages**
- Problem: Some pages only appear based on previous answers
- Solution: Flexible page counting, don't assume fixed page count

**3. Validation Error Recovery**
- Problem: Some fields may require specific format (phone, email)
- Solution: Implement field-specific retry logic with format correction

**4. Navigation Button Variety**
- Problem: "Next" vs "Continue" vs "Save & Continue" vs just arrow icon
- Solution: Multiple selector strategies per button type

**5. Checkpoint Staleness**
- Problem: Resume from old checkpoint might fail if form changed
- Solution: Add checkpoint timestamp, expire after 1 hour

**6. Screenshot Storage**
- Problem: Multiple screenshots per application (3-5 pages × 2 per page = 6-10 images)
- Solution: Compress images, store metadata separately

---

## 8. Testing Strategy

**Unit Tests:**
- PageNavigator: Button detection, page counting
- FormStateManager: Checkpoint save/load
- ValidationHandler: Error detection, field retry

**Integration Tests:**
- Multi-page navigation end-to-end
- Checkpoint recovery after failure
- Validation error handling

**E2E Tests (Real Forms):**
- Test with 10+ real multi-page Indeed applications
- Test checkpoint recovery by intentional mid-form exit
- Test validation error scenarios (invalid phone, email)

---

## 9. Success Criteria

**Functional:**
- ✅ Successfully navigate 2-5 page forms
- ✅ Checkpoint saves after each page
- ✅ Resume from checkpoint works on retry
- ✅ Validation errors detected and retried
- ✅ Screenshots captured per page

**Performance:**
- ✅ Multi-page forms complete in <120 seconds
- ✅ Checkpoint overhead <500ms per page
- ✅ Success rate >75% on multi-page forms (lower than single-page due to complexity)

**Reliability:**
- ✅ No data loss on failures (checkpoint recovery)
- ✅ Graceful degradation (fallback to manual if unrecoverable error)
- ✅ All errors logged with context

---

## 10. Assumptions & Decisions

**Assumptions:**
1. Indeed's multi-page forms follow consistent patterns
2. "Next" button is always visible and clickable when present
3. Validation errors appear immediately after field blur or page navigation
4. Checkpoint data <10KB per application (JSONB storage)

**Decisions Made:**
1. **Checkpoint storage:** Database JSONB column (not separate table)
   - Rationale: Simpler, faster, atomic updates
2. **Screenshot strategy:** One per page (pre-navigation)
   - Rationale: Balance between coverage and storage
3. **Page detection:** Dynamic (not fixed count)
   - Rationale: Handles conditional pages
4. **Validation retry:** Max 2 attempts per field
   - Rationale: Prevent infinite loops

---

## 11. Dependencies & Integration Points

**Existing Code to Modify:**
- `form_filler.py`: Add multi-page logic to `fill_application_form()`
- `models.py`: Add checkpoint columns
- `form_mappings/indeed.json`: Add navigation patterns
- `screenshot_manager.py`: Add per-page screenshot support

**New Files to Create:**
- `page_navigator.py`
- `form_state_manager.py`
- `validation_handler.py`
- `form_mappings/indeed_multipage.json` (or extend existing)

**No External Dependencies:** All functionality uses existing Playwright and SQLAlchemy

---

## 12. Risks & Mitigation

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| Indeed changes page structure | High | Medium | Monitor and update selectors monthly |
| Checkpoint data grows too large | Medium | Low | Limit to 10KB, compress if needed |
| Page detection fails | High | Low | Fallback to single-page flow |
| Navigation button not found | High | Medium | Multiple selector strategies + timeout |
| Validation errors undetected | Medium | Medium | Generic error detection patterns |

---

## Discovery Complete ✓

**Next Steps:**
1. Generate comprehensive task list (parent + sub-tasks)
2. Implement components sequentially
3. Test with real forms incrementally

**Estimated Effort:** 2-3 weeks (autonomous implementation)
