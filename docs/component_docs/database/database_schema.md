# Database Schema Documentation

**Version**: 2.16.5  
**Date**: July 28, 2025  
**Tables**: 32  
**Security**: Enhanced with comprehensive audit logging

**Security Note**: All database operations implement comprehensive security controls including parameterized queries, input validation, and audit logging to prevent SQL injection and ensure data integrity.
**Automated Job Application System**

*Last Updated: July 14, 2025*  
*Auto-generated from PostgreSQL information_schema*  
*System Version: 2.6*

## Overview

This database supports a comprehensive automated job application system that scrapes job postings, analyzes them with AI, manages user preferences, and tracks applications with sophisticated document generation and tone analysis. The database has undergone complete normalization with 32 tables achieving optimal relational structure.

## Historical Changes
The database underwent comprehensive normalization to replace JSONB and array columns with proper relational tables. For detailed information about the normalization process, table transformations, and architectural decisions, see the **[Database Normalization Summary](../../../archived_files/docs/database_normalization_summary.md)** which documents the complete evolution from 28 to 32 tables with improved data integrity and query performance.

## Related Documentation
- **[Database Normalization Summary](../../../archived_files/docs/database_normalization_summary.md)** - Historical normalization process and achievements (archived)
- **[Project Architecture](../../../replit.md)** - System overview and development guidelines

### Architecture Summary
- **Primary Tables**: 28 tables with UUID primary keys
- **Database**: neondb
- **Generated**: 2025-07-13T19:43:54.311599

---

## Table Summary

| Table Name | Purpose | Key Relationships |
|------------|---------|-------------------|
| application_settings | System configuration and settings | Standalone |
| cleaned_job_scrapes | Processed and deduplicated job data | Standalone |
| clicks | Database table | tracking_id → link_tracking |
| companies | Company information and metadata | Standalone |
| document_jobs | Document generation tracking | Standalone |
| document_sentences | Database table | document_job_id → document_jobs |
| document_tone_analysis | Document tone analysis results | Standalone |
| job_analysis | Database table | job_id → cleaned_job_scrapes |
| job_application_documents | Database table | job_application_id → job_applications |
| job_application_tracking | Database table | job_application_id → job_applications |
| job_applications | Application tracking and status management | job_id → jobs |
| job_ats_keywords | Database table | job_id → job_analysis |
| job_authenticity_red_flags | Database table | job_id → job_analysis |
| job_benefits | Database table | job_id → jobs |
| job_content_analysis | Database table | job_id → cleaned_job_scrapes |
| job_cover_letter_insights | Database table | job_id → job_analysis |
| job_implicit_requirements | Database table | job_id → job_analysis |
| job_logs | System audit trail and debugging | Standalone |
| job_red_flags | Database table | job_id → job_analysis |
| job_required_skills | Database table | job_id → jobs |
| job_secondary_industries | Database table | job_id → job_analysis |
| job_skills | Database table | job_id → job_analysis |
| jobs | Primary entity for job postings | company_id → companies |
| link_tracking | Hyperlink click tracking | Standalone |
| raw_job_scrapes | Raw scraped data before processing | Standalone |
| sentence_bank_cover_letter | Cover letter content sentence bank | Standalone |
| sentence_bank_resume | Resume content sentence bank | Standalone |
| user_job_preferences | User criteria and preference packages | Standalone |

---

## Detailed Table Specifications

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

### cleaned_job_scrapes
**Processed and deduplicated job data**

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| cleaned_job_id | uuid | NOT NULL, DEFAULT gen_random_uuid(), PK |  |
| original_scrape_ids | ARRAY | NOT NULL |  |
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

### clicks
**Database table**

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| tracking_id | character varying(255) | NOT NULL, FK → link_tracking(tracking_id) |  |
| timestamp | timestamp without time zone | DEFAULT CURRENT_TIMESTAMP |  |

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

