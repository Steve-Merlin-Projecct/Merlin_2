---
title: "Projectoverview 1751526150641"
type: technical_doc
component: general
status: draft
tags: []
---



User: I don't want salary ranges, I want the low and the high stored as separate columns.
I want one table for all the raw scrapes of job desccriptions, per source platform, another table for the unique jobs per platform, and another table that will consolidate all of the job records into a single job record. That single job record needs the lowest and highest salary, across all platforms.
I want more information about the jobs and the companies: what industry, is supervisor? the url source etc.
for job analysis I want to know which career path

Perfect! Now the database structure supports your three-tier job architecture:

**Key Improvements:**

1. **Three-Tier Job Structure:**
   - `job_scrapes_raw`: Every single scrape with raw HTML and platform-specific data
   - `jobs_per_platform`: Deduplicated jobs within each platform
   - `jobs`: Consolidated single record per unique job with best salary ranges

2. **Separate Salary Columns:** `salary_low` and `salary_high` as integers for easy comparison and aggregation

3. **Enhanced Company Information:** Industry details, employee counts, company URLs, founding info, etc.

4. **Rich Job Details:** 
   - Supervisor status, team size, department
   - Career path and seniority level
   - Skills and benefits arrays
   - Source URLs and platform tracking

5. **Career Path Analysis:** Added to job_analyses table with career progression insights

6. **Smart Consolidation:** The `job_platform_mapping` table links consolidated jobs to their platform-specific versions with confidence scores

**Data Flow:**
1. Raw scrapes → `job_scrapes_raw` (everything captured)
2. Platform deduplication → `jobs_per_platform` (unique per platform)
3. Cross-platform consolidation → `jobs` (single record with min/max salary)
4. All your resume/cover letter/application logic operates on the consolidated `jobs` table

This structure gives you complete traceability from raw scrape to final application while maintaining the job-centric design you wanted. You can easily track which platforms had the best salary data and maintain data lineage throughout your entire workflow.

-- Enhanced company information
CREATE TABLE companies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    domain VARCHAR(255),
    industry VARCHAR(100),
    sub_industry VARCHAR(100),
    size_range VARCHAR(50),
    employee_count_min INTEGER,
    employee_count_max INTEGER,
    headquarters_location VARCHAR(255),
    founded_year INTEGER,
    company_type VARCHAR(50), -- Public, Private, Startup, Non-profit, etc.
    stock_symbol VARCHAR(10),
    revenue_range VARCHAR(100),
    company_url VARCHAR(500),
    linkedin_url VARCHAR(500),
    glassdoor_url VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Raw job scrapes per platform (all scraped data)
