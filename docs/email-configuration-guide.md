# Email Configuration Guide
**Version:** 4.2.0
**Last Updated:** October 9, 2025
**Status:** ✅ Complete

---

## Overview

This guide explains how to configure the email integration system for the Automated Job Application platform. All email-related configuration is now centralized in environment variables for easy management and updates.

---

## Quick Start

### 1. Copy Environment Template
```bash
cp .env.example .env
```

### 2. Update Required Fields
Open `.env` and configure:
```bash
# REQUIRED: Your professional email address
USER_EMAIL_ADDRESS=your.email@gmail.com  # ⚠️ UPDATE THIS!

# RECOMMENDED: Update with your actual information
USER_PHONE=(780) 555-0123
USER_LINKEDIN_URL=linkedin.com/in/yourprofile
```

### 3. Test Configuration
```bash
# Test signature generator
python modules/email_integration/signature_generator.py

# Test email validator
python modules/email_integration/email_validator.py
```

---

## Environment Variables Reference

### User Contact Information

#### USER_EMAIL_ADDRESS (REQUIRED)
**Purpose:** Primary email address for sending job applications
**Format:** `your.email@domain.com`
**Example:** `steve.glen@gmail.com` or `steve@steveglen.com`

**Decision Guide:**
- See `tasks/email-address-decision-guide.md` for detailed options
- Option 1: New Gmail account (free, quick)
- Option 2: Custom domain (professional, ~$12/year) ⭐ RECOMMENDED
- Option 3: Keep current (not recommended if obfuscated)

**Validation:**
- Must be valid email format (RFC 5322)
- Will be used in From/Reply-To headers
- Displayed in recipient's inbox

---

#### USER_DISPLAY_NAME
**Purpose:** Name displayed in email From field
**Default:** `Steve Glen`
**Format:** `First Last` or `First Middle Last`
**Example:** `Steve Glen`

**Displayed As:**
```
From: "Steve Glen" <steve.glen@gmail.com>
```

---

#### USER_PHONE
**Purpose:** Contact phone number in signature
**Default:** `(780) 555-0123`
**Format:** Any readable format
**Examples:**
- `(780) 555-0123` (North American)
- `+1-780-555-0123` (International)
- `780.555.0123` (dotted)

**HTML Email:** Converted to clickable `tel:` link on mobile

---

#### USER_LOCATION
**Purpose:** Geographic location in signature
**Default:** `Edmonton, Alberta, Canada`
**Format:** `City, State/Province, Country` (flexible)
**Examples:**
- `Toronto, Ontario, Canada`
- `Vancouver, BC`
- `Remote (Based in Calgary, AB)`

---

#### USER_PROFESSIONAL_TITLE
**Purpose:** Professional title/tagline in signature
**Default:** `Marketing Communications Professional`
**Format:** Brief professional description
**Examples:**
- `Senior Marketing Manager`
- `Digital Marketing Specialist`
- `Marketing Communications Professional`
- `Business Development Executive`

---

#### USER_LINKEDIN_URL
**Purpose:** LinkedIn profile link in signature
**Default:** `linkedin.com/in/steveglen`
**Format:** `linkedin.com/in/yourprofile` (domain optional)
**Example:** `linkedin.com/in/stevenglen`

**Note:** System auto-adds `https://` if missing

---

#### USER_PORTFOLIO_URL (Optional)
**Purpose:** Portfolio website link in signature
**Default:** Empty (not displayed if blank)
**Format:** `yourportfolio.com` or full URL
**Example:** `steveglen.myportfolio.com`

---

#### USER_WEBSITE_URL (Optional)
**Purpose:** Personal website link in signature
**Default:** Empty (not displayed if blank)
**Format:** `yourdomain.com` or full URL
**Example:** `steveglen.com`

---

### Email Template Configuration

#### EMAIL_USE_HTML
**Purpose:** Enable HTML email formatting
**Default:** `true`
**Options:** `true` | `false`

**Details:**
- `true`: Enhanced plain text HTML (clickable links, subtle formatting)
- `false`: Pure plain text (ASCII only, no links)

**Recommendation:** `true` for marketing/communications roles

See `tasks/email-refinement-analysis.md` for HTML vs plain text analysis

---

#### EMAIL_TEMPLATE_DEFAULT
**Purpose:** Default email template style
**Default:** `professional`
**Options:** `professional` | `conservative` | `creative`

**Templates:**
- **professional**: Marketing, business roles (default)
- **conservative**: Finance, legal, government
- **creative**: Design, media, creative roles

---

#### EMAIL_SIGNATURE_ICONS
**Purpose:** Include emoji icons in signature
**Default:** `false`
**Options:** `true` | `false`

**With Icons (`true`):**
```
📞 (780) 555-0123
📧 steve.glen@gmail.com
🔗 LinkedIn: linkedin.com/in/steveglen
```

**Without Icons (`false`):**
```
Phone: (780) 555-0123
Email: steve.glen@gmail.com
LinkedIn: linkedin.com/in/steveglen
```

