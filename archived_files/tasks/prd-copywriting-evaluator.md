# Product Requirements Document: Copywriting Evaluator System

## Introduction/Overview

The Copywriting Evaluator System is a standalone feature designed to process and validate sentences in the job application system's sentence banks through a comprehensive multi-stage pipeline. This system operates independently from the main job scraping and application generation workflow, serving as a setup and maintenance tool to ensure content integrity, brand alignment, and factual accuracy.

The system implements a five-stage processing pipeline: (1) keyword filtering to remove sentences that don't align with personal brand, (2) truthfulness validation against candidate facts using Google Gemini AI, (3) style guide processing for Canadian Press spelling and publication formatting, (4) tone analysis and classification, and (5) primary skill assignment. Each stage is tracked independently, allowing for efficient processing, restart capability, and granular status monitoring.

## Goals

1. **Filter Brand-Aligned Content**: Remove sentences containing keywords that don't align with personal brand before expensive LLM processing
2. **Validate Sentence Truthfulness**: Evaluate filtered sentences against candidate facts to ensure factual accuracy
3. **Classify Content Characteristics**: Analyze tone, tone strength, and primary skill associations for approved sentences
4. **Automate Quality Assurance**: Reduce manual review overhead through multi-stage automated processing
5. **Track Processing Pipeline**: Monitor each stage independently with restart capability and comprehensive status tracking
6. **Support Development Cycles**: Provide both testing and production operational modes

## User Stories

- **As a system administrator**, I want to upload CSV files with sentence data so that new content can be batch-processed through the multi-stage pipeline
- **As a system administrator**, I want to manage keyword filters so that sentences not aligned with my personal brand are automatically rejected
- **As a system administrator**, I want to manually input candidate facts so that sentences can be evaluated against accurate, specific information
- **As a system administrator**, I want to view processing results through a dashboard so that I can track pipeline progress and review performance metrics
- **As a system administrator**, I want the system to restart processing from any stage so that failed or incomplete batches can be efficiently resumed
- **As a developer**, I want immediate processing during testing so that I can quickly validate system functionality across all pipeline stages
- **As a system administrator**, I want performance metrics tracked so that I can optimize API usage and batch processing efficiency

## Functional Requirements

### Core Processing Requirements
1. **The system must automatically detect and process CSV files placed in a designated directory**
2. **The system must parse CSV data and store it in the existing PostgreSQL sentence bank tables**
3. **The system must implement a five-stage processing pipeline with independent status tracking:**
   - Stage 1: Keyword filtering (case-insensitive matching against filter database)
   - Stage 2: Truthfulness evaluation via Gemini API (5 sentences per batch)
   - Stage 3: Canadian spelling corrections (134 American-to-Canadian conversion pairs)
   - Stage 4: Tone analysis and strength classification via Gemini API
   - Stage 5: Primary skill assignment via Gemini API
4. **The system must filter sentences after database storage but before LLM batch processing**
5. **The system must skip LLM processing entirely for sentences that fail keyword filtering**
6. **The system must support both immediate processing (testing mode) and scheduled processing (production mode)**
7. **The system must allow processing restart from any stage based on current sentence status**

### Database Requirements

#### Sentence Bank Tables (both `sentence_bank_cover_letter` and `sentence_bank_resume`)
8. **The system must rename the `stage` column to `status` in both sentence bank tables**
9. **The system must add a `variable` column (boolean, default false) to `sentence_bank_cover_letter` only**
10. **The system must add these multi-stage processing columns to both tables:**
    - `keyword_filter_status` (varchar, default "pending"): "pending", "testing", "error", "preprocessed", "rejected", "approved"
    - `keyword_filter_date` (date)
    - `keyword_filter_error_message` (text)
    - `truthfulness_status` (varchar, default "pending"): "pending", "testing", "error", "preprocessed", "rejected", "approved"
    - `truthfulness_date` (date)
    - `truthfulness_model` (varchar)
    - `truthfulness_error_message` (text)
    - `canadian_spelling_status` (varchar, default "pending"): "pending", "testing", "error", "preprocessed", "rejected", "approved"
    - `canadian_spelling_date` (date)
    - `tone_analysis_status` (varchar, default "pending"): "pending", "testing", "error", "preprocessed", "rejected", "approved"
    - `tone_analysis_date` (date)
    - `tone_analysis_model` (varchar)
    - `tone_analysis_error_message` (text)
    - `skill_analysis_status` (varchar, default "pending"): "pending", "testing", "error", "preprocessed", "rejected", "approved"
    - `skill_analysis_date` (date)
    - `skill_analysis_model` (varchar)
    - `skill_analysis_error_message` (text)

