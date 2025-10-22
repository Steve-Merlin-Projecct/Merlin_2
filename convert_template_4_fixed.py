#!/usr/bin/env python3
"""
Template 4 Converter - Assistant Hotel Manager Template (FIXED VERSION)
Properly handles XML entities when converting to variables.
"""

import zipfile
import shutil
from lxml import etree
import os
import html


def convert_template_4():
    """
    Convert Template 4 from hardcoded values to variables.
    Uses proper XML escaping to prevent corruption.
    """

    source_path = "/workspace/.trees/convert-raw-template-files-into-ready-for-producti/content_template_library/manual_converted/template_4_source.docx"
    output_path = "/workspace/.trees/convert-raw-template-files-into-ready-for-producti/content_template_library/manual_converted/template_4_converted.docx"

    # Create a copy to work with
    shutil.copy(source_path, output_path)

    # Define replacements
    # Note: We'll replace with &lt;&lt;variable&gt;&gt; which renders as <<variable>>
    replacements = []

    # Contact Information
    replacements.append(('716-555-0100', '&lt;&lt;phone&gt;&gt;'))
    replacements.append(('www.interestingsite.com', '&lt;&lt;website&gt;&gt;'))
    replacements.append(('lisandro@example.com', '&lt;&lt;email&gt;&gt;'))
    replacements.append(('Lisandro Milanesi', '&lt;&lt;first_name&gt;&gt; &lt;&lt;last_name&gt;&gt;'))

    # Profile Section
    profile_text = ('Assistant Hotel Manager with a warm and friendly demeanor. Skilled at conflict resolution. '
                   'Team builder who is acutely attentive to employee and guest needs. Punctual problem solver and '
                   'avid multitasker. Track record of being an essential part of the management team and instrumental '
                   'in providing effective solutions that produce immediate impact and contribute to the establishment\'s '
                   'long-term success.')
    replacements.append((profile_text, '&lt;&lt;career_overview_1&gt;&gt;'))

    # Section Headers
    replacements.append(('Profile', '&lt;&lt;profile_header&gt;&gt;'))
    replacements.append(('WORK EXPERIENCE', '&lt;&lt;experience_header&gt;&gt;'))
    replacements.append(('Activities and interests', '&lt;&lt;interests_header&gt;&gt;'))
    replacements.append(('Key skills', '&lt;&lt;skills_header&gt;&gt;'))
    replacements.append(('education', '&lt;&lt;education_header&gt;&gt;'))

    # Job 1 experience
    job1_exp = ('Supervise hotel staff. Improve staff performance through training, attention to detail, '
               'and empathetic problem-solving methods. Assist with the preparation of staff assessments. '
               'Resolve staff and guest conflicts in a professional and courteous manner. Inventory and order '
               'business supplies. Responsible for guest billing and settling payment disputes. Admin tasks as '
               'needed including bookings, check-ins, answering phones, responding to email, and social media inquiries.')
    replacements.append((job1_exp, '&lt;&lt;job_1_experience_1&gt;&gt;'))

    # Job 2 experience
    job2_exp = ('Supervised and trained hotel staff and resolved staff conflicts. Daily financial reporting. '
               'In charge of guest database and stays schedule. Point person for corporate client relations and '
               'reviewing guest feedback posted online. Worked with marketing team on campaign to increase guest '
               'bookings. Assisted accountant with accounting tasks. Handled in-person guest complaints.')
    replacements.append((job2_exp, '&lt;&lt;job_2_experience_1&gt;&gt;'))

    # Company names
    replacements.append(('The Rosehip Hotel', '&lt;&lt;company_1&gt;&gt;'))
    replacements.append(('The Seattle Sea Home', '&lt;&lt;company_2&gt;&gt;'))

    # Date patterns
    replacements.append(('20XX – Present', '&lt;&lt;start_date_1&gt;&gt; – &lt;&lt;end_date_1&gt;&gt;'))
    replacements.append(('20XX – 20XX', '&lt;&lt;start_date_2&gt;&gt; – &lt;&lt;end_date_2&gt;&gt;'))

    # Skills
    replacements.append(('Budget management', '&lt;&lt;skill_1&gt;&gt;'))
    replacements.append(('Excellent listener', '&lt;&lt;skill_2&gt;&gt;'))
    replacements.append(('Friendly, courteous, & service oriented', '&lt;&lt;skill_3&gt;&gt;'))
    replacements.append(('Poised under pressure', '&lt;&lt;skill_4&gt;&gt;'))
    replacements.append(('Staff training & coaching', '&lt;&lt;skill_5&gt;&gt;'))
    replacements.append(('Recruiting & hiring talent', '&lt;&lt;skill_6&gt;&gt;'))
    replacements.append(('Quality assurance', '&lt;&lt;skill_7&gt;&gt;'))
    replacements.append(('Solid written & verbal communicator', '&lt;&lt;skill_8&gt;&gt;'))

    # Interests
    replacements.append(('Surfing', '&lt;&lt;interest_1&gt;&gt;'))
    replacements.append(('Scuba diving', '&lt;&lt;interest_2&gt;&gt;'))
    replacements.append(('Snorkeling', '&lt;&lt;interest_3&gt;&gt;'))
    replacements.append(('Craft beer', '&lt;&lt;interest_4&gt;&gt;'))
    replacements.append(('Travel', '&lt;&lt;interest_5&gt;&gt;'))
    replacements.append(('Great food', '&lt;&lt;interest_6&gt;&gt;'))
    replacements.append(('Food Pantry Volunteer', '&lt;&lt;interest_7&gt;&gt;'))

    # Education
    replacements.append(('Bachelor of Science in Hospitality Management', '&lt;&lt;degree_1&gt;&gt;'))
    replacements.append(('Bellows College', '&lt;&lt;institution_1&gt;&gt;'))

    # Open and modify the document XML
    with zipfile.ZipFile(output_path, 'r') as zip_ref:
        temp_dir = '/tmp/template_4_temp'
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

    # Handle "Assistant Hotel Manager" (appears twice - once for each job)
    parts = xml_str.split('Assistant Hotel Manager', 2)
    if len(parts) >= 3:
        xml_str = parts[0] + '&lt;&lt;position_1&gt;&gt;' + parts[1] + '&lt;&lt;position_2&gt;&gt;' + parts[2]
    elif len(parts) == 2:
        xml_str = parts[0] + '&lt;&lt;position_1&gt;&gt;' + parts[1]

    # Handle "Seattle, WA" (appears twice)
    parts = xml_str.split('Seattle, WA', 2)
    if len(parts) >= 3:
        xml_str = parts[0] + '&lt;&lt;job_city_1&gt;&gt;, &lt;&lt;job_state_1&gt;&gt;' + parts[1] + '&lt;&lt;job_city_2&gt;&gt;, &lt;&lt;job_state_2&gt;&gt;' + parts[2]
    elif len(parts) == 2:
        xml_str = parts[0] + '&lt;&lt;job_city_1&gt;&gt;, &lt;&lt;job_state_1&gt;&gt;' + parts[1]

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

    print("✅ Template 4 converted successfully!")
    print(f"   Output: {output_path}")

    return 42  # Total variable count


if __name__ == "__main__":
    total_vars = convert_template_4()
    print(f"\nTotal variables: {total_vars}")
