---
title: "Email Content Mapping Guide"
type: guide
component: email
status: draft
tags: []
---

# Email Content Mapping Guide
**Version:** 4.2.0
**Last Updated:** October 9, 2025
**Status:** ✅ Complete

---

## Overview

This guide documents how job application data flows through the email system and how content is mapped from database fields to email components.

**New Architecture (v4.2.0):**
- `EmailContentBuilder` - Intelligent content mapping from job data
- `EmailValidator` - Pre-send validation
- `SignatureGenerator` - Configurable signatures
- `EmailApplicationSender` - Orchestration and sending

---

## Data Flow Architecture

```
Job Application Package (from analyzed_jobs table)
             ↓
   Document Generation
   - Resume (DOCX)
   - Cover Letter (DOCX)
             ↓
   EmailContentBuilder.build_email_package()
   - Maps job data → email fields
   - Generates subject line
   - Composes email body
   - Builds attachment list
   - Creates metadata
             ↓
   EmailValidator.validate_email()
   - RFC 5322 email validation
   - Content checking
   - Attachment verification
             ↓
   EmailApplicationSender.send_job_application()
   - Sends via Gmail OAuth
   - Updates database
   - Tracks delivery
```

---

## Job Data → Email Mapping

### Input: analyzed_jobs Table Fields

**Core Job Information:**
- `id` - Job ID (integer)
- `job_title` - Job title (string)
- `company_name` - Company name (string)
- `company_id` - Company ID (integer)
- `job_description` - Full job description (text)
- `application_email` - Application email if available (string)

**Location Information:**
- `office_city` - City (string)
- `office_province` - Province/State (string)
- `office_country` - Country (string)

**Compensation:**
- `salary_low` - Minimum salary (integer)
- `salary_high` - Maximum salary (integer)

**Dates:**
- `posted_date` - When job was posted (timestamp)
- `created_at` - When record was created (timestamp)
- `submission_deadline` - Application deadline (timestamp)

**Analysis Data:**
- `compatibility_score` - Overall match score (0-100)
- `title_compatibility_score` - Title match score (0-30)
- `primary_industry` - Industry classification (string)
- `location_match` - Location preference match (boolean)

**Job Details:**
- `source_url` - Original job posting URL (string)
- `job_type` - Full-time, Part-time, etc. (string)
- `experience_level` - Entry, Mid, Senior (string)
- `hiring_manager_name` - Hiring manager if known (string)

**Generated Documents:**
- `resume_path` - Path to generated resume DOCX
- `cover_letter_path` - Path to generated cover letter DOCX

---

### Output: Email Package Components

#### 1. Recipient Determination