### job_analysis
**Database table**

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| job_id | uuid | NOT NULL, FK → cleaned_job_scrapes(cleaned_job_id), PK | Associated job reference |
| analysis_timestamp | timestamp without time zone | DEFAULT CURRENT_TIMESTAMP |  |
| model_used | character varying(100) |  |  |
| analysis_version | character varying(20) |  |  |
| is_authentic | boolean |  |  |
| authenticity_confidence_score | integer(32) |  |  |
| title_match_score | integer(32) |  |  |
| authenticity_reasoning | text |  |  |
| primary_industry | character varying(100) |  |  |
| job_function | character varying(100) |  |  |
| seniority_level | character varying(50) |  |  |
| industry_confidence | integer(32) |  |  |
| salary_transparency | character varying(20) |  |  |
| company_size_indicator | character varying(20) |  |  |
| growth_opportunity | character varying(20) |  |  |
| work_arrangement | character varying(20) |  |  |
| estimated_salary_min | integer(32) |  |  |
| estimated_salary_max | integer(32) |  |  |
| salary_currency | character varying(3) | DEFAULT 'CAD' |  |
| work_hours_per_week | integer(32) |  |  |
| overtime_expected | boolean |  |  |
| remote_work_percentage | integer(32) |  |  |
| stress_level_score | integer(32) |  |  |
| workload_intensity | character varying(20) |  |  |
| deadline_pressure | character varying(20) |  |  |
| total_skills_found | integer(32) | DEFAULT 0 |  |

### job_application_documents
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
| job_id | uuid | FK → job_analysis(job_id), UNIQUE, UNIQUE | Associated job reference |
| keyword | character varying(100) | NOT NULL, UNIQUE, UNIQUE |  |
| keyword_category | character varying(30) |  |  |
| frequency_in_posting | integer(32) | DEFAULT 1 |  |

### job_authenticity_red_flags
**Database table**

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | uuid | NOT NULL, DEFAULT gen_random_uuid(), PK | Unique identifier |
| job_id | uuid | FK → job_analysis(job_id), UNIQUE, UNIQUE | Associated job reference |
| red_flag_type | character varying(100) | NOT NULL, UNIQUE, UNIQUE |  |
| red_flag_description | text |  |  |

### job_benefits
**Database table**

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| benefit_id | uuid | NOT NULL, DEFAULT gen_random_uuid(), PK |  |
| job_id | uuid | FK → jobs(id), UNIQUE, UNIQUE | Associated job reference |
| benefit_type | character varying(50) | NOT NULL, UNIQUE, UNIQUE |  |
| benefit_description | text |  |  |
| benefit_value | character varying(100) |  |  |

### job_content_analysis
**Database table**

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| job_id | uuid | NOT NULL, FK → cleaned_job_scrapes(cleaned_job_id), PK | Associated job reference |
| skills_analysis | jsonb |  |  |
| authenticity_check | jsonb |  |  |
| industry_classification | jsonb |  |  |
| additional_insights | jsonb |  |  |
| analysis_timestamp | timestamp without time zone | DEFAULT CURRENT_TIMESTAMP |  |
| model_used | character varying(100) |  |  |
| analysis_version | character varying(20) |  |  |

### job_cover_letter_insights
**Database table**

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | uuid | NOT NULL, DEFAULT gen_random_uuid(), PK | Unique identifier |
| job_id | uuid | FK → job_analysis(job_id), UNIQUE, UNIQUE | Associated job reference |
| insight_type | character varying(50) | NOT NULL, UNIQUE, UNIQUE |  |
| insight_description | text | NOT NULL |  |
| strategic_value | character varying(20) |  |  |

### job_implicit_requirements
**Database table**

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | uuid | NOT NULL, DEFAULT gen_random_uuid(), PK | Unique identifier |
| job_id | uuid | FK → job_analysis(job_id), UNIQUE, UNIQUE | Associated job reference |
| requirement_type | character varying(50) | NOT NULL, UNIQUE, UNIQUE |  |
| requirement_description | text | NOT NULL |  |
| importance_level | character varying(20) |  |  |

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

### job_red_flags
**Database table**

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | uuid | NOT NULL, DEFAULT gen_random_uuid(), PK | Unique identifier |
| job_id | uuid | FK → job_analysis(job_id), UNIQUE, UNIQUE | Associated job reference |
| flag_category | character varying(50) | NOT NULL, UNIQUE, UNIQUE |  |
| flag_description | text | NOT NULL |  |
| severity_level | character varying(20) |  |  |

### job_required_skills
**Database table**

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| skill_id | uuid | NOT NULL, DEFAULT gen_random_uuid(), PK |  |
| job_id | uuid | FK → jobs(id), UNIQUE, UNIQUE | Associated job reference |
| skill_name | character varying(100) | NOT NULL, UNIQUE, UNIQUE |  |
| skill_level | character varying(20) |  |  |
| is_required | boolean | DEFAULT true |  |
| years_experience | integer(32) |  |  |