#### New Tables
11. **The system must create a `keyword_filters` table with:**
    - `id` (primary key)
    - `keyword` (varchar, case-insensitive matching)
    - `status` (varchar, default "active")
    - `created_date` (date)
    - Initial data: "meticulous", "meticulously"
    - Additional keywords will be provided as needed (infrequent updates)
12. **The system must create a `canadian_spellings` table with:**
    - `id` (primary key)
    - `american_spelling` (varchar)
    - `canadian_spelling` (varchar)
    - `status` (varchar, default "active")
    - `created_date` (date)
    - Initial data: 134 American-to-Canadian spelling conversions provided
13. **The system must create a performance metrics table to track Gemini API calls including:**
    - Response time
    - Error rates
    - Cost per API call
    - Usage patterns
    - Batch processing metrics
    - Stage-specific performance data

### Error Handling & Resilience
13. **The system must retry failed Gemini API calls exactly once**
14. **The system must stop processing after 15 consecutive errors during normal operations and wait 23 hours**
15. **The system must continue processing despite errors during testing mode (no 15-error limit)**
16. **The system must log all errors and mark failed sentences with "error" status for each relevant stage**
17. **The system must store detailed error messages in stage-specific error_message columns for debugging**
18. **The system must continue processing remaining sentences when individual calls fail**
19. **The system must track error details and processing stage where failures occurred**

### User Interface Requirements
19. **The system must integrate with the existing website dashboard at the current Flask application URL**
20. **The system must provide a dashboard showing multi-stage processing results and statistics**
21. **The system must display performance metrics and API usage data by processing stage**
22. **The system must show processing status and progress for each pipeline stage**
23. **The system must NOT display filtered sentences (keyword-rejected sentences are hidden from UI)**
24. **The system must allow keyword filter management through Agent requests (no direct UI editing)**

### Scheduling & Operational Modes
25. **The system must support immediate processing when files are uploaded (testing mode)**
26. **The system must support scheduled processing twice per week (production mode)**
27. **The system must allow queue-based background processing for regular operations**
28. **The system must provide real-time processing with immediate results during testing**
29. **The system must support selective stage processing (restart from specific pipeline stages)**

### Integration Requirements
30. **The system must reuse existing CSV processing code from the current project**
31. **The system must utilize existing batch processing code from `modules/ai_job_description_analysis/batch_analyzer.py`**
32. **The system must integrate with existing database schema and connection handling**
33. **The system must use the established Google Gemini API integration patterns**
34. **The system must implement keyword filtering using case-insensitive text matching**
35. **The system must support Administrator requests for keyword filter modifications through Agent interface**
36. **The system must implement Canadian Press spelling corrections as Stage 3 processing using 134 provided conversion pairs**
37. **The system must apply publication name italics formatting during document generation (not database storage)**
38. **The system must process these publication names for italics formatting:**
    - "Edify", "Together We Thrive", "Legacy in Action"
    - "Edify Unfiltered", "CroneCast", "The Well Endowed Podcast"
39. **The system must implement style guide processing in `modules/content/document_generation/template_engine.py`**

### Variable Feature Requirements
40. **The system must support only two curly bracket variables: `{job_title}` and `{company_name}`**
41. **The system must reject sentences with unsupported variables during pipeline processing**
42. **The system must prevent duplicate variable usage: maximum 1 sentence containing `{job_title}` and maximum 1 sentence containing `{company_name}` per cover letter**
43. **The system must allow one sentence to contain both supported variables**
44. **The system must modify `_select_cover_letter_content` method to track variable usage**
45. **The system must maintain existing skill and keyword matching algorithm priority (70% skill, 30% keyword)**
46. **The system must integrate `{job_title}` and `{company_name}` substitution into TemplateEngine during document generation**
47. **The system must maintain original job data capitalization during variable substitution**
48. **The system must keep curly bracket variables `{variable}` separate from template variables `<<variable>>`**

## Non-Goals (Out of Scope)

- **Manual sentence quality scoring** (focus is on brand filtering, truthfulness, tone, and skill classification)
- **Integration with the main job application workflow** (this system operates independently)
- **Real-time processing during normal operations** (scheduled processing is sufficient)
- **Manual sentence creation or editing interface** (CSV upload only)
- **User authentication beyond existing admin access** (leverages current system security)
- **Direct UI editing of keyword filters** (managed through Agent requests only)
- **Display of filtered/rejected sentences in dashboard** (hidden from user interface)
- **Processing priority queues or sentence prioritization** (all sentences processed in upload order)
- **Accuracy tracking over time** (performance metrics focus on API usage and processing efficiency)

## Design Considerations

### UI/UX Requirements
- Integrate seamlessly with existing Flask dashboard design
- Use consistent styling and navigation patterns from current application
- Provide clear status indicators for processing states
- Display results in tabular format with filtering and sorting capabilities

