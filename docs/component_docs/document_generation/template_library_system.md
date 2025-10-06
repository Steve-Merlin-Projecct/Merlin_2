# Template Library System

**Version**: 2.16.5  
**Implementation Date**: July 27, 2025  
**Status**: Production Ready with CSV Mapping Enhancement

## Overview

The Template Library System provides a comprehensive framework for managing and processing document templates with both traditional variable substitution and advanced CSV content mapping. This system enables dynamic document generation while preserving professional formatting and supporting intelligent content selection.

## System Architecture

### Directory Structure
```
content_template_library/
├── reference/                    # Original template files
├── resume/                      # Resume template variants
├── coverletter/                 # Cover letter templates
├── mapped_templates/            # CSV-processed templates
├── test_data/                   # Sample data for testing
└── backup/                      # Template backups
```

### Template Processing Pipeline

#### Traditional Template Processing
1. **Template Selection**: Choose appropriate template based on document type
2. **Variable Substitution**: Replace `<<variable_name>>` placeholders
3. **Format Preservation**: Maintain original document styling
4. **Document Generation**: Create final formatted document

#### CSV-Enhanced Processing
1. **CSV Mapping Load**: Parse transformation rules from CSV file
2. **Variable Categorization**: Organize variables by content type
3. **Template Transformation**: Apply mapping rules to original template
4. **Content Resolution**: Populate variables from multiple data sources
5. **Document Generation**: Create job-specific customized document

## Template Categories

### Resume Templates

#### Accessible-MCS-Resume-Template-Bullet-Points
**Source File**: `Accessible-MCS-Resume-Template-Bullet-Points_Variables_1.docx`
**CSV Mapping**: `Content mapping for template_1753649780614.csv`
**Status**: CSV Mapping Complete

**Template Features:**
- Harvard MCS professional format
- Bullet-point focused experience sections
- Clean, ATS-friendly layout
- Single-page optimized design

**CSV Mapping Results:**
- **35 Variables**: Dynamic content placeholders
- **7 Static Changes**: Professional text improvements
- **17 Discarded Items**: Removed instructional content
- **Processing**: 24 replacements, 9 static changes, 11 removals

**Variable Categories:**
- User Profile (6): Personal identification and contact
- Education (6): Academic background and credentials
- Work Experience (16): Professional history with skills
- Volunteer (5): Community involvement and leadership
- Skills (3): Technical, methodological, and domain expertise

### Cover Letter Templates
**Status**: Planned for future CSV mapping implementation
**Current**: Standard variable substitution available

### Reference Templates
**Status**: Available for standard template processing
**Features**: Contact information formatting, professional layout

## CSV Mapping Implementation

### Mapping File Specification

#### Required Columns
| Column | Type | Purpose | Example |
|--------|------|---------|---------|
| `Original_Text` | String | Text to be transformed | "FirstName" |
| `Is_Variable` | Boolean | Mark for variable substitution | TRUE |
| `Is_Static` | Boolean | Mark for static text replacement | FALSE |
| `Is_discarded` | Boolean | Mark for content removal | FALSE |
| `Variable_name` | String | Template variable identifier | "user_first_name" |
| `Variable intention` | String | Variable description | "user's first name" |
| `Static_Text` | String | Replacement text for static changes | "Education" |

#### Processing Rules
1. **Variable Priority**: Variables processed first
2. **Static Changes**: Applied after variable processing
3. **Content Removal**: Applied last to clean unwanted content
4. **Format Preservation**: Original styling maintained throughout

### Variable Resolution System

#### Data Source Hierarchy
1. **User Profile Data**: Primary source for personal information
2. **Content Manager Selections**: Job-specific skill descriptions
3. **Default Values**: Professional fallbacks for missing data
4. **Placeholder Text**: Clear indicators for unresolved variables

#### Category-Specific Resolution

##### User Profile Variables
```python
user_profile_mapping = {
    'user_first_name': user_profile.get('first_name', 'Steve'),
    'user_last_name': user_profile.get('last_name', 'Glen'),
    'user_email': user_profile.get('email', 'therealstevenglen@gmail.com'),
    'user_phone': user_profile.get('phone', '780-884-7038'),
    'user_city_prov': f"{user_profile.get('city', 'Edmonton')}, {user_profile.get('province', 'AB')}",
    'user_linkedin': 'linkedin.com/in/steve-glen'  # With tracking integration
}
```

##### Education Variables
```python
education_mapping = {
    'edu_1_name': education.get('institution', 'University of Alberta'),
    'edu_1_degree': education.get('degree_type', 'Bachelor'),
    'edu_1_concentration': education.get('field_of_study', 'Commerce'),
    'edu_1_specialization': education.get('specialization', 'Entrepreneurship, Strategy, Marketing'),
    'edu_1_location': f"{education.get('city', 'Edmonton')}, {education.get('province', 'AB')}",
    'edu_1_grad_date': str(education.get('graduation_year', '2018'))
}
```