### job_secondary_industries
**Database table**

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | uuid | NOT NULL, DEFAULT gen_random_uuid(), PK | Unique identifier |
| job_id | uuid | FK → job_analysis(job_id), UNIQUE, UNIQUE | Associated job reference |
| industry_name | character varying(100) | NOT NULL, UNIQUE, UNIQUE |  |

### job_skills
**Database table**

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| skill_id | uuid | NOT NULL, DEFAULT gen_random_uuid(), PK |  |
| job_id | uuid | FK → job_analysis(job_id), UNIQUE, UNIQUE | Associated job reference |
| skill_name | character varying(100) | NOT NULL, UNIQUE, UNIQUE |  |
| importance_rating | integer(32) |  |  |
| skill_category | character varying(20) |  |  |
| is_required | boolean | DEFAULT false |  |
| years_experience | integer(32) |  |  |

### jobs
**Primary entity for job postings**

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | uuid | NOT NULL, DEFAULT gen_random_uuid(), PK | Unique identifier |
| company_id | uuid | FK → companies(id) | Associated company reference |
| job_title | character varying(255) | NOT NULL | Position title |
| job_description | text |  |  |
| requirements | text |  |  |
| job_number | character varying(100) |  |  |
| salary_low | integer(32) |  | Minimum salary (in cents) |
| salary_high | integer(32) |  | Maximum salary (in cents) |
| salary_currency | character varying(10) | DEFAULT 'USD' |  |
| salary_period | character varying(20) |  |  |
| location | character varying(255) |  |  |
| remote_options | character varying(50) |  |  |
| job_type | character varying(50) |  |  |
| experience_level | character varying(50) |  |  |
| is_supervisor | boolean | DEFAULT false |  |
| reports_to | character varying(100) |  |  |
| team_size | character varying(50) |  |  |
| department | character varying(100) |  |  |
| industry | character varying(100) |  |  |
| career_path | character varying(100) |  |  |
| seniority_level | character varying(50) |  |  |
| skills_required | ARRAY |  |  |
| benefits | ARRAY |  |  |
| application_deadline | date |  |  |
| is_active | boolean | DEFAULT true |  |
| application_status | character varying(50) | DEFAULT 'not_applied' |  |
| last_application_attempt | timestamp without time zone |  |  |
| application_method | character varying(50) |  |  |
| eligibility_flag | boolean | DEFAULT false | Meets user criteria |
| analysis_completed | boolean | DEFAULT false |  |
| priority_score | double precision(53) | DEFAULT 0.0 | AI-calculated priority (0.0-10.0) |
| consolidation_confidence | double precision(53) |  |  |
| platforms_found | ARRAY |  |  |
| primary_source_url | character varying(500) |  |  |
| posted_date | date |  |  |
| created_at | timestamp without time zone | DEFAULT CURRENT_TIMESTAMP | Record creation timestamp |

**Business Rules:**
- Salary amounts stored in cents for precision
- Priority score ranges 0.0-10.0, higher = better match
- Application status: 'not_applied', 'pending', 'submitted', 'responded', 'rejected'

### link_tracking
**Hyperlink click tracking**

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| tracking_id | character varying(100) | NOT NULL, PK, UNIQUE |  |
| link_type | character varying(50) | NOT NULL |  |
| original_url | character varying(500) | NOT NULL |  |

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

### sentence_bank_cover_letter
**Cover letter content sentence bank**

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | uuid | NOT NULL, DEFAULT gen_random_uuid(), PK | Unique identifier |
| text | text | NOT NULL |  |
| category | character varying(100) |  |  |
| tone | character varying(100) |  |  |
| tone_strength | double precision(53) |  |  |
| tags | ARRAY |  |  |
| matches_job_attributes | ARRAY |  |  |
| length | character varying(20) |  |  |
| stage | character varying(20) | DEFAULT 'Draft' |  |
| position_label | character varying(100) |  |  |
| sentence_strength | integer(32) |  |  |
| created_at | timestamp without time zone | DEFAULT CURRENT_TIMESTAMP | Record creation timestamp |

