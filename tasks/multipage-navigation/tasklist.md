# Task List: Multi-Page Form Navigation
**Feature:** Multi-page application form navigation with state tracking
**Created:** 2025-10-17
**Status:** Ready for Implementation

---

## Parent Tasks Overview

1. **[Foundation]** Database Schema & Models
2. **[Core]** Page Navigation System
3. **[Core]** Form State Management
4. **[Core]** Validation Error Handling
5. **[Integration]** Form Filler Integration
6. **[Configuration]** Enhanced Form Mappings
7. **[Testing]** Comprehensive Testing Suite
8. **[Documentation]** Documentation & Examples

---

## Task 1: Database Schema & Models ⏳
**Status:** `[x]`
**Estimated Time:** 3-4 hours
**Dependencies:** None

### Sub-tasks:

- [x] **1.1** Write SQL migration to add checkpoint columns
  - Add `checkpoint_data JSONB`
  - Add `current_page INTEGER`
  - Add `total_pages INTEGER`
  - Add `pages_completed INTEGER[]`
  - Add `validation_errors JSONB`
  - Add `navigation_history JSONB`
  - Create GIN index on checkpoint_data

- [x] **1.2** Update SQLAlchemy model in `models.py`
  - Add new column definitions
  - Update `to_dict()` method
  - Add checkpoint-related helper methods

- [x] **1.3** Create migration script
  - File: `modules/application_automation/migrations/002_add_multipage_support.sql`
  - Include rollback script

- [x] **1.4** Test migration on development database
  - Apply migration
  - Verify columns created
  - Test rollback

**Completion Criteria:**
- ✓ Migration script runs successfully
- ✓ All columns added with correct types
- ✓ Model updated and imports correctly
- ✓ No breaking changes to existing code

---

## Task 2: Page Navigation System ⏳
**Status:** `[ ]`
**Estimated Time:** 6-8 hours
**Dependencies:** None

### Sub-tasks:

- [ ] **2.1** Create `page_navigator.py` with base class
  - File: `modules/application_automation/page_navigator.py`
  - Implement `PageNavigator` class skeleton
  - Add comprehensive docstrings

- [ ] **2.2** Implement page detection logic
  - Method: `detect_current_page(page: Page) -> int`
  - Look for pagination indicators
  - Look for step counters ("Step 2 of 3")
  - Look for progress bars
  - Return current page number (default: 1)

- [ ] **2.3** Implement navigation button detection
  - Method: `find_navigation_button(page: Page) -> Tuple[Element, ButtonType]`
  - Try multiple selector strategies
  - Detect button type: "next", "continue", "submit"
  - Return button element and type
  - Handle button not found gracefully

- [ ] **2.4** Implement page navigation
  - Method: `navigate_to_next(page: Page) -> bool`
  - Click navigation button
  - Wait for page transition
  - Verify new page loaded
  - Return success status

- [ ] **2.5** Implement final page detection
  - Method: `is_final_page(page: Page) -> bool`
  - Check for submit button (vs next/continue)
  - Check for confirmation indicators
  - Return boolean

- [ ] **2.6** Implement page transition waiting
  - Method: `wait_for_page_transition(page: Page, timeout: int)`
  - Wait for network idle
  - Wait for DOM changes
  - Handle loading states

- [ ] **2.7** Add error handling and logging
  - Comprehensive try/except blocks
  - Detailed logging at each step
  - Custom exceptions for navigation failures

**Completion Criteria:**
- ✓ PageNavigator class fully implemented
- ✓ All methods have docstrings and type hints
- ✓ Navigation works with real Indeed multi-page forms
- ✓ Graceful error handling

---

## Task 3: Form State Management ⏳
**Status:** `[ ]`
**Estimated Time:** 5-6 hours
**Dependencies:** Task 1 (Database Schema)

### Sub-tasks:

- [ ] **3.1** Create `form_state_manager.py` with base class
  - File: `modules/application_automation/form_state_manager.py`
  - Implement `FormStateManager` class
  - Add database session management