### Data Flow
**Multi-Stage Processing Pipeline:**
- CSV files → Directory monitoring → Database ingestion → **Stage 1:** Keyword filtering → **Stage 2:** Truthfulness evaluation → **Stage 3:** Style guide processing → **Stage 4:** Tone analysis → **Stage 5:** Skill assignment
- Administrator fact input → Structured fact storage → Evaluation context for LLM calls
- Canadian Press spelling corrections and publication name identification → Applied during document generation
- Filtered sentences (keyword rejected) → Hidden from further processing and UI display

## Technical Considerations

### Dependencies
- Reuse existing Google Gemini API client and authentication
- Leverage current PostgreSQL database connection and ORM patterns
- Utilize existing CSV processing utilities
- Integrate with current batch processing error handling framework

### API Integration
- Use established Gemini prompt engineering patterns
- Implement structured JSON response parsing
- Follow existing rate limiting and cost management practices

### Database Schema Changes
- Implement database migrations for new columns using existing migration patterns
- Evaluate removal of `document_sentences` table if made redundant
- Ensure backward compatibility with existing sentence bank queries

## Success Metrics

### Functional Success
- **100% of uploaded sentences processed successfully** (excluding API errors)
- **Less than 2% API error rate** during normal operations
- **Processing completion within 24 hours** for typical batch sizes
- **Zero data loss** during CSV ingestion and processing

### Performance Targets
- **Average API response time under 3 seconds** per batch
- **Successful processing of batches up to 500 sentences**
- **System uptime of 99%** during scheduled processing windows
- **Error recovery within 1 processing cycle** after system issues

### Operational Success
- **Reduction in manual sentence review time by 80%**
- **Automated processing reliability of 95%** during scheduled runs
- **Complete integration with existing dashboard** within development timeline

## Open Questions

1. **Should the system automatically mark sentences as "rejected" if they fail truthfulness evaluation, or flag them for manual review?**
Answer: mark as "rejected"
2. **What is the preferred format and structure for the candidate facts document that administrators will create?**
Amswer: For now, this section will be copied directly into the prompt text.
3. **Should there be a notification system to alert administrators when processing completes or encounters significant errors?**
Answer: No.
5. **Do we need version control or audit trails for changes made to sentence processing status across pipeline stages?**
Answer: No.
6. **Should the performance metrics dashboard include cost tracking and budget alerts for Gemini API usage?**
Answer: No.
7. **Is there a preferred backup/rollback mechanism if batch processing results need to be reverted?**
Answer: No.
8. **What specific tone categories and primary skills should the LLM analysis stages classify sentences into?**
Answer: Tone categories are given and are not to be derived from. Use only case-insensitive "Confident", "Warm", "Storytelling", "Curious", "Analytical", "Insightful", "Bold", "Rebellious", "Quirky". A file will be uploaded that defines these words, with examples.
Primary Skill analysis is intentionally left open for interpretation.
9. **Should there be minimum confidence thresholds for LLM classifications before marking sentences as "approved"?**
Answer: allow the LLM to return boolean without "overthinking"
---

**Target Implementation Timeline**: Based on reusing existing components, estimated 2-3 weeks for core functionality plus 1 week for dashboard integration and testing.

**Dependencies**: Google Gemini API access, existing database schema understanding, administrator training for fact document creation.


*Suggestions & Observations*
**Column Naming & Organization**

Complete Column Set per Sentence Table:
Keyword Filter: status, date, error_message
Truthfulness: status, date, model, error_message
Tone Analysis: status, date, model, error_message
Skill Analysis: status, date, model, error_message

## Clarifying Questions: Variable Feature & Sentence Selection Compatibility

### Variable Feature Implementation Questions

1. **What is the purpose of the `variable` column in `sentence_bank_cover_letter`?**
   - Is this for sentences that contain template variables (like curly brackets `{job_title}`, `{company_name}`)?
      - Answer = Yes
   - Are these sentences meant to be dynamically populated with job-specific information?
      - Answer = Yes
   - Should variable sentences be treated differently during pipeline processing?
      -  Answer = Unsure

2. **How do curly brackets affect sentence selection and processing?**
   - Do sentences with curly brackets (e.g., `{variable_name}`) cause issues in the current sentence selection algorithm?
      - I'm asking you to evaluate the python scripts and the interationw with the database
   - Should the pipeline stages (keyword filtering, truthfulness, tone analysis, skill assignment) process the literal text with curly brackets, or should variables be substituted first?
      -  Answer = No, let's leave it as it is.
   - Do curly brackets interfere with the relevance scoring in `_calculate_relevance_score`?
      -  Answer = I don't know.