### sentence_bank_resume
**Resume content sentence bank**

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | uuid | NOT NULL, DEFAULT gen_random_uuid(), PK | Unique identifier |
| text | text | NOT NULL |  |
| category | character varying(100) |  |  |
| tone | character varying(100) |  |  |
| tone_strength | double precision(53) |  |  |
| tags | ARRAY |  |  |
| matches_job_attributes | ARRAY |  |  |
| length | character varying(20) |  |  |
| stage | character varying(20) | DEFAULT 'Draft' |  |
| position_label | character varying(100) |  |  |
| sentence_strength | integer(32) |  |  |
| created_at | timestamp without time zone | DEFAULT CURRENT_TIMESTAMP | Record creation timestamp |

### user_job_preferences
**User criteria and preference packages**

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | uuid | NOT NULL, DEFAULT gen_random_uuid(), PK | Unique identifier |
| user_id | uuid | DEFAULT gen_random_uuid() | User identifier |
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
| preferred_industries | ARRAY |  |  |
| excluded_industries | ARRAY |  |  |
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

**Business Rules:**
- Salary amounts in cents for precision
- Multiple preference packages per user supported
- Contextual conditions stored as JSON for flexibility

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

**application_settings:**
- `application_settings_pkey`

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

**document_jobs:**
- `document_jobs_pkey`

**document_sentences:**
- `document_sentences_document_job_id_sentence_order_key`
- `document_sentences_pkey`
- `idx_document_sentences_job_id`
- `idx_document_sentences_tone_score`

**document_tone_analysis:**
- `document_tone_analysis_pkey`

**job_analysis:**
- `idx_job_analysis_industry`
- `idx_job_analysis_salary_range`
- `idx_job_analysis_seniority`
- `idx_job_analysis_timestamp`
- `idx_job_analysis_work_arrangement`
- `job_analysis_pkey`

**job_application_documents:**
- `idx_job_application_documents_app_id`
- `job_application_documents_job_application_id_document_type__key`
- `job_application_documents_pkey`

**job_application_tracking:**
- `idx_job_application_tracking_app_id`
- `idx_job_application_tracking_type`
- `job_application_tracking_pkey`

**job_applications:**
- `job_applications_pkey`

**job_ats_keywords:**
- `idx_job_ats_keywords_category`
- `job_ats_keywords_job_id_keyword_key`
- `job_ats_keywords_pkey`

**job_authenticity_red_flags:**
- `job_authenticity_red_flags_job_id_red_flag_type_key`
- `job_authenticity_red_flags_pkey`

**job_benefits:**
- `idx_job_benefits_job_id`
- `job_benefits_job_id_benefit_type_key`
- `job_benefits_pkey`

**job_content_analysis:**
- `job_content_analysis_pkey`

**job_cover_letter_insights:**
- `job_cover_letter_insights_job_id_insight_type_key`
- `job_cover_letter_insights_pkey`

**job_implicit_requirements:**
- `idx_job_implicit_requirements_importance`
- `job_implicit_requirements_job_id_requirement_type_key`
- `job_implicit_requirements_pkey`

**job_logs:**
- `job_logs_pkey`

**job_red_flags:**
- `idx_job_red_flags_severity`
- `job_red_flags_job_id_flag_category_key`
- `job_red_flags_pkey`

**job_required_skills:**
- `idx_job_required_skills_job_id`
- `job_required_skills_job_id_skill_name_key`
- `job_required_skills_pkey`

**job_secondary_industries:**
- `job_secondary_industries_job_id_industry_name_key`
- `job_secondary_industries_pkey`

**job_skills:**
- `idx_job_skills_category`
- `idx_job_skills_importance`
- `idx_job_skills_required`
- `job_skills_job_id_skill_name_key`
- `job_skills_pkey`

**jobs:**
- `jobs_pkey`

**link_tracking:**
- `link_tracking_pkey`
- `link_tracking_tracking_id_key`

**raw_job_scrapes:**
- `idx_raw_scrapes_run_id`
- `idx_raw_scrapes_source`
- `idx_raw_scrapes_timestamp`
- `idx_raw_scrapes_url`
- `raw_job_scrapes_pkey`

**sentence_bank_cover_letter:**
- `sentence_bank_cover_letter_pkey`

**sentence_bank_resume:**
- `sentence_bank_resume_pkey`

**user_job_preferences:**
- `user_job_preferences_pkey`

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

