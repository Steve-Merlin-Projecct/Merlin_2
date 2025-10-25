---
title: "Template Expected Inputs Guide"
type: guide
component: general
status: draft
tags: []
---

# Template Expected Inputs Guide

## Overview

This guide documents all expected inputs for the fully converted templates. Each template requires specific data to replace the variable placeholders with actual content.

**Total Variables Across Templates: 92**
- Restaurant Manager: 43 variables
- Accountant: 29 variables
- UI/UX Designer: 20 variables

---

## Input Data Format

Provide data as JSON with variable names as keys:

```json
{
  "first_name": "John",
  "last_name": "Doe",
  "email": "john.doe@example.com",
  // ... additional variables
}
```

---

## Restaurant Manager Template (43 Variables)

### Personal & Contact Information
```json
{
  "first_name": "Your first name",
  "last_name": "Your last name",
  "street_address": "123 Main Street",
  "city": "New York",
  "state": "NY",
  "zip_code": "10001",
  "phone": "(555) 123-4567",
  "email": "your.email@example.com",
  "linkedin_url": "linkedin.com/in/yourprofile"
}
```

### Career Overview (Professional Summary)
Break your professional summary into 5 semantic components:

```json
{
  "career_overview_1": "Your leadership qualities and team management approach",
  "career_overview_2": "Your core expertise and passion in the industry",
  "career_overview_3": "Your key competencies and proven track record",
  "career_overview_4": "Specific performance metrics or achievements",
  "career_overview_5": "Your unique value proposition or special expertise"
}
```

**Example:**
```json
{
  "career_overview_1": "Dynamic and inspiring leader able to motivate teams of 50+ staff members",
  "career_overview_2": "Passionate restaurant professional with expertise in fine dining operations",
  "career_overview_3": "Track record of implementing training programs that improve service quality",
  "career_overview_4": "Consistently exceed revenue targets by 15-20% year over year",
  "career_overview_5": "Expert in wine pairing and customer experience optimization"
}
```

### Work Experience - Job 1 (Most Recent)
```json
{
  "position_1": "Your current/most recent job title",
  "company_1": "Company name",
  "start_date_1": "Month Year",
  "end_date_1": "Present or Month Year",
  "job_1_responsibility_1": "Primary responsibility with scope and scale",
  "job_1_achievement_1": "Quantified cost reduction or efficiency achievement",
  "job_1_achievement_2": "Revenue or customer satisfaction improvement"
}
```

### Work Experience - Job 2 (Previous)
```json
{
  "position_2": "Previous job title",
  "company_2": "Previous company name",
  "start_date_2": "Month Year",
  "end_date_2": "Month Year",
  "job_2_responsibility_1": "Key initiative or program you created",
  "job_2_achievement_1": "Growth metrics (customers, social media, etc.)",
  "job_2_achievement_2": "Quality or compliance achievement",
  "job_2_achievement_3": "Efficiency or process improvement"
}
```

### Education
```json
{
  "degree_1": "B.S. in Hospitality Management",
  "graduation_date_1": "May 2020",
  "institution_1": "Cornell University",
  "institution_1_city": "Ithaca",
  "institution_1_state": "New York",

  "degree_2": "A.A. in Culinary Arts",
  "graduation_date_2": "May 2018",
  "institution_2": "Culinary Institute",
  "institution_2_city": "Hyde Park",
  "institution_2_state": "New York"
}
```

### Skills (6 Required)
```json
{
  "skill_1": "Financial/Accounting skill (e.g., P&L Management)",
  "skill_2": "Technical system skill (e.g., POS Systems)",
  "skill_3": "Communication skill (e.g., Team Leadership)",
  "skill_4": "Performance trait (e.g., Crisis Management)",
  "skill_5": "Experience breadth (e.g., Multi-unit Operations)",
  "skill_6": "Personality trait (e.g., Customer-Focused)"
}
```

### Interests (6 Required)
```json
{
  "interest_1": "Professional development interest",
  "interest_2": "Industry-related hobby",
  "interest_3": "Creative pursuit",
  "interest_4": "Physical activity",
  "interest_5": "Cultural interest",
  "interest_6": "Travel or adventure"
}
```

### Section Headers (Optional - Use Defaults)
```json
{
  "profile_section_header": "Profile",
  "experience_section_header": "Experience",
  "education_section_header": "Education",
  "skills_section_header": "Skills & Abilities",
  "interests_section_header": "Activities and Interests"
}
```

