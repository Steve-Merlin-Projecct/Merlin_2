-- Normalized Database Schema for AI Job Analysis
-- Replaces the JSONB approach with proper relational tables

-- 1. Main job analysis table (normalized from job_content_analysis)
CREATE TABLE job_analysis (
    job_id UUID PRIMARY KEY REFERENCES cleaned_job_scrapes(cleaned_job_id),
    analysis_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    model_used VARCHAR(100),
    analysis_version VARCHAR(20),
    
    -- Authenticity Check (single values)
    is_authentic BOOLEAN,
    authenticity_confidence_score INTEGER CHECK (authenticity_confidence_score >= 0 AND authenticity_confidence_score <= 100),
    title_match_score INTEGER CHECK (title_match_score >= 0 AND title_match_score <= 100),
    authenticity_reasoning TEXT,
    
    -- Industry Classification (single values)
    primary_industry VARCHAR(100),
    job_function VARCHAR(100),
    seniority_level VARCHAR(50),
    industry_confidence INTEGER CHECK (industry_confidence >= 0 AND industry_confidence <= 100),
    
    -- Additional Insights (single values)
    salary_transparency VARCHAR(20) CHECK (salary_transparency IN ('explicit', 'implied', 'none')),
    company_size_indicator VARCHAR(20) CHECK (company_size_indicator IN ('startup', 'small', 'medium', 'large', 'enterprise')),
    growth_opportunity VARCHAR(20) CHECK (growth_opportunity IN ('low', 'medium', 'high')),
    work_arrangement VARCHAR(20) CHECK (work_arrangement IN ('remote', 'hybrid', 'onsite')),
    
    -- Structured Data (from additional_insights.structured_data)
    estimated_salary_min INTEGER,
    estimated_salary_max INTEGER,
    salary_currency VARCHAR(3) DEFAULT 'CAD',
    work_hours_per_week INTEGER,
    overtime_expected BOOLEAN,
    remote_work_percentage INTEGER CHECK (remote_work_percentage >= 0 AND remote_work_percentage <= 100),
    
    -- Stress Level Analysis
    stress_level_score INTEGER CHECK (stress_level_score >= 1 AND stress_level_score <= 10),
    workload_intensity VARCHAR(20) CHECK (workload_intensity IN ('low', 'moderate', 'high', 'extreme')),
    deadline_pressure VARCHAR(20) CHECK (deadline_pressure IN ('low', 'moderate', 'high', 'extreme')),
    
    -- Metrics
    total_skills_found INTEGER DEFAULT 0,
    
    UNIQUE(job_id)
);

-- 2. Skills analysis (normalized from skills_analysis JSONB)
CREATE TABLE job_skills (
    skill_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id UUID REFERENCES job_analysis(job_id) ON DELETE CASCADE,
    skill_name VARCHAR(100) NOT NULL,
    importance_rating INTEGER CHECK (importance_rating >= 1 AND importance_rating <= 100),
    skill_category VARCHAR(20) CHECK (skill_category IN ('technical', 'soft', 'industry')),
    is_required BOOLEAN DEFAULT FALSE,
    years_experience INTEGER,
    
    UNIQUE(job_id, skill_name)
);

-- 3. Secondary industries (normalized from industry_classification.secondary_industries)
CREATE TABLE job_secondary_industries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id UUID REFERENCES job_analysis(job_id) ON DELETE CASCADE,
    industry_name VARCHAR(100) NOT NULL,
    
    UNIQUE(job_id, industry_name)
);

-- 4. Authenticity red flags (normalized from authenticity_check.red_flags)
CREATE TABLE job_authenticity_red_flags (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id UUID REFERENCES job_analysis(job_id) ON DELETE CASCADE,
    red_flag_type VARCHAR(100) NOT NULL,
    red_flag_description TEXT,
    
    UNIQUE(job_id, red_flag_type)
);

-- 5. Implicit requirements (normalized from additional_insights.implicit_requirements)
CREATE TABLE job_implicit_requirements (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id UUID REFERENCES job_analysis(job_id) ON DELETE CASCADE,
    requirement_type VARCHAR(50) NOT NULL,
    requirement_description TEXT NOT NULL,
    importance_level VARCHAR(20) CHECK (importance_level IN ('low', 'medium', 'high', 'critical')),
    
    UNIQUE(job_id, requirement_type)
);

