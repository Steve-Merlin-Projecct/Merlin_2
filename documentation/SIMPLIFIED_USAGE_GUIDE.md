---
title: "Simplified Usage Guide"
type: guide
component: general
status: draft
tags: []
---

# Simplified Template Variables - Usage Guide

## Overview

All templates now use **unified, simplified variable naming** where work experience uses the same format regardless of whether it's a responsibility or achievement.

### Key Principle
**All experience bullets come from the same source** - no distinction between "responsibilities" and "achievements"

---

## Simplified Variable Format

### Work Experience: `<<job_X_experience_Y>>`

**Example:**
```json
{
  "job_1_experience_1": "Led team of 40 staff members across all operations",
  "job_1_experience_2": "Reduced operational costs by 15% through strategic planning",
  "job_1_experience_3": "Increased customer satisfaction from 4.2 to 4.8 stars"
}
```

**NOT:**
```json
{
  "job_1_responsibility_1": "...",  // ❌ OLD FORMAT
  "job_1_achievement_1": "...",     // ❌ OLD FORMAT
}
```

---

## Complete Variable Lists

### Restaurant Manager (43 Variables)

#### Contact Information (9)
- `<<first_name>>` - First name
- `<<last_name>>` - Last name
- `<<street_address>>` - Street address
- `<<city>>` - City
- `<<state>>` - State/Province
- `<<zip_code>>` - ZIP/Postal code
- `<<phone>>` - Phone number
- `<<email>>` - Email address
- `<<linkedin_url>>` - LinkedIn profile URL

#### Career Overview (5)
- `<<career_overview_1>>` - Leadership/team management qualities
- `<<career_overview_2>>` - Core expertise and passion
- `<<career_overview_3>>` - Key competencies and track record
- `<<career_overview_4>>` - Performance metrics
- `<<career_overview_5>>` - Unique value proposition

#### Work Experience - Job 1 (7)
- `<<position_1>>` - Job title
- `<<company_1>>` - Company name
- `<<start_date_1>>` - Start date
- `<<end_date_1>>` - End date or "Present"
- `<<job_1_experience_1>>` - Experience bullet 1
- `<<job_1_experience_2>>` - Experience bullet 2
- `<<job_1_experience_3>>` - Experience bullet 3

#### Work Experience - Job 2 (8)
- `<<position_2>>` - Job title
- `<<company_2>>` - Company name
- `<<start_date_2>>` - Start date
- `<<end_date_2>>` - End date
- `<<job_2_experience_1>>` - Experience bullet 1
- `<<job_2_experience_2>>` - Experience bullet 2
- `<<job_2_experience_3>>` - Experience bullet 3
- `<<job_2_experience_4>>` - Experience bullet 4

#### Education (10)
- `<<degree_1>>` - First degree
- `<<graduation_date_1>>` - First graduation date
- `<<institution_1>>` - First institution
- `<<institution_city_1>>` - First institution city
- `<<institution_state_1>>` - First institution state
- `<<degree_2>>` - Second degree
- `<<graduation_date_2>>` - Second graduation date
- `<<institution_2>>` - Second institution
- `<<institution_city_2>>` - Second institution city
- `<<institution_state_2>>` - Second institution state

#### Skills (6)
- `<<skill_1>>` through `<<skill_6>>` - Six skill entries

#### Interests (6)
- `<<interest_1>>` through `<<interest_6>>` - Six interest entries

#### Section Headers (5)
- `<<profile_header>>` - Default: "Profile"
- `<<experience_header>>` - Default: "Experience"
- `<<education_header>>` - Default: "Education"
- `<<skills_header>>` - Default: "Skills"
- `<<interests_header>>` - Default: "Interests"

---

### Accountant (29 Variables)

#### Contact (9)
Same as Restaurant Manager

#### Professional Summary (2)
- `<<professional_summary_1>>` - Core expertise statement
- `<<professional_summary_2>>` - Value proposition

#### Education (5)
- `<<degree_1>>` - Degree name
- `<<minor_1>>` - Minor field
- `<<institution_1>>` - Institution name
- `<<degree_label>>` - Label (usually "Degree")
- `<<graduation_date_1>>` - Graduation date

#### Experience (6)
- `<<position_1>>` - Job title
- `<<company_1>>` - Company name
- `<<job_city_1>>` - Job city
- `<<job_state_1>>` - Job state
- `<<start_date_1>>` - Start date
- `<<end_date_1>>` - End date

#### Skills (6)
- `<<skill_1>>` through `<<skill_6>>` - Six skill entries

#### Headers (3)
- `<<education_header>>`
- `<<experience_header>>`
- `<<skills_header>>`

---

### UI/UX Designer (20+ Variables)

#### Personal (3)
- `<<first_name>>` - First name
- `<<last_name>>` - Last name
- `<<current_title>>` - Current job title

#### Contact (5)
- `<<email>>` - Email
- `<<portfolio_website>>` - Portfolio URL
- `<<phone>>` - Phone
- `<<city>>` - City
- `<<contact_header>>` - Header

#### Professional Bio (2)
- `<<professional_bio_1>>` - First bio paragraph
- `<<professional_bio_2>>` - Second bio paragraph

#### Education (5)
- `<<institution_1>>` - Institution name
- `<<degree_1>>` - Degree type
- `<<major_1>>` - Major field
- `<<graduation_year_1>>` - Graduation year
- `<<education_header>>` - Header

#### Skills (5)
- `<<skill_1>>` through `<<skill_4>>` - Four skills
- `<<skills_header>>` - Header

#### Work Experience - Job 1 (8)
- `<<position_1>>` - Position title
- `<<company_1>>` - Company name
- `<<start_date_1>>` - Start date
- `<<end_date_1>>` - End date
- `<<job_1_experience_1>>` through `<<job_1_experience_4>>` - Experience bullets

