-- Additional Database Normalization
-- Normalize remaining JSONB and array columns for better data integrity

-- 1. NORMALIZE document_tone_analysis.sentences JSONB column
CREATE TABLE document_sentences (
    sentence_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_job_id UUID REFERENCES document_jobs(job_id) ON DELETE CASCADE,
    sentence_text TEXT NOT NULL,
    tone_score DECIMAL(3,2) CHECK (tone_score >= 0.0 AND tone_score <= 1.0),
    sentiment_category VARCHAR(20) CHECK (sentiment_category IN ('positive', 'negative', 'neutral')),
    confidence_score DECIMAL(3,2) CHECK (confidence_score >= 0.0 AND confidence_score <= 1.0),
    word_count INTEGER,
    sentence_order INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(document_job_id, sentence_order)
);

-- 2. NORMALIZE job_applications.tracking_data JSONB column
CREATE TABLE job_application_tracking (
    tracking_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_application_id UUID REFERENCES job_applications(application_id) ON DELETE CASCADE,
    tracking_type VARCHAR(50) NOT NULL, -- 'email_open', 'link_click', 'document_download', etc.
    tracking_event VARCHAR(100) NOT NULL,
    event_timestamp TIMESTAMP NOT NULL,
    event_data JSONB, -- Only for complex event metadata that doesn't warrant its own table
    ip_address INET,
    user_agent TEXT,
    
    INDEX ON (job_application_id, event_timestamp),
    INDEX ON (tracking_type, event_timestamp)
);

-- 3. NORMALIZE job_applications.documents_sent array
CREATE TABLE job_application_documents (
    document_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_application_id UUID REFERENCES job_applications(application_id) ON DELETE CASCADE,
    document_type VARCHAR(30) NOT NULL CHECK (document_type IN ('resume', 'cover_letter', 'portfolio', 'transcript', 'references')),
    document_name VARCHAR(255) NOT NULL,
    file_path TEXT,
    file_size INTEGER,
    sent_timestamp TIMESTAMP NOT NULL,
    
    UNIQUE(job_application_id, document_type, document_name)
);

-- 4. NORMALIZE jobs.benefits array
CREATE TABLE job_benefits (
    benefit_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id UUID REFERENCES jobs(job_id) ON DELETE CASCADE,
    benefit_type VARCHAR(50) NOT NULL, -- 'health', 'dental', 'vision', 'retirement', 'pto', 'flexible_hours', etc.
    benefit_description TEXT,
    benefit_value VARCHAR(100), -- e.g., "100% coverage", "$500/year", "unlimited"
    
    UNIQUE(job_id, benefit_type)
);

-- 5. NORMALIZE jobs.skills_required array
CREATE TABLE job_required_skills (
    skill_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id UUID REFERENCES jobs(job_id) ON DELETE CASCADE,
    skill_name VARCHAR(100) NOT NULL,
    skill_level VARCHAR(20) CHECK (skill_level IN ('beginner', 'intermediate', 'advanced', 'expert')),
    is_required BOOLEAN DEFAULT TRUE,
    years_experience INTEGER,
    
    UNIQUE(job_id, skill_name)
);

-- 6. NORMALIZE jobs.platforms_found array
CREATE TABLE job_platforms (
    platform_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id UUID REFERENCES jobs(job_id) ON DELETE CASCADE,
    platform_name VARCHAR(100) NOT NULL, -- 'Indeed', 'LinkedIn', 'Glassdoor', etc.
    platform_url TEXT,
    first_found_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(job_id, platform_name)
);

-- 7. NORMALIZE sentence_bank_*.tags arrays
CREATE TABLE sentence_bank_tags (
    tag_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sentence_bank_id UUID NOT NULL, -- Will reference either resume or cover letter sentence
    sentence_bank_type VARCHAR(20) NOT NULL CHECK (sentence_bank_type IN ('resume', 'cover_letter')),
    tag_name VARCHAR(50) NOT NULL,
    tag_category VARCHAR(30), -- 'skill', 'industry', 'tone', 'format', etc.
    
    UNIQUE(sentence_bank_id, sentence_bank_type, tag_name)
);

-- 8. NORMALIZE sentence_bank_*.matches_job_attributes arrays
CREATE TABLE sentence_bank_job_attributes (
    attribute_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sentence_bank_id UUID NOT NULL,
    sentence_bank_type VARCHAR(20) NOT NULL CHECK (sentence_bank_type IN ('resume', 'cover_letter')),
    attribute_name VARCHAR(100) NOT NULL,
    attribute_value VARCHAR(200),
    match_strength DECIMAL(3,2) CHECK (match_strength >= 0.0 AND match_strength <= 1.0),
    
    UNIQUE(sentence_bank_id, sentence_bank_type, attribute_name)
);

