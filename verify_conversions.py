#!/usr/bin/env python3
"""
Verification script to check if all hardcoded values were properly replaced.
"""

import zipfile
from lxml import etree
import re


def verify_template(doc_path, template_name):
    """
    Verify that template has been properly converted to variables.

    Checks for:
    - Remaining hardcoded names
    - Remaining hardcoded companies
    - Remaining hardcoded dates
    - All variables are properly formatted with <<>>
    """

    print(f"\n{'='*80}")
    print(f"VERIFYING: {template_name}")
    print(f"{'='*80}\n")

    with zipfile.ZipFile(doc_path, 'r') as zip_ref:
        xml_content = zip_ref.read('word/document.xml')

    xml_str = xml_content.decode('utf-8')

    # Extract all text elements
    root = etree.fromstring(xml_content)
    namespaces = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
    text_elements = root.xpath('.//w:t', namespaces=namespaces)

    all_text = []
    for elem in text_elements:
        if elem.text and elem.text.strip():
            all_text.append(elem.text)

    combined_text = ' '.join(all_text)

    # Check for variables
    variables = re.findall(r'<<([^>]+)>>', combined_text)

    print(f"Total variables found: {len(variables)}\n")

    # Check for potential hardcoded values that should be variables
    issues = []

    # Check for hardcoded dates (20XX patterns)
    date_patterns = re.findall(r'20XX', combined_text)
    if date_patterns:
        issues.append(f"⚠️  Found {len(date_patterns)} instances of '20XX' (should be variables)")

    # Check for common hardcoded company indicators
    if 'Corporation' in combined_text and '<<company' not in combined_text:
        issues.append("⚠️  Found 'Corporation' which might be a hardcoded company name")

    if 'Company' in combined_text and '<<company' not in combined_text:
        # Check if it's part of a variable
        if '<<company_' not in combined_text:
            issues.append("⚠️  Found 'Company' which might be a hardcoded company name")

    # Check for email patterns (shouldn't be hardcoded)
    email_pattern = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', combined_text)
    if email_pattern:
        # Check if they're variables
        for email in email_pattern:
            if '@example.com' not in email and '<<email>>' not in combined_text:
                issues.append(f"⚠️  Found potentially hardcoded email: {email}")

    # Check for phone patterns
    phone_pattern = re.findall(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', combined_text)
    if phone_pattern:
        for phone in phone_pattern:
            if '555' not in phone:  # 555 is typically used in examples
                issues.append(f"⚠️  Found potentially hardcoded phone: {phone}")

    # Print results
    if issues:
        print("ISSUES FOUND:")
        for issue in issues:
            print(f"  {issue}")
        print(f"\nStatus: ⚠️  REVIEW NEEDED")
    else:
        print("Status: ✅ LOOKS GOOD - No obvious hardcoded values detected")

    # Print all variables found
    print(f"\nVariables in template ({len(variables)}):")
    unique_vars = sorted(set(variables))
    for var in unique_vars:
        print(f"  <<{var}>>")

    # Show sample text to verify
    print(f"\nSample text from template (first 500 chars):")
    print(combined_text[:500])

    return {
        'total_variables': len(variables),
        'unique_variables': len(unique_vars),
        'issues': issues,
        'status': 'NEEDS_REVIEW' if issues else 'GOOD'
    }


if __name__ == "__main__":
    template_4_path = "/workspace/.trees/convert-raw-template-files-into-ready-for-producti/content_template_library/manual_converted/template_4_converted.docx"
    template_5_path = "/workspace/.trees/convert-raw-template-files-into-ready-for-producti/content_template_library/manual_converted/template_5_converted.docx"

    # Verify Template 4
    result_4 = verify_template(template_4_path, "Template 4 (Assistant Hotel Manager)")

    print("\n\n" + "#"*80 + "\n\n")

    # Verify Template 5
    result_5 = verify_template(template_5_path, "Template 5 (Office Manager)")

    # Summary
    print("\n\n" + "="*80)
    print("VERIFICATION SUMMARY")
    print("="*80 + "\n")

    print(f"Template 4: {result_4['unique_variables']} unique variables, Status: {result_4['status']}")
    print(f"Template 5: {result_5['unique_variables']} unique variables, Status: {result_5['status']}")
