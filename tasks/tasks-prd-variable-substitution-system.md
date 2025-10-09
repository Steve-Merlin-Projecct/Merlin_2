---
title: 'Tasks: Variable Substitution System for Application Packages'
created: '2025-10-06'
updated: '2025-10-06'
author: Steve-Merlin-Projecct
type: prd
status: active
tags:
- tasks
- variable
- substitution
- system
---

# Tasks: Variable Substitution System for Application Packages

Based on Product Requirements Document: `prd-variable-substitution-system.md`

## Relevant Files

- `modules/content/document_generation/template_engine.py` - Enhanced to integrate URL tracking for candidate variables
- `modules/content/document_generation/experience_processor.py` - NEW: Chronological work experience ordering system
- `modules/content/document_generation/csv_content_mapper.py` - Updated to use dynamic work experience ordering
- `modules/link_tracking/secure_link_tracker.py` - Integration point for trackable URL generation
- `modules/database/migrations/add_candidate_info_tables.sql` - NEW: Database schema for candidate information
- `modules/database/migrations/enhance_jobs_table.sql` - NEW: Add hiring organization fields to jobs table
- `modules/user_management/candidate_profile_manager.py` - NEW: Manages candidate personal information and work experiences
- `tests/test_experience_processor.py` - Unit tests for chronological ordering and date parsing
- `tests/test_template_url_integration.py` - Integration tests for tracking URL generation
- `tests/test_variable_substitution_scenarios.py` - End-to-end tests for all four scenarios

### Notes

- Scenario 3 (Dynamic Company/Job Variable Placement) is already fully implemented and working
- The system builds on existing infrastructure: TemplateEngine, LinkTracker, and ContentManager
- Focus on enhancing existing components rather than rebuilding from scratch
- Database migrations should be backward compatible

## Tasks

- [ ] 1.0 Database Schema and Candidate Information Infrastructure
  - [x] 1.1 Review existing user tables (`user_job_preferences`, `user_preferred_industries`, `user_preference_packages`) to understand current candidate data structure
  - [x] 1.2 Create migration to add missing candidate personal information fields to existing tables:
    - [x] 1.2.1 Add `first_name`, `last_name`, `email`, `phone`, `mailing_address` columns to `user_candidate_info` table (COMPLETED - table created in Phase 2)
    - [x] 1.2.2 Add `linkedin_url`, `portfolio_url`, `calendly_url` columns for original (non-tracked) URLs (COMPLETED - table created in Phase 2)
  - [ ] 1.3 Create `work_experiences` table with comprehensive structure:
    - [x] 1.3.1 Define schema: `id`, `user_id`, `company_name`, `job_title`, `start_date`, `end_date`, `is_current`, `location`, `description`, `display_order`, `created_at`, `updated_at`
    - [x] 1.3.2 Add foreign key constraints and indexes for performance
    - [x] 1.3.3 Create trigger to auto-update `display_order` based on chronological sorting

- [ ] 3.0 Hiring Organization Variable Enhancement (Scenario 2)
  - [ ] 3.1 Find hiring organization information from existing tables and scripts. Add next steps in 3.1.1 onwards

  - [ ] 3.2 Implement fallback logic for missing hiring organization data:
    - [ ] 3.2.1 Create default values: "Hiring Manager" for missing names, "Dear Hiring Team" for greetings
    - [ ] 3.2.2 Handle missing company address by using company name only
    - [ ] 3.2.3 Make job reference number optional in templates
  - [ ] 3.3 Update TemplateEngine variable substitution:
    - [ ] 3.3.1 Add hiring organization variables to existing substitution logic
    - [ ] 3.3.2 Implement conditional logic for optional fields (show only if available)
    - [ ] 3.3.3 Add proper formatting for company addresses in template output
  - [ ] 3.4 Enhance ContentManager for hiring organization context:
    - [ ] 3.4.1 Pass hiring manager name to email generation for personalized greetings
    - [ ] 3.4.2 Update job data retrieval to include new hiring organization fields
    - [ ] 3.4.3 Ensure company name consistency across all document types

- [ ] 4.0 Chronological Work Experience Ordering System (Scenario 4)
  - [ ] 4.1 Create ExperienceProcessor module:
    - [ ] 4.1.1 Design `ExperienceProcessor` class in `modules/content/document_generation/experience_processor.py`
    - [ ] 4.1.2 Implement robust date parsing for multiple formats:
      - [ ] 4.1.2.1 Handle "YYYY-MM" format (2022-01)
      - [ ] 4.1.2.2 Handle "Month YYYY" format (January 2022)
      - [ ] 4.1.2.3 Handle "YYYY" only format
      - [ ] 4.1.2.4 Handle "Present", "Current", "Ongoing" for current positions
      - [ ] 4.1.2.5 Handle "MM/YYYY" format
      - [ ] 4.1.2.6 Add error handling for unparseable dates
    - [ ] 4.1.3 Implement chronological sorting algorithm:
      - [ ] 4.1.3.1 Sort by end_date DESC (nulls/present first)
      - [ ] 4.1.3.2 Use start_date as tiebreaker for same end dates
      - [ ] 4.1.3.3 Handle overlapping employment periods
    - [ ] 4.1.4 Create dynamic variable mapping:
      - [ ] 4.1.4.1 Map ordered experiences to `work_experience_N_company_name`, `work_experience_N_job_title`, etc.
      - [ ] 4.1.4.2 Support unlimited number of work experiences (not just 2)
      - [ ] 4.1.4.3 Format date ranges consistently (e.g., "2020 - Present", "2018 - 2020")
  - [ ] 4.2 Integrate ExperienceProcessor with CSVContentMapper:
    - [ ] 4.2.1 Replace hardcoded work experience resolution in `_resolve_work_experience_variable()`
    - [ ] 4.2.2 Call ExperienceProcessor to get dynamically ordered experiences
    - [ ] 4.2.3 Remove hardcoded "Odvod Media" and "Rona" mappings
    - [ ] 4.2.4 Ensure backward compatibility during transition period
  - [ ] 4.3 Update ContentManager for experience context:
    - [ ] 4.3.1 Pass most recent company name to content selection algorithm
    - [ ] 4.3.2 Prioritize resume sentences related to current/most recent employer
    - [ ] 4.3.3 Ensure skills and achievements align with work experience order
  - [ ] 4.4 Add data migration for existing work experience data:
    - [ ] 4.4.1 Create script to migrate hardcoded experiences to new `work_experiences` table
    - [ ] 4.4.2 Set appropriate start/end dates for existing Steve Glen experience data
    - [ ] 4.4.3 Verify data integrity after migration

- [ ] 5.0 Integration Testing and Production Deployment
  - [ ] 5.1 Create comprehensive simple tests. Add 4 simples tests to this task list in 5.1.1