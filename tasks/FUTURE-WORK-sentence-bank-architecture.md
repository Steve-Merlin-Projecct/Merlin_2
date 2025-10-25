---
title: Sentence Bank Architecture - Future Work
type: future-work
created: 2025-10-25
status: pending
priority: high
worktree: resume-and-cover-letter-content-improvements
---

# Sentence Bank Architecture Refinement - Future Work

## Context & Purpose

This document captures architectural analysis and design decisions for improving the resume and cover letter sentence generation system. The goal is to:

1. **Reduce wasted API calls** - Currently 711 truthfulness checks performed without proper context
2. **Enable experience tracking** - Link sentences to actual user experiences for validation
3. **Prevent AI exaggeration** - Detect when generated sentences overstate user's actual accomplishments
4. **Human approval workflow** - Implement review process before sentences are used in applications

## Current State Analysis

### Database Statistics (as of 2025-10-25)

**Resume Sentences: 120 total**
- ✅ All analyzed (keyword, truthfulness, tone, skill)
- ❌ **57 sentences (48%) missing body_section** - not properly categorized
- ❌ **120 sentences (100%) missing experience_id** - no experience linkage
- Only 63 categorized:
  - `constituent`: 29
  - `general`: 25
  - `award`: 9

**Cover Letter Sentences: 591 total**
- ✅ All analyzed (keyword, truthfulness, tone, skill)
- ❌ **544 sentences (92%) missing position_label** - major categorization issue
- Only 47 categorized:
  - `open`: 10
  - `middle`: 10
  - `close`: 10
  - `body`: 6
  - `closing`: 4
  - `opening`: 3
  - `Marketing Automation Manager`: 4 (appears to be misused field)

**Total waste identified:**
- 711 truthfulness checks performed without validation context
- All sentences are generic (no experience_id linkage)
- Cannot verify claims against actual user experiences

### Existing Data Model Issues

**Problem 1: Wrong Foreign Key**
```python
# Line 1500 in database_tools/generated/models.py
experience_id = Column(UUID(as_uuid=True), ForeignKey('job_applications.id'))
```
This points to jobs the user is **applying TO**, not jobs they've **held**.

