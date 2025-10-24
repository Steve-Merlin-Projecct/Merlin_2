---
title: "Database Schema"
type: technical_doc
component: database
status: draft
tags: []
---

# Database Schema Documentation
**Automated Job Application System**

*Last Updated: September 12, 2025*  
*Auto-generated from PostgreSQL information_schema*

## Overview

This database supports a comprehensive automated job application system that scrapes job postings, analyzes them with AI, manages user preferences, and tracks applications with sophisticated document generation and tone analysis.

### Architecture Summary
- **Primary Tables**: 46 tables with UUID primary keys
- **Database**: neondb
- **Generated**: 2025-09-12T13:08:24.645397

---

## Table Summary

| Table Name | Purpose | Key Relationships |
|------------|---------|-------------------|
| analyzed_jobs | Database table | company_id → companies, job_id → jobs |
| application_documents | Database table | job_application_id → job_applications |
| application_settings | System configuration and settings | Standalone |
| canadian_spellings | Database table | Standalone |
| cleaned_job_scrape_sources | Database table | cleaned_job_id → cleaned_job_scrapes, job_id → jobs |
| cleaned_job_scrapes | Processed and deduplicated job data | Standalone |
| companies | Company information and metadata | Standalone |
| consistency_validation_logs | Database table | Standalone |
| data_corrections | Database table | Standalone |
| document_jobs | Document generation tracking | Standalone |
| document_sentences | Database table | document_job_id → document_jobs |
| document_template_metadata | Database table | Standalone |
| document_tone_analysis | Document tone analysis results | Standalone |
| error_log | Database table | Standalone |
| failure_logs | Database table | Standalone |
| job_analysis_queue | Database table | job_id → jobs |
| job_application_tracking | Database table | job_application_id → job_applications |
| job_applications | Application tracking and status management | job_id → jobs |
| job_ats_keywords | Database table | Standalone |
| job_benefits | Database table | job_id → jobs |
| job_certifications | Database table | job_id → jobs |
| job_education_requirements | Database table | job_id → jobs |
| job_logs | System audit trail and debugging | Standalone |
| job_platforms_found | Database table | job_id → jobs |
| job_red_flags_details | Database table | job_id → jobs |
| job_required_documents | Database table | job_id → jobs |
| job_required_skills | Database table | job_id → jobs |
| job_skills | Database table | Standalone |
| job_stress_indicators | Database table | job_id → jobs |
| jobs | Primary entity for job postings | company_id → companies |
| keyword_filters | Database table | Standalone |
| link_clicks | Database table | tracking_id → link_tracking |
| link_tracking | Hyperlink click tracking | job_id → jobs, application_id → job_applications |
| performance_metrics | Database table | Standalone |
| pre_analyzed_jobs | Database table | cleaned_scrape_id → cleaned_job_scrapes, company_id → companies |
| raw_job_scrapes | Raw scraped data before processing | Standalone |
| recovery_statistics | Database table | Standalone |
| security_test_table | Database table | Standalone |
| sentence_bank_cover_letter | Cover letter content sentence bank | Standalone |
| sentence_bank_resume | Resume content sentence bank | experience_id → job_applications |
| user_candidate_info | Database table | Standalone |
| user_job_preferences | User criteria and preference packages | candidate_id → user_candidate_info |
| user_preference_packages | Database table | user_id → user_candidate_info |
| user_preferred_industries | Database table | user_id → user_candidate_info |
| work_experiences | Database table | user_id → user_candidate_info |
| workflow_checkpoints | Database table | Standalone |

---

## Detailed Table Specifications

### analyzed_jobs
**Database table**

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | uuid | NOT NULL, DEFAULT gen_random_uuid(), PK | Unique identifier |
| pre_analyzed_job_id | uuid |  |  |
| company_id | uuid | FK → companies(id) | Associated company reference |
| job_title | character varying | NOT NULL |  |
| job_description | text |  |  |
| job_number | character varying |  |  |
| salary_low | integer(32) |  |  |
| salary_high | integer(32) |  |  |
| salary_period | character varying |  |  |
| compensation_currency | character varying | DEFAULT 'CAD' |  |
| equity_stock_options | boolean |  |  |
| commission_or_performance_incentive | text |  |  |
| est_total_compensation | text |  |  |
| remote_options | character varying |  |  |
| job_type | character varying |  |  |
| in_office_requirements | character varying |  |  |
| office_address | text |  |  |
| office_city | character varying |  |  |
| office_province | character varying |  |  |
| office_country | character varying |  |  |
| working_hours_per_week | integer(32) |  |  |
| work_schedule | text |  |  |
| specific_schedule | text |  |  |
| travel_requirements | text |  |  |
| is_supervisor | boolean | DEFAULT false |  |
| department | character varying |  |  |
| industry | character varying |  |  |
| sub_industry | character varying |  |  |
| job_function | character varying |  |  |
| seniority_level | character varying |  |  |
| supervision_count | integer(32) | DEFAULT 0 |  |
| budget_size_category | character varying |  |  |
| company_size_category | character varying |  |  |
| application_deadline | date |  |  |
| application_email | character varying |  |  |
| application_method | character varying |  |  |
| special_instructions | text |  |  |
| primary_source_url | character varying |  |  |
| posted_date | date |  |  |
| ai_analysis_completed | boolean | DEFAULT false |  |
| primary_industry | character varying |  |  |
| authenticity_score | numeric(3,2) |  |  |
| deduplication_key | character varying | UNIQUE |  |
| application_status | character varying | DEFAULT 'not_applied' |  |
| last_application_attempt | timestamp without time zone |  |  |
| eligibility_flag | boolean | DEFAULT true |  |
| prestige_factor | integer(32) |  |  |
| prestige_reasoning | text |  |  |
| estimated_stress_level | integer(32) |  |  |
| stress_reasoning | text |  |  |
| analysis_date | timestamp without time zone |  |  |
| gemini_model_used | character varying |  |  |
| analysis_tokens_used | integer(32) |  |  |
| created_at | timestamp without time zone | DEFAULT CURRENT_TIMESTAMP | Record creation timestamp |
| job_id | uuid | FK → jobs(id) | Associated job reference |
| hiring_manager | character varying(100) |  |  |
| reporting_to | character varying(100) |  |  |
| job_title_extracted | character varying(200) |  |  |
| company_name_extracted | character varying(100) |  |  |
| additional_insights | text |  |  |

