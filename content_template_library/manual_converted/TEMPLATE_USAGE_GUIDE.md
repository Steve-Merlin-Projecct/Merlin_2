---
title: "Template Usage Guide"
type: guide
component: general
status: draft
tags: []
---

# Template Usage Guide

## Converted Templates

This directory contains professionally formatted Word document templates that have been converted to use variable placeholders for dynamic content generation.

### Available Templates

1. **restaurant_manager_template_converted.docx**
   - Professional resume template for restaurant management positions
   - 15 unique variables
   - Includes skills section and interests

2. **accountant_template_converted.docx**
   - Professional resume template for accounting positions
   - 15 unique variables
   - Includes education and skills sections

## Variable Reference

### Common Variables (Both Templates)

#### Personal Information
- `<<first_name>>` - First name
- `<<last_name>>` - Last name
- `<<street_address>>` - Street address
- `<<city>>` - City name
- `<<state>>` - State abbreviation
- `<<zip_code>>` - ZIP code
- `<<phone>>` - Phone number in format (XXX) XXX-XXXX
- `<<email>>` - Email address
- `<<linkedin>>` - LinkedIn profile URL

#### Professional Information
- `<<position_title>>` - Job title being applied for
- `<<company_name>>` - Employer/company name
- `<<start_date>>` - Employment/education start date
- `<<end_date>>` - Employment/education end date (or "Present")

#### Education
- `<<education_institution>>` - School/university name
- `<<degree>>` - Degree name and major
- `<<graduation_date>>` - Graduation date

#### Skills
- `<<skill_1>>` through `<<skill_6>>` - Individual skills or competencies

### Template-Specific Variables

#### Restaurant Manager Template Only
- `<<interests>>` - Personal interests and hobbies

#### Accountant Template Only
- `<<minor>>` - Academic minor field of study

## Usage with Document Generation System

### Basic Example

```python
from docx import Document

# Load the template
template_path = "content_template_library/manual_converted/restaurant_manager_template_converted.docx"
doc = Document(template_path)

# Define your data
data = {
    "first_name": "John",
    "last_name": "Doe",
    "street_address": "123 Main Street",
    "city": "New York",
    "state": "NY",
    "zip_code": "10001",
    "phone": "(555) 123-4567",
    "email": "john.doe@example.com",
    "linkedin": "www.linkedin.com/in/johndoe",
    "position_title": "Senior Restaurant Manager",
    "company_name": "Fine Dining Restaurant",
    "start_date": "January 2020",
    "end_date": "Present",
    # ... additional fields
}

# Replace variables in paragraphs
for paragraph in doc.paragraphs:
    for key, value in data.items():
        if f"<<{key}>>" in paragraph.text:
            for run in paragraph.runs:
                run.text = run.text.replace(f"<<{key}>>", value)

# Replace variables in tables
for table in doc.tables:
    for row in table.rows:
        for cell in row.cells:
            for paragraph in cell.paragraphs:
                for key, value in data.items():
                    if f"<<{key}>>" in paragraph.text:
                        for run in paragraph.runs:
                            run.text = run.text.replace(f"<<{key}>>", value)

# Save the generated document
doc.save("output/john_doe_resume.docx")
```

### Integration with BaseGenerator

```python
from modules.document_generation.base_generator import BaseGenerator

class ResumeGenerator(BaseGenerator):
    def __init__(self, template_path: str):
        super().__init__(template_path)

    def generate(self, applicant_data: dict, output_path: str):
        """
        Generate a resume from template.

        Args:
            applicant_data: Dictionary containing all variable values
            output_path: Where to save generated document
        """
        # Use the base generator's variable replacement
        return self.replace_variables(applicant_data, output_path)

# Usage
generator = ResumeGenerator(
    "content_template_library/manual_converted/restaurant_manager_template_converted.docx"
)

applicant_data = {
    "first_name": "Jane",
    "last_name": "Smith",
    # ... all other fields
}

generator.generate(applicant_data, "output/jane_smith_resume.docx")
```

## Data Validation

### Required Fields

All templates require at minimum:
- Personal information (name, contact details)
- At least one position with company and dates
- At least one education entry

### Recommended Pydantic Model

```python
from pydantic import BaseModel, EmailStr, HttpUrl
from typing import Optional, List
from datetime import date

class ApplicantData(BaseModel):
    # Personal
    first_name: str
    last_name: str
    street_address: str
    city: str
    state: str
    zip_code: str
    phone: str
    email: EmailStr
    linkedin: Optional[HttpUrl]

    # Professional
    position_title: str
    company_name: str
    start_date: str
    end_date: str

    # Education
    education_institution: str
    degree: str
    graduation_date: str
    minor: Optional[str] = None  # Accountant template only

    # Skills
    skill_1: Optional[str] = None
    skill_2: Optional[str] = None
    skill_3: Optional[str] = None
    skill_4: Optional[str] = None
    skill_5: Optional[str] = None
    skill_6: Optional[str] = None

    # Additional
    interests: Optional[str] = None  # Restaurant manager template only
```

## Best Practices

### 1. Always Validate Data
```python
from pydantic import ValidationError

try:
    applicant = ApplicantData(**raw_data)
except ValidationError as e:
    print(f"Invalid data: {e}")
    return
```

### 2. Handle Missing Optional Fields
```python
# Provide defaults for optional fields
data = applicant.dict()
for i in range(1, 7):
    if not data.get(f'skill_{i}'):
        data[f'skill_{i}'] = ''  # Empty string instead of None
```

### 3. Format Dates Consistently
```python
from datetime import datetime

# Convert dates to consistent format
date_obj = datetime.strptime(raw_date, "%Y-%m-%d")
formatted_date = date_obj.strftime("%B %Y")  # "January 2024"
```

### 4. Preserve Formatting
Always use run-level replacements to preserve formatting:
```python
# Good - preserves formatting
for run in paragraph.runs:
    run.text = run.text.replace(old, new)

# Bad - loses formatting
paragraph.text = paragraph.text.replace(old, new)
```

### 5. Test Output
Always verify generated documents:
- Open in Microsoft Word
- Check all variables replaced
- Verify formatting intact
- Review for professional appearance

## Troubleshooting

### Variable Not Replaced
**Symptom:** Variable placeholder still visible in output

**Solutions:**
1. Check variable name spelling (case-sensitive)
2. Ensure data dictionary includes the variable
3. Verify replacement code processes both paragraphs and tables

### Formatting Lost
**Symptom:** Bold, italics, or colors removed

**Solutions:**
1. Use run-level replacement, not paragraph-level
2. Don't reassign `paragraph.text` directly
3. Process each run individually

### Multiple Values
**Symptom:** Same variable used multiple times, but only first is replaced

**Solutions:**
1. Iterate through all paragraphs, not just until first match
2. Process tables separately from paragraphs
3. Check for duplicate cell content in tables

## Original Templates

Original (unconverted) templates are also available:
- `restaurant_manager_template.docx` - Original with sample data
- `accountant_template.docx` - Original with sample data

These can be useful for:
- Visual reference
- Understanding original structure
- Testing conversion scripts
- Comparison with converted versions

## Conversion Scripts

Scripts used to create these templates:
- `/workspace/manual_conversion_final.py` - Production conversion script
- `/workspace/TEMPLATE_CONVERSION_REPORT.md` - Detailed conversion documentation

## Support

For issues or questions:
1. Review the Template Conversion Report for technical details
2. Check the document generation module documentation
3. Verify your data matches the expected variable names
4. Test with the example code in this guide