3. **How should the sentence selection algorithm prioritize variable sentences?**
   - Should variable sentences be preferred over static sentences when both are available for the same purpose?
      -  Answer = No
   - Should there be separate scoring logic for variable vs. non-variable sentences?
      -  Answer = Yes, I don't want to have multiple instances of variable text in the final output. Implement a rule that a `{job_title}`, `{company_name}` appear only once each in the final output for the entire document (cover letter).
   - Do variable sentences need special handling in the content selection process?
      - Answer, besides the no repition rule, I'm not sure. I want to fully understand how the content selection algorithm works, why the algorithm was implemented in that way, and the future development path for the algorithm before consulting and providing advice.

### Sentence Selection Algorithm Adaptation Questions

4. **Should variable sentences be filtered differently during keyword filtering (Stage 1)?**
      answer = no
   - Should keyword matching ignore text within curly brackets `{}`?
      ansswer = no
   - Should keywords be matched against the variable names themselves?
       answer = no
   - Should variable sentences bypass certain keyword filters?
      - answer = no

5. **How should truthfulness evaluation (Stage 2) handle variable sentences?**
   - Should Gemini API evaluate sentences with variables as-is, or with placeholder values?
      answer = use as-is, don't use placeholders
   - Are variable sentences inherently considered "truthful" since they'll be populated with real data?
      answer = NO
   - Should variable sentences skip truthfulness evaluation entirely?
      answer = NO

6. **How should the content selection prioritize variable vs. static sentences?**
   - In `select_content_for_job`, when both variable and static sentences are available for the same section/purpose, which should be preferred?
      answer = no preference
   - Should variable sentences get a scoring bonus since they're more adaptable?
    answer = no
   - Should there be a minimum threshold of variable sentences required in each document?
      answer = no

7. **Are there specific variable naming conventions or validation requirements?**
   - What variable names are supported (e.g., `{job_title}`, `{company_name}`
   answer  = only `{job_title}`, `{company_name}`
   - Should the system validate that variable names in sentences match available job data fields?
   answer = I'm not sure what this is asking. Default to "no"
   - Should sentences with unsupported variables be flagged or rejected?
   - answer = yes, reject for this instance

8. **How does this affect the document generation integration?**
   - Does the template engine already support curly bracket variables, or does this need integration work?
      answer = this needs integration work
   - Should variable substitution happen during document generation or during sentence selection?
      answer = during document generation
   - Are there formatting considerations for variable content (e.g., capitalization, punctuation)?
      answer = maintain original capitalization from source data

## Implementation Decisions Summary

### **Variable Feature Requirements (FINAL)**

Based on clarification sessions, the variable feature implementation requirements are:

#### **Variable Support:**
- **Supported Variables**: Only `{job_title}` and `{company_name}` 
- **Unsupported Variables**: Any other curly bracket variables (e.g., `{salary}`, `{years_experience}`) must be **rejected** during pipeline processing and marked with status "rejected"
- **Variable Systems**: Two separate variable systems exist:
  - Document Template Variables: `<<variable_name>>` (existing TemplateEngine system)
  - Sentence Content Variables: `{job_title}` and `{company_name}` (new system)

#### **Content Selection Algorithm Integration:**
- **Keyword Matching Impact**: No changes needed - variable content doesn't affect keyword matching (ignore variable text in matching)
- **Repetition Prevention**: Maximum 1 sentence containing `{job_title}` AND maximum 1 sentence containing `{company_name}` in final cover letter output
- **Single Sentence Rule**: One sentence may contain both `{job_title}` and `{company_name}`
- **Implementation Location**: Modify `_select_cover_letter_content` to track variables after category selection
- **Algorithm Priority**: Maintain existing skill matching (70%) + keyword matching (30%) scoring system

#### **Pipeline Processing Rules:**
- **Stage 1 (Keyword Filter)**: Process variable sentences normally, no special filtering
- **Stage 2 (Truthfulness)**: Evaluate variable sentences as-is with curly brackets, no placeholder substitution
- **Stage 3 (Canadian Spelling)**: Apply spelling corrections to text around variables
- **Stage 4 (Tone Analysis)**: Analyze tone with variables present in text
- **Stage 5 (Skill Analysis)**: Assign skills to variable sentences normally
- **Variable Validation**: Reject sentences with unsupported variables during any stage processing

#### **Document Generation Integration:**
- **Substitution Timing**: Variable substitution happens during document generation via TemplateEngine
- **Formatting Rules**: Maintain original capitalization from job data (no automatic formatting changes)
- **Template Integration**: Add `{job_title}` and `{company_name}` support to TemplateEngine.substitute_variables() method
- **Two-System Approach**: Keep existing `<<variable>>` system separate from new `{variable}` system

#### **Content Selection Algorithm Changes Completed:**
- ✅ **Variable Repetition Prevention**: Implemented in `_select_cover_letter_content` method
- ✅ **Constraint Tracking**: Added variable usage tracking system 
- ✅ **Quality Preservation**: Maintains existing composite scoring (skill + keyword matching)
- ✅ **Fallback Logic**: Ensures complete cover letters even with constraint violations
