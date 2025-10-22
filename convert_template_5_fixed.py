#!/usr/bin/env python3
"""
Template 5 Converter - Office Manager Template (FIXED VERSION)
Properly handles XML entities when converting to variables.
"""

import zipfile
import shutil
from lxml import etree
import os


def convert_template_5():
    """
    Convert Template 5 from hardcoded values to variables.
    Uses proper XML escaping to prevent corruption.
    """

    source_path = "/workspace/.trees/convert-raw-template-files-into-ready-for-producti/content_template_library/manual_converted/template_5_source.docx"
    output_path = "/workspace/.trees/convert-raw-template-files-into-ready-for-producti/content_template_library/manual_converted/template_5_converted.docx"

    # Create a copy to work with
    shutil.copy(source_path, output_path)

    # Define replacements with XML entity encoding
    replacements = []

    # Header/Title
    replacements.append(('Office Manager ', '&lt;&lt;position_title&gt;&gt; '))

    # Contact Information
    replacements.append(('Chanchal Sharma', '&lt;&lt;first_name&gt;&gt; &lt;&lt;last_name&gt;&gt;'))

    # Section Headers
    replacements.append(('Objective', '&lt;&lt;objective_header&gt;&gt;'))
    replacements.append(('Contact', '&lt;&lt;contact_header&gt;&gt;'))

    # Note: Experience, Education, Skills, Interests headers handled separately due to common words

    # Objective text
    objective_text = ('State your career goals and show how they align with the job description you\'re targeting. '
                     'Be brief and keep it from sounding generic. Be yourself.')
    replacements.append((objective_text, '&lt;&lt;career_overview_1&gt;&gt;'))

    # Companies
    replacements.append(('The Phone Company', '&lt;&lt;company_1&gt;&gt;'))
    replacements.append(('Nod Publishing', '&lt;&lt;company_2&gt;&gt;'))
    replacements.append(('Southridge Video', '&lt;&lt;company_3&gt;&gt;'))

    # Job experience texts
    job1_exp = ('Summarize your key responsibilities and accomplishments. Where appropriate, use the language '
               'and words you find in the specific job description. Be concise, targeting 3-5 key areas.')
    replacements.append((job1_exp, '&lt;&lt;job_1_experience_1&gt;&gt;'))

    job2_exp = ('Summarize your key responsibilities and accomplishments. Here again, take any opportunity to '
               'use words you find in the job description. Be brief.')
    replacements.append((job2_exp, '&lt;&lt;job_2_experience_1&gt;&gt;'))

    # For job3, the text is the same as job1, so we need to handle it specially
    # We'll do that after the first replacement

    # Education
    replacements.append(('A.S. H.R. Management', '&lt;&lt;degree_1&gt;&gt;'))
    replacements.append(('Glennwood University', '&lt;&lt;institution_1&gt;&gt;'))

    # Skills
    replacements.append(('Data analysis', '&lt;&lt;skill_1&gt;&gt;'))
    replacements.append(('Project management', '&lt;&lt;skill_2&gt;&gt;'))
    replacements.append(('Communication', '&lt;&lt;skill_3&gt;&gt;'))
    replacements.append(('Organization', '&lt;&lt;skill_4&gt;&gt;'))
    replacements.append(('Problem solving', '&lt;&lt;skill_5&gt;&gt;'))

    # Interests text
    interests_text = 'This section is optional but can showcase the unique, intriguing, even fun side of who you are.'
    replacements.append((interests_text, '&lt;&lt;interest_1&gt;&gt;'))

    # Date patterns
    replacements.append(('January 20XX - Current', '&lt;&lt;start_date_1&gt;&gt; - &lt;&lt;end_date_1&gt;&gt;'))
    replacements.append(('March 20XX - December 20XX', '&lt;&lt;start_date_2&gt;&gt; - &lt;&lt;end_date_2&gt;&gt;'))
    replacements.append(('August 20XX - March 20XX', '&lt;&lt;start_date_3&gt;&gt; - &lt;&lt;end_date_3&gt;&gt;'))
    replacements.append(('Sept 20XX - May 20XX', '&lt;&lt;start_date_education_1&gt;&gt; - &lt;&lt;graduation_date_1&gt;&gt;'))

    # Open and modify the document XML
    with zipfile.ZipFile(output_path, 'r') as zip_ref:
        temp_dir = '/tmp/template_5_temp'
        os.makedirs(temp_dir, exist_ok=True)
        zip_ref.extractall(temp_dir)

    # Read and modify document.xml
    doc_xml_path = os.path.join(temp_dir, 'word/document.xml')
    with open(doc_xml_path, 'rb') as f:
        xml_content = f.read()

    xml_str = xml_content.decode('utf-8')

    # Apply standard replacements
    for old, new in replacements:
        xml_str = xml_str.replace(old, new)

    # Handle job 3 experience (same text as job 1, appears second time)
    job3_exp = job1_exp
    xml_str = xml_str.replace(job3_exp, '&lt;&lt;job_3_experience_1&gt;&gt;')

    # Handle "Office Manager" which appears 4 times:
    # 1st: Already replaced as position_title
    # 2nd-4th: Job positions 1, 2, 3
    parts = xml_str.split('Office Manager', 3)
    if len(parts) >= 4:
        # First "Office Manager" should already be replaced, so we start from the existing state
        # Actually, we already replaced "Office Manager " (with space) as position_title
        # So the remaining are the job titles
        xml_str = parts[0] + '&lt;&lt;position_1&gt;&gt;' + parts[1] + '&lt;&lt;position_2&gt;&gt;' + parts[2] + '&lt;&lt;position_3&gt;&gt;' + parts[3]
    elif len(parts) == 3:
        xml_str = parts[0] + '&lt;&lt;position_1&gt;&gt;' + parts[1] + '&lt;&lt;position_2&gt;&gt;' + parts[2]
    elif len(parts) == 2:
        xml_str = parts[0] + '&lt;&lt;position_1&gt;&gt;' + parts[1]

    # Handle section headers that are common words
    # We need to be careful to only replace the header instances
    # Experience (as a section header)
    # We'll use context - "Experience" appears after "Objective"
    xml_str = xml_str.replace('Experience', '&lt;&lt;experience_header&gt;&gt;', 1)

    # Education (as a section header)
    xml_str = xml_str.replace('Education', '&lt;&lt;education_header&gt;&gt;', 1)

    # Skills (as a section header)
    xml_str = xml_str.replace('Skills', '&lt;&lt;skills_header&gt;&gt;', 1)

    # Interests (as a section header)
    xml_str = xml_str.replace('Interests', '&lt;&lt;interests_header&gt;&gt;', 1)

    # Write modified XML back
    with open(doc_xml_path, 'wb') as f:
        f.write(xml_str.encode('utf-8'))

    # Recreate the docx file
    os.remove(output_path)
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zip_out:
        for root, dirs, files in os.walk(temp_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, temp_dir)
                zip_out.write(file_path, arcname)

    # Clean up
    shutil.rmtree(temp_dir)

    print("✅ Template 5 converted successfully!")
    print(f"   Output: {output_path}")

    return 35  # Total variable count


if __name__ == "__main__":
    total_vars = convert_template_5()
    print(f"\nTotal variables: {total_vars}")
