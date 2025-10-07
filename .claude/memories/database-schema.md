# Database Schema Memory

## Database Overview
- **Database**: local_Merlin_3 (PostgreSQL)
- **Tables**: 32 normalized tables
- **Schema Management**: Automated with database_tools/

## Key Tables

### Core Workflow
- `companies` - Company information
- `jobs` - Job postings
- `job_applications` - Application tracking
- `user_job_preferences` - User preferences
- `cleaned_job_scrapes` - Processed job data
- `raw_job_scrapes` - Raw scraping results

### Content Analysis
- `sentence_bank_resume` - Resume content library
- `sentence_bank_cover_letter` - Cover letter content
- `job_analysis` - AI analysis results
- `ai_analysis_batches` - Batch processing tracking
- `ai_usage_tracking` - AI API usage metrics

### Tracking & Monitoring
- `link_tracking` - URL tracking
- `document_jobs` - Document generation jobs
- `job_logs` - Application logs
- `application_settings` - App configuration

## Schema Protection
- Auto-generated files are protected by PreToolUse hook
- Never manually edit files in `database_tools/generated/`
- Always run `python database_tools/update_schema.py` after schema changes

## Common Operations
```bash
# Update schema documentation
make db-update

# Check schema status
make db-check

# Force update
make db-force
```
