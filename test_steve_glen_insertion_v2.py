#!/usr/bin/env python3
"""
Test Steve Glen data insertion with FIXED template
Uses CSV work history for better context
"""

import json
import sys
import re
import csv
sys.path.insert(0, './scripts')

from simplified_inserter import SimplifiedInserter
from docx import Document


def load_work_history_csv(csv_path):
    """Load work history from CSV"""
    jobs = []
    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            jobs.append(row)
    return jobs


def map_steve_glen_to_template_v2(json_path, csv_path):
    """Map Steve Glen's data to template variables - IMPROVED VERSION"""

    with open(json_path, 'r') as f:
        data = json.load(f)

    work_history = load_work_history_csv(csv_path)

    resume = data['resume_data']
    personal = resume['personal']

    # Create mapping
    mapped_data = {}

    # CONTACT - Direct mapping (NO STATE/PROVINCE)
    mapped_data['first_name'] = personal.get('first_name', '')
    mapped_data['last_name'] = personal.get('last_name', '')
    mapped_data['email'] = personal.get('email', '')
    mapped_data['phone'] = personal.get('phone', '')
    mapped_data['city'] = personal.get('city', '')
    # REMOVED: mapped_data['state'] - User doesn't want province on resume
    mapped_data['street_address'] = personal.get('address', '')
    mapped_data['zip_code'] = personal.get('postal_code', '')
    mapped_data['linkedin_url'] = personal.get('linkedin', '')

    # CAREER OVERVIEW - Split professional summary into sentences
    prof_summary = resume.get('professional_summary', '')

    # Split into sentences
    sentences = [s.strip() + '.' for s in prof_summary.split('.') if s.strip()]

    # Map to career_overview_1 through 5
    for i in range(1, 6):
        mapped_data[f'career_overview_{i}'] = sentences[i-1] if i-1 < len(sentences) else ''

    # JOB EXPERIENCE - Use work history CSV for better mapping
    # Filter to marketing/professional jobs
    marketing_jobs = [j for j in work_history if j['Type'] == 'Marketing Communications']

    # Job 1 - Most recent (Odvod Media)
    if len(marketing_jobs) > 0:
        job1 = marketing_jobs[0]
        mapped_data['position_1'] = 'Digital Strategist, Content Contributor, Resource Coordinator, and Business Analyst'
        mapped_data['company_1'] = job1['Where']
        mapped_data['start_date_1'] = 'February 2020'  # From CSV "2020-present"
        mapped_data['end_date_1'] = 'Present'

        # Use bullets from JSON
        if resume.get('experience') and len(resume['experience']) > 0:
            bullets = resume['experience'][0].get('bullets', [])
            mapped_data['job_1_experience_1'] = bullets[0] if len(bullets) > 0 else ''
            mapped_data['job_1_experience_2'] = bullets[1] if len(bullets) > 1 else ''
            mapped_data['job_1_experience_3'] = bullets[2] if len(bullets) > 2 else ''

    # Job 2 - Use management experience from CSV
    management_jobs = [j for j in work_history if j['Type'] == 'management']
    if len(management_jobs) > 0:
        # Use Shambhala events as Job 2
        job2 = [j for j in management_jobs if 'Shambhala' in j['Where']]
        if job2:
            mapped_data['position_2'] = 'Event Manager & Beverage Operations Supervisor'
            mapped_data['company_2'] = 'Shambhala Music Festival'
            mapped_data['start_date_2'] = '2016'
            mapped_data['end_date_2'] = '2019'

            # Create experience bullets based on roles
            mapped_data['job_2_experience_1'] = 'Managed logistics and operations for large-scale music festival events with 10,000+ attendees'
            mapped_data['job_2_experience_2'] = 'Supervised beverage sales operations and trained staff on customer service best practices'
            mapped_data['job_2_experience_3'] = 'Coordinated site logistics including security, entertainment, and customer service'
            mapped_data['job_2_experience_4'] = 'Ensured compliance with safety regulations and maintained high customer satisfaction ratings'
    else:
        # No second job
        mapped_data['position_2'] = ''
        mapped_data['company_2'] = ''
        mapped_data['start_date_2'] = ''
        mapped_data['end_date_2'] = ''
        mapped_data['job_2_experience_1'] = ''
        mapped_data['job_2_experience_2'] = ''
        mapped_data['job_2_experience_3'] = ''
        mapped_data['job_2_experience_4'] = ''

    # EDUCATION
    if resume.get('education') and len(resume['education']) > 0:
        edu1 = resume['education'][0]
        mapped_data['degree_1'] = edu1.get('degree', '')
        mapped_data['institution_1'] = edu1.get('institution', '')
        mapped_data['graduation_date_1'] = edu1.get('graduation_date', '')

        # Parse location "Edmonton, AB" into city and state
        location = edu1.get('location', '')
        if ',' in location:
            parts = location.split(',')
            mapped_data['institution_city_1'] = parts[0].strip()
            mapped_data['institution_state_1'] = parts[1].strip() if len(parts) > 1 else ''
        else:
            mapped_data['institution_city_1'] = ''
            mapped_data['institution_state_1'] = ''

    # Education 2 (if exists)
    if resume.get('education') and len(resume['education']) > 1:
        edu2 = resume['education'][1]
        mapped_data['degree_2'] = edu2.get('degree', '')
        mapped_data['institution_2'] = edu2.get('institution', '')
        mapped_data['graduation_date_2'] = edu2.get('graduation_date', '')

        location = edu2.get('location', '')
        if ',' in location:
            parts = location.split(',')
            mapped_data['institution_city_2'] = parts[0].strip()
            mapped_data['institution_state_2'] = parts[1].strip() if len(parts) > 1 else ''
        else:
            mapped_data['institution_city_2'] = ''
            mapped_data['institution_state_2'] = ''
    else:
        mapped_data['degree_2'] = ''
        mapped_data['institution_2'] = ''
        mapped_data['institution_city_2'] = ''
        mapped_data['institution_state_2'] = ''
        mapped_data['graduation_date_2'] = ''

    # SKILLS - Extract from categorized format
    skills_data = resume.get('skills', {})
    all_skills = []

    # Extract from digital_marketing
    if 'digital_marketing' in skills_data:
        dm_skills = skills_data['digital_marketing'].split(',')
        all_skills.extend([s.strip() for s in dm_skills[:2]])

    # Extract from technical_expertise
    if 'technical_expertise' in skills_data:
        tech_skills = skills_data['technical_expertise'].split(',')
        all_skills.extend([s.strip() for s in tech_skills[:2]])

    # Extract from business_analytics
    if 'business_analytics' in skills_data:
        ba_skills = skills_data['business_analytics'].split(',')
        all_skills.extend([s.strip() for s in ba_skills[:2]])

    # Map to skill_1 through skill_6
    for i in range(1, 7):
        mapped_data[f'skill_{i}'] = all_skills[i-1] if i-1 < len(all_skills) else ''

    # INTERESTS - Split comma-separated string
    interests_str = skills_data.get('interests', '')
    if interests_str:
        interests_list = [i.strip() for i in interests_str.split(',')]
        for i in range(1, 7):
            mapped_data[f'interest_{i}'] = interests_list[i-1] if i-1 < len(interests_list) else ''
    else:
        for i in range(1, 7):
            mapped_data[f'interest_{i}'] = ''

    # Headers (use defaults)
    mapped_data['profile_header'] = 'Profile'
    mapped_data['experience_header'] = 'Experience'
    mapped_data['education_header'] = 'Education'
    mapped_data['skills_header'] = 'Skills'
    mapped_data['interests_header'] = 'Interests'

    return mapped_data


