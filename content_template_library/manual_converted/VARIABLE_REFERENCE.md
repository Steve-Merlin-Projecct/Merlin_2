# UI/UX Designer Template - Variable Reference Guide

**Template:** `uiux_designer_template_converted.docx`
**Total Variables:** 21
**Last Updated:** October 21, 2025

---

## Quick Variable Lookup

This document provides a quick reference for all variables in the UI/UX Designer template.

---

## Variables by Category

### Personal Information (2)

| Variable | Type | Example Value | Notes |
|----------|------|---------------|-------|
| `<<first_name>>` | String | Angelica | First name only |
| `<<last_name>>` | String | Astrom | Last name only |

**Location:** Document paragraphs (header area)

---

### Contact Information (4)

| Variable | Type | Example Value | Format |
|----------|------|---------------|--------|
| `<<email>>` | String | angelica@example.com | Valid email format |
| `<<portfolio_website>>` | String | www.interestingsite.com | URL format |
| `<<phone>>` | String | (212) 555-0155 | US phone format |
| `<<city>>` | String | New York City | City name |

**Location:** Table 1, Right column (Contact section)

---

### Professional Summary (2)

| Variable | Type | Example Value | Max Length |
|----------|------|---------------|------------|
| `<<job_title>>` | String | UI/UX Designer | ~50 chars |
| `<<professional_bio>>` | Text | I am passionate about designing... | ~200 chars |

**Location:** Table 1, Left column

**Bio Example:**
```
I am passionate about designing digital experiences that are both visually
stunning and easy to use. With a keen eye for detail and a user-centric
approach, I strive to create products that delight and engage users.
```

---

### Education (3)

| Variable | Type | Example Value | Notes |
|----------|------|---------------|-------|
| `<<education_institution>>` | String | SCHOOL OF FINE ART | Institution name |
| `<<degree>>, <<major>>` | String | BFA, Graphic Design | Degree type, Major field |
| `<<graduation_year>>` | Integer/String | 2020 | Four-digit year |

**Location:** Table 2, Column 1 (Education section)

**Important:** The degree and major variable is a single replacement that includes both values separated by a comma.

---

### Skills (4)

| Variable | Type | Example Value |
|----------|------|---------------|
| `<<skill_1>>` | String | UI/UX design |
| `<<skill_2>>` | String | User research |
| `<<skill_3>>` | String | Usability testing |
| `<<skill_4>>` | String | Project management |

**Location:** Table 2, Column 1 (Skills section)

**Notes:**
- Skills are listed sequentially
- Template has space for 4 skills
- Keep skill names concise (< 30 characters)
- More skills can be added by duplicating the pattern

---

### Experience - Position 1 (6)

| Variable | Type | Example Value | Format |
|----------|------|---------------|--------|
| `<<position_1>>` | String | Senior UI/UX Designer | Job title |
| `<<company_1>>` | String | PROSEWARE, INC. | Company name |
| `<<start_date_1>>` | String | Jan 2020 | Month YYYY |
| `<<end_date_1>>` | String | Dec 2022 | Month YYYY or "Present" |
| `<<job_description_1_2>>` | Text | Managed the design team... | Description paragraph |
| `<<job_description_1_3>>` | Text | Led the redesign of... | Description paragraph |
| `<<job_description_1_4>>` | Text | Conducted user research... | Description paragraph |

**Location:** Table 2, Column 2 (Experience section)

**Date Range Format:**
```
<<start_date_1>> - <<end_date_1>>
```
Displays as: `Jan 2020 - Dec 2022`

**Job Description Examples:**
```
<<job_description_1_2>>
Managed the design team and mentored junior designers. Established design
guidelines and best practices for the entire organization.

<<job_description_1_3>>
Led the redesign of the company's e-commerce platform, resulting in a 30%
increase in conversion rates and improved user satisfaction scores.

<<job_description_1_4>>
Conducted user research and developed user personas to guide design decisions.
Implemented A/B testing to validate design choices.
```

---

## Variable Replacement Example

### Input Data (Python dict):
```python
template_data = {
    # Personal
    "first_name": "John",
    "last_name": "Smith",

    # Contact
    "email": "john.smith@email.com",
    "portfolio_website": "www.johnsmithdesign.com",
    "phone": "(555) 123-4567",
    "city": "San Francisco",

    # Professional
    "job_title": "Senior UX Designer",
    "professional_bio": "Creative UX designer with 8+ years of experience...",

    # Education
    "education_institution": "CALIFORNIA DESIGN INSTITUTE",
    "degree": "MS",
    "major": "Human-Computer Interaction",
    "graduation_year": "2015",

    # Skills
    "skill_1": "User Experience Design",
    "skill_2": "Interaction Design",
    "skill_3": "Wireframing & Prototyping",
    "skill_4": "Design Systems",

    # Experience
    "position_1": "Senior UX Designer",
    "company_1": "TECH INNOVATIONS INC.",
    "start_date_1": "Mar 2020",
    "end_date_1": "Present",
    "job_description_1_2": "Lead UX designer for mobile applications...",
    "job_description_1_3": "Created comprehensive design systems...",
    "job_description_1_4": "Collaborated with cross-functional teams...",
}
```

