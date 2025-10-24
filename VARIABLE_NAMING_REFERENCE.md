# Variable Naming Reference Guide

**Document Version:** 1.0
**Last Updated:** 2025-10-24
**Status:** Canonical Reference

## Overview

This document provides the authoritative reference for all variable naming conventions used in the document generation system. The system has been harmonized to use a **single unified naming standard** based on the CSV naming convention.

## Naming Standard

All variables use the **CSV naming convention** with the format:
- Descriptive snake_case names
- User-prefixed for personal information: `user_first_name`, `user_email`
- Numbered patterns for repeated items: `work_experience_1_position`, `edu_1_degree`
- Multi-numbered for nested repetitions: `work_experience_1_skill1`, `work_experience_2_skill3`

## Variable Categories

### 1. Personal Information

| Variable Name | Description | Data Source |
|--------------|-------------|-------------|
| `user_first_name` | First name | user_profile |
| `user_last_name` | Last name | user_profile |
| `user_email` | Email address | user_profile |
| `user_phone` | Phone number | user_profile |
| `user_linkedin` | LinkedIn URL | user_profile |
| `user_city_prov` | City and province (combined) | user_profile |
| `user_portfolio` | Portfolio URL | user_profile |
| `user_github` | GitHub URL | user_profile |
| `professional_title` | Professional title/tagline | user_profile |

### 2. Professional Summary

| Variable Name | Description | Data Source |
|--------------|-------------|-------------|
| `professional_summary` | Professional summary paragraph | user_profile |
| `executive_summary` | Executive summary paragraph | user_profile |
| `executive_title` | Executive title | user_profile |
| `tech_specialty` | Technology specialty | user_profile |

### 3. Skills

| Variable Name | Description | Data Source |
|--------------|-------------|-------------|
| `technical_summary` | Technical skills list | user_skills |
| `methodology_summary` | Methodologies/frameworks list | user_skills |
| `domain_summary` | Domain expertise list | user_skills |

### 4. Leadership Competencies

| Variable Name | Description | Data Source |
|--------------|-------------|-------------|
| `leadership_competency_1` | Leadership competency 1 | user_skills |
| `leadership_competency_2` | Leadership competency 2 | user_skills |
| `leadership_competency_3` | Leadership competency 3 | user_skills |
| `leadership_competency_4` | Leadership competency 4 | user_skills |

### 5. Skills-Based Achievements

| Variable Name | Description | Data Source |
|--------------|-------------|-------------|
| `achievement_technical_1` | Technical achievement 1 | sentence_bank_resume |
| `achievement_technical_2` | Technical achievement 2 | sentence_bank_resume |
| `achievement_leadership_1` | Leadership achievement 1 | sentence_bank_resume |
| `achievement_leadership_2` | Leadership achievement 2 | sentence_bank_resume |

### 6. Education

| Variable Name | Description | Data Source |
|--------------|-------------|-------------|
| `edu_1_name` | Educational institution name | user_education |
| `edu_1_degree` | Degree type | user_education |
| `edu_1_concentration` | Field of study/concentration | user_education |
| `edu_1_specialization` | Specialization area | user_education |
| `edu_1_grad_date` | Graduation date | user_education |
| `edu_1_location` | Institution location | user_education |

**Note:** Use `edu_2_*`, `edu_3_*`, etc. for additional education entries.

### 7. Work Experience - Job 1

| Variable Name | Description | Data Source |
|--------------|-------------|-------------|
| `work_experience_1_position` | Job position/title | user_work_experience |
| `work_experience_1_name` | Company name | user_work_experience |
| `work_experience_1_location` | Job location | user_work_experience |
| `work_experience_1_dates` | Employment dates | user_work_experience |
| `work_experience_1_context` | Company context description | user_work_experience |
| `work_experience_1_tech_stack` | Technology stack used | user_work_experience |
| `work_experience_1_skill1` | Achievement/responsibility 1 | sentence_bank_resume |
| `work_experience_1_skill2` | Achievement/responsibility 2 | sentence_bank_resume |
| `work_experience_1_skill3` | Achievement/responsibility 3 | sentence_bank_resume |
| `work_experience_1_skill4` | Achievement/responsibility 4 | sentence_bank_resume |
| `work_experience_1_skill5` | Achievement/responsibility 5 | sentence_bank_resume |
| `work_experience_1_skill6` | Achievement/responsibility 6 | sentence_bank_resume |

### 8. Work Experience - Job 2