**Problem 2: No Experience Tracking**
- `work_experiences` table exists with 3 records (user's actual jobs)
- But sentences aren't linked to these experiences
- Cannot validate "Led team of 15" against actual job history

**Problem 3: No Atomic Claim Storage**
- User submits prose: "A major factor in the rebranding, including leading certain initiatives"
- AI generates: "Led a rebranding of the company" ← EXAGGERATION
- No way to validate because original claim isn't stored atomically

## Corrected Architecture Understanding

### The Actual Workflow (CRITICAL)

**Sentences are REUSABLE ASSETS, not ephemeral outputs:**

```
1. GENERATION PHASE (One-time or periodic)
   ├─ Input: User experiences + GENERIC job archetype descriptions
   │         (e.g., "Marketing Manager," "Senior Developer," etc.)
   ├─ AI generates: 50-100 candidate sentences per archetype
   ├─ Filter: Truthfulness check against user experiences
   └─ Output: Candidate sentences awaiting approval

2. APPROVAL PHASE (Human-in-the-loop)
   ├─ Human reviews each sentence (dashboard interface TBD)
   ├─ Approves/Rejects/Edits
   └─ Approved sentences → Sentence Bank (permanent storage)

3. SELECTION PHASE (Per specific job application)
   ├─ Input: Specific job posting for "Marketing Manager at Company X"
   ├─ AI/Logic selects: Best sentences from approved bank
   │         Based on: job description keywords, skills match, relevance
   └─ Output: Subset of 10-15 sentences for THIS application

4. ASSEMBLY PHASE
   ├─ Selected sentences → Resume/Cover Letter document
   └─ Generated document sent to employer
```

**Why This Architecture:**
- **Efficiency**: Generate once, reuse across many applications
- **Quality Control**: Human approves before ANY use
- **Prevents Overfitting**: Generic sentences work for similar jobs
- **Scalability**: Apply to 50 jobs quickly (selection is fast)
- **Audit Trail**: Know exactly what sentences exist and are approved

### The Exaggeration Problem (Core Challenge)

**Example:**

```
User Input (Original Experience):
"A major factor in the rebranding of the company, including leading certain initiatives"

AI Generated Sentence (EXAGGERATED):
"Led a rebranding of the company"

Truthfulness Check: REJECT ❌
Reason: "Led A rebranding" overstates "major factor, led CERTAIN initiatives"
```

**What makes this hard:**
- Semantic difference between "led the rebranding" vs "led certain initiatives"
- Scope difference (all vs. some)
- Ownership difference (primary leader vs. contributor)
- Claim magnitude changes

**Validation requirements:**
```python
def validate_truthfulness(generated_sentence, original_user_claim):
    """
    Check if generated sentence exaggerates beyond what user actually did.

    This is NOT checking if user COULD have done it.
    This IS checking if user's own words support the claim.
    """
    # Must detect:
    # - Magnitude changes (numbers, scope)
    # - Ownership changes (contributor → leader)
    # - Definiteness changes ("certain" → "all")
```

## Proposed Data Model Architecture

### New Table: experience_claims

**Purpose**: Store atomic factual claims from user's experience descriptions

```sql
CREATE TABLE experience_claims (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    experience_id UUID NOT NULL REFERENCES work_experiences(id),
    claim_text TEXT NOT NULL,  -- Atomic factual claim
    claim_type VARCHAR(50),  -- achievement, responsibility, skill, metric
    original_user_text TEXT NOT NULL,  -- Preserve original wording
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),

    -- Verification metadata
    verified_by_user BOOLEAN DEFAULT FALSE,
    contains_metrics BOOLEAN,
    metrics_value JSONB,  -- e.g., {"percentage": 40, "type": "latency_reduction"}

    -- Audit trail
    parsed_by VARCHAR(50),  -- AI model used for parsing
    parsed_at TIMESTAMP
);

CREATE INDEX idx_experience_claims_experience ON experience_claims(experience_id);
CREATE INDEX idx_experience_claims_type ON experience_claims(claim_type);
```

### Updated Table: sentence_bank_resume

**Add source tracking:**

```sql
ALTER TABLE sentence_bank_resume
ADD COLUMN source_claim_id UUID REFERENCES experience_claims(id);

ALTER TABLE sentence_bank_resume
ADD COLUMN human_approval_status VARCHAR(20) DEFAULT 'pending';

ALTER TABLE sentence_bank_resume
ADD COLUMN rejection_reason TEXT;

-- Fix the wrong foreign key
ALTER TABLE sentence_bank_resume
DROP CONSTRAINT IF EXISTS sentence_bank_resume_experience_id_fkey;

ALTER TABLE sentence_bank_resume
ADD CONSTRAINT sentence_bank_resume_experience_id_fkey
FOREIGN KEY (experience_id) REFERENCES work_experiences(id);
```

**Now we have full chain:**
```
sentence_bank_resume → experience_claims → work_experiences
```

### Updated Table: sentence_bank_cover_letter

**Similar changes:**

```sql
ALTER TABLE sentence_bank_cover_letter
ADD COLUMN source_claim_id UUID REFERENCES experience_claims(id);

ALTER TABLE sentence_bank_cover_letter
ADD COLUMN human_approval_status VARCHAR(20) DEFAULT 'pending';

ALTER TABLE sentence_bank_cover_letter
ADD COLUMN rejection_reason TEXT;
```

## User Experience Submission Workflow

### Phase A: User Input (Free-form)

User writes in dashboard:
```
Company: Latest Company
Role: Lead Developer
Dates: 2024-present

Description:
"A major factor in the rebranding of the company, including leading certain
initiatives. Managed team of 3-5 developers. Implemented microservices
architecture that reduced latency by 40%."
```

### Phase B: Parse into Atomic Claims (AI)

```python
def parse_experience_into_claims(user_text, experience_id):
    """
    Break down user's free-form text into individual verifiable claims.
    Each claim gets its own unique ID and must be associated with employer/role.
    """
    prompt = f"""
    User's job description:
    "{user_text}"

    Extract individual factual claims. Each claim should be:
    - Specific and atomic (one claim per statement)
    - Verifiable
    - Preserve exact scope/magnitude from original

    Return as JSON array of claims.
    """

    claims = ai.parse(prompt)
    # Returns:
    # [
    #   "A major factor in company rebranding, led certain initiatives",
    #   "Managed team of 3-5 developers",
    #   "Implemented microservices architecture",
    #   "Reduced latency by 40%"
    # ]

    for claim_text in claims:
        save_claim(
            experience_id=experience_id,
            claim_text=claim_text,
            original_user_text=user_text,
            parsed_by="gemini-1.5-pro",
            parsed_at=datetime.utcnow()
        )
```

**Database result:**
```
experience_claims table:
├─ id: claim-uuid-1
├─ experience_id: work-exp-uuid-1 (Latest Company)
├─ claim_text: "A major factor in company rebranding, led certain initiatives"
├─ original_user_text: "A major factor in the rebranding of the company..."
└─ claim_type: "achievement"

├─ id: claim-uuid-2
├─ experience_id: work-exp-uuid-1
├─ claim_text: "Managed team of 3-5 developers"
└─ claim_type: "responsibility"

├─ id: claim-uuid-3
├─ experience_id: work-exp-uuid-1
├─ claim_text: "Implemented microservices architecture"
└─ claim_type: "achievement"

├─ id: claim-uuid-4
├─ experience_id: work-exp-uuid-1
├─ claim_text: "Reduced latency by 40%"
├─ claim_type: "metric"
└─ metrics_value: {"percentage": 40, "type": "latency_reduction"}
```

### Phase C: Generate Sentences from Claims

```python
def generate_sentences_from_claim(claim_id, target_archetype):
    """
    Generate resume sentences from a single atomic claim.
    Preserve source linkage from the start - defeats purpose to figure out after.
    """
    claim = load_claim(claim_id)

    prompt = f"""
    Original claim: "{claim.claim_text}"
    Target job archetype: "{target_archetype}"

    Generate 3-5 resume bullet variations:
    - Stay truthful to the original claim
    - Don't exaggerate scope or impact
    - Reframe for target job type
    - Use strong action verbs
    """

    sentences = ai.generate(prompt)

    for sentence_text in sentences:
        # Validate before saving
        is_truthful = validate_against_claim(sentence_text, claim.claim_text)

        save_sentence(
            content_text=sentence_text,
            source_claim_id=claim_id,  # ← CRITICAL: PRESERVE SOURCE
            experience_id=claim.experience_id,  # ← REDUNDANT BUT USEFUL
            truthfulness_status="approved" if is_truthful else "rejected",
            rejection_reason=validation_explanation if not is_truthful else None,
            human_approval_status="pending"  # Awaits dashboard review
        )
```

**Database result:**
```
sentence_bank_resume table:
├─ id: sentence-uuid-1
├─ content_text: "Led a rebranding of the company"
├─ source_claim_id: claim-uuid-1
├─ experience_id: work-exp-uuid-1
├─ truthfulness_status: "rejected"
├─ rejection_reason: "Overstates 'major factor' as 'led'"
└─ human_approval_status: "rejected"

├─ id: sentence-uuid-2
├─ content_text: "Contributed to successful company rebranding initiative"
├─ source_claim_id: claim-uuid-1
├─ experience_id: work-exp-uuid-1
├─ truthfulness_status: "approved"
└─ human_approval_status: "pending"  ← Awaits human review

├─ id: sentence-uuid-3
├─ content_text: "Managed development team of 3-5 engineers"
├─ source_claim_id: claim-uuid-2
├─ experience_id: work-exp-uuid-1
├─ truthfulness_status: "approved"
└─ human_approval_status: "pending"
```

## Key Design Decisions

### Decision 1: Skills Field (DECIDED)

**Keep `matches_job_skill` as singular (VARCHAR(100))**
- One primary skill per sentence
- Current schema is correct as-is
- Status: ✅ DECIDED - No changes needed

### Decision 2: Tone Field

**Already singular:**
```python
tone = Column(String(100))  # One tone per sentence ✓
```
Status: ✅ Correct as-is

### Decision 3: Source Tracking Philosophy

**Rule: "The original experience or job position must accompany any record generated"**

- Defeats the purpose to try to figure out the source after the fact
- Each claim needs unique ID
- Must be associated with employer/volunteer role/education enrollment
- Full provenance chain: sentence → claim → experience

Status: ✅ Architecture supports this

### Decision 4: Human Approval Interface

**Requirements:**
- Connected with dashboard module (not yet built)
- Show sentence + source claim side-by-side
- Allow approve/reject/edit
- Display validation results
- Batch operations support

Status: ⏳ FUTURE WORK - Dashboard integration needed

## Exaggeration Detection Examples

### Hard Cases

**Case 1: Magnitude Changes**
```
Claim: "Managed team of 3-5 developers"

Generated: "Led team of developers"
→ Acceptable? (removed number - less specific but not false)

Generated: "Managed development team of 5"
→ Acceptable (specific number within range)

Generated: "Led team of 15 developers"
→ REJECT ❌ (wrong number - exaggerated)
```

**Case 2: Scope Changes**
```
Claim: "Major factor in rebranding, led certain initiatives"

Generated: "Contributed to company rebranding"
→ Acceptable (understated if anything)

Generated: "Led rebranding initiatives"
→ Borderline (removes "certain" - implies all initiatives)

Generated: "Led company rebranding"
→ REJECT ❌ (overstates scope - implies sole/primary leader)
```

**Case 3: Metric Changes**
```
Claim: "Reduced latency by 40%"

Generated: "Reduced system latency by 40%"
→ Acceptable (added context, same metric)

Generated: "Reduced latency by up to 40%"
→ Acceptable (hedged claim)

Generated: "Reduced latency by 50%"
→ REJECT ❌ (wrong number)
```

**Validation must catch:**
- Magnitude changes (numbers, scope)
- Ownership changes (contributor → leader)
- Definiteness changes ("certain" → "all")
- Metric inflation

## Open Questions for Future Resolution

### Question 1: Generic Sentences

Some sentences aren't tied to experiences:
- "Passionate about continuous learning"
- "Strong communication skills"

**Options:**
- A) Have `source_claim_id = NULL` for generic
- B) Create "generic_claims" for soft skills
- C) Still require human approval even if no experience link