- [ ] **3.2** Implement checkpoint saving
  - Method: `save_checkpoint(submission_id, page_num, fields_filled, metadata) -> bool`
  - Construct checkpoint data structure
  - Update database record
  - Handle serialization (JSON)
  - Return success status

- [ ] **3.3** Implement checkpoint loading
  - Method: `load_checkpoint(submission_id) -> Optional[CheckpointData]`
  - Query database for checkpoint
  - Deserialize checkpoint data
  - Validate checkpoint (not stale)
  - Return CheckpointData object or None

- [ ] **3.4** Implement checkpoint clearing
  - Method: `clear_checkpoint(submission_id) -> bool`
  - Clear checkpoint_data column
  - Reset page counters
  - Return success status

- [ ] **3.5** Implement page progress tracking
  - Method: `update_page_progress(submission_id, page_num)`
  - Update current_page
  - Add to pages_completed array
  - Update navigation_history

- [ ] **3.6** Define CheckpointData dataclass
  - Fields: current_page, total_pages, page_fields, timestamp
  - Serialization methods (to_dict, from_dict)
  - Validation method (is_stale, is_valid)

- [ ] **3.7** Add checkpoint expiration logic
  - Checkpoint expires after 1 hour
  - Method: `is_checkpoint_valid(checkpoint: CheckpointData) -> bool`

**Completion Criteria:**
- ✓ FormStateManager class fully implemented
- ✓ Checkpoint save/load/clear works correctly
- ✓ Checkpoint expiration prevents stale resumes
- ✓ Database operations are transactional

---

## Task 4: Validation Error Handling ⏳
**Status:** `[ ]`
**Estimated Time:** 4-5 hours
**Dependencies:** None

### Sub-tasks:

- [ ] **4.1** Create `validation_handler.py` with base class
  - File: `modules/application_automation/validation_handler.py`
  - Implement `ValidationHandler` class
  - Define `ValidationError` dataclass

- [ ] **4.2** Implement error detection
  - Method: `check_for_errors(page: Page) -> List[ValidationError]`
  - Look for error containers
  - Look for field-specific errors
  - Extract error messages
  - Return list of ValidationError objects

- [ ] **4.3** Implement field error extraction
  - Method: `get_error_fields(page: Page) -> List[str]`
  - Identify which fields have errors
  - Map error elements to field names
  - Return list of field names

- [ ] **4.4** Implement error message extraction
  - Method: `extract_error_message(element: Element) -> str`
  - Get text content of error element
  - Clean up message (strip whitespace)
  - Return error message string

- [ ] **4.5** Implement field retry logic
  - Method: `retry_field(page: Page, field_name: str, correction: str)`
  - Re-fill field with corrected value
  - Apply format corrections (phone, email)
  - Wait for validation
  - Check if error cleared

- [ ] **4.6** Add format correction utilities
  - Phone number formatting (e.g., (555) 123-4567)
  - Email validation
  - Date formatting
  - Return corrected value

- [ ] **4.7** Define ValidationError dataclass
  - Fields: field_name, error_message, element, retry_count
  - Methods: to_dict()

**Completion Criteria:**
- ✓ ValidationHandler class fully implemented
- ✓ Errors detected accurately
- ✓ Field retry logic works
- ✓ Format corrections applied correctly

---

## Task 5: Form Filler Integration ⏳
**Status:** `[ ]`
**Estimated Time:** 8-10 hours
**Dependencies:** Tasks 2, 3, 4

### Sub-tasks:

- [ ] **5.1** Refactor `fill_application_form()` method
  - Add multi-page detection
  - Branch: single-page vs multi-page flow
  - Maintain backward compatibility

- [ ] **5.2** Implement multi-page form workflow
  - Method: `_fill_multipage_form(page, data, application_id) -> FormFillResult`
  - Initialize PageNavigator, FormStateManager, ValidationHandler
  - Check for existing checkpoint
  - Loop through pages

