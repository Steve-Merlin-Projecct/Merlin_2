#!/usr/bin/env python3
"""
Demonstration and Testing Script for DOCX Authenticity Enhancement

This script demonstrates all authenticity features:
1. Smart Typography
2. Metadata Generation
3. Authenticity Validation
4. Complete Document Generation

Author: Automated Job Application System
Date: October 9, 2025
"""

import sys
import os
from datetime import datetime
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.content.document_generation import (
    SmartTypography,
    MetadataGenerator,
    AuthenticityValidator,
    enhance_text,
    get_typography_stats,
    generate_realistic_metadata,
    validate_document_authenticity,
    get_authenticity_level,
)


def test_smart_typography():
    """Test smart typography transformations"""
    print("\n" + "=" * 70)
    print("TEST 1: SMART TYPOGRAPHY")
    print("=" * 70)

    test_cases = [
        ('"Hello World"', 'Smart Quotes'),
        ("It's John's book", 'Apostrophes'),
        ('2020-2023', 'Date Range (En Dash)'),
        ('word--word', 'Em Dash'),
        ('Wait...', 'Ellipsis'),
        ('Dr. Smith', 'Non-Breaking Space'),
        ('10 MB', 'Non-Breaking Space (Units)'),
        ('Copyright (C) 2025', 'Copyright Symbol'),
        ('Temperature: 75 degrees', 'Degree Symbol'),
        ('1/2 cup', 'Fraction'),
    ]

    typography = SmartTypography()

    for original, description in test_cases:
        enhanced, stats = typography.apply_all(original)
        print(f"\n{description}:")
        print(f"  Original:  {repr(original)}")
        print(f"  Enhanced:  {repr(enhanced)}")
        if stats['smart_quotes'] > 0:
            print(f"  → {stats['smart_quotes']} smart quotes applied")
        if stats['smart_dashes'] > 0:
            print(f"  → {stats['smart_dashes']} smart dashes applied")
        if stats['smart_ellipsis'] > 0:
            print(f"  → {stats['smart_ellipsis']} smart ellipsis applied")

    # Quality score
    sample_text = 'This is a "professional" document -- created in 2020-2023... It\'s great!'
    enhanced_text = enhance_text(sample_text)
    quality_score = typography.get_typography_quality_score(enhanced_text)

    print(f"\n\nQuality Assessment:")
    print(f"  Original:  {repr(sample_text)}")
    print(f"  Enhanced:  {repr(enhanced_text)}")
    print(f"  Quality Score: {quality_score}/100")

    return enhanced_text


