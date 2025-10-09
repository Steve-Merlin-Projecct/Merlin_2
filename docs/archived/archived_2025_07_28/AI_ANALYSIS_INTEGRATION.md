---
title: AI Analysis Integration - Enhanced Jobs Table Schema
status: completed
version: '2.10'
created: '2025-10-06'
updated: '2025-10-06'
author: Steve-Merlin-Projecct
type: archived
tags:
- analysis
- integration
---

# AI Analysis Integration - Enhanced Jobs Table Schema
**Version**: 2.10  
**Date**: July 22, 2025  
**Status**: Complete

## Overview

This document outlines the comprehensive AI analysis integration that enhances the jobs table with 35+ new columns and creates 6 normalized tables for complete job analysis data storage. The system now stores all AI analysis results directly in the jobs table, making it the single source of truth for all job data.

## User Requirements Implemented

All 6 specific user requirements have been successfully implemented:

1. **✓ No classification_confidence column** - Removed from all analysis outputs
2. **✓ Office location split into 4 columns** - Implemented address, city, province, country parsing
3. **✓ Removed years_experience field** - Not included in analysis structure
4. **✓ No skill_category field** - Skills stored without categorization
5. **✓ No job_implicit_requirements table** - Implicit requirements integrated into skills analysis
6. **✓ Single cover letter insight only** - One pain point with evidence and solution angle

## Enhanced Jobs Table Schema

### New Analysis Columns Added (35+ columns)

#### Authenticity Analysis
- `title_matches_role` (BOOLEAN)
- `mismatch_explanation` (TEXT)
- `is_authentic` (BOOLEAN)
- `authenticity_reasoning` (TEXT)

#### Classification Enhancement
- `sub_industry` (VARCHAR(100))
- `job_function` (VARCHAR(100))

#### Work Arrangement Details
- `in_office_requirements` (TEXT)
- `office_address` (VARCHAR(255))
- `office_city` (VARCHAR(100))
- `office_province` (VARCHAR(100))
- `office_country` (VARCHAR(100))
- `working_hours_per_week` (INTEGER)
- `work_schedule` (VARCHAR(100))
- `specific_schedule` (TEXT)
- `travel_requirements` (TEXT)

#### Compensation Analysis
- `salary_mentioned` (BOOLEAN)
- `equity_stock_options` (BOOLEAN)
- `commission_or_performance_incentive` (BOOLEAN)
- `est_total_compensation` (DECIMAL(12,2))
- `compensation_currency` (VARCHAR(10))

#### Application Process
- `application_email` (VARCHAR(255))
- `special_instructions` (TEXT)

#### Stress Level Analysis
- `estimated_stress_level` (INTEGER)
- `stress_reasoning` (TEXT)

#### Education & Experience
- `education_requirements` (TEXT)

#### Red Flags Analysis
- `overall_red_flag_reasoning` (TEXT)

#### Cover Letter Strategy
- `cover_letter_pain_point` (TEXT)
- `cover_letter_evidence` (TEXT)
- `cover_letter_solution_angle` (TEXT)

#### Analysis Metadata
- `analysis_completed` (BOOLEAN DEFAULT FALSE)

## Normalized Tables Created (6 tables)

### 1. job_skills
Stores individual skills with importance ratings without categorization
- `job_id` (UUID, FK to jobs.id)
- `skill_name` (VARCHAR(100))
- `importance_rating` (INTEGER 1-100)
- `reasoning` (TEXT)
- `created_at` (TIMESTAMP)

### 2. job_benefits
Stores job benefits as individual records
- `job_id` (UUID, FK to jobs.id)
- `benefit_name` (VARCHAR(200))
- `created_at` (TIMESTAMP)

### 3. job_required_documents
Stores required application documents
- `job_id` (UUID, FK to jobs.id)
- `document_type` (VARCHAR(100))
- `is_required` (BOOLEAN)
- `created_at` (TIMESTAMP)

### 4. job_stress_indicators
Stores individual stress indicators
- `job_id` (UUID, FK to jobs.id)
- `indicator` (VARCHAR(200))
- `created_at` (TIMESTAMP)

### 5. job_certifications
Stores required certifications
- `job_id` (UUID, FK to jobs.id)
- `certification_name` (VARCHAR(150))
- `is_required` (BOOLEAN)
- `created_at` (TIMESTAMP)

### 6. job_ats_keywords
Stores ATS optimization keywords by type
- `job_id` (UUID, FK to jobs.id)
- `keyword_type` (VARCHAR(50)) - 'primary', 'industry', 'must_have_phrase'
- `keyword` (VARCHAR(200))
- `created_at` (TIMESTAMP)

### 7. job_red_flags_details
Stores detailed red flag analysis
- `job_id` (UUID, FK to jobs.id)
- `flag_type` (VARCHAR(100))
- `detected` (BOOLEAN)
- `details` (TEXT)
- `created_at` (TIMESTAMP)