**Decision needed:** TBD

### Question 2: Claim Parsing Automation

**Options:**
- A) Automatic - AI parses on submit, user reviews claims
- B) Manual - User explicitly creates each claim
- C) Hybrid - AI suggests, user must approve each claim

**Decision needed:** TBD

### Question 3: Current 711 Sentences Fate

They lack source tracking. Should we:
- A) Delete them (no provenance, can't validate)
- B) Keep as legacy (mark `source_claim_id = NULL`, `human_approval_status = 'legacy'`)
- C) Archive to JSON file, start fresh
- D) Attempt reverse-engineering (risky, may be inaccurate)

**Decision needed:** TBD

### Question 4: Dashboard Interface Features

**Required features:**
- Show sentence with source claim side-by-side
- Display validation results (why rejected)
- Edit sentence before approval
- Batch approve/reject
- Filter by status, experience, archetype

**Priority:** HIGH - blocks human-in-the-loop workflow

**Decision needed:** Detailed UI/UX design

### Question 5: Job Archetype Taxonomy

How many generic job archetypes?
- Broad: "Marketing Manager", "Senior Developer" (10-20 archetypes)
- Specific: "Marketing Automation Manager", "Lead Backend Engineer" (50+ archetypes)

**Trade-offs:**
- Fewer archetypes = more generic sentences = less targeted
- More archetypes = better targeting = more sentences to manage

