# Product Requirements Document: Variable Substitution System for Application Packages

## Executive Summary

This document outlines the requirements for enhancing the existing variable substitution system to fully support personalized job application packages (email, cover letter, and resume) through four distinct scenarios. The system partially exists with template processing and some variable handling, but requires significant enhancements for complete functionality.

## Current Implementation Status

### What Already Exists:
- **Template Engine**: Supports `<<variable_name>>` and `{job_title}/{company_name}` patterns

- **CSV Content Mapper**: Basic work_experience_1/2 variables (hardcoded)
- **Content Manager**: Variable repetition prevention for {job_title} and {company_name}
- **Document Generator**: Integration with template engine and CSV mapping

### What Needs to Be Built:
- **Scenario 1 Enhancements**: Integration between template variables and tracking system for URLs
- **Scenario 2 Additions**: Hiring manager name, company address, job number handling
- **Scenario 4 Complete Implementation**: Chronological work experience ordering algorithm
- **Date Parsing System**: Standardization of various date formats
- **Dynamic Experience Mapping**: Replace hardcoded work experiences with dynamic ordering

## System Overview

The Variable Substitution System processes templates and dynamically generated content to create personalized application documents by:
- Replacing candidate information at predefined template positions
- Inserting hiring organization details at specified locations
- Dynamically placing company/job variables within sentences
- Chronologically ordering work experiences and mapping to template variables
- Using experience context to guide content selection for resumes

## Business Requirements

### Core Objectives
1. Automate personalization of application packages at scale
2. Maintain tracking capabilities through redirect URLs
3. Ensure consistency across all document types
4. Prevent repetition and maintain natural language flow
5. Support both static and dynamic variable placement
6. Ensure chronological accuracy in work experience presentation
7. Align content selection with most recent work experience

### Success Criteria
- 100% accurate variable substitution in templates
- Zero duplicate company/job title variables in dynamic placement
- Successful tracking parameter capture for all redirect URLs
- Seamless integration with existing document generation pipeline

## Functional Requirements

### Scenario 1: Candidate Information Substitution (Template-Defined)

#### Current Status
✅ **Partially Implemented**
- Template engine supports `<<variable_name>>` format
- Basic variable substitution works

❌ **Not Implemented**
- Integration between template variables and tracking system

- Phone number and address formatting

#### Description
Fixed-position substitution of candidate personal information where templates explicitly define variable placement using 

#### Variables
| Variable Name | Format | Required | Document Types | Special Processing |
|--------------|--------|----------|----------------|-------------------|
| `{{first_name}}` | Text | Yes | Email, Cover Letter, Resume | None |
| `{{last_name}}` | Text | Yes | Email, Cover Letter, Resume | None |
| `{{email_address}}` | Email | Yes | Cover Letter, Resume | None |
| `{{phone_number}}` | Phone | Yes | Cover Letter, Resume | Format standardization |
| `{{mailing_address}}` | Address | Yes | Cover Letter, Resume | Multi-line support |


#### Template Marker Format
```
Dear Hiring Manager,

I am {{first_name}} {{last_name}}, and I am writing to express...

Contact me at {{email_address}} or {{phone_number}}.

Schedule a meeting: {{calendly_url}}
```

### Scenario 2: Hiring Organization Information (Template-Defined)

#### Current Status
✅ **Partially Implemented**
- Template engine supports `<<variable_name>>` format
- Company name and job title available in job data

❌ **Not Implemented**
- Hiring manager name extraction and storage
- Company address formatting
- Job number/reference ID handling
- Fallback logic for missing data

#### Description
Fixed-position substitution of hiring organization details in conversational segments of emails and cover letters. Requires enhancement of job data storage and retrieval.

#### Variables
| Variable Name | Format | Location | Required | Notes |
|--------------|--------|----------|----------|-------|
| `{{company_name}}` | Text | Header, Body | Yes | Used in address block and content |
| `{{hiring_manager_name}}` | Text | Greeting, Body | No | Falls back to "Hiring Manager" |
| `{{company_address}}` | Address | Header | No | Multi-line format |
| `{{job_number}}` | Alphanumeric | Body | Conditional | Based on template type |
| `{{job_title}}` | Text | Body | Yes | Position being applied for |

#### Usage Examples
```
{{company_name}}
{{company_address}}

Dear {{hiring_manager_name|Hiring Manager}},

I am writing to apply for the {{job_title}} position (Job #{{job_number}}) at {{company_name}}...
```

### Scenario 3: Dynamic Company/Job Variable Placement