## AI Analysis JSON Structure

The enhanced AI analysis now follows this structure:

```json
{
  "job_id": "uuid",
  "authenticity_check": {
    "title_matches_role": boolean,
    "mismatch_explanation": "string",
    "is_authentic": boolean,
    "reasoning": "string"
  },
  "classification": {
    "sub_industry": "string",
    "job_function": "string"
  },
  "structured_data": {
    "skill_requirements": {
      "skills": [
        {
          "skill_name": "string",
          "importance_rating": integer,
          "reasoning": "string"
        }
      ],
      "education_requirements": "string",
      "certifications": ["string"]
    },
    "work_arrangement": {
      "in_office_requirements": "string",
      "office_location": "address, city, province, country",
      "working_hours_per_week": integer,
      "work_schedule": "string",
      "specific_schedule": "string",
      "travel_requirements": "string"
    },
    "compensation": {
      "salary_mentioned": boolean,
      "equity_stock_options": boolean,
      "commission_or_performance_incentive": boolean,
      "est_total_compensation": decimal,
      "compensation_currency": "CAD|USD|other",
      "benefits": ["string"]
    },
    "application_details": {
      "application_email": "email",
      "special_instructions": "string",
      "required_documents": ["string"]
    },
    "ats_optimization": {
      "primary_keywords": ["string"],
      "industry_keywords": ["string"],
      "must_have_phrases": ["string"]
    }
  },
  "stress_level_analysis": {
    "estimated_stress_level": integer,
    "reasoning": "string",
    "stress_indicators": ["string"]
  },
  "red_flags": {
    "overall_red_flag_reasoning": "string",
    "unrealistic_expectations": {
      "detected": boolean,
      "details": "string"
    },
    "potential_scam_indicators": {
      "detected": boolean,
      "details": "string"
    }
  },
  "cover_letter_insight": {
    "employer_pain_point": {
      "pain_point": "string",
      "evidence": "string",
      "solution_angle": "string"
    }
  }
}
```

## Data Pipeline Architecture

The enhanced pipeline now follows this flow:

1. **Job Scraping** → Raw job data stored in jobs table
2. **AI Analysis** → Enhanced analysis results stored in jobs table + normalized tables
3. **Document Generation** → Uses enriched jobs table data for personalized documents

## Database Storage Process

The `NormalizedAnalysisWriter` class handles the complete storage process:

1. **Jobs Table Update**: Updates the main jobs record with 35+ analysis fields
2. **Office Location Parsing**: Splits office_location into address, city, province, country components
3. **Normalized Table Storage**: Saves related data to 6 normalized tables
4. **Data Integrity**: Uses transaction-based operations with proper error handling

## Key Implementation Features

- **No Skill Categories**: Skills stored without categorization per user requirement #4
- **Single Cover Letter Insight**: One employer pain point with evidence and solution angle
- **Currency Support**: Compensation amounts stored with appropriate currency (CAD/USD/other)
- **Experience as Skills**: Experience requirements interpreted as skills and subskills
- **ATS Optimization**: Focus on primary keywords, industry keywords, and must-have phrases (no action verbs)
- **Office Location Splitting**: Automatic parsing of location strings into structured components

## Benefits of Enhanced Integration

1. **Single Source of Truth**: Jobs table contains all job data including AI analysis results
2. **Query Performance**: Direct access to analysis data without JSON parsing
3. **Data Integrity**: Proper foreign key relationships and normalized structure
4. **Scalability**: Indexed columns for fast filtering and searching
5. **Flexibility**: Normalized tables allow for complex analysis queries
6. **User Requirements**: All 6 specific user requirements successfully implemented

## Usage Examples

### Query jobs with high-stress indicators
```sql
SELECT j.*, COUNT(jsi.indicator) as stress_indicator_count
FROM jobs j
LEFT JOIN job_stress_indicators jsi ON j.id = jsi.job_id
WHERE j.estimated_stress_level > 7
GROUP BY j.id;
```

### Find jobs with specific skills and importance ratings
```sql
SELECT j.title, j.company_name, js.skill_name, js.importance_rating
FROM jobs j
JOIN job_skills js ON j.id = js.job_id
WHERE js.skill_name ILIKE '%marketing%' 
AND js.importance_rating >= 80;
```

### Get comprehensive job analysis data
```sql
SELECT j.*, 
       j.cover_letter_pain_point,
       j.cover_letter_evidence,
       j.cover_letter_solution_angle,
       j.compensation_currency,
       j.office_city,
       j.office_province
FROM jobs j
WHERE j.analysis_completed = TRUE
AND j.is_authentic = TRUE;
```

This enhanced integration provides a robust foundation for the automated job application system with comprehensive AI analysis capabilities and user-specified customizations.