**Decision needed:** TBD

## Migration Strategy

### Phase 1: Schema Changes (Database)

```sql
-- Create new tables
CREATE TABLE experience_claims (...);

-- Update existing tables
ALTER TABLE sentence_bank_resume ADD COLUMN source_claim_id UUID;
ALTER TABLE sentence_bank_resume ADD COLUMN human_approval_status VARCHAR(20);
ALTER TABLE sentence_bank_resume ADD COLUMN rejection_reason TEXT;

-- Fix foreign keys
ALTER TABLE sentence_bank_resume DROP CONSTRAINT sentence_bank_resume_experience_id_fkey;
ALTER TABLE sentence_bank_resume ADD CONSTRAINT sentence_bank_resume_experience_id_fkey
  FOREIGN KEY (experience_id) REFERENCES work_experiences(id);

-- Run schema automation
python database_tools/update_schema.py
```

### Phase 2: Handle Existing Sentences

**Options (decision needed):**
1. Archive to JSON, start fresh
2. Mark as legacy, keep in database
3. Delete and regenerate with proper tracking

### Phase 3: Build Claim Parsing Pipeline

```python
# New module: modules/experience_parser/
experience_parser.py
claim_validator.py
truthfulness_checker.py
```

### Phase 4: Dashboard Integration

