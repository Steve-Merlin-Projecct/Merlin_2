#!/usr/bin/env python3
"""
Template 5 Converter - Office Manager Template
Converts hardcoded content to variable-based template.
"""

import zipfile
import shutil
from lxml import etree
import os


def convert_template_5():
    """
    Convert Template 5 from hardcoded values to variables.

    Template 5 is an Office Manager resume with:
    - Contact information
    - Objective section
    - Work experience (3 jobs)
    - Education
    - Skills
    - Interests
    """

    source_path = "/workspace/.trees/convert-raw-template-files-into-ready-for-producti/content_template_library/manual_converted/template_5_source.docx"
    output_path = "/workspace/.trees/convert-raw-template-files-into-ready-for-producti/content_template_library/manual_converted/template_5_converted.docx"

    # Create a copy to work with
    shutil.copy(source_path, output_path)

    # Define replacements based on the content found
    # Following the guide: Replace EVERYTHING that could vary between users
    replacements = []

    # Header/Title
    replacements.append(('Office Manager ', '<<position_title>>'))  # Note the trailing space

    # Contact Information
    replacements.append(('Chanchal Sharma', '<<first_name>> <<last_name>>'))

    # Section Headers
    replacements.append(('Objective', '<<objective_header>>'))
    replacements.append(('Experience', '<<experience_header>>'))
    replacements.append(('Education', '<<education_header>>'))
    replacements.append(('Skills', '<<skills_header>>'))
    replacements.append(('Interests', '<<interests_header>>'))
    replacements.append(('Contact', '<<contact_header>>'))

    # Objective section text
    objective_text = ('State your career goals and show how they align with the job description you\'re targeting. '
                     'Be brief and keep it from sounding generic. Be yourself.')
    replacements.append((objective_text, '<<career_overview_1>>'))

    # Job 1 - The Phone Company
    replacements.append(('The Phone Company', '<<company_1>>'))
    job1_exp = ('Summarize your key responsibilities and accomplishments. Where appropriate, use the language '
               'and words you find in the specific job description. Be concise, targeting 3-5 key areas.')
    replacements.append((job1_exp, '<<job_1_experience_1>>'))

    # Job 2 - Nod Publishing
    replacements.append(('Nod Publishing', '<<company_2>>'))
    job2_exp = ('Summarize your key responsibilities and accomplishments. Here again, take any opportunity to '
               'use words you find in the job description. Be brief.')
    replacements.append((job2_exp, '<<job_2_experience_1>>'))

    # Job 3 - Southridge Video
    replacements.append(('Southridge Video', '<<company_3>>'))
    job3_exp = ('Summarize your key responsibilities and accomplishments. Where appropriate, use the language '
               'and words you find in the job description. Be concise, targeting 3-5 key areas.')
    replacements.append((job3_exp, '<<job_3_experience_1>>'))

    # Education
    replacements.append(('A.S. H.R. Management', '<<degree_1>>'))
    replacements.append(('Glennwood University', '<<institution_1>>'))

    # Skills (5 skills)
    replacements.append(('Data analysis', '<<skill_1>>'))
    replacements.append(('Project management', '<<skill_2>>'))
    replacements.append(('Communication', '<<skill_3>>'))
    replacements.append(('Organization', '<<skill_4>>'))
    replacements.append(('Problem solving', '<<skill_5>>'))

    # Interests section text
    interests_text = 'This section is optional but can showcase the unique, intriguing, even fun side of who you are.'
    replacements.append((interests_text, '<<interest_1>>'))

    # Open and modify the document XML
    with zipfile.ZipFile(output_path, 'r') as zip_ref:
        # Extract to temp directory
        temp_dir = '/tmp/template_5_temp'
        os.makedirs(temp_dir, exist_ok=True)
        zip_ref.extractall(temp_dir)

    # Read and modify document.xml
    doc_xml_path = os.path.join(temp_dir, 'word/document.xml')
    with open(doc_xml_path, 'rb') as f:
        xml_content = f.read()

    # Convert to string for replacements
    xml_str = xml_content.decode('utf-8')

    # Apply standard replacements
    for old, new in replacements:
        xml_str = xml_str.replace(old, new)

    # Special handling for "Office Manager" which appears 4 times:
    # 1st: Title/header at top (already replaced with <<position_title>>)
    # 2nd: Job 1 position
    # 3rd: Job 2 position
    # 4th: Job 3 position
    # We need to replace the remaining 3 occurrences
    parts = xml_str.split('Office Manager', 3)
    if len(parts) >= 4:
        xml_str = parts[0] + 'Office Manager' + parts[1] + '<<position_1>>' + parts[2] + '<<position_2>>' + parts[3]
        # Now handle the 4th occurrence
        remaining_parts = xml_str.split('Office Manager', 1)
        if len(remaining_parts) >= 2:
            xml_str = remaining_parts[0] + '<<position_3>>' + remaining_parts[1]
    elif len(parts) == 3:
        xml_str = parts[0] + 'Office Manager' + parts[1] + '<<position_1>>' + parts[2]

    # Handle date patterns for Job 1
    xml_str = xml_str.replace('January 20XX - Current', '<<start_date_1>> - <<end_date_1>>')

    # Handle date patterns for Job 2
    xml_str = xml_str.replace('March 20XX - December 20XX', '<<start_date_2>> - <<end_date_2>>')

    # Handle date patterns for Job 3
    xml_str = xml_str.replace('August 20XX - March 20XX', '<<start_date_3>> - <<end_date_3>>')

    # Handle education dates
    xml_str = xml_str.replace('Sept 20XX - May 20XX', '<<start_date_education_1>> - <<graduation_date_1>>')

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

    # Clean up temp directory
    shutil.rmtree(temp_dir)

    print("✅ Template 5 converted successfully!")
    print(f"   Output: {output_path}")

    # Return variable list for documentation
    variables = {
        'Header/Title': [
            '<<position_title>>'
        ],
        'Contact Information': [
            '<<first_name>>',
            '<<last_name>>',
            '<<contact_header>>'
        ],
        'Section Headers': [
            '<<objective_header>>',
            '<<experience_header>>',
            '<<education_header>>',
            '<<skills_header>>',
            '<<interests_header>>'
        ],
        'Objective Section': [
            '<<career_overview_1>>'
        ],
        'Job 1 (The Phone Company)': [
            '<<position_1>>',
            '<<company_1>>',
            '<<start_date_1>>',
            '<<end_date_1>>',
            '<<job_1_experience_1>>'
        ],
        'Job 2 (Nod Publishing)': [
            '<<position_2>>',
            '<<company_2>>',
            '<<start_date_2>>',
            '<<end_date_2>>',
            '<<job_2_experience_1>>'
        ],
        'Job 3 (Southridge Video)': [
            '<<position_3>>',
            '<<company_3>>',
            '<<start_date_3>>',
            '<<end_date_3>>',
            '<<job_3_experience_1>>'
        ],
        'Education': [
            '<<degree_1>>',
            '<<institution_1>>',
            '<<start_date_education_1>>',
            '<<graduation_date_1>>'
        ],
        'Skills': [
            '<<skill_1>>',
            '<<skill_2>>',
            '<<skill_3>>',
            '<<skill_4>>',
            '<<skill_5>>'
        ],
        'Interests': [
            '<<interest_1>>'
        ]
    }

    return variables


if __name__ == "__main__":
    variables = convert_template_5()

    print("\n" + "="*80)
    print("TEMPLATE 5 VARIABLE SUMMARY")
    print("="*80 + "\n")

    total = 0
    for section, vars_list in variables.items():
        print(f"{section}:")
        for var in vars_list:
            print(f"  {var}")
        print(f"  Subtotal: {len(vars_list)}\n")
        total += len(vars_list)

    print(f"TOTAL VARIABLES: {total}")