#### Current Status
✅ **Fully Implemented**
- Template engine recognizes `{job_title}` and `{company_name}` patterns
- ContentManager prevents duplicate usage (max 1 of each)
- Variable stripping for keyword matching
- Integration with sentence selection algorithm

#### Description
Algorithmic insertion of company name or job title within sentence content from sentence banks. Maximum one instance of each variable per cover letter. **This scenario is already complete and working.**

#### Variables
- `{company_name}` - Company name within sentence flow
- `{job_title}` - Job position within sentence flow

#### Algorithm Requirements
1. **Sentence Selection Phase**
   - Identify sentences containing `{company_name}` or `{job_title}` variables
   - Track which variables have been used globally in document
   - Exclude sentences with already-used variables from selection pool

2. **Placement Rules**
   - Maximum 1 instance of `{company_name}` per document
   - Maximum 1 instance of `{job_title}` per document
   - Variables can appear in any paragraph
   - Must maintain grammatical correctness after substitution

3. **Validation Requirements**
   - Verify variable syntax before selection
   - Ensure no duplicate variable usage
   - Validate sentence structure post-substitution
   - Flag any sentences with unsupported variables

#### Example Sentences
```
"I am excited about the opportunity to contribute to {company_name}'s continued success."
"The {job_title} position aligns perfectly with my career objectives."
"Having researched {company_name} extensively, I am impressed by your commitment to innovation."
```

### Scenario 4: Chronological Work Experience Ordering

#### Current Status
✅ **Partially Implemented**
- CSV mapper has work_experience_1 and work_experience_2 variables
- Basic structure for experience variables exists

❌ **Not Implemented**
- Chronological ordering algorithm
- Date parsing and standardization
- Dynamic experience mapping (currently hardcoded to Odvod Media and Rona)
- Integration with content selection context
- Support for more than 2 work experiences

#### Description
System must analyze candidate's work history to determine chronological order and dynamically map experiences to numbered template variables. This preprocessing step must occur BEFORE content selection to ensure resume sentences are chosen that relate to the correct companies.

#### Variables Format
Work experiences are numbered based on recency (1 = most recent):
- `<<work_experience_1_company_name>>` - Most recent employer
- `<<work_experience_1_job_title>>` - Most recent position
- `<<work_experience_1_dates>>` - Most recent employment period
- `<<work_experience_1_location>>` - Most recent work location
- `<<work_experience_2_company_name>>` - Second most recent employer
- `<<work_experience_2_job_title>>` - Second most recent position
- `<<work_experience_2_dates>>` - Second most recent employment period
- `<<work_experience_2_location>>` - Second most recent work location
- (Pattern continues for all experiences...)

#### Example Mapping
Given candidate work history:
```
1. Odvod Media - Senior Developer - 2022 to present - Toronto, ON
2. Hudson's Bay Company - Developer - 2020 to 2022 - Toronto, ON  
3. Tech Startup Inc - Junior Developer - 2018 to 2020 - Mississauga, ON
```

Variables filled:
- `<<work_experience_1_company_name>>` → "Odvod Media"
- `<<work_experience_1_job_title>>` → "Senior Developer"
- `<<work_experience_1_dates>>` → "2022 - Present"
- `<<work_experience_2_company_name>>` → "Hudson's Bay Company"
- `<<work_experience_2_dates>>` → "2020 - 2022"

#### Algorithm Requirements

1. **Date Parsing & Ordering**
   - Parse various date formats (MM/YYYY, Month YYYY, YYYY-YYYY, "Present", "Current")
   - Handle overlapping employment periods
   - Sort by end date (nulls/present = most recent)
   - Break ties using start date
   - Handle gaps in employment history

2. **Experience Validation**
   - Verify all required fields present (company, title, dates)
   - Standardize date formats for output
   - Handle missing or incomplete data gracefully
   - Flag suspicious date patterns for review

3. **Integration with Content Selection**
   - Pass ordered company names to content selection system
   - Ensure resume sentences are selected for correct companies (especially most recent)
   - Map experience-specific achievements to correct positions
   - Maintain experience context for skill selection
   - Prioritize content from most recent experience (work_experience_1)

#### Processing Rules
```python
# Pseudocode for experience ordering
experiences = sort_experiences_by_date(candidate.work_history)
for index, experience in enumerate(experiences, start=1):
    variables[f"work_experience_{index}_company_name"] = experience.company
    variables[f"work_experience_{index}_job_title"] = experience.title
    variables[f"work_experience_{index}_dates"] = format_dates(experience)
    variables[f"work_experience_{index}_location"] = experience.location
    
# Pass to content selection
content_selector.set_company_context(experiences[0].company)  # Most recent
```

