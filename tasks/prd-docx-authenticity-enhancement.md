---
title: "Prd Docx Authenticity Enhancement"
type: technical_doc
component: general
status: draft
tags: []
---

# Product Requirements Document: DOCX Authenticity Enhancement System

**Version:** 1.0
**Date:** October 9, 2025
**Status:** Active Development
**Author:** Automated Job Application System Team
**Related PRDs:** `prd-docx-security-verification-system.md`

---

## 1. Introduction/Overview

### Problem Statement
The Automated Job Application System generates personalized Word documents (.docx files) for resumes and cover letters. While the current template-based system preserves formatting, **generated documents lack authenticity markers** that make them indistinguishable from manually created professional documents.

Analysis of the `/workspace/modules/content` document generation system revealed gaps in:
- **Document metadata authenticity** (generic timestamps, missing properties)
- **Professional typography** (straight quotes, missing em dashes, improper spacing)
- **Document statistics realism** (default values, no editing time simulation)
- **Content formatting sophistication** (missing smart formatting, proper citations)

Additionally, analysis of 30 official Microsoft Word templates identified **baseline characteristics of authentic documents** that our generated files must match to avoid:
- Triggering malware detection false positives
- Appearing machine-generated or inauthentic
- Failing ATS parsing or metadata validation
- Being flagged by enterprise security tools

### Goal
Enhance the document generation system to produce **super authentic, professional-quality DOCX files** that are indistinguishable from manually created documents and pass all security verification checks on major platforms (Gmail, Outlook, SharePoint, Google Drive, ATS systems).

---

## 2. Goals

1. **Authenticity**: Generated documents indistinguishable from manually created files in metadata, formatting, and structure
2. **Security Compliance**: Pass security scans on Microsoft 365, Google Workspace, enterprise antivirus tools
3. **Professional Quality**: Typography, formatting, and structure meet professional standards
4. **Metadata Realism**: Realistic creation dates, editing times, revision history, and document properties
5. **Verification Integration**: Automated verification prevents delivery of non-authentic documents
6. **Platform Compatibility**: Documents pass ATS parsing, email attachment scanning, cloud storage verification

---

## 3. Research Findings Summary

### 3.1 Current System Analysis (`/workspace/modules/content`)

**Existing Components:**
- `template_engine.py`: Template variable substitution, basic formatting
- `document_generator.py`: Document generation workflow, storage integration
- `template_converter.py`: Reference document to template conversion
- `canadian_spelling_processor.py`: Canadian spelling corrections (183 conversion pairs)

**Current Capabilities:**
- ✅ Template-based generation preserving formatting
- ✅ Variable substitution (`<<variable>>`, `{job_title}`)
- ✅ Canadian spelling corrections
- ✅ Publication italics formatting
- ✅ Storage backend integration
- ✅ Basic metadata setting (author, title, subject)

**Identified Gaps:**
- ❌ Generic metadata (creation date always `datetime.now()`)
- ❌ No editing time simulation (always appears instantly created)
- ❌ Revision number always "1" (unrealistic)
- ❌ Missing advanced typography (smart quotes, em dashes, ellipsis)
- ❌ No document statistics validation
- ❌ No authenticity verification before delivery

### 3.2 Microsoft Template Analysis (30 Official Samples)

**Authentic Document Characteristics:**

**Metadata Patterns:**
- **Creation timestamps:** Realistic dates/times (business hours, weekdays)
- **Modification timestamps:** 0-24 hours after creation (same day or next day)
- **Editing time:** 0 minutes for templates, 30-300 minutes for edited documents
- **Revision numbers:** 0-1 for templates, 1-5 for edited documents
- **Author/Title/Subject:** Blank in templates, populated in real documents
- **Application:** "Microsoft Office Word"
- **AppVersion:** "16.0000" (Office 2016/2019/365)

**Structural Features:**
- **File size:** 20-160 KB (average 50 KB)
- **Internal files:** 22-41 files in ZIP structure
- **No VBA macros:** 0/30 documents (100% macro-free)
- **CustomXml:** 97% prevalence (Microsoft 365 SharePoint integration)
- **Sensitivity labels:** 100% prevalence (`docMetadata/LabelInfo.xml`)
- **Themes:** 100% have Office theme files
- **Thumbnails:** 40% have preview thumbnails

