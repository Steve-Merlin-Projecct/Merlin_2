#!/usr/bin/env python3
"""
Verification script to check if converted templates are valid and properly formatted.
"""

import zipfile
from lxml import etree
import re


def verify_template(doc_path, template_name):
    """
    Verify that template has been properly converted.
    """

    print(f"\n{'='*80}")
    print(f"VERIFYING: {template_name}")
    print(f"{'='*80}\n")

    try:
        with zipfile.ZipFile(doc_path, 'r') as zip_ref:
            xml_content = zip_ref.read('word/document.xml')

        # Try to parse XML to verify it's valid
        root = etree.fromstring(xml_content)
        print("✅ XML structure is valid")

        # Extract all text elements
        namespaces = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
        text_elements = root.xpath('.//w:t', namespaces=namespaces)

        all_text = []
        for elem in text_elements:
            if elem.text:
                all_text.append(elem.text)

        combined_text = ' '.join(all_text)

        # Count variables (looking for &lt;&lt;...&gt;&gt; or <<...>>)
        # In XML, they're stored as &lt;&lt; but when rendered become <<
        xml_str = xml_content.decode('utf-8')

        # Count encoded variables
        encoded_vars = re.findall(r'&lt;&lt;([^&]+)&gt;&gt;', xml_str)
        # Count regular variables (shouldn't be there, but check)
        regular_vars = re.findall(r'<<([^>]+)>>', combined_text)

        print(f"✅ Found {len(encoded_vars)} properly encoded variables")

        if regular_vars:
            print(f"⚠️  Found {len(regular_vars)} unencoded variables (may cause XML issues)")

        # Check for unique variables
        unique_encoded = sorted(set(encoded_vars))
        print(f"✅ {len(unique_encoded)} unique variables")

        # Check for potential issues
        issues = []

        # Check for remaining hardcoded dates
        if '20XX' in combined_text and '&lt;&lt;' not in xml_str[:xml_str.find('20XX')+100]:
            issues.append("⚠️  Found '20XX' that might not be variablized")

        # Check for common hardcoded patterns
        hardcoded_patterns = [
            (r'\b\d{3}-\d{3}-\d{4}\b', 'phone number'),
            (r'\b[A-Za-z0-9._%+-]+@(?!example\.com)[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', 'email address'),
        ]

        for pattern, description in hardcoded_patterns:
            matches = re.findall(pattern, combined_text)
            if matches:
                # Check if they're actually variables (encoded)
                for match in matches:
                    if f'&lt;&lt;' not in xml_str[max(0, xml_str.find(match)-50):xml_str.find(match)+50]:
                        issues.append(f"⚠️  Found potentially hardcoded {description}: {match}")

        # Print results
        print(f"\nVariable Summary:")
        print(f"  Total: {len(encoded_vars)}")
        print(f"  Unique: {len(unique_encoded)}")

        print(f"\nUnique variables in template:")
        for i, var in enumerate(unique_encoded, 1):
            print(f"  {i:2d}. <<{var}>>")

        if issues:
            print(f"\n⚠️  ISSUES FOUND:")
            for issue in issues:
                print(f"  {issue}")
            status = "NEEDS_REVIEW"
        else:
            print(f"\n✅ NO ISSUES FOUND - Template looks good!")
            status = "GOOD"

        # Show sample text
        print(f"\nSample text (first 400 chars):")
        sample = combined_text[:400].replace('\n', ' ')
        print(f"  {sample}...")

        return {
            'total_variables': len(encoded_vars),
            'unique_variables': len(unique_encoded),
            'issues': issues,
            'status': status,
            'variable_list': unique_encoded
        }

    except etree.XMLSyntaxError as e:
        print(f"❌ XML PARSING ERROR: {e}")
        return {
            'total_variables': 0,
            'unique_variables': 0,
            'issues': [f"XML parsing error: {e}"],
            'status': 'FAILED',
            'variable_list': []
        }
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return {
            'total_variables': 0,
            'unique_variables': 0,
            'issues': [f"Error: {e}"],
            'status': 'FAILED',
            'variable_list': []
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
    print("FINAL VERIFICATION SUMMARY")
    print("="*80 + "\n")

    print(f"Template 4 (Assistant Hotel Manager):")
    print(f"  Status: {result_4['status']}")
    print(f"  Variables: {result_4['unique_variables']} unique ({result_4['total_variables']} total)")
    print(f"  Issues: {len(result_4['issues'])}")

    print(f"\nTemplate 5 (Office Manager):")
    print(f"  Status: {result_5['status']}")
    print(f"  Variables: {result_5['unique_variables']} unique ({result_5['total_variables']} total)")
    print(f"  Issues: {len(result_5['issues'])}")

    if result_4['status'] == 'GOOD' and result_5['status'] == 'GOOD':
        print(f"\n{'='*80}")
        print("✅ ALL TEMPLATES PASSED VERIFICATION!")
        print("="*80)
    else:
        print(f"\n{'='*80}")
        print("⚠️  SOME TEMPLATES NEED REVIEW")
        print("="*80)
