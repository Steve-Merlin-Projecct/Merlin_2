# Variable Naming - Quick Start Guide

**Status:** ✅ Harmonized to unified CSV naming standard
**Last Updated:** 2025-10-24

## TL;DR

All variables now use the **CSV naming convention**. Templates and CSV mappings are perfectly synchronized.

**Quick Reference:**
- Personal: `user_first_name`, `user_email`, `user_phone`
- Work: `work_experience_1_position`, `work_experience_1_skill1`
- Education: `edu_1_degree`, `edu_1_name`
- Cover Letter: `cover_letter_opening`, `hiring_manager_name`

**Full Reference:** See [`VARIABLE_NAMING_REFERENCE.md`](./VARIABLE_NAMING_REFERENCE.md)

## Usage Examples

### Resume Variables
```python
data = {
    'user_first_name': 'John',
    'user_last_name': 'Doe',
    'user_email': 'john.doe@example.com',
    'user_phone': '555-1234',
    'user_linkedin': 'linkedin.com/in/johndoe',
    'user_city_prov': 'Toronto, ON',

    'professional_summary': 'Experienced software engineer with...',
    'technical_summary': 'Python, JavaScript, React, Docker',
    'methodology_summary': 'Agile, Scrum, CI/CD',
    'domain_summary': 'Web Development, Cloud Architecture',

    'edu_1_name': 'University of Toronto',
    'edu_1_degree': 'Bachelor of Science',
    'edu_1_concentration': 'Computer Science',
    'edu_1_grad_date': 'May 2020',

    'work_experience_1_position': 'Senior Software Engineer',
    'work_experience_1_name': 'Tech Corp',
    'work_experience_1_location': 'Toronto, ON',
    'work_experience_1_dates': 'Jan 2020 - Present',
    'work_experience_1_skill1': 'Led team of 5 developers on microservices project',
    'work_experience_1_skill2': 'Increased system performance by 40%',
    'work_experience_1_skill3': 'Implemented CI/CD pipeline reducing deployment time by 60%',

    'certifications_list': 'AWS Solutions Architect, PMP',
}
```

### Cover Letter Variables
```python
data = {
    'user_first_name': 'John',
    'user_last_name': 'Doe',
    'user_email': 'john.doe@example.com',
    'user_phone': '555-1234',
    'user_linkedin': 'linkedin.com/in/johndoe',

    'company_name': 'Innovative Tech Inc.',
    'hiring_manager_name': 'Jane Smith',
    'current_date': '2025-10-24',

    'cover_letter_opening': 'I am excited to apply for the Senior Engineer position...',
    'cover_letter_skills_alignment': 'My experience with cloud architecture...',
    'cover_letter_achievement': 'In my current role, I led a team that...',
    'cover_letter_closing': 'I look forward to discussing how my expertise...',
}
```

### Template Usage
In your .docx template:
```
<<user_first_name>> <<user_last_name>>
<<user_email>> | <<user_phone>> | <<user_linkedin>>
<<user_city_prov>>

PROFESSIONAL SUMMARY
<<professional_summary>>

TECHNICAL SKILLS
<<technical_summary>>

WORK EXPERIENCE
<<work_experience_1_position>> | <<work_experience_1_name>> | <<work_experience_1_dates>>
<<work_experience_1_location>>
• <<work_experience_1_skill1>>
• <<work_experience_1_skill2>>
```

## Naming Patterns

### Simple Variables
```
user_first_name          # Personal info
professional_summary     # Profile summary
certifications_list      # List of certs
```

### Numbered Variables (Multiple Items)
```
edu_1_degree            # First education entry
edu_2_degree            # Second education entry
work_experience_1_name  # First job company
work_experience_2_name  # Second job company
```

### Multi-Numbered Variables (Nested Items)
```
work_experience_1_skill1   # First achievement at first job
work_experience_1_skill2   # Second achievement at first job
work_experience_2_skill1   # First achievement at second job
```

## Template-Specific Variables

Some templates have specialized variables:

### Executive Leadership Resume
```python
'executive_summary': 'C-level executive with...',
'executive_title': 'Chief Technology Officer',
'leadership_competency_1': 'Strategic Planning',
'leadership_competency_2': 'Team Building',
```

### Tech Creative Resume
```python
'tech_specialty': 'Full-Stack Development',
'user_github': 'github.com/johndoe',
'user_portfolio': 'johndoe.dev',
'work_experience_1_tech_stack': 'React, Node.js, PostgreSQL, AWS',
```

### T-Format Cover Letter
```python
'job_requirement_1': '5+ years Python experience',
'matching_qualification_1': 'I have 7 years of Python development...',
'job_requirement_2': 'Leadership experience',
'matching_qualification_2': 'Led team of 5 developers...',
```

## Validation

Run validation tests:
```bash
python3 test_variable_harmonization.py
```

Expected output:
```
✅ All templates perfectly synchronized with CSV mappings!
✅ Variable naming harmonization is COMPLETE.
✅ System ready for production use
```

## Tools & Scripts

### Analysis Tool
```bash
python3 harmonize_variable_names.py
```
Analyzes templates and CSV mappings, identifies inconsistencies.

### Update Tool
```bash
python3 update_csv_mappings.py
```
Updates CSV mappings to match template variables.

### Validation Test
```bash
python3 test_variable_harmonization.py
```
Validates synchronization and naming conventions.

## Common Tasks

### Adding a New Variable

1. **Add to template** (.docx file):
   ```
   <<new_variable_name>>
   ```

2. **Update CSV mapping** (run update tool):
   ```bash
   python3 update_csv_mappings.py
   ```

3. **Validate**:
   ```bash
   python3 test_variable_harmonization.py
   ```

### Adding a New Template

1. **Create template** with <<variable_name>> placeholders
2. **Generate CSV mapping**:
   ```bash
   python3 update_csv_mappings.py
   ```
3. **Verify** the mapping file was created and matches template variables

### Checking Variable Names

Use the reference:
- **Quick reference:** This file (common variables)
- **Complete reference:** `VARIABLE_NAMING_REFERENCE.md` (all 65 variables)

## Best Practices

### ✅ DO:
- Use exact variable names from reference docs
- Follow snake_case naming
- Use numbered patterns for multiple items (1, 2, 3...)
- Keep variable names descriptive
- Validate after changes

### ❌ DON'T:
- Create custom variable names
- Mix naming conventions
- Use camelCase or PascalCase
- Skip numbers in sequences
- Modify templates without updating CSVs

## Documentation

| Document | Purpose |
|----------|---------|
| `VARIABLE_NAMING_QUICKSTART.md` | This file - quick reference |
| `VARIABLE_NAMING_REFERENCE.md` | Complete authoritative reference (all 86 variables) |
| `HARMONIZATION_SUMMARY_REPORT.md` | Full harmonization project summary |
| `VARIABLE_NAMING_ANALYSIS.md` | Technical analysis report |

## Support

**Questions?**
- Check `VARIABLE_NAMING_REFERENCE.md` for complete variable list
- Review `HARMONIZATION_SUMMARY_REPORT.md` for project details
- Run validation tests to verify your changes

**Making Changes?**
- Always validate after modifications
- Keep templates and CSV mappings synchronized
- Follow the CSV naming convention
- Document template-specific variables

---

**Status:** ✅ System harmonized and production-ready
**Last Validated:** 2025-10-24
