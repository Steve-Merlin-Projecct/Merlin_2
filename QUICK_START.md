# Quick Start Guide
## Multi-Page Indeed Application Automation

**Last Updated:** 2025-10-19

---

## TL;DR - Get Started in 5 Minutes

```bash
# 1. Run database migration
psql -U postgres -d local_Merlin_3 -f modules/application_automation/migrations/002_add_multipage_support.sql

# 2. Test the integration
cd modules/application_automation
python test_indeed_integration.py

# 3. Use in your code
from custom_document_handler import CustomDocumentHandler
from dynamic_question_analyzer import DynamicQuestionAnalyzer

# Apply to a job
handler = CustomDocumentHandler()
result = await handler.upload_custom_resume(page, custom_resume_path, default_resume_path)
```

---

## What Was Built

### 1. Multi-Page Form Navigation
Navigate through multi-page Indeed applications (up to 4 pages):
- Page 1: Job listing
- Page 2: Resume selection
- Page 3: Screening questions
- Page 4: Review and submit

### 2. Custom Document Upload (Bot Detection Safe)
Upload custom resume/cover letter WITHOUT triggering bot detection:
```python
# ✅ CORRECT
async with page.expect_file_chooser() as fc_info:
    await button.click()
file_chooser = await fc_info.value
await file_chooser.set_files(custom_resume_path)

# ❌ WRONG (triggers bot detection)
await page.evaluate("el.style.display = 'block'", hidden_input)
```

### 3. Dynamic Screening Questions
Answer employer-specific questions automatically:
- Experience dropdowns
- Yes/No radio buttons
- Text area responses
- File uploads
- Date/time inputs

---

## File Locations

```
modules/application_automation/
├── migrations/
│   └── 002_add_multipage_support.sql      # Database schema
├── page_navigator.py                      # Page detection
├── form_state_manager.py                  # Checkpoints
├── validation_handler.py                  # Error handling
├── custom_document_handler.py             # File uploads
├── screening_questions_handler.py         # Question detection
├── dynamic_question_analyzer.py           # Answer generation
├── test_indeed_integration.py             # Integration test
└── form_mappings/
    └── indeed.json                        # Updated selectors
```

---

## Real Selectors (From Test Data)

### Page 1 - Job Listing
```python
apply_button = "#indeedApplyButton > div"
```

### Page 2 - Resume Selection
```python
resume_options = "button[data-testid='ResumeOptionsMenu']"
upload_different = "button[data-testid='ResumeOptionsMenu-upload']"
# DON'T make hidden input visible - bot detection!
```

### Page 3 - Screening Questions
```python
cover_letter = "button[data-testid*='upload-button']"
experience = "select[name^='q_']"
yes_no = "input[type='radio'][id^='single-select-question']"
text_area = "textarea[id^='rich-text-question-input']"
continue_btn = "#mosaic-provider-module-apply-questions button"
```

---

## Usage Examples

### Example 1: Upload Custom Resume
```python
from custom_document_handler import CustomDocumentHandler

handler = CustomDocumentHandler(max_retries=3)

result = await handler.upload_custom_resume(
    page=page,
    custom_resume_path="/tmp/custom_resume_job123.pdf",
    default_resume_path="/templates/default_resume.pdf",
    job_id="job_123"
)

if result.success:
    print(f"Uploaded: {result.document_used}")
    print(f"Custom: {result.is_custom}")
else:
    print(f"Failed: {result.error_message}")
```

### Example 2: Answer Screening Questions
```python
from screening_questions_handler import ScreeningQuestionsHandler
from dynamic_question_analyzer import DynamicQuestionAnalyzer

# Setup
applicant_profile = {
    "experience_years": 5,
    "work_authorization": True,
    "willing_to_relocate": True
}

handler = ScreeningQuestionsHandler(applicant_profile)
analyzer = DynamicQuestionAnalyzer(applicant_profile=applicant_profile)

# Detect questions
questions = await handler.detect_questions(page)

# Answer each question
for question in questions:
    analysis = analyzer.analyze_question(
        question.question_text,
        question.question_type.value,
        question.options
    )

    print(f"Q: {question.question_text}")
    print(f"A: {analysis.suggested_answer}")
    print(f"Reasoning: {analysis.reasoning}")
```

### Example 3: Navigate Multi-Page Form
```python
from page_navigator import PageNavigator

navigator = PageNavigator()

# Detect current page
page_info = await navigator.detect_current_page(page)
print(f"On page {page_info['current_page']} of {page_info['total_pages']}")

# Navigate to next page
success = await navigator.navigate_to_next(page)

# Check if final page
if await navigator.is_final_page(page):
    print("Ready to submit!")
```

### Example 4: Complete Application Flow
```python
from test_indeed_integration import IndeedApplicationFlow

flow = IndeedApplicationFlow()

await flow.apply_to_job(
    page=page,
    job_url="https://www.indeed.com/viewjob?jk=123",
    custom_resume_path="/tmp/resume.pdf",
    custom_cover_letter_path="/tmp/cover.pdf"
)
```

---

## Critical Insights

### 1. Bot Detection Avoidance
**DO NOT** make hidden file inputs visible. This creates abnormal UI elements that trigger bot detection.

**Instead:** Use Playwright's `expect_file_chooser` API to intercept file dialogs.

### 2. React Dynamic IDs
Indeed uses React IDs with colons (`:r4:`, `:r7:`, `:rc:`). These change on page reload.

**Solution:** Prefer `data-testid` attributes:
```python
# ✅ Stable
button = "button[data-testid='ResumeOptionsMenu']"

# ❌ Unstable
button = "#:r3:"
```

### 3. Question Variability
Screening questions are hand-written by employers. No two jobs have the same questions.

**Solution:** Use dynamic analysis instead of pre-mapping.

---

## Next Steps

1. **Run Database Migration**
   ```bash
   psql -U postgres -d local_Merlin_3 -f modules/application_automation/migrations/002_add_multipage_support.sql
   ```

2. **Test with Real Jobs**
   - Find 3-5 Indeed jobs
   - Run integration test
   - Verify no bot detection
   - Check answer quality

3. **Separate Apify Actor**
   - Create Actor structure
   - Move components
   - Add input schema
   - Test on Apify platform

---

## Troubleshooting

### Issue: File upload triggers bot detection
**Symptom:** Application gets rejected or captcha appears
**Solution:** Verify you're using `expect_file_chooser`, not making inputs visible

### Issue: Questions not detected
**Symptom:** Screening questions remain unanswered
**Solution:** Check for new question types, update `ScreeningQuestionsHandler`

### Issue: Navigation stuck
**Symptom:** Can't find Continue/Next button
**Solution:** Check `page.url` for navigation, update selectors in `indeed.json`

### Issue: Dynamic IDs not found
**Symptom:** Selectors fail on React elements
**Solution:** Use `data-testid` attributes or pattern matching (`[id^='prefix']`)

---

## Testing Checklist

Before merging to develop:
- [ ] Database migration runs successfully
- [ ] Can upload custom resume without bot detection
- [ ] Can answer all question types (text, select, radio, file)
- [ ] Navigation works across all page counts (1-4 pages)
- [ ] Checkpoint system saves and resumes state
- [ ] No unhandled exceptions in logs

---

## Resources

**Full Documentation:** See `WORKTREE_HANDOFF.md`
**Test Data:** `test-data/session1/`
**Architecture:** `docs/architecture/system-overview.md`

---

**Questions?** Review `WORKTREE_HANDOFF.md` section "Questions for Next Developer"