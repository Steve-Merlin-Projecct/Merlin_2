# Email Refinement - Product Requirements Document (PRD)
**Version:** 1.0 (Draft)
**Branch:** task/11-email
**Date:** October 9, 2025
**Owner:** Steve Glen
**Status:** 🟡 DRAFT - Awaiting Approval

---

## Product Vision

Enhance the automated job application email system to maximize readability and credibility while maintaining the authentic, personal voice of an individual job seeker—not a corporate recruitment agency.

**Core Principle:** Professional presentation that feels genuinely human, not automated.

---

## Problem Statement

### Current State
- Email integration functional but uses plain text only
- No personalization beyond basic template variables
- Generic "Dear Hiring Manager" greetings
- Hardcoded contact information
- No preview or quality control workflow
- Email sending currently disabled (safety)
- OAuth authentication incomplete

### Pain Points
1. **Readability:** Plain text emails lack clickable links and visual hierarchy
2. **Credibility:** Generic greetings and templates reduce personalization
3. **Professionalism:** Missing professional signature and structured formatting
4. **Tracking:** No visibility into delivery success or failures
5. **Quality Control:** Cannot preview emails before sending
6. **Authenticity vs Polish:** Need to balance professional appearance with individual authenticity

### Success Metrics
- **Primary:** Response rate from job applications (% replies received)
- **Secondary:** Email delivery rate (% successfully delivered, not bounced)
- **Tertiary:** Time saved per application (automation efficiency)
- **Quality:** Errors per 100 emails sent (typos, broken links, formatting issues)

---

## Goals & Non-Goals

### Goals ✅
1. Improve email readability through better structure and formatting
2. Enhance credibility with personalization and research
3. Implement quality control with preview workflow
4. Add email delivery tracking and error handling
5. Maintain authentic, individual voice (not corporate/agency)
6. Enable configurable templates for different industries
7. Complete Gmail OAuth setup for production use

### Non-Goals ❌
1. ~~Build a full CRM or applicant tracking system~~
2. ~~Create heavily branded or graphic-rich HTML emails~~
3. ~~Implement mass email marketing features~~
4. ~~Add complex scheduling or drip campaign logic~~
5. ~~Build hiring manager relationship management~~
6. ~~Replace the core job scraping or analysis systems~~

---

## User Stories

### As Steve (Job Seeker)
1. **US-1:** I want my emails to look professional but authentic, so hiring managers see me as an individual candidate, not a recruitment agency
2. **US-2:** I want to preview emails before they're sent, so I can verify quality and catch errors
3. **US-3:** I want emails automatically customized for each job, so they show genuine interest and research
4. **US-4:** I want to know if my emails were delivered successfully, so I can troubleshoot issues
5. **US-5:** I want clickable links in my emails, so hiring managers can easily view my LinkedIn or portfolio

### As a Hiring Manager (Recipient)
6. **US-6:** I want to quickly scan the email to understand the candidate's qualifications
7. **US-7:** I want to see personalized content that shows the candidate researched our company
8. **US-8:** I want clickable links to view the candidate's portfolio and credentials
9. **US-9:** I want emails that feel personally written, not mass-generated
10. **US-10:** I want properly formatted emails that work on mobile and desktop

---

## Requirements

### Phase 1: Foundation (Week 1) - REQUIRED FOR MVP

#### R1.1: HTML Email Template (Hybrid Approach)
**Priority:** P0 (Blocker)
**Decision Required:** ⚠️ Choose HTML approach before implementation

**Option A: Enhanced Plain Text HTML** (RECOMMENDED)
```
Description: HTML that looks like plain text
- Clean typography (Arial, sans-serif, 14px)
- Clickable hyperlinks
- Simple bold for emphasis
- No colors, graphics, or corporate styling
- Automatic plain text fallback
- Mobile responsive

Pros:
+ Looks authentic and personal
+ Better UX (clickable links)
+ Works on all devices
+ Easy to maintain
+ Industry-appropriate for marketing/comms

Cons:
- Still technically HTML (some purists may object)
- Requires HTML email testing

Acceptance Criteria:
- Email renders as plain text aesthetic in all major clients
- Links are clickable (LinkedIn, portfolio, phone)
- Fallback plain text version auto-generated
- No graphics, colors, or corporate branding
- Mobile-friendly formatting
- Maximum width: 650px
```

