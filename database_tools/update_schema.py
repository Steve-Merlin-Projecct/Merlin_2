#!/usr/bin/env python3
"""
Simple automation script to update database schema HTML
Can be run manually or scheduled as needed.
"""

import os
import sys
import hashlib
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from database_tools.schema_html_generator import DatabaseSchemaHTMLGenerator

def get_file_hash(file_path: str) -> str:
    """Get SHA-256 hash of file content"""
    try:
        with open(file_path, 'rb') as f:
            return hashlib.sha256(f.read()).hexdigest()
    except FileNotFoundError:
        return ""

def main():
    """Main update process"""
    template_path = Path(__file__).parent.parent / 'frontend_templates' / 'database_schema.html'
    
    # Get current file hash
    old_hash = get_file_hash(str(template_path))
    
    print("🔄 Updating database schema HTML...")
    
    try:
        # Generate new schema HTML
        generator = DatabaseSchemaHTMLGenerator()
        generator.update_schema_html(str(template_path))
        
        # Check if file actually changed
        new_hash = get_file_hash(str(template_path))
        
        if old_hash != new_hash:
            print("✅ Schema HTML updated - changes detected")
        else:
            print("ℹ️  Schema HTML unchanged - no database changes detected")
            
    except Exception as e:
        print(f"❌ Error updating schema: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()