-- 9. NORMALIZE user_job_preferences industry arrays
CREATE TABLE user_preferred_industries (
    preference_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES user_job_preferences(user_id) ON DELETE CASCADE,
    industry_name VARCHAR(100) NOT NULL,
    preference_type VARCHAR(20) NOT NULL CHECK (preference_type IN ('preferred', 'excluded')),
    priority_level INTEGER CHECK (priority_level >= 1 AND priority_level <= 10),
    
    UNIQUE(user_id, industry_name, preference_type)
);

-- 10. NORMALIZE cleaned_job_scrapes.original_scrape_ids array
CREATE TABLE cleaned_job_scrape_sources (
    source_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cleaned_job_id UUID REFERENCES cleaned_job_scrapes(cleaned_job_id) ON DELETE CASCADE,
    original_scrape_id UUID NOT NULL,
    source_priority INTEGER, -- For tracking which source was considered "best"
    merge_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(cleaned_job_id, original_scrape_id)
);

-- Create indexes for better query performance
CREATE INDEX idx_document_sentences_job_id ON document_sentences(document_job_id);
CREATE INDEX idx_document_sentences_tone_score ON document_sentences(tone_score DESC);

CREATE INDEX idx_job_application_tracking_app_id ON job_application_tracking(job_application_id);
CREATE INDEX idx_job_application_tracking_type ON job_application_tracking(tracking_type);
CREATE INDEX idx_job_application_tracking_timestamp ON job_application_tracking(event_timestamp DESC);

CREATE INDEX idx_job_application_documents_app_id ON job_application_documents(job_application_id);
CREATE INDEX idx_job_application_documents_type ON job_application_documents(document_type);

CREATE INDEX idx_job_benefits_job_id ON job_benefits(job_id);
CREATE INDEX idx_job_benefits_type ON job_benefits(benefit_type);

CREATE INDEX idx_job_required_skills_job_id ON job_required_skills(job_id);
CREATE INDEX idx_job_required_skills_level ON job_required_skills(skill_level);
CREATE INDEX idx_job_required_skills_required ON job_required_skills(is_required);

CREATE INDEX idx_job_platforms_job_id ON job_platforms(job_id);
CREATE INDEX idx_job_platforms_name ON job_platforms(platform_name);

CREATE INDEX idx_sentence_bank_tags_id_type ON sentence_bank_tags(sentence_bank_id, sentence_bank_type);
CREATE INDEX idx_sentence_bank_tags_name ON sentence_bank_tags(tag_name);

CREATE INDEX idx_sentence_bank_attributes_id_type ON sentence_bank_job_attributes(sentence_bank_id, sentence_bank_type);
CREATE INDEX idx_sentence_bank_attributes_name ON sentence_bank_job_attributes(attribute_name);

CREATE INDEX idx_user_preferred_industries_user_id ON user_preferred_industries(user_id);
CREATE INDEX idx_user_preferred_industries_type ON user_preferred_industries(preference_type);

CREATE INDEX idx_cleaned_job_scrape_sources_cleaned_id ON cleaned_job_scrape_sources(cleaned_job_id);
CREATE INDEX idx_cleaned_job_scrape_sources_original_id ON cleaned_job_scrape_sources(original_scrape_id);

-- Comments for documentation
COMMENT ON TABLE document_sentences IS 'Individual sentences from document tone analysis with scores';
COMMENT ON TABLE job_application_tracking IS 'Tracking events for job applications (emails, clicks, downloads)';
COMMENT ON TABLE job_application_documents IS 'Documents sent with each job application';
COMMENT ON TABLE job_benefits IS 'Benefits offered by job postings';
COMMENT ON TABLE job_required_skills IS 'Skills required for job postings';
COMMENT ON TABLE job_platforms IS 'Platforms where job postings were found';
COMMENT ON TABLE sentence_bank_tags IS 'Tags associated with sentence bank entries';
COMMENT ON TABLE sentence_bank_job_attributes IS 'Job attributes that sentence bank entries match';
COMMENT ON TABLE user_preferred_industries IS 'User industry preferences (preferred and excluded)';
COMMENT ON TABLE cleaned_job_scrape_sources IS 'Original raw scrape sources for cleaned job records';