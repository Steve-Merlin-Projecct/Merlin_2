#!/usr/bin/env python3
"""
Automated template conversion using TemplateConverter class
This script runs the existing TemplateConverter on the same templates
that were manually converted for comparison.
"""

import sys
import os

# Add the module path to system path
sys.path.insert(0, '/workspace/.trees/convert-raw-template-files-into-ready-for-producti')
sys.path.insert(0, '/workspace')

from modules.content.document_generation.template_converter import TemplateConverter

def main():
    """Run automated conversion on the same templates"""

    # Initialize the converter
    converter = TemplateConverter()

    # Define source and target paths
    conversions = [
        {
            "source": "/workspace/content_template_library/downloaded from microsft/TF57cae682-222c-4646-9a80-c404ee5c5d7e394a39ab_wac-08402e1a51c0.docx",
            "target": "/workspace/content_template_library/automated_converted/restaurant_manager_automated.docx",
            "type": "resume",
            "name": "Restaurant Manager"
        },
        {
            "source": "/workspace/content_template_library/downloaded from microsft/TFb97c34b7-bcc4-4366-92c6-8b5a08ba27cc7b6784e7_wac-1406ae744f4d.docx",
            "target": "/workspace/content_template_library/automated_converted/accountant_automated.docx",
            "type": "resume",
            "name": "Accountant"
        }
    ]

    print("=" * 60)
    print("AUTOMATED TEMPLATE CONVERSION USING TemplateConverter")
    print("=" * 60)
    print()

    # Process each template
    for conv in conversions:
        print(f"Converting: {conv['name']}")
        print(f"  Source: {conv['source']}")
        print(f"  Target: {conv['target']}")

        try:
            # Run the conversion
            stats = converter.convert_reference_to_template(
                conv["source"],
                conv["target"],
                conv["type"]
            )

            print(f"  ✓ Conversion completed")
            print(f"    - Paragraphs modified: {stats['paragraphs_modified']}")
            print(f"    - Patterns matched: {len(stats['patterns_matched'])}")
            print(f"    - Variables created: {len(stats['variables_created'])}")
            print(f"    - Unmatched content: {len(stats['unmatched_content'])}")

            # Show matched patterns
            if stats['patterns_matched']:
                print(f"    - Patterns used:")
                for pattern, count in stats['patterns_matched'].items():
                    print(f"      • {pattern}: {count}x")

            print()

        except Exception as e:
            print(f"  ✗ Error: {str(e)}")
            print()

    print("=" * 60)
    print("Automated conversion complete!")
    print("Files saved to: /workspace/content_template_library/automated_converted/")

if __name__ == "__main__":
    main()