---

## Accountant Template (29 Variables)

### Personal & Contact Information
```json
{
  "first_name": "Your first name",
  "last_name": "Your last name",
  "street_address": "456 Oak Avenue",
  "city": "San Francisco",
  "state": "CA",
  "zip_code": "94102",
  "phone": "(415) 555-0100",
  "email": "your.email@example.com",
  "linkedin_url": "linkedin.com/in/yourprofile"
}
```

### Professional Summary (2 Parts)
```json
{
  "professional_summary_1": "Your core expertise and years of experience",
  "professional_summary_2": "Your value proposition and approach to work"
}
```

**Example:**
```json
{
  "professional_summary_1": "CPA with 10+ years of experience in public accounting and financial reporting for Fortune 500 companies",
  "professional_summary_2": "Known for implementing cost-saving measures and streamlining financial processes that improve accuracy by 40%"
}
```

### Education
```json
{
  "degree_1": "Bachelor of Science in Accounting",
  "minor_1": "Finance",
  "institution_1": "University Name",
  "degree_label": "Degree",
  "graduation_date_1": "May 2015"
}
```

### Experience
```json
{
  "position_1": "Senior Accountant",
  "company_1": "Big Four Firm",
  "job_1_city": "San Francisco",
  "job_1_state": "CA",
  "start_date_1": "January 2018",
  "end_date_1": "Present"
}
```

### Skills
```json
{
  "technical_skill_1": "Software (e.g., QuickBooks)",
  "technical_skill_2": "Technical skill (e.g., Financial Analysis)",
  "technical_skill_3": "Compliance (e.g., GAAP)",
  "technical_skill_4": "Process skill (e.g., Auditing)",
  "soft_skill_1": "Communication skill",
  "language_skill_1": "Language and proficiency level"
}
```

### Section Headers (Optional)
```json
{
  "education_header": "Education",
  "experience_header": "Experience",
  "skills_header": "Skills"
}
```

---

## UI/UX Designer Template (20 Variables)

### Personal Information
```json
{
  "first_name": "Your first name",
  "last_name": "Your last name"
}
```

### Professional
```json
{
  "current_title": "Senior UI/UX Designer"
}
```

### Contact Information
```json
{
  "contact_header": "Contact",
  "email": "your.email@example.com",
  "portfolio_website": "www.yourportfolio.com",
  "phone": "(212) 555-0100",
  "city": "New York City"
}
```

### Education
```json
{
  "education_header": "Education",
  "institution_1": "Parsons School of Design",
  "degree_type_1": "MFA",
  "major_1": "Digital Design",
  "graduation_year_1": "2020"
}
```

### Skills
```json
{
  "skills_header": "Skills",
  "skill_2": "User Research",
  "skill_3": "Wireframing",
  "skill_4": "Prototyping"
}
```

### Experience
```json
{
  "experience_header": "Experience",
  "position_2": "UI/UX Designer",
  "company_1": "Tech Company Name"
}
```

---

## Complete Example JSON File

