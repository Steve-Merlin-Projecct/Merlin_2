-- Migration: 001_create_security_detections_table.sql
-- Date: 2025-10-09
-- Purpose: Create table for logging security detections (unpunctuated streams, injection attempts)
-- Part of: Gemini Prompt Optimization - Phase 1 (Security Enhancement)

-- Create security_detections table
CREATE TABLE IF NOT EXISTS security_detections (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id UUID REFERENCES jobs(id) ON DELETE SET NULL,
    detection_type VARCHAR(50) NOT NULL,  -- 'injection_pattern', 'unpunctuated_stream', 'non_job_content'
    severity VARCHAR(20) NOT NULL,        -- 'low', 'medium', 'high', 'critical'
    pattern_matched TEXT,
    text_sample TEXT,                     -- First 200 chars of suspicious content
    metadata JSONB,                       -- Additional detection details
    detected_at TIMESTAMP DEFAULT NOW(),
    handled BOOLEAN DEFAULT FALSE,
    action_taken VARCHAR(100)             -- 'logged', 'blocked', 'sanitized'
);

-- Create indexes for performance
CREATE INDEX idx_security_detections_type ON security_detections(detection_type);
CREATE INDEX idx_security_detections_detected_at ON security_detections(detected_at);
CREATE INDEX idx_security_detections_severity ON security_detections(severity);
CREATE INDEX idx_security_detections_job_id ON security_detections(job_id);

-- Add comments
COMMENT ON TABLE security_detections IS 'Logs security-related detections from AI job analysis system';
COMMENT ON COLUMN security_detections.detection_type IS 'Type of detection: injection_pattern, unpunctuated_stream, non_job_content';
COMMENT ON COLUMN security_detections.severity IS 'Severity level: low, medium, high, critical';
COMMENT ON COLUMN security_detections.metadata IS 'Additional detection details in JSON format';