**Option B: Pure Plain Text** (CONSERVATIVE)
```
Description: ASCII plain text only
- No HTML formatting
- Manual URL typing
- Simple line breaks
- Traditional business letter format

Pros:
+ Maximum authenticity
+ Works everywhere
+ No rendering issues
+ Fastest to implement

Cons:
- Links not clickable (copy/paste required)
- No visual hierarchy
- Looks dated
- Poor mobile UX

Acceptance Criteria:
- Text/plain MIME type only
- No HTML alternative
- 80-character line wrapping
- ASCII characters only
```

**Option C: Configurable Per Job** (FLEXIBLE)
```
Description: Choose HTML or plain text based on industry
- Template flag: use_html (boolean)
- Auto-select based on industry/company type
- Manual override available

Pros:
+ Best of both worlds
+ Adapt to industry norms
+ Maximum flexibility

Cons:
- More complex implementation
- Requires industry classification
- Testing both paths

Acceptance Criteria:
- Template selector in job data
- Industry-based auto-detection
- Manual override in API
- Both paths tested and working
```

**👉 DECISION NEEDED:** Which option to implement? (Edit this section)

**Selected Option:** _[PENDING - Please select Option A, B, or C above]_

---

#### R1.2: Professional Email Headers
**Priority:** P0 (Blocker)

**Requirements:**
- Display name: `"Steve Glen" <{USER_EMAIL_ADDRESS}>`
- Reply-To header: Same as From (unless specified otherwise)
- Subject line format: `"Application for [Job Title] - Steve Glen"`
- Optional reference ID: `"Application #[YYYYMMDD-NNN]: [Job Title] - Steve Glen"`

**Configuration Variables:**
```bash
USER_EMAIL_ADDRESS=your.professional.email@gmail.com  # ⚠️ TO BE CONFIGURED
USER_DISPLAY_NAME="Steve Glen"
```

**Acceptance Criteria:**
- [ ] Email appears as "Steve Glen" in inbox, not raw email address
- [ ] Reply goes to correct address
- [ ] Subject line under 60 characters (mobile preview)
- [ ] Reference ID optional via configuration flag
- [ ] Email address configurable via environment variable (not hardcoded)

**Implementation File:** `modules/email_integration/gmail_oauth_official.py`

---

#### R1.3: Professional Signature Block
**Priority:** P0 (Blocker)

**Requirements:**
```
Best regards,
Steve Glen
Marketing Communications Professional

📞 {USER_PHONE}
📧 {USER_EMAIL_ADDRESS}
🔗 LinkedIn: {USER_LINKEDIN_URL}
📍 {USER_LOCATION}
```

**Configuration Variables:**
```bash
# User Contact Information (⚠️ ALL TO BE CONFIGURED)
USER_DISPLAY_NAME="Steve Glen"
USER_EMAIL_ADDRESS=your.professional.email@gmail.com
USER_PHONE="(780) 555-0123"  # Or your actual phone number
USER_LINKEDIN_URL="linkedin.com/in/steveglen"
USER_LOCATION="Edmonton, Alberta, Canada"
USER_PROFESSIONAL_TITLE="Marketing Communications Professional"

# Optional Portfolio/Website
USER_PORTFOLIO_URL=""  # Optional
USER_WEBSITE_URL=""    # Optional
```

**Acceptance Criteria:**
- [ ] Structured contact information
- [ ] Professional title/tagline (configurable)
- [ ] All contact methods included
- [ ] Icons optional (if HTML enabled)
- [ ] Links clickable (if HTML enabled)
- [ ] Plain text fallback version
- [ ] All values configurable via environment variables (no hardcoded personal info)

**Configuration:**
- Stored in environment variables (.env file)
- Easy to update without code changes
- Support multiple profiles (future: different personas)

**Implementation File:** `modules/email_integration/signature_generator.py` (new)

---

#### R1.4: Gmail OAuth Setup Completion
**Priority:** P0 (Blocker)

**Requirements:**
- Complete OAuth 2.0 authentication flow for {USER_EMAIL_ADDRESS}
- Store credentials securely
- Test email sending functionality
- Disable mock email sender

**Pre-requisites:**
- [ ] User email address decided and configured in .env (USER_EMAIL_ADDRESS)
- [ ] Gmail account created/accessible for that email address
- [ ] OAuth credentials downloaded from Google Cloud Console

**Acceptance Criteria:**
- [ ] `storage/gmail_token.json` created and valid
- [ ] Test email successfully sent to {USER_EMAIL_ADDRESS} (yourself)
- [ ] OAuth status endpoint returns `authenticated: true`
- [ ] Mock sender disabled in production
- [ ] Email sends from correct address (USER_EMAIL_ADDRESS)

