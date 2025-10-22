#!/usr/bin/env python3
"""
Template 4 Converter - Assistant Hotel Manager Template
Converts hardcoded content to variable-based template.
"""

import zipfile
import shutil
from lxml import etree
import os


def convert_template_4():
    """
    Convert Template 4 from hardcoded values to variables.

    Template 4 is an Assistant Hotel Manager resume with:
    - Contact information
    - Profile section
    - Work experience (2 jobs)
    - Education
    - Skills
    - Activities/Interests
    """

    source_path = "/workspace/.trees/convert-raw-template-files-into-ready-for-producti/content_template_library/manual_converted/template_4_source.docx"
    output_path = "/workspace/.trees/convert-raw-template-files-into-ready-for-producti/content_template_library/manual_converted/template_4_converted.docx"

    # Create a copy to work with
    shutil.copy(source_path, output_path)

    # Define replacements based on the content found
    # Following the guide: Replace EVERYTHING that could vary between users
    replacements = []

    # Contact Information
    replacements.append(('716-555-0100', '<<phone>>'))
    replacements.append(('www.interestingsite.com', '<<website>>'))
    replacements.append(('lisandro@example.com', '<<email>>'))
    replacements.append(('Lisandro Milanesi', '<<first_name>> <<last_name>>'))

    # Profile Section - Full paragraph
    profile_text = ('Assistant Hotel Manager with a warm and friendly demeanor. Skilled at conflict resolution. '
                   'Team builder who is acutely attentive to employee and guest needs. Punctual problem solver and '
                   'avid multitasker. Track record of being an essential part of the management team and instrumental '
                   'in providing effective solutions that produce immediate impact and contribute to the establishment\'s '
                   'long-term success.')
    replacements.append((profile_text, '<<career_overview_1>>'))

    # Section Headers (make them variables for flexibility)
    replacements.append(('Profile', '<<profile_header>>'))
    replacements.append(('WORK EXPERIENCE', '<<experience_header>>'))
    replacements.append(('Activities and interests', '<<interests_header>>'))
    replacements.append(('Key skills', '<<skills_header>>'))
    replacements.append(('education', '<<education_header>>'))

    # Job 1 experience text
    job1_exp = ('Supervise hotel staff. Improve staff performance through training, attention to detail, '
               'and empathetic problem-solving methods. Assist with the preparation of staff assessments. '
               'Resolve staff and guest conflicts in a professional and courteous manner. Inventory and order '
               'business supplies. Responsible for guest billing and settling payment disputes. Admin tasks as '
               'needed including bookings, check-ins, answering phones, responding to email, and social media inquiries.')
    replacements.append((job1_exp, '<<job_1_experience_1>>'))

    # Job 2 experience text
    job2_exp = ('Supervised and trained hotel staff and resolved staff conflicts. Daily financial reporting. '
               'In charge of guest database and stays schedule. Point person for corporate client relations and '
               'reviewing guest feedback posted online. Worked with marketing team on campaign to increase guest '
               'bookings. Assisted accountant with accounting tasks. Handled in-person guest complaints.')
    replacements.append((job2_exp, '<<job_2_experience_1>>'))

    # Job 1 - The Rosehip Hotel
    replacements.append(('The Rosehip Hotel', '<<company_1>>'))
    replacements.append(('20XX – Present', '<<start_date_1>> – <<end_date_1>>'))

    # Job 2 - The Seattle Sea Home
    replacements.append(('The Seattle Sea Home', '<<company_2>>'))

    # Skills (8 skills)
    replacements.append(('Budget management', '<<skill_1>>'))
    replacements.append(('Excellent listener', '<<skill_2>>'))
    replacements.append(('Friendly, courteous, & service oriented', '<<skill_3>>'))
    replacements.append(('Poised under pressure', '<<skill_4>>'))
    replacements.append(('Staff training & coaching', '<<skill_5>>'))
    replacements.append(('Recruiting & hiring talent', '<<skill_6>>'))
    replacements.append(('Quality assurance', '<<skill_7>>'))
    replacements.append(('Solid written & verbal communicator', '<<skill_8>>'))

    # Interests (7 interests)
    replacements.append(('Surfing', '<<interest_1>>'))
    replacements.append(('Scuba diving', '<<interest_2>>'))
    replacements.append(('Snorkeling', '<<interest_3>>'))
    replacements.append(('Craft beer', '<<interest_4>>'))
    replacements.append(('Travel', '<<interest_5>>'))
    replacements.append(('Great food', '<<interest_6>>'))
    replacements.append(('Food Pantry Volunteer', '<<interest_7>>'))

    # Education
    replacements.append(('Bachelor of Science in Hospitality Management', '<<degree_1>>'))
    replacements.append(('Bellows College', '<<institution_1>>'))

    # Open and modify the document XML
    with zipfile.ZipFile(output_path, 'r') as zip_ref:
        # Extract to temp directory
        temp_dir = '/tmp/template_4_temp'
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

    # Special handling for "Assistant Hotel Manager" which appears twice
    # First occurrence: position_1 (Job 1)
    # Second occurrence: position_2 (Job 2)
    parts = xml_str.split('Assistant Hotel Manager', 2)
    if len(parts) >= 3:
        xml_str = parts[0] + '<<position_1>>' + parts[1] + '<<position_2>>' + parts[2]
    elif len(parts) == 2:
        xml_str = parts[0] + '<<position_1>>' + parts[1]

    # Special handling for "Seattle, WA" which appears twice
    # First occurrence: job 1 location
    # Second occurrence: job 2 location
    parts = xml_str.split('Seattle, WA', 2)
    if len(parts) >= 3:
        xml_str = parts[0] + '<<job_city_1>>, <<job_state_1>>' + parts[1] + '<<job_city_2>>, <<job_state_2>>' + parts[2]
    elif len(parts) == 2:
        xml_str = parts[0] + '<<job_city_1>>, <<job_state_1>>' + parts[1]

    # Special handling for "20XX" dates in Job 2 (appears as "20XX – 20XX")
    # We need to handle the date pattern for job 2
    xml_str = xml_str.replace('20XX – 20XX', '<<start_date_2>> – <<end_date_2>>')

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

    print("✅ Template 4 converted successfully!")
    print(f"   Output: {output_path}")

    # Return variable list for documentation
    variables = {
        'Contact Information': [
            '<<first_name>>',
            '<<last_name>>',
            '<<phone>>',
            '<<email>>',
            '<<website>>'
        ],
        'Section Headers': [
            '<<profile_header>>',
            '<<experience_header>>',
            '<<education_header>>',
            '<<skills_header>>',
            '<<interests_header>>'
        ],
        'Profile Section': [
            '<<career_overview_1>>'
        ],
        'Job 1 (The Rosehip Hotel)': [
            '<<position_1>>',
            '<<company_1>>',
            '<<job_city_1>>',
            '<<job_state_1>>',
            '<<start_date_1>>',
            '<<end_date_1>>',
            '<<job_1_experience_1>>'
        ],
        'Job 2 (The Seattle Sea Home)': [
            '<<position_2>>',
            '<<company_2>>',
            '<<job_city_2>>',
            '<<job_state_2>>',
            '<<start_date_2>>',
            '<<end_date_2>>',
            '<<job_2_experience_1>>'
        ],
        'Education': [
            '<<degree_1>>',
            '<<institution_1>>'
        ],
        'Skills': [
            '<<skill_1>>',
            '<<skill_2>>',
            '<<skill_3>>',
            '<<skill_4>>',
            '<<skill_5>>',
            '<<skill_6>>',
            '<<skill_7>>',
            '<<skill_8>>'
        ],
        'Interests': [
            '<<interest_1>>',
            '<<interest_2>>',
            '<<interest_3>>',
            '<<interest_4>>',
            '<<interest_5>>',
            '<<interest_6>>',
            '<<interest_7>>'
        ]
    }

    return variables


if __name__ == "__main__":
    variables = convert_template_4()

    print("\n" + "="*80)
    print("TEMPLATE 4 VARIABLE SUMMARY")
    print("="*80 + "\n")

    total = 0
    for section, vars_list in variables.items():
        print(f"{section}:")
        for var in vars_list:
            print(f"  {var}")
        print(f"  Subtotal: {len(vars_list)}\n")
        total += len(vars_list)

    print(f"TOTAL VARIABLES: {total}")
