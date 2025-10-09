# Product Requirements Document: Resume & Cover Letter Template Library Expansion

**Version**: 1.0
**Date**: October 9, 2025
**Status**: Draft
**Project Lead**: Template Creation Initiative
**Branch**: `task/04-template-creation`

---

## Executive Summary

This PRD outlines the expansion of the job application system's template library from a single Harvard MCS resume template to a comprehensive collection of 5 professional resume templates and 5 cover letter templates based on enterprise-grade standards from Microsoft, Google, and LinkedIn best practices for 2025.

### Objectives
- Create production-ready, ATS-optimized resume and cover letter templates
- Base designs on verified enterprise standards (Microsoft Create, Google XYZ method, LinkedIn best practices)
- Integrate templates with existing CSV mapping and document generation infrastructure
- Support diverse job application scenarios (corporate, tech, creative, career change)
- Maintain 95%+ ATS compatibility across all templates
- Enable intelligent template selection based on job type and industry

---

## Research Foundation

### Enterprise Template Sources (Verified)

#### **1. Microsoft Create (Official)**
**Source**: https://create.microsoft.com/en-us/templates/resumes
**Source**: https://create.microsoft.com/en-us/templates/ats-resumes

**Verified Template Categories:**
- **Simple/Professional**: Clean Elegant Resume (Blue), Simple Resume, Classic Management Resume
- **ATS-Optimized**: ATS Simple Classic Resume, ATS Bold Classic Resume, ATS Office Manager Resume
- **Industry-Specific**: Modern Web Developer Resume, Modern Accounting Resume, Social Media Marketing Resume
- **Creative**: Color Block Resume (Blue), Geometric Resume, Stylish Teaching Resume (Red)

**Key Design Standards:**
- Standard fonts (Arial, Calibri, Times New Roman)
- Clear section headings for ATS compatibility
- Single and multi-column layouts
- Professional color schemes (primarily blue, green, black accents)
- Customizable in Microsoft Word
- PDF export capability

#### **2. Google Resume Standards (Official)**
**Source**: Google Careers Official Guidance

**Google's XYZ Method:**
> "Accomplished [X] as measured by [Y], by doing [Z]"

**Official Recommendations:**
- **Format**: Reverse chronological preferred
- **Length**: Concise, ideally one page ("concision and precision are key")
- **Design**: "Simple and consistent design, font, spacing and sizing throughout"
- **Content**: Quantified achievements using metrics
- **Structure**: Focus on impact and measurable results

**Critical Insight**: Google receives 2M+ applications/year; ATS optimization is essential

#### **3. LinkedIn Best Practices (Official)**
**Source**: LinkedIn Business Blog, LinkedIn Profile Best Practices

**2025 Resume Integration Standards:**
- **LinkedIn URL Placement**: Header section alongside contact info
- **Success Metric**: 69.4% of candidates who landed interviews included LinkedIn URL (Q2 2025 data)
- **Profile Alignment**: Resume work history must mirror LinkedIn profile (mismatches are red flags)
- **Skills Optimization**: List skills at top of resume for quick recruiter scanning
- **Photo Impact**: Profiles with photos get 14x more views
- **Visibility**: Fully completed profiles get 40x more opportunities

**Content Strategy**: 2-5 posts per week for optimal visibility

---

## Template Requirements

### Design Principles (All Templates)

#### **ATS Compatibility Requirements**
- Standard fonts: Arial, Calibri, Georgia, Times New Roman (10-12pt)
- Clear section headings: Summary, Experience, Education, Skills, Certifications
- No headers/footers with critical information
- No text boxes, graphics, or images
- No tables (unless simple two-column layouts tested for ATS)
- No columns that confuse parsing order
- Bullet points using standard characters (•, -, *)
- Standard file format: .docx (Word 2007+)

#### **Variable Placeholder System**
**User Profile Variables:**
```
<<user_first_name>>
<<user_last_name>>
<<user_email>>
<<user_phone>>
<<user_city_prov>>
<<user_linkedin>>
```

**Education Variables (up to 2 entries):**
```
<<edu_1_name>>
<<edu_1_degree>>
<<edu_1_concentration>>
<<edu_1_specialization>>
<<edu_1_location>>
<<edu_1_grad_date>>
```

**Work Experience Variables (up to 2 entries, 6 skills each):**
```
<<work_experience_1_name>>
<<work_experience_1_position>>
<<work_experience_1_location>>
<<work_experience_1_dates>>
<<work_experience_1_skill1>> through <<work_experience_1_skill6>>
<<work_experience_2_name>> [same pattern]
```

**Skills Summary Variables:**
```
<<technical_summary>>
<<methodology_summary>>
<<domain_summary>>
```

**Volunteer/Leadership Variables (up to 2 entries):**
```
<<volunteer_1_name>>
<<volunteer_1_position>>
<<volunteer_1_location>>
<<volunteer_1_dates>>
<<volunteer_1_description>>
```

**Job-Specific Variables:**
```
{job_title}
{company_name}
```

#### **Canadian Standards**
- Canadian English spelling (handled automatically by system)
- Province abbreviations (AB, BC, ON, etc.)
- Date format: Month YYYY or YYYY-MM-DD
- Phone format: XXX-XXX-XXXX

---

## Template Specifications

### Resume Templates (5 Templates)

#### **Template 1: ATS-Optimized Professional Resume**
**Based on**: Microsoft ATS Simple Classic Resume
**Target Industries**: Corporate, Finance, Healthcare, Government
**File Name**: `ats_professional_resume.docx`