#### Date Format Standardization
| Input Format | Output Format | Example |
|-------------|---------------|---------|
| "2022-01-01 to present" | "2022 - Present" | Current job |
| "Jan 2020 - Dec 2021" | "2020 - 2021" | Completed |
| "2019/06 - 2020/08" | "2019 - 2020" | Completed |
| "Summer 2018" | "2018" | Seasonal |
| "2017-ongoing" | "2017 - Present" | Current |

## Technical Requirements

### Required Integrations with Existing Systems


#### 2. Job Data Enhancement (Scenario 2)
- Extend jobs table to include: hiring_manager_name, company_address, job_reference_number
- Modify scraping pipeline to extract these fields when available
- Add fallback logic to ContentManager for missing fields

#### 3. Work Experience Processor (Scenario 4)
- Create new module: `modules/content/document_generation/experience_processor.py`
- Integrate with CSVContentMapper to replace hardcoded experiences
- Add date parsing utilities for various formats
- Implement sorting algorithm based on end dates

### Data Structure Enhancements

#### Extend Existing Tables
```sql
-- Add to jobs table
ALTER TABLE jobs ADD COLUMN IF NOT EXISTS hiring_manager_name VARCHAR(200);
ALTER TABLE jobs ADD COLUMN IF NOT EXISTS company_address TEXT;
ALTER TABLE jobs ADD COLUMN IF NOT EXISTS job_reference_number VARCHAR(100);

-- Add to user_profiles or create work_experiences table
CREATE TABLE IF NOT EXISTS work_experiences (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    company_name VARCHAR(200) NOT NULL,
    job_title VARCHAR(200) NOT NULL,
    start_date DATE,
    end_date DATE,
    is_current BOOLEAN DEFAULT FALSE,
    location VARCHAR(200),
    display_order INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### Variable Usage Tracking
```sql
CREATE TABLE variable_usage_log (
    id SERIAL PRIMARY KEY,
    document_id INTEGER NOT NULL,
    variable_name VARCHAR(50) NOT NULL,
    substituted_value TEXT,
    original_context TEXT, -- surrounding text for dynamic variables
    position_in_document INTEGER,
    tracking_url TEXT, -- if applicable
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (document_id) REFERENCES generated_documents(id)
);
```

### Enhanced Processing Pipeline

#### Integration Points with Existing Systems

1. **Template Loading** (Existing - TemplateEngine)
   - Already parses `<<variable>>` and `{variable}` patterns
   - Need to add recognition for trackable URL variables

2. **Data Collection** (Partial - Needs Enhancement)
   - Existing: Candidate data from user_profiles
   - Existing: Job data from jobs table
   - **NEW**: Load work experiences with dates for ordering
   - **NEW**: Fetch hiring manager and company address

3. **Preprocessing Phase** (NEW - Critical Addition)
   - **NEW**: Create ExperienceProcessor class
   - **NEW**: Parse and standardize dates
   - **NEW**: Sort experiences by end_date DESC
   - **NEW**: Generate work_experience_N variables dynamically
   - **MODIFY**: Update CSVContentMapper to use dynamic experiences


5. **Substitution Processing** (Enhance Existing)
   - **EXISTING**: Template variable substitution
   - **EXISTING**: Job variable substitution (Scenario 3)
   - **ENHANCE**: Add tracking URL generation
   - **ENHANCE**: Add hiring org fields
   - **NEW**: Use dynamically ordered work experiences

6. **Validation & Output** (Existing)
   - Already handles missing variables
   - Already generates documents
   - **ENHANCE**: Add tracking URL validation

### API Endpoints

#### Process Document with Variables
```
POST /api/documents/generate-with-variables
{
    "template_id": "cover_letter_template_001",
    "candidate_id": 123,
    "job_posting_id": 456,
    "scenarios_enabled": [1, 2, 3, 4],
    "tracking_domain": "track.candidatedomain.com"
}
```

#### Validate Variable Template
```
POST /api/templates/validate-variables
{
    "template_content": "...",
    "expected_variables": ["{{first_name}}", "{{company_name}}"]
}
```

## Integration Requirements

### Existing System Integration

1. **Document Generation Pipeline**
   - Hook into existing TemplateEngine class
   - Extend current variable substitution logic
   - Maintain backward compatibility

2. **Sentence Bank System**
   - Query sentences with variable patterns
   - Track variable usage across selection
   - Integrate with copywriting evaluator results

3. **Tracking System**
   - Generate unique tracking IDs
   - Create redirect URLs with parameters
   - Log click-through events

### External Dependencies

- URL shortening service for tracking URLs
- Email validation service
- Address formatting service
- Phone number formatting library

## Performance Requirements

- Variable substitution: < 100ms per document
- Work experience ordering: < 50ms per document
- Content selection with context: < 500ms per document
- Batch processing: 100 documents per minute
- Tracking redirect response: < 50ms

## Security Requirements

1. **Data Protection**
   - Encrypt candidate PII at rest
   - Use parameterized queries for all substitutions
   - Sanitize all variable inputs

2. **URL Security**
   - Sign tracking URLs to prevent tampering
   - Implement rate limiting on redirect endpoint
   - Validate target URLs against whitelist

3. **Template Security**
   - Prevent script injection through variables
   - Validate template structure before processing
   - Limit variable recursion depth

## Testing Requirements

### Unit Tests
- Variable parser accuracy
- Substitution engine correctness
- Experience ordering logic
- Date parsing accuracy
- Variable mapping correctness
- Tracking URL generation

### Integration Tests
- End-to-end document generation
- Multi-scenario processing
- Database transaction integrity
- External service integration

### Performance Tests
- Load testing with 1000+ concurrent documents
- Memory usage under high load
- Database query optimization
- Caching effectiveness

## Error Handling

### Variable Errors
| Error Type | Handling | User Message |
|-----------|----------|--------------|
| Missing required variable | Skip document | "Required information missing: [variable]" |
| Invalid variable format | Use default or skip | "Invalid format for: [variable]" |

| Dynamic placement failure | Skip dynamic variables | "Using standard content without personalization" |
| Experience ordering failure | Use provided order | "Using default experience order" |

### Recovery Procedures
1. Log all errors with context
2. Attempt retry for transient failures
3. Fallback to template defaults where possible
4. Alert administrators for systematic failures

## Monitoring & Analytics

### Key Metrics
- Variable substitution success rate
- Average processing time per scenario
- Tracking URL click-through rate
- Experience ordering accuracy rate
- Context-aware content selection effectiveness
- Error rate by variable type

### Dashboards
- Real-time processing status
- Variable usage heat map
- Content selection distribution
- Tracking analytics summary

## Implementation Phases

### Phase 1: Database & Infrastructure Updates (Week 1)
- Add hiring_manager_name, company_address, job_reference_number to jobs table
- Create work_experiences table

- Update scraping pipeline for new fields

### Phase 2: Scenario 1 & 2 Enhancements (Week 2-3)

- Implement hiring organization variable handling
- Add fallback logic for missing data
- Test with existing templates

### Phase 3: Work Experience Ordering (Week 4-5)
- Create ExperienceProcessor module
- Implement date parsing for multiple formats
- Build chronological sorting algorithm
- Replace hardcoded experiences in CSVContentMapper
- Test with various date formats and edge cases

### Phase 4: Integration & Testing (Week 6)
- Full pipeline integration testing
- Performance optimization
- Update ContentManager for experience context
- Ensure backward compatibility
- Create comprehensive test suite

### Phase 5: Production Deployment (Week 7)
- Documentation updates
- Migration scripts for existing data
- Monitoring setup
- Gradual rollout plan
- Performance benchmarking

## Acceptance Criteria

### Must Have (MVP)
1. ✅ Scenario 3 already working (no changes needed)

3. Scenario 2: Basic hiring org variables working with fallbacks
4. Scenario 4: Work experiences correctly ordered chronologically
5. Backward compatibility with existing templates
6. No performance degradation from current system

### Should Have
1. Complete date format standardization
2. Support for 5+ work experiences
3. Hiring manager name extraction from job postings
4. Company address formatting
5. Test coverage >85%

### Nice to Have
1. A/B testing for variable effectiveness
2. Analytics dashboard for variable usage
3. Auto-detection of variable types from templates
4. Machine learning for optimal experience ordering

## Appendices

### A. Variable Naming Conventions
- Template variables: `{{variable_name}}`
- Dynamic variables: `{variable_name}`
- System variables: `__variable_name__`

### B. Supported Data Formats
- Phone: +1 (XXX) XXX-XXXX
- Email: RFC 5322 compliant
- URL: HTTP/HTTPS only
- Address: Multi-line with postal code

### C. Error Codes
- VSE001: Missing required variable
- VSE002: Invalid variable format
- VSE003: Duplicate dynamic variable
- VSE004: Tracking URL generation failed
- VSE005: Content selection failed

## Code Implementation Examples



### Example 2: ExperienceProcessor for Scenario 4
```python
# modules/content/document_generation/experience_processor.py (NEW)
from datetime import datetime
import re