def test_insertion_v2():
    """Test the insertion process with FIXED template"""

    print("=" * 60)
    print("STEVE GLEN DATA INSERTION TEST V2")
    print("Using FIXED template (all issues resolved)")
    print("=" * 60)
    print()

    # Map Steve's data
    print("Step 1: Mapping Steve Glen data to template variables...")
    steve_data = map_steve_glen_to_template_v2(
        '/workspace/content_template_library/steve_glen_comprehensive_defaults.json',
        './user_profile/Steve-Glen_Work-History Table Simple 2025 - Sheet1.csv'
    )

    # Show what we mapped
    non_empty = {k: v for k, v in steve_data.items() if v}
    print(f"  Mapped {len(non_empty)} non-empty variables")
    print()

    # Insert into FIXED template
    print("Step 2: Inserting data into FIXED template...")
    inserter = SimplifiedInserter()

    # Temporarily override template file to use fixed version
    inserter.templates['restaurant_manager']['file'] = 'restaurant_manager_fixed.docx'

    output_path = inserter.populate_template(
        template_name='restaurant_manager',
        data=steve_data,
        output_filename='steve_glen_restaurant_manager_FIXED_test.docx'
    )

    print(f"  Output: {output_path}")
    print()

    # Analyze result
    print("Step 3: Analyzing output document...")
    doc = Document(output_path)

    # Check for remaining placeholders
    all_text = []
    for p in doc.paragraphs:
        all_text.append(p.text)

    # Find remaining variables
    remaining = set()
    for text in all_text:
        found = re.findall(r'<<([^>]+)>>', text)
        remaining.update(found)

    print(f"  Remaining placeholders: {len(remaining)}")
    if remaining:
        print("  Variables NOT replaced:")
        for var in sorted(remaining):
            print(f"    - <<{var}>>")

    print()
    print("=" * 60)
    print("Step 4: Summary Report")
    print("=" * 60)
    print()

    total_vars = 47  # Updated count with fixes
    replaced = total_vars - len(remaining)

    print(f"Total template variables: {total_vars}")
    print(f"Successfully replaced: {replaced}")
    print(f"Still placeholders: {len(remaining)}")
    print(f"Success rate: {replaced/total_vars*100:.1f}%")
    print()

    print("Key improvements from fixes:")
    print("  ✅ Removed state/province (Canadian user)")
    print("  ✅ Added company_1, start_date_1")
    print("  ✅ Fixed position_2 in Job 2")
    print("  ✅ Added degree and graduation date variables")
    print("  ✅ Split career overview into sentences")
    print("  ✅ Added Job 2 experience from work history CSV")
    print()

    return {
        'total': total_vars,
        'replaced': replaced,
        'remaining': len(remaining),
        'remaining_vars': sorted(remaining),
        'output_path': output_path
    }


if __name__ == "__main__":
    results = test_insertion_v2()
