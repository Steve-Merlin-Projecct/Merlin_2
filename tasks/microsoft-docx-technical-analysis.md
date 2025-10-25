---
title: "Microsoft Docx Technical Analysis"
type: technical_doc
component: general
status: draft
tags: []
---

# Microsoft DOCX Technical Analysis Report

**Date:** October 9, 2025
**Samples Analyzed:** 30 official Microsoft Word templates
**Source:** `/workspace/.trees/docx-verification/content_template_library/Microsoft-downlaods/`
**Purpose:** Establish baseline characteristics of legitimate, professional DOCX files for security verification system

---

## Executive Summary

Analyzed 30 official Microsoft Word document templates (resumes and cover letters) to establish technical baselines for authentic DOCX file structure, metadata patterns, and embedded resources. These findings will inform the DOCX Security Verification System to minimize false positives while detecting malicious documents.

**Key Findings:**
- ✅ **Zero VBA macros** in all 30 documents (0%)
- ✅ **100% sensitivity label** support (Microsoft 365 compliance feature)
- ✅ **100% creation timestamps** present in metadata
- ⚠️ **Minimal metadata**: Most fields (author, title, subject) are blank in templates
- ⚠️ **CustomXml prevalent**: 97% contain customXml data (SharePoint/compliance integration)

---

## 1. File Size Statistics

**Distribution:**
- **Minimum:** 22,405 bytes (21.9 KB)
- **Maximum:** 160,381 bytes (156.6 KB)
- **Average:** 51,350 bytes (50.1 KB)

**Implications for Verification:**
- Typical professional resume/cover letter: **20-160 KB**
- Files significantly outside this range warrant inspection
- Large files (>200 KB) may contain excessive embedded images or suspicious content

---

## 2. Internal ZIP Structure Analysis

### 2.1 File Count Distribution

| Internal Files | # Documents | Notes |
|----------------|-------------|-------|
| 22-25 files | 8 documents | Minimal structure (simple documents) |
| 29-35 files | 16 documents | Standard structure (most common) |
| 37-41 files | 6 documents | Complex structure (images, glossaries) |

**Typical File Count:** 22-41 internal files

### 2.2 Required OOXML Files (Always Present)

```
[Content_Types].xml          - Content type definitions (REQUIRED)
_rels/.rels                  - Package-level relationships
docProps/app.xml             - Application properties
docProps/core.xml            - Core document metadata
word/document.xml            - Main document content
word/_rels/document.xml.rels - Document relationships
word/settings2.xml           - Document settings
word/styles2.xml             - Style definitions
word/fontTable2.xml          - Font table
word/theme/theme11.xml       - Theme definition
word/webSettings2.xml        - Web settings
```

### 2.3 Optional but Common Files

```
word/glossary/document.xml   - Building blocks/glossary (60% prevalence)
docMetadata/LabelInfo.xml    - Sensitivity labels (100% prevalence)
docProps/thumbnail.emf       - Document thumbnail (40% prevalence)
customXml/item*.xml          - Custom XML data (97% prevalence)
word/media/image*.png/svg    - Embedded images (variable)
word/endnotes.xml            - Endnotes
word/footnotes.xml           - Footnotes
```

---

## 3. Metadata Characteristics

### 3.1 Core Properties (docProps/core.xml)

**Analyzed Sample:**
```xml
<cp:coreProperties>
    <dc:title></dc:title>                    <!-- Blank in templates -->
    <dc:subject></dc:subject>                <!-- Blank in templates -->
    <dc:creator></dc:creator>                <!-- Blank in templates -->
    <cp:keywords></cp:keywords>              <!-- Blank in templates -->
    <dc:description></dc:description>        <!-- Blank in templates -->
    <cp:lastModifiedBy></cp:lastModifiedBy>  <!-- Blank in templates -->
    <cp:revision>1</cp:revision>             <!-- 0-1 typical for templates -->
    <dcterms:created>2023-05-01T23:08:00Z</dcterms:created>  <!-- ✓ Always present -->
    <dcterms:modified>2023-05-01T23:08:00Z</dcterms:modified>  <!-- ✓ Always present -->
</cp:coreProperties>
```

**Key Insights:**
- **Creation/Modified Dates:** 100% of documents have realistic timestamps
- **Blank Fields:** Author, title, subject, keywords are intentionally blank in templates
- **Revision Numbers:** 0-1 for templates (47% have revision tracking)
- **Same Create/Modify Date:** Common in templates (created and saved once)

**Timestamp Patterns:**
- Templates created during business hours (mostly UTC daytime)
- Date ranges: 2023-2024 (recent, actively maintained)
- Modified date = Created date (no subsequent edits)

### 3.2 Application Properties (docProps/app.xml)

