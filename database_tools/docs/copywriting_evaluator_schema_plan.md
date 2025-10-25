---
title: "Copywriting Evaluator Schema Plan"
type: technical_doc
component: database
status: draft
tags: []
---

# Copywriting Evaluator Database Schema Migration Plan

**Created:** September 5, 2025  
**Task:** 1.1 - Examine existing sentence bank table structure and create schema migration plan

## Current Schema Analysis

### Existing Tables Structure

#### sentence_bank_cover_letter
- `id` (uuid, primary key, auto-generated)
- `content_text` (text, required)
- `tone` (varchar, nullable)
- `tone_strength` (double precision, nullable)
- `stage` (varchar, default 'Draft') **→ TO BE RENAMED to `status`**
- `position_label` (varchar, nullable)
- `created_at` (timestamp, default CURRENT_TIMESTAMP)
- `matches_job_skill` (varchar, nullable)

#### sentence_bank_resume
- `id` (uuid, primary key, auto-generated)
- `content_text` (text, required)
- `body_section` (varchar, nullable)
- `tone` (varchar, nullable)
- `tone_strength` (double precision, nullable)
- `stage` (varchar, default 'Draft') **→ TO BE RENAMED to `status`**
- `created_at` (timestamp, default CURRENT_TIMESTAMP)
- `matches_job_skill` (varchar, nullable)
- `experience_id` (uuid, nullable)

## Required Schema Changes

### Phase 1: Existing Table Modifications

#### 1.1 Column Renames (Both Tables)
```sql
-- Rename stage column to status in both tables
ALTER TABLE sentence_bank_cover_letter RENAME COLUMN stage TO status;
ALTER TABLE sentence_bank_resume RENAME COLUMN stage TO status;
```

#### 1.2 New Column Additions

**sentence_bank_cover_letter only:**
```sql
-- Add variable column (boolean, default false)
ALTER TABLE sentence_bank_cover_letter ADD COLUMN variable boolean DEFAULT false;
```

**Both tables - Multi-stage Processing Tracking:**
```sql
-- Stage 1: Keyword Filtering
ALTER TABLE {table} ADD COLUMN keyword_filter_status varchar DEFAULT 'pending';
ALTER TABLE {table} ADD COLUMN keyword_filter_date date;
ALTER TABLE {table} ADD COLUMN keyword_filter_error_message text;

-- Stage 2: Truthfulness Evaluation  
ALTER TABLE {table} ADD COLUMN truthfulness_status varchar DEFAULT 'pending';
ALTER TABLE {table} ADD COLUMN truthfulness_date date;
ALTER TABLE {table} ADD COLUMN truthfulness_model varchar;
ALTER TABLE {table} ADD COLUMN truthfulness_error_message text;

-- Stage 3: Canadian Spelling Corrections
ALTER TABLE {table} ADD COLUMN canadian_spelling_status varchar DEFAULT 'pending';
ALTER TABLE {table} ADD COLUMN canadian_spelling_date date;

-- Stage 4: Tone Analysis
ALTER TABLE {table} ADD COLUMN tone_analysis_status varchar DEFAULT 'pending';
ALTER TABLE {table} ADD COLUMN tone_analysis_date date;
ALTER TABLE {table} ADD COLUMN tone_analysis_model varchar;
ALTER TABLE {table} ADD COLUMN tone_analysis_error_message text;

-- Stage 5: Skill Analysis
ALTER TABLE {table} ADD COLUMN skill_analysis_status varchar DEFAULT 'pending';
ALTER TABLE {table} ADD COLUMN skill_analysis_date date;
ALTER TABLE {table} ADD COLUMN skill_analysis_model varchar;
ALTER TABLE {table} ADD COLUMN skill_analysis_error_message text;
```

**Status Values:** "pending", "testing", "error", "preprocessed", "rejected", "approved"

### Phase 2: New Table Creation

#### 2.1 keyword_filters Table
```sql
CREATE TABLE keyword_filters (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    keyword varchar NOT NULL,
    status varchar DEFAULT 'active',
    created_date date DEFAULT CURRENT_DATE
);

-- Initial data
INSERT INTO keyword_filters (keyword) VALUES 
    ('meticulous'), 
    ('meticulously');
```