#### Work Experience - Job 2 (7)
- `<<position_2>>` - Position title
- `<<company_2>>` - Company name
- `<<start_date_2>>` - Start date
- `<<end_date_2>>` - End date
- `<<job_2_experience_1>>` through `<<job_2_experience_3>>` - Experience bullets

---

## Example Data

### Complete Restaurant Manager Example

```json
{
  "first_name": "Sarah",
  "last_name": "Johnson",
  "street_address": "789 Park Avenue",
  "city": "Chicago",
  "state": "IL",
  "zip_code": "60601",
  "phone": "(312) 555-0200",
  "email": "sarah.johnson@email.com",
  "linkedin_url": "linkedin.com/in/sarahjohnson",

  "profile_header": "Profile",

  "career_overview_1": "Innovative restaurant leader with 15 years of experience managing high-volume establishments",
  "career_overview_2": "Passionate about creating memorable dining experiences and developing talent",
  "career_overview_3": "Expert in operational efficiency, staff development, and customer service excellence",
  "career_overview_4": "Consistently achieve 20% annual revenue growth and maintain 95% customer satisfaction",
  "career_overview_5": "Specialized in farm-to-table concepts and sustainable restaurant practices",

  "experience_header": "Experience",

  "position_1": "General Manager",
  "company_1": "The Urban Table Group",
  "start_date_1": "March 2019",
  "end_date_1": "Present",
  "job_1_experience_1": "Oversee all operations for 3 restaurant locations with combined annual revenue of $12M",
  "job_1_experience_2": "Reduced labor costs by 15% through optimized scheduling and cross-training programs",
  "job_1_experience_3": "Increased average check size by 22% through strategic menu engineering and staff training",

  "position_2": "Restaurant Manager",
  "company_2": "Harvest & Hearth",
  "start_date_2": "January 2016",
  "end_date_2": "February 2019",
  "job_2_experience_1": "Launched successful brunch program that increased weekend revenue by 40%",
  "job_2_experience_2": "Grew Instagram following from 500 to 15,000 through engaging content strategy",
  "job_2_experience_3": "Achieved perfect health department scores for 3 consecutive years",
  "job_2_experience_4": "Implemented inventory system that reduced food waste by 25% and saved $50K annually",

  "education_header": "Education",

  "degree_1": "B.S. in Hospitality Management",
  "graduation_date_1": "May 2015",
  "institution_1": "Cornell University",
  "institution_city_1": "Ithaca",
  "institution_state_1": "New York",

  "degree_2": "A.A. in Culinary Arts",
  "graduation_date_2": "May 2013",
  "institution_2": "Culinary Institute",
  "institution_city_2": "Hyde Park",
  "institution_state_2": "New York",

  "skills_header": "Skills",
  "skill_1": "Financial Planning & P&L Management",
  "skill_2": "Toast POS & Restaurant365",
  "skill_3": "Team Building & Leadership",
  "skill_4": "High-Pressure Decision Making",
  "skill_5": "Multi-Unit Operations",
  "skill_6": "Guest Experience Innovation",

  "interests_header": "Interests",
  "interest_1": "Sommelier Certification",
  "interest_2": "Sustainable Agriculture",
  "interest_3": "Food Photography",
  "interest_4": "Marathon Running",
  "interest_5": "International Cuisine",
  "interest_6": "Culinary Travel"
}
```

---

## Usage with Python

```python
from scripts.simplified_inserter import SimplifiedInserter

# Initialize
inserter = SimplifiedInserter()

# Your data
data = {
    "first_name": "John",
    "last_name": "Doe",
    # ... all variables
    "job_1_experience_1": "First experience bullet",
    "job_1_experience_2": "Second experience bullet",
    "job_1_experience_3": "Third experience bullet",
    # etc.
}

# Generate document
output = inserter.populate_template(
    template_name="restaurant_manager",
    data=data,
    output_filename="john_doe_resume.docx"
)

print(f"Generated: {output}")
```

---

## Key Benefits of Simplified Format

### 1. Single Data Source
All experience bullets come from one list - no need to categorize as "responsibilities" vs "achievements"

```python
experience_bullets = [
    "Led team of 40 staff members",
    "Reduced costs by 15%",
    "Achieved 95% customer satisfaction"
]

# Map directly to variables
data = {
    "job_1_experience_1": experience_bullets[0],
    "job_1_experience_2": experience_bullets[1],
    "job_1_experience_3": experience_bullets[2],
}
```

### 2. Easier Data Extraction
If pulling from a database or API, you just need a list of experience points:

```python
# Database query returns list
job_experiences = db.query("SELECT bullet FROM experience WHERE job_id = 1")

# Map to variables
for i, bullet in enumerate(job_experiences, 1):
    data[f"job_1_experience_{i}"] = bullet
```

### 3. Flexible Content
Users can include any combination of:
- Responsibilities
- Achievements
- Projects
- Quantified results
- Qualitative descriptions

All in the same format without artificial categorization.

---

## Files

**Templates:**
- `restaurant_manager_final.docx`
- `accountant_final.docx`
- `uiux_designer_final.docx`

**Scripts:**
- `scripts/simplified_inserter.py` - Variable insertion
- `scripts/simplified_template_converter.py` - Template conversion

**Documentation:**
- `documentation/SIMPLIFIED_VARIABLES.md` - Variable lists
- `documentation/SIMPLIFIED_USAGE_GUIDE.md` - This file

---

## Support

For questions or issues:
1. Check variable lists in `SIMPLIFIED_VARIABLES.md`
2. Review example data in this guide
3. Test with `simplified_inserter.py`