### application_documents
**Database table**

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| document_id | uuid | NOT NULL, DEFAULT gen_random_uuid(), PK |  |
| job_application_id | uuid | FK → job_applications(id), UNIQUE, UNIQUE, UNIQUE |  |
| document_type | character varying(30) | NOT NULL, UNIQUE, UNIQUE, UNIQUE |  |
| document_name | character varying(255) | NOT NULL, UNIQUE, UNIQUE, UNIQUE |  |
| file_path | text |  |  |
| file_size | integer(32) |  |  |
| sent_timestamp | timestamp without time zone | NOT NULL |  |

### application_settings
**System configuration and settings**

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| setting_key | character varying(100) | NOT NULL, PK |  |
| setting_value | text |  |  |
| setting_type | character varying(20) |  |  |
| description | text |  |  |
| created_at | timestamp without time zone |  | Record creation timestamp |
| updated_at | timestamp without time zone |  | Last modification timestamp |

### canadian_spellings
**Database table**

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | uuid | NOT NULL, DEFAULT gen_random_uuid(), PK | Unique identifier |
| american_spelling | character varying | NOT NULL |  |
| canadian_spelling | character varying | NOT NULL |  |
| status | character varying | DEFAULT 'active' |  |
| created_date | date | DEFAULT CURRENT_DATE |  |

### cleaned_job_scrape_sources
**Database table**

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| source_id | uuid | NOT NULL, DEFAULT gen_random_uuid(), PK |  |
| cleaned_job_id | uuid | FK → cleaned_job_scrapes(cleaned_job_id), UNIQUE, UNIQUE |  |
| original_scrape_id | uuid | NOT NULL, UNIQUE, UNIQUE |  |
| source_priority | integer(32) |  |  |
| merge_timestamp | timestamp without time zone | DEFAULT CURRENT_TIMESTAMP |  |
| processed_to_jobs | boolean | DEFAULT false |  |
| job_id | uuid | FK → jobs(id) | Associated job reference |
| processed_at | timestamp without time zone |  |  |

### cleaned_job_scrapes
**Processed and deduplicated job data**

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| cleaned_job_id | uuid | NOT NULL, DEFAULT gen_random_uuid(), PK |  |
| job_title | character varying(500) |  |  |
| company_name | character varying(300) |  |  |
| location_city | character varying(100) |  |  |
| location_province | character varying(100) |  |  |
| location_country | character varying(100) |  |  |
| work_arrangement | character varying(50) |  |  |
| salary_min | integer(32) |  |  |
| salary_max | integer(32) |  |  |
| salary_currency | character varying(10) |  |  |
| salary_period | character varying(20) |  |  |
| job_description | text |  |  |
| requirements | text |  |  |
| benefits | text |  |  |
| industry | character varying(100) |  |  |
| job_type | character varying(50) |  |  |
| experience_level | character varying(50) |  |  |
| posting_date | date |  |  |
| application_deadline | date |  |  |
| external_job_id | character varying(255) |  |  |
| source_website | character varying(255) | NOT NULL |  |
| application_url | text |  |  |
| is_expired | boolean | DEFAULT false |  |
| cleaned_timestamp | timestamp without time zone | DEFAULT CURRENT_TIMESTAMP |  |
| last_seen_timestamp | timestamp without time zone | DEFAULT CURRENT_TIMESTAMP |  |
| processing_notes | text |  |  |
| location_street_address | text |  |  |
| application_email | text |  |  |
| confidence_score | numeric(3,2) | DEFAULT 0.00 |  |
| duplicates_count | integer(32) | DEFAULT 0 |  |

### companies
**Company information and metadata**

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | uuid | NOT NULL, DEFAULT gen_random_uuid(), PK | Unique identifier |
| name | character varying(255) | NOT NULL |  |
| domain | character varying(255) |  |  |
| industry | character varying(100) |  |  |
| sub_industry | character varying(100) |  |  |
| size_range | character varying(50) |  |  |
| employee_count_min | integer(32) |  |  |
| employee_count_max | integer(32) |  |  |
| headquarters_location | character varying(255) |  |  |
| founded_year | integer(32) |  |  |
| company_type | character varying(50) |  |  |
| company_url | character varying(500) |  |  |
| linkedin_url | character varying(500) |  |  |
| glassdoor_url | character varying(500) |  |  |
| created_at | timestamp without time zone | DEFAULT CURRENT_TIMESTAMP | Record creation timestamp |
| company_description | text |  |  |
| strategic_mission | text |  |  |
| strategic_values | text |  |  |
| recent_news | text |  |  |

### consistency_validation_logs
**Database table**

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | uuid | NOT NULL, DEFAULT gen_random_uuid(), PK | Unique identifier |
| validation_run_id | uuid | NOT NULL |  |
| issue_type | character varying(100) |  |  |
| severity | character varying(20) |  |  |
| description | text |  |  |
| affected_record_count | integer(32) |  |  |
| correctable | boolean |  |  |
| correction_applied | boolean | DEFAULT false |  |
| created_at | timestamp without time zone | DEFAULT now() | Record creation timestamp |

### data_corrections
**Database table**

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | uuid | NOT NULL, DEFAULT gen_random_uuid(), PK | Unique identifier |
| validation_run_id | uuid | NOT NULL |  |
| correction_type | character varying(100) |  |  |
| affected_table | character varying(100) |  |  |
| affected_records | jsonb |  |  |
| correction_sql | text |  |  |
| applied_at | timestamp without time zone | DEFAULT now() |  |
| success | boolean | DEFAULT true |  |

### document_jobs
**Document generation tracking**

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| job_id | uuid | NOT NULL, PK | Associated job reference |
| file_path | character varying(500) |  |  |
| filename | character varying(255) |  |  |
| file_size | integer(32) |  |  |
| title | character varying(255) |  |  |
| author | character varying(255) |  |  |
| document_type | character varying(50) | NOT NULL |  |
| status | character varying(50) |  |  |
| created_at | timestamp without time zone |  | Record creation timestamp |
| completed_at | timestamp without time zone |  |  |
| webhook_data | json |  |  |
| has_error | boolean |  |  |
| error_code | character varying(100) |  |  |
| error_message | text |  |  |
| error_details | json |  |  |
| storage_type | character varying(50) |  |  |
| object_storage_path | character varying(500) |  |  |