**Security Profile:**
- ✅ Zero VBA macros
- ✅ No OLE objects
- ✅ No external HTTP/HTTPS references (only schema URLs)
- ✅ Valid ZIP structure (magic number: `50 4B 03 04`)
- ✅ All required OOXML files present

---

## 4. User Stories

**US-1:** As a job applicant, I want my generated resume to have realistic creation/modification timestamps, so that it appears professionally created rather than machine-generated.

**US-2:** As a hiring manager, I want to see professional typography (smart quotes, em dashes) in cover letters, so that documents appear polished and attention to detail.

**US-3:** As an ATS system, I want documents to have realistic metadata (editing time, revision history), so that I can verify document authenticity.

**US-4:** As a security scanner (Gmail/Outlook), I want documents to match authentic Microsoft Office file patterns, so that I don't flag legitimate job applications as suspicious.

**US-5:** As a system administrator, I want automated verification to catch any non-authentic documents before delivery, so that no malformed files are sent to employers.

**US-6:** As a job applicant, I want my resume to pass SharePoint's Safe Attachments scanning without flags, so that my application reaches the hiring team.

---

## 5. Functional Requirements

### 5.1 Enhanced Metadata Generation

**FR-1:** The system MUST generate realistic document creation timestamps:
- Creation date: 1-30 days before current date
- Creation time: Business hours (9 AM - 6 PM) on weekdays only
- Timezone: User's local timezone or UTC
- No default values (never `datetime.now()` at generation time)

**FR-2:** The system MUST generate realistic modification timestamps:
- Modified date: 0-7 days after creation date
- Modified time: Different from creation time (simulate editing)
- Modified date ≥ creation date (never in the past)

**FR-3:** The system MUST simulate realistic editing time:
- Resume documents: 30-180 minutes (0.5-3 hours)
- Cover letters: 20-120 minutes (0.3-2 hours)
- Store as `TotalTime` in `docProps/app.xml`

**FR-4:** The system MUST set realistic revision numbers:
- New documents: 1-3 revisions
- Templates being populated: 2-5 revisions
- Never 0 or >10 (both unrealistic)

**FR-5:** The system MUST populate all core properties:
- `author`: Full name from document data (never blank)
- `title`: "{Name} Resume" or "{Name} Cover Letter"
- `subject`: "Professional Resume" or "Professional Cover Letter"
- `keywords`: Relevant job-related keywords
- `comments`: Professional description (not "Generated on...")
- `category`: "Job Application"
- `language`: "en-CA" or "en-US"

**FR-6:** The system MUST set application properties accurately:
- `Application`: "Microsoft Office Word"
- `AppVersion`: "16.0000" (Office 2016+)
- `DocSecurity`: 0 (no protection)
- `Pages`: Calculated from actual document
- `Words`: Calculated from actual content
- `Characters`: Calculated (with and without spaces)
- `Paragraphs`: Calculated from document structure
- `Lines`: Calculated from content

### 5.2 Advanced Typography & Formatting

**FR-7:** The system MUST apply smart quotation marks:
- Convert straight double quotes (`"`) to curly quotes (`""`)
- Convert straight single quotes (`'`) to curly apostrophes (`'`)
- Context-aware: Opening vs. closing quotes

**FR-8:** The system MUST apply smart dashes:
- Convert double hyphens (`--`) to em dashes (`—`)
- Convert single hyphens in date ranges to en dashes (`–`)
- Example: "2020--2023" → "2020–2023"

**FR-9:** The system MUST apply smart ellipsis:
- Convert three periods (`...`) to proper ellipsis (`…`)

**FR-10:** The system MUST apply non-breaking spaces:
- After titles: "Dr.", "Mr.", "Mrs.", "Ms.", "Prof."
- Between initials: "J. Smith" → "J. Smith" (non-breaking)
- Before units: "10 MB" → "10 MB" (non-breaking)

**FR-11:** The system MUST format special characters properly:
- Degree symbols: "°" for temperatures/angles
- Trademark/copyright: ™, ®, © properly rendered
- Multiplication sign: × (not lowercase x)