**Implementation Files:**
- `modules/email_integration/gmail_oauth_official.py`
- `modules/email_integration/email_disabled.py`
- `modules/workflow/email_application_sender.py`

**Setup Steps:**
1. Update .env with USER_EMAIL_ADDRESS
2. Ensure Gmail account accessible
3. Run OAuth flow: `POST /api/email/oauth/authorize`
4. Complete authentication in browser
5. Verify token created: `ls storage/gmail_token.json`
6. Test send: `POST /api/email/test` with test_email={USER_EMAIL_ADDRESS}

---

### Phase 2: Quality & Personalization (Week 2-3) - HIGH VALUE

#### R2.1: Email Preview Endpoint
**Priority:** P1 (High)

**Requirements:**
- REST API endpoint: `POST /api/email/preview`
- Generate full email preview with rendered HTML
- Return both HTML and plain text versions
- No actual sending (dry run)

**Request Format:**
```json
{
  "job_id": "12345",
  "template_type": "professional_application",
  "preview_mode": "html"  // or "text"
}
```

**Response Format:**
```json
{
  "success": true,
  "preview": {
    "from": "Steve Glen <1234.s.t.e.v.e.glen@gmail.com>",
    "to": "hiring@company.com",
    "subject": "Application for Marketing Manager - Steve Glen",
    "body_html": "<html>...</html>",
    "body_text": "Plain text version...",
    "attachments": [
      {"filename": "Steve_Glen_Resume.pdf", "size": "145 KB"},
      {"filename": "Steve_Glen_Cover_Letter.pdf", "size": "95 KB"}
    ],
    "validation": {
      "errors": [],
      "warnings": ["No hiring manager name found - using generic greeting"]
    }
  }
}
```

**Acceptance Criteria:**
- [ ] Preview endpoint functional
- [ ] Both HTML and plain text previews
- [ ] Validation warnings included
- [ ] Attachment metadata shown
- [ ] No email actually sent

**Implementation File:** `modules/email_integration/email_api.py`

---

#### R2.2: Hiring Manager Name Extraction
**Priority:** P1 (High)

**Requirements:**
- Extract hiring manager name from job description
- Support common formats:
  - "Contact: Jane Smith"
  - "Hiring Manager: John Doe"
  - "Report to: Sarah Johnson"
  - Email signatures with names
- Fallback to company-based greeting if not found

**Greeting Priority:**
```
1. "Dear [First Name] [Last Name]," (if full name found)
2. "Dear [First Name]," (if first name only)
3. "Dear [Company Name] Hiring Team," (if no name but have company)
4. "Dear Hiring Manager," (fallback)
```

**Acceptance Criteria:**
- [ ] Name extraction regex patterns tested
- [ ] 80%+ accuracy on sample job descriptions
- [ ] Graceful fallback to generic greeting
- [ ] Names validated (no email addresses, no gibberish)
- [ ] Stored in database for future reference

**Implementation File:** `modules/workflow/email_application_sender.py`

---

#### R2.3: Job-Specific Bullet Point Customization
**Priority:** P1 (High)

**Requirements:**
- Analyze job description requirements
- Select 3-5 most relevant experience bullet points
- Customize based on required skills/keywords
- Maintain authentic voice

**Customization Logic:**
```python
# Example keywords → bullet point mapping
keywords = {
    "digital marketing": "Led comprehensive digital marketing campaigns resulting in 300%+ ROI",
    "google analytics": "Advanced proficiency in Google Analytics, Google Ads, and social media platforms",
    "content strategy": "Created and managed content strategies for B2B and B2C audiences",
    "team leadership": "Cross-functional team leadership across marketing, design, and development",
    "budget management": "Expert in budget management (\$100,000+ with proven ROI)"
}
```

**Acceptance Criteria:**
- [ ] Keyword extraction from job description
- [ ] Bullet points ranked by relevance
- [ ] Top 5 selected automatically
- [ ] Manual override available
- [ ] Natural language flow maintained

**Implementation File:** `modules/email_integration/dynamic_email_generator.py`

---

#### R2.4: Email Validation & Quality Checks
**Priority:** P1 (High)

**Requirements:**
Pre-send validation:
- ✅ Email address RFC 5322 compliance
- ✅ All URLs accessible (HTTP 200 check)
- ✅ Attachments exist and readable
- ✅ Attachment size limits (< 25MB total)
- ✅ Spell check (basic)
- ✅ Grammar check (basic)
- ⚠️ Template variable substitution complete
- ⚠️ No broken links or missing images