**Recommendation:** `false` for professional applications (safer)

---

### Email Features

#### EMAIL_ENABLE_TRACKING
**Purpose:** Track email delivery status
**Default:** `true`
**Options:** `true` | `false`

**Tracking Data:**
- Delivery status (sent, delivered, bounced, failed)
- Timestamp
- Gmail message ID
- Error logging

---

#### EMAIL_ENABLE_PREVIEW
**Purpose:** Allow email preview before sending
**Default:** `true`
**Options:** `true` | `false`

**When Enabled:**
- Preview endpoint available: `/api/email/preview`
- Manual approval workflow option
- Quality control before sending

---

### Email Validation

#### EMAIL_VALIDATE_URLS
**Purpose:** Check that all URLs are accessible
**Default:** `true`
**Options:** `true` | `false`

**Validation:**
- Checks HTTP status (200 OK)
- Prevents broken links in emails
- Logs warnings for unreachable URLs

---

#### EMAIL_BLOCK_ON_ERRORS
**Purpose:** Block sending if validation errors found
**Default:** `true`
**Options:** `true` | `false`

**Error Categories:**
- **Blocking Errors** (if `true`):
  - Invalid email address format
  - Unsubstituted template variables
  - Missing attachments
  - Empty subject/body

- **Warnings** (never block):
  - Long subject line
  - Potential spam words
  - Short email body

---

### Email Delivery

#### EMAIL_MAX_RETRIES
**Purpose:** Number of retry attempts for failed sends
**Default:** `3`
**Range:** `0` - `10`

**Retry Logic:**
- Exponential backoff
- Only transient failures retried
- Permanent failures not retried

---

#### EMAIL_RETRY_DELAY_SECONDS
**Purpose:** Delay between retry attempts
**Default:** `300` (5 minutes)
**Range:** `60` - `3600` (1 min - 1 hour)

---

#### EMAIL_MAX_DAILY_SENDS
**Purpose:** Maximum emails sent per day
**Default:** `50`
**Range:** `1` - `200`

**Purpose:**
- Prevent spam classification
- Build sender reputation gradually
- Comply with Gmail sending limits

---

### Subject Line Configuration

#### EMAIL_INCLUDE_REFERENCE_ID
**Purpose:** Add tracking ID to subject line
**Default:** `false`
**Options:** `true` | `false`

**With Reference ID (`true`):**
```
Application #20251009-001: Marketing Manager - Steve Glen
```

**Without Reference ID (`false`):**
```
Application for Marketing Manager - Steve Glen
```

---

## Configuration Examples

### Example 1: New Gmail Account
```bash
# User Contact Information
USER_EMAIL_ADDRESS=steve.glen@gmail.com
USER_DISPLAY_NAME=Steve Glen
USER_PHONE=(780) 555-0123
USER_LOCATION=Edmonton, Alberta, Canada
USER_PROFESSIONAL_TITLE=Marketing Communications Professional
USER_LINKEDIN_URL=linkedin.com/in/stevenglen
USER_PORTFOLIO_URL=
USER_WEBSITE_URL=

# Email Template Configuration
EMAIL_USE_HTML=true
EMAIL_TEMPLATE_DEFAULT=professional
EMAIL_SIGNATURE_ICONS=false

# Email Features
EMAIL_ENABLE_TRACKING=true
EMAIL_ENABLE_PREVIEW=true

# Email Validation
EMAIL_VALIDATE_URLS=true
EMAIL_BLOCK_ON_ERRORS=true

# Email Delivery
EMAIL_MAX_RETRIES=3
EMAIL_RETRY_DELAY_SECONDS=300
EMAIL_MAX_DAILY_SENDS=50

# Subject Line
EMAIL_INCLUDE_REFERENCE_ID=false
```

---

### Example 2: Custom Domain (Professional)
```bash
# User Contact Information
USER_EMAIL_ADDRESS=steve@steveglen.com  # Custom domain
USER_DISPLAY_NAME=Steve Glen
USER_PHONE=+1 (780) 555-0123
USER_LOCATION=Edmonton, Alberta, Canada
USER_PROFESSIONAL_TITLE=Senior Marketing Communications Manager
USER_LINKEDIN_URL=linkedin.com/in/stevenglen
USER_PORTFOLIO_URL=steveglen.com/portfolio
USER_WEBSITE_URL=steveglen.com

# Email Template Configuration
EMAIL_USE_HTML=true
EMAIL_TEMPLATE_DEFAULT=professional
EMAIL_SIGNATURE_ICONS=false

# Features (same as Example 1)
```

---

### Example 3: Conservative Industry (Plain Text)
```bash
# User Contact Information
USER_EMAIL_ADDRESS=s.glen@gmail.com
USER_DISPLAY_NAME=Steve Glen
USER_PHONE=(780) 555-0123
USER_LOCATION=Edmonton, AB
USER_PROFESSIONAL_TITLE=Business Development Professional
USER_LINKEDIN_URL=linkedin.com/in/stevenglen
USER_PORTFOLIO_URL=
USER_WEBSITE_URL=

# Email Template Configuration
EMAIL_USE_HTML=false  # Plain text only for conservative industries
EMAIL_TEMPLATE_DEFAULT=conservative
EMAIL_SIGNATURE_ICONS=false

# Features (same as Example 1)
```