- [ ] **5.3** Implement per-page filling logic
  - Method: `_fill_page_fields(page, data, page_num) -> List[str]`
  - Determine fields for current page
  - Fill fields sequentially
  - Return list of filled fields

- [ ] **5.4** Integrate checkpoint system
  - Save checkpoint after each page
  - Load checkpoint on retry
  - Clear checkpoint on completion

- [ ] **5.5** Integrate validation error handling
  - Check for errors after filling page
  - Retry failed fields with corrections
  - Max 2 retry attempts per field

- [ ] **5.6** Integrate screenshot capture per page
  - Capture before navigation
  - Store with page number in filename
  - Update screenshot_manager to handle multiple screenshots

- [ ] **5.7** Implement page navigation loop
  - Fill page → screenshot → checkpoint → validate → navigate
  - Detect final page
  - Break loop on final page
  - Submit on final page

- [ ] **5.8** Add comprehensive error handling
  - Try/except around each page
  - Log errors with page context
  - Save error screenshots
  - Graceful degradation

**Completion Criteria:**
- ✓ Multi-page workflow integrated into form_filler.py
- ✓ Single-page flow still works (backward compatible)
- ✓ Checkpoint recovery works on retry
- ✓ Validation errors handled correctly
- ✓ Screenshots captured per page

---

## Task 6: Enhanced Form Mappings ⏳
**Status:** `[ ]`
**Estimated Time:** 3-4 hours
**Dependencies:** None

### Sub-tasks:

- [ ] **6.1** Extend `indeed.json` with multi-page patterns
  - Add `multipage_support` section
  - Define navigation button selectors
  - Define validation error selectors
  - Define page detection patterns

- [ ] **6.2** Define page groups
  - Map fields to typical page groups
  - Example: page_1_basic_info, page_2_experience, etc.
  - Allow flexible grouping (not strict)

- [ ] **6.3** Add navigation button selectors
  - "Next" button selectors (5+ variations)
  - "Continue" button selectors
  - "Submit" button selectors (separate from single-page)

- [ ] **6.4** Add validation error selectors
  - Error container selectors
  - Field-specific error selectors
  - Error message extraction patterns

- [ ] **6.5** Add page indicator selectors
  - Pagination dots
  - Step counters ("Step 2 of 3")
  - Progress bars

- [ ] **6.6** Document selector patterns
  - Add comments explaining each pattern
  - Add notes on Indeed's multi-page behavior

**Completion Criteria:**
- ✓ indeed.json extended with complete multi-page support
- ✓ All selector categories covered
- ✓ Selectors tested with real forms
- ✓ Documentation clear and comprehensive

---

## Task 7: Comprehensive Testing Suite ⏳
**Status:** `[ ]`
**Estimated Time:** 6-8 hours
**Dependencies:** Tasks 2, 3, 4, 5

### Sub-tasks:

- [ ] **7.1** Create unit tests for PageNavigator
  - File: `modules/application_automation/tests/test_page_navigator.py`
  - Test page detection
  - Test button finding
  - Test navigation
  - Mock Playwright page object

- [ ] **7.2** Create unit tests for FormStateManager
  - File: `modules/application_automation/tests/test_form_state_manager.py`
  - Test checkpoint save/load
  - Test checkpoint expiration
  - Test page progress tracking
  - Mock database

- [ ] **7.3** Create unit tests for ValidationHandler
  - File: `modules/application_automation/tests/test_validation_handler.py`
  - Test error detection
  - Test field retry
  - Test format corrections
  - Mock Playwright page

- [ ] **7.4** Create integration test for multi-page workflow
  - File: `modules/application_automation/tests/test_multipage_integration.py`
  - Test full multi-page flow
  - Test checkpoint recovery
  - Test validation error handling
  - Use Playwright with mock server

- [ ] **7.5** Create E2E test with real Indeed forms
  - File: `modules/application_automation/tests/test_multipage_e2e.py`
  - Test with 3+ real multi-page applications
  - Test checkpoint recovery (intentional exit)
  - Test validation error scenarios
  - Requires real test account