**Acceptance Criteria:**
- [ ] Validation runs before every send
- [ ] Errors block sending (hard fails)
- [ ] Warnings logged but don't block (soft fails)
- [ ] Validation results in preview endpoint
- [ ] Clear error messages for debugging

**Implementation File:** `modules/email_integration/email_validator.py` (new)

---

### Phase 3: Tracking & Reliability (Month 2) - MEDIUM PRIORITY

#### R3.1: Email Delivery Tracking
**Priority:** P2 (Medium)

**Requirements:**
- Unique tracking ID per email
- Delivery status logging
- Bounce detection and handling
- Error categorization

**Tracking Data:**
```python
{
  "tracking_id": "email_20251009_123456",
  "job_id": "12345",
  "sent_to": "hiring@company.com",
  "sent_at": "2025-10-09T14:30:00Z",
  "status": "delivered",  // sent, delivered, bounced, failed
  "gmail_message_id": "msg_xyz789",
  "thread_id": "thread_abc123",
  "error": null,
  "retry_count": 0
}
```

**Acceptance Criteria:**
- [ ] Tracking ID generated for every email
- [ ] Status stored in database
- [ ] Bounce notifications handled
- [ ] Failed sends logged with error details
- [ ] Retry logic for transient failures (3 attempts)

**Implementation File:** `modules/email_integration/email_tracking.py` (new)

---

#### R3.2: Email Authentication Setup
**Priority:** P2 (Medium)

**Requirements:**
- Verify SPF record for sending domain
- Configure DKIM signing
- Set up DMARC policy
- Monitor sender reputation

**Acceptance Criteria:**
- [ ] SPF record verified: `v=spf1 include:_spf.google.com ~all`
- [ ] DKIM enabled in Gmail settings
- [ ] DMARC policy published: `v=DMARC1; p=none; rua=mailto:...`
- [ ] Documentation created for DNS setup
- [ ] Deliverability rate > 95%

**Implementation File:** `docs/email-authentication-setup.md` (new)

---

#### R3.3: Attachment Metadata Enhancement
**Priority:** P2 (Medium)

**Requirements:**
- Descriptive filenames: `Steve_Glen_Resume_Marketing_Manager_ABC_Company.pdf`
- Document metadata (author, title, subject)
- Filename sanitization (no special characters)
- Consistent naming convention

**Filename Template:**
```
[Candidate_Name]_[Document_Type]_[Job_Title]_[Company_Name].pdf
Example: Steve_Glen_Resume_Marketing_Manager_ABC_Corp.pdf
```

**Acceptance Criteria:**
- [ ] Filenames follow template
- [ ] Special characters removed (spaces → underscores)
- [ ] Length limit: 100 characters
- [ ] Document metadata set correctly
- [ ] Filename preview in email body

**Implementation File:** `modules/workflow/email_application_sender.py`

---

### Phase 4: Advanced Features (Month 3+) - NICE TO HAVE

#### R4.1: Template Library
**Priority:** P3 (Low)

**Requirements:**
- Multiple template variations (formal, casual, executive)
- Industry-specific templates
- A/B testing framework
- Template performance metrics

**Templates:**
1. **Professional** (default) - Marketing, business roles
2. **Conservative** - Finance, legal, government
3. **Creative** - Design, marketing, media
4. **Executive** - Senior leadership roles
5. **Technical** - Engineering, IT roles

**Acceptance Criteria:**
- [ ] 5+ templates available
- [ ] Template selection API
- [ ] Performance tracking per template
- [ ] Easy template editing (no code changes)

**Implementation File:** `modules/email_integration/template_library.py` (new)

---

#### R4.2: Company Research Integration
**Priority:** P3 (Low)

**Requirements:**
- Automatic company research (via web search or API)
- Extract recent news, achievements, or announcements
- Insert 1-2 sentences of company-specific content
- Cache research results (avoid redundant searches)

**Research Sources:**
- Company website
- Recent news articles
- LinkedIn company page
- Press releases

**Acceptance Criteria:**
- [ ] Company research automated
- [ ] Relevant insights extracted
- [ ] Integrated into email template
- [ ] Research cached for 30 days
- [ ] Fallback if research fails (no blocking)

**Implementation File:** `modules/ai_job_description_analysis/company_research.py` (new)

---

#### R4.3: Email Analytics Dashboard
**Priority:** P3 (Low)

