---
title: "Email Address Decision Guide"
type: guide
component: email
status: draft
tags: []
---

# Email Address Decision Guide
**Branch:** task/11-email
**Date:** October 9, 2025
**Status:** User Decision Required

---

## Current Situation

**Current Email:** `1234.S.t.e.v.e.Glen@gmail.com`

**Issue:** This obfuscated email format may appear:
- Unprofessional or suspicious to hiring managers
- Like a temporary or throwaway account
- Difficult to remember or communicate verbally

**Decision Needed:** Choose professional email address for job applications before implementing email system.

---

## Option 1: New Gmail Account

### Overview
Create a new, professional Gmail account with a clean, simple address.

### Suggested Addresses
Check availability at: https://accounts.google.com/signup

**First Choice (Simple & Professional):**
- `steve.glen@gmail.com`
- `stevenglen@gmail.com`
- `s.glen@gmail.com`

**Backup Options (If Taken):**
- `steve.glen.marketing@gmail.com`
- `stevenglen.pro@gmail.com`
- `stevenglen.ca@gmail.com` (location indicator)
- `contact.steveglen@gmail.com`
- `stevenglen2024@gmail.com` (year indicator)

### How to Check Availability
**Cannot be done via API** - Gmail doesn't provide email availability checking.

**Manual Process:**
1. Go to: https://accounts.google.com/signup
2. Enter desired username (e.g., "steve.glen")
3. Gmail will immediately tell you if it's taken
4. If taken, try variations until you find available one
5. Don't create account yet - just test availability

### Pros ✅
- Free (no ongoing costs)
- Reliable Gmail infrastructure
- Easy integration (already using Gmail OAuth)
- Can start using immediately
- Works with existing system

### Cons ❌
- Desired username may be taken
- Still a gmail.com address (less unique than custom domain)
- No personal branding opportunity
- Can't change easily later (email becomes your identity)

### Implementation Effort
**Low** - Just update environment variable:
```bash
USER_EMAIL_ADDRESS=steve.glen@gmail.com
```

### Cost
**$0** - Completely free

---

## Option 2: Custom Domain Email (RECOMMENDED)

### Overview
Purchase your own domain (e.g., `steveglen.com`) and create professional email address like `steve@steveglen.com`.

### Example Domains to Check
- `steveglen.com`
- `stevenglen.ca` (Canadian domain)
- `glenmarketing.com`
- `steveglen.pro`

### How It Works
1. **Buy domain** ($12/year at Namecheap, Google Domains, Cloudflare)
2. **Set up email forwarding** - Emails to `steve@steveglen.com` → forward to Gmail
3. **Configure Gmail "Send As"** - Send emails FROM `steve@steveglen.com` using Gmail
4. **Result:** Professional custom email, managed through familiar Gmail interface

### Pros ✅
- **Most professional** - Shows you're serious and invested
- **Memorable** - Easy to communicate verbally
- **Personal branding** - Own your online identity
- **Future-proof** - Can use for website, portfolio, personal brand
- **Flexible** - Create unlimited addresses (contact@, jobs@, etc.)
- **Unique** - Guaranteed available if you buy the domain

### Cons ❌
- Small annual cost (~$12-15/year)
- Requires DNS configuration (5-10 minute setup)
- Additional step beyond Gmail account
- Renewal required annually (can auto-renew)

### Implementation Effort
**Medium** - Requires domain purchase + DNS setup:

**Step-by-step:**
1. Check domain availability: https://www.namecheap.com or https://domains.google
2. Purchase domain (~$12/year)
3. Set up email forwarding in domain settings
4. Configure Gmail "Send As" feature
5. Update environment variable:
   ```bash
   USER_EMAIL_ADDRESS=steve@steveglen.com
   ```

**Setup Time:** ~30 minutes total

### Cost
- **Domain:** $12-15/year
- **Email forwarding:** Free (included with most domain registrars)
- **Total:** ~$1/month

### Resources
- **Domain Registration:**
  - Namecheap: https://www.namecheap.com
  - Google Domains: https://domains.google
  - Cloudflare: https://www.cloudflare.com/products/registrar/

- **Gmail Custom Domain Setup:**
  - Official guide: https://support.google.com/domains/answer/9437157
  - Video tutorial: Search "Gmail custom domain forwarding" on YouTube

---

## Option 3: Keep Current Email

### Overview
Continue using `1234.S.t.e.v.e.Glen@gmail.com` as-is.

### Pros ✅
- No changes required
- Already set up and working
- Zero additional cost or effort

### Cons ❌
- Obfuscated format looks unprofessional
- May raise red flags with hiring managers:
  - "Is this a spam account?"
  - "Why the unusual formatting?"
  - "Is this person trying to hide their identity?"
- Difficult to communicate verbally (spell out: "One two three four dot S dot t dot e...")
- Creates unnecessary friction in professional communication

### Recommendation
**Not recommended** for job applications. The obfuscated format significantly undermines professional credibility.

---

## Comparison Matrix

| Factor | Gmail (Option 1) | Custom Domain (Option 2) | Current Email (Option 3) |
|--------|------------------|--------------------------|--------------------------|
| **Professionalism** | ⭐⭐⭐ Good | ⭐⭐⭐⭐⭐ Excellent | ⭐ Poor |
| **Cost** | Free | ~$12/year | Free |
| **Setup Time** | 5 minutes | 30 minutes | 0 minutes |
| **Memorability** | ⭐⭐⭐ Good | ⭐⭐⭐⭐⭐ Excellent | ⭐ Poor |
| **Branding** | ⭐⭐ Limited | ⭐⭐⭐⭐⭐ Excellent | ⭐ None |
| **Uniqueness** | ⭐⭐ May be taken | ⭐⭐⭐⭐⭐ Yours | ⭐⭐⭐ Unique (but odd) |
| **Future Value** | ⭐⭐ Email only | ⭐⭐⭐⭐⭐ Website/portfolio too | ⭐ None |
| **Implementation** | ⭐⭐⭐⭐⭐ Easy | ⭐⭐⭐⭐ Moderate | ⭐⭐⭐⭐⭐ None needed |

---

## Recommendation

### Best Choice: **Option 2 - Custom Domain Email**

**Rationale:**
- Small investment ($12/year) with significant professional ROI
- Positions you as serious, established professional
- Future-proof for personal website, portfolio, personal brand
- Complete control and ownership
- Industry standard for senior professionals

**Suggested Domain:** `steveglen.com` or `stevenglen.ca`
**Suggested Email:** `steve@steveglen.com`

### Acceptable Alternative: **Option 1 - New Gmail Account**

**Use case:** If you want to start immediately without spending money.

**Rationale:**
- Free and quick to implement
- Still professional and credible
- Easy to switch to custom domain later if desired

**Suggested Email:** Check availability in this order:
1. `steve.glen@gmail.com`
2. `stevenglen@gmail.com`
3. `s.glen@gmail.com`

### Not Recommended: **Option 3 - Keep Current**

The obfuscated format undermines the professionalism of the entire automated system. The credibility cost outweighs the convenience of not changing.

---

## Decision Process

### Step 1: Choose Your Option
- [ ] **Option 2:** Custom domain (recommended) - budget $12/year, 30 min setup
- [ ] **Option 1:** New Gmail account - free, 5 min setup
- [ ] ~~Option 3: Keep current~~ (not recommended)

### Step 2: If Option 2 (Custom Domain)
1. [ ] Check domain availability at Namecheap/Google Domains
2. [ ] Purchase domain (save receipt for records)
3. [ ] Set up email forwarding to existing Gmail
4. [ ] Configure Gmail "Send As" feature
5. [ ] Test sending/receiving email
6. [ ] Update USER_EMAIL_ADDRESS in .env file

### Step 3: If Option 1 (New Gmail)
1. [ ] Go to https://accounts.google.com/signup
2. [ ] Try desired usernames until you find available one
3. [ ] Create account (save credentials securely)
4. [ ] Set up OAuth for new account
5. [ ] Update USER_EMAIL_ADDRESS in .env file

### Step 4: System Configuration
1. [ ] Update `.env` file with new email address:
   ```bash
   USER_EMAIL_ADDRESS=your.chosen.email@domain.com
   ```
2. [ ] Update other contact info if needed (phone, LinkedIn, etc.)
3. [ ] Complete Gmail OAuth setup for new address
4. [ ] Send test email to yourself
5. [ ] Verify email displays correctly in inbox

---

## Common Questions

### Q: Can I change my email address later?
**A:** Yes, but not recommended. Your email becomes your professional identity. Changing it means:
- Re-doing OAuth authentication
- Updating all applications in progress
- Losing continuity with hiring managers
- Potential confusion in email threads

**Best practice:** Choose carefully now, commit for at least 1-2 years.

---

### Q: What if steveglen.com is taken?
**A:** Try variations:
- `stevenglen.com` (different spelling)
- `steveglen.ca` (Canadian domain)
- `steveglen.pro` (professional domain)
- `glenmarketing.com` (industry + name)
- `steveglen.me` (personal domain)

Or use domain search tools to see what's available.

---

### Q: Can I use Gmail with a custom domain?
**A:** Yes! Two options:

**Option A: Email Forwarding (Free)**
- Emails sent to `steve@steveglen.com` → auto-forward to Gmail
- Send FROM custom address using Gmail "Send As" feature
- No cost, works perfectly for individual use

**Option B: Google Workspace ($6/month)**
- Full Gmail interface with custom domain
- Professional Google Drive, Calendar, etc.
- Overkill for individual job seeking (not needed)

**Recommended:** Option A (free forwarding)

---

### Q: Do I need the domain for anything else?
**A:** Not required, but valuable:
- **Portfolio website:** `steveglen.com` with work samples
- **LinkedIn custom URL:** Link to your domain
- **Email signatures:** Professional web presence
- **Future projects:** Personal brand foundation

Even if you don't use it now, owning your name protects your online identity.

---

### Q: What about privacy/spam?
**A:** Custom domains actually help:
- Create aliases for different purposes (jobs@, contact@)
- Forward to Gmail for spam filtering
- Can change forwarding destination anytime
- Control your own domain reputation

---

### Q: Is steve.glen@gmail.com professional enough?
**A:** Yes, if that's what you prefer:
- Gmail is widely accepted for professional communication
- Clean, simple format is perfectly fine
- Custom domain is *better*, but Gmail is acceptable
- The key is avoiding obfuscated formats

**Bottom line:** Gmail is good, custom domain is better, obfuscated is bad.

---

## Next Steps

**Before implementing email system:**
1. ✅ Read this guide
2. ⚠️ **Make email decision** (Option 1 or 2)
3. ⚠️ **Set up new email** (Gmail account or custom domain)
4. ⚠️ **Update .env configuration** with new address
5. ⚠️ **Test email sending/receiving**
6. ✅ Proceed with email system implementation (PRD Phase 1)

**Estimated Time to Decision:** 30 minutes - 1 hour (including domain research/setup)

---

## Configuration Template

Once you've decided, update `.env` file:

```bash
# =============================================================================
# User Contact Information
# =============================================================================

# YOUR CHOSEN EMAIL ADDRESS (update this!)
USER_EMAIL_ADDRESS=_________________________  # ⚠️ FILL THIS IN

# Display name (how you want to appear in inbox)
USER_DISPLAY_NAME="Steve Glen"

# Your actual contact information
USER_PHONE="(780) 555-0123"  # Update with real number
USER_LOCATION="Edmonton, Alberta, Canada"
USER_PROFESSIONAL_TITLE="Marketing Communications Professional"

# Professional links (update with your actual URLs)
USER_LINKEDIN_URL="linkedin.com/in/steveglen"  # Update with real profile
USER_PORTFOLIO_URL=""  # Optional: Add if you have portfolio
USER_WEBSITE_URL=""    # Optional: Add if you have website (e.g., steveglen.com)
```

---

## Resources

### Domain Registration
- **Namecheap:** https://www.namecheap.com (recommended, ~$12/year)
- **Google Domains:** https://domains.google (~$12/year)
- **Cloudflare Registrar:** https://www.cloudflare.com/products/registrar/ (~$9/year, cheapest)

### Gmail Setup
- **Create Gmail:** https://accounts.google.com/signup
- **Custom Domain Guide:** https://support.google.com/domains/answer/9437157
- **Send As Setup:** https://support.google.com/mail/answer/22370

### Email Best Practices
- **Professional Email Guide:** https://www.thebalancemoney.com/professional-email-address-2062093
- **Gmail Tips:** https://support.google.com/mail

---

**Document Status:** ✅ Complete - Ready for User Decision
**Next Action:** User to choose Option 1 or 2 and configure email address
**Blocking:** Email system implementation (PRD Phase 1)