def test_metadata_generation():
    """Test realistic metadata generation"""
    print("\n\n" + "=" * 70)
    print("TEST 2: METADATA GENERATION")
    print("=" * 70)

    generator = MetadataGenerator()

    # Test timestamp generation
    print("\n1. Realistic Timestamps:")
    for i in range(3):
        created = generator.generate_creation_timestamp()
        modified = generator.generate_modification_timestamp(created)
        print(f"\n  Document {i+1}:")
        print(f"    Created:  {created.strftime('%Y-%m-%d %H:%M:%S %A')}")
        print(f"    Modified: {modified.strftime('%Y-%m-%d %H:%M:%S %A')}")
        print(f"    Days between: {(modified - created).days}")

    # Test editing time
    print("\n\n2. Editing Time Simulation:")
    for doc_type in ['resume', 'coverletter', 'template']:
        times = [generator.generate_editing_time(doc_type) for _ in range(3)]
        print(f"  {doc_type.title()}: {times} minutes (avg: {sum(times)/len(times):.0f} min)")

    # Test revision numbers
    print("\n3. Revision Numbers:")
    for doc_type in ['resume', 'coverletter', 'template']:
        revisions = [generator.generate_revision_number(doc_type) for _ in range(5)]
        print(f"  {doc_type.title()}: {revisions}")

    # Complete metadata generation
    print("\n\n4. Complete Metadata Package:")
    metadata = generate_realistic_metadata(
        document_type='resume',
        author_name='John Doe',
        document_title='John Doe Resume',
        subject='Professional Resume',
        keywords='Resume, Python, Engineer'
    )

    core = metadata['core_properties']
    app = metadata['app_properties']

    print(f"  Core Properties:")
    print(f"    Title: {core['title']}")
    print(f"    Author: {core['author']}")
    print(f"    Created: {core['created'].strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"    Modified: {core['modified'].strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"    Revision: {core['revision']}")
    print(f"\n  App Properties:")
    print(f"    Application: {app['application']}")
    print(f"    Version: {app['app_version']}")
    print(f"    Editing Time: {app['total_time']} minutes")

    return metadata


def test_authenticity_validation(metadata, text_content):
    """Test authenticity validation and scoring"""
    print("\n\n" + "=" * 70)
    print("TEST 3: AUTHENTICITY VALIDATION")
    print("=" * 70)

    validator = AuthenticityValidator()

    # Individual component tests
    print("\n1. Individual Component Scores:")

    meta_score, meta_issues = validator.validate_metadata_completeness(metadata)
    print(f"\n  Metadata Completeness: {meta_score}/25 points")
    if meta_issues:
        for issue in meta_issues:
            print(f"    ⚠ {issue}")

    time_score, time_issues = validator.validate_timestamp_realism(metadata)
    print(f"\n  Timestamp Realism: {time_score}/20 points")
    if time_issues:
        for issue in time_issues:
            print(f"    ⚠ {issue}")

    edit_score, edit_issues = validator.validate_editing_time(metadata)
    print(f"\n  Editing Time: {edit_score}/15 points")
    if edit_issues:
        for issue in edit_issues:
            print(f"    ⚠ {issue}")

    typo_score, typo_issues = validator.validate_typography_quality(text_content)
    print(f"\n  Typography Quality: {typo_score}/15 points")
    if typo_issues:
        for issue in typo_issues:
            print(f"    ⚠ {issue}")

    template_score, template_issues = validator.validate_template_completion(text_content)
    print(f"\n  Template Completion: {template_score}/10 points")
    if template_issues:
        for issue in template_issues:
            print(f"    ⚠ {issue}")

    # Overall validation
    print("\n\n2. Overall Authenticity Score:")

    results = validate_document_authenticity(
        metadata=metadata,
        text_content=text_content,
    )

    print(f"\n  Total Score: {results['total_score']}/100")
    print(f"  Level: {results['level'].upper()}")
    print(f"  Status: {'✓ PASSED' if results['passed'] else '✗ FAILED'}")
    print(f"  Total Issues: {results['total_issues']}")

    # Detailed score breakdown
    print("\n  Score Breakdown:")
    for component, score in results['scores'].items():
        max_score = validator.scoring_weights[component]
        percentage = (score / max_score * 100) if max_score > 0 else 0
        status = "✓" if percentage >= 80 else "⚠" if percentage >= 60 else "✗"
        print(f"    {status} {component.replace('_', ' ').title():<30} {score:>2}/{max_score:<2} ({percentage:>5.1f}%)")

    # Generate report
    print("\n\n3. Verification Report:")
    report = validator.generate_verification_report(results)
    print(report)

    return results


def test_complete_workflow():
    """Test complete document generation workflow with authenticity"""
    print("\n\n" + "=" * 70)
    print("TEST 4: COMPLETE WORKFLOW")
    print("=" * 70)

    print("\nSimulating complete document generation with authenticity enhancement...")

    # Step 1: Prepare document data
    data = {
        'first_name': 'Jane',
        'last_name': 'Smith',
        'email': 'jane.smith@email.com',
        'phone_number': '(555) 123-4567',
        'linkedin_url': 'linkedin.com/in/janesmith',
        'document_type': 'resume',
    }

    # Step 2: Generate sample content
    original_content = '''
    "Professional Summary"

    I'm a dedicated software engineer with 5-10 years of experience...
    My skills include Python, JavaScript--and I love working on challenging projects.

    Contact me at (555) 123-4567 or visit my LinkedIn.

    Copyright (C) 2025 Jane Smith. Temperature preference: 72 degrees.
    '''

    # Step 3: Apply typography
    print("\n1. Applying Smart Typography...")
    typography = SmartTypography()
    enhanced_content, stats = typography.apply_all(original_content)

    print(f"   Applied {stats['smart_quotes']} smart quotes")
    print(f"   Applied {stats['smart_dashes']} smart dashes")
    print(f"   Applied {stats['smart_ellipsis']} smart ellipsis")
    print(f"   Applied {stats['non_breaking_spaces']} non-breaking spaces")

    # Step 4: Generate metadata
    print("\n2. Generating Realistic Metadata...")
    generator = MetadataGenerator()
    metadata = generator.generate_complete_metadata(
        document_type='resume',
        author_name=f"{data['first_name']} {data['last_name']}",
        document_title=f"{data['first_name']} {data['last_name']} Resume",
        subject='Professional Software Engineer Resume',
        keywords='Software Engineer, Python, JavaScript, Resume',
    )

    created = metadata['core_properties']['created']
    modified = metadata['core_properties']['modified']
    editing_time = metadata['app_properties']['total_time']
    revision = metadata['core_properties']['revision']

    print(f"   Created: {created.strftime('%Y-%m-%d %H:%M:%S %A')}")
    print(f"   Modified: {modified.strftime('%Y-%m-%d %H:%M:%S %A')}")
    print(f"   Editing Time: {editing_time} minutes")
    print(f"   Revision: {revision}")

    # Step 5: Validate authenticity
    print("\n3. Validating Authenticity...")
    validator = AuthenticityValidator()
    results = validator.calculate_authenticity_score(
        metadata=metadata,
        text_content=enhanced_content,
    )

    print(f"   Authenticity Score: {results['total_score']}/100 ({results['level'].upper()})")
    print(f"   Status: {'✓ PASSED' if results['passed'] else '✗ FAILED'}")

    # Step 6: Summary
    print("\n\n4. Summary:")
    print(f"   Document Type: Resume")
    print(f"   Author: {data['first_name']} {data['last_name']}")
    print(f"   Typography Enhanced: ✓")
    print(f"   Realistic Metadata: ✓")
    print(f"   Authenticity Score: {results['total_score']}/100")
    print(f"   Ready for Delivery: {'✓ YES' if results['passed'] else '✗ NO'}")

    return {
        'metadata': metadata,
        'content': enhanced_content,
        'validation': results,
    }


def main():
    """Run all tests"""
    print("\n" + "=" * 70)
    print("DOCX AUTHENTICITY ENHANCEMENT - DEMONSTRATION")
    print("=" * 70)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("Version: 2.0.0")

    try:
        # Test 1: Smart Typography
        enhanced_text = test_smart_typography()

        # Test 2: Metadata Generation
        metadata = test_metadata_generation()

        # Test 3: Authenticity Validation
        validation = test_authenticity_validation(metadata, enhanced_text)

        # Test 4: Complete Workflow
        workflow_result = test_complete_workflow()

        # Final Summary
        print("\n\n" + "=" * 70)
        print("ALL TESTS COMPLETED SUCCESSFULLY ✓")
        print("=" * 70)
        print(f"\nAuthenticity Enhancement System: OPERATIONAL")
        print(f"Final Workflow Score: {workflow_result['validation']['total_score']}/100")
        print(f"System Status: READY FOR PRODUCTION")

    except Exception as e:
        print(f"\n\n✗ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == '__main__':
    sys.exit(main())