**Requirements:**
- Dashboard showing email performance
- Metrics: sent, delivered, bounced, response rate
- Per-template analytics
- Time-series charts

**Metrics:**
- Total emails sent
- Delivery rate (%)
- Bounce rate (%)
- Response rate (% replies received)
- Average time to response
- Template performance comparison

**Acceptance Criteria:**
- [ ] Dashboard accessible via `/dashboard/email-analytics`
- [ ] Real-time metrics display
- [ ] Filterable by date range, template, industry
- [ ] Export to CSV

**Implementation File:** `frontend_templates/email_analytics.html` (new)

---

## Technical Specifications

### Email Format Standards

**MIME Types:**
- If HTML enabled: `multipart/alternative` (HTML + plain text)
- If plain text only: `text/plain; charset=utf-8`

**Character Encoding:**
- UTF-8 for all emails
- Support for international characters (accents, special symbols)

**Line Length:**
- Plain text: 78 characters per line (RFC 2822)
- HTML: No limit (browser wraps)

**Attachment Limits:**
- Max individual file: 25 MB
- Max total size: 25 MB (Gmail limit)
- Supported formats: PDF, DOCX, TXT

### Database Schema Updates

**New Table: `email_tracking`**
```sql
CREATE TABLE email_tracking (
  id SERIAL PRIMARY KEY,
  tracking_id VARCHAR(100) UNIQUE NOT NULL,
  job_id INTEGER REFERENCES analyzed_jobs(id),
  sent_to VARCHAR(255) NOT NULL,
  sent_at TIMESTAMP NOT NULL,
  status VARCHAR(50) NOT NULL,  -- sent, delivered, bounced, failed
  gmail_message_id VARCHAR(255),
  thread_id VARCHAR(255),
  template_type VARCHAR(100),
  error_message TEXT,
  retry_count INTEGER DEFAULT 0,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_email_tracking_job_id ON email_tracking(job_id);
CREATE INDEX idx_email_tracking_status ON email_tracking(status);
CREATE INDEX idx_email_tracking_sent_at ON email_tracking(sent_at);
```

**New Table: `email_templates`**
```sql
CREATE TABLE email_templates (
  id SERIAL PRIMARY KEY,
  template_name VARCHAR(100) UNIQUE NOT NULL,
  template_type VARCHAR(50) NOT NULL,  -- professional, conservative, creative, etc.
  subject_template TEXT NOT NULL,
  body_template TEXT NOT NULL,
  use_html BOOLEAN DEFAULT false,
  industry VARCHAR(100),
  active BOOLEAN DEFAULT true,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Updated Table: `analyzed_jobs`**
```sql
ALTER TABLE analyzed_jobs
ADD COLUMN hiring_manager_name VARCHAR(255),
ADD COLUMN hiring_manager_email VARCHAR(255),
ADD COLUMN email_sent BOOLEAN DEFAULT false,
ADD COLUMN email_tracking_id VARCHAR(100);
```

### Configuration Updates

**New Environment Variables (.env):**
```bash
# =============================================================================
# User Contact Information (⚠️ CONFIGURE BEFORE USE)
# =============================================================================

# Email Address - Choose one of these options:
# Option 1: New Gmail account (check availability at accounts.google.com/signup)
# Option 2: Custom domain email (recommended for professionalism)
# Option 3: Keep current email
USER_EMAIL_ADDRESS=your.professional.email@gmail.com  # ⚠️ REQUIRED - Update this!

# Display Name (appears in recipient's inbox)
USER_DISPLAY_NAME="Steve Glen"

# Contact Information
USER_PHONE="(780) 555-0123"  # Update with your actual phone number
USER_LOCATION="Edmonton, Alberta, Canada"
USER_PROFESSIONAL_TITLE="Marketing Communications Professional"

# Professional Links (update with your actual profiles)
USER_LINKEDIN_URL="linkedin.com/in/steveglen"  # ⚠️ Update with your LinkedIn
USER_PORTFOLIO_URL=""  # Optional: Add if you have a portfolio
USER_WEBSITE_URL=""    # Optional: Add if you have a personal website

# =============================================================================
# Email Template Configuration
# =============================================================================

EMAIL_USE_HTML=true  # or false for plain text (see PRD R1.1 for decision)
EMAIL_TEMPLATE_DEFAULT=professional
EMAIL_ENABLE_TRACKING=true
EMAIL_ENABLE_PREVIEW=true

