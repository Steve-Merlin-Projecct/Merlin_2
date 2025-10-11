================================================================================
DATABASE SCHEMA AUDIT
Dashboard V2 Completion - Schema Verification
================================================================================

Connecting to: postgresql://postgres:***@host.docker.internal:5432/local_Merlin_3

✅ Connected successfully!
Database: local_Merlin_3

================================================================================
TABLE: jobs
================================================================================

COLUMNS (59 total):
--------------------------------------------------------------------------------
  id                             UUID                      NOT NULL   DEFAULT gen_random_uuid()
  company_id                     UUID                      NULL       
  job_title                      VARCHAR(255)              NOT NULL   
  job_description                TEXT                      NULL       
  job_number                     VARCHAR(100)              NULL       
  salary_low                     INTEGER                   NULL       
  salary_high                    INTEGER                   NULL       
  salary_period                  VARCHAR(20)               NULL       
  remote_options                 VARCHAR(50)               NULL       
  job_type                       VARCHAR(50)               NULL       
  is_supervisor                  BOOLEAN                   NULL       DEFAULT false
  department                     VARCHAR(100)              NULL       
  industry                       VARCHAR(100)              NULL       
  seniority_level                VARCHAR(50)               NULL       
  application_deadline           DATE                      NULL       
  is_active                      BOOLEAN                   NULL       DEFAULT true
  application_status             VARCHAR(50)               NULL       DEFAULT 'not_applied'::character varying
  last_application_attempt       TIMESTAMP                 NULL       
  application_method             VARCHAR(50)               NULL       
  analysis_completed             BOOLEAN                   NULL       DEFAULT false
  consolidation_confidence       DOUBLE PRECISION          NULL       
  primary_source_url             VARCHAR(500)              NULL       
  posted_date                    DATE                      NULL       
  created_at                     TIMESTAMP                 NULL       DEFAULT CURRENT_TIMESTAMP
  title_matches_role             BOOLEAN                   NULL       
  mismatch_explanation           TEXT                      NULL       
  is_authentic                   BOOLEAN                   NULL       
  authenticity_reasoning         TEXT                      NULL       
  sub_industry                   VARCHAR(100)              NULL       
  job_function                   VARCHAR(100)              NULL       
  in_office_requirements         VARCHAR(50)               NULL       
  office_address                 TEXT                      NULL       
  office_city                    VARCHAR(100)              NULL       
  office_province                VARCHAR(100)              NULL       
  office_country                 VARCHAR(100)              NULL       
  working_hours_per_week         INTEGER                   NULL       
  work_schedule                  TEXT                      NULL       
  specific_schedule              TEXT                      NULL       
  travel_requirements            TEXT                      NULL       
  salary_mentioned               BOOLEAN                   NULL       
  equity_stock_options           BOOLEAN                   NULL       
  commission_or_performance_incentive TEXT                      NULL       
  est_total_compensation         TEXT                      NULL       
  compensation_currency          VARCHAR(10)               NULL       DEFAULT 'CAD'::character varying
  application_email              VARCHAR(255)              NULL       
  special_instructions           TEXT                      NULL       
  estimated_stress_level         INTEGER                   NULL       
  stress_reasoning               TEXT                      NULL       
  education_requirements         TEXT                      NULL       
  overall_red_flag_reasoning     TEXT                      NULL       
  cover_letter_pain_point        TEXT                      NULL       
  cover_letter_evidence          TEXT                      NULL       
  cover_letter_solution_angle    TEXT                      NULL       
  eligibility_flag               BOOLEAN                   NULL       DEFAULT true
  prestige_factor                INTEGER                   NULL       
  prestige_reasoning             TEXT                      NULL       
  supervision_count              INTEGER                   NULL       DEFAULT 0
  budget_size_category           VARCHAR(20)               NULL       
  company_size_category          VARCHAR(20)               NULL       

PRIMARY KEY:
  id

FOREIGN KEYS (1 total):
  ['company_id'] -> companies.['id']

INDEXES (3 total):
  idx_jobs_company_analysis                           (company_id, analysis_completed)
  idx_jobs_created_at                                 (created_at)
  idx_jobs_title_lower                                (NULL)

CHECK CONSTRAINTS (2 total):
  jobs_estimated_stress_level_check        estimated_stress_level >= 1 AND estimated_stress_level <= 10
  jobs_prestige_factor_check               prestige_factor >= 1 AND prestige_factor <= 10

================================================================================
TABLE: job_applications
================================================================================

COLUMNS (16 total):
--------------------------------------------------------------------------------
  id                             UUID                      NOT NULL   DEFAULT gen_random_uuid()
  job_id                         UUID                      NULL       
  application_date               TIMESTAMP                 NULL       DEFAULT CURRENT_TIMESTAMP
  application_method             VARCHAR(50)               NULL       
  application_status             VARCHAR(50)               NULL       
  email_sent_to                  VARCHAR(255)              NULL       
  documents_sent                 ARRAY                     NULL       
  tracking_data                  JSONB                     NULL       
  first_response_received_at     TIMESTAMP                 NULL       
  response_type                  VARCHAR(50)               NULL       
  notes                          TEXT                      NULL       
  tone_jump_score                DOUBLE PRECISION          NULL       
  tone_coherence_score           DOUBLE PRECISION          NULL       
  total_tone_travel              DOUBLE PRECISION          NULL       
  created_at                     TIMESTAMP                 NULL       DEFAULT CURRENT_TIMESTAMP
  last_response_received_at      TIMESTAMP                 NULL       

PRIMARY KEY:
  id

FOREIGN KEYS (1 total):
  ['job_id'] -> jobs.['id']

================================================================================
TABLE: companies
================================================================================

COLUMNS (19 total):
--------------------------------------------------------------------------------
  id                             UUID                      NOT NULL   DEFAULT gen_random_uuid()
  name                           VARCHAR(255)              NOT NULL   
  domain                         VARCHAR(255)              NULL       
  industry                       VARCHAR(100)              NULL       
  sub_industry                   VARCHAR(100)              NULL       
  size_range                     VARCHAR(50)               NULL       
  employee_count_min             INTEGER                   NULL       
  employee_count_max             INTEGER                   NULL       
  headquarters_location          VARCHAR(255)              NULL       
  founded_year                   INTEGER                   NULL       
  company_type                   VARCHAR(50)               NULL       
  company_url                    VARCHAR(500)              NULL       
  linkedin_url                   VARCHAR(500)              NULL       
  glassdoor_url                  VARCHAR(500)              NULL       
  created_at                     TIMESTAMP                 NULL       DEFAULT CURRENT_TIMESTAMP
  company_description            TEXT                      NULL       
  strategic_mission              TEXT                      NULL       
  strategic_values               TEXT                      NULL       
  recent_news                    TEXT                      NULL       

PRIMARY KEY:
  id

INDEXES (3 total):
  idx_companies_created_at                            (created_at)
  idx_companies_name_lower                            (NULL)
  idx_companies_name_trgm                             (name)

================================================================================
SCHEMA COMPATIBILITY CHECK
Checking for columns referenced in migration files
================================================================================


Table: jobs
--------------------------------------------------------------------------------
  priority_score                 ❌ MISSING
  salary_currency                ❌ MISSING
  location                       ❌ MISSING
  experience_level               ❌ MISSING

================================================================================
SUGGESTED COLUMN ALTERNATIVES
================================================================================

For 'location' (missing), consider:

For 'salary_currency' (missing), consider:

For 'priority_score' (missing), consider:

For 'experience_level' (missing), consider:

================================================================================
AUDIT COMPLETE
================================================================================

