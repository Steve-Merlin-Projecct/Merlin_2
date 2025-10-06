# Tasks: Copywriting Evaluator System Implementation

Based on Product Requirements Document: `prd-copywriting-evaluator.md`

## Current Status Assessment

✅ **Database Schema: COMPLETE** - All required schema changes have been applied:
- Both sentence bank tables have multi-stage tracking columns (17 new columns each)
- New support tables exist: keyword_filters, canadian_spellings, performance_metrics
- Column renames completed (stage → status)

🔧 **Next Phase: Core Implementation** - Need to build processing modules and dashboard integration

## Relevant Files

- `modules/content/copywriting_evaluator/pipeline_processor.py` - Main pipeline orchestrator handling five-stage processing workflow
- `modules/content/copywriting_evaluator/keyword_filter.py` - Stage 1: Keyword filtering against brand alignment database  
- `modules/content/copywriting_evaluator/truthfulness_evaluator.py` - Stage 2: Gemini AI truthfulness validation (5 sentences per batch)
- `modules/content/copywriting_evaluator/canadian_spelling_processor.py` - Stage 3: Canadian Press spelling corrections (183 conversion pairs)
- `modules/content/copywriting_evaluator/tone_analyzer.py` - Stage 4: Tone analysis and strength classification via Gemini API
- `modules/content/copywriting_evaluator/skill_analyzer.py` - Stage 5: Primary skill assignment via Gemini API
- `modules/content/copywriting_evaluator/performance_tracker.py` - API performance metrics and error tracking
- `modules/content/copywriting_evaluator/copywriting_evaluator_api.py` - Flask blueprint with API endpoints for dashboard integration
- `modules/content/document_generation/template_engine.py` - Template engine with publication italics and Canadian spelling integration
- `modules/content/content_manager.py` - Content selection algorithm with variable repetition prevention
- `frontend_templates/copywriting_evaluator_dashboard.html` - Dashboard UI for processing results and statistics
- `app_modular.py` - Main Flask application with copywriting evaluator routes registered
- `tests/test_copywriting_evaluator.py` - Comprehensive test suite for all pipeline stages
- `tests/test_variable_features.py` - Test suite for variable validation, repetition prevention, and substitution

### Notes

- Follow existing Flask application patterns and integrate with current dashboard design
- Reuse existing Gemini API client, database connections, and CSV processing utilities
- Database changes are complete - focus on business logic implementation and variable feature integration
- All processing stages must support restart capability and independent status tracking
- Variable feature requires two separate systems: `{job_title}` variables and existing `<<template>>` variables
- Content selection algorithm modified to prevent variable repetition in cover letters
- Pipeline processing must validate and reject sentences with unsupported variables (anything other than `{job_title}` and `{company_name}`)

## Tasks

- [x] 1.0 Verify Database Schema and Load Initial Data
  - [x] 1.1 Verify all schema changes are applied and test multi-stage tracking columns
  - [x] 1.2 Load 183 Canadian spelling conversions from attached_assets/Canadian-spellings.csv
  - [x] 1.3 Load initial keyword filters ('meticulous', 'meticulously') into database
- [x] 2.0 Core Pipeline Processing System Architecture
  - [x] 2.1 Create main pipeline orchestrator (modules/content/copywriting_evaluator/pipeline_processor.py)
  - [x] 2.2 Implement CSV file detection and database ingestion system
  - [x] 2.3 Build testing vs production mode switching with immediate vs scheduled processing
  - [x] 2.4 Create comprehensive error handling with 15-error limit and 23-hour cooldown
- [x] 3.0 Stage Processing Implementation  
  - [x] 3.1 Stage 1: Implement keyword filtering with case-insensitive matching
  - [x] 3.2 Stage 2: Build truthfulness evaluator using Gemini API (5 sentences per batch)
  - [x] 3.3 Stage 3: Create Canadian spelling processor with 183 conversion pairs
  - [x] 3.4 Stage 4: Implement tone analysis with predefined categories (Confident, Warm, etc.)
  - [x] 3.5 Stage 5: Build primary skill assignment system via Gemini API
- [x] 4.0 Dashboard Integration and User Interface
  - [x] 4.1 Create Flask routes for copywriting evaluator endpoints
  - [x] 4.2 Build dashboard template showing processing results and statistics
  - [x] 4.3 Implement performance metrics tracking and display for Gemini API usage
- [x] 5.0 Document Generation Integration
  - [x] 5.1 Add publication italics formatting to TemplateEngine for document generation
  - [x] 5.2 Integrate Canadian spelling corrections into template processing workflow
- [x] 6.0 Variable Feature Implementation and Integration
  - [x] 6.1 Implement variable repetition prevention in content selection algorithm
  - [x] 6.2 Add variable validation to pipeline processing (reject unsupported variables)
  - [x] 6.3 Integrate {job_title} and {company_name} substitution into TemplateEngine
  - [x] 6.4 Update content selection to handle variable sentences properly
- [x] 7.0 Testing and Production Readiness
  - [x] 7.1 Create comprehensive test suite for all pipeline stages and error scenarios
  - [x] 7.2 Add variable feature test cases (repetition prevention, validation, substitution)
  - [x] 7.3 Set up twice-weekly scheduled processing for production mode
  - [x] 7.4 Integration testing with existing Flask dashboard and document generation system