class ExperienceProcessor:
    """Process and order work experiences chronologically"""
    
    def parse_date(self, date_str):
        """Parse various date formats to datetime"""
        if not date_str or date_str.lower() in ['present', 'current', 'ongoing']:
            return datetime.now()
        
        # Try different date patterns
        patterns = [
            (r'(\d{4})-(\d{2})', '%Y-%m'),
            (r'(\w+)\s+(\d{4})', '%B %Y'),
            (r'(\d{4})', '%Y'),
            (r'(\d{2})/(\d{4})', '%m/%Y')
        ]
        
        for pattern, date_format in patterns:
            match = re.match(pattern, date_str)
            if match:
                try:
                    return datetime.strptime(match.group(0), date_format)
                except:
                    continue
        
        return datetime(2000, 1, 1)  # Default for unparseable dates
    
    def order_experiences(self, experiences):
        """Sort experiences by end date (most recent first)"""
        for exp in experiences:
            exp['parsed_end_date'] = self.parse_date(exp.get('end_date'))
            exp['parsed_start_date'] = self.parse_date(exp.get('start_date'))
        
        # Sort by end date descending, then start date descending
        sorted_exp = sorted(experiences, 
                          key=lambda x: (x['parsed_end_date'], x['parsed_start_date']), 
                          reverse=True)
        
        return sorted_exp
    
    def map_to_variables(self, ordered_experiences):
        """Map ordered experiences to numbered variables"""
        variables = {}
        
        for i, exp in enumerate(ordered_experiences, 1):
            prefix = f"work_experience_{i}"
            variables[f"{prefix}_company_name"] = exp.get('company_name', '')
            variables[f"{prefix}_job_title"] = exp.get('job_title', '')
            variables[f"{prefix}_location"] = exp.get('location', '')
            variables[f"{prefix}_dates"] = self.format_date_range(
                exp.get('start_date'), 
                exp.get('end_date')
            )
            
            # Add skills if available
            for j in range(1, 5):
                skill_key = f"skill_{j}"
                if skill_key in exp:
                    variables[f"{prefix}_skill{j}"] = exp[skill_key]
        
        return variables
    
    def format_date_range(self, start, end):
        """Format date range for display"""
        if not end or end.lower() in ['present', 'current']:
            end_str = 'Present'
        else:
            end_str = self.parse_date(end).strftime('%Y')
        
        start_str = self.parse_date(start).strftime('%Y') if start else ''
        
        return f"{start_str} - {end_str}" if start_str else end_str