CREATE TABLE job_scrapes_raw (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_platform VARCHAR(100) NOT NULL, -- indeed, linkedin, glassdoor, etc.
    posting_url VARCHAR(500) NOT NULL,
    company_name VARCHAR(255),
    job_title VARCHAR(255),
    job_description TEXT,
    requirements TEXT,
    salary_low INTEGER,
    salary_high INTEGER,
    salary_currency VARCHAR(10) DEFAULT 'USD',
    salary_period VARCHAR(20), -- hourly, monthly, yearly
    location VARCHAR(255),
    remote_options VARCHAR(50),
    job_type VARCHAR(50), -- Full-time, Part-time, Contract, Internship
    experience_level VARCHAR(50), -- Entry, Mid, Senior, Executive
    is_supervisor BOOLEAN DEFAULT FALSE,
    reports_to VARCHAR(100),
    team_size VARCHAR(50),
    department VARCHAR(100),
    posted_date DATE,
    application_deadline DATE,
    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    hash_signature VARCHAR(64), -- for exact duplicate detection
    raw_html TEXT, -- original scraped content
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Unique jobs per platform (deduplicated within each platform)
CREATE TABLE jobs_per_platform (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_platform VARCHAR(100) NOT NULL,
    company_id UUID REFERENCES companies(id),
    job_title VARCHAR(255) NOT NULL,
    job_description TEXT,
    requirements TEXT,
    salary_low INTEGER,
    salary_high INTEGER,
    salary_currency VARCHAR(10) DEFAULT 'USD',
    salary_period VARCHAR(20),
    location VARCHAR(255),
    remote_options VARCHAR(50),
    job_type VARCHAR(50),
    experience_level VARCHAR(50),
    is_supervisor BOOLEAN DEFAULT FALSE,
    reports_to VARCHAR(100),
    team_size VARCHAR(50),
    department VARCHAR(100),
    industry VARCHAR(100),
    career_path VARCHAR(100), -- Software Engineering, Product Management, Data Science, etc.
    posting_url VARCHAR(500),
    posted_date DATE,
    application_deadline DATE,
    is_active BOOLEAN DEFAULT TRUE,
    similarity_hash VARCHAR(64), -- for cross-platform matching
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Consolidated jobs (single record per unique job across all platforms)
CREATE TABLE jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID REFERENCES companies(id),
    job_title VARCHAR(255) NOT NULL,
    job_description TEXT, -- merged/best description from all platforms
    requirements TEXT, -- merged/best requirements from all platforms
    salary_low INTEGER, -- lowest salary across all platforms
    salary_high INTEGER, -- highest salary across all platforms
    salary_currency VARCHAR(10) DEFAULT 'USD',
    salary_period VARCHAR(20),
    location VARCHAR(255),
    remote_options VARCHAR(50),
    job_type VARCHAR(50),
    experience_level VARCHAR(50),
    is_supervisor BOOLEAN DEFAULT FALSE,
    reports_to VARCHAR(100),
    team_size VARCHAR(50),
    department VARCHAR(100),
    industry VARCHAR(100),
    career_path VARCHAR(100), -- Software Engineering, Product Management, Data Science, etc.
    seniority_level VARCHAR(50), -- Junior, Mid, Senior, Staff, Principal, etc.
    skills_required TEXT[],
    benefits TEXT[],
    application_deadline DATE,
    is_active BOOLEAN DEFAULT TRUE,
    consolidation_confidence FLOAT, -- how confident we are this is the same job
    platforms_found TEXT[], -- which platforms this job was found on
    primary_source_url VARCHAR(500), -- best/primary posting URL
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Link jobs to their platform-specific versions
CREATE TABLE job_platform_mapping (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    consolidated_job_id UUID REFERENCES jobs(id),
    platform_job_id UUID REFERENCES jobs_per_platform(id),
    match_confidence FLOAT, -- how confident we are this is the same job
    is_primary_source BOOLEAN DEFAULT FALSE, -- which platform version is considered primary
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Skills extraction and matching
CREATE TABLE skills (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) UNIQUE NOT NULL,
    category VARCHAR(50), -- technical, soft, industry-specific
    synonyms TEXT[], -- alternative names for fuzzy matching
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE job_required_skills (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id UUID REFERENCES jobs(id),
    skill_id UUID REFERENCES skills(id),
    importance_score FLOAT, -- determined by LLM analysis
    mentioned_count INTEGER DEFAULT 1,
    context TEXT, -- how it was mentioned in the job description
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- User's experience, education and skills
CREATE TABLE user_experiences (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_name VARCHAR(255),
    position_title VARCHAR(255),
    start_date DATE,
    end_date DATE,
    description TEXT,
    achievements TEXT[],
    is_current BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE user_education (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    institution_name VARCHAR(255) NOT NULL,
    degree_type VARCHAR(100), -- Bachelor's, Master's, PhD, Certificate, etc.
    field_of_study VARCHAR(255),
    start_date DATE,
    end_date DATE,
    gpa DECIMAL(3,2),
    honors TEXT[],
    relevant_coursework TEXT[],
    is_current BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE user_certificates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    certificate_name VARCHAR(255) NOT NULL,
    issuing_organization VARCHAR(255),
    issue_date DATE,
    expiry_date DATE,
    certificate_url VARCHAR(500),
    verification_code VARCHAR(100),
    skill_tags TEXT[],
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE user_skills (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    skill_id UUID REFERENCES skills(id),
    proficiency_level INTEGER CHECK (proficiency_level >= 1 AND proficiency_level <= 5),
    years_experience FLOAT,
    last_used DATE,
    evidence_text TEXT, -- how this skill was demonstrated
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Sentence banks for content generation
CREATE TABLE sentence_bank_resume (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    text TEXT NOT NULL,
    category VARCHAR(100), -- Achievement, Skill, Responsibility, etc.
    tone VARCHAR(100), -- Bold/Insightful, Professional, Technical, etc.
    tags TEXT[], -- ["UX", "SaaS", "strategy", "design"]
    matches_job_attributes TEXT[], -- ["UX", "Customer Experience", "Product"]
    length VARCHAR(20) CHECK (length IN ('Short', 'Medium', 'Long')),
    stage VARCHAR(20) CHECK (stage IN ('Draft', 'Approved', 'Flagged')),
    position_label VARCHAR(100), -- Senior Developer, Product Manager, etc.
    sentence_strength INTEGER CHECK (sentence_strength >= 1 AND sentence_strength <= 10),
    intended_document VARCHAR(50) CHECK (intended_document IN ('resume', 'cover_letter', 'email')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE sentence_bank_cover_letter (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    text TEXT NOT NULL,
    category VARCHAR(100), -- Opening, Body, Closing, Flattery, etc.
    tone VARCHAR(100), -- Bold/Insightful, Professional, Technical, etc.
    tags TEXT[], -- ["UX", "SaaS", "strategy", "design"]
    matches_job_attributes TEXT[], -- ["UX", "Customer Experience", "Product"]
    length VARCHAR(20) CHECK (length IN ('Short', 'Medium', 'Long')),
    stage VARCHAR(20) CHECK (stage IN ('Draft', 'Approved', 'Flagged')),
    position_label VARCHAR(100), -- Senior Developer, Product Manager, etc.
    sentence_strength INTEGER CHECK (sentence_strength >= 1 AND sentence_strength <= 10),
    intended_document VARCHAR(50) CHECK (intended_document IN ('resume', 'cover_letter', 'email')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Resume generation and customization (Job-centric)
CREATE TABLE resume_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,
    template_data JSONB, -- structure and formatting info
    is_default BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE generated_resumes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id UUID REFERENCES jobs(id), -- Primary relationship to job
    template_id UUID REFERENCES resume_templates(id),
    customized_content JSONB, -- the actual resume content
    skill_order UUID[], -- array of skill_ids in priority order
    version INTEGER DEFAULT 1,
    tone_jump_score FLOAT, -- measures tone consistency
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Track individual resume components with unique tags
CREATE TABLE resume_components (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    resume_id UUID REFERENCES generated_resumes(id),
    component_type VARCHAR(50), -- linkedin_link, email, phone, skill, experience, etc.
    content TEXT,
    position_order INTEGER,
    unique_tag VARCHAR(100), -- each component gets unique identifier
    source_sentence_id UUID, -- references sentence_bank_resume(id) if applicable
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Cover letter generation (Job-centric)
CREATE TABLE generated_cover_letters (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id UUID REFERENCES jobs(id), -- Primary relationship to job
    content TEXT,
    version INTEGER DEFAULT 1,
    tone_jump_score FLOAT, -- measures tone consistency
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Track individual cover letter components
CREATE TABLE cover_letter_components (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cover_letter_id UUID REFERENCES generated_cover_letters(id),
    component_type VARCHAR(50), -- opening, body_paragraph, closing, etc.
    content TEXT,
    position_order INTEGER,
    unique_tag VARCHAR(100), -- each component gets unique identifier
    source_sentence_id UUID, -- references sentence_bank_cover_letter(id) if applicable
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Application tracking (Job-centric)
CREATE TABLE applications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id UUID REFERENCES jobs(id), -- Primary relationship to job
    resume_id UUID REFERENCES generated_resumes(id),
    cover_letter_id UUID REFERENCES generated_cover_letters(id),
    application_date DATE,
    platform VARCHAR(50), -- workday, greenhouse, etc.
    status VARCHAR(50) DEFAULT 'submitted', -- submitted, reviewed, interview, rejected, offer
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tracking links (Job-centric)
CREATE TABLE tracking_links (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id UUID REFERENCES jobs(id), -- Primary relationship to job
    application_id UUID REFERENCES applications(id),
    link_type VARCHAR(50), -- application_status, company_portal, etc.
    url VARCHAR(500),
    description TEXT,
    last_checked TIMESTAMP,
    status VARCHAR(50), -- active, expired, broken
    unique_tag VARCHAR(100), -- each link gets unique identifier
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Calendar and scheduling (Job-centric)
CREATE TABLE calendar_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id UUID REFERENCES jobs(id), -- Primary relationship to job
    application_id UUID REFERENCES applications(id),
    event_type VARCHAR(50), -- interview, deadline, follow-up
    title VARCHAR(255),
    description TEXT,
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    location VARCHAR(255),
    calendar_platform VARCHAR(50), -- google, outlook
    external_event_id VARCHAR(255),
    unique_tag VARCHAR(100), -- each event gets unique identifier
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- LLM analysis and insights (Job-centric)
CREATE TABLE job_analyses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id UUID REFERENCES jobs(id), -- Primary relationship to job
    analysis_type VARCHAR(50), -- skill_extraction, company_research, interview_prep, career_path_analysis
    career_path VARCHAR(100), -- Software Engineering, Product Management, Data Science, etc.
    career_level VARCHAR(50), -- Junior, Mid, Senior, Staff, Principal, etc.
    growth_potential VARCHAR(50), -- High, Medium, Low
    skill_alignment_score FLOAT, -- how well job aligns with user skills
    prompt_used TEXT,
    llm_response TEXT,
    confidence_score FLOAT,
    unique_tag VARCHAR(100), -- each analysis gets unique identifier
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Performance tracking and analytics (Job-centric)
CREATE TABLE job_performance_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id UUID REFERENCES jobs(id), -- Primary relationship to job
    application_id UUID REFERENCES applications(id),
    response_rate FLOAT,
    time_to_response INTERVAL,
    interview_conversion BOOLEAN DEFAULT FALSE,
    offer_conversion BOOLEAN DEFAULT FALSE,
    calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Interview preparation (Job-centric)
CREATE TABLE interview_prep_materials (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id UUID REFERENCES jobs(id), -- Primary relationship to job
    application_id UUID REFERENCES applications(id),
    company_research TEXT,
    potential_questions TEXT[],
    prepared_answers TEXT[],
    company_values TEXT[],
    recent_news TEXT[],
    unique_tag VARCHAR(100), -- each prep material gets unique identifier
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Deduplication tracking removed (replaced with platform mapping system)

-- Indexes for performance
CREATE INDEX idx_jobs_company ON jobs(company_id);
CREATE INDEX idx_jobs_active ON jobs(is_active);
CREATE INDEX idx_jobs_career_path ON jobs(career_path);
CREATE INDEX idx_jobs_salary_range ON jobs(salary_low, salary_high);
CREATE INDEX idx_job_scrapes_raw_platform ON job_scrapes_raw(source_platform);
CREATE INDEX idx_job_scrapes_raw_hash ON job_scrapes_raw(hash_signature);
CREATE INDEX idx_job_scrapes_raw_scraped_at ON job_scrapes_raw(scraped_at);
CREATE INDEX idx_jobs_per_platform_source ON jobs_per_platform(source_platform);
CREATE INDEX idx_jobs_per_platform_similarity ON jobs_per_platform(similarity_hash);
CREATE INDEX idx_jobs_per_platform_company ON jobs_per_platform(company_id);
CREATE INDEX idx_job_platform_mapping_consolidated ON job_platform_mapping(consolidated_job_id);
CREATE INDEX idx_job_platform_mapping_platform ON job_platform_mapping(platform_job_id);
CREATE INDEX idx_applications_job ON applications(job_id);
CREATE INDEX idx_applications_status ON applications(status);
CREATE INDEX idx_generated_resumes_job ON generated_resumes(job_id);
CREATE INDEX idx_generated_cover_letters_job ON generated_cover_letters(job_id);
CREATE INDEX idx_tracking_links_job ON tracking_links(job_id);
CREATE INDEX idx_calendar_events_job ON calendar_events(job_id);
CREATE INDEX idx_job_analyses_job ON job_analyses(job_id);
CREATE INDEX idx_job_analyses_career_path ON job_analyses(career_path);
CREATE INDEX idx_job_performance_metrics_job ON job_performance_metrics(job_id);
CREATE INDEX idx_interview_prep_materials_job ON interview_prep_materials(job_id);
CREATE INDEX idx_job_required_skills_job ON job_required_skills(job_id);
CREATE INDEX idx_job_required_skills_importance ON job_required_skills(importance_score DESC);
CREATE INDEX idx_sentence_bank_resume_stage ON sentence_bank_resume(stage);
CREATE INDEX idx_sentence_bank_cover_letter_stage ON sentence_bank_cover_letter(stage);
CREATE INDEX idx_resume_components_resume ON resume_components(resume_id);
CREATE INDEX idx_cover_letter_components_cover_letter ON cover_letter_components(cover_letter_id);