```json
{
  "restaurant_manager": {
    "first_name": "Sarah",
    "last_name": "Johnson",
    "street_address": "789 Park Avenue",
    "city": "Chicago",
    "state": "IL",
    "zip_code": "60601",
    "phone": "(312) 555-0200",
    "email": "sarah.johnson@email.com",
    "linkedin_url": "linkedin.com/in/sarahjohnson",

    "profile_section_header": "Profile",
    "career_overview_1": "Innovative restaurant leader with 15 years of experience managing high-volume establishments",
    "career_overview_2": "Passionate about creating memorable dining experiences and developing talent",
    "career_overview_3": "Expert in operational efficiency, staff development, and customer service excellence",
    "career_overview_4": "Consistently achieve 20% annual revenue growth and maintain 95% customer satisfaction",
    "career_overview_5": "Specialized in farm-to-table concepts and sustainable restaurant practices",

    "experience_section_header": "Experience",
    "position_1": "General Manager",
    "company_1": "The Urban Table Group",
    "start_date_1": "March 2019",
    "end_date_1": "Present",
    "job_1_responsibility_1": "Oversee all operations for 3 restaurant locations with combined annual revenue of $12M",
    "job_1_achievement_1": "Reduced labor costs by 15% through optimized scheduling and cross-training programs",
    "job_1_achievement_2": "Increased average check size by 22% through strategic menu engineering and staff training",

    "position_2": "Restaurant Manager",
    "company_2": "Harvest & Hearth",
    "start_date_2": "January 2016",
    "end_date_2": "February 2019",
    "job_2_responsibility_1": "Launched successful brunch program that increased weekend revenue by 40%",
    "job_2_achievement_1": "Grew Instagram following from 500 to 15,000 through engaging content strategy",
    "job_2_achievement_2": "Achieved perfect health department scores for 3 consecutive years",
    "job_2_achievement_3": "Implemented inventory system that reduced food waste by 25% and saved $50K annually",

    "education_section_header": "Education",
    "degree_1": "B.S. in Hospitality Management",
    "graduation_date_1": "May 2015",
    "institution_1": "Johnson & Wales University",
    "institution_1_city": "Providence",
    "institution_1_state": "Rhode Island",

    "degree_2": "A.A. in Culinary Arts",
    "graduation_date_2": "May 2013",
    "institution_2": "Le Cordon Bleu",
    "institution_2_city": "Chicago",
    "institution_2_state": "Illinois",

    "skills_section_header": "Skills",
    "skill_1": "Financial Planning & P&L Management",
    "skill_2": "Toast POS & Restaurant365",
    "skill_3": "Team Building & Leadership",
    "skill_4": "High-Pressure Decision Making",
    "skill_5": "Multi-Unit Operations",
    "skill_6": "Guest Experience Innovation",

    "interests_section_header": "Interests",
    "interest_1": "Sommelier Certification",
    "interest_2": "Sustainable Agriculture",
    "interest_3": "Food Photography",
    "interest_4": "Marathon Running",
    "interest_5": "International Cuisine",
    "interest_6": "Culinary Travel"
  }
}
```

---

## Important Notes

### Missing Variables
If you don't provide a value for a variable, it will remain as `<<variable_name>>` in the generated document. Always provide values for all variables.

### Variable Naming Convention
- Variables use lowercase with underscores: `job_1_achievement_1`
- Number suffixes indicate sequence: `_1`, `_2`, etc.
- Semantic prefixes indicate content type: `career_overview_`, `job_`, `skill_`

### Content Guidelines

#### Career Overview / Professional Summary
- Break long paragraphs into 3-5 semantic chunks
- Each chunk should be 1-2 sentences
- Focus on different aspects: leadership, expertise, achievements, unique value

#### Work Experience
- Responsibilities: Focus on scope, scale, and key initiatives
- Achievements: Include quantified results (percentages, dollar amounts, metrics)
- Use action verbs: Led, Implemented, Achieved, Reduced, Increased

#### Skills
- Balance technical and soft skills
- Be specific rather than generic
- Include both tools/systems and competencies

#### Education
- Include city and state for each institution
- Use standard degree abbreviations (B.S., M.A., etc.)
- Include graduation dates

### Section Headers
All section headers are customizable but have sensible defaults:
- "Profile" → Can change to "Summary" or "Overview"
- "Experience" → Can change to "Professional Experience" or "Work History"
- "Education" → Can change to "Academic Background"
- "Skills" → Can change to "Core Competencies" or "Expertise"

---

## Usage Example

```python
from scripts.template_variable_inserter import TemplateVariableInserter

# Initialize inserter
inserter = TemplateVariableInserter()

# Load your data
data = {
    "first_name": "John",
    "last_name": "Smith",
    # ... all other variables
}

# Generate document
output_path = inserter.populate_template(
    template_name="restaurant_manager",
    data=data,
    output_filename="john_smith_resume.docx"
)

print(f"Resume generated: {output_path}")
```

---

## Validation Checklist

Before generating your document, ensure:

- [ ] All required variables have values
- [ ] Dates use consistent format (Month Year)
- [ ] Phone numbers include area code
- [ ] Email addresses are valid format
- [ ] Skills and interests have all 6 slots filled
- [ ] Career overview has all 5 components
- [ ] Work experience includes both responsibilities and achievements
- [ ] Education includes location information

---

## Support

For questions about specific variables, refer to:
- `./documentation/TEMPLATE_VARIABLES_COMPLETE.md` - Complete variable list
- `./data/sample_data.json` - Example data for all templates
- `./scripts/template_variable_inserter.py` - Implementation details