**Design Specifications:**
- **Layout**: Single column, left-aligned
- **Font**: Arial 11pt (body), 14pt (name), 12pt (section headings)
- **Colors**: Black text, navy blue (#003366) for name and section headings
- **Spacing**: 1.15 line spacing, 6pt after paragraphs
- **Margins**: 0.75" all sides
- **Sections (in order)**:
  1. Header: Name (14pt bold), Contact Info (11pt) with LinkedIn
  2. Professional Summary (3-4 lines)
  3. Core Competencies/Skills (bullet list, 2-column)
  4. Professional Experience (reverse chronological)
  5. Education
  6. Certifications
  7. Technical Skills (optional)

**ATS Compatibility**: 100% (no graphics, no tables, standard formatting)
**Best For**: Large corporations with ATS systems, conservative industries
**Length**: Strictly one page

---

#### **Template 2: Modern Professional Resume**
**Based on**: Microsoft Clean Elegant Resume (Blue)
**Target Industries**: Technology, Digital Marketing, Modern Corporations
**File Name**: `modern_professional_resume.docx`

**Design Specifications:**
- **Layout**: Two-column (70% main, 30% sidebar)
- **Font**: Calibri 11pt (body), 16pt (name), 12pt (section headings)
- **Colors**:
  - Primary: #0078D4 (Microsoft blue)
  - Accent: #50E6FF (light blue)
  - Text: #323130 (dark gray)
- **Spacing**: 1.15 line spacing, subtle section dividers
- **Margins**: 0.5" all sides

**Layout Structure:**
- **Left Sidebar (30%)**:
  - Contact Information (with icons if ATS-compatible)
  - Skills (categorized: Technical, Methodologies, Domains)
  - Certifications
  - Languages (if applicable)

- **Main Column (70%)**:
  1. Name & Professional Title
  2. Professional Summary
  3. Professional Experience (Google XYZ format)
  4. Education
  5. Volunteer/Leadership

**ATS Compatibility**: 90% (simple two-column tested for major ATS)
**Best For**: Tech companies, startups, modern corporate environments
**Length**: One page (strict)

---

#### **Template 3: Executive/Leadership Resume**
**Based on**: Microsoft Classic Management Resume
**Target Industries**: Senior Management, Executive Roles, C-Suite
**File Name**: `executive_leadership_resume.docx`

**Design Specifications:**
- **Layout**: Single column with elegant formatting
- **Font**: Georgia 11pt (body), 18pt (name), 13pt (section headings)
- **Colors**: Black text, dark blue (#1F4788) accents
- **Spacing**: 1.2 line spacing, 8pt after paragraphs
- **Margins**: 1" all sides

**Sections (in order)**:
1. Header: Name (18pt), Title/Tagline (12pt italic), Contact (11pt)
2. Executive Summary (5-6 lines highlighting leadership achievements)
3. Core Leadership Competencies (2-column bullet grid)
4. Professional Experience
   - Company name, title, dates
   - 2-3 sentence context paragraph
   - 4-6 achievement bullets (Google XYZ format with metrics)
5. Education (with honors/distinctions)
6. Board Memberships/Advisory Roles (if applicable)
7. Professional Certifications
8. Awards & Recognition (optional)

**ATS Compatibility**: 95% (minimal formatting, standard structure)
**Best For**: Senior management, director+ roles, executive positions
**Length**: 1-2 pages (context-dependent)

---

#### **Template 4: Tech/Creative Modern Resume**
**Based on**: Microsoft Modern Web Developer Resume + Color Block Resume
**Target Industries**: Tech, Creative Agencies, Digital Media, UX/UI
**File Name**: `tech_creative_resume.docx`

**Design Specifications:**
- **Layout**: Asymmetric two-column with color block header
- **Font**: Calibri Light 11pt (body), Calibri Bold 20pt (name), 13pt (headings)
- **Colors**:
  - Primary: #00B294 (teal)
  - Secondary: #FFB900 (amber accent)
  - Text: #252423 (near black)
- **Spacing**: 1.0 line spacing, clean modern aesthetic
- **Margins**: 0.5" all sides with color block header

**Layout Structure:**
- **Header Section (full width, color block background)**:
  - Name (20pt white text)
  - Title/Specialty (12pt white text)
  - Contact info (white icons + text)

- **Left Column (35%)**:
  - Skills & Technologies (icon bullets)
  - Tools & Platforms
  - Certifications
  - Portfolio Link (prominent)
  - GitHub/LinkedIn

- **Right Column (65%)**:
  - Professional Summary (brief, 2-3 lines)
  - Selected Projects/Work Experience
    - Project-focused with tech stack
    - Impact metrics highlighted
  - Education
  - Awards/Hackathons (if applicable)

**ATS Compatibility**: 75% (color block may cause issues; include text-only version)
**Best For**: Software developers, UX/UI designers, digital creatives, portfolio-driven roles
**Length**: One page (strict)
**Note**: Should be paired with ATS-optimized version for large company applications

---

#### **Template 5: Skills-Based/Career Change Resume**
**Based on**: Microsoft Simple Resume + LinkedIn Skills-First Guidance
**Target Industries**: Career changers, skills-focused roles, consulting
**File Name**: `skills_based_resume.docx`

**Design Specifications:**
- **Layout**: Single column, skills-prominent structure
- **Font**: Arial 11pt (body), 15pt (name), 12pt (section headings)
- **Colors**: Black text, dark green (#0E6B41) section dividers
- **Spacing**: 1.15 line spacing
- **Margins**: 0.75" all sides

**Sections (in order)**:
1. Header: Name, Contact (with LinkedIn prominent)
2. Professional Summary (tailored to target role)
3. **Core Competencies & Skills Matrix** (featured section)
   - Category 1: Technical Skills (with proficiency levels)
   - Category 2: Methodologies & Frameworks
   - Category 3: Domain Expertise
   - Category 4: Soft Skills/Leadership
4. **Professional Achievements** (skills-grouped, not chronological)
   - Leadership & Strategy
   - Technical Implementation
   - Business Development
   - (each with 2-3 achievement bullets using XYZ format)
5. **Professional Experience** (condensed chronological)
   - Company, title, dates
   - 1-2 bullet points max per role
6. Education
7. Certifications & Training

**ATS Compatibility**: 90% (standard formatting, clear structure)
**Best For**: Career changers, diverse backgrounds, consulting, contract work
**Length**: One page

---

### Cover Letter Templates (5 Templates)

#### **Template 1: Professional/Formal Cover Letter**
**Based on**: Microsoft Professional Cover Letter Standards
**Target**: Corporate, Finance, Legal, Government
**File Name**: `professional_cover_letter.docx`

**Design Specifications:**
- **Layout**: Single column, traditional business letter
- **Font**: Georgia 11pt (body), 12pt (name)
- **Colors**: Black text only
- **Spacing**: 1.15 line spacing, 12pt between sections
- **Margins**: 1" all sides

**Structure:**
```
[Date]

[Hiring Manager Name]
[Title]
[Company Name]
[Address]
[City, Province Postal Code]

Dear [Hiring Manager Name/Hiring Manager],

[Opening Paragraph - 3-4 sentences]
- Express interest in {job_title} at {company_name}
- Brief statement of qualifications
- How you learned about position

[Body Paragraph 1 - Skills Alignment]
- Variable: <<cover_letter_skill_alignment>>
- 4-5 sentences matching your skills to job requirements
- Reference specific company initiatives/values

[Body Paragraph 2 - Achievement/Impact]
- Variable: <<cover_letter_achievement_1>>
- Quantified achievement relevant to role
- Demonstrates value you bring

[Body Paragraph 3 - Cultural Fit/Enthusiasm (optional)]
- Variable: <<cover_letter_culture_fit>>
- Why this company specifically
- Alignment with company mission

[Closing Paragraph]
- Variable: <<cover_letter_closing>>
- Call to action
- Availability for interview
- Thank you

Sincerely,

<<user_first_name>> <<user_last_name>>
<<user_email>>
<<user_phone>>
```

**Variable Constraints**: Max 1 `{job_title}`, Max 1 `{company_name}`
**Length**: 300-400 words (fits on one page)
**Tone**: Confident, analytical, professional

---

#### **Template 2: Modern/Conversational Cover Letter**
**Based on**: LinkedIn Modern Application Standards + Microsoft Simple Cover Letter
**Target**: Tech, Startups, Creative Agencies, Modern Corporations
**File Name**: `modern_cover_letter.docx`

**Design Specifications:**
- **Layout**: Single column, simplified header
- **Font**: Calibri 11pt (body), 14pt (name)
- **Colors**: Dark gray text (#323130), blue accent (#0078D4) for name
- **Spacing**: 1.2 line spacing, relaxed formatting
- **Margins**: 0.75" all sides

**Structure:**
```
<<user_first_name>> <<user_last_name>>
<<user_email>> | <<user_phone>> | <<user_linkedin>>
[Date]

[Hiring Manager Name] or Hiring Team
{company_name}

Hi [Name]/Hello,

[Hook Opening - 2 sentences]
- Variable: <<cover_letter_hook>>
- Engaging opening showing company research
- Clear statement of interest in {job_title}

[Value Proposition - 3-4 sentences]
- Variable: <<cover_letter_value_prop>>
- What you bring to the role
- Relevant skills and experience summary

[Specific Achievement - 3-4 sentences]
- Variable: <<cover_letter_achievement_1>>
- Story-based achievement with metrics
- Demonstrates relevant capability

[Why This Company - 2-3 sentences]
- Variable: <<cover_letter_company_interest>>
- Genuine interest in company mission/product
- How you align with company values

[Closing - 2 sentences]
- Variable: <<cover_letter_closing>>
- Enthusiasm for next steps
- Appreciation

Best regards,
<<user_first_name>> <<user_last_name>>
```

**Variable Constraints**: Max 1 `{job_title}`, Max 1 `{company_name}`
**Length**: 250-350 words
**Tone**: Warm, curious, confident

---

#### **Template 3: T-Format Skills-Match Cover Letter**
**Based on**: Hybrid of Microsoft Professional + LinkedIn Skills-First Approach
**Target**: Roles with specific requirements, career change, skills-focused positions
**File Name**: `t_format_cover_letter.docx`

**Design Specifications:**
- **Layout**: Traditional with table insert for T-format
- **Font**: Arial 11pt (body), 12pt (name and headings)
- **Colors**: Black text, dark blue (#003366) table borders
- **Spacing**: 1.15 line spacing, 6pt table cell padding
- **Margins**: 0.75" all sides

**Structure:**
```
<<user_first_name>> <<user_last_name>>
<<user_email>> | <<user_phone>> | <<user_city_prov>>
LinkedIn: <<user_linkedin>>

[Date]

[Hiring Manager Name]
{company_name}

Dear [Hiring Manager Name],

[Introduction - 2-3 sentences]
- Express interest in {job_title}
- Brief credential statement
- Transition to skills match

[T-Format Table]
┌─────────────────────────────────┬─────────────────────────────────┐
│ Your Requirements               │ My Qualifications               │
├─────────────────────────────────┼─────────────────────────────────┤
│ <<job_requirement_1>>           │ <<matching_qualification_1>>    │
├─────────────────────────────────┼─────────────────────────────────┤
│ <<job_requirement_2>>           │ <<matching_qualification_2>>    │
├─────────────────────────────────┼─────────────────────────────────┤
│ <<job_requirement_3>>           │ <<matching_qualification_3>>    │
├─────────────────────────────────┼─────────────────────────────────┤
│ <<job_requirement_4>>           │ <<matching_qualification_4>>    │
└─────────────────────────────────┴─────────────────────────────────┘

[Summary Paragraph - 3-4 sentences]
- Variable: <<cover_letter_achievement_summary>>
- Synthesize your fit
- Quantified achievement example
- Value proposition

[Closing - 2 sentences]
I would welcome the opportunity to discuss how my background aligns
with {company_name}'s needs. Thank you for your consideration.

Sincerely,
<<user_first_name>> <<user_last_name>>
```

**Variable Constraints**: Max 2 `{job_title}`, Max 2 `{company_name}` (due to T-table)
**Special Variables**: Requires 4 job requirement/qualification pairs
**Length**: 300-350 words
**Tone**: Analytical, confident
**Note**: Table must be simple for ATS compatibility

---

#### **Template 4: Career Change/Transition Cover Letter**
**Based on**: Microsoft Career Transition Guidance + LinkedIn Alignment Best Practices
**Target**: Career changers, industry switchers, role transitions
**File Name**: `career_change_cover_letter.docx`

**Design Specifications:**
- **Layout**: Single column, emphasis on transferable skills
- **Font**: Calibri 11pt (body), 13pt (name)
- **Colors**: Black text, green accent (#0E6B41) for name
- **Spacing**: 1.2 line spacing
- **Margins**: 0.75" all sides

**Structure:**
```
<<user_first_name>> <<user_last_name>>
<<user_email>> | <<user_phone>> | <<user_linkedin>>

[Date]

[Hiring Manager Name]
{company_name}

Dear [Hiring Manager Name],

[Opening - Explain Transition - 3-4 sentences]
- Variable: <<cover_letter_transition_hook>>
- Why you're interested in {job_title}
- What sparked your interest in this industry/role
- Brief background context

[Transferable Skills - 4-5 sentences]
- Variable: <<cover_letter_transferable_skills>>
- Skills from previous career applicable to new role
- Bridge the gap between old and new
- Emphasize universal competencies

[Demonstrated Success - 4-5 sentences]
- Variable: <<cover_letter_achievement_1>>
- Achievement from previous role showing relevant capability
- Quantified results
- How this applies to target role

[Preparation & Commitment - 3-4 sentences]
- Variable: <<cover_letter_preparation>>
- Certifications, courses, self-study undertaken
- Demonstrated commitment to transition
- Relevant projects or volunteer work in new field

[Enthusiasm & Closing - 2-3 sentences]
I'm excited about bringing my <<previous_industry>> experience and
fresh perspective to {company_name}'s {job_title} role. I would
welcome the opportunity to discuss how my unique background can
contribute to your team's success.

Thank you for considering my application.

Best regards,
<<user_first_name>> <<user_last_name>>
```

**Variable Constraints**: Max 2 `{job_title}`, Max 1 `{company_name}`
**Special Variables**: `<<previous_industry>>`
**Length**: 350-450 words
**Tone**: Warm, curious, confident with alignment focus

---

#### **Template 5: Email Cover Letter (Brief)**
**Based on**: LinkedIn 2025 Digital Application Standards
**Target**: Startups, digital-first companies, quick applications, email submissions
**File Name**: `email_cover_letter.docx`

**Design Specifications:**
- **Layout**: Email-optimized (no formal letterhead)
- **Font**: Arial 11pt (web-safe)
- **Colors**: Black text only
- **Spacing**: 1.5 line spacing for readability
- **Margins**: Minimal (email body)

**Structure:**
```
Subject Line Template:
Application for {job_title} - <<user_first_name>> <<user_last_name>>

---

Hi [Hiring Manager Name/Team],

[Opening Sentence]
- Variable: <<cover_letter_email_hook>>
- Express interest in {job_title} at {company_name}

[Value Proposition - 2-3 sentences]
- Variable: <<cover_letter_value_prop_brief>>
- Core qualifications
- Key relevant experience

[Achievement Example - 2 sentences]
- Variable: <<cover_letter_achievement_brief>>
- One quantified achievement
- Directly relevant to role

[Call to Action - 1-2 sentences]
- Variable: <<cover_letter_cta>>
- Attached resume mention
- Availability for discussion

Best regards,

<<user_first_name>> <<user_last_name>>
<<user_email>> | <<user_phone>>
LinkedIn: <<user_linkedin>>
Portfolio: <<user_portfolio>> (if applicable)
```

**Variable Constraints**: Max 1 `{job_title}`, Max 1 `{company_name}`
**Length**: 150-250 words (strictly concise)
**Tone**: Direct, confident, friendly
**Format Note**: Optimized for mobile reading

---

## Technical Implementation

### CSV Mapping File Specifications

Each template requires a corresponding CSV mapping file following this structure:

**File Naming Convention:**
- `ats_professional_resume_mapping.csv`
- `modern_professional_resume_mapping.csv`
- etc.

**Required Columns:**
| Column | Type | Description | Example |
|--------|------|-------------|---------|
| `Original_Text` | String | Text in template to be transformed | "FirstName LastName" |
| `Is_Variable` | Boolean | Mark for variable substitution | TRUE |
| `Is_Static` | Boolean | Mark for static text replacement | FALSE |
| `Is_discarded` | Boolean | Mark for content removal | FALSE |
| `Variable_name` | String | Template variable identifier | "user_first_name user_last_name" |
| `Variable_intention` | String | Variable description/purpose | "Candidate's full name" |
| `Variable_category` | String | Category for organization | "User Profile" |
| `Static_Text` | String | Replacement text if static | "Professional Experience" |
| `Content_source` | String | Data source (user_profile, content_manager, job_data) | "user_profile" |

**Processing Rules:**
1. Variables processed first (Is_Variable = TRUE)
2. Static text replacements second (Is_Static = TRUE)
3. Content removal last (Is_discarded = TRUE)
4. Original formatting preserved throughout

### Variable Resolution Hierarchy

```python
# Priority order for variable resolution:
1. User Profile Database (personal, contact, education, certifications)
2. Content Manager Sentence Bank (work experience, skills, achievements)
3. Job Analysis Data (job-specific variables like {job_title}, {company_name})
4. Default Values (professional fallbacks from steve_glen_comprehensive_defaults.json)
5. Placeholder Text (if no data available: "[Not Provided]")
```

### Template Metadata JSON

Each template requires a metadata file:

**File Naming Convention:** `{template_name}_metadata.json`

**Required Fields:**
```json
{
  "template_name": "ATS Professional Resume",
  "template_file": "ats_professional_resume.docx",
  "template_type": "resume",
  "version": "1.0",
  "created_date": "2025-10-09",
  "last_modified": "2025-10-09",
  "description": "ATS-optimized professional resume for corporate environments",
  "target_industries": ["Corporate", "Finance", "Healthcare", "Government"],
  "ats_compatibility_score": 100,
  "design_style": "Professional",
  "layout_type": "Single Column",
  "color_scheme": "Navy Blue Accents",
  "recommended_length": "1 page",
  "variables_required": [
    "user_first_name",
    "user_last_name",
    "user_email",
    "user_phone",
    "user_city_prov",
    "user_linkedin"
  ],
  "variables_optional": [
    "volunteer_1_name",
    "certifications"
  ],
  "csv_mapping_file": "ats_professional_resume_mapping.csv",
  "test_data_file": "steve_glen_resume_test.json",
  "use_cases": [
    "Large corporations with ATS systems",
    "Conservative industries (finance, legal, healthcare)",
    "Government positions",
    "Traditional corporate environments"
  ],
  "notes": "Strictly ATS-compliant with no graphics, tables, or complex formatting"
}
```

---

## Integration Points

### Document Generator Integration

**Update Required in**: `/workspace/modules/content/document_generation/document_generator.py`

**Method**: `get_template_path(document_type, template_name=None, job_data=None)`

**New Logic:**
```python
def get_template_path(self, document_type, template_name=None, job_data=None):
    """
    Determine template path with intelligent selection

    Args:
        document_type: 'resume' or 'coverletter'
        template_name: Specific template name (optional)
        job_data: Job information for intelligent template selection (optional)

    Returns:
        str: Path to selected template
    """

    if template_name:
        # Use explicitly requested template
        return self._get_specific_template(document_type, template_name)

    if job_data:
        # Intelligent template selection based on job analysis
        return self._select_template_by_job(document_type, job_data)

    # Default to ATS-optimized template
    if document_type == 'resume':
        return 'content_template_library/resumes/ats_professional_resume.docx'
    elif document_type == 'coverletter':
        return 'content_template_library/coverletters/professional_cover_letter.docx'
```

**New Method**: `_select_template_by_job(document_type, job_data)`

**Selection Logic:**
```python
def _select_template_by_job(self, document_type, job_data):
    """
    Intelligently select template based on job characteristics

    Selection Criteria:
    - Industry/company type
    - Job level (entry, mid, senior, executive)
    - Company size (startup, mid-size, enterprise)
    - Role type (technical, creative, traditional)
    """

    industry = job_data.get('industry', '').lower()
    company_size = job_data.get('company_size', 'unknown')
    job_level = job_data.get('level', 'mid')
    job_title = job_data.get('job_title', '').lower()

    # Executive level
    if job_level in ['senior', 'executive', 'director', 'vp', 'c-level']:
        return 'content_template_library/resumes/executive_leadership_resume.docx'

    # Tech/Creative roles
    if any(keyword in job_title for keyword in ['developer', 'engineer', 'designer', 'creative', 'ux', 'ui']):
        if company_size in ['startup', 'small']:
            return 'content_template_library/resumes/tech_creative_resume.docx'
        else:
            return 'content_template_library/resumes/modern_professional_resume.docx'

    # Career change indicators
    if job_data.get('career_change', False):
        return 'content_template_library/resumes/skills_based_resume.docx'

    # Modern tech companies
    if industry in ['technology', 'software', 'saas', 'digital'] and company_size != 'enterprise':
        return 'content_template_library/resumes/modern_professional_resume.docx'

    # Default to ATS-optimized for large companies and traditional industries
    return 'content_template_library/resumes/ats_professional_resume.docx'
```

### Content Manager Integration

**Update Required in**: `/workspace/modules/content/content_manager.py`

**New Method**: `select_cover_letter_content_by_template(job_data, template_type)`

**Purpose**: Select sentence bank content appropriate for cover letter template type

```python
def select_cover_letter_content_by_template(self, job_data, template_type):
    """
    Select cover letter content tailored to specific template

    Template Types:
    - 'professional': Formal, analytical tone
    - 'modern': Warm, conversational tone
    - 't_format': Skills-focused, structured
    - 'career_change': Transition-focused, alignment emphasis
    - 'email': Brief, direct, scannable
    """

    # Get base content selection
    base_content = self.select_content_for_job(job_data)

    # Filter and adapt based on template requirements
    if template_type == 'professional':
        # Select confident, analytical tone sentences
        tone_filter = ['Confident', 'Analytical']
    elif template_type == 'modern':
        # Select warm, curious tone sentences
        tone_filter = ['Warm', 'Curious', 'Confident']
    elif template_type == 'career_change':
        # Focus on alignment and transferable skills
        category_filter = ['Alignment', 'Skills']
    elif template_type == 'email':
        # Select concise, high-impact sentences
        length_filter = ['Short', 'Medium']

    # Apply filters and return adapted content
    return self._filter_content_by_template(base_content, template_type)
```

### Database Schema Updates

**No new tables required**. Existing schema supports template library:

**Existing Tables Used:**
- `sentence_bank_resume`: Work experience skill descriptions
- `sentence_bank_cover_letter`: Cover letter paragraph content
- `user_profiles`: Personal information, contact details
- `user_education`: Educational background
- `user_work_experience`: Professional history
- `user_certifications`: Credentials and training
- `user_skills`: Technical, methodological, domain skills
- `jobs`: Job postings and analysis data
- `job_skills`: AI-analyzed job requirements
- `job_ats_keywords`: ATS optimization keywords

**Optional Enhancement**: Add `template_usage_tracking` table for analytics

```sql
CREATE TABLE template_usage_tracking (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    template_name VARCHAR(255) NOT NULL,
    template_type VARCHAR(50) NOT NULL,  -- 'resume' or 'coverletter'
    job_id UUID REFERENCES jobs(id),
    application_id UUID REFERENCES job_applications(id),
    generation_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    generation_success BOOLEAN DEFAULT TRUE,
    variables_resolved INTEGER,
    variables_missing INTEGER,
    file_size_bytes INTEGER,
    generation_time_ms INTEGER
);
```

---

## Quality Assurance Standards

### Template Validation Checklist

**Pre-Production Validation (Per Template):**
- [ ] All variable placeholders use correct syntax (`<<variable_name>>` or `{job_var}`)
- [ ] CSV mapping file complete with all variables documented
- [ ] Metadata JSON file created and validated
- [ ] ATS compatibility tested with jobscan.co or similar tool
- [ ] Template generates successfully with Steve Glen test data
- [ ] All variables resolve (no missing data errors)
- [ ] Original formatting preserved after generation
- [ ] PDF export works correctly
- [ ] File size < 200KB (for email compatibility)
- [ ] Professional appearance validated by human review
- [ ] Canadian English spelling verified
- [ ] Publication italics formatting works (if applicable)
- [ ] LinkedIn URL formatting correct
- [ ] Phone number formatting consistent (XXX-XXX-XXXX)

### ATS Compatibility Testing

**Testing Tools:**
- Jobscan.co ATS Resume Checker
- Resume Worded ATS Scan
- TopResume ATS Analysis

**Target Scores:**
- ATS Professional Resume: 95-100%
- Modern Professional Resume: 85-95%
- Executive Leadership Resume: 90-100%
- Tech/Creative Resume: 70-85% (acceptable with text-only backup)
- Skills-Based Resume: 85-95%

**Critical ATS Factors:**
- Standard fonts (Arial, Calibri, Georgia, Times New Roman)
- No headers/footers with critical content
- Clear section headings
- No text boxes or embedded graphics
- Simple table structures (if any)
- Standard bullet points
- Proper heading hierarchy

### Content Quality Standards

**Resume Bullet Points:**
- 100% start with action verbs (accomplished, managed, developed, led, etc.)
- 80%+ include quantified metrics or results
- Average length: 100-120 characters
- Google XYZ format: "Accomplished [X] as measured by [Y], by doing [Z]"
- No personal pronouns (I, me, my)
- Professional, industry-appropriate terminology

**Cover Letter Content:**
- Tone consistency score: >80% (via ToneAnalyzer)
- Average tone jump: <0.3 (smooth transitions)
- Length within specified range (by template)
- Variable constraints respected (max 1-2 job_title/company_name uses)
- Professional language, no typos
- Clear value proposition in opening paragraph
- Quantified achievements included
- Call to action in closing

### Performance Standards

**Generation Speed:**
- Target: <2 seconds per document (resume or cover letter)
- Maximum acceptable: <5 seconds per document
- Batch generation (10 documents): <30 seconds

**Success Rate:**
- Template loading: 100%
- Variable resolution: >95% (with intelligent fallbacks)
- CSV mapping application: 100%
- Document generation: >99%
- PDF export: >99%

---

## Project Timeline

### Phase 1: Template Creation (Week 1)
**Days 1-3: Resume Templates**
- Day 1: Create ATS Professional Resume + CSV mapping
- Day 2: Create Modern Professional Resume + Executive Leadership Resume + CSV mappings
- Day 3: Create Tech/Creative Resume + Skills-Based Resume + CSV mappings

**Days 4-5: Cover Letter Templates**
- Day 4: Create Professional Cover Letter + Modern Cover Letter + T-Format Cover Letter + CSV mappings
- Day 5: Create Career Change Cover Letter + Email Cover Letter + CSV mappings

**Day 6: Metadata & Documentation**
- Create metadata JSON for all 10 templates
- Document variable requirements
- Create template selection guide

**Day 7: Quality Review**
- Visual design review
- Variable placeholder verification
- CSV mapping validation

### Phase 2: Integration & Testing (Week 2)
**Days 8-10: Code Integration**
- Update DocumentGenerator.get_template_path()
- Implement _select_template_by_job()
- Update ContentManager for template-specific content selection
- Create template usage tracking (optional)

**Days 11-12: Testing**
- Generate all templates with Steve Glen test data
- ATS compatibility testing
- Variable resolution testing
- Edge case handling (missing data)
- Performance benchmarking

**Day 13: Bug Fixes & Refinement**
- Address any issues found in testing
- Optimize variable resolution
- Improve template selection logic

**Day 14: Final Validation**
- End-to-end workflow testing
- Documentation review
- Code review
- Prepare for production deployment

### Phase 3: Documentation & Deployment (Week 3)
**Days 15-16: Documentation**
- Update CLAUDE.md with template library information
- Update template_library_system.md
- Create user guide for template selection
- Document CSV mapping specifications

**Days 17-18: Production Preparation**
- Final testing in production-like environment
- Create backup of existing templates
- Prepare rollback plan
- Staging deployment

**Day 19: Production Deployment**
- Deploy templates to production
- Update database (if template_usage_tracking added)
- Monitor initial usage
- Address any immediate issues

**Day 20-21: Monitoring & Optimization**
- Monitor template usage patterns
- Collect user feedback
- Performance monitoring
- Initial optimization based on real-world usage

---

## Success Metrics

### Quantitative Metrics

**Template Coverage:**
- Target: 90% of job applications matched to appropriate template
- Measurement: Template usage tracking analytics

**ATS Pass Rate:**
- Target: 95% of generated resumes pass ATS compatibility check
- Measurement: ATS testing tool scores (jobscan.co, etc.)

**Variable Resolution:**
- Target: 98% of variables resolve successfully
- Measurement: Generation logs, missing variable tracking

**Generation Performance:**
- Target: <2 seconds average document generation time
- Measurement: Performance monitoring logs

**Success Rate:**
- Target: 99% successful document generation (no errors)
- Measurement: Error logs, exception tracking

### Qualitative Metrics

**Professional Quality:**
- Assessment: Human review of generated documents
- Standard: "Ready to submit without manual editing"
- Frequency: Weekly review of 10 random samples

**User Satisfaction:**
- Assessment: Quality of output, minimal manual editing required
- Target: Positive feedback, low revision requests

**Template Appropriateness:**
- Assessment: Intelligent template selection accuracy
- Standard: Template matches job type/industry >85% of time

### Business Metrics

**Application Success Rate:**
- Track: Interview requests for applications using new templates vs. old template
- Target: No decrease (maintain or improve current rates)

**Time Savings:**
- Track: Average time from job discovery to application submission
- Target: Reduce by 30% with template variety and intelligent selection

---

## Risk Assessment & Mitigation

### Technical Risks

**Risk 1: ATS Compatibility Issues**
- **Impact**: High - Resumes rejected by ATS systems
- **Probability**: Medium
- **Mitigation**:
  - Extensive ATS testing with multiple tools
  - Conservative design choices for primary templates
  - Fallback to text-only ATS-optimized template for uncertain situations
  - Regular testing with major ATS platforms (Taleo, Workday, Greenhouse)

**Risk 2: Variable Resolution Failures**
- **Impact**: Medium - Missing data in generated documents
- **Probability**: Low-Medium
- **Mitigation**:
  - Comprehensive default values from steve_glen_comprehensive_defaults.json
  - Intelligent fallback hierarchy
  - Clear placeholder text for missing data ("[Not Provided]")
  - Pre-generation validation checks

**Risk 3: Performance Degradation**
- **Impact**: Medium - Slow document generation
- **Probability**: Low
- **Mitigation**:
  - Template caching (already implemented)
  - Performance benchmarking during testing
  - Optimize CSV mapping processing
  - Monitor performance in production

### Content Quality Risks

**Risk 4: Template-Job Mismatch**
- **Impact**: Medium - Wrong template selected for job type
- **Probability**: Medium
- **Mitigation**:
  - Conservative default (ATS-optimized template)
  - Allow manual template override
  - Refine selection algorithm based on usage data
  - Clear template selection guidance documentation

**Risk 5: Formatting Inconsistencies**
- **Impact**: Low-Medium - Visual quality issues
- **Probability**: Low
- **Mitigation**:
  - Extensive testing with Steve Glen data
  - Visual QA review of all templates
  - Consistent design standards across templates
  - Regular visual spot-checks of generated documents

### Operational Risks

**Risk 6: Increased Maintenance Burden**
- **Impact**: Medium - More templates to maintain
- **Probability**: Medium
- **Mitigation**:
  - Clear documentation for each template
  - Standardized variable system across all templates
  - Automated testing for template generation
  - Version control for template changes

---

## Dependencies

### External Dependencies
- Microsoft Word .docx format compatibility (python-docx library)
- Existing TemplateEngine class
- Existing CSVContentMapper class
- Existing DocumentGenerator class
- Existing ContentManager class
- PostgreSQL database with current schema
- Storage backend (local filesystem or cloud)

### Data Dependencies
- User profile data (personal, contact, education, certifications)
- Sentence bank content (resume bullets, cover letter paragraphs)
- Job analysis data (skills, keywords, ATS requirements)
- Default values (steve_glen_comprehensive_defaults.json)

### System Dependencies
- Python 3.11+
- python-docx library
- Flask application framework
- SQLAlchemy ORM
- Existing module structure (/workspace/modules/content/)

---

## Future Enhancements

### Short-term (3-6 months)
1. **Industry-Specific Templates**: Healthcare, Legal, Finance specialized templates
2. **Multi-Language Support**: French-Canadian templates for bilingual applications
3. **AI Content Enhancement**: LLM-powered bullet point optimization
4. **Real-Time Preview**: Web-based document preview before generation

### Medium-term (6-12 months)
1. **Template Analytics Dashboard**: Usage patterns, success rates by template
2. **A/B Testing Framework**: Test template effectiveness for different job types
3. **Custom Template Builder**: User-defined template creation tool
4. **Mobile-Optimized Templates**: Templates designed for mobile job applications

### Long-term (12+ months)
1. **Video Resume Templates**: Integration with video cover letter system
2. **Portfolio Integration**: Templates with portfolio/work sample sections
3. **International Templates**: UK, US, Australian resume format variations
4. **Collaborative Features**: Multi-user template sharing and feedback

---

## Appendix A: Variable Reference Guide

### User Profile Variables
| Variable | Source | Example | Required |
|----------|--------|---------|----------|
| `<<user_first_name>>` | user_profiles.first_name | "Steve" | Yes |
| `<<user_last_name>>` | user_profiles.last_name | "Glen" | Yes |
| `<<user_email>>` | user_profiles.email | "therealstevenglen@gmail.com" | Yes |
| `<<user_phone>>` | user_profiles.phone | "780-884-7038" | Yes |
| `<<user_city_prov>>` | user_profiles.city + province | "Edmonton, AB" | Yes |
| `<<user_linkedin>>` | user_profiles.linkedin_url | "linkedin.com/in/steve-glen" | Recommended |
| `<<user_portfolio>>` | user_profiles.portfolio_url | "steveglen.com" | Optional |

### Education Variables (per entry, up to 2)
| Variable | Source | Example | Required |
|----------|--------|---------|----------|
| `<<edu_1_name>>` | user_education.institution | "University of Alberta" | Yes |
| `<<edu_1_degree>>` | user_education.degree_type | "Bachelor of Commerce" | Yes |
| `<<edu_1_concentration>>` | user_education.field_of_study | "Strategic Management" | Optional |
| `<<edu_1_specialization>>` | user_education.specialization | "Entrepreneurship, Marketing" | Optional |
| `<<edu_1_location>>` | user_education.city + province | "Edmonton, AB" | Optional |
| `<<edu_1_grad_date>>` | user_education.graduation_year | "2018" | Yes |

### Work Experience Variables (per entry, up to 2)
| Variable | Source | Example | Required |
|----------|--------|---------|----------|
| `<<work_experience_1_name>>` | user_work_experience.company | "Odvod Media" | Yes |
| `<<work_experience_1_position>>` | user_work_experience.position | "Digital Strategist" | Yes |
| `<<work_experience_1_location>>` | user_work_experience.city + province | "Edmonton, AB" | Optional |
| `<<work_experience_1_dates>>` | user_work_experience.start + end | "2020 - Present" | Yes |
| `<<work_experience_1_skill1>>` | sentence_bank_resume (selected) | "Led transformation of digital channels..." | Yes |
| `<<work_experience_1_skill2-6>>` | sentence_bank_resume (selected) | [Additional achievement bullets] | Optional |

### Skills Variables
| Variable | Source | Example | Required |
|----------|--------|---------|----------|
| `<<technical_summary>>` | user_skills (category: technical) | "Microsoft Office, Google Analytics, Adobe Suite" | Yes |
| `<<methodology_summary>>` | user_skills (category: methodologies) | "Agile, Scrum, Design Thinking" | Optional |
| `<<domain_summary>>` | user_skills (category: domains) | "Digital Marketing, Content Strategy, Brand Management" | Yes |

### Volunteer/Leadership Variables (per entry, up to 2)
| Variable | Source | Example | Required |
|----------|--------|---------|----------|
| `<<volunteer_1_name>>` | user_volunteer.organization | "League of Extraordinary Albertans" | Optional |
| `<<volunteer_1_position>>` | user_volunteer.position | "Media Lead" | Optional |
| `<<volunteer_1_location>>` | user_volunteer.city + province | "Edmonton, AB" | Optional |
| `<<volunteer_1_dates>>` | user_volunteer.start + end | "2024 - Present" | Optional |
| `<<volunteer_1_description>>` | user_volunteer.description | "Collaborate with production teams..." | Optional |

### Cover Letter Variables
| Variable | Source | Example | Required |
|----------|--------|---------|----------|
| `<<cover_letter_hook>>` | sentence_bank_cover_letter (category: Opening) | "Your innovative approach to digital transformation..." | Yes |
| `<<cover_letter_value_prop>>` | sentence_bank_cover_letter (category: Alignment) | "I bring 14+ years of experience in..." | Yes |
| `<<cover_letter_achievement_1>>` | sentence_bank_cover_letter (category: Achievement) | "At Odvod Media, I transformed our content strategy..." | Yes |
| `<<cover_letter_company_interest>>` | sentence_bank_cover_letter (category: Alignment) | "I'm particularly drawn to your company's..." | Optional |
| `<<cover_letter_closing>>` | sentence_bank_cover_letter (category: Closing) | "I'm excited about the opportunity to contribute..." | Yes |
| `{job_title}` | jobs.job_title | "Marketing Manager" | Yes |
| `{company_name}` | companies.name | "Tech Innovators Inc." | Yes |

---

## Appendix B: Template File Structure

```
/workspace/content_template_library/
├── resumes/
│   ├── ats_professional_resume.docx
│   ├── ats_professional_resume_mapping.csv
│   ├── ats_professional_resume_metadata.json
│   ├── modern_professional_resume.docx
│   ├── modern_professional_resume_mapping.csv
│   ├── modern_professional_resume_metadata.json
│   ├── executive_leadership_resume.docx
│   ├── executive_leadership_resume_mapping.csv
│   ├── executive_leadership_resume_metadata.json
│   ├── tech_creative_resume.docx
│   ├── tech_creative_resume_mapping.csv
│   ├── tech_creative_resume_metadata.json
│   ├── skills_based_resume.docx
│   ├── skills_based_resume_mapping.csv
│   └── skills_based_resume_metadata.json
├── coverletters/
│   ├── professional_cover_letter.docx
│   ├── professional_cover_letter_mapping.csv
│   ├── professional_cover_letter_metadata.json
│   ├── modern_cover_letter.docx
│   ├── modern_cover_letter_mapping.csv
│   ├── modern_cover_letter_metadata.json
│   ├── t_format_cover_letter.docx
│   ├── t_format_cover_letter_mapping.csv
│   ├── t_format_cover_letter_metadata.json
│   ├── career_change_cover_letter.docx
│   ├── career_change_cover_letter_mapping.csv
│   ├── career_change_cover_letter_metadata.json
│   ├── email_cover_letter.docx
│   ├── email_cover_letter_mapping.csv
│   └── email_cover_letter_metadata.json
├── reference/
│   └── [original source templates for reference]
├── test_data/
│   ├── steve_glen_resume_test.json
│   ├── steve_glen_cover_letter_test.json
│   └── steve_glen_comprehensive_defaults.json
└── generated_samples/
    └── [sample outputs for QA review]
```

---

## Appendix C: ATS Optimization Guidelines

### Font Requirements
**Acceptable Fonts:**
- Arial
- Calibri
- Georgia
- Times New Roman
- Helvetica
- Verdana

**Font Sizes:**
- Name: 14-20pt
- Section Headings: 11-14pt
- Body Text: 10-12pt
- Never below 10pt

### Section Heading Standards
**Standard Section Names (ATS-friendly):**
- Professional Summary (or Summary, Professional Profile)
- Professional Experience (or Work Experience, Experience)
- Education
- Skills (or Core Competencies, Technical Skills)
- Certifications (or Professional Certifications)
- Volunteer Experience (or Leadership, Community Involvement)

**Avoid:**
- Creative section names ("My Journey", "What I Bring", etc.)
- Icons or graphics as section markers
- Underlines or excessive formatting on headings

### Layout Requirements
**ATS-Compatible:**
- Single column (safest)
- Simple two-column (main content + sidebar) - test with major ATS platforms
- Standard margins (0.5" - 1")
- Consistent alignment
- Clear visual hierarchy

**ATS-Problematic:**
- Complex multi-column layouts
- Text boxes
- Headers/footers with critical content
- Tables with merged cells
- Embedded objects or images
- Graphics, logos, or photos

### Content Formatting
**Safe Formatting:**
- Bullet points using • or - or *
- Bold for emphasis (sparingly)
- Italic for publication names
- Standard date formats

**Avoid:**
- Custom bullet characters
- Excessive underlining
- Colored text (for critical content)
- All caps for entire sections
- Fancy borders or lines

### Testing Checklist
- [ ] Copy-paste text from PDF/Word - all content intact
- [ ] Upload to jobscan.co - score 80%+
- [ ] Open in Google Docs - formatting preserved
- [ ] Open in plain text editor - content readable
- [ ] Save as PDF - searchable text maintained
- [ ] Test with Taleo (if possible)
- [ ] Test with Workday (if possible)
- [ ] Test with Greenhouse (if possible)

---

**END OF PRD**

---

## Document Control

**Version History:**
| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-10-09 | Template Creation Initiative | Initial PRD creation |

**Approval:**
- [ ] Technical Lead Review
- [ ] Content Quality Review
- [ ] Security Review
- [ ] Final Approval

**Related Documents:**
- [Template Library System Documentation](/workspace/docs/component_docs/document_generation/template_library_system.md)
- [CSV Content Mapping Specification](/workspace/docs/component_docs/document_generation/csv_content_mapping.md)
- [CLAUDE.md Project Instructions](/workspace/CLAUDE.md)
- [Content Selection Algorithm](/workspace/docs/component_docs/document_generation/content_selection_algorithm.md)