#### 2.2 canadian_spellings Table  
```sql
CREATE TABLE canadian_spellings (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    american_spelling varchar NOT NULL,
    canadian_spelling varchar NOT NULL,
    status varchar DEFAULT 'active',
    created_date date DEFAULT CURRENT_DATE
);

-- 134 conversion pairs will be loaded from CSV
```

#### 2.3 performance_metrics Table
```sql
CREATE TABLE performance_metrics (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    stage_name varchar NOT NULL,
    api_call_type varchar NOT NULL,
    response_time_ms integer,
    success boolean NOT NULL,
    error_message text,
    cost_estimate decimal(10,4),
    batch_size integer,
    sentences_processed integer,
    processing_date timestamp DEFAULT CURRENT_TIMESTAMP,
    model_used varchar,
    session_id varchar
);
```

## Migration Implementation Strategy

### Using Automated Schema System

1. **Create Migration Script:** Use existing pattern from `database_tools/generated/migration_*.py`
2. **Schema Automation:** Leverage `database_tools/schema_automation.py` for tracking
3. **Generate New Models:** Update auto-generated SQLAlchemy models via `database_tools/code_generator.py`

### Migration File Template
File: `database_tools/generated/migration_copywriting_evaluator.py`

```python
"""
Database Migration Script: Copywriting Evaluator System
Generated on {date}
"""

from sqlalchemy import text
from sqlalchemy.orm import Session

def migrate_database(db: Session):
    """Apply copywriting evaluator schema changes"""
    migration_statements = [
        # Phase 1: Column renames
        "ALTER TABLE sentence_bank_cover_letter RENAME COLUMN stage TO status;",
        "ALTER TABLE sentence_bank_resume RENAME COLUMN stage TO status;",
        
        # Phase 1: New columns for sentence_bank_cover_letter
        "ALTER TABLE sentence_bank_cover_letter ADD COLUMN variable boolean DEFAULT false;",
        
        # Phase 1: Multi-stage tracking columns (both tables)
        # ... (all tracking columns for both tables)
        
        # Phase 2: New tables
        # ... (keyword_filters, canadian_spellings, performance_metrics)
    ]
    
    for statement in migration_statements:
        db.execute(text(statement))
    db.commit()
```

## Data Integrity Considerations

### Backup Strategy
- Current data will be preserved during column renames
- New columns have appropriate defaults to avoid NULL issues
- Foreign key relationships remain intact

### Validation Checks
- Verify all existing sentence records maintain their IDs
- Confirm status values are properly migrated from stage column
- Test new columns accept expected data types and ranges

## Integration Points

### Code Generation Updates
After schema changes, regenerate:
- `database_tools/generated/models.py` - Updated SQLAlchemy models
- `database_tools/generated/schemas.py` - New Pydantic schemas
- `database_tools/generated/crud.py` - CRUD operations for new tables
- `database_tools/generated/routes.py` - API endpoints

### Documentation Updates
- `docs/database_schema.md` - Updated comprehensive documentation
- `docs/database_schema.json` - JSON schema for APIs

## Risk Assessment

### Low Risk Changes
- Column renames (preserve data)
- Adding new nullable columns with defaults
- Creating new independent tables

### Testing Requirements
- Verify existing queries still work after stage→status rename
- Test new column constraints and defaults
- Validate foreign key relationships
- Confirm CSV import processes work with new schema

## Post-Migration Verification

1. **Data Integrity:** Count records before/after migration
2. **Application Compatibility:** Test existing sentence bank queries
3. **New Functionality:** Verify new columns accept expected values
4. **Performance:** Check query performance on expanded tables
5. **Auto-Generated Code:** Confirm models and schemas are updated

## Implementation Timeline

- **Task 1.1:** Schema analysis and planning ✓
- **Task 1.2-1.8:** Execute migration phases sequentially
- **Post-completion:** Run automated schema tools for code generation