---

## Template Structure Overview

```
┌─────────────────────────────────────────────────────────────┐
│ <<first_name>> <<last_name>>                                │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ TABLE 1: Header / Contact Information                      │
├────────────────────────────────┬────────────────────────────┤
│ Left Column                    │ Right Column               │
├────────────────────────────────┼────────────────────────────┤
│ <<job_title>>                  │ Contact                    │
│                                │ <<email>>                  │
│ <<professional_bio>>           │ <<portfolio_website>>      │
│                                │ <<phone>>                  │
│                                │ <<city>>                   │
└────────────────────────────────┴────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ TABLE 2: Education / Skills / Experience                   │
├──────────────┬──────────────┬───────────────────────────────┤
│ Column 1     │ Column 2     │ Column 3                      │
├──────────────┼──────────────┼───────────────────────────────┤
│ Education    │              │ Experience                    │
│              │              │                               │
│ <<education_ │              │ <<position_1>>                │
│  institution>>│             │ <<company_1>>                 │
│ <<degree>>,  │              │ <<start_date_1>> -            │
│  <<major>>   │              │  <<end_date_1>>               │
│ <<grad_year>>│              │                               │
│              │              │ <<job_description_1_2>>       │
│ Skills       │              │ <<job_description_1_3>>       │
│              │              │ <<job_description_1_4>>       │
│ <<skill_1>>  │              │                               │
│ <<skill_2>>  │              │                               │
│ <<skill_3>>  │              │                               │
│ <<skill_4>>  │              │                               │
└──────────────┴──────────────┴───────────────────────────────┘
```

---

## Programming Interface

### For Document Generation System

```python
from docx import Document

def populate_uiux_template(template_path: str, data: dict, output_path: str):
    """
    Populate the UI/UX Designer template with actual data.

    Args:
        template_path: Path to uiux_designer_template_converted.docx
        data: Dictionary containing variable values
        output_path: Path to save the populated document
    """
    doc = Document(template_path)

    # Replace variables in paragraphs
    for paragraph in doc.paragraphs:
        for key, value in data.items():
            placeholder = f'<<{key}>>'
            if placeholder in paragraph.text:
                for run in paragraph.runs:
                    run.text = run.text.replace(placeholder, str(value))

    # Replace variables in tables
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for paragraph in cell.paragraphs:
                    for key, value in data.items():
                        placeholder = f'<<{key}>>'
                        if placeholder in paragraph.text:
                            for run in paragraph.runs:
                                run.text = run.text.replace(placeholder, str(value))

    doc.save(output_path)
```

---

## Validation Rules

### Required Fields
The following variables MUST be populated:
- `<<first_name>>`
- `<<last_name>>`
- `<<email>>`
- `<<phone>>`
- `<<job_title>>`

### Optional Fields
These variables can be left as placeholders or removed:
- `<<portfolio_website>>` - Can be omitted if no portfolio
- `<<skill_3>>`, `<<skill_4>>` - Can reduce number of skills if needed

### Format Validation

**Email:**
```python
import re
email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
assert re.match(email_pattern, email_value)
```

**Phone:**
```python
phone_pattern = r'^\(\d{3}\)\s*\d{3}-\d{4}$'
assert re.match(phone_pattern, phone_value)
```

**Year:**
```python
assert 1950 <= int(graduation_year) <= 2030
```

---

## Common Issues & Solutions

### Issue 1: Variable Not Replaced
**Problem:** Variable placeholder still visible in final document
**Solution:** Ensure exact match including `<<` and `>>` delimiters

### Issue 2: Formatting Lost
**Problem:** Replaced text has different formatting than original
**Solution:** Use run-level replacement, don't recreate paragraphs

### Issue 3: Date Range Format
**Problem:** Date range displays incorrectly
**Solution:** Ensure both `<<start_date_1>>` and `<<end_date_1>>` are replaced

### Issue 4: Special Characters
**Problem:** Special characters (&, <, >) cause issues
**Solution:** Escape special characters or use character codes

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | Oct 21, 2025 | Initial conversion with 21 variables |

---

## Support & Documentation

- **Conversion Script:** `uiux_conversion_final.py`
- **Summary Document:** `UIUX_CONVERSION_SUMMARY.md`
- **Complete Report:** `CONVERSION_COMPLETE_REPORT.md`
- **This Reference:** `VARIABLE_REFERENCE.md`

---

**Template File:** `/workspace/content_template_library/manual_converted/uiux_designer_template_converted.docx`

**Status:** ✓ Production Ready

---

*End of Variable Reference*
