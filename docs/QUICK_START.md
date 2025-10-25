---
title: "Quick Start"
type: technical_doc
component: general
status: draft
tags: []
---

# Quick Start Guide - Seed Sentence Processing Pipeline

## TL;DR - Run the Pipeline

```bash
# 1. Configure Gemini API Key
export GEMINI_API_KEY="your-api-key-here"

# 2. Run the simplified pipeline (recommended for first run)
python3 process_seeds_only.py

# OR run the full pipeline with variations
python3 process_seed_sentences_pipeline.py
```

## What This Does

Processes 300 Marketing Automation Manager seed sentences through a 5-stage copywriting evaluation pipeline:

1. **Stage 1 - Keyword Filter:** Brand alignment check
2. **Stage 2 - Truthfulness Assessment:** AI validation against 51 atomic truths
3. **Stage 3 - Canadian Spelling:** US→Canadian conversion
4. **Stage 4 - Tone Analysis:** 9-category tone classification
5. **Stage 5 - Skill Analysis:** Job skill matching

## Files Overview

| File | Purpose | When to Use |
|------|---------|-------------|
| `process_seeds_only.py` | Process 300 seeds (no variations) | Fast execution, testing |
| `process_seed_sentences_pipeline.py` | Process 300 seeds + 2,100 variations | Full production run |
| `marketing_automation_seed_sentences_new.txt` | 300 source sentences | Read-only input |
| `marketing_automation_atomic_truths.txt` | 51 truth statements | Read-only input |
| `PROCESSING_REPORT.md` | Full documentation | Reference |

## Expected Output

### Terminal Output
- Real-time progress logs
- Stage-by-stage statistics
- Error tracking
- Final summary

### Report File
- JSON file: `processing_report_YYYYMMDD_HHMMSS.json`
- Contains:
  - Total sentences processed
  - Approval/rejection counts per stage
  - Production-ready sentence count
  - SQL verification queries
  - Error log (if any)

### Database Updates
Tables populated:
- `sentence_bank_resume` (28 sentences)
- `sentence_bank_cover_letter` (272 sentences)

Columns updated per sentence:
- `keyword_filter_status` → 'approved' or 'rejected'
- `truthfulness_status` → 'approved' or 'rejected'
- `canadian_spelling_status` → 'completed'
- `tone_analysis_status` → 'completed'
- `skill_analysis_status` → 'completed'

## Estimated Processing Time

- **Seeds Only:** ~15-20 minutes
  - 300 sentences ÷ 5 per batch = 60 API calls
  - ~3 seconds per API call for AI stages

- **With Variations:** ~2-3 hours
  - 300 seeds + 2,100 variations = 2,400 sentences
  - Additional variation generation time

## Verification Queries

After processing, run these queries to check results:

```sql
-- Total production-ready sentences
SELECT COUNT(*) FROM sentence_bank_resume
WHERE keyword_filter_status = 'approved'
  AND truthfulness_status = 'approved'
  AND canadian_spelling_status = 'completed'
  AND tone_analysis_status = 'completed'
  AND skill_analysis_status = 'completed';

-- Stage-by-stage breakdown
SELECT
    COUNT(*) as total,
    COUNT(CASE WHEN keyword_filter_status = 'approved' THEN 1 END) as stage_1_pass,
    COUNT(CASE WHEN truthfulness_status = 'approved' THEN 1 END) as stage_2_pass,
    COUNT(CASE WHEN canadian_spelling_status = 'completed' THEN 1 END) as stage_3_complete
FROM sentence_bank_resume
WHERE created_at >= CURRENT_DATE;
```

## Troubleshooting

### Error: "GEMINI_API_KEY environment variable not found"
```bash
export GEMINI_API_KEY="your-key"
```

### Error: "column body_section violates check constraint"
This is handled in the current version - should not occur.

### Pipeline stalls or times out
- Reduce batch size in pipeline_processor.py
- Check network connection to Gemini API
- Verify database connection

### No sentences processed
- Check if sentences already exist in database with non-'pending' status
- Re-run will only process sentences with status='pending'

## Current State

- **Database:** Already contains 91 sentences from testing
- **Status:** All set to 'pending' for processing
- **Ready:** Pipeline tested and verified
- **Blocking:** Gemini API key configuration

## Support

For detailed documentation see `PROCESSING_REPORT.md`

For code details see inline comments in:
- `process_seeds_only.py`
- `process_seed_sentences_pipeline.py`