-- 6. Cover letter insights (normalized from additional_insights.cover_letter_insights)
CREATE TABLE job_cover_letter_insights (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id UUID REFERENCES job_analysis(job_id) ON DELETE CASCADE,
    insight_type VARCHAR(50) NOT NULL,
    insight_description TEXT NOT NULL,
    strategic_value VARCHAR(20) CHECK (strategic_value IN ('low', 'medium', 'high')),
    
    UNIQUE(job_id, insight_type)
);

-- 7. ATS optimization keywords (normalized from additional_insights.structured_data.ats_optimization)
CREATE TABLE job_ats_keywords (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id UUID REFERENCES job_analysis(job_id) ON DELETE CASCADE,
    keyword VARCHAR(100) NOT NULL,
    keyword_category VARCHAR(30) CHECK (keyword_category IN ('critical', 'important', 'supplementary')),
    frequency_in_posting INTEGER DEFAULT 1,
    
    UNIQUE(job_id, keyword)
);

-- 8. General red flags (normalized from additional_insights.red_flags)
CREATE TABLE job_red_flags (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id UUID REFERENCES job_analysis(job_id) ON DELETE CASCADE,
    flag_category VARCHAR(50) NOT NULL,
    flag_description TEXT NOT NULL,
    severity_level VARCHAR(20) CHECK (severity_level IN ('low', 'medium', 'high', 'critical')),
    
    UNIQUE(job_id, flag_category)
);

-- Create indexes for better query performance
CREATE INDEX idx_job_analysis_timestamp ON job_analysis(analysis_timestamp);
CREATE INDEX idx_job_analysis_industry ON job_analysis(primary_industry);
CREATE INDEX idx_job_analysis_seniority ON job_analysis(seniority_level);
CREATE INDEX idx_job_analysis_work_arrangement ON job_analysis(work_arrangement);
CREATE INDEX idx_job_analysis_salary_range ON job_analysis(estimated_salary_min, estimated_salary_max);

CREATE INDEX idx_job_skills_importance ON job_skills(importance_rating DESC);
CREATE INDEX idx_job_skills_category ON job_skills(skill_category);
CREATE INDEX idx_job_skills_required ON job_skills(is_required);

CREATE INDEX idx_job_ats_keywords_category ON job_ats_keywords(keyword_category);
CREATE INDEX idx_job_implicit_requirements_importance ON job_implicit_requirements(importance_level);
CREATE INDEX idx_job_red_flags_severity ON job_red_flags(severity_level);

-- Migration helper: Function to extract data from existing JSONB columns
CREATE OR REPLACE FUNCTION migrate_jsonb_to_normalized()
RETURNS TABLE(migrated_count INTEGER) AS $$
DECLARE
    job_record RECORD;
    skill_record RECORD;
    industry_record RECORD;
    migrated_jobs INTEGER := 0;
BEGIN
    -- This function can be used to migrate existing JSONB data to normalized tables
    -- Implementation would go here based on existing data structure
    RETURN QUERY SELECT migrated_jobs;
END;
$$ LANGUAGE plpgsql;

-- Comments explaining the normalization
COMMENT ON TABLE job_analysis IS 'Main job analysis table with normalized single-value fields from AI analysis';
COMMENT ON TABLE job_skills IS 'Individual skills extracted from job postings with importance ratings';
COMMENT ON TABLE job_secondary_industries IS 'Additional industries associated with job postings';
COMMENT ON TABLE job_authenticity_red_flags IS 'Specific red flags identified in authenticity checking';
COMMENT ON TABLE job_implicit_requirements IS 'Unstated requirements identified by AI analysis';
COMMENT ON TABLE job_cover_letter_insights IS 'Strategic insights for cover letter writing';
COMMENT ON TABLE job_ats_keywords IS 'ATS-optimized keywords for job applications';
COMMENT ON TABLE job_red_flags IS 'General red flags and concerns about job postings';