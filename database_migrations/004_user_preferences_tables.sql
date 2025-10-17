-- Migration 004: User Preferences System Tables
-- Created: 2025-10-12
-- Purpose: Multi-variable regression-based user preference system

-- Table: user_preference_scenarios
-- Stores user's input scenarios (1-5 per user) describing acceptable jobs
CREATE TABLE IF NOT EXISTS user_preference_scenarios (
    scenario_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id VARCHAR(100) NOT NULL,
    scenario_name VARCHAR(200),

    -- Core preference variables (nullable - user may not specify all)
    salary DECIMAL(12, 2),
    job_stress INTEGER CHECK (job_stress BETWEEN 1 AND 10),
    career_growth INTEGER CHECK (career_growth BETWEEN 1 AND 10),
    commute_time_minutes INTEGER CHECK (commute_time_minutes >= 0),
    mission_match INTEGER CHECK (mission_match BETWEEN 1 AND 10),
    industry_preference INTEGER CHECK (industry_preference BETWEEN 1 AND 10),
    work_hours_per_week DECIMAL(5, 2) CHECK (work_hours_per_week >= 0),
    work_hour_flexibility INTEGER CHECK (work_hour_flexibility BETWEEN 1 AND 10),
    work_arrangement INTEGER CHECK (work_arrangement BETWEEN 1 AND 3), -- 1=onsite, 2=hybrid, 3=remote
    job_title_match INTEGER CHECK (job_title_match BETWEEN 1 AND 10),
    company_prestige INTEGER CHECK (company_prestige BETWEEN 1 AND 10),

    -- Job characteristics
    job_type INTEGER CHECK (job_type BETWEEN 1 AND 3), -- 1=part-time, 2=contract, 3=full-time
    company_size INTEGER CHECK (company_size BETWEEN 1 AND 5), -- 1=startup, 2=small, 3=medium, 4=large, 5=enterprise
    team_size INTEGER CHECK (team_size >= 0),
    management_responsibilities INTEGER CHECK (management_responsibilities BETWEEN 1 AND 10), -- 1=no supervision, 10=large team

    -- Benefits & compensation
    equity_offered INTEGER CHECK (equity_offered BETWEEN 1 AND 10),
    vacation_days INTEGER CHECK (vacation_days >= 0),
    benefits_quality INTEGER CHECK (benefits_quality BETWEEN 1 AND 10),
    bonus_potential DECIMAL(5, 2) CHECK (bonus_potential BETWEEN 0 AND 100), -- Percent of salary
    professional_development INTEGER CHECK (professional_development BETWEEN 1 AND 10),

    -- Work-life balance
    travel_percent DECIMAL(5, 2) CHECK (travel_percent BETWEEN 0 AND 100),
    management_autonomy INTEGER CHECK (management_autonomy BETWEEN 1 AND 10),

    -- Impact & culture
    product_stage INTEGER CHECK (product_stage BETWEEN 1 AND 10), -- 1=early/greenfield, 10=mature/maintenance
    social_impact INTEGER CHECK (social_impact BETWEEN 1 AND 10),
    diversity_culture INTEGER CHECK (diversity_culture BETWEEN 1 AND 10),

    -- Contract-specific
    contract_length_months INTEGER CHECK (contract_length_months >= 0),

    -- User's acceptance rating for this scenario (0-100)
    acceptance_score DECIMAL(5, 2) CHECK (acceptance_score BETWEEN 0 AND 100),

    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,

    CONSTRAINT unique_user_scenario_name UNIQUE (user_id, scenario_name)
);

-- Index for querying scenarios by user
CREATE INDEX IF NOT EXISTS idx_user_preference_scenarios_user_id
ON user_preference_scenarios(user_id) WHERE is_active = TRUE;


-- Table: user_preference_models
-- Stores trained regression models for each user
CREATE TABLE IF NOT EXISTS user_preference_models (
    model_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id VARCHAR(100) NOT NULL,

    -- Model metadata
    model_type VARCHAR(50) NOT NULL, -- 'Ridge', 'RandomForest'
    feature_names TEXT[] NOT NULL, -- Array of feature names used
    num_scenarios INTEGER NOT NULL,

    -- Serialized model data (stored as bytea for sklearn models)
    model_data BYTEA NOT NULL,
    scaler_data BYTEA NOT NULL,

    -- Training statistics
    train_r2 DECIMAL(5, 4),
    mean_acceptance DECIMAL(5, 2),
    std_acceptance DECIMAL(5, 2),

    -- Feature importance (JSONB for flexibility)
    feature_importance JSONB,

    -- Metadata
    trained_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,

    CONSTRAINT unique_active_model_per_user UNIQUE (user_id, is_active)
    DEFERRABLE INITIALLY DEFERRED
);

-- Index for querying active models
CREATE INDEX IF NOT EXISTS idx_user_preference_models_user_id
ON user_preference_models(user_id) WHERE is_active = TRUE;

-- Index for feature importance queries
CREATE INDEX IF NOT EXISTS idx_user_preference_models_feature_importance
ON user_preference_models USING GIN (feature_importance);


-- Table: job_preference_scores
-- Caches job evaluation results
CREATE TABLE IF NOT EXISTS job_preference_scores (
    score_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id VARCHAR(100) NOT NULL,
    user_id VARCHAR(100) NOT NULL,

    -- Evaluation results
    acceptance_score DECIMAL(5, 2) NOT NULL CHECK (acceptance_score BETWEEN 0 AND 100),
    should_apply BOOLEAN NOT NULL,
    confidence DECIMAL(4, 3) CHECK (confidence BETWEEN 0 AND 1),

    -- Explanation (JSONB array of strings)
    explanation JSONB,

    -- Metadata
    evaluated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    model_id UUID REFERENCES user_preference_models(model_id),

    CONSTRAINT unique_job_user_score UNIQUE (job_id, user_id)
);

-- Indexes for querying scores
CREATE INDEX IF NOT EXISTS idx_job_preference_scores_job_id
ON job_preference_scores(job_id);

CREATE INDEX IF NOT EXISTS idx_job_preference_scores_user_id
ON job_preference_scores(user_id);

CREATE INDEX IF NOT EXISTS idx_job_preference_scores_should_apply
ON job_preference_scores(user_id, should_apply);

CREATE INDEX IF NOT EXISTS idx_job_preference_scores_score
ON job_preference_scores(user_id, acceptance_score DESC);


-- Trigger to update updated_at timestamp on scenarios
CREATE OR REPLACE FUNCTION update_user_preference_scenarios_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_user_preference_scenarios_updated_at
    BEFORE UPDATE ON user_preference_scenarios
    FOR EACH ROW
    EXECUTE FUNCTION update_user_preference_scenarios_updated_at();


-- Function to ensure only one active model per user
CREATE OR REPLACE FUNCTION ensure_single_active_model()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.is_active = TRUE THEN
        -- Deactivate all other models for this user
        UPDATE user_preference_models
        SET is_active = FALSE
        WHERE user_id = NEW.user_id
          AND model_id != NEW.model_id
          AND is_active = TRUE;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_ensure_single_active_model
    AFTER INSERT OR UPDATE OF is_active ON user_preference_models
    FOR EACH ROW
    WHEN (NEW.is_active = TRUE)
    EXECUTE FUNCTION ensure_single_active_model();


-- Grant permissions (adjust as needed)
-- GRANT SELECT, INSERT, UPDATE, DELETE ON user_preference_scenarios TO your_app_user;
-- GRANT SELECT, INSERT, UPDATE, DELETE ON user_preference_models TO your_app_user;
-- GRANT SELECT, INSERT, UPDATE, DELETE ON job_preference_scores TO your_app_user;


-- Comments for documentation
COMMENT ON TABLE user_preference_scenarios IS
'Stores 1-5 user scenarios describing minimum acceptable jobs for multi-variable regression';

COMMENT ON TABLE user_preference_models IS
'Stores trained sklearn regression models for user job preferences';

COMMENT ON TABLE job_preference_scores IS
'Caches job evaluation results to avoid recomputation';

COMMENT ON COLUMN user_preference_scenarios.acceptance_score IS
'User rating 0-100 indicating how acceptable this scenario is (used as regression target)';

COMMENT ON COLUMN user_preference_scenarios.management_responsibilities IS
'Management/supervision level: 1=no supervision, 5=team lead, 10=large team management';

COMMENT ON COLUMN user_preference_scenarios.job_type IS
'Employment type: 1=part-time, 2=contract, 3=full-time';

COMMENT ON COLUMN user_preference_scenarios.company_size IS
'Company size: 1=startup (<50), 2=small (50-200), 3=medium (200-1000), 4=large (1000-5000), 5=enterprise (5000+)';

COMMENT ON COLUMN user_preference_models.model_data IS
'Serialized sklearn model (joblib format stored as bytea)';

COMMENT ON COLUMN job_preference_scores.should_apply IS
'Binary decision: should apply to this job based on learned preferences';
