# Simplified Template Variables

All templates use unified, simplified variable naming.

## Key Simplifications

- **Work Experience**: All bullets use `<<job_X_experience_Y>>` format
- **No distinction** between responsibilities and achievements
- **Sequential numbering**: Experience bullets numbered 1, 2, 3, etc.

## Summary

| Template | Variables | File |
|----------|-----------|------|
| Restaurant Manager | 43 | restaurant_manager_final.docx |
| Accountant | 29 | accountant_final.docx |
| Uiux Designer | 20 | uiux_designer_final.docx |

## Restaurant Manager

### Contact
- `<<city>>`
- `<<email>>`
- `<<first_name>>`
- `<<institution_city_1>>`
- `<<institution_state_1>>`
- `<<last_name>>`
- `<<linkedin_url>>`
- `<<phone>>`
- `<<state>>`
- `<<street_address>>`
- `<<zip_code>>`

### Career Overview / Summary
- `<<career_overview_1>>`
- `<<career_overview_2>>`
- `<<career_overview_3>>`
- `<<career_overview_4>>`
- `<<career_overview_5>>`

### Work Experience
- `<<company_2>>`
- `<<end_date_1>>`
- `<<job_1_experience_1>>`
- `<<job_1_experience_2>>`
- `<<job_1_experience_3>>`
- `<<job_2_experience_1>>`
- `<<job_2_experience_3>>`
- `<<job_2_experience_4>>`
- `<<position_1>>`

### Education
- `<<institution_1>>`

### Skills
- `<<skill_1>>`
- `<<skill_2>>`
- `<<skill_3>>`
- `<<skill_4>>`
- `<<skill_5>>`
- `<<skill_6>>`
- `<<skills_header>>`

### Interests
- `<<interest_1>>`
- `<<interest_2>>`
- `<<interest_3>>`
- `<<interest_4>>`
- `<<interest_5>>`
- `<<interest_6>>`
- `<<interests_header>>`

### Headers
- `<<education_header>>`
- `<<experience_header>>`
- `<<profile_header>>`


## Accountant

### Contact
- `<<city>>`
- `<<email>>`
- `<<first_name>>`
- `<<job_city_1>>`
- `<<job_state_1>>`
- `<<last_name>>`
- `<<linkedin_url>>`
- `<<phone>>`
- `<<state>>`
- `<<zip_code>>`

### Career Overview / Summary
- `<<professional_summary_1>>`
- `<<professional_summary_2>>`

### Work Experience
- `<<company_1>>`
- `<<end_date_1>>`
- `<<position_1>>`

### Education
- `<<degree_1>>`
- `<<degree_label>>`
- `<<graduation_date_1>>`
- `<<institution_1>>`
- `<<minor_1>>`

### Skills
- `<<skill_1>>`
- `<<skill_2>>`
- `<<skill_3>>`
- `<<skill_4>>`
- `<<skill_5>>`
- `<<skill_6>>`
- `<<skills_header>>`

### Headers
- `<<education_header>>`
- `<<experience_header>>`


## Uiux Designer

### Contact
- `<<city>>`
- `<<email>>`
- `<<first_name>>`
- `<<last_name>>`
- `<<phone>>`

### Work Experience
- `<<company_1>>`
- `<<position_2>>`

### Education
- `<<degree_1>>`
- `<<graduation_year_1>>`
- `<<institution_1>>`
- `<<major_1>>`

### Skills
- `<<skill_2>>`
- `<<skill_3>>`
- `<<skill_4>>`
- `<<skills_header>>`

### Headers
- `<<contact_header>>`
- `<<education_header>>`
- `<<experience_header>>`


## Example: Work Experience Variables

```json
{
  "job_1_experience_1": "Led team of 40 staff members across operations",
  "job_1_experience_2": "Reduced costs by 15% through strategic planning",
  "job_1_experience_3": "Increased customer satisfaction from 4.2 to 4.8 stars",
  
  "job_2_experience_1": "Implemented training program for new hires",
  "job_2_experience_2": "Grew social media following by 45%",
  "job_2_experience_3": "Achieved highest inspection score in district"
}
```

**Note**: No distinction between responsibilities and achievements - all come from the same source.