# Email Validation
EMAIL_VALIDATE_URLS=true
EMAIL_VALIDATE_SPELLING=true
EMAIL_BLOCK_ON_ERRORS=true

# Email Delivery
EMAIL_MAX_RETRIES=3
EMAIL_RETRY_DELAY_SECONDS=300  # 5 minutes

# =============================================================================
# Email Address Setup Notes
# =============================================================================
#
# OPTION 1: New Gmail Account
# 1. Visit: https://accounts.google.com/signup
# 2. Try your desired email (e.g., steve.glen@gmail.com)
# 3. If available, create account and update USER_EMAIL_ADDRESS above
# 4. Complete Gmail OAuth setup for this new address
#
# OPTION 2: Custom Domain Email (RECOMMENDED)
# 1. Purchase domain at Namecheap, Google Domains, or Cloudflare (~$12/year)
# 2. Example: steveglen.com → use steve@steveglen.com
# 3. Set up Gmail forwarding and "Send As" feature
# 4. Guide: https://support.google.com/domains/answer/9437157
# 5. Update USER_EMAIL_ADDRESS with custom domain email
#
# OPTION 3: Keep Current Email
# 1. Update USER_EMAIL_ADDRESS with your current email
# 2. Note: Obfuscated formats (1234.S.t.e.v.e.Glen@gmail.com) may appear
#    less professional to hiring managers
#
# =============================================================================
```

---

## API Endpoints

### New Endpoints

**POST /api/email/preview**
```
Description: Preview email without sending
Authentication: Required (dashboard auth)
Request Body:
  {
    "job_id": integer,
    "template_type": string (optional),
    "preview_mode": "html" | "text" (optional)
  }
Response: Email preview with validation results
```

**POST /api/email/send-application**
```
Description: Send job application email (ENHANCED)
Authentication: Required (dashboard auth)
Request Body:
  {
    "job_id": integer,
    "to_email": string (optional, auto-detected if not provided),
    "template_type": string (optional, uses default),
    "preview_required": boolean (optional, default: false)
  }