### document_sentences
**Database table**

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| sentence_id | uuid | NOT NULL, DEFAULT gen_random_uuid(), PK |  |
| document_job_id | uuid | FK → document_jobs(job_id), UNIQUE, UNIQUE |  |
| sentence_text | text | NOT NULL |  |
| tone_score | numeric(3,2) |  |  |
| sentiment_category | character varying(20) |  |  |
| confidence_score | numeric(3,2) |  |  |
| word_count | integer(32) |  |  |
| sentence_order | integer(32) | UNIQUE, UNIQUE |  |
| created_at | timestamp without time zone | DEFAULT CURRENT_TIMESTAMP | Record creation timestamp |

### document_template_metadata
**Database table**

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| document_type | character varying(20) | NOT NULL |  |
| resume_general_section_count | integer(32) |  |  |
| resume_constituent_section_count | integer(32) |  |  |
| cover_par_one | integer(32) |  |  |
| cover_par_two | integer(32) |  |  |
| cover_par_three | integer(32) |  |  |
| count | integer(32) | DEFAULT 0 |  |
| template_file_path | character varying(255) |  |  |
| id | integer(32) | NOT NULL, DEFAULT nextval('document_template_..., PK | Unique identifier |

### document_tone_analysis
**Document tone analysis results**

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | uuid | NOT NULL, DEFAULT gen_random_uuid(), PK | Unique identifier |
| document_type | character varying(50) | NOT NULL |  |
| sentences | jsonb | NOT NULL |  |
| tone_jump_score | double precision(53) |  |  |
| tone_coherence_score | double precision(53) |  |  |
| total_tone_travel | double precision(53) |  |  |
| average_tone_jump | double precision(53) |  |  |

### error_log
**Database table**

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | integer(32) | NOT NULL, DEFAULT nextval('error_log_id_seq':..., PK | Unique identifier |
| error_id | character varying(36) | NOT NULL, UNIQUE |  |
| timestamp | timestamp without time zone | NOT NULL |  |
| session_id | character varying(36) |  |  |
| stage_name | character varying(50) |  |  |
| error_category | character varying(30) | NOT NULL |  |
| severity | character varying(20) | NOT NULL |  |
| error_message | text | NOT NULL |  |
| error_details | text |  |  |
| exception_type | character varying(100) |  |  |
| stack_trace | text |  |  |
| context_data | jsonb |  |  |
| retry_count | integer(32) | DEFAULT 0 |  |
| resolved | boolean | DEFAULT false |  |
| resolution_notes | text |  |  |
| created_at | timestamp without time zone | DEFAULT CURRENT_TIMESTAMP | Record creation timestamp |

### failure_logs
**Database table**

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | uuid | NOT NULL, DEFAULT gen_random_uuid(), PK | Unique identifier |
| failure_type | character varying(100) | NOT NULL |  |
| operation_name | character varying(200) | NOT NULL |  |
| workflow_id | uuid |  |  |
| error_message | text |  |  |
| error_details | jsonb |  |  |
| recovery_attempts | integer(32) | DEFAULT 0 |  |
| recovery_successful | boolean | DEFAULT false |  |
| created_at | timestamp without time zone | DEFAULT now() | Record creation timestamp |
| resolved_at | timestamp without time zone |  |  |

### job_analysis_queue
**Database table**

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | integer(32) | NOT NULL, DEFAULT nextval('job_analysis_queue..., PK | Unique identifier |
| job_id | uuid | NOT NULL, FK → jobs(id), UNIQUE | Associated job reference |
| priority | character varying(20) | DEFAULT 'normal' |  |
| queued_at | timestamp without time zone | DEFAULT CURRENT_TIMESTAMP |  |
| attempts | integer(32) | DEFAULT 0 |  |
| last_attempt_at | timestamp without time zone |  |  |
| error_message | text |  |  |
| status | character varying(20) | DEFAULT 'pending' |  |
| created_at | timestamp without time zone | DEFAULT CURRENT_TIMESTAMP | Record creation timestamp |

### job_application_tracking
**Database table**

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| tracking_id | uuid | NOT NULL, DEFAULT gen_random_uuid(), PK |  |
| job_application_id | uuid | FK → job_applications(id) |  |
| tracking_type | character varying(50) | NOT NULL |  |
| tracking_event | character varying(100) | NOT NULL |  |
| event_timestamp | timestamp without time zone | NOT NULL |  |
| event_data | jsonb |  |  |
| ip_address | inet |  |  |
| user_agent | text |  |  |

### job_applications
**Application tracking and status management**

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | uuid | NOT NULL, DEFAULT gen_random_uuid(), PK | Unique identifier |
| job_id | uuid | FK → jobs(id) | Associated job reference |
| application_date | timestamp without time zone | DEFAULT CURRENT_TIMESTAMP |  |
| application_method | character varying(50) |  |  |
| application_status | character varying(50) |  |  |
| email_sent_to | character varying(255) |  |  |
| documents_sent | ARRAY |  |  |
| tracking_data | jsonb |  |  |
| first_response_received_at | timestamp without time zone |  |  |
| response_type | character varying(50) |  |  |
| notes | text |  |  |
| tone_jump_score | double precision(53) |  |  |
| tone_coherence_score | double precision(53) |  |  |
| total_tone_travel | double precision(53) |  |  |
| created_at | timestamp without time zone | DEFAULT CURRENT_TIMESTAMP | Record creation timestamp |
| last_response_received_at | timestamp without time zone |  |  |

**Business Rules:**
- Application status: 'submitted', 'pending', 'responded', 'rejected', 'hired'
- Tone scores range 0.0-1.0, lower = more coherent

### job_ats_keywords
**Database table**

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | uuid | NOT NULL, DEFAULT gen_random_uuid(), PK | Unique identifier |
| job_id | uuid | UNIQUE, UNIQUE | Associated job reference |
| keyword | character varying(100) | NOT NULL, UNIQUE, UNIQUE |  |
| keyword_category | character varying(30) |  |  |
| frequency_in_posting | integer(32) | DEFAULT 1 |  |

### job_benefits
**Database table**

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| benefit_id | uuid | NOT NULL, DEFAULT gen_random_uuid(), PK |  |
| job_id | uuid | FK → jobs(id), UNIQUE, UNIQUE | Associated job reference |
| benefit_type | character varying(50) | NOT NULL, UNIQUE, UNIQUE |  |
| benefit_description | text |  |  |
| benefit_value | character varying(100) |  |  |

### job_certifications
**Database table**

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | integer(32) | NOT NULL, DEFAULT nextval('job_certifications..., PK | Unique identifier |
| job_id | uuid | FK → jobs(id) | Associated job reference |
| certification_name | character varying(100) | NOT NULL |  |
| is_required | boolean | DEFAULT true |  |
| created_at | timestamp without time zone | DEFAULT CURRENT_TIMESTAMP | Record creation timestamp |

### job_education_requirements
**Database table**

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | integer(32) | NOT NULL, DEFAULT nextval('job_education_requ..., PK | Unique identifier |
| job_id | uuid | NOT NULL, FK → jobs(id) | Associated job reference |
| degree_level | character varying(100) |  |  |
| field_of_study | character varying(200) |  |  |
| institution_type | character varying(100) |  |  |
| years_required | integer(32) |  |  |
| is_required | boolean | DEFAULT true |  |
| alternative_experience | text |  |  |
| created_at | timestamp without time zone | DEFAULT CURRENT_TIMESTAMP | Record creation timestamp |

### job_logs
**System audit trail and debugging**

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| log_id | uuid | NOT NULL, PK |  |
| job_id | uuid | NOT NULL | Associated job reference |
| timestamp | timestamp without time zone |  |  |
| log_level | character varying(20) |  |  |
| message | text | NOT NULL |  |
| details | json |  |  |

### job_platforms_found
**Database table**

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| platform_id | uuid | NOT NULL, DEFAULT gen_random_uuid(), PK |  |
| job_id | uuid | FK → jobs(id), UNIQUE, UNIQUE | Associated job reference |
| platform_name | character varying(100) | NOT NULL, UNIQUE, UNIQUE |  |
| platform_url | text |  |  |
| first_found_at | timestamp without time zone | DEFAULT CURRENT_TIMESTAMP |  |

### job_red_flags_details
**Database table**

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | integer(32) | NOT NULL, DEFAULT nextval('job_red_flags_deta..., PK | Unique identifier |
| job_id | uuid | FK → jobs(id) | Associated job reference |
| flag_type | character varying(50) | NOT NULL |  |
| detected | boolean | DEFAULT false |  |
| details | text |  |  |
| created_at | timestamp without time zone | DEFAULT CURRENT_TIMESTAMP | Record creation timestamp |

### job_required_documents
**Database table**

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | integer(32) | NOT NULL, DEFAULT nextval('job_required_docum..., PK | Unique identifier |
| job_id | uuid | FK → jobs(id) | Associated job reference |
| document_type | character varying(50) | NOT NULL |  |
| is_required | boolean | DEFAULT true |  |
| created_at | timestamp without time zone | DEFAULT CURRENT_TIMESTAMP | Record creation timestamp |

### job_required_skills
**Database table**

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| skill_id | uuid | NOT NULL, DEFAULT gen_random_uuid(), PK |  |
| job_id | uuid | FK → jobs(id), UNIQUE, UNIQUE | Associated job reference |
| skill_name | character varying(100) | NOT NULL, UNIQUE, UNIQUE |  |
| skill_level | character varying(20) |  |  |
| is_required | boolean | DEFAULT true |  |

### job_skills
**Database table**

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| skill_id | uuid | NOT NULL, DEFAULT gen_random_uuid(), PK |  |
| job_id | uuid | UNIQUE, UNIQUE | Associated job reference |
| skill_name | character varying(100) | NOT NULL, UNIQUE, UNIQUE |  |
| importance_rating | integer(32) |  |  |
| is_required | boolean | DEFAULT false |  |
| reasoning | text |  |  |

### job_stress_indicators
**Database table**

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | integer(32) | NOT NULL, DEFAULT nextval('job_stress_indicat..., PK | Unique identifier |
| job_id | uuid | FK → jobs(id) | Associated job reference |
| indicator | character varying(100) | NOT NULL |  |
| description | text |  |  |
| created_at | timestamp without time zone | DEFAULT CURRENT_TIMESTAMP | Record creation timestamp |

### jobs
**Primary entity for job postings**

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | uuid | NOT NULL, DEFAULT gen_random_uuid(), PK | Unique identifier |
| company_id | uuid | FK → companies(id) | Associated company reference |
| job_title | character varying(255) | NOT NULL | Position title |
| job_description | text |  |  |
| job_number | character varying(100) |  |  |
| salary_low | integer(32) |  | Minimum salary (in cents) |
| salary_high | integer(32) |  | Maximum salary (in cents) |
| salary_period | character varying(20) |  |  |
| remote_options | character varying(50) |  |  |
| job_type | character varying(50) |  |  |
| is_supervisor | boolean | DEFAULT false |  |
| department | character varying(100) |  |  |
| industry | character varying(100) |  |  |
| seniority_level | character varying(50) |  |  |
| application_deadline | date |  |  |
| is_active | boolean | DEFAULT true |  |
| application_status | character varying(50) | DEFAULT 'not_applied' |  |
| last_application_attempt | timestamp without time zone |  |  |
| application_method | character varying(50) |  |  |
| analysis_completed | boolean | DEFAULT false |  |
| consolidation_confidence | double precision(53) |  |  |
| primary_source_url | character varying(500) |  |  |
| posted_date | date |  |  |
| created_at | timestamp without time zone | DEFAULT CURRENT_TIMESTAMP | Record creation timestamp |
| title_matches_role | boolean |  |  |
| mismatch_explanation | text |  |  |
| is_authentic | boolean |  |  |
| authenticity_reasoning | text |  |  |
| sub_industry | character varying(100) |  |  |
| job_function | character varying(100) |  |  |
| in_office_requirements | character varying(50) |  |  |
| office_address | text |  |  |
| office_city | character varying(100) |  |  |
| office_province | character varying(100) |  |  |
| office_country | character varying(100) |  |  |
| working_hours_per_week | integer(32) |  |  |
| work_schedule | text |  |  |
| specific_schedule | text |  |  |
| travel_requirements | text |  |  |
| salary_mentioned | boolean |  |  |
| equity_stock_options | boolean |  |  |
| commission_or_performance_incentive | text |  |  |
| est_total_compensation | text |  |  |
| compensation_currency | character varying(10) | DEFAULT 'CAD' |  |
| application_email | character varying(255) |  |  |
| special_instructions | text |  |  |
| estimated_stress_level | integer(32) |  |  |
| stress_reasoning | text |  |  |
| education_requirements | text |  |  |
| overall_red_flag_reasoning | text |  |  |
| cover_letter_pain_point | text |  |  |
| cover_letter_evidence | text |  |  |
| cover_letter_solution_angle | text |  |  |
| eligibility_flag | boolean | DEFAULT true | Meets user criteria |
| prestige_factor | integer(32) |  |  |
| prestige_reasoning | text |  |  |
| supervision_count | integer(32) | DEFAULT 0 |  |
| budget_size_category | character varying(20) |  |  |
| company_size_category | character varying(20) |  |  |

**Business Rules:**
- Salary amounts stored in cents for precision
- Priority score ranges 0.0-10.0, higher = better match
- Application status: 'not_applied', 'pending', 'submitted', 'responded', 'rejected'

### keyword_filters
**Database table**

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | uuid | NOT NULL, DEFAULT gen_random_uuid(), PK | Unique identifier |
| keyword | character varying | NOT NULL |  |
| status | character varying | DEFAULT 'active' |  |
| created_date | date | DEFAULT CURRENT_DATE |  |

### link_clicks
**Database table**

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| click_id | uuid | NOT NULL, DEFAULT gen_random_uuid(), PK |  |
| tracking_id | character varying(100) | NOT NULL, FK → link_tracking(tracking_id) |  |
| clicked_at | timestamp without time zone | DEFAULT CURRENT_TIMESTAMP |  |
| ip_address | inet |  |  |
| user_agent | text |  |  |
| referrer_url | character varying(1000) |  |  |
| session_id | character varying(100) |  |  |
| click_source | character varying(50) |  |  |
| metadata | jsonb | DEFAULT '{}'::jsonb |  |

### link_tracking
**Hyperlink click tracking**

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| tracking_id | character varying(100) | NOT NULL, PK |  |
| job_id | uuid | FK → jobs(id) | Associated job reference |
| application_id | uuid | FK → job_applications(id) | Associated application reference |
| link_function | character varying(50) | NOT NULL |  |
| link_type | character varying(50) | NOT NULL |  |
| original_url | character varying(1000) | NOT NULL |  |
| redirect_url | character varying(1000) | NOT NULL |  |
| created_at | timestamp without time zone | DEFAULT CURRENT_TIMESTAMP | Record creation timestamp |
| created_by | character varying(100) | DEFAULT 'system' |  |
| is_active | boolean | DEFAULT true |  |
| description | text |  |  |

### performance_metrics
**Database table**

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | uuid | NOT NULL, DEFAULT gen_random_uuid(), PK | Unique identifier |
| stage_name | character varying | NOT NULL |  |
| api_call_type | character varying | NOT NULL |  |
| response_time_ms | integer(32) |  |  |
| success | boolean | NOT NULL |  |
| error_message | text |  |  |
| cost_estimate | numeric(10,4) |  |  |
| batch_size | integer(32) |  |  |
| sentences_processed | integer(32) |  |  |
| processing_date | timestamp without time zone | DEFAULT CURRENT_TIMESTAMP |  |
| model_used | character varying |  |  |
| session_id | character varying |  |  |

### pre_analyzed_jobs
**Database table**

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | uuid | NOT NULL, DEFAULT gen_random_uuid(), PK | Unique identifier |
| cleaned_scrape_id | uuid | FK → cleaned_job_scrapes(cleaned_job_id) |  |
| company_id | uuid | FK → companies(id) | Associated company reference |
| job_title | character varying | NOT NULL |  |
| company_name | character varying |  |  |
| location_city | character varying |  |  |
| location_province | character varying |  |  |
| location_country | character varying |  |  |
| work_arrangement | character varying |  |  |
| salary_min | integer(32) |  |  |
| salary_max | integer(32) |  |  |
| salary_currency | character varying | DEFAULT 'CAD' |  |
| salary_period | character varying |  |  |
| job_description | text |  |  |
| requirements | text |  |  |
| benefits | text |  |  |
| industry | character varying |  |  |
| job_type | character varying |  |  |
| experience_level | character varying |  |  |
| posting_date | date |  |  |
| application_deadline | date |  |  |
| external_job_id | character varying |  |  |
| source_website | character varying |  |  |
| application_url | character varying |  |  |
| application_email | character varying |  |  |
| confidence_score | numeric(3,2) |  |  |
| duplicates_count | integer(32) | DEFAULT 1 |  |
| deduplication_key | character varying |  |  |
| is_active | boolean | DEFAULT true |  |
| queued_for_analysis | boolean | DEFAULT false |  |
| created_at | timestamp without time zone | DEFAULT CURRENT_TIMESTAMP | Record creation timestamp |
| processed_at | timestamp without time zone |  |  |

### raw_job_scrapes
**Raw scraped data before processing**

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| scrape_id | uuid | NOT NULL, DEFAULT gen_random_uuid(), PK |  |
| source_website | character varying(255) | NOT NULL |  |
| source_url | text | NOT NULL |  |
| full_application_url | text |  |  |
| scrape_timestamp | timestamp without time zone | DEFAULT CURRENT_TIMESTAMP |  |
| raw_data | jsonb | NOT NULL |  |
| scraper_used | character varying(100) |  |  |
| scraper_run_id | character varying(255) |  |  |
| user_agent | text |  |  |
| ip_address | character varying(45) |  |  |
| success_status | boolean | DEFAULT true |  |
| error_message | text |  |  |
| response_time_ms | integer(32) |  |  |
| data_size_bytes | integer(32) |  |  |

### recovery_statistics
**Database table**

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | uuid | NOT NULL, DEFAULT gen_random_uuid(), PK | Unique identifier |
| date | date | DEFAULT CURRENT_DATE, UNIQUE, UNIQUE |  |
| failure_type | character varying(100) | UNIQUE, UNIQUE |  |
| total_failures | integer(32) | DEFAULT 0 |  |
| successful_recoveries | integer(32) | DEFAULT 0 |  |
| failed_recoveries | integer(32) | DEFAULT 0 |  |
| average_recovery_time | numeric(10,2) |  |  |
| created_at | timestamp without time zone | DEFAULT now() | Record creation timestamp |

### security_test_table
**Database table**

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | integer(32) |  | Unique identifier |

### sentence_bank_cover_letter
**Cover letter content sentence bank**

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | uuid | NOT NULL, DEFAULT gen_random_uuid(), PK | Unique identifier |
| content_text | text | NOT NULL |  |
| tone | character varying(100) |  |  |
| tone_strength | double precision(53) |  |  |
| status | character varying(20) | DEFAULT 'Draft' |  |
| position_label | character varying(100) |  |  |
| created_at | timestamp without time zone | DEFAULT CURRENT_TIMESTAMP | Record creation timestamp |
| matches_job_skill | character varying(100) |  |  |
| variable | boolean | DEFAULT false |  |
| keyword_filter_status | character varying | DEFAULT 'pending' |  |
| keyword_filter_date | date |  |  |
| keyword_filter_error_message | text |  |  |
| truthfulness_status | character varying | DEFAULT 'pending' |  |
| truthfulness_date | date |  |  |
| truthfulness_model | character varying |  |  |
| truthfulness_error_message | text |  |  |
| canadian_spelling_status | character varying | DEFAULT 'pending' |  |
| canadian_spelling_date | date |  |  |
| tone_analysis_status | character varying | DEFAULT 'pending' |  |
| tone_analysis_date | date |  |  |
| tone_analysis_model | character varying |  |  |
| tone_analysis_error_message | text |  |  |
| skill_analysis_status | character varying | DEFAULT 'pending' |  |
| skill_analysis_date | date |  |  |
| skill_analysis_model | character varying |  |  |
| skill_analysis_error_message | text |  |  |

### sentence_bank_resume
**Resume content sentence bank**

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | uuid | NOT NULL, DEFAULT gen_random_uuid(), PK | Unique identifier |
| content_text | text | NOT NULL |  |
| body_section | character varying(100) |  |  |
| tone | character varying(100) |  |  |
| tone_strength | double precision(53) |  |  |
| status | character varying(20) | DEFAULT 'Draft' |  |
| created_at | timestamp without time zone | DEFAULT CURRENT_TIMESTAMP | Record creation timestamp |
| matches_job_skill | character varying(100) |  |  |
| experience_id | uuid | FK → job_applications(id) |  |
| keyword_filter_status | character varying | DEFAULT 'pending' |  |
| keyword_filter_date | date |  |  |
| keyword_filter_error_message | text |  |  |
| truthfulness_status | character varying | DEFAULT 'pending' |  |
| truthfulness_date | date |  |  |
| truthfulness_model | character varying |  |  |
| truthfulness_error_message | text |  |  |
| canadian_spelling_status | character varying | DEFAULT 'pending' |  |
| canadian_spelling_date | date |  |  |
| tone_analysis_status | character varying | DEFAULT 'pending' |  |
| tone_analysis_date | date |  |  |
| tone_analysis_model | character varying |  |  |
| tone_analysis_error_message | text |  |  |
| skill_analysis_status | character varying | DEFAULT 'pending' |  |
| skill_analysis_date | date |  |  |
| skill_analysis_model | character varying |  |  |
| skill_analysis_error_message | text |  |  |

### user_candidate_info
**Database table**

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | uuid | NOT NULL, DEFAULT gen_random_uuid(), PK | Unique identifier |
| user_id | uuid | NOT NULL, UNIQUE | User identifier |
| first_name | character varying(100) |  |  |
| last_name | character varying(100) |  |  |
| email | character varying(255) |  |  |
| phone | character varying(20) |  |  |
| mailing_address | text |  |  |
| linkedin_url | character varying(500) |  |  |
| portfolio_url | character varying(500) |  |  |
| calendly_url | character varying(500) |  |  |
| created_at | timestamp without time zone | DEFAULT CURRENT_TIMESTAMP | Record creation timestamp |
| updated_at | timestamp without time zone | DEFAULT CURRENT_TIMESTAMP | Last modification timestamp |

### user_job_preferences
**User criteria and preference packages**

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | uuid | NOT NULL, DEFAULT gen_random_uuid(), PK | Unique identifier |
| user_id | uuid | DEFAULT gen_random_uuid(), UNIQUE | User identifier |
| salary_minimum | integer(32) |  |  |
| hourly_rate_minimum | numeric(10,2) |  |  |
| bonus_expected | boolean | DEFAULT false |  |
| stock_options_preferred | boolean | DEFAULT false |  |
| hours_per_week_minimum | integer(32) |  |  |
| hours_per_week_maximum | integer(32) |  |  |
| flexible_hours_required | boolean | DEFAULT false |  |
| overtime_acceptable | boolean | DEFAULT true |  |
| work_arrangement | character varying(20) |  |  |
| travel_percentage_maximum | integer(32) |  |  |
| preferred_city | character varying(100) |  |  |
| preferred_province_state | character varying(100) |  |  |
| preferred_country | character varying(100) |  |  |
| commute_time_maximum | integer(32) |  |  |
| relocation_acceptable | boolean | DEFAULT false |  |
| health_insurance_required | boolean | DEFAULT true |  |
| dental_insurance_required | boolean | DEFAULT true |  |
| vision_insurance_preferred | boolean | DEFAULT false |  |
| health_benefits_dollar_value | integer(32) |  |  |
| retirement_matching_minimum | numeric(5,2) |  |  |
| vacation_days_minimum | integer(32) |  |  |
| sick_days_minimum | integer(32) |  |  |
| parental_leave_required | boolean | DEFAULT false |  |
| parental_leave_weeks_minimum | integer(32) |  |  |
| training_budget_minimum | integer(32) |  |  |
| conference_attendance_preferred | boolean | DEFAULT false |  |
| certification_support_required | boolean | DEFAULT false |  |
| mentorship_program_preferred | boolean | DEFAULT false |  |
| career_advancement_timeline | integer(32) |  |  |
| company_size_minimum | integer(32) |  |  |
| company_size_maximum | integer(32) |  |  |
| startup_acceptable | boolean | DEFAULT true |  |
| public_company_preferred | boolean | DEFAULT false |  |
| industry_prestige_importance | integer(32) |  |  |
| company_mission_alignment_importance | integer(32) |  |  |
| acceptable_stress | integer(32) |  |  |
| experience_level_minimum | character varying(20) |  |  |
| experience_level_maximum | character varying(20) |  |  |
| management_responsibility_acceptable | boolean | DEFAULT true |  |
| individual_contributor_preferred | boolean | DEFAULT false |  |
| drug_testing_acceptable | boolean | DEFAULT true |  |
| background_check_acceptable | boolean | DEFAULT true |  |
| security_clearance_required | boolean | DEFAULT false |  |
| is_active | boolean | DEFAULT true |  |
| created_at | timestamp without time zone | DEFAULT CURRENT_TIMESTAMP | Record creation timestamp |
| updated_at | timestamp without time zone | DEFAULT CURRENT_TIMESTAMP | Last modification timestamp |
| street_address | text |  |  |
| candidate_id | uuid | FK → user_candidate_info(id) |  |

**Business Rules:**
- Salary amounts in cents for precision
- Multiple preference packages per user supported
- Contextual conditions stored as JSON for flexibility

### user_preference_packages
**Database table**

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| package_id | uuid | NOT NULL, DEFAULT gen_random_uuid(), PK |  |
| user_id | uuid | NOT NULL, FK → user_candidate_info(id) | User identifier |
| package_name | character varying(100) | NOT NULL |  |
| package_description | text |  |  |
| salary_minimum | integer(32) |  |  |
| salary_maximum | integer(32) |  |  |
| location_priority | character varying(200) |  |  |
| work_arrangement | character varying(50) |  |  |
| commute_time_maximum | integer(32) |  |  |
| travel_percentage_maximum | integer(32) |  |  |
| is_active | boolean | DEFAULT true |  |
| created_at | timestamp without time zone | DEFAULT CURRENT_TIMESTAMP | Record creation timestamp |
| updated_at | timestamp without time zone | DEFAULT CURRENT_TIMESTAMP | Last modification timestamp |

### user_preferred_industries
**Database table**

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| preference_id | uuid | NOT NULL, DEFAULT gen_random_uuid(), PK |  |
| user_id | uuid | FK → user_candidate_info(id), UNIQUE, UNIQUE, UNIQUE | User identifier |
| industry_name | character varying(100) | NOT NULL, UNIQUE, UNIQUE, UNIQUE |  |
| preference_type | character varying(20) | NOT NULL, UNIQUE, UNIQUE, UNIQUE |  |
| priority_level | integer(32) |  |  |
| created_at | timestamp without time zone | DEFAULT CURRENT_TIMESTAMP | Record creation timestamp |

### work_experiences
**Database table**

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | uuid | NOT NULL, DEFAULT gen_random_uuid(), PK | Unique identifier |
| user_id | uuid | NOT NULL, FK → user_candidate_info(id), UNIQUE, UNIQUE | User identifier |
| company_name | character varying(200) | NOT NULL |  |
| job_title | character varying(200) | NOT NULL |  |
| start_date | date | NOT NULL |  |
| end_date | date |  |  |
| is_current | boolean | DEFAULT false |  |
| location | character varying(200) |  |  |
| description | text |  |  |
| display_order | integer(32) | UNIQUE, UNIQUE |  |
| created_at | timestamp without time zone | DEFAULT CURRENT_TIMESTAMP | Record creation timestamp |
| updated_at | timestamp without time zone | DEFAULT CURRENT_TIMESTAMP | Last modification timestamp |

### workflow_checkpoints
**Database table**

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | uuid | NOT NULL, DEFAULT gen_random_uuid(), PK | Unique identifier |
| checkpoint_id | character varying(100) | NOT NULL, UNIQUE |  |
| workflow_id | uuid | NOT NULL |  |
| stage | character varying(100) | NOT NULL |  |
| checkpoint_data | jsonb | NOT NULL |  |
| created_at | timestamp without time zone | DEFAULT now() | Record creation timestamp |

## Table Relationships

```
companies (1) ──→ (∞) jobs ──→ (∞) job_applications
                     │              │
                     ├─→ (∞) document_tone_analysis
                     ├─→ (∞) link_tracking
                     └─→ (1) user_job_preferences
                     
raw_job_scrapes ──→ cleaned_job_scrapes (processing pipeline)
```

## Indexes and Performance

### Existing Indexes

**analyzed_jobs:**
- `analyzed_jobs_deduplication_key_key`
- `analyzed_jobs_pkey`
- `idx_analyzed_jobs_department`
- `idx_analyzed_jobs_hiring_manager`
- `idx_analyzed_jobs_job_id`

**application_documents:**
- `idx_job_application_documents_app_id`
- `job_application_documents_job_application_id_document_type__key`
- `job_application_documents_pkey`

**application_settings:**
- `application_settings_pkey`

**canadian_spellings:**
- `canadian_spellings_pkey`

**cleaned_job_scrape_sources:**
- `cleaned_job_scrape_sources_cleaned_job_id_original_scrape_i_key`
- `cleaned_job_scrape_sources_pkey`
- `idx_cleaned_job_scrape_sources_cleaned_id`
- `idx_cleaned_job_scrape_sources_original_id`
- `idx_cleaned_scrapes_processed`
- `idx_cleaned_scrapes_unprocessed`

**cleaned_job_scrapes:**
- `cleaned_job_scrapes_pkey`
- `idx_cleaned_jobs_company`
- `idx_cleaned_jobs_external_id`
- `idx_cleaned_jobs_location`
- `idx_cleaned_jobs_not_expired`
- `idx_cleaned_jobs_salary`
- `idx_cleaned_jobs_timestamp`

**companies:**
- `companies_pkey`
- `idx_companies_created_at`
- `idx_companies_name_lower`

**consistency_validation_logs:**
- `consistency_validation_logs_pkey`

**data_corrections:**
- `data_corrections_pkey`

**document_jobs:**
- `document_jobs_pkey`

**document_sentences:**
- `document_sentences_document_job_id_sentence_order_key`
- `document_sentences_pkey`
- `idx_document_sentences_job_id`
- `idx_document_sentences_tone_score`

**document_template_metadata:**
- `document_template_metadata_pkey`

**document_tone_analysis:**
- `document_tone_analysis_pkey`

**error_log:**
- `error_log_error_id_key`
- `error_log_pkey`

**failure_logs:**
- `failure_logs_pkey`

**job_analysis_queue:**
- `job_analysis_queue_job_id_key`
- `job_analysis_queue_pkey`

**job_application_tracking:**
- `idx_job_application_tracking_app_id`
- `idx_job_application_tracking_type`
- `job_application_tracking_pkey`

**job_applications:**
- `job_applications_pkey`

**job_ats_keywords:**
- `idx_job_ats_keywords_category`
- `idx_job_ats_keywords_job_id`
- `job_ats_keywords_job_id_keyword_key`
- `job_ats_keywords_pkey`

**job_benefits:**
- `idx_job_benefits_job_id`
- `job_benefits_job_id_benefit_type_key`
- `job_benefits_pkey`

**job_certifications:**
- `idx_job_certifications_job_id`
- `job_certifications_pkey`

**job_education_requirements:**
- `job_education_requirements_pkey`

**job_logs:**
- `job_logs_pkey`

**job_platforms_found:**
- `idx_job_platforms_found_job_id`
- `idx_job_platforms_found_platform`
- `job_platforms_found_job_id_platform_name_key`
- `job_platforms_found_pkey`

**job_red_flags_details:**
- `idx_job_red_flags_details_job_id`
- `job_red_flags_details_pkey`

**job_required_documents:**
- `idx_job_required_documents_job_id`
- `job_required_documents_pkey`

**job_required_skills:**
- `idx_job_required_skills_job_id`
- `job_required_skills_job_id_skill_name_key`
- `job_required_skills_pkey`

**job_skills:**
- `idx_job_skills_importance`
- `idx_job_skills_required`
- `job_skills_job_id_skill_name_key`
- `job_skills_pkey`

**job_stress_indicators:**
- `idx_job_stress_indicators_job_id`
- `job_stress_indicators_pkey`

**jobs:**
- `idx_jobs_company_analysis`
- `idx_jobs_created_at`
- `idx_jobs_title_lower`
- `jobs_pkey`

**keyword_filters:**
- `keyword_filters_pkey`

**link_clicks:**
- `idx_link_clicks_clicked_at`
- `idx_link_clicks_source`
- `idx_link_clicks_tracking_id`
- `link_clicks_pkey`

**link_tracking:**
- `idx_link_tracking_active`
- `idx_link_tracking_application_id`
- `idx_link_tracking_function`
- `idx_link_tracking_job_id`
- `link_tracking_pkey`

**performance_metrics:**
- `performance_metrics_pkey`

**pre_analyzed_jobs:**
- `pre_analyzed_jobs_pkey`

**raw_job_scrapes:**
- `idx_raw_scrapes_run_id`
- `idx_raw_scrapes_source`
- `idx_raw_scrapes_timestamp`
- `idx_raw_scrapes_url`
- `raw_job_scrapes_pkey`

**recovery_statistics:**
- `recovery_statistics_date_failure_type_key`
- `recovery_statistics_pkey`

**sentence_bank_cover_letter:**
- `sentence_bank_cover_letter_pkey`

**sentence_bank_resume:**
- `sentence_bank_resume_pkey`

**user_candidate_info:**
- `idx_user_candidate_info_email`
- `idx_user_candidate_info_user_id`
- `uk_user_candidate_info_user_id`
- `user_candidate_info_pkey`

**user_job_preferences:**
- `uk_user_job_preferences_user_id`
- `user_job_preferences_pkey`

**user_preference_packages:**
- `user_preference_packages_pkey`

**user_preferred_industries:**
- `idx_user_preferred_industries_priority`
- `idx_user_preferred_industries_type`
- `idx_user_preferred_industries_user_id`
- `user_preferred_industries_pkey`
- `user_preferred_industries_user_id_industry_name_preference__key`

**work_experiences:**
- `idx_work_experiences_company_name`
- `idx_work_experiences_created_at`
- `idx_work_experiences_current`
- `idx_work_experiences_user_chronological`
- `idx_work_experiences_user_id`
- `uq_user_display_order`
- `work_experiences_pkey`

**workflow_checkpoints:**
- `workflow_checkpoints_checkpoint_id_key`
- `workflow_checkpoints_pkey`

### Recommended Performance Indexes
```sql
-- Performance indexes (not auto-created)
CREATE INDEX idx_jobs_company_eligibility ON jobs(company_id, eligibility_flag);
CREATE INDEX idx_jobs_created_priority ON jobs(created_at DESC, priority_score DESC);
CREATE INDEX idx_applications_status_date ON job_applications(application_status, application_date DESC);
CREATE INDEX idx_raw_scrapes_website_timestamp ON raw_job_scrapes(source_website, scrape_timestamp DESC);
CREATE INDEX idx_cleaned_scrapes_title_company ON cleaned_job_scrapes(job_title, company_name);
CREATE INDEX idx_preferences_active_user ON user_job_preferences(is_active, user_id);
```

## Sample Data Examples

### Example Job Record
```sql
INSERT INTO jobs (job_title, company_id, salary_low, salary_high, location, eligibility_flag) 
VALUES ('Marketing Manager', '123e4567-e89b-12d3-a456-426614174000', 6500000, 8500000, 'Edmonton, AB', true);
```

### Example User Preferences
```sql
INSERT INTO user_job_preferences (salary_minimum, salary_maximum, preferred_city, work_arrangement) 
VALUES (6500000, 8500000, 'Edmonton', 'hybrid');
```

