#!/usr/bin/env python3
"""
Sync Protected Content Script
Updates tools/protected_claude_content.md when users modify the protected section of CLAUDE.md
Only acts on user changes, not agent or automated changes
"""

import os
import sys
import stat
from pathlib import Path
from datetime import datetime

# Add parent directory to path to import monitor
sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.monitor_claude_md import ClaudeMdMonitor

class ProtectedContentSyncer:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.claude_md_path = self.project_root / "CLAUDE.md"
        self.protected_content_file = self.project_root / "tools/protected_claude_content.md"
        
        # Protection tags
        self.start_protection_tag = "<!-- critical: do not change anything below this line -->"
        self.end_protection_tag = "<!-- critical: do not change anything above this line -->"
    
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
    
    def update_protected_reference(self, new_content):
        """Update the protected content reference file"""
        try:
            # Make file writable temporarily if it's read-only
            was_readonly = False
            current_permissions = None
            
            if self.protected_content_file.exists():
                current_permissions = self.protected_content_file.stat().st_mode
                if not (current_permissions & stat.S_IWUSR):
                    was_readonly = True
                    # Make writable
                    self.protected_content_file.chmod(0o644)
            
            # Write new content (completely replace existing content)
            self.protected_content_file.write_text(new_content, encoding='utf-8')
            
            # Restore read-only permissions if it was read-only before
            if was_readonly and current_permissions is not None:
                readonly_permissions = current_permissions & ~stat.S_IWUSR & ~stat.S_IWGRP & ~stat.S_IWOTH
                self.protected_content_file.chmod(readonly_permissions)
            
            print(f"✅ Protected reference content updated: {self.protected_content_file}")
            return True
            
        except Exception as e:
            print(f"❌ Error updating protected reference: {e}")
            return False
    
    def sync_from_user_changes(self):
        """Sync protected content if last change was made by user"""
        if not self.claude_md_path.exists():
            print("⚠️ CLAUDE.md not found")
            return False

        # Check who made the last change
        monitor = ClaudeMdMonitor()
        user_info = monitor.get_current_user()

        # Only sync if change was made by user (not agent or auto-restore)
        if user_info.get('entity') in ['claude-agent', 'auto-restore-protection', 'content-syncer']:
            print(f"⏭️ Skipping sync - last change by: {user_info.get('entity')}")
            return False

        try:
            # Read current CLAUDE.md content
            current_content = self.claude_md_path.read_text(encoding='utf-8')
            
            # Extract protected section
            protected_content = self.extract_protected_section(current_content)
            
            if not protected_content.strip():
                print("⚠️ No protected content found between tags")
                return False
            
            # Update reference file
            if self.update_protected_reference(protected_content):
                print(f"🔄 Synced protected content from user changes")
                
                # Log this action in the monitoring system
                self.log_sync_action(user_info)
                return True
            
        except Exception as e:
            print(f"❌ Error during sync: {e}")
        
        return False
    
    def log_sync_action(self, original_user_info):
        """Log the sync action in the monitoring system"""
        try:
            monitor = ClaudeMdMonitor()
            
            # Create sync action log entry
            sync_info = {
                'entity': 'content-syncer',
                'type': 'reference_update',
                'timestamp': datetime.now().isoformat(),
                'commit': 'content-sync',
                'original_user': original_user_info.get('entity', 'unknown')
            }
            
            # Log entry for the sync action
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
            log_entry = f"""
==========================================
CONTENT SYNC: {timestamp}
==========================================
Entity: {sync_info['entity']}
Type: {sync_info['type']}
Original User: {sync_info['original_user']}
Action: Updated protected reference file from user changes
Timestamp: {sync_info['timestamp']}

SYNC DETAILS:
Protected content reference file updated with latest user modifications
Source: CLAUDE.md protected section (between critical tags)
Target: tools/protected_claude_content.md

"""
            
            # Append to changelog
            with open(monitor.changelog_path, 'a', encoding='utf-8') as f:
                f.write(log_entry)
            
            print(f"📝 Sync action logged to changelog")
            
        except Exception as e:
            print(f"⚠️ Error logging sync action: {e}")

def main():
    """Main execution function"""
    syncer = ProtectedContentSyncer()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == 'sync':
            print("🔄 Checking for user changes to sync...")
            if syncer.sync_from_user_changes():
                print("✅ Sync completed successfully")
            else:
                print("ℹ️ No sync needed")
                
        elif command == 'force':
            print("🔄 Force syncing protected content...")
            # Force sync regardless of who made changes
            try:
                current_content = syncer.claude_md_path.read_text(encoding='utf-8')
                protected_content = syncer.extract_protected_section(current_content)
                
                if protected_content.strip():
                    if syncer.update_protected_reference(protected_content):
                        print("✅ Force sync completed")
                    else:
                        print("❌ Force sync failed")
                else:
                    print("⚠️ No protected content found")
            except Exception as e:
                print(f"❌ Force sync error: {e}")
                
        else:
            print(f"❌ Unknown command: {command}")
            print("Available commands: sync, force")
            sys.exit(1)
    else:
        print("Protected Content Syncer")
        print("Usage:")
        print("  python tools/sync_protected_content.py sync   # Sync if user made changes")
        print("  python tools/sync_protected_content.py force  # Force sync regardless of user")
        print("")
        print("This tool updates the protected content reference file when users")
        print("modify the protected section of CLAUDE.md")

if __name__ == "__main__":
    main()