**Priority Order:**
1. `application_email` field (if present)
2. Extract from `job_description` text
3. Fallback to `USER_EMAIL_ADDRESS` (user's own email)

**Email Extraction Logic:**
```python
# Priority keywords for email matching
priority_keywords = ['hr', 'career', 'job', 'recruit', 'hiring', 'talent']

# Filters
skip_domains = ['example.com', 'test.com', 'noreply', 'no-reply']
```

**Result:**
- `recipient`: Email address (string)
- `is_fallback`: Boolean indicating if sent to user's email

---

#### 2. Subject Line Generation

**Format (Direct Application):**
```
Application for {job_title} Position - {display_name}
```

**With Reference ID (if EMAIL_INCLUDE_REFERENCE_ID=true):**
```
Application #YYYYMMDD-JJJ: {job_title} - {display_name}
```
- `YYYYMMDD` = Current date
- `JJJ` = Job ID (zero-padded)

**Format (Fallback):**
```
Job Application Opportunity: {job_title} at {company_name}
```

**Examples:**
- `Application for Senior Marketing Manager Position - Steve Glen`
- `Application #20251009-123: Senior Marketing Manager - Steve Glen`
- `Job Application Opportunity: Marketing Manager at Tech Corp`

---

#### 3. Email Body Composition

**Direct Application Template:**

**Structure:**
1. Greeting (personalized if `hiring_manager_name` available)
2. Opening paragraph with job title and company name
3. Key highlights (bullet points)
4. Company-specific interest paragraph
5. Attachment reference
6. Closing
7. Signature (from SignatureGenerator)

**Field Mapping:**
- `{job_title}` → `job_title`
- `{company_name}` → `company_name`
- Greeting → `hiring_manager_name` (first name) or "Hiring Manager"
- Signature → Environment variables (USER_*)

**Fallback Template (Sent to User):**

**Structure:**
1. Greeting with user's first name
2. Job details summary
3. Compatibility scores
4. Attachment list
5. Action instructions
6. Source URL

**Field Mapping:**
```
Job Title: {job_title}
Company: {company_name}
Location: {office_city}, {office_province}, {office_country}
Salary Range: ${salary_low:,} - ${salary_high:,}
Posted Date: {posted_date}

Title compatibility: {title_compatibility_score}/30
Overall score: {compatibility_score}/100
Industry: {primary_industry}
Location match: {location_match}

Source: {source_url}
```

---

#### 4. Attachment Generation

**Filename Format:**
```
{FirstName}_{LastName}_{DocumentType}_{JobTitle}_{CompanyName}.docx
```

**Example:**
```
Steve_Glen_Resume_Senior_Marketing_Manager_Tech_Innovations_Inc.docx
Steve_Glen_Cover_Letter_Senior_Marketing_Manager_Tech_Innovations_Inc.docx
```

**Sanitization Rules:**
- Spaces → Underscores
- Remove special characters (keep alphanumeric + underscore)
- Maximum length: 100 characters
- Truncate job title/company name proportionally if needed

**Attachment Metadata:**
```python
{
    'path': '/path/to/document.docx',
    'filename': 'Steve_Glen_Resume_Marketing_Manager_ABC.docx',
    'type': 'resume',  # or 'cover_letter'
    'mime_type': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
}
```

---

#### 5. Email Metadata

**Generated Metadata:**
```python
{
    'job_id': 12345,
    'job_title': 'Senior Marketing Manager',
    'company_name': 'Tech Innovations Inc',
    'company_id': 456,
    'generated_at': '2025-10-09T14:30:00',
    'reference_id': '20251009-123',  # If enabled
    'source_url': 'https://ca.indeed.com/job/12345',
    'compatibility_score': 85
}
```

**Purpose:**
- Tracking and analytics
- Database storage
- Email threading (future)
- Audit trail

---

## EmailContentBuilder Methods

### `build_email_package(job_data, generated_documents)`

**Input:**
```python
job_data = {
    # From analyzed_jobs table
    'id': int,
    'job_title': str,
    'company_name': str,
    # ... all fields listed above
}

generated_documents = {
    'resume_path': str,
    'cover_letter_path': str,
    'resume_filename': str (optional),
    'cover_letter_filename': str (optional)
}
```

**Output:**
```python
{
    'recipient': str,
    'subject': str,
    'body': str (plain text),
    'body_html': str (if EMAIL_USE_HTML=true),
    'attachments': [
        {
            'path': str,
            'filename': str,
            'type': str,
            'mime_type': str
        }
    ],
    'metadata': dict,
    'is_fallback': bool,
    'job_id': int,
    'job_title': str,
    'company_name': str
}
```

---

### `_extract_job_info(job_data)`

**Purpose:** Normalize and extract key job information

**Returns:**
```python
{
    'job_id': int,
    'job_title': str,
    'company_name': str,
    'location': str,  # Formatted: "City, Province, Country"
    'salary_range': str,  # Formatted: "$85,000 - $110,000"
    'posted_date': str,  # Formatted: "2025-10-01"
    'source_url': str,
    'application_email': str or None,
    'compatibility_score': int,
    'title_compatibility_score': int,
    'primary_industry': str,
    'location_match': bool,
    'hiring_manager_name': str or None
}
```

---

### `_determine_recipient(job_data)`

**Logic:**
1. Check `application_email` field
2. If not present, extract from `job_description`
3. If extraction fails, use `USER_EMAIL_ADDRESS`

**Returns:** Email address (string)

---

### `_build_subject_line(job_info, is_fallback)`

**Parameters:**
- `job_info`: Extracted job information
- `is_fallback`: Boolean

**Returns:** Subject line string

**Logic:**
- Direct app: "Application for {job_title} Position - {display_name}"
- With ref ID: "Application #{ref_id}: {job_title} - {display_name}"
- Fallback: "Job Application Opportunity: {job_title} at {company_name}"

---

### `_build_application_email_body(job_data, job_info)`

**Returns:** Plain text email body with:
- Personalized greeting
- Professional introduction
- Key highlights (bullets)
- Company-specific paragraph
- Closing
- Signature from SignatureGenerator

---

### `_build_attachments_list(job_info, generated_documents)`

**Returns:** List of attachment dictionaries

**Each attachment includes:**
- `path` - File system path
- `filename` - Professional formatted filename
- `type` - 'resume' or 'cover_letter'
- `mime_type` - DOCX MIME type

---

## Integration with EmailApplicationSender

### Updated Workflow

**Old (v4.1.0):**
```python
# Hardcoded templates
subject, body = compose_email_content(job_data, recipient)
attachments = [{'path': path, 'filename': filename}]
send_email_with_attachments(recipient, subject, body, attachments)
```

**New (v4.2.0):**
```python
# Intelligent content builder
documents = prepare_application_documents(job_data)
email_package = content_builder.build_email_package(job_data, documents)

# Validation
validation_result = email_validator.validate_email(
    email_package['recipient'],
    email_package['subject'],
    email_package['body'],
    email_package['attachments']
)

# Send if valid
if validation_result['can_send']:
    email_result = email_sender.send_email_with_attachments(...)
```

---

## Configuration Impact

### Environment Variables Used

**User Information:**
- `USER_EMAIL_ADDRESS` - Fallback recipient
- `USER_DISPLAY_NAME` - Used in subject lines and body
- `USER_PHONE`, `USER_LOCATION`, etc. - Signature

**Email Settings:**
- `EMAIL_USE_HTML` - Generate HTML body variant
- `EMAIL_INCLUDE_REFERENCE_ID` - Add tracking ID to subject

---

## Validation Rules

### Pre-Send Validation (EmailValidator)

**Subject Line:**
- ✓ Not empty
- ✓ Under 200 characters
- ✓ No unsubstituted variables (`{job_title}`)
- ⚠ Warning if > 60 characters (mobile truncation)

**Body:**
- ✓ Not empty
- ✓ Minimum 50 characters
- ✓ Under 50,000 characters
- ✓ No unsubstituted template variables

**Recipient:**
- ✓ Valid email format (RFC 5322)
- ✓ Not in skip list (example.com, noreply, etc.)

**Attachments:**
- ✓ Files exist and readable
- ✓ Not empty (size > 0)
- ✓ Under 25MB each (Gmail limit)
- ✓ Total size under 25MB

---

## Examples

### Example 1: Direct Application Email

**Input Job Data:**
```python
{
    'id': 123,
    'job_title': 'Marketing Manager',
    'company_name': 'ABC Corporation',
    'application_email': 'careers@abc.com',
    'hiring_manager_name': 'Jane Smith',
    'office_city': 'Toronto',
    'office_province': 'Ontario',
    'salary_low': 70000,
    'salary_high': 90000
}
```

**Generated Email:**
```
To: careers@abc.com
Subject: Application for Marketing Manager Position - Steve Glen

Dear Jane,

I am writing to express my strong interest in the Marketing Manager position at ABC Corporation...

[Professional content with bullet points]

Best regards,
Steve Glen
Marketing Communications Professional

Phone: (780) 555-0123
Email: steve.glen@gmail.com
LinkedIn: linkedin.com/in/steveglen
Location: Edmonton, Alberta, Canada
```

**Attachments:**
- `Steve_Glen_Resume_Marketing_Manager_ABC_Corporation.docx`
- `Steve_Glen_Cover_Letter_Marketing_Manager_ABC_Corporation.docx`

---

### Example 2: Fallback Email (No Application Email)

**Input Job Data:**
```python
{
    'id': 456,
    'job_title': 'Senior Developer',
    'company_name': 'Tech Startup',
    'application_email': None,  # Not provided
    'source_url': 'https://ca.indeed.com/job/456',
    'compatibility_score': 92,
    'title_compatibility_score': 27
}
```

**Generated Email:**
```
To: your.email@gmail.com  # User's own email
Subject: Job Application Opportunity: Senior Developer at Tech Startup

Steve,

I've identified a potential job opportunity that matches your preferences...

Job Title: Senior Developer
Company: Tech Startup
Location: Toronto, Ontario, Canada
Salary Range: Not specified
Posted Date: 2025-10-09

The position appears to be a strong match based on:
• Job title compatibility: 27/30 points
• Overall compatibility score: 92/100 points
...

Since no direct application email was found, you'll need to apply through:
https://ca.indeed.com/job/456
```

---

## Troubleshooting

### Issue: Recipient always fallback

**Cause:** No `application_email` and extraction failing

**Check:**
1. Verify `application_email` field populated in database
2. Check `job_description` contains valid email
3. Review email extraction regex patterns

**Solution:**
```python
# Extract email manually from job description
extracted = content_builder._extract_email_from_text(job_description)
print(f"Extracted: {extracted}")
```

---

### Issue: Attachment filename too long

**Cause:** Long job title or company name

**Behavior:** Automatic truncation to 100 characters

**Check:**
```python
# Test filename generation
filename = content_builder._generate_attachment_filename(
    'Resume',
    'Very Long Job Title With Many Words',
    'Very Long Company Name With Many Words'
)
print(len(filename), filename)
```

---

### Issue: Template variables not substituted

**Cause:** Missing field in job_data

**Detection:** EmailValidator will catch unsubstituted `{variables}`

**Solution:** Ensure all template variables have data:
- `{job_title}` → required
- `{company_name}` → required
- `{hiring_manager_name}` → optional (falls back to "Hiring Manager")

---

## Best Practices

### 1. Always Provide Core Fields
Required minimum:
- `id`
- `job_title`
- `company_name`

### 2. Enrich Job Data When Possible
Recommended:
- `application_email` (avoid fallback)
- `hiring_manager_name` (personalization)
- `salary_low`, `salary_high` (informative)
- `source_url` (trackability)

### 3. Validate Before Calling Content Builder
```python
required_fields = ['id', 'job_title', 'company_name']
missing = [f for f in required_fields if not job_data.get(f)]
if missing:
    raise ValueError(f"Missing required fields: {missing}")
```

### 4. Handle Validation Failures Gracefully
```python
validation_result = validator.validate_email(...)
if not validation_result['can_send']:
    logger.error(f"Validation failed: {validation_result['errors']}")
    # Don't send, log for review
```

### 5. Log Email Metadata
```python
logger.info(f"Email generated for job {job_id}: "
            f"recipient={recipient}, "
            f"subject='{subject}', "
            f"attachments={len(attachments)}")
```

---

## Related Documentation

- **Email Configuration Guide:** `docs/email-configuration-guide.md`
- **Email Address Decision:** `tasks/email-address-decision-guide.md`
- **Email Refinement PRD:** `tasks/email-refinement-prd.md`
- **Signature Generator:** `modules/email_integration/signature_generator.py`
- **Email Validator:** `modules/email_integration/email_validator.py`

---

**Document Status:** ✅ Complete
**Version:** 4.2.0
**Last Updated:** October 9, 2025