**Standard Fields Present:**
```xml
<Properties>
    <Template>TM67390153</Template>           <!-- Microsoft template ID -->
    <TotalTime>0</TotalTime>                  <!-- 0 minutes editing time -->
    <Pages>1</Pages>                          <!-- 1-2 pages typical -->
    <Words>176</Words>                        <!-- 100-300 words for templates -->
    <Characters>1007</Characters>             <!-- Character count -->
    <Application>Microsoft Office Word</Application>
    <DocSecurity>0</DocSecurity>              <!-- No protection -->
    <Lines>8</Lines>                          <!-- Line count -->
    <Paragraphs>2</Paragraphs>                <!-- Paragraph count -->
    <CharactersWithSpaces>1181</CharactersWithSpaces>
    <AppVersion>16.0000</AppVersion>          <!-- Office 2016+ -->
</Properties>
```

**Key Insights:**
- **Application:** Always "Microsoft Office Word"
- **AppVersion:** 16.0000 (Office 2016/2019/365)
- **TotalTime:** 0 minutes (templates not edited after creation)
- **Template ID:** Proprietary Microsoft template identifiers (e.g., TM67390153)
- **DocSecurity:** 0 (no password protection or restrictions)

---

## 4. Feature Prevalence Analysis

| Feature | Prevalence | Security Implication |
|---------|------------|---------------------|
| **VBA Macros** | 0/30 (0%) | ✅ Safe - No executable code |
| **Sensitivity Labels** | 30/30 (100%) | ✅ Microsoft 365 compliance (docMetadata/LabelInfo.xml) |
| **Theme Files** | 30/30 (100%) | ✅ Expected - Standard Office theme |
| **Creation Timestamps** | 30/30 (100%) | ✅ Authentic - Realistic metadata |
| **CustomXml Data** | 29/30 (97%) | ⚠️ Common - SharePoint/metadata integration |
| **Glossary/Building Blocks** | 18/30 (60%) | ✅ Safe - Reusable content blocks |
| **Revision Tracking** | 14/30 (47%) | ✅ Benign - Version control metadata |
| **Thumbnails** | 12/30 (40%) | ✅ Safe - Preview images |
| **OLE Objects** | 0/30 (0%) | ✅ Safe - No embedded executable objects |
| **External URLs** | 0/30 (0%) | ✅ Safe - Only internal schema references |

---

## 5. CustomXml Analysis

### 5.1 Purpose and Prevalence
- **Found in:** 97% of documents (29/30)
- **Purpose:** SharePoint metadata, Microsoft 365 compliance properties, document management
- **Location:** `customXml/item*.xml` with corresponding `itemProps*.xml`

### 5.2 Sample Content
```xml
<?xml version="1.0" encoding="utf-8"?>
<p:properties xmlns:p="http://schemas.microsoft.com/office/2006/metadata/properties">
    <documentManagement>
        <_ip_UnifiedCompliancePolicyUIAction xmlns="http://schemas.microsoft.com/sharepoint/v3" xsi:nil="true"/>
        <Image xmlns="71af3243-3dd4-4a8d-8c0d-dd76da1f02a5">
            <Url xsi:nil="true"></Url>
            <Description xsi:nil="true"></Description>
        </Image>
    </documentManagement>
</p:properties>
```

**Key Insights:**
- CustomXml is **NOT malicious** - it's a standard Microsoft 365 feature
- Used for SharePoint integration and compliance policies
- Should **NOT** be flagged as suspicious in verification system
- Contains empty/null values in templates (populated when document is used)

---

## 6. Sensitivity Labels (Microsoft 365)

### 6.1 Discovery
- **Prevalence:** 100% of analyzed documents
- **Location:** `docMetadata/LabelInfo.xml`
- **Purpose:** Microsoft Information Protection (MIP) / data classification

### 6.2 Significance
This is a **modern Microsoft 365 feature** for:
- Data loss prevention (DLP)
- Compliance and governance
- Automatic classification and protection

**Verification System Action:**
- ✅ Presence of `LabelInfo.xml` indicates legitimate Microsoft 365 document
- ⚠️ Absence is acceptable (older Office versions, non-365 documents)
- ❌ Malformed `LabelInfo.xml` could indicate tampering

---

## 7. Embedded Resources Analysis

### 7.1 Images and Media
**Example: Classic UI/UX Designer Resume**
- **Image Count:** 8 embedded images
- **Formats:** PNG, SVG
- **Sizes:** 0.7 KB - 12.3 KB (small icons/graphics)
- **Location:** `word/media/image*.png` or `image*.svg`

**Security Considerations:**
- Images are **expected** in modern resumes
- Large images (>100 KB) warrant inspection
- SVG files should be scanned for embedded scripts (XSS vectors)

### 7.2 Fonts
- **Embedded Fonts:** 0/30 documents
- **Font References:** All documents use system fonts via `word/fontTable2.xml`

