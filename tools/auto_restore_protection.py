#!/usr/bin/env python3
"""
Auto-Restore Protection System
Automatically detects and reverts unauthorized changes to protected sections of replit.md
"""

import os
import hashlib
from datetime import datetime
from pathlib import Path


class AutoRestoreProtection:
    def __init__(self, project_root=None):
        self.project_root = project_root or Path(__file__).parent.parent
        self.replit_md_path = self.project_root / "replit.md"
        self.protected_content_file = self.project_root / "tools/protected_replit_content.md"
        
        # Protection tags
        self.start_protection_tag = "<!-- critical: do not change anything below this line -->"
        self.end_protection_tag = "<!-- critical: do not change anything above this line -->"
    
    def get_file_hash(self, content):
        """Generate SHA256 hash of file content"""
        return hashlib.sha256(content.encode('utf-8')).hexdigest()
    
    def auto_restore_protected_content(self, monitor=None):
        """Automatically restore protected content if agent made unauthorized changes"""
        if not self.replit_md_path.exists():
            print("⚠️ replit.md not found")
            return False
        
        if not self.protected_content_file.exists():
            print("⚠️ Protected content reference file not found")
            return False
        
        try:
            current_content = self.replit_md_path.read_text(encoding='utf-8')
            
            # Import here to avoid circular imports
            if monitor is None:
                from tools.monitor_replit_md import ReplitMdMonitor
                monitor = ReplitMdMonitor()
            
            user_info = monitor.get_current_user()
            
            # Only act if the change was made by replit-agent (not user or content-syncer)
            if user_info.get('entity') not in ['replit-agent']:
                return False
            
            # Check if protected section was modified
            if self.is_protected_section_changed(current_content):
                print("🛡️ AUTO-RESTORE ACTIVATED: Agent modified protected section")
                
                # Restore protected content
                restored_content = self.restore_protected_section(current_content)
                if restored_content and restored_content != current_content:
                    # Write restored content
                    self.replit_md_path.write_text(restored_content, encoding='utf-8')
                    
                    # Log the auto-restore action
                    restore_info = {
                        'entity': 'auto-restore-protection',
                        'type': 'automated_restore',
                        'timestamp': datetime.now().isoformat(),
                        'commit': 'auto-restore'
                    }
                    
                    monitor.log_change(current_content, restored_content, restore_info)
                    
                    # Update stored hash
                    new_hash = self.get_file_hash(restored_content)
                    monitor.store_hash(new_hash)
                    
                    print("✅ Protected section restored by auto-restore")
                    return True
        
        except Exception as e:
            print(f"❌ Auto-restore error: {e}")
        
        return False
    
    def is_protected_section_changed(self, content):
        """Check if the protected section has been modified"""
        try:
            # Extract current protected content
            current_protected = self.extract_protected_section(content)
            
            # Get reference protected content
            reference_content = self.protected_content_file.read_text(encoding='utf-8')
            
            # Compare
            return current_protected.strip() != reference_content.strip()
            
        except Exception as e:
            print(f"Error checking protected section: {e}")
            return False
    
    def extract_protected_section(self, content):
        """Extract content between protection tags"""
        lines = content.split('\n')
        start_idx = None
        end_idx = None
        
        for i, line in enumerate(lines):
            if self.start_protection_tag in line:
                start_idx = i + 1
            elif self.end_protection_tag in line:
                end_idx = i
                break
        
        if start_idx is not None and end_idx is not None:
            return '\n'.join(lines[start_idx:end_idx])
        
        return ""
    
    def restore_protected_section(self, content):
        """Restore the protected section with reference content"""
        try:
            lines = content.split('\n')
            start_idx = None
            end_idx = None
            
            # Find protection tags
            for i, line in enumerate(lines):
                if self.start_protection_tag in line:
                    start_idx = i
                elif self.end_protection_tag in line:
                    end_idx = i
                    break
            
            if start_idx is not None and end_idx is not None:
                # Get reference content
                reference_content = self.protected_content_file.read_text(encoding='utf-8')
                
                # Replace protected section
                before_protection = lines[:start_idx + 1]  # Include start tag
                after_protection = lines[end_idx:]  # Include end tag
                
                # Combine with reference content
                restored_lines = before_protection + reference_content.split('\n') + after_protection
                return '\n'.join(restored_lines)
        
        except Exception as e:
            print(f"Error restoring protected section: {e}")
        
        return None


def main():
    """Main execution function for standalone testing"""
    protection = AutoRestoreProtection()
    
    print("🛡️ Running auto-restore protection check...")
    if protection.auto_restore_protected_content():
        print("✅ Protected section restored")
    else:
        print("✅ No unauthorized changes detected")


if __name__ == "__main__":
    main()