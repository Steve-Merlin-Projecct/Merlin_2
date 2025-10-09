---
title: 'Implementation Plan: Automated Job Application System'
created: '2025-10-06'
updated: '2025-10-06'
author: Steve-Merlin-Projecct
type: archived
status: archived
tags:
- implementation
- plan
- automated
- system
---

# Implementation Plan: Automated Job Application System

## Phase 1: Job Scraping & Database Foundation

### 1.1 Indeed.com APify Integration
**Files to create:**
- `modules/job_scraper.py` - APify client and scraping orchestration
- `modules/apify_client.py` - APify API wrapper

**Implementation steps:**
1. Research and select best Indeed scraper from APify marketplace
2. Implement APify client with authentication and rate limiting
3. Create scraping configuration for job search parameters
4. Handle pagination and bulk data extraction
5. Implement error handling and retry logic

**Database updates needed:**
- Add APify-specific metadata columns to track scraper performance
- Store raw APify responses for debugging

### 1.2 Database Schema Updates & Job Storage
**Files to modify:**
- `modules/database_models.py` - Add missing job_number column
- `modules/database_writer.py` - Bulk job insertion methods
- `modules/job_processor.py` - New file for job data processing

**Schema changes needed:**
```sql
-- Add missing column to existing tables
ALTER TABLE job_scrapes_raw ADD COLUMN job_number VARCHAR(100);
ALTER TABLE jobs_per_platform ADD COLUMN job_number VARCHAR(100);
ALTER TABLE jobs ADD COLUMN job_number VARCHAR(100);

-- Add application tracking
ALTER TABLE jobs ADD COLUMN application_status VARCHAR(50) DEFAULT 'not_applied';
ALTER TABLE jobs ADD COLUMN last_application_attempt TIMESTAMP;
ALTER TABLE jobs ADD COLUMN application_method VARCHAR(50); -- 'email', 'platform', 'unavailable'
```

### 1.3 Job Deduplication & Canonicalization
**Files to create:**
- `modules/job_deduplicator.py` - Fuzzy matching and canonicalization
- `modules/company_matcher.py` - Handle recruiting firm variations

**Key algorithms:**
1. **Company name fuzzy matching** using:
   - Levenshtein distance for typos
   - Remove common recruiting suffixes ("LLC", "Inc", "Recruiting")
   - Handle variations like "Google" vs "Google Inc" vs "Google LLC"
2. **Job title similarity** using semantic similarity
3. **Location and salary range matching**
4. **Job description similarity** using TF-IDF or embeddings

**Implementation approach:**
```python
def canonicalize_job(job_data):
    # 1. Normalize company name
    canonical_company = normalize_company_name(job_data.company_name)
    
    # 2. Find existing similar jobs
    similar_jobs = find_similar_jobs(job_data)
    
    # 3. If match found, merge data; otherwise create new canonical job
    if similar_jobs:
        return merge_job_data(job_data, similar_jobs)
    else:
        return create_canonical_job(job_data)
```

### 1.4 LLM Job Analysis Framework
**Files to create:**
- `modules/llm_analyzer.py` - OpenAI/Anthropic integration for job analysis
- `modules/job_analysis_prompts.py` - Structured prompts for consistent analysis
- `modules/skills_extractor.py` - Extract and categorize required skills

**Analysis pipeline:**
1. **Skills extraction** - Identify required technical and soft skills
2. **Experience level determination** - Junior, Mid, Senior classification
3. **Industry/domain classification** - SaaS, FinTech, HealthTech, etc.
4. **Company culture analysis** - Remote-friendly, startup vs enterprise
5. **Salary analysis** - Fair market rate assessment
6. **Application difficulty** - Easy apply vs complex process

**LLM prompt structure:**
```python
ANALYSIS_PROMPT = """
Analyze this job posting and extract structured information:

Job Title: {job_title}
Company: {company_name}
Description: {job_description}

Return JSON with:
{
    "required_skills": ["skill1", "skill2"],
    "nice_to_have_skills": ["skill3"],
    "experience_level": "mid|senior|junior",
    "industry": "saas|fintech|healthcare",
    "remote_friendly": true|false,
    "salary_assessment": "above_market|market_rate|below_market",
    "application_method": "email|easy_apply|complex_form",
    "culture_indicators": ["startup", "fast_paced", "collaborative"]
}
"""
```