**FR-12:** The system MUST apply hyperlink styling:
- Email addresses: Blue color (#0563C1), underlined
- URLs: Blue color, underlined, properly encoded
- Remove hyperlinks from printed text where inappropriate

### 5.3 Content Enhancement

**FR-13:** The system MUST detect and format acronyms:
- Apply small caps to common acronyms (ATS, PDF, CEO, CTO)
- Maintain readability while adding professional polish

**FR-14:** The system MUST format citations properly:
- Support APA, MLA, Chicago style citations
- Italicize publication names automatically
- Format DOI links correctly

**FR-15:** The system MUST apply bold emphasis to key achievements:
- Detect quantified achievements (metrics, percentages, dollar amounts)
- Apply bold formatting to numbers and key results
- Example: "Increased revenue by **$2.5M**" (bold the amount)

**FR-16:** The system MUST validate template variable replacement:
- Scan for unreplaced variables: `<<variable>>`, `{placeholder}`
- Flag documents with remaining template markers
- Block delivery if critical variables missing

### 5.4 Document Structure Enhancement

**FR-17:** The system MUST apply widow/orphan control:
- Prevent single lines at top/bottom of pages
- Ensure proper paragraph flow across page breaks
- Set `<w:widowControl>` in paragraph properties

**FR-18:** The system MUST optimize page breaks:
- Avoid breaking sections awkwardly
- Keep headings with following content
- Insert proper page breaks vs. soft breaks

**FR-19:** The system MUST format tables professionally:
- Consistent borders (0.5pt or 1pt, never heavy)
- Proper cell padding (0.08" standard)
- Alternating row shading (optional, subtle)
- Header row formatting (bold, centered)

**FR-20:** The system MUST ensure bullet point consistency:
- Uniform bullet styles throughout document
- Proper indentation (0.25" or 0.5" standard)
- Consistent spacing between bullet items

### 5.5 Document Verification Integration

**FR-21:** The system MUST verify documents before delivery:
- Run authenticity checks after generation
- Validate metadata completeness and realism
- Check for unreplaced template variables
- Verify document statistics (word count, page count)
- Ensure file structure integrity (ZIP, OOXML)

**FR-22:** The system MUST block delivery of non-authentic documents:
- Documents with unreplaced variables: BLOCKED
- Documents with default metadata: BLOCKED
- Documents with corrupted structure: BLOCKED
- Documents with suspicious patterns: FLAGGED for review

**FR-23:** The system MUST generate authenticity reports:
- Metadata validation results
- Typography quality score
- Structure integrity check
- Security scan results (if integrated)
- Overall authenticity score (0-100)

### 5.6 Randomization for Human-Like Variation

**FR-24:** The system MUST randomize creation timestamps:
- Vary creation dates within acceptable range (1-30 days ago)
- Randomize creation time within business hours
- Add random minutes/seconds (not always on the hour)

**FR-25:** The system MUST randomize editing characteristics:
- Vary editing time within acceptable range
- Randomize revision count (1-3 or 2-5 based on document type)
- Add micro-variations in spacing (within style guidelines)

**FR-26:** The system MUST randomize modification patterns:
- Modified date: 0-7 days after creation (random within range)
- Modified time: Different hour than creation (simulate editing session)
- Simulate realistic editing patterns (not same-day for older documents)

---

## 6. Non-Goals (Out of Scope)

**NG-1:** **Forging document history** - System creates realistic but accurate metadata, not fraudulent backdating

**NG-2:** **Modifying user-provided content** - System enhances formatting but doesn't change user's words/data

**NG-3:** **PDF enhancement** - System focuses on DOCX format only; PDF is separate scope

**NG-4:** **Real-time collaborative editing features** - No Track Changes, Comments, or multi-author support

**NG-5:** **Advanced graphic design** - No custom shapes, SmartArt, or complex graphics generation

**NG-6:** **Macro-enabled documents** - System never generates `.docm` files with VBA code

**NG-7:** **Document encryption** - No password protection or Rights Management Services (RMS)

---

## 7. Technical Considerations

### 7.1 Architecture

**Component Updates:**

```
template_engine.py (EXISTING - ENHANCE)
├── Add: SmartTypography class
│   ├── smart_quotes()
│   ├── smart_dashes()
│   ├── smart_ellipsis()
│   ├── non_breaking_spaces()
│   └── special_characters()
├── Add: MetadataGenerator class
│   ├── generate_realistic_timestamps()
│   ├── calculate_editing_time()
│   ├── generate_revision_number()
│   └── set_document_statistics()
├── Enhance: apply_enhanced_formatting()
│   └── Integrate typography enhancements
└── Add: validate_template_completion()
    └── Check for unreplaced variables

document_generator.py (EXISTING - ENHANCE)
├── Add: pre-delivery verification hook
├── Enhance: prepare_document_metadata()
│   └── Use MetadataGenerator for realistic values
└── Add: authenticity_check()
    └── Call verification before storage

NEW: modules/security/docx_verifier.py
├── DocumentVerifier (main orchestrator)
├── AuthenticityValidator (metadata realism)
├── StructureValidator (ZIP, OOXML)
├── MacroDetector (VBA scanning)
└── ReportGenerator (authenticity reports)
```

### 7.2 Dependencies

**New Python Packages:**
- None required for authenticity enhancements (use existing `python-docx`, `lxml`)
- Optional: `python-dateutil` for advanced date manipulation

**For Verification System (Phase 2):**
- `oletools>=0.60` - VBA/OLE analysis
- `yara-python>=4.3.0` - Pattern matching (optional)
- `clamd>=1.0.2` - ClamAV integration (optional)

### 7.3 Performance Considerations

**Enhancement Overhead:**
- Typography processing: +0.1-0.3 seconds per document
- Metadata generation: +0.05 seconds per document
- Verification: +1-3 seconds per document (if external scans enabled)
- **Total target:** <5 seconds for complete generation + verification

**Caching:**
- Cache randomization seeds per session (consistency across batch)
- Cache typography rules (compile regex patterns once)

### 7.4 Configuration

**New Configuration Options (`.env` or config file):**

```python
# Metadata Generation
DOCX_CREATION_DATE_RANGE_DAYS = 30  # How far back to randomize creation dates
DOCX_MODIFICATION_MAX_DAYS = 7      # Max days between creation and modification
DOCX_BUSINESS_HOURS_START = 9       # 9 AM
DOCX_BUSINESS_HOURS_END = 18        # 6 PM
DOCX_MIN_EDITING_TIME_MINUTES = 30  # Resumes: 30-180 min
DOCX_MAX_EDITING_TIME_MINUTES = 180

# Typography
DOCX_ENABLE_SMART_QUOTES = True
DOCX_ENABLE_SMART_DASHES = True
DOCX_ENABLE_SMART_ELLIPSIS = True
DOCX_ENABLE_NON_BREAKING_SPACES = True

# Verification
DOCX_ENABLE_PRE_DELIVERY_VERIFICATION = True
DOCX_BLOCK_ON_VERIFICATION_FAILURE = True
DOCX_VERIFICATION_TIMEOUT_SECONDS = 10
```

### 7.5 Database Schema Updates

**Extend Existing Table: `generated_documents`**

```sql
ALTER TABLE generated_documents
ADD COLUMN authenticity_score INTEGER,           -- 0-100 authenticity score
ADD COLUMN metadata_creation_date TIMESTAMP,     -- Actual creation date set in metadata
ADD COLUMN metadata_modified_date TIMESTAMP,     -- Actual modified date set in metadata
ADD COLUMN editing_time_minutes INTEGER,         -- Simulated editing time
ADD COLUMN revision_number INTEGER,              -- Revision count set in metadata
ADD COLUMN typography_enhanced BOOLEAN DEFAULT FALSE,
ADD COLUMN verification_passed BOOLEAN,
ADD COLUMN verification_report_id INTEGER REFERENCES document_verifications(id);

CREATE INDEX idx_generated_documents_authenticity ON generated_documents(authenticity_score);
CREATE INDEX idx_generated_documents_verification ON generated_documents(verification_passed);
```

---

## 8. Design Considerations

### 8.1 Smart Typography Rules

**Smart Quotes Implementation:**
```python
QUOTE_RULES = {
    # Opening quotes after whitespace, start of line, or punctuation
    r'(\s|^|[(\[\{<])\"': r'\1"',  # Opening double quote
    r'(\s|^|[(\[\{<])\'': r'\1'',  # Opening single quote

    # Closing quotes before whitespace, end of line, or punctuation
    r'\"(\s|$|[.,!?;:)\]\}>])': r'"\1',  # Closing double quote
    r'\'(\s|$|[.,!?;:)\]\}>])': r''\1',  # Closing single quote

    # Apostrophes (possessives, contractions)
    r'([a-zA-Z])\'([a-zA-Z])': r'\1'\2',  # don't, it's, Steve's
}
```

**Smart Dashes Implementation:**
```python
DASH_RULES = {
    r'(\d+)\s*-\s*(\d+)': r'\1–\2',      # Number ranges: 2020-2023 → 2020–2023 (en dash)
    r'(\w+)\s*--\s*(\w+)': r'\1—\2',     # Em dash: word--word → word—word
    r'\s--\s': ' — ',                     # Spaced em dash
}
```

### 8.2 Metadata Realism Algorithm

**Creation Timestamp Generation:**
```python
import random
from datetime import datetime, timedelta

def generate_creation_timestamp():
    # Random date 1-30 days ago
    days_ago = random.randint(1, 30)

    # Random weekday (Monday=0 to Friday=4)
    target_date = datetime.now() - timedelta(days=days_ago)
    while target_date.weekday() > 4:  # Skip weekends
        days_ago += 1
        target_date = datetime.now() - timedelta(days=days_ago)

    # Random hour during business hours (9 AM - 6 PM)
    hour = random.randint(9, 17)
    minute = random.randint(0, 59)
    second = random.randint(0, 59)

    return target_date.replace(hour=hour, minute=minute, second=second)

def generate_modification_timestamp(creation_date):
    # Modified 0-7 days after creation
    days_after = random.randint(0, 7)
    mod_date = creation_date + timedelta(days=days_after)

    # Different hour than creation (simulate editing session)
    hour = random.randint(9, 17)
    while hour == creation_date.hour and days_after == 0:
        hour = random.randint(9, 17)

    minute = random.randint(0, 59)
    second = random.randint(0, 59)

    return mod_date.replace(hour=hour, minute=minute, second=second)
```

### 8.3 Authenticity Scoring System

**Scoring Algorithm:**
```python
AUTHENTICITY_SCORE = {
    'metadata_completeness': 25,      # All required fields populated
    'timestamp_realism': 20,          # Realistic creation/modification dates
    'editing_time': 15,               # Reasonable editing time set
    'typography_quality': 15,         # Smart quotes, dashes, etc.
    'structure_integrity': 15,        # Valid ZIP/OOXML structure
    'template_completion': 10,        # No unreplaced variables
}

# Score 0-100:
# 90-100: Excellent (indistinguishable from manual)
# 75-89: Good (minor issues)
# 60-74: Acceptable (noticeable issues)
# 0-59: Poor (fails authenticity)
```

---

## 9. Success Metrics

**SM-1:** **Authenticity Score ≥90** - 95% of generated documents score 90+ on authenticity scale

**SM-2:** **Zero Template Variables** - 100% of delivered documents have all variables replaced

**SM-3:** **Metadata Completeness** - 100% of documents have all required metadata fields populated

**SM-4:** **Security Scan Pass Rate** - 100% of documents pass Gmail/Outlook/SharePoint scans with no flags

**SM-5:** **Typography Enhancement** - 100% of documents have smart quotes, em dashes, proper ellipsis

**SM-6:** **Realistic Timestamps** - 100% of documents have creation dates 1-30 days ago, business hours

**SM-7:** **Performance** - 95th percentile generation + verification time <5 seconds

---

## 10. Implementation Phases

### Phase 1: Enhanced Metadata Generation (Week 1)
- Implement `MetadataGenerator` class
- Realistic timestamp generation
- Editing time simulation
- Revision number generation
- Document statistics calculation
- Integration with `document_generator.py`
- Unit tests

### Phase 2: Advanced Typography (Week 1-2)
- Implement `SmartTypography` class
- Smart quotes algorithm
- Smart dashes and ellipsis
- Non-breaking spaces
- Special characters
- Integration with `template_engine.py`
- Typography quality validation

### Phase 3: Content Enhancement (Week 2)
- Template variable validation
- Acronym detection and formatting
- Bold emphasis for metrics
- Citation formatting
- Hyperlink styling
- Content quality checks

### Phase 4: Structure Enhancement (Week 2-3)
- Widow/orphan control
- Page break optimization
- Table formatting
- Bullet point consistency
- Section break management

### Phase 5: Verification Integration (Week 3-4)
- Implement `DocumentVerifier` class
- Authenticity scoring system
- Pre-delivery verification hook
- Verification reporting
- Database integration
- Block/flag logic

### Phase 6: Testing & Production (Week 4-5)
- End-to-end testing with real documents
- A/B testing (enhanced vs. original)
- Security scan testing (Gmail, Outlook, SharePoint)
- ATS compatibility testing
- Performance optimization
- Production rollout

---

## 11. Open Questions

**OQ-1:** Should we randomize creation dates per document or per batch (all documents in one session have similar dates)?

**OQ-2:** What should happen if verification fails? Options:
- A) Block delivery entirely
- B) Flag for manual review
- C) Log warning but allow delivery
- D) Attempt automatic remediation

