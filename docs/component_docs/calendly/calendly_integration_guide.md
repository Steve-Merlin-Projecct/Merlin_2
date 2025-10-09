# Calendly Integration - User Guide

**Version**: 4.2.0
**Last Updated**: October 9, 2025
**Status**: Production Ready

## Table of Contents

- [Overview](#overview)
- [What is Calendly Integration?](#what-is-calendly-integration)
- [Benefits](#benefits)
- [Quick Start](#quick-start)
- [Setup Instructions](#setup-instructions)
- [Usage Examples](#usage-examples)
- [Troubleshooting](#troubleshooting)
- [FAQ](#faq)

---

## Overview

The Calendly Integration automatically tracks when hiring managers click on your Calendly scheduling link in job application documents. This provides valuable analytics about which jobs generate the most interest and helps you measure engagement beyond just sending applications.

### What Gets Tracked?

- **Calendly scheduling links** - When someone clicks to schedule a meeting
- **LinkedIn profile links** - When someone views your professional profile
- **Portfolio website links** - When someone visits your portfolio

### What Information is Captured?

For each click, the system records:
- Which job application generated the click
- When the click occurred
- What device/browser was used (user agent)
- Where the click came from (referrer URL)
- Geographic information (IP address)

---

## What is Calendly Integration?

### Before Integration

Your resume/cover letter contains:
```
Schedule a meeting: https://calendly.com/steve-glen/30min
```

**Problem**: You have no idea if anyone actually clicked the link.

### After Integration

Your resume/cover letter contains:
```
Schedule a meeting: http://yourdomain.com/track/lt_calendly_abc123
```

**Benefit**:
1. Link redirects to your Calendly page (invisible to user)
2. Click is recorded with job/application context
3. You see analytics: "5 people clicked Calendly link for Marketing Manager at Tech Corp"

---

## Benefits

### For Job Seekers

1. **Measure Engagement**: Know which companies are interested enough to schedule meetings
2. **Optimize Applications**: Focus on job types that generate most clicks
3. **Track Success Rate**: Compare applications sent → Calendly clicks → interviews scheduled
4. **Professional Insight**: Understand which aspects of your profile drive engagement

### For Recruiters/Hiring Managers

1. **Candidate Interest**: See which candidates are most engaged
2. **Process Analytics**: Track time from application to meeting request
3. **Source Attribution**: Understand which job boards drive best candidates

---

## Quick Start

### Step 1: Configure Your Calendly URL

Add your Calendly URL to the database:

```sql
UPDATE user_candidate_info
SET calendly_url = 'https://calendly.com/your-username/30min'
WHERE user_id = 'your_user_id';
```

Or use the Python interface:

```python
from modules.user_management.candidate_profile_manager import CandidateProfileManager

manager = CandidateProfileManager()
manager.update_calendly_url(
    calendly_url="https://calendly.com/your-username/30min",
    user_id="your_user_id"
)
```

### Step 2: Update Your Templates

Ensure your resume/cover letter templates include the variable:

```
Schedule a meeting: {{calendly_url}}
```

### Step 3: Generate Documents with Tracking

When generating documents via API, include `job_id` and `application_id`:

```bash
curl -X POST http://localhost:5000/resume \
  -H "Content-Type: application/json" \
  -d '{
    "personal": {...},
    "job_id": "550e8400-e29b-41d4-a716-446655440000",
    "application_id": "650e8400-e29b-41d4-a716-446655440001"
  }'
```

### Step 4: View Analytics

Query link analytics to see engagement:

```bash
GET /api/link-tracking/analytics/lt_calendly_abc123
```

---

## Setup Instructions

### Prerequisites

- PostgreSQL database with `user_candidate_info` table
- LinkTracking system operational
- Document templates with `{{calendly_url}}` variable
- Active Calendly account

### Detailed Setup

#### 1. Database Configuration

Ensure `user_candidate_info` table has required columns:

```sql
-- Check if columns exist
SELECT column_name
FROM information_schema.columns
WHERE table_name = 'user_candidate_info'
AND column_name IN ('calendly_url', 'linkedin_url', 'portfolio_url');
```

Expected result:
```
 column_name
----------------
 calendly_url
 linkedin_url
 portfolio_url
```

#### 2. Set Your URLs

```sql
-- For Steve Glen (example)
UPDATE user_candidate_info
SET
    calendly_url = 'https://calendly.com/steve-glen/30min',
    linkedin_url = 'https://linkedin.com/in/steve-glen',
    portfolio_url = 'https://steveglen.com'
WHERE user_id = 'steve_glen';
```

#### 3. Verify Configuration

```python
from modules.user_management.candidate_profile_manager import CandidateProfileManager

manager = CandidateProfileManager()
info = manager.get_candidate_info("steve_glen")

print(f"Calendly URL: {info['calendly_url']}")
print(f"LinkedIn URL: {info['linkedin_url']}")
print(f"Portfolio URL: {info['portfolio_url']}")
```

Expected output:
```
Calendly URL: https://calendly.com/steve-glen/30min
LinkedIn URL: https://linkedin.com/in/steve-glen
Portfolio URL: https://steveglen.com
```

#### 4. Environment Variables

Optional: Configure tracking behavior

```bash
# .env file
ENABLE_URL_TRACKING=true
BASE_REDIRECT_URL=https://your-domain.com/track
```

---

## Usage Examples

### Example 1: Generate Resume with Tracking

```python
import requests

response = requests.post('http://localhost:5000/resume', json={
    "personal": {
        "full_name": "Steve Glen",
        "email": "steve@example.com",
        "phone": "(780) 555-0123"
    },
    "professional_summary": "Marketing professional with 10+ years experience",
    "target_position": "Marketing Manager",

    # Enable tracking for this specific job
    "job_id": "550e8400-e29b-41d4-a716-446655440000",
    "application_id": "650e8400-e29b-41d4-a716-446655440001"
})

print(response.json())
# {'success': True, 'filename': 'resume_Steve_Glen_20251009.docx', ...}
```

### Example 2: Generate Cover Letter with Tracking

```python
response = requests.post('http://localhost:5000/cover-letter', json={
    "personal": {
        "full_name": "Steve Glen",
        "email": "steve@example.com"
    },
    "recipient": {
        "name": "Jane Smith",
        "company": "Tech Corp"
    },
    "position": {
        "title": "Marketing Manager"
    },
    "content": {
        "opening_paragraph": "I am excited to apply...",
        "body_paragraphs": ["My experience includes..."],
        "closing_paragraph": "I look forward to hearing from you."
    },

    # Same job_id as resume for consolidated analytics
    "job_id": "550e8400-e29b-41d4-a716-446655440000",
    "application_id": "650e8400-e29b-41d4-a716-446655440001"
})
```

### Example 3: Query Analytics

```python
import requests

# Get analytics for specific tracking ID
response = requests.get('http://localhost:5000/api/link-tracking/analytics/lt_calendly_abc123')
analytics = response.json()

print(f"Total Clicks: {analytics['click_statistics']['total_clicks']}")
print(f"Unique Sessions: {analytics['click_statistics']['unique_sessions']}")
print(f"First Click: {analytics['click_statistics']['first_click']}")
```

Output:
```
Total Clicks: 5
Unique Sessions: 3
First Click: 2025-10-09T15:00:00Z
```

### Example 4: Workflow Automation

```python
from modules.user_management.candidate_profile_manager import CandidateProfileManager
from modules.link_tracking.link_tracker import LinkTracker
import requests
import uuid

# 1. Get candidate info
profile = CandidateProfileManager()
candidate = profile.get_candidate_info("steve_glen")

# 2. Generate unique IDs for this application
job_id = str(uuid.uuid4())
application_id = str(uuid.uuid4())

# 3. Generate both resume and cover letter with same job context
resume = requests.post('http://localhost:5000/resume', json={
    "personal": candidate,
    "job_id": job_id,
    "application_id": application_id
})

cover_letter = requests.post('http://localhost:5000/cover-letter', json={
    "personal": candidate,
    "recipient": {"name": "Hiring Manager", "company": "Tech Corp"},
    "position": {"title": "Marketing Manager"},
    "content": {...},
    "job_id": job_id,
    "application_id": application_id
})

# 4. Later, check analytics for this job
tracker = LinkTracker()
job_summary = tracker.get_job_link_summary(job_id)
print(f"Calendly clicks for this job: {job_summary['Calendly']['click_count']}")
```

---

## Troubleshooting

### Problem: Calendly URL Not Appearing in Document

**Symptoms**:
- Generated document doesn't have Calendly link
- Template variable `{{calendly_url}}` remains in document

**Possible Causes**:
1. Calendly URL not configured in database
2. Template doesn't contain `{{calendly_url}}` variable
3. User ID mismatch

**Solution**:

```python
# Check if URL is configured
from modules.user_management.candidate_profile_manager import CandidateProfileManager

manager = CandidateProfileManager()
info = manager.get_candidate_info("your_user_id")

if info['calendly_url'] is None:
    print("❌ Calendly URL not configured!")
    # Set it:
    manager.update_calendly_url(
        "https://calendly.com/your-username/30min",
        "your_user_id"
    )
else:
    print(f"✅ Calendly URL configured: {info['calendly_url']}")
```

---

### Problem: Link Not Being Tracked

**Symptoms**:
- Document contains original Calendly URL (not tracked version)
- No entries in `link_tracking` table

**Possible Causes**:
1. `job_id` or `application_id` not provided in API request
2. URL tracking disabled (`ENABLE_URL_TRACKING=false`)
3. LinkTracker service unavailable

**Solution**:

```bash
# 1. Check environment variable
echo $ENABLE_URL_TRACKING
# Should output: true

# 2. Verify job_id in request
curl -X POST http://localhost:5000/resume \
  -H "Content-Type: application/json" \
  -d '{
    "personal": {...},
    "job_id": "MAKE-SURE-THIS-IS-PRESENT",
    "application_id": "AND-THIS-TOO"
  }'

# 3. Check LinkTracker health
curl http://localhost:5000/api/link-tracking/health
```

---

### Problem: Tracked URL Redirects to Wrong Page

**Symptoms**:
- Clicking tracked link doesn't go to Calendly
- Gets 404 error or wrong destination

**Possible Causes**:
1. Original Calendly URL incorrect in database
2. Tracking ID doesn't exist
3. Link deactivated

**Solution**:

```sql
-- Verify original URL in database
SELECT tracking_id, original_url, is_active
FROM link_tracking
WHERE tracking_id = 'lt_calendly_abc123';

-- Check if link is active
-- is_active should be TRUE

-- Verify original URL is correct
-- original_url should be: https://calendly.com/your-username/meeting-type
```

---

### Problem: No Click Data Recorded

**Symptoms**:
- Clicks happen but `link_clicks` table empty
- Analytics show 0 clicks

**Possible Causes**:
1. Redirect handler not capturing clicks
2. Database connection issue
3. Tracking ID mismatch

**Solution**:

```sql
-- Check if redirect endpoint is working
-- Visit: http://localhost:5000/track/lt_calendly_abc123

-- Check link_clicks table
SELECT * FROM link_clicks
WHERE tracking_id = 'lt_calendly_abc123'
ORDER BY clicked_at DESC;

-- If no results, check link_tracking table exists
SELECT tracking_id, redirect_url
FROM link_tracking
WHERE tracking_id = 'lt_calendly_abc123';
```

---

## FAQ

### Q: Do I need to provide both job_id and application_id?

**A**: No, either one is sufficient for tracking. However, providing both gives you more granular analytics:
- `job_id` only: Track clicks per job posting
- `application_id` only: Track clicks per application
- Both: Full context for comprehensive analytics

### Q: Can I track other URLs besides Calendly?

**A**: Yes! The system tracks three types of URLs:
1. `{{calendly_url}}` - Scheduling links
2. `{{linkedin_url}}` - LinkedIn profile
3. `{{portfolio_url}}` - Personal website/portfolio

### Q: What happens if tracking fails?

**A**: The system uses graceful fallback:
1. Attempts to create tracked URL
2. If fails, uses original URL instead
3. Document generation continues (never fails)
4. Error logged for monitoring

### Q: Can I disable tracking for specific documents?

**A**: Yes, two ways:
1. **Don't provide** `job_id`/`application_id` in request (backward compatible)
2. **Set environment variable**: `ENABLE_URL_TRACKING=false` (disables globally)

### Q: How long is click data stored?

**A**: Click data is stored indefinitely by default. However:
- IP addresses can be anonymized after 90 days (privacy compliance)
- You can implement custom retention policies
- GDPR compliance tools available for data deletion

### Q: Can hiring managers see they're being tracked?

**A**: No. The tracking is transparent:
1. They click your Calendly link
2. Instant redirect to your actual Calendly page
3. No visible difference in user experience
4. URL may show redirect domain briefly (< 1 second)

### Q: What if I change my Calendly URL?

**A**: Update it in the database:

```python
from modules.user_management.candidate_profile_manager import CandidateProfileManager

manager = CandidateProfileManager()
manager.update_calendly_url(
    "https://calendly.com/new-username/new-meeting-type",
    "your_user_id"
)
```

New documents will use the new URL. Existing tracked links continue working with old URL.

### Q: Can I use custom tracking domains?

**A**: Yes, configure `BASE_REDIRECT_URL`:

```bash
# .env file
BASE_REDIRECT_URL=https://tracking.yourdomain.com/track
```

This makes tracked URLs look like: `https://tracking.yourdomain.com/track/lt_calendly_abc123`

### Q: How accurate are the click analytics?

**A**: Very accurate. The system tracks:
- ✅ Unique sessions (based on session ID)
- ✅ Total clicks (including repeat clicks)
- ✅ Click timing (timestamp)
- ✅ Click source (email, LinkedIn, direct, etc.)
- ✅ Device information (user agent)

Note: Some corporate firewalls or privacy tools may block tracking.

---

## Best Practices

### 1. Consistent Job IDs

Use the same `job_id` for all documents related to one job:

```python
job_id = str(uuid.uuid4())  # Generate once

# Use for resume
requests.post('/resume', json={..., "job_id": job_id})

# Use for cover letter
requests.post('/cover-letter', json={..., "job_id": job_id})

# Analytics will show combined metrics
```

### 2. Meaningful Application IDs

Generate unique `application_id` per application attempt:

```python
application_id = f"app_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4()}"
```

### 3. Regular Analytics Review

Schedule weekly analytics review:

```python
# Get link performance for last 7 days
tracker = LinkTracker()
report = tracker.get_link_performance_report(days=7)

print(f"Total clicks this week: {report['overall_statistics']['total_clicks']}")
print(f"Most clicked link type: {report['function_performance'][0]['function']}")
```

### 4. Template Consistency

Use consistent variable placement in templates:

```
Dear Hiring Manager,

I'm excited about this opportunity. Let's schedule a time to discuss:
{{calendly_url}}

You can also view my professional background:
LinkedIn: {{linkedin_url}}
Portfolio: {{portfolio_url}}
```

### 5. Privacy Compliance

If operating in EU/EEA:
- Implement IP anonymization after 90 days
- Provide data deletion upon request
- Respect DNT (Do Not Track) headers

---

## Additional Resources

- [API Documentation](../../api/calendly-integration-api.md)
- [Link Tracking System Documentation](../link_tracking/link_tracking_system.md)
- [Database Schema Reference](../../../export/database_schema_reference.md)
- [External Domain Integration Guide](../../../export/external_domain_integration_guide.md)

---

## Support

For issues or questions:
1. Check [Troubleshooting](#troubleshooting) section above
2. Review [FAQ](#faq) for common questions
3. Check system logs for detailed error messages
4. Consult technical documentation for advanced topics

---

**Document Version**: 1.0
**Last Updated**: October 9, 2025
**Maintained By**: Development Team