##### Work Experience Variables
```python
work_experience_mapping = {
    'work_experience_1_name': experience[0].get('company', 'Odvod Media'),
    'work_experience_1_position': experience[0].get('position', 'Digital Strategist'),
    'work_experience_1_location': f"{experience[0].get('city', 'Edmonton')} {experience[0].get('province', 'AB')}",
    'work_experience_1_dates': f"{experience[0].get('start_year', '2020')} - {experience[0].get('end_year', 'current')}",
    'work_experience_1_skill1': content_selections.get('work_exp_1_skill_1', '[skill description]'),
    # ... additional skills and second work experience
}
```

##### Skills Variables
```python
skills_mapping = {
    'technical_summary': ', '.join(skills.get('technical', [
        'Microsoft Office Suite', 'Google Analytics', 'Adobe Creative Suite'
    ])),
    'methodology_summary': ', '.join(skills.get('methodologies', [
        'Agile', 'Scrum', 'Lean UX', 'Design Thinking'
    ])),
    'domain_summary': ', '.join(skills.get('domains', [
        'Digital Marketing', 'Content Strategy', 'Brand Management'
    ]))
}
```

## Quality Assurance Standards

### Content Quality Metrics
- **Action Verb Usage**: 100% of bullet points start with strong action verbs
- **Quantification**: Measurable results and achievements included
- **Professional Language**: Industry-appropriate terminology
- **Conciseness**: Optimal length for readability (average 116 characters)

### Technical Quality Standards
- **Format Preservation**: 100% original document styling maintained
- **Variable Resolution**: Complete data population with intelligent fallbacks
- **Error Handling**: Graceful processing of missing or invalid data
- **Performance**: Sub-second template processing times

### Testing Requirements
- **Template Validation**: Verify all variables resolve correctly
- **Format Verification**: Confirm original styling preservation
- **Content Quality**: Validate professional writing standards
- **Integration Testing**: End-to-end workflow validation

## Usage Examples

### Standard Template Usage
```python
from modules.content.document_generation.document_generator import DocumentGenerator

doc_gen = DocumentGenerator()
result = doc_gen.generate_document(
    data=user_data,
    document_type='resume',
    template_name='harvard_bullet_points'
)
```

### CSV-Mapped Template Usage
```python
result = doc_gen.generate_document_with_csv_mapping(
    data={
        'user_profile': user_data,
        'job_data': job_requirements,
        'content_selections': skill_descriptions
    },
    document_type='resume',
    csv_mapping_path='attached_assets/Content mapping for template.csv'
)
```

### Template Processing Statistics
```python
mapper = CSVContentMapper()
mapping = mapper.load_mapping_from_csv(csv_path)
summary = mapper.get_mapping_summary(mapping)

print(f"Variables: {summary['total_variables']}")
print(f"Static changes: {summary['static_changes']}")
print(f"Discarded items: {summary['discarded_items']}")
```

## Integration Points

### Document Generation System
- **Primary Interface**: DocumentGenerator class with CSV mapping support
- **Template Engine**: Underlying processing engine for variable substitution
- **Storage Integration**: Cloud and local storage for template and output files

### Content Management System
- **Skill Selection**: Dynamic content based on job requirements
- **Quality Standards**: Professional writing standards enforcement
- **Content Categorization**: Organized content for targeted insertion

### User Profile System
- **Personal Data**: Contact information and identification
- **Professional History**: Work experience and education background
- **Skills Database**: Technical competencies and methodologies

### Email Application System
- **Document Attachment**: Generated resumes attached to job applications
- **Workflow Integration**: Seamless document creation within application process
- **Tracking Integration**: Document generation logged with application attempts

## Maintenance and Updates

### Template Management
- **Version Control**: Track template changes and updates
- **Backup Systems**: Preserve original templates before modifications
- **Validation Tools**: Verify template integrity after changes
- **Documentation Updates**: Maintain current usage instructions

### CSV Mapping Maintenance
- **Mapping Validation**: Ensure CSV files match template requirements
- **Variable Verification**: Confirm all variables resolve correctly
- **Content Quality Review**: Regular assessment of generated content
- **Performance Monitoring**: Track processing times and resource usage

### System Updates
- **Dependency Management**: Keep python-docx and related libraries current
- **Security Updates**: Apply security patches and vulnerability fixes
- **Performance Optimization**: Improve processing speed and memory usage
- **Feature Enhancements**: Add new capabilities based on user needs

## Future Enhancements

### Planned Developments
1. **Multi-Template CSV Mapping**: Extend CSV system to cover letters and other documents
2. **AI Content Enhancement**: Intelligent content optimization based on job requirements
3. **Dynamic Formatting**: Conditional styling based on content length and type
4. **Real-Time Preview**: Live document preview during template editing

### System Expansions
- **Industry Templates**: Sector-specific resume and cover letter variants
- **International Support**: Multi-language template processing
- **Collaborative Features**: Multi-user template development and sharing
- **Advanced Analytics**: Template usage statistics and effectiveness metrics

## Related Documentation

- [CSV Content Mapping System](csv_content_mapping.md)
- [Document Generation Architecture](document_generation_architecture.md)
- [Resume Template Transformation Project](../../project_docs/resume_template_transformation.md)
- [Content Manager Integration](../content_management/content_manager.md)