---

## Configuration Validation

### Check Configuration Status

**Signature Generator:**
```bash
python modules/email_integration/signature_generator.py
```

**Output:**
```
Configuration Status:
  ✓ email_configured: True
  ✓ display_name_configured: True
  ✓ phone_configured: True
  ✓ location_configured: True
  ✓ linkedin_configured: True
  ✗ portfolio_configured: False
  ✗ website_configured: False
  ✓ professional_title_configured: True
```

---

### Test Email Validation

**Validator:**
```bash
python modules/email_integration/email_validator.py
```

**Manual Test:**
```python
from modules.email_integration.email_validator import get_email_validator

validator = get_email_validator()
result = validator.validate_email(
    to_email="hiring@company.com",
    subject="Application for Marketing Manager - Steve Glen",
    body="Dear Hiring Manager,\n\nI am writing to...",
    attachments=None
)

print(f"Valid: {result['valid']}")
print(f"Errors: {result['errors']}")
print(f"Warnings: {result['warnings']}")
```

---

## Troubleshooting

### Issue: "USER_EMAIL_ADDRESS not configured"

**Cause:** Environment variable not set in `.env`

**Solution:**
1. Open `.env` file
2. Update line: `USER_EMAIL_ADDRESS=your.email@gmail.com`
3. Replace with your actual email
4. Restart application/tests

---

### Issue: Email validation fails

**Check:**
```python
from modules.email_integration.email_validator import validate_email

result = validate_email(
    "your.email@gmail.com",
    "Test Subject",
    "Test body content",
    None
)

print(result)
```

**Common Issues:**
- Invalid email format
- Empty subject/body
- Unsubstituted template variables (`{job_title}` still in text)
- Missing attachments

---

### Issue: Signature looks wrong

**Generate Preview:**
```python
from modules.email_integration.signature_generator import get_signature_generator

gen = get_signature_generator()

# Plain text version
print(gen.generate_plain_text_signature())

# HTML version
print(gen.generate_html_signature())
```

**Check:**
- All environment variables set correctly
- No extra spaces or special characters
- URLs formatted properly (no `http://` needed in config)

---

## Integration with Email System

### Email Application Sender

**File:** `modules/workflow/email_application_sender.py`

**Configuration Loaded Automatically:**
```python
self.user_email = os.getenv("USER_EMAIL_ADDRESS")
self.display_name = os.getenv("USER_DISPLAY_NAME")
self.signature_generator = get_signature_generator()
```

**Template Variables Auto-Replaced:**
- `{job_title}` → Actual job title
- `{company_name}` → Company name
- Signature appended automatically

---

### Gmail OAuth Sender

**File:** `modules/email_integration/gmail_oauth_official.py`

**Configuration Loaded:**
```python
self.user_email = os.getenv("USER_EMAIL_ADDRESS")
self.display_name = os.getenv("USER_DISPLAY_NAME")
```

**Email Headers Set:**
```python
message["From"] = f'"{self.display_name}" <{self.user_email}>'
message["Reply-To"] = f'"{self.display_name}" <{self.user_email}>'
```

---

## Best Practices

### 1. Use Custom Domain (If Possible)
- More professional appearance
- Builds personal brand
- Easy to remember
- ~$12/year investment

### 2. Keep Configuration Updated
- Update LinkedIn when URL changes
- Update phone if number changes
- Update location if you move
- Update professional title for career progression

### 3. Test Before Production
- Run signature generator demo
- Send test email to yourself
- Preview emails before sending
- Check all links work

### 4. Security
- Never commit `.env` file to git
- Use strong OAuth credentials
- Rotate API keys periodically
- Monitor email sending activity

### 5. Gradual Sending
- Start with low daily limit (10-20 emails)
- Increase gradually over weeks
- Build sender reputation
- Avoid spam classification

---

## Related Documentation

- **Email Address Decision Guide:** `tasks/email-address-decision-guide.md`
- **Email Refinement Analysis:** `tasks/email-refinement-analysis.md`
- **Email Refinement PRD:** `tasks/email-refinement-prd.md`
- **Environment Template:** `.env.example`

---

## Support

### Configuration Issues
1. Check `.env` file exists and is readable
2. Verify environment variables loaded: `python -c "import os; print(os.getenv('USER_EMAIL_ADDRESS'))"`
3. Restart application after config changes
4. Check logs for warnings

### Email Sending Issues
1. Verify Gmail OAuth setup complete
2. Check `storage/gmail_token.json` exists
3. Test authentication: `GET /api/email/oauth/status`
4. Send test email: `POST /api/email/test`

---

**Document Status:** ✅ Complete
**Version:** 4.2.0
**Last Updated:** October 9, 2025
