-- Database Schema Archive
-- This file contains database schemas for future reference

-- RAW JOB SCRAPES TABLE (ACTIVE)
-- Stores all scraped job data with no modifications
-- Everything that gets scraped goes here first
CREATE TABLE IF NOT EXISTS raw_job_scrapes (
    scrape_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_website VARCHAR(255) NOT NULL,
    source_url TEXT NOT NULL,
    full_application_url TEXT,
    scrape_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    raw_data JSONB NOT NULL,
    scraper_used VARCHAR(100),
    scraper_run_id VARCHAR(255),
    user_agent TEXT,
    ip_address VARCHAR(45),
    success_status BOOLEAN DEFAULT TRUE,
    error_message TEXT,
    response_time_ms INTEGER,
    data_size_bytes INTEGER
);

-- CLEANED JOB SCRAPES TABLE (ACTIVE)
-- Cleaned and deduplicated version that feeds into jobs table
CREATE TABLE IF NOT EXISTS cleaned_job_scrapes (
    cleaned_job_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    original_scrape_ids UUID[] NOT NULL,
    job_title VARCHAR(500),
    company_name VARCHAR(300),
    location_raw TEXT,
    location_city VARCHAR(100),
    location_province VARCHAR(100),
    location_country VARCHAR(100),
    work_arrangement VARCHAR(50),
    salary_raw TEXT,
    salary_min INTEGER,
    salary_max INTEGER,
    salary_currency VARCHAR(10),
    salary_period VARCHAR(20),
    job_description TEXT,
    requirements TEXT,
    benefits TEXT,
    company_description TEXT,
    industry VARCHAR(100),
    job_type VARCHAR(50),
    experience_level VARCHAR(50),
    posting_date DATE,
    application_deadline DATE,
    external_job_id VARCHAR(255),
    source_website VARCHAR(255) NOT NULL,
    application_url TEXT,
    company_website TEXT,
    company_logo_url TEXT,
    reviews_count INTEGER,
    company_rating DECIMAL(3,2),
    is_expired BOOLEAN DEFAULT FALSE,
    duplicates_count INTEGER DEFAULT 1,
    confidence_score DECIMAL(5,4),
    cleaned_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_seen_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processing_notes TEXT
);

-- SECURITY LOGS TABLE (ACTIVE)
-- Tracks security events and potential threats
CREATE TABLE IF NOT EXISTS security_logs (
    log_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_type VARCHAR(100) NOT NULL,
    details JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    severity VARCHAR(20) DEFAULT 'INFO',
    source_ip VARCHAR(45),
    user_agent TEXT,
    resolved BOOLEAN DEFAULT FALSE
);

-- Alternative Schema: Job ID provided by Make.com
-- (Kept for potential future use)

/*
CREATE TABLE document_jobs (
    job_id VARCHAR(255) PRIMARY KEY,
    file_path VARCHAR(500),
    filename VARCHAR(255),
    webhook_data JSONB,
    status VARCHAR(50) DEFAULT 'processing',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    file_size INTEGER,
    title VARCHAR(255),
    author VARCHAR(255),
    has_error BOOLEAN DEFAULT FALSE,
    error_code VARCHAR(100),
    error_message TEXT,
    error_details JSONB
);

-- Key difference: job_id is VARCHAR provided by Make.com instead of auto-generated UUID
-- Required webhook fields would include: 'title', 'content', 'job_id'
*/

-- Current Schema: Auto-generated UUID job_id (see replit.md for active schema)