```python
# Extend existing dashboard module
modules/dashboard/
├─ routes/
│   └─ sentence_approval.py  # New route
├─ templates/
│   └─ sentence_approval.html  # New UI
└─ static/
    └─ js/sentence_review.js  # Interactive review
```

### Phase 5: Generation Workflow Update

Update sentence generation to use new architecture:
1. User submits experience → Parse to claims
2. Generate sentences from claims → Preserve source_claim_id
3. Validate truthfulness → Mark approved/rejected
4. Human review in dashboard → Final approval
5. Approved sentences → Available for selection

## Implementation Checklist

### Database Layer
- [ ] Create `experience_claims` table
- [ ] Add source tracking columns to `sentence_bank_resume`
- [ ] Add source tracking columns to `sentence_bank_cover_letter`
- [ ] Fix foreign key from `job_applications` → `work_experiences`
- [ ] Run database automation tools
- [ ] Update SQLAlchemy models
- [ ] Update Pydantic schemas

### Backend Services
- [ ] Build claim parsing service (AI-based)
- [ ] Build truthfulness validation service
- [ ] Build sentence generation pipeline (with source tracking)
- [ ] Create API endpoints for claim management
- [ ] Create API endpoints for sentence approval
- [ ] Add validation logic for exaggeration detection

### Dashboard UI
- [ ] Design sentence approval interface
- [ ] Build claim viewing interface
- [ ] Implement approve/reject/edit workflow
- [ ] Add batch operations
- [ ] Create filtering and search
- [ ] Add analytics/stats view

### Data Migration
- [ ] Decide fate of 711 existing sentences
- [ ] Archive or delete current sentences
- [ ] Populate user's actual work experiences (3 exist, verify complete)
- [ ] Parse experiences into claims
- [ ] Generate new sentences with proper tracking

### Testing
- [ ] Test claim parsing accuracy
- [ ] Test exaggeration detection
- [ ] Test full pipeline: experience → claim → sentence
- [ ] Test dashboard approval workflow
- [ ] Test sentence selection for job applications

### Documentation
- [ ] Document claim parsing methodology
- [ ] Document validation rules
- [ ] Document dashboard usage
- [ ] Update CLAUDE.md with new architecture
- [ ] Create user guide for experience submission

## Success Metrics

**When implementation is complete:**
- ✅ 0% of sentences without source tracking (currently 100%)
- ✅ 100% of sentences have human approval status
- ✅ Exaggeration detection catches >90% of test cases
- ✅ No truthfulness checks on generic sentences (waste elimination)
- ✅ Full provenance chain: sentence → claim → experience
- ✅ Dashboard allows sentence review and approval
- ✅ Claims properly categorized (achievement, responsibility, metric)

## References

**Related Files:**
- `/workspace/database_tools/generated/models.py` (line 1489-1551: SentenceBankResume, SentenceBankCoverLetter)
- `/workspace/database_tools/generated/models.py` (line 1767-1801: WorkExperiences)
- `/workspace/scripts/migrate_to_digitalocean.py` (migration tool for production)

**Related Tables:**
- `sentence_bank_resume` (120 records, needs source tracking)
- `sentence_bank_cover_letter` (591 records, needs source tracking)
- `work_experiences` (3 records, user's actual jobs)
- `user_candidate_info` (1 record, user profile)

**Database Connection:**
- Environment: Devcontainer (connects via `host.docker.internal`)
- Local DB: `local_Merlin_3` on host machine
- Production DB: Digital Ocean Managed PostgreSQL (in `.env`)

## Timeline Estimate

**Phase 1 (Schema):** 1-2 days
**Phase 2 (Backend):** 3-5 days
**Phase 3 (Dashboard):** 5-7 days
**Phase 4 (Testing):** 2-3 days
**Phase 5 (Migration):** 1-2 days

**Total:** 12-19 days

## Priority Rationale

**HIGH PRIORITY** because:
1. Current system wastes 711 API calls (cost + inefficiency)
2. Cannot validate claims without source tracking
3. Blocks human approval workflow (quality control)
4. Foundation for all future resume/cover letter generation
5. Prevents AI exaggeration (truthfulness is core value)

---

**Document Status:** Draft - Awaiting review and prioritization
**Next Steps:** Review with user, prioritize phases, begin implementation
**Owner:** TBD
**Last Updated:** 2025-10-25
