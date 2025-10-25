"""
Database Migration Script
Generated on 2025-10-24 02:33:15
"""

from sqlalchemy import text
from sqlalchemy.orm import Session

def migrate_database(db: Session):
    """
    Apply database schema changes
    """
    migration_statements = []
    
    # Create new table: apify_application_submissions
    migration_statements.append("""
CREATE TABLE apify_application_submissions (
    submission_id uuid NOT NULL DEFAULT gen_random_uuid(),
    application_id character varying(255),
    job_id character varying(255) NOT NULL,
    actor_run_id character varying(255),
    status character varying(50) NOT NULL DEFAULT 'pending'::character varying,
    form_platform character varying(50) NOT NULL,
    form_type character varying(100),
    fields_filled jsonb,
    submission_confirmed boolean DEFAULT false,
    confirmation_message text,
    screenshot_urls jsonb,
    screenshot_metadata jsonb,
    error_message text,
    error_details jsonb,
    submitted_at timestamp without time zone NOT NULL DEFAULT now(),
    reviewed_at timestamp without time zone,
    created_at timestamp without time zone NOT NULL DEFAULT now(),
    updated_at timestamp without time zone NOT NULL DEFAULT now(),
    reviewed_by character varying(255),
    review_notes text,
    PRIMARY KEY (submission_id)
);    """)

    # Create new table: dashboard_metrics_daily
    migration_statements.append("""
CREATE TABLE dashboard_metrics_daily (
    id uuid NOT NULL DEFAULT gen_random_uuid(),
    metric_date date NOT NULL,
    jobs_scraped_count integer DEFAULT 0,
    jobs_cleaned_count integer DEFAULT 0,
    jobs_deduplicated_count integer DEFAULT 0,
    scraping_errors_count integer DEFAULT 0,
    scraping_avg_duration_ms integer DEFAULT 0,
    scraping_peak_hour integer,
    jobs_analyzed_count integer DEFAULT 0,
    ai_requests_sent integer DEFAULT 0,
    ai_tokens_input integer DEFAULT 0,
    ai_tokens_output integer DEFAULT 0,
    ai_cost_incurred numeric DEFAULT 0.00,
    ai_avg_duration_ms integer DEFAULT 0,
    ai_model_used character varying(100),
    applications_sent_count integer DEFAULT 0,
    applications_success_count integer DEFAULT 0,
    applications_failed_count integer DEFAULT 0,
    documents_generated_count integer DEFAULT 0,
    application_avg_duration_ms integer DEFAULT 0,
    success_rate numeric DEFAULT 0.00,
    pipeline_conversion_rate numeric DEFAULT 0.00,
    pipeline_bottleneck character varying(50),
    total_pipeline_jobs integer DEFAULT 0,
    jobs_trend_pct numeric DEFAULT 0.00,
    applications_trend_pct numeric DEFAULT 0.00,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id)
);    """)

    # Create new table: dashboard_metrics_hourly
    migration_statements.append("""
CREATE TABLE dashboard_metrics_hourly (
    id uuid NOT NULL DEFAULT gen_random_uuid(),
    metric_hour timestamp without time zone NOT NULL,
    jobs_scraped_count integer DEFAULT 0,
    jobs_cleaned_count integer DEFAULT 0,
    jobs_deduplicated_count integer DEFAULT 0,
    scraping_errors_count integer DEFAULT 0,
    scraping_avg_duration_ms integer DEFAULT 0,
    jobs_analyzed_count integer DEFAULT 0,
    ai_requests_sent integer DEFAULT 0,
    ai_tokens_input integer DEFAULT 0,
    ai_tokens_output integer DEFAULT 0,
    ai_cost_incurred numeric DEFAULT 0.00,
    ai_avg_duration_ms integer DEFAULT 0,
    applications_sent_count integer DEFAULT 0,
    applications_success_count integer DEFAULT 0,
    applications_failed_count integer DEFAULT 0,
    documents_generated_count integer DEFAULT 0,
    application_avg_duration_ms integer DEFAULT 0,
    pipeline_conversion_rate numeric DEFAULT 0.00,
    pipeline_bottleneck character varying(50),
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id)
);    """)

    # Create new table: job_analysis_tiers
    migration_statements.append("""
CREATE TABLE job_analysis_tiers (
    id uuid NOT NULL DEFAULT gen_random_uuid(),
    job_id uuid NOT NULL,
    tier_1_completed boolean DEFAULT false,
    tier_1_timestamp timestamp without time zone,
    tier_1_tokens_used integer,
    tier_1_model character varying(50),
    tier_1_response_time_ms integer,
    tier_2_completed boolean DEFAULT false,
    tier_2_timestamp timestamp without time zone,
    tier_2_tokens_used integer,
    tier_2_model character varying(50),
    tier_2_response_time_ms integer,
    tier_3_completed boolean DEFAULT false,
    tier_3_timestamp timestamp without time zone,
    tier_3_tokens_used integer,
    tier_3_model character varying(50),
    tier_3_response_time_ms integer,
    created_at timestamp without time zone DEFAULT now(),
    updated_at timestamp without time zone DEFAULT now(),
    FOREIGN KEY (job_id) REFERENCES jobs(id),
    PRIMARY KEY (id)
);    """)

    # Create new table: security_detections
    migration_statements.append("""
CREATE TABLE security_detections (
    id uuid NOT NULL DEFAULT gen_random_uuid(),
    job_id uuid,
    detection_type character varying(50) NOT NULL,
    severity character varying(20) NOT NULL,
    pattern_matched text,
    text_sample text,
    metadata jsonb,
    detected_at timestamp without time zone DEFAULT now(),
    handled boolean DEFAULT false,
    action_taken character varying(100),
    FOREIGN KEY (job_id) REFERENCES jobs(id),
    PRIMARY KEY (id)
);    """)


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

