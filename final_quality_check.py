#!/usr/bin/env python3
"""
Final Quality Check - Comprehensive validation of converted templates.
"""

import zipfile
from lxml import etree
import re
from docx import Document


def final_check(template_path, template_name):
    """
    Perform final comprehensive quality check.
    """

    print(f"\n{'='*80}")
    print(f"FINAL QUALITY CHECK: {template_name}")
    print(f"{'='*80}\n")

    checks_passed = 0
    checks_total = 0

    # Check 1: File exists and can be opened
    checks_total += 1
    try:
        with zipfile.ZipFile(template_path, 'r') as zf:
            print("✅ Check 1: File opens as valid ZIP/DOCX")
            checks_passed += 1
    except Exception as e:
        print(f"❌ Check 1: Failed to open file - {e}")
        return

    # Check 2: XML is valid
    checks_total += 1
    try:
        with zipfile.ZipFile(template_path, 'r') as zf:
            xml_content = zf.read('word/document.xml')
            root = etree.fromstring(xml_content)
        print("✅ Check 2: XML structure is valid and parseable")
        checks_passed += 1
    except Exception as e:
        print(f"❌ Check 2: XML parsing failed - {e}")
        return

    # Check 3: Can be loaded with python-docx
    checks_total += 1
    try:
        doc = Document(template_path)
        print(f"✅ Check 3: Template loads correctly with python-docx ({len(doc.paragraphs)} paragraphs)")
        checks_passed += 1
    except Exception as e:
        print(f"❌ Check 3: python-docx loading failed - {e}")

    # Check 4: Contains variables
    checks_total += 1
    try:
        with zipfile.ZipFile(template_path, 'r') as zf:
            xml_content = zf.read('word/document.xml')
            xml_str = xml_content.decode('utf-8')

        variables = re.findall(r'&lt;&lt;([^&]+)&gt;&gt;', xml_str)
        if len(variables) > 0:
            print(f"✅ Check 4: Contains {len(variables)} variable instances ({len(set(variables))} unique)")
            checks_passed += 1
        else:
            print("❌ Check 4: No variables found!")
    except Exception as e:
        print(f"❌ Check 4: Variable check failed - {e}")

    # Check 5: No obvious hardcoded values
    checks_total += 1
    issues = []

    # Extract text
    namespaces = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
    text_elements = root.xpath('.//w:t', namespaces=namespaces)
    all_text = ' '.join([elem.text for elem in text_elements if elem.text])

    # Check for patterns that should be variables
    if re.search(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', all_text):
        if '555' not in all_text:  # Exclude example numbers
            issues.append("Found phone number pattern")

    if re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', all_text):
        if '@example.com' not in all_text.lower():
            issues.append("Found email pattern")

    # Check for common hardcoded company indicators
    suspicious_words = ['Corporation', 'Inc.', 'LLC', 'Ltd.']
    for word in suspicious_words:
        if word in all_text and f'<<company' not in all_text:
            # Make sure it's not part of a variable
            context = all_text[max(0, all_text.find(word)-20):all_text.find(word)+20]
            if '<<' not in context:
                issues.append(f"Found '{word}' which might be hardcoded")

    if len(issues) == 0:
        print("✅ Check 5: No obvious hardcoded values detected")
        checks_passed += 1
    else:
        print(f"⚠️  Check 5: Potential issues found:")
        for issue in issues:
            print(f"    - {issue}")

    # Check 6: Variable naming convention
    checks_total += 1
    good_naming = True
    for var in set(variables):
        # Check for good naming patterns
        if not re.match(r'^[a-z_0-9]+$', var):
            print(f"⚠️  Variable '{var}' doesn't follow snake_case convention")
            good_naming = False

    if good_naming:
        print("✅ Check 6: Variable naming follows conventions")
        checks_passed += 1
    else:
        print("⚠️  Check 6: Some variables have non-standard naming")

    # Summary
    print(f"\n{'-'*80}")
    print(f"CHECKS PASSED: {checks_passed}/{checks_total}")

    if checks_passed == checks_total:
        print(f"STATUS: ✅ EXCELLENT - All checks passed!")
        return "EXCELLENT"
    elif checks_passed >= checks_total * 0.8:
        print(f"STATUS: ✅ GOOD - Most checks passed")
        return "GOOD"
    else:
        print(f"STATUS: ⚠️  NEEDS REVIEW - Several checks failed")
        return "NEEDS_REVIEW"


def main():
    print("\n" + "="*80)
    print("FINAL QUALITY CHECK - TEMPLATES 4 & 5")
    print("="*80)

    template_4 = "/workspace/.trees/convert-raw-template-files-into-ready-for-producti/content_template_library/manual_converted/template_4_converted.docx"
    template_5 = "/workspace/.trees/convert-raw-template-files-into-ready-for-producti/content_template_library/manual_converted/template_5_converted.docx"

    status_4 = final_check(template_4, "Template 4 (Assistant Hotel Manager)")
    status_5 = final_check(template_5, "Template 5 (Office Manager)")

    print("\n\n" + "="*80)
    print("OVERALL SUMMARY")
    print("="*80 + "\n")

    print(f"Template 4: {status_4}")
    print(f"Template 5: {status_5}")

    if status_4 in ["EXCELLENT", "GOOD"] and status_5 in ["EXCELLENT", "GOOD"]:
        print("\n" + "="*80)
        print("✅ BOTH TEMPLATES READY FOR PRODUCTION")
        print("="*80)
        print("\nDeliverables:")
        print(f"  1. {template_4}")
        print(f"  2. {template_5}")
        print(f"  3. /workspace/.trees/convert-raw-template-files-into-ready-for-producti/TEMPLATE_45_CONVERSION_REPORT.md")
        print("\nNext Steps:")
        print("  - Integrate templates into document generation system")
        print("  - Test with real user data")
        print("  - Deploy to production")
    else:
        print("\n⚠️  REVIEW RECOMMENDED before production deployment")


if __name__ == "__main__":
    main()