| Variable Name | Description | Data Source |
|--------------|-------------|-------------|
| `work_experience_2_position` | Job 2 position/title | user_work_experience |
| `work_experience_2_name` | Job 2 company name | user_work_experience |
| `work_experience_2_location` | Job 2 location | user_work_experience |
| `work_experience_2_dates` | Job 2 employment dates | user_work_experience |
| `work_experience_2_skill1` | Job 2 achievement 1 | sentence_bank_resume |
| `work_experience_2_skill2` | Job 2 achievement 2 | sentence_bank_resume |
| `work_experience_2_skill3` | Job 2 achievement 3 | sentence_bank_resume |

**Note:** Pattern continues for `work_experience_3_*`, `work_experience_4_*`, etc.

### 9. Volunteer Experience

| Variable Name | Description | Data Source |
|--------------|-------------|-------------|
| `volunteer_1_position` | Volunteer position title | user_volunteer |
| `volunteer_1_name` | Volunteer organization name | user_volunteer |
| `volunteer_1_location` | Volunteer location | user_volunteer |
| `volunteer_1_dates` | Volunteer date range | user_volunteer |
| `volunteer_1_description` | Volunteer work description | user_volunteer |

**Note:** Use `volunteer_2_*`, `volunteer_3_*`, etc. for additional volunteer entries.

### 10. Certifications

| Variable Name | Description | Data Source |
|--------------|-------------|-------------|
| `certifications_list` | Professional certifications (comma-separated or list) | user_certifications |

### 11. Cover Letter - Company Information

| Variable Name | Description | Data Source |
|--------------|-------------|-------------|
| `company_name` | Target company name | job_data |
| `company_address` | Company street address | job_data |
| `company_city_prov` | Company city and province | job_data |
| `hiring_manager_name` | Hiring manager full name | job_data |
| `hiring_manager_first_name` | Hiring manager first name only | job_data |
| `hiring_manager_title` | Hiring manager job title | job_data |

### 12. Cover Letter - Content (General)

| Variable Name | Description | Data Source |
|--------------|-------------|-------------|
| `cover_letter_opening` | Opening paragraph | sentence_bank_cover_letter |
| `cover_letter_skills_alignment` | Skills alignment paragraph | sentence_bank_cover_letter |
| `cover_letter_achievement` | Achievement paragraph | sentence_bank_cover_letter |
| `cover_letter_closing` | Closing paragraph | sentence_bank_cover_letter |

### 13. Cover Letter - Content (Modern Template)

| Variable Name | Description | Data Source |
|--------------|-------------|-------------|
| `cover_letter_hook` | Opening hook statement | sentence_bank_cover_letter |
| `cover_letter_value_prop` | Value proposition paragraph | sentence_bank_cover_letter |
| `cover_letter_company_interest` | Company interest statement | sentence_bank_cover_letter |

### 14. Cover Letter - Content (Email Template)

| Variable Name | Description | Data Source |
|--------------|-------------|-------------|
| `cover_letter_email_hook` | Email-specific opening hook | sentence_bank_cover_letter |
| `cover_letter_value_prop_brief` | Brief value proposition | sentence_bank_cover_letter |
| `cover_letter_achievement_brief` | Brief achievement highlight | sentence_bank_cover_letter |
| `cover_letter_cta` | Call to action statement | sentence_bank_cover_letter |

### 15. Cover Letter - Content (Career Change Template)

| Variable Name | Description | Data Source |
|--------------|-------------|-------------|
| `cover_letter_transition_hook` | Career transition opening hook | sentence_bank_cover_letter |
| `cover_letter_transferable_skills` | Transferable skills paragraph | sentence_bank_cover_letter |
| `cover_letter_enthusiasm` | Enthusiasm statement | sentence_bank_cover_letter |
| `cover_letter_preparation` | Preparation/commitment statement | sentence_bank_cover_letter |

### 16. Cover Letter - Content (T-Format Template)

| Variable Name | Description | Data Source |
|--------------|-------------|-------------|
| `cover_letter_intro` | Introduction paragraph | sentence_bank_cover_letter |
| `cover_letter_summary` | Summary/closing paragraph | sentence_bank_cover_letter |
| `job_requirement_1` | Job requirement 1 from posting | job_data |
| `job_requirement_2` | Job requirement 2 from posting | job_data |
| `job_requirement_3` | Job requirement 3 from posting | job_data |
| `job_requirement_4` | Job requirement 4 from posting | job_data |
| `matching_qualification_1` | Your qualification matching req 1 | sentence_bank_cover_letter |
| `matching_qualification_2` | Your qualification matching req 2 | sentence_bank_cover_letter |
| `matching_qualification_3` | Your qualification matching req 3 | sentence_bank_cover_letter |
| `matching_qualification_4` | Your qualification matching req 4 | sentence_bank_cover_letter |

