# Jinja Template Directory

This directory contains Word document templates used for generating resumes and cover letters.

## Directory Structure

```
jinja_templates/
├── resume/
│   └── *.docx templates for resume generation
└── cover_letter/
    └── *.docx templates for cover letter generation
```

## Template Format

Templates should be Microsoft Word (.docx) files with Jinja2 template syntax for variable substitution.

### Example Template Variables

**Resume Templates:**
- `{{ name }}`
- `{{ email }}`
- `{{ phone }}`
- `{{ skills }}`
- `{{ experience }}`
- `{{ education }}`

**Cover Letter Templates:**
- `{{ name }}`
- `{{ company_name }}`
- `{{ position }}`
- `{{ body_paragraphs }}`
- `{{ signature }}`

## Current Status

⚠️ **Template files are not included in version control.**

The actual .docx template files should be:
1. Created using Microsoft Word or compatible editor
2. Saved with Jinja2 template syntax for variables
3. Placed in the appropriate subdirectory (resume/ or cover_letter/)
4. Referenced in the document generation code

## Expected Template

Based on code analysis, the system expects:
- Resume template: `Accessible-MCS-Resume-Template-Bullet-Points_*.docx`

## Next Steps

1. Create or obtain Word document templates
2. Add Jinja2 variable placeholders
3. Place files in appropriate directories
4. Test document generation
5. Update this README with template inventory