**Implications:**
- Embedded fonts are **rare** in legitimate documents
- Presence of `fonts/` directory warrants closer inspection
- Font files can be vectors for malware (rare but possible)

### 7.3 OLE Objects
- **Prevalence:** 0/30 (0%)
- **Detection Method:** Look for `embeddings/` directory or `activeX` files

**Security:**
- OLE objects are **high-risk** for malware embedding
- Absence is ideal for security verification
- Presence should trigger elevated scrutiny

---

## 8. Relationships and External References

### 8.1 Internal Relationships (word/_rels/document.xml.rels)

**Typical Relationship Types:**
```xml
<Relationships>
    <Relationship Type=".../glossaryDocument" Target="/word/glossary/document.xml" />
    <Relationship Type=".../settings" Target="/word/settings2.xml" />
    <Relationship Type=".../fontTable" Target="/word/fontTable2.xml" />
    <Relationship Type=".../styles" Target="/word/styles2.xml" />
    <Relationship Type=".../theme" Target="/word/theme/theme11.xml" />
    <Relationship Type=".../customXml" Target="/customXml/item4.xml" />
    <Relationship Type=".../endnotes" Target="/word/endnotes.xml" />
    <Relationship Type=".../footnotes" Target="/word/footnotes.xml" />
    <Relationship Type=".../webSettings" Target="/word/webSettings2.xml" />
</Relationships>
```

**All relationships are internal** (no external HTTP/HTTPS URLs)

### 8.2 Schema References (Not Security Threats)
Documents reference standard Office Open XML schemas:
- `http://schemas.openxmlformats.org/package/2006/relationships`
- `http://schemas.openxmlformats.org/officeDocument/2006/relationships/*`
- `http://schemas.microsoft.com/office/2006/metadata/properties`

**These are NOT malicious external references** - they are XML namespace declarations.

### 8.3 Malicious External References (None Found)
**What to look for:**
- ❌ Remote template injection: `Target="http://malicious.com/template.dotx"`
- ❌ External OLE links: `TargetMode="External"` with HTTP URLs
- ❌ Embedded video URLs: Modified video frame URLs

**Verification System:**
- Scan relationships for `TargetMode="External"` + HTTP/HTTPS
- Flag non-schema HTTP/HTTPS references
- Whitelist standard Microsoft/OpenXML schema URLs

---

## 9. Document Settings Analysis

### 9.1 Common Settings (word/settings2.xml)
- Zoom levels (100%, 125%)
- Default tab stops (720 twips = 0.5 inches)
- View settings (Print, Web, Outline)
- Compatibility mode settings

### 9.2 Security-Relevant Settings
**Track Changes:**
- Not enabled in templates (would be suspicious in generated documents)

**Document Protection:**
- Not found in any analyzed documents
- Password protection or editing restrictions would be flagged

**Macro Security:**
- No macro settings found (no VBA present)

---

## 10. Verification System Recommendations

### 10.1 Baseline Validation Rules

**MUST HAVE (Critical):**
1. ✅ `[Content_Types].xml` present in root
2. ✅ Valid ZIP structure (magic number: `50 4B 03 04`)
3. ✅ `word/document.xml` present
4. ✅ `docProps/core.xml` with creation timestamp
5. ✅ No `word/vbaProject.bin` (macros)

**SHOULD HAVE (Expected):**
6. ✅ `docProps/app.xml` with realistic statistics
7. ✅ `word/styles2.xml`, `word/fontTable2.xml`, `word/theme/`
8. ✅ File size: 20-200 KB for resumes
9. ✅ 20-45 internal files

**ACCEPTABLE (Common in Modern Docs):**
10. ✅ `customXml/` directory (97% prevalence)
11. ✅ `docMetadata/LabelInfo.xml` (100% in Microsoft 365)
12. ✅ `word/glossary/` directory (60% prevalence)
13. ✅ `word/media/` with PNG/SVG images

### 10.2 Red Flags (Require Investigation)

**CRITICAL ALERTS:**
- ❌ `word/vbaProject.bin` present (VBA macros)
- ❌ `embeddings/` directory (OLE objects)
- ❌ External HTTP/HTTPS in relationships (excluding schemas)
- ❌ `TargetMode="External"` with non-schema URLs
- ❌ File extension mismatch (`.docx` but contains macros)

**HIGH SEVERITY:**
- ⚠️ File size >500 KB (unusually large)
- ⚠️ >50 internal files (excessive complexity)
- ⚠️ Embedded fonts (`fonts/` directory)
- ⚠️ Missing `[Content_Types].xml`
- ⚠️ Corrupted ZIP structure
- ⚠️ Creation date in future or >10 years old
- ⚠️ TotalTime >100 hours (suspicious editing duration)