### 17. Metadata

| Variable Name | Description | Data Source |
|--------------|-------------|-------------|
| `current_date` | Document generation date | system_generated |

## Template Usage

### In .docx Templates
Variables are referenced using double angle bracket notation:
```
<<user_first_name>> <<user_last_name>>
<<user_email>> | <<user_phone>> | <<user_linkedin>>
<<user_city_prov>>
```

### In CSV Mapping Files
Each variable has a corresponding entry in the template's CSV mapping file:
```csv
Original_Text,Is_Variable,Is_Static,Is_discarded,Variable_name,Variable_intention,Variable_category,Static_Text,Content_source
FirstName LastName,TRUE,FALSE,FALSE,user_first_name user_last_name,Full name,User Profile,,user_profile
```

### In Python Code
Templates use the variable names directly:
```python
data = {
    'user_first_name': 'John',
    'user_last_name': 'Doe',
    'user_email': 'john.doe@example.com',
    'professional_summary': 'Experienced software engineer...'
}
```

## Naming Patterns

### Single Values
Simple descriptive names:
- `user_email`
- `professional_summary`
- `certifications_list`

### Numbered Items
For repeated sections (jobs, education, etc.):
- `work_experience_1_position` (first job title)
- `work_experience_2_name` (second job company)
- `edu_1_degree` (first education degree)

### Multi-Numbered Items
For items within repeated sections (achievements within jobs):
- `work_experience_1_skill1` (first achievement at first job)
- `work_experience_1_skill2` (second achievement at first job)
- `work_experience_2_skill1` (first achievement at second job)

## Data Sources

Variables pull data from different sources:

| Source | Description | Examples |
|--------|-------------|----------|
| `user_profile` | Personal information | name, contact info, location |
| `user_skills` | Skills and competencies | technical_summary, domain_summary |
| `user_education` | Educational background | degrees, institutions, dates |
| `user_work_experience` | Work history metadata | company names, titles, dates |
| `user_volunteer` | Volunteer experience | organizations, roles, dates |
| `user_certifications` | Professional certifications | certification names |
| `job_data` | Job-specific information | company name, requirements |
| `sentence_bank_resume` | AI-generated resume content | achievements, responsibilities |
| `sentence_bank_cover_letter` | AI-generated cover letter content | paragraphs, statements |
| `system_generated` | System-provided values | current date, timestamps |

## Best Practices

### DO:
- ✅ Use the exact variable names as documented
- ✅ Follow the numbered pattern for multiple items
- ✅ Use descriptive names that clearly indicate content
- ✅ Keep variable names in snake_case format
- ✅ Prefix user-related variables with `user_`

### DON'T:
- ❌ Create custom variable names not in this reference
- ❌ Mix naming conventions (CSV vs production names)
- ❌ Use camelCase or PascalCase
- ❌ Skip numbers in sequences (use 1, 2, 3 not 1, 3, 5)
- ❌ Modify variable names in templates without updating mappings

## Template-Specific Variables

Some templates use specialized variables:

### Executive Leadership Resume
- `executive_summary` - Executive-level summary
- `executive_title` - Executive title
- `leadership_competency_1-4` - Leadership competencies
- `work_experience_1_context` - Company context

### Tech Creative Resume
- `tech_specialty` - Technology specialty area
- `user_github` - GitHub profile URL
- `user_portfolio` - Portfolio website URL
- `work_experience_1_tech_stack` - Technology stack

### Skills-Based Resume
- `achievement_technical_1-2` - Technical achievements
- `achievement_leadership_1-2` - Leadership achievements

### T-Format Cover Letter
- `job_requirement_1-4` - Requirements from job posting
- `matching_qualification_1-4` - Your matching qualifications

## Validation

All variable names should:
1. Exist in this reference document
2. Match exactly in templates and CSV mappings
3. Use consistent snake_case formatting
4. Follow documented numbering patterns
5. Pull from appropriate data sources

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-10-24 | Initial unified naming standard |

---

**For questions or updates, consult the development team before modifying variable names.**