```

### Example 3: Enhanced CSVContentMapper Integration
```python
# Modification to modules/content/document_generation/csv_content_mapper.py
def _resolve_work_experience_variable(self, variable_name, user_profile, content_selections):
    """Resolve work experience variables using chronological ordering"""
    from .experience_processor import ExperienceProcessor
    
    processor = ExperienceProcessor()
    
    # Get all work experiences from user profile
    experiences = user_profile.get('work_experiences', [])
    
    # Order chronologically
    ordered = processor.order_experiences(experiences)
    
    # Map to variables
    all_variables = processor.map_to_variables(ordered)
    
    # Return the requested variable
    return all_variables.get(variable_name, f"[{variable_name}]")
```

## Migration Strategy

### Phase 1: Data Migration
```sql
-- Migrate existing hardcoded experiences to dynamic system
INSERT INTO work_experiences (user_id, company_name, job_title, start_date, end_date, location)
SELECT 
    u.id,
    'Odvod Media',
    'Digital Strategist',
    '2020-01-01'::date,
    NULL,
    'Edmonton, AB'
FROM users u
WHERE NOT EXISTS (
    SELECT 1 FROM work_experiences we 
    WHERE we.user_id = u.id AND we.company_name = 'Odvod Media'
);
```

### Phase 2: Template Updates
- Audit existing templates for variable usage
- Update templates to use new variable names if needed
- Test with both old and new variable formats

### Phase 3: Gradual Rollout
1. Enable for test users first
2. Monitor for errors and performance
3. Roll out to 10% of users
4. Full deployment after validation

---

Document Version: 2.0.0
Created: September 2025
Last Updated: September 2025
Status: Updated - Reflects Current Implementation
Authors: System Architecture Team
Review Status: Ready for Technical Review