**MEDIUM SEVERITY:**
- ⚠️ Blank creation/modified timestamps
- ⚠️ Revision number >10 (excessive iterations)
- ⚠️ DocSecurity >0 (password protection)
- ⚠️ Large embedded images (>100 KB each)

### 10.3 Metadata Authenticity Checks

**Generated Document Requirements:**
```python
{
    "core_properties": {
        "author": "John Doe",                    # MUST be set (not blank)
        "title": "John Doe Resume",              # MUST be set
        "subject": "Professional Resume",        # SHOULD be set
        "created": "2025-10-09T14:30:00Z",      # MUST be realistic (not default)
        "modified": "2025-10-09T14:35:00Z",     # After created, within 24 hours
        "revision": 1                            # 1-3 acceptable for new docs
    },
    "app_properties": {
        "Application": "Microsoft Office Word",  # Standard
        "TotalTime": 30-300,                    # 0.5 - 5 hours editing time
        "AppVersion": "16.0000",                # Office 2016+
        "DocSecurity": 0,                       # No protection
        "Pages": 1-3,                           # Typical resume length
        "Words": 200-800                        # Realistic content
    }
}
```

### 10.4 Whitelist: Safe CustomXml Schemas

**Do NOT flag these as malicious:**
```
http://schemas.microsoft.com/office/2006/metadata/properties
http://schemas.microsoft.com/sharepoint/v3
http://schemas.microsoft.com/office/infopath/2007/PartnerControls
```

---

## 11. Implementation Priorities for Verification System

### Phase 1: Structure Validation (Highest Priority)
1. ZIP integrity check (CRC, magic number)
2. Required OOXML files presence
3. XML well-formedness validation
4. Internal file count sanity check (20-50 acceptable)

### Phase 2: Macro Detection (Critical Security)
1. Check for `word/vbaProject.bin`
2. Validate file extension (`.docx` not `.docm`)
3. Scan `[Content_Types].xml` for macro content types

### Phase 3: Embedded Content Scanning
1. Detect OLE objects (`embeddings/` directory)
2. Scan relationships for external URLs
3. Validate image files (size, format, embedded scripts in SVG)
4. Check for embedded fonts (rare, potentially suspicious)

### Phase 4: Metadata Validation
1. Verify creation/modification timestamps are set and realistic
2. Check author, title, subject are populated (not blank)
3. Validate editing time (0.5-10 hours acceptable)
4. Ensure revision number is reasonable (1-5)

### Phase 5: Content Analysis
1. Scan for unreplaced template variables (`<<var>>`, `{var}`)
2. Check document statistics (word count, page count)
3. Validate no suspicious strings or patterns

---

## 12. Test Data Recommendations

**For testing verification system, use:**

1. **Clean Baseline:** Microsoft official templates (analyzed here)
2. **Generated Documents:** Output from our document generation system
3. **Malicious Samples:**
   - Documents with VBA macros (`vbaProject.bin`)
   - Remote template injection samples
   - OLE object embeddings
   - Corrupted ZIP structures
   - Documents with external HTTP references

**Sources for Malicious Samples:**
- [Malware Bazaar](https://bazaar.abuse.ch/) - Real malware samples
- [VirusTotal](https://www.virustotal.com/) - Community malware database
- Generate synthetic malicious documents for controlled testing

---

## 13. Key Takeaways

### What Makes a Document Look Authentic?

1. **Minimal but Complete Metadata:**
   - Creation/modification timestamps present and realistic
   - Author, title, subject populated
   - Revision count 1-5
   - Editing time 0.5-10 hours

2. **Standard OOXML Structure:**
   - 20-45 internal files
   - All required XML files present
   - Valid ZIP compression

3. **No Executable Content:**
   - Zero VBA macros
   - No OLE objects
   - No external references (except schemas)

4. **Modern Microsoft 365 Features:**
   - CustomXml for SharePoint integration (97% prevalence)
   - Sensitivity labels (100% in M365 docs)
   - Glossary/building blocks (60% prevalence)

5. **Professional Statistics:**
   - File size: 20-160 KB
   - Word count: 200-800 words
   - Page count: 1-3 pages
   - Application: "Microsoft Office Word"
   - App version: 16.0000 (Office 2016+)

### What Should Trigger Alerts?

1. **VBA macros** (critical)
2. **OLE objects** (high risk)
3. **External HTTP/HTTPS URLs** in relationships (high risk)
4. **Blank metadata** (author, title, timestamps)
5. **Unrealistic editing time** (>100 hours)
6. **Large file size** (>500 KB for simple resume)
7. **Corrupted structure** (invalid ZIP, missing required files)

---

**End of Report**

This analysis provides a comprehensive baseline for implementing the DOCX Security Verification System with high accuracy and minimal false positives.