- [ ] **7.6** Add test fixtures and utilities
  - Mock page objects
  - Mock database sessions
  - Sample form HTML
  - Test data builders

- [ ] **7.7** Run full test suite and fix issues
  - Run: `pytest modules/application_automation/tests/ -v`
  - Achieve >80% code coverage
  - Fix any failing tests

**Completion Criteria:**
- ✓ All unit tests passing
- ✓ Integration tests passing
- ✓ E2E tests passing with real forms
- ✓ Code coverage >80%

---

## Task 8: Documentation & Examples ⏳
**Status:** `[ ]`
**Estimated Time:** 3-4 hours
**Dependencies:** All previous tasks

### Sub-tasks:

- [ ] **8.1** Update README.md
  - Add multi-page support section
  - Update feature list
  - Add usage examples
  - Update limitations section

- [ ] **8.2** Create multi-page architecture doc
  - File: `modules/application_automation/docs/MULTIPAGE_ARCHITECTURE.md`
  - Explain component interactions
  - Explain checkpoint system
  - Explain validation handling
  - Include diagrams (flowcharts)

- [ ] **8.3** Update API documentation
  - Document checkpoint-related fields
  - Document new error types
  - Update response schemas

- [ ] **8.4** Create troubleshooting guide
  - File: `modules/application_automation/docs/MULTIPAGE_TROUBLESHOOTING.md`
  - Common issues and solutions
  - Debugging tips
  - Checkpoint recovery procedures

- [ ] **8.5** Add inline code documentation
  - Comprehensive docstrings for all new methods
  - Type hints throughout
  - Example usage in docstrings
  - Explain "why" not just "what"

- [ ] **8.6** Update FUTURE_DEVELOPMENT_PLAN.md
  - Mark Phase 2.1 as complete
  - Update roadmap with lessons learned

**Completion Criteria:**
- ✓ README.md updated
- ✓ Architecture documentation complete
- ✓ Troubleshooting guide created
- ✓ All code has comprehensive docstrings

---

## Completion Protocol

After completing all parent tasks:

1. **Run final test suite:**
   ```bash
   pytest modules/application_automation/tests/ -v --cov=modules/application_automation
   ```

2. **Verify integration:**
   - Test multi-page form end-to-end
   - Test checkpoint recovery
   - Test validation error handling
   - Test backward compatibility (single-page still works)

3. **Update version:**
   - Update VERSION in README.md: 1.0.0 → 1.1.0
   - Update CLAUDE.md project version

4. **Run database schema automation:**
   ```bash
   python database_tools/update_schema.py
   ```

5. **Commit changes:**
   - Use git-orchestrator agent for commit
   - Pattern: `checkpoint_check:Multi-page Navigation Complete`

---

## Task Execution Order (Optimized)

**Parallel Track A (Database):**
1. Task 1: Database Schema & Models

**Parallel Track B (Core Components):**
1. Task 2: Page Navigation System
2. Task 4: Validation Error Handling
3. Task 3: Form State Management (after Task 1)

**Sequential Track C (Integration):**
1. Task 6: Enhanced Form Mappings (can start early)
2. Task 5: Form Filler Integration (after Track B complete)
3. Task 7: Testing (after Task 5)
4. Task 8: Documentation (after Task 7)

**Total Estimated Time:** 38-47 hours (~1.5-2 weeks at 6-8 hours/day)

---

## Risk Mitigation

- **Risk:** Indeed changes page structure mid-development
  - **Mitigation:** Test frequently with real forms, keep selectors flexible

- **Risk:** Checkpoint data grows too large
  - **Mitigation:** Monitor checkpoint size, compress if >10KB

- **Risk:** Navigation button not found
  - **Mitigation:** Multiple selector strategies, fallback to single-page flow

---

## Status Legend
- `[ ]` Not started
- `[~]` In progress
- `[x]` Complete
- `[!]` Blocked