Response: Sending status with tracking ID
```

**GET /api/email/tracking/{tracking_id}**
```
Description: Get email delivery status
Authentication: Required (dashboard auth)
Response: Tracking information and status
```

**GET /api/email/templates**
```
Description: List available email templates
Authentication: Required (dashboard auth)
Response: Array of template metadata
```

### Updated Endpoints

**POST /api/email/test**
```
Current: Sends static test email
Enhanced: Uses dynamic content generator with preview option
```

---

## Testing Requirements

### Unit Tests

**Test Coverage:** Minimum 80%

**Critical Test Cases:**
1. Email template rendering (HTML and plain text)
2. Name extraction from job descriptions
3. Email validation (RFC compliance, URL checking)
4. Signature generation
5. Attachment filename sanitization
6. Template variable substitution

**Test Files:**
- `tests/unit/test_email_templates.py`
- `tests/unit/test_email_validator.py`
- `tests/unit/test_signature_generator.py`

### Integration Tests

**Test Scenarios:**
1. End-to-end email sending workflow
2. OAuth authentication flow
3. Preview → Send workflow
4. Failed send retry logic
5. Bounce handling

**Test Files:**
- `tests/integration/test_email_workflow.py`
- `tests/integration/test_email_delivery.py`

### Manual Testing

**Test Plan:**
1. Send test emails to multiple email clients:
   - Gmail (desktop & mobile)
   - Outlook (desktop & mobile)
   - Apple Mail
   - Thunderbird
2. Verify formatting consistency across clients
3. Test clickable links on mobile devices
4. Verify attachments open correctly
5. Check spam folder placement

**Test Recipients:**
- {USER_EMAIL_ADDRESS} (send test to yourself)
- Test accounts on other platforms (Outlook, Yahoo, etc.) if available

---

## Security & Privacy

### Security Requirements

1. **Credential Protection:**
   - OAuth tokens stored in secure storage (not git)
   - Environment variables for sensitive config
   - No credentials in logs

2. **Input Validation:**
   - Sanitize all email addresses
   - Prevent email injection attacks
   - Validate attachment MIME types

3. **Rate Limiting:**
   - Max 50 emails per hour (prevent spam classification)
   - Max 200 emails per day
   - Configurable limits

### Privacy Requirements

1. **Data Minimization:**
   - Store only necessary tracking data
   - Auto-delete tracking records > 1 year old

2. **Transparency:**
   - Clear disclosure of automation in email footer (optional)
   - Opt-out mechanism if sending bulk

3. **Compliance:**
   - CAN-SPAM Act compliance
   - GDPR considerations (if applicable)

---

## Rollout Plan

### Phase 1: Foundation (Week 1)
**Goal:** Basic improvements, OAuth setup

**Deliverables:**
- ✅ Gmail OAuth authenticated
- ✅ HTML email template (option selected)
- ✅ Professional signature block
- ✅ Email headers improved

**Success Criteria:**
- Send first real email successfully
- Email renders correctly in Gmail

### Phase 2: Quality (Week 2-3)
**Goal:** Personalization and validation

**Deliverables:**
- ✅ Email preview endpoint
- ✅ Hiring manager name extraction
- ✅ Job-specific customization
- ✅ Email validation

**Success Criteria:**
- 95%+ validation pass rate
- Personalized greetings in 60%+ of emails

### Phase 3: Tracking (Month 2)
**Goal:** Reliability and monitoring

**Deliverables:**
- ✅ Email delivery tracking
- ✅ Authentication setup (SPF/DKIM/DMARC)
- ✅ Attachment metadata enhancement

**Success Criteria:**
- 98%+ delivery rate
- < 2% bounce rate

### Phase 4: Advanced (Month 3+)
**Goal:** Optimization and scaling

**Deliverables:**
- ✅ Template library
- ✅ Company research integration
- ✅ Analytics dashboard

**Success Criteria:**
- 5+ template options
- Response rate tracking enabled

---

## Risks & Mitigations

### Risk 1: Emails Flagged as Spam
**Likelihood:** Medium
**Impact:** High

**Mitigation:**
- Proper email authentication (SPF, DKIM, DMARC)
- Rate limiting to avoid bulk sender classification
- Avoid spam trigger words in subject/body
- Monitor sender reputation
- Warm up sending IP (gradual volume increase)

### Risk 2: HTML Emails Look Too Corporate
**Likelihood:** Medium
**Impact:** Medium

**Mitigation:**
- Use "enhanced plain text" approach (minimal HTML)
- A/B test HTML vs plain text
- Get feedback from hiring managers
- Allow manual override per job
- Keep design minimal and authentic

### Risk 3: Personalization Errors
**Likelihood:** Medium
**Impact:** High (embarrassing mistakes)

**Mitigation:**
- Mandatory preview for first 100 emails
- Validation checks for name extraction
- Fallback to generic greeting if uncertain
- Manual review flag for suspicious patterns
- Test suite for name extraction accuracy

### Risk 4: OAuth Token Expiration
**Likelihood:** Low
**Impact:** High (emails stop sending)

**Mitigation:**
- Automatic token refresh logic
- Monitoring and alerts for auth failures
- Backup credentials
- Error notifications to admin
- Graceful degradation to mock sender

### Risk 5: Over-Automation Concerns
**Likelihood:** Low
**Impact:** Medium (ethical concerns)

**Mitigation:**
- Transparent footer disclosure (optional)
- Human-in-the-loop preview/approval
- Authenticity over volume (quality > quantity)
- Limit daily sending volume
- Regular review of email quality

---

## Success Metrics

### Primary Metrics

**Response Rate:**
- **Target:** 10% response rate (industry average: 5-8%)
- **Measurement:** % of emails receiving replies within 14 days
- **Baseline:** TBD (first 100 emails)

**Delivery Rate:**
- **Target:** 98% successful delivery
- **Measurement:** % of emails delivered (not bounced)
- **Baseline:** 95% (typical for Gmail)

### Secondary Metrics

**Email Quality:**
- **Target:** < 1% error rate
- **Measurement:** Validation errors, broken links, typos per 100 emails
- **Baseline:** 0% (manual review initially)

**Personalization Rate:**
- **Target:** 60% personalized greetings
- **Measurement:** % using actual hiring manager name vs generic
- **Baseline:** 0% (currently all generic)

**Time Saved:**
- **Target:** 15 minutes per application
- **Measurement:** Time to send with automation vs manual
- **Baseline:** 30 minutes manual (estimated)

### Reporting Cadence
- Weekly during Phase 1-2 (active development)
- Bi-weekly during Phase 3-4
- Monthly after full rollout

---

## Open Questions & Decisions

### Decision Required: User Email Address
**Question:** What email address should be used for sending job applications?
**Current:** `1234.S.t.e.v.e.Glen@gmail.com` (obfuscated, needs replacement)
**Status:** ⚠️ PENDING - User needs to decide on professional email address
**Decision Maker:** Steve Glen
**Deadline:** Before Phase 1 implementation

**Options:**

**Option 1: New Gmail Account**
- Create a professional Gmail address
- Suggestions: `steve.glen@gmail.com`, `stevenglen@gmail.com`, `s.glen@gmail.com`
- Check availability: https://accounts.google.com/signup
- **Pro:** Free, reliable, integrated with system
- **Con:** Gmail addresses may be taken, less professional than custom domain

**Option 2: Custom Domain Email** (RECOMMENDED for maximum professionalism)
- Purchase domain: `steveglen.com` (~$12/year)
- Set up email: `steve@steveglen.com` or `contact@steveglen.com`
- Forward to existing Gmail account
- Configure Gmail to send FROM custom address
- **Pro:** Most professional, memorable, brand-building
- **Con:** Small annual cost, requires DNS setup

**Option 3: Keep Current Email**
- Use existing `1234.S.t.e.v.e.Glen@gmail.com`
- **Pro:** No changes needed, already set up
- **Con:** Obfuscated format may look unprofessional or suspicious

**Implementation Notes:**
- Email address stored as environment variable: `USER_EMAIL_ADDRESS`
- Easy to update across entire system (no hardcoded values)
- Display name separate from email: `USER_DISPLAY_NAME = "Steve Glen"`
- See R1.2 for email header configuration

**Resources:**
- Gmail signup: https://accounts.google.com/signup
- Domain registration: Namecheap, Google Domains, Cloudflare
- Gmail custom domain setup: https://support.google.com/domains/answer/9437157

---

### Decision Required: HTML vs Plain Text
**Options:** Enhanced Plain Text HTML (A), Pure Plain Text (B), Configurable (C)
**Status:** ⚠️ PENDING - See R1.1 for detailed analysis
**Decision Maker:** Steve Glen
**Deadline:** Before Phase 1 implementation

**Recommendation:** Option A (Enhanced Plain Text HTML)
- Clickable links = major UX improvement
- Looks authentic, not corporate
- Industry-appropriate for marketing roles
- Can always switch to plain text if needed

---

### Question: Email Signature Icons
**Question:** Include emoji icons (📞 📧 🔗) in signature or plain text only?
**Considerations:**
- **Pro:** Visual appeal, modern, easy to scan
- **Con:** May look unprofessional to some, compatibility issues
**Status:** Open
**Recommendation:** Configurable flag, default OFF

---

### Question: Email Footer Disclosure
**Question:** Include "Sent via Automated Job Application System" footer?
**Considerations:**
- **Pro:** Transparency, honesty, explains quality/consistency
- **Con:** Reduces authenticity, may seem impersonal
**Status:** Open
**Recommendation:** Optional flag, default OFF (unless legally required)

---

### Question: Read Receipts / Tracking Pixels
**Question:** Include 1x1 tracking pixel for open tracking?
**Considerations:**
- **Pro:** Valuable analytics, know if email was opened
- **Con:** Privacy concerns, may be blocked by email clients
**Status:** Open
**Recommendation:** OFF initially, privacy-first approach

---

### Question: LinkedIn Profile Link
**Question:** Include LinkedIn link in every email?
**Considerations:**
- **Pro:** Easy for hiring managers to view full profile
- **Con:** May redirect attention away from resume
**Status:** Open
**Recommendation:** YES - standard practice in modern applications

---

## Appendix

### Related Documentation
- `tasks/email-refinement-analysis.md` - Detailed discovery analysis
- `docs/database-connection-guide.md` - Database setup
- `.env.example` - Environment configuration

### External References
- [RFC 5322](https://tools.ietf.org/html/rfc5322) - Email format standard
- [CAN-SPAM Act](https://www.ftc.gov/tips-advice/business-center/guidance/can-spam-act-compliance-guide-business) - Email compliance
- [Google Gmail API Docs](https://developers.google.com/gmail/api/guides) - API reference

### Glossary
- **SPF:** Sender Policy Framework (email authentication)
- **DKIM:** DomainKeys Identified Mail (email signing)
- **DMARC:** Domain-based Message Authentication, Reporting & Conformance
- **MIME:** Multipurpose Internet Mail Extensions
- **OAuth:** Open Authorization (authentication protocol)
- **RFC:** Request for Comments (internet standards)

---

## Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-10-09 | Steve Glen | Initial draft - discovery complete |

---

**Document Status:** 🟡 DRAFT
**Next Action:** Review and approve requirements, make HTML decision
**Owner:** Steve Glen