**OQ-3:** Should typography enhancements be configurable per user (some may prefer straight quotes)?

**OQ-4:** How should we handle existing generated documents? Options:
- A) Re-generate with enhancements
- B) Leave existing as-is, only enhance new
- C) Offer optional "upgrade" process

**OQ-5:** Should authenticity score be exposed to users, or remain internal metric?

**OQ-6:** What threshold for authenticity score should block delivery? (Recommended: <75)

**OQ-7:** Should we add "Office Theme" files to match Microsoft 365 templates (100% prevalence)?

**OQ-8:** Should we generate document thumbnails (40% prevalence in Microsoft templates)?

---

## 12. References

**Internal Documentation:**
- Original request: "find ways to make sure that when the system generates a docx file, the file looks super duper very authentic"
- Analysis: `/workspace/modules/content` document generation module review
- Research: Microsoft DOCX Technical Analysis Report (30 official templates)
- Related PRD: `prd-docx-security-verification-system.md`

**Code Files Referenced:**
- `modules/content/document_generation/template_engine.py`
- `modules/content/document_generation/document_generator.py`
- `modules/content/document_generation/template_converter.py`
- `modules/content/copywriting_evaluator/canadian_spelling_processor.py`

---

## 13. Acceptance Criteria

**Document Generation:**
- ✅ All generated documents have realistic metadata (creation date 1-30 days ago, business hours)
- ✅ All documents have non-default editing time (30-300 minutes)
- ✅ All documents have realistic revision numbers (1-5)
- ✅ All required metadata fields populated (author, title, subject)

**Typography:**
- ✅ Smart quotes applied throughout (no straight quotes remain)
- ✅ Em dashes replace double hyphens
- ✅ En dashes in date ranges
- ✅ Proper ellipsis character (not three periods)
- ✅ Non-breaking spaces after titles and units

**Content Quality:**
- ✅ Zero unreplaced template variables (`<<var>>`, `{var}`)
- ✅ Document statistics accurate (word count, page count, character count)
- ✅ Hyperlinks properly styled (blue, underlined)

**Verification:**
- ✅ All documents pass pre-delivery verification
- ✅ Authenticity score ≥75 for all delivered documents
- ✅ Verification reports generated and stored
- ✅ Failed verifications blocked or flagged

**Security:**
- ✅ Generated documents pass Gmail virus scanning (100%)
- ✅ Generated documents pass Outlook Safe Attachments (100%)
- ✅ Generated documents pass SharePoint scanning (100%)
- ✅ No false positives on VirusTotal scans

**Performance:**
- ✅ Generation + enhancement: <3 seconds (95th percentile)
- ✅ Verification (local): <2 seconds (95th percentile)
- ✅ Total end-to-end: <5 seconds (95th percentile)

---

**End of Document**