### 1.5 Application Tracking System
**Files to modify:**
- `modules/database_models.py` - Add application tracking tables
- `modules/application_tracker.py` - New file for application state management

**New database tables:**
```sql
CREATE TABLE job_applications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id UUID REFERENCES jobs(id),
    application_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    application_method VARCHAR(50), -- 'email', 'platform'
    application_status VARCHAR(50), -- 'sent', 'responded', 'rejected', 'interview'
    email_sent_to VARCHAR(255),
    documents_sent TEXT[], -- ['resume.docx', 'cover_letter.docx']
    tracking_data JSONB, -- email tracking, link clicks, etc.
    response_received_at TIMESTAMP,
    response_type VARCHAR(50), -- 'auto_reply', 'human_response', 'rejection'
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 1.6 User Preferences & Job Eligibility
**Files to create:**
- `modules/user_preferences.py` - User criteria management
- `modules/job_eligibility.py` - Apply user filters to jobs

**User preferences schema:**
```sql
CREATE TABLE user_job_preferences (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID, -- for future multi-user support
    preference_type VARCHAR(50), -- 'salary_min', 'remote_required', 'industry_include'
    preference_value TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Eligibility rules engine:**
```python
def check_job_eligibility(job, user_preferences):
    rules = [
        ('salary_minimum', lambda j, p: j.salary_low >= p.salary_min),
        ('remote_required', lambda j, p: p.remote_required and j.remote_friendly),
        ('industry_include', lambda j, p: j.industry in p.included_industries),
        ('experience_match', lambda j, p: j.experience_level in p.target_levels)
    ]
    
    for rule_name, rule_func in rules:
        if not rule_func(job, user_preferences):
            return False, f"Failed rule: {rule_name}"
    
    return True, "Eligible"
```

### 1.7 Application Method Detection
**Files to create:**
- `modules/application_method_detector.py` - Determine how to apply

**Detection logic:**
```python
def determine_application_method(job):
    # 1. Check if email is explicitly mentioned
    if has_email_application(job.description):
        return 'email', extract_email_address(job.description)
    
    # 2. Check for "easy apply" buttons (for future platform integration)
    if has_easy_apply_option(job.posting_url):
        return 'easy_apply', job.posting_url
    
    # 3. Check for complex application forms
    if requires_complex_form(job.posting_url):
        return 'complex_form', job.posting_url
    
    # 4. Default to email if company email can be inferred
    company_email = infer_company_email(job.company_name)
    if company_email:
        return 'email_inferred', company_email
    
    return 'unavailable', None
```

## Phase 2: Application Package Creation

### 2.1 Content Library Import System
**Files to create:**
- `modules/content_importer.py` - CSV to database import
- `data/approved_content.csv` - Content library structure

**CSV structure:**
```csv
content_type,category,tone,text,tags,position_labels,strength_score,approval_status
resume,achievement,confident,"Led cross-functional team of 8 to deliver $2M product launch","leadership,product,strategy","Senior Manager,Product Manager",9,approved
cover_letter,opening,warm,"Your recent post about reimagining customer onboarding caught my attention","company_research,personalization","All",8,approved
```

**Import functionality:**
```python
def import_content_from_csv(csv_path):
    with open(csv_path, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row['content_type'] == 'resume':
                create_resume_sentence(row)
            elif row['content_type'] == 'cover_letter':
                create_cover_letter_sentence(row)
```

### 2.2 Content Database Access Layer
**Files to create:**
- `modules/content_selector.py` - Smart content selection algorithms
- `modules/content_ranker.py` - Rank content by job relevance

**Content selection algorithm:**
```python
def select_resume_content(job, user_profile):
    # 1. Get content matching job skills/industry
    relevant_content = filter_content_by_tags(
        job.required_skills + [job.industry, job.experience_level]
    )
    
    # 2. Rank by relevance score
    ranked_content = rank_by_relevance(relevant_content, job)
    
    # 3. Ensure tone consistency
    consistent_content = ensure_tone_consistency(ranked_content)
    
    # 4. Fill resume sections with best content
    return {
        'achievements': select_achievements(consistent_content, 3),
        'skills': select_skills(consistent_content, job.required_skills),
        'experience': select_experience_bullets(consistent_content, 5)
    }
```

### 2.3 Application Queue Management
**Files to create:**
- `modules/application_queue.py` - Manage pending applications
- `modules/application_scheduler.py` - Rate limiting and timing

**Queue processing:**
```python
def get_ready_to_apply_jobs():
    return db.query("""
        SELECT j.* FROM jobs j
        WHERE j.application_status = 'not_applied'
        AND j.eligibility_flag = true
        AND j.application_method IN ('email', 'email_inferred')
        AND j.analysis_completed = true
        ORDER BY j.priority_score DESC
        LIMIT 10
    """)
```

### 2.4 Document Generation Pipeline
**Files to modify:**
- `modules/resume_generator.py` - Add job-specific customization
- `modules/cover_letter_generator.py` - Add job-specific content selection
- `modules/email_generator.py` - New file for email content

**Integration with existing system:**
```python
def generate_application_package(job_id):
    job = get_job_by_id(job_id)
    selected_content = select_content_for_job(job)
    
    # Use existing document generators with job-specific content
    resume_info = resume_generator.generate_resume({
        'job_specific_content': selected_content['resume'],
        'target_skills': job.required_skills
    })
    
    cover_letter_info = cover_letter_generator.generate_cover_letter({
        'job_specific_content': selected_content['cover_letter'],
        'company': job.company_name,
        'position': job.job_title
    })
    
    email_content = generate_application_email(job, selected_content)
    
    return {
        'resume': resume_info,
        'cover_letter': cover_letter_info,
        'email': email_content
    }
```

### 2.5 Link Tracking System
**Files to create:**
- `modules/link_tracker.py` - Generate and track unique links
- `routes/tracking.py` - Handle tracking redirects

**Tracking implementation:**
```python
def generate_tracked_links(job_id, email_content):
    tracked_links = {}
    
    # Generate unique tracking IDs for each link type
    for link_type in ['linkedin', 'portfolio', 'calendar']:
        tracking_id = generate_tracking_id(job_id, link_type)
        tracked_url = f"https://yourapp.replit.app/track/{tracking_id}"
        tracked_links[link_type] = tracked_url
        
        # Store in database
        store_tracking_record(tracking_id, job_id, link_type, original_url)
    
    return tracked_links

@app.route('/track/<tracking_id>')
def handle_click_tracking(tracking_id):
    # Record click in database
    record_click(tracking_id, request.remote_addr, request.user_agent)
    
    # Redirect to original URL
    original_url = get_original_url(tracking_id)
    return redirect(original_url)
```

## Implementation Schedule

### Week 1: Database & Scraping Foundation
- Days 1-2: Database schema updates and migrations
- Days 3-4: APify integration and job scraping
- Days 5-7: Basic job storage and deduplication

### Week 2: Analysis & Intelligence
- Days 1-3: LLM analysis integration
- Days 4-5: User preferences and eligibility system
- Days 6-7: Application method detection

### Week 3: Content & Generation
- Days 1-2: Content library import system
- Days 3-4: Content selection algorithms
- Days 5-7: Integration with existing document generators

### Week 4: Tracking & Polish
- Days 1-3: Link tracking system
- Days 4-5: Application queue management
- Days 6-7: Testing and refinement

## Success Metrics
- **Jobs scraped per day**: Target 100-500 new jobs
- **Deduplication accuracy**: >95% correct canonical job creation
- **LLM analysis success**: >90% successful job analysis
- **Content relevance**: User approval rating >80%
- **Application generation**: End-to-end package creation in <30 seconds

This foundation will give you a complete system from job discovery through document generation, ready to integrate with your existing Make.com email automation.