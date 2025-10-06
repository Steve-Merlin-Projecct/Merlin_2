"""
Database Migration Script
Generated on 2025-09-12 13:08:25
"""

from sqlalchemy import text
from sqlalchemy.orm import Session

def migrate_database(db: Session):
    """
    Apply database schema changes
    """
    migration_statements = []
    
    # Create new table: analyzed_jobs
    migration_statements.append("""
CREATE TABLE analyzed_jobs (
    id uuid NOT NULL DEFAULT gen_random_uuid(),
    pre_analyzed_job_id uuid,
    company_id uuid,
    job_title character varying NOT NULL,
    job_description text,
    job_number character varying,
    salary_low integer,
    salary_high integer,
    salary_period character varying,
    compensation_currency character varying DEFAULT 'CAD'::character varying,
    equity_stock_options boolean,
    commission_or_performance_incentive text,
    est_total_compensation text,
    remote_options character varying,
    job_type character varying,
    in_office_requirements character varying,
    office_address text,
    office_city character varying,
    office_province character varying,
    office_country character varying,
    working_hours_per_week integer,
    work_schedule text,
    specific_schedule text,
    travel_requirements text,
    is_supervisor boolean DEFAULT false,
    department character varying,
    industry character varying,
    sub_industry character varying,
    job_function character varying,
    seniority_level character varying,
    supervision_count integer DEFAULT 0,
    budget_size_category character varying,
    company_size_category character varying,
    application_deadline date,
    application_email character varying,
    application_method character varying,
    special_instructions text,
    primary_source_url character varying,
    posted_date date,
    ai_analysis_completed boolean DEFAULT false,
    primary_industry character varying,
    authenticity_score numeric,
    deduplication_key character varying,
    application_status character varying DEFAULT 'not_applied'::character varying,
    last_application_attempt timestamp without time zone,
    eligibility_flag boolean DEFAULT true,
    prestige_factor integer,
    prestige_reasoning text,
    estimated_stress_level integer,
    stress_reasoning text,
    analysis_date timestamp without time zone,
    gemini_model_used character varying,
    analysis_tokens_used integer,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    job_id uuid,
    hiring_manager character varying(100),
    reporting_to character varying(100),
    job_title_extracted character varying(200),
    company_name_extracted character varying(100),
    additional_insights text,
    FOREIGN KEY (company_id) REFERENCES companies(id),
    FOREIGN KEY (job_id) REFERENCES jobs(id),
    PRIMARY KEY (id)
);    """)

    # Create new table: application_documents
    migration_statements.append("""
CREATE TABLE application_documents (
    document_id uuid NOT NULL DEFAULT gen_random_uuid(),
    job_application_id uuid,
    document_type character varying(30) NOT NULL,
    document_name character varying(255) NOT NULL,
    file_path text,
    file_size integer,
    sent_timestamp timestamp without time zone NOT NULL,
    FOREIGN KEY (job_application_id) REFERENCES job_applications(id),
    PRIMARY KEY (document_id)
);    """)

    # Create new table: canadian_spellings
    migration_statements.append("""
CREATE TABLE canadian_spellings (
    id uuid NOT NULL DEFAULT gen_random_uuid(),
    american_spelling character varying NOT NULL,
    canadian_spelling character varying NOT NULL,
    status character varying DEFAULT 'active'::character varying,
    created_date date DEFAULT CURRENT_DATE,
    PRIMARY KEY (id)
);    """)

    # Create new table: cleaned_job_scrape_sources
    migration_statements.append("""
CREATE TABLE cleaned_job_scrape_sources (
    source_id uuid NOT NULL DEFAULT gen_random_uuid(),
    cleaned_job_id uuid,
    original_scrape_id uuid NOT NULL,
    source_priority integer,
    merge_timestamp timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    processed_to_jobs boolean DEFAULT false,
    job_id uuid,
    processed_at timestamp without time zone,
    FOREIGN KEY (cleaned_job_id) REFERENCES cleaned_job_scrapes(cleaned_job_id),
    FOREIGN KEY (job_id) REFERENCES jobs(id),
    PRIMARY KEY (source_id)
);    """)

    # Create new table: consistency_validation_logs
    migration_statements.append("""
CREATE TABLE consistency_validation_logs (
    id uuid NOT NULL DEFAULT gen_random_uuid(),
    validation_run_id uuid NOT NULL,
    issue_type character varying(100),
    severity character varying(20),
    description text,
    affected_record_count integer,
    correctable boolean,
    correction_applied boolean DEFAULT false,
    created_at timestamp without time zone DEFAULT now(),
    PRIMARY KEY (id)
);    """)

    # Create new table: data_corrections
    migration_statements.append("""
CREATE TABLE data_corrections (
    id uuid NOT NULL DEFAULT gen_random_uuid(),
    validation_run_id uuid NOT NULL,
    correction_type character varying(100),
    affected_table character varying(100),
    affected_records jsonb,
    correction_sql text,
    applied_at timestamp without time zone DEFAULT now(),
    success boolean DEFAULT true,
    PRIMARY KEY (id)
);    """)

    # Create new table: document_sentences
    migration_statements.append("""
CREATE TABLE document_sentences (
    sentence_id uuid NOT NULL DEFAULT gen_random_uuid(),
    document_job_id uuid,
    sentence_text text NOT NULL,
    tone_score numeric,
    sentiment_category character varying(20),
    confidence_score numeric,
    word_count integer,
    sentence_order integer,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (document_job_id) REFERENCES document_jobs(job_id),
    PRIMARY KEY (sentence_id)
);    """)

    # Create new table: document_template_metadata
    migration_statements.append("""
CREATE TABLE document_template_metadata (
    document_type character varying(20) NOT NULL,
    resume_general_section_count integer,
    resume_constituent_section_count integer,
    cover_par_one integer,
    cover_par_two integer,
    cover_par_three integer,
    count integer DEFAULT 0,
    template_file_path character varying(255),
    id integer NOT NULL DEFAULT nextval('document_template_metadata_id_seq'::regclass),
    PRIMARY KEY (id)
);    """)

    # Create new table: error_log
    migration_statements.append("""
CREATE TABLE error_log (
    id integer NOT NULL DEFAULT nextval('error_log_id_seq'::regclass),
    error_id character varying(36) NOT NULL,
    timestamp timestamp without time zone NOT NULL,
    session_id character varying(36),
    stage_name character varying(50),
    error_category character varying(30) NOT NULL,
    severity character varying(20) NOT NULL,
    error_message text NOT NULL,
    error_details text,
    exception_type character varying(100),
    stack_trace text,
    context_data jsonb,
    retry_count integer DEFAULT 0,
    resolved boolean DEFAULT false,
    resolution_notes text,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id)
);    """)

    # Create new table: failure_logs
    migration_statements.append("""
CREATE TABLE failure_logs (
    id uuid NOT NULL DEFAULT gen_random_uuid(),
    failure_type character varying(100) NOT NULL,
    operation_name character varying(200) NOT NULL,
    workflow_id uuid,
    error_message text,
    error_details jsonb,
    recovery_attempts integer DEFAULT 0,
    recovery_successful boolean DEFAULT false,
    created_at timestamp without time zone DEFAULT now(),
    resolved_at timestamp without time zone,
    PRIMARY KEY (id)
);    """)

    # Create new table: job_analysis_queue
    migration_statements.append("""
CREATE TABLE job_analysis_queue (
    id integer NOT NULL DEFAULT nextval('job_analysis_queue_id_seq'::regclass),
    job_id uuid NOT NULL,
    priority character varying(20) DEFAULT 'normal'::character varying,
    queued_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    attempts integer DEFAULT 0,
    last_attempt_at timestamp without time zone,
    error_message text,
    status character varying(20) DEFAULT 'pending'::character varying,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (job_id) REFERENCES jobs(id),
    PRIMARY KEY (id)
);    """)

    # Create new table: job_application_tracking
    migration_statements.append("""
CREATE TABLE job_application_tracking (
    tracking_id uuid NOT NULL DEFAULT gen_random_uuid(),
    job_application_id uuid,
    tracking_type character varying(50) NOT NULL,
    tracking_event character varying(100) NOT NULL,
    event_timestamp timestamp without time zone NOT NULL,
    event_data jsonb,
    ip_address inet,
    user_agent text,
    FOREIGN KEY (job_application_id) REFERENCES job_applications(id),
    PRIMARY KEY (tracking_id)
);    """)

    # Create new table: job_ats_keywords
    migration_statements.append("""
CREATE TABLE job_ats_keywords (
    id uuid NOT NULL DEFAULT gen_random_uuid(),
    job_id uuid,
    keyword character varying(100) NOT NULL,
    keyword_category character varying(30),
    frequency_in_posting integer DEFAULT 1,
    PRIMARY KEY (id)
);    """)

    # Create new table: job_benefits
    migration_statements.append("""
CREATE TABLE job_benefits (
    benefit_id uuid NOT NULL DEFAULT gen_random_uuid(),
    job_id uuid,
    benefit_type character varying(50) NOT NULL,
    benefit_description text,
    benefit_value character varying(100),
    FOREIGN KEY (job_id) REFERENCES jobs(id),
    PRIMARY KEY (benefit_id)
);    """)

    # Create new table: job_certifications
    migration_statements.append("""
CREATE TABLE job_certifications (
    id integer NOT NULL DEFAULT nextval('job_certifications_id_seq'::regclass),
    job_id uuid,
    certification_name character varying(100) NOT NULL,
    is_required boolean DEFAULT true,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (job_id) REFERENCES jobs(id),
    PRIMARY KEY (id)
);    """)

    # Create new table: job_education_requirements
    migration_statements.append("""
CREATE TABLE job_education_requirements (
    id integer NOT NULL DEFAULT nextval('job_education_requirements_id_seq'::regclass),
    job_id uuid NOT NULL,
    degree_level character varying(100),
    field_of_study character varying(200),
    institution_type character varying(100),
    years_required integer,
    is_required boolean DEFAULT true,
    alternative_experience text,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (job_id) REFERENCES jobs(id),
    PRIMARY KEY (id)
);    """)

    # Create new table: job_platforms_found
    migration_statements.append("""
CREATE TABLE job_platforms_found (
    platform_id uuid NOT NULL DEFAULT gen_random_uuid(),
    job_id uuid,
    platform_name character varying(100) NOT NULL,
    platform_url text,
    first_found_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (job_id) REFERENCES jobs(id),
    PRIMARY KEY (platform_id)
);    """)

    # Create new table: job_red_flags_details
    migration_statements.append("""
CREATE TABLE job_red_flags_details (
    id integer NOT NULL DEFAULT nextval('job_red_flags_details_id_seq'::regclass),
    job_id uuid,
    flag_type character varying(50) NOT NULL,
    detected boolean DEFAULT false,
    details text,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (job_id) REFERENCES jobs(id),
    PRIMARY KEY (id)
);    """)

    # Create new table: job_required_documents
    migration_statements.append("""
CREATE TABLE job_required_documents (
    id integer NOT NULL DEFAULT nextval('job_required_documents_id_seq'::regclass),
    job_id uuid,
    document_type character varying(50) NOT NULL,
    is_required boolean DEFAULT true,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (job_id) REFERENCES jobs(id),
    PRIMARY KEY (id)
);    """)

    # Create new table: job_required_skills
    migration_statements.append("""
CREATE TABLE job_required_skills (
    skill_id uuid NOT NULL DEFAULT gen_random_uuid(),
    job_id uuid,
    skill_name character varying(100) NOT NULL,
    skill_level character varying(20),
    is_required boolean DEFAULT true,
    FOREIGN KEY (job_id) REFERENCES jobs(id),
    PRIMARY KEY (skill_id)
);    """)

    # Create new table: job_skills
    migration_statements.append("""
CREATE TABLE job_skills (
    skill_id uuid NOT NULL DEFAULT gen_random_uuid(),
    job_id uuid,
    skill_name character varying(100) NOT NULL,
    importance_rating integer,
    is_required boolean DEFAULT false,
    reasoning text,
    PRIMARY KEY (skill_id)
);    """)

    # Create new table: job_stress_indicators
    migration_statements.append("""
CREATE TABLE job_stress_indicators (
    id integer NOT NULL DEFAULT nextval('job_stress_indicators_id_seq'::regclass),
    job_id uuid,
    indicator character varying(100) NOT NULL,
    description text,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (job_id) REFERENCES jobs(id),
    PRIMARY KEY (id)
);    """)

    # Create new table: keyword_filters
    migration_statements.append("""
CREATE TABLE keyword_filters (
    id uuid NOT NULL DEFAULT gen_random_uuid(),
    keyword character varying NOT NULL,
    status character varying DEFAULT 'active'::character varying,
    created_date date DEFAULT CURRENT_DATE,
    PRIMARY KEY (id)
);    """)

    # Create new table: link_clicks
    migration_statements.append("""
CREATE TABLE link_clicks (
    click_id uuid NOT NULL DEFAULT gen_random_uuid(),
    tracking_id character varying(100) NOT NULL,
    clicked_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    ip_address inet,
    user_agent text,
    referrer_url character varying(1000),
    session_id character varying(100),
    click_source character varying(50),
    metadata jsonb DEFAULT '{}'::jsonb,
    FOREIGN KEY (tracking_id) REFERENCES link_tracking(tracking_id),
    PRIMARY KEY (click_id)
);    """)

    # Create new table: performance_metrics
    migration_statements.append("""
CREATE TABLE performance_metrics (
    id uuid NOT NULL DEFAULT gen_random_uuid(),
    stage_name character varying NOT NULL,
    api_call_type character varying NOT NULL,
    response_time_ms integer,
    success boolean NOT NULL,
    error_message text,
    cost_estimate numeric,
    batch_size integer,
    sentences_processed integer,
    processing_date timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    model_used character varying,
    session_id character varying,
    PRIMARY KEY (id)
);    """)

    # Create new table: pre_analyzed_jobs
    migration_statements.append("""
CREATE TABLE pre_analyzed_jobs (
    id uuid NOT NULL DEFAULT gen_random_uuid(),
    cleaned_scrape_id uuid,
    company_id uuid,
    job_title character varying NOT NULL,
    company_name character varying,
    location_city character varying,
    location_province character varying,
    location_country character varying,
    work_arrangement character varying,
    salary_min integer,
    salary_max integer,
    salary_currency character varying DEFAULT 'CAD'::character varying,
    salary_period character varying,
    job_description text,
    requirements text,
    benefits text,
    industry character varying,
    job_type character varying,
    experience_level character varying,
    posting_date date,
    application_deadline date,
    external_job_id character varying,
    source_website character varying,
    application_url character varying,
    application_email character varying,
    confidence_score numeric,
    duplicates_count integer DEFAULT 1,
    deduplication_key character varying,
    is_active boolean DEFAULT true,
    queued_for_analysis boolean DEFAULT false,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    processed_at timestamp without time zone,
    FOREIGN KEY (cleaned_scrape_id) REFERENCES cleaned_job_scrapes(cleaned_job_id),
    FOREIGN KEY (company_id) REFERENCES companies(id),
    PRIMARY KEY (id)
);    """)

    # Create new table: recovery_statistics
    migration_statements.append("""
CREATE TABLE recovery_statistics (
    id uuid NOT NULL DEFAULT gen_random_uuid(),
    date date DEFAULT CURRENT_DATE,
    failure_type character varying(100),
    total_failures integer DEFAULT 0,
    successful_recoveries integer DEFAULT 0,
    failed_recoveries integer DEFAULT 0,
    average_recovery_time numeric,
    created_at timestamp without time zone DEFAULT now(),
    PRIMARY KEY (id)
);    """)

    # Create new table: security_test_table
    migration_statements.append("""
CREATE TABLE security_test_table (
    id integer
);    """)

    # Create new table: user_candidate_info
    migration_statements.append("""
CREATE TABLE user_candidate_info (
    id uuid NOT NULL DEFAULT gen_random_uuid(),
    user_id uuid NOT NULL,
    first_name character varying(100),
    last_name character varying(100),
    email character varying(255),
    phone character varying(20),
    mailing_address text,
    linkedin_url character varying(500),
    portfolio_url character varying(500),
    calendly_url character varying(500),
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id)
);    """)

    # Create new table: user_preference_packages
    migration_statements.append("""
CREATE TABLE user_preference_packages (
    package_id uuid NOT NULL DEFAULT gen_random_uuid(),
    user_id uuid NOT NULL,
    package_name character varying(100) NOT NULL,
    package_description text,
    salary_minimum integer,
    salary_maximum integer,
    location_priority character varying(200),
    work_arrangement character varying(50),
    commute_time_maximum integer,
    travel_percentage_maximum integer,
    is_active boolean DEFAULT true,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user_candidate_info(id),
    PRIMARY KEY (package_id)
);    """)

    # Create new table: user_preferred_industries
    migration_statements.append("""
CREATE TABLE user_preferred_industries (
    preference_id uuid NOT NULL DEFAULT gen_random_uuid(),
    user_id uuid,
    industry_name character varying(100) NOT NULL,
    preference_type character varying(20) NOT NULL,
    priority_level integer,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user_candidate_info(id),
    PRIMARY KEY (preference_id)
);    """)

    # Create new table: work_experiences
    migration_statements.append("""
CREATE TABLE work_experiences (
    id uuid NOT NULL DEFAULT gen_random_uuid(),
    user_id uuid NOT NULL,
    company_name character varying(200) NOT NULL,
    job_title character varying(200) NOT NULL,
    start_date date NOT NULL,
    end_date date,
    is_current boolean DEFAULT false,
    location character varying(200),
    description text,
    display_order integer,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user_candidate_info(id),
    PRIMARY KEY (id)
);    """)

    # Create new table: workflow_checkpoints
    migration_statements.append("""
CREATE TABLE workflow_checkpoints (
    id uuid NOT NULL DEFAULT gen_random_uuid(),
    checkpoint_id character varying(100) NOT NULL,
    workflow_id uuid NOT NULL,
    stage character varying(100) NOT NULL,
    checkpoint_data jsonb NOT NULL,
    created_at timestamp without time zone DEFAULT now(),
    PRIMARY KEY (id)
);    """)

    # Drop table: clicks
    migration_statements.append("DROP TABLE IF EXISTS clicks CASCADE;")

    # Add column confidence_score to cleaned_job_scrapes
    migration_statements.append("""ALTER TABLE cleaned_job_scrapes ADD COLUMN confidence_score numeric;""")

    # Add column duplicates_count to cleaned_job_scrapes
    migration_statements.append("""ALTER TABLE cleaned_job_scrapes ADD COLUMN duplicates_count integer;""")

    # Drop column original_scrape_ids from cleaned_job_scrapes
    migration_statements.append("""ALTER TABLE cleaned_job_scrapes DROP COLUMN original_scrape_ids;""")

    # Add column title_matches_role to jobs
    migration_statements.append("""ALTER TABLE jobs ADD COLUMN title_matches_role boolean;""")

    # Add column mismatch_explanation to jobs
    migration_statements.append("""ALTER TABLE jobs ADD COLUMN mismatch_explanation text;""")

    # Add column is_authentic to jobs
    migration_statements.append("""ALTER TABLE jobs ADD COLUMN is_authentic boolean;""")

    # Add column authenticity_reasoning to jobs
    migration_statements.append("""ALTER TABLE jobs ADD COLUMN authenticity_reasoning text;""")

    # Add column sub_industry to jobs
    migration_statements.append("""ALTER TABLE jobs ADD COLUMN sub_industry character varying;""")

    # Add column job_function to jobs
    migration_statements.append("""ALTER TABLE jobs ADD COLUMN job_function character varying;""")

    # Add column in_office_requirements to jobs
    migration_statements.append("""ALTER TABLE jobs ADD COLUMN in_office_requirements character varying;""")

    # Add column office_address to jobs
    migration_statements.append("""ALTER TABLE jobs ADD COLUMN office_address text;""")

    # Add column office_city to jobs
    migration_statements.append("""ALTER TABLE jobs ADD COLUMN office_city character varying;""")

    # Add column office_province to jobs
    migration_statements.append("""ALTER TABLE jobs ADD COLUMN office_province character varying;""")

    # Add column office_country to jobs
    migration_statements.append("""ALTER TABLE jobs ADD COLUMN office_country character varying;""")

    # Add column working_hours_per_week to jobs
    migration_statements.append("""ALTER TABLE jobs ADD COLUMN working_hours_per_week integer;""")

    # Add column work_schedule to jobs
    migration_statements.append("""ALTER TABLE jobs ADD COLUMN work_schedule text;""")

    # Add column specific_schedule to jobs
    migration_statements.append("""ALTER TABLE jobs ADD COLUMN specific_schedule text;""")

    # Add column travel_requirements to jobs
    migration_statements.append("""ALTER TABLE jobs ADD COLUMN travel_requirements text;""")

    # Add column salary_mentioned to jobs
    migration_statements.append("""ALTER TABLE jobs ADD COLUMN salary_mentioned boolean;""")

    # Add column equity_stock_options to jobs
    migration_statements.append("""ALTER TABLE jobs ADD COLUMN equity_stock_options boolean;""")

    # Add column commission_or_performance_incentive to jobs
    migration_statements.append("""ALTER TABLE jobs ADD COLUMN commission_or_performance_incentive text;""")

    # Add column est_total_compensation to jobs
    migration_statements.append("""ALTER TABLE jobs ADD COLUMN est_total_compensation text;""")

    # Add column compensation_currency to jobs
    migration_statements.append("""ALTER TABLE jobs ADD COLUMN compensation_currency character varying;""")

    # Add column application_email to jobs
    migration_statements.append("""ALTER TABLE jobs ADD COLUMN application_email character varying;""")

    # Add column special_instructions to jobs
    migration_statements.append("""ALTER TABLE jobs ADD COLUMN special_instructions text;""")

    # Add column estimated_stress_level to jobs
    migration_statements.append("""ALTER TABLE jobs ADD COLUMN estimated_stress_level integer;""")

    # Add column stress_reasoning to jobs
    migration_statements.append("""ALTER TABLE jobs ADD COLUMN stress_reasoning text;""")

    # Add column education_requirements to jobs
    migration_statements.append("""ALTER TABLE jobs ADD COLUMN education_requirements text;""")

    # Add column overall_red_flag_reasoning to jobs
    migration_statements.append("""ALTER TABLE jobs ADD COLUMN overall_red_flag_reasoning text;""")

    # Add column cover_letter_pain_point to jobs
    migration_statements.append("""ALTER TABLE jobs ADD COLUMN cover_letter_pain_point text;""")

    # Add column cover_letter_evidence to jobs
    migration_statements.append("""ALTER TABLE jobs ADD COLUMN cover_letter_evidence text;""")

    # Add column cover_letter_solution_angle to jobs
    migration_statements.append("""ALTER TABLE jobs ADD COLUMN cover_letter_solution_angle text;""")

    # Add column prestige_factor to jobs
    migration_statements.append("""ALTER TABLE jobs ADD COLUMN prestige_factor integer;""")

    # Add column prestige_reasoning to jobs
    migration_statements.append("""ALTER TABLE jobs ADD COLUMN prestige_reasoning text;""")

    # Add column supervision_count to jobs
    migration_statements.append("""ALTER TABLE jobs ADD COLUMN supervision_count integer;""")

    # Add column budget_size_category to jobs
    migration_statements.append("""ALTER TABLE jobs ADD COLUMN budget_size_category character varying;""")

    # Add column company_size_category to jobs
    migration_statements.append("""ALTER TABLE jobs ADD COLUMN company_size_category character varying;""")

    # Drop column requirements from jobs
    migration_statements.append("""ALTER TABLE jobs DROP COLUMN requirements;""")

    # Drop column salary_currency from jobs
    migration_statements.append("""ALTER TABLE jobs DROP COLUMN salary_currency;""")

    # Drop column location from jobs
    migration_statements.append("""ALTER TABLE jobs DROP COLUMN location;""")

    # Drop column experience_level from jobs
    migration_statements.append("""ALTER TABLE jobs DROP COLUMN experience_level;""")

    # Drop column reports_to from jobs
    migration_statements.append("""ALTER TABLE jobs DROP COLUMN reports_to;""")

    # Drop column team_size from jobs
    migration_statements.append("""ALTER TABLE jobs DROP COLUMN team_size;""")

    # Drop column career_path from jobs
    migration_statements.append("""ALTER TABLE jobs DROP COLUMN career_path;""")

    # Drop column skills_required from jobs
    migration_statements.append("""ALTER TABLE jobs DROP COLUMN skills_required;""")

    # Drop column benefits from jobs
    migration_statements.append("""ALTER TABLE jobs DROP COLUMN benefits;""")

    # Drop column priority_score from jobs
    migration_statements.append("""ALTER TABLE jobs DROP COLUMN priority_score;""")

    # Drop column platforms_found from jobs
    migration_statements.append("""ALTER TABLE jobs DROP COLUMN platforms_found;""")

    # Add column job_id to link_tracking
    migration_statements.append("""ALTER TABLE link_tracking ADD COLUMN job_id uuid;""")

    # Add column application_id to link_tracking
    migration_statements.append("""ALTER TABLE link_tracking ADD COLUMN application_id uuid;""")

    # Add column link_function to link_tracking
    migration_statements.append("""ALTER TABLE link_tracking ADD COLUMN link_function character varying;""")

    # Add column redirect_url to link_tracking
    migration_statements.append("""ALTER TABLE link_tracking ADD COLUMN redirect_url character varying;""")

    # Add column created_at to link_tracking
    migration_statements.append("""ALTER TABLE link_tracking ADD COLUMN created_at timestamp without time zone;""")

    # Add column created_by to link_tracking
    migration_statements.append("""ALTER TABLE link_tracking ADD COLUMN created_by character varying;""")

    # Add column is_active to link_tracking
    migration_statements.append("""ALTER TABLE link_tracking ADD COLUMN is_active boolean;""")

    # Add column description to link_tracking
    migration_statements.append("""ALTER TABLE link_tracking ADD COLUMN description text;""")

    # Add column content_text to sentence_bank_cover_letter
    migration_statements.append("""ALTER TABLE sentence_bank_cover_letter ADD COLUMN content_text text;""")

    # Add column status to sentence_bank_cover_letter
    migration_statements.append("""ALTER TABLE sentence_bank_cover_letter ADD COLUMN status character varying;""")

    # Add column matches_job_skill to sentence_bank_cover_letter
    migration_statements.append("""ALTER TABLE sentence_bank_cover_letter ADD COLUMN matches_job_skill character varying;""")

    # Add column variable to sentence_bank_cover_letter
    migration_statements.append("""ALTER TABLE sentence_bank_cover_letter ADD COLUMN variable boolean;""")

    # Add column keyword_filter_status to sentence_bank_cover_letter
    migration_statements.append("""ALTER TABLE sentence_bank_cover_letter ADD COLUMN keyword_filter_status character varying;""")

    # Add column keyword_filter_date to sentence_bank_cover_letter
    migration_statements.append("""ALTER TABLE sentence_bank_cover_letter ADD COLUMN keyword_filter_date date;""")

    # Add column keyword_filter_error_message to sentence_bank_cover_letter
    migration_statements.append("""ALTER TABLE sentence_bank_cover_letter ADD COLUMN keyword_filter_error_message text;""")

    # Add column truthfulness_status to sentence_bank_cover_letter
    migration_statements.append("""ALTER TABLE sentence_bank_cover_letter ADD COLUMN truthfulness_status character varying;""")

    # Add column truthfulness_date to sentence_bank_cover_letter
    migration_statements.append("""ALTER TABLE sentence_bank_cover_letter ADD COLUMN truthfulness_date date;""")

    # Add column truthfulness_model to sentence_bank_cover_letter
    migration_statements.append("""ALTER TABLE sentence_bank_cover_letter ADD COLUMN truthfulness_model character varying;""")

    # Add column truthfulness_error_message to sentence_bank_cover_letter
    migration_statements.append("""ALTER TABLE sentence_bank_cover_letter ADD COLUMN truthfulness_error_message text;""")

    # Add column canadian_spelling_status to sentence_bank_cover_letter
    migration_statements.append("""ALTER TABLE sentence_bank_cover_letter ADD COLUMN canadian_spelling_status character varying;""")

    # Add column canadian_spelling_date to sentence_bank_cover_letter
    migration_statements.append("""ALTER TABLE sentence_bank_cover_letter ADD COLUMN canadian_spelling_date date;""")

    # Add column tone_analysis_status to sentence_bank_cover_letter
    migration_statements.append("""ALTER TABLE sentence_bank_cover_letter ADD COLUMN tone_analysis_status character varying;""")

    # Add column tone_analysis_date to sentence_bank_cover_letter
    migration_statements.append("""ALTER TABLE sentence_bank_cover_letter ADD COLUMN tone_analysis_date date;""")

    # Add column tone_analysis_model to sentence_bank_cover_letter
    migration_statements.append("""ALTER TABLE sentence_bank_cover_letter ADD COLUMN tone_analysis_model character varying;""")

    # Add column tone_analysis_error_message to sentence_bank_cover_letter
    migration_statements.append("""ALTER TABLE sentence_bank_cover_letter ADD COLUMN tone_analysis_error_message text;""")

    # Add column skill_analysis_status to sentence_bank_cover_letter
    migration_statements.append("""ALTER TABLE sentence_bank_cover_letter ADD COLUMN skill_analysis_status character varying;""")

    # Add column skill_analysis_date to sentence_bank_cover_letter
    migration_statements.append("""ALTER TABLE sentence_bank_cover_letter ADD COLUMN skill_analysis_date date;""")

    # Add column skill_analysis_model to sentence_bank_cover_letter
    migration_statements.append("""ALTER TABLE sentence_bank_cover_letter ADD COLUMN skill_analysis_model character varying;""")

    # Add column skill_analysis_error_message to sentence_bank_cover_letter
    migration_statements.append("""ALTER TABLE sentence_bank_cover_letter ADD COLUMN skill_analysis_error_message text;""")

    # Drop column text from sentence_bank_cover_letter
    migration_statements.append("""ALTER TABLE sentence_bank_cover_letter DROP COLUMN text;""")

    # Drop column category from sentence_bank_cover_letter
    migration_statements.append("""ALTER TABLE sentence_bank_cover_letter DROP COLUMN category;""")

    # Drop column tags from sentence_bank_cover_letter
    migration_statements.append("""ALTER TABLE sentence_bank_cover_letter DROP COLUMN tags;""")

    # Drop column matches_job_attributes from sentence_bank_cover_letter
    migration_statements.append("""ALTER TABLE sentence_bank_cover_letter DROP COLUMN matches_job_attributes;""")

    # Drop column length from sentence_bank_cover_letter
    migration_statements.append("""ALTER TABLE sentence_bank_cover_letter DROP COLUMN length;""")

    # Drop column stage from sentence_bank_cover_letter
    migration_statements.append("""ALTER TABLE sentence_bank_cover_letter DROP COLUMN stage;""")

    # Drop column sentence_strength from sentence_bank_cover_letter
    migration_statements.append("""ALTER TABLE sentence_bank_cover_letter DROP COLUMN sentence_strength;""")

    # Add column content_text to sentence_bank_resume
    migration_statements.append("""ALTER TABLE sentence_bank_resume ADD COLUMN content_text text;""")

    # Add column body_section to sentence_bank_resume
    migration_statements.append("""ALTER TABLE sentence_bank_resume ADD COLUMN body_section character varying;""")

    # Add column status to sentence_bank_resume
    migration_statements.append("""ALTER TABLE sentence_bank_resume ADD COLUMN status character varying;""")

    # Add column matches_job_skill to sentence_bank_resume
    migration_statements.append("""ALTER TABLE sentence_bank_resume ADD COLUMN matches_job_skill character varying;""")

    # Add column experience_id to sentence_bank_resume
    migration_statements.append("""ALTER TABLE sentence_bank_resume ADD COLUMN experience_id uuid;""")

    # Add column keyword_filter_status to sentence_bank_resume
    migration_statements.append("""ALTER TABLE sentence_bank_resume ADD COLUMN keyword_filter_status character varying;""")

    # Add column keyword_filter_date to sentence_bank_resume
    migration_statements.append("""ALTER TABLE sentence_bank_resume ADD COLUMN keyword_filter_date date;""")

    # Add column keyword_filter_error_message to sentence_bank_resume
    migration_statements.append("""ALTER TABLE sentence_bank_resume ADD COLUMN keyword_filter_error_message text;""")

    # Add column truthfulness_status to sentence_bank_resume
    migration_statements.append("""ALTER TABLE sentence_bank_resume ADD COLUMN truthfulness_status character varying;""")

    # Add column truthfulness_date to sentence_bank_resume
    migration_statements.append("""ALTER TABLE sentence_bank_resume ADD COLUMN truthfulness_date date;""")

    # Add column truthfulness_model to sentence_bank_resume
    migration_statements.append("""ALTER TABLE sentence_bank_resume ADD COLUMN truthfulness_model character varying;""")

    # Add column truthfulness_error_message to sentence_bank_resume
    migration_statements.append("""ALTER TABLE sentence_bank_resume ADD COLUMN truthfulness_error_message text;""")

    # Add column canadian_spelling_status to sentence_bank_resume
    migration_statements.append("""ALTER TABLE sentence_bank_resume ADD COLUMN canadian_spelling_status character varying;""")

    # Add column canadian_spelling_date to sentence_bank_resume
    migration_statements.append("""ALTER TABLE sentence_bank_resume ADD COLUMN canadian_spelling_date date;""")

    # Add column tone_analysis_status to sentence_bank_resume
    migration_statements.append("""ALTER TABLE sentence_bank_resume ADD COLUMN tone_analysis_status character varying;""")

    # Add column tone_analysis_date to sentence_bank_resume
    migration_statements.append("""ALTER TABLE sentence_bank_resume ADD COLUMN tone_analysis_date date;""")

    # Add column tone_analysis_model to sentence_bank_resume
    migration_statements.append("""ALTER TABLE sentence_bank_resume ADD COLUMN tone_analysis_model character varying;""")

    # Add column tone_analysis_error_message to sentence_bank_resume
    migration_statements.append("""ALTER TABLE sentence_bank_resume ADD COLUMN tone_analysis_error_message text;""")

    # Add column skill_analysis_status to sentence_bank_resume
    migration_statements.append("""ALTER TABLE sentence_bank_resume ADD COLUMN skill_analysis_status character varying;""")

    # Add column skill_analysis_date to sentence_bank_resume
    migration_statements.append("""ALTER TABLE sentence_bank_resume ADD COLUMN skill_analysis_date date;""")

    # Add column skill_analysis_model to sentence_bank_resume
    migration_statements.append("""ALTER TABLE sentence_bank_resume ADD COLUMN skill_analysis_model character varying;""")

    # Add column skill_analysis_error_message to sentence_bank_resume
    migration_statements.append("""ALTER TABLE sentence_bank_resume ADD COLUMN skill_analysis_error_message text;""")

    # Drop column text from sentence_bank_resume
    migration_statements.append("""ALTER TABLE sentence_bank_resume DROP COLUMN text;""")

    # Drop column category from sentence_bank_resume
    migration_statements.append("""ALTER TABLE sentence_bank_resume DROP COLUMN category;""")

    # Drop column tags from sentence_bank_resume
    migration_statements.append("""ALTER TABLE sentence_bank_resume DROP COLUMN tags;""")

    # Drop column matches_job_attributes from sentence_bank_resume
    migration_statements.append("""ALTER TABLE sentence_bank_resume DROP COLUMN matches_job_attributes;""")

    # Drop column length from sentence_bank_resume
    migration_statements.append("""ALTER TABLE sentence_bank_resume DROP COLUMN length;""")

    # Drop column stage from sentence_bank_resume
    migration_statements.append("""ALTER TABLE sentence_bank_resume DROP COLUMN stage;""")

    # Drop column position_label from sentence_bank_resume
    migration_statements.append("""ALTER TABLE sentence_bank_resume DROP COLUMN position_label;""")

    # Drop column sentence_strength from sentence_bank_resume
    migration_statements.append("""ALTER TABLE sentence_bank_resume DROP COLUMN sentence_strength;""")

    # Add column candidate_id to user_job_preferences
    migration_statements.append("""ALTER TABLE user_job_preferences ADD COLUMN candidate_id uuid;""")

    # Drop column preferred_industries from user_job_preferences
    migration_statements.append("""ALTER TABLE user_job_preferences DROP COLUMN preferred_industries;""")

    # Drop column excluded_industries from user_job_preferences
    migration_statements.append("""ALTER TABLE user_job_preferences DROP COLUMN excluded_industries;""")


    # Execute migrations
    for statement in migration_statements:
        try:
            db.execute(text(statement))
            print(f"Executed: {statement[:50]}...")
        except Exception as e:
            print(f"Error executing migration: {e}")
            print(f"Statement: {statement}")
            raise
    
    db.commit()
    print("Migration completed successfully!")

