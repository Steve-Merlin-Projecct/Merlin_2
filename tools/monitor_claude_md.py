#!/usr/bin/env python3
"""
CLAUDE.md Monitor System
Tracks changes to CLAUDE.md and logs them with entity attribution (user vs claude-agent)
Integrates with auto-restore protection for protected sections
"""

import os
import hashlib
import difflib
from datetime import datetime
from pathlib import Path
import time


class ClaudeMdMonitor:
    def __init__(self, project_root=None):
        self.project_root = project_root or Path(__file__).parent.parent
        self.claude_md_path = self.project_root / "CLAUDE.md"
        self.changelog_path = self.project_root / "docs/changelogs/claude-md_changelog.md"
        self.hash_file = self.project_root / "docs/changelogs/.claude_md_hash"

        # Ensure changelog directory exists
        self.changelog_path.parent.mkdir(parents=True, exist_ok=True)

        # Protection tags
        self.start_protection_tag = "<!-- critical: do not change anything below this line -->"
        self.end_protection_tag = "<!-- critical: do not change anything above this line -->"

    def get_file_hash(self, content):
        """Generate SHA256 hash of file content"""
        return hashlib.sha256(content.encode('utf-8')).hexdigest()

    def get_stored_hash(self):
        """Retrieve the last stored hash"""
        if self.hash_file.exists():
            return self.hash_file.read_text(encoding='utf-8').strip()
        return None

    def store_hash(self, content_hash):
        """Store the current file hash"""
        self.hash_file.write_text(content_hash, encoding='utf-8')

    def get_current_user(self):
        """
        Determine who made the change (user or claude-agent)
        Returns dict with entity info
        """
        # In Claude Code, we detect based on the tool that made the change
        # For now, we'll check if the change was made programmatically
        # This is a simplified detection - can be enhanced based on environment

        return {
            'entity': 'claude-agent',  # Default to agent, can be overridden
            'type': 'active_edit',
            'timestamp': datetime.now().isoformat(),
            'commit': 'pending'
        }

    def detect_change_author(self, old_content, new_content):
        """
        Enhanced detection of who made the change
        Returns 'user' or 'claude-agent' based on heuristics
        """
        # If content is identical, no change
        if old_content == new_content:
            return None

        # Check if change was in protected section
        if self.is_protected_section_changed(old_content, new_content):
            # Protected section changes are likely from agent (will be auto-restored)
            return 'claude-agent'

        # Default to claude-agent for programmatic detection
        # In a real deployment, this would check:
        # - File modification timestamps
        # - Process information
        # - Git authorship
        return 'claude-agent'

    def is_protected_section_changed(self, old_content, new_content):
        """Check if the protected section was modified"""
        old_protected = self.extract_protected_section(old_content)
        new_protected = self.extract_protected_section(new_content)
        return old_protected != new_protected

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

    def calculate_character_changes(self, old_content, new_content):
        """Calculate characters added and removed"""
        added = len(new_content) - len(old_content)
        if added >= 0:
            return added, 0
        else:
            return 0, abs(added)

    def get_detailed_changes(self, old_content, new_content, max_changes=30):
        """Get detailed line-by-line changes"""
        old_lines = old_content.splitlines()
        new_lines = new_content.splitlines()

        differ = difflib.Differ()
        diff = list(differ.compare(old_lines, new_lines))

        changes = []
        for i, line in enumerate(diff):
            if line.startswith('- '):
                changes.append(f"  • Line {i}: Removed '{line[2:]}'")
            elif line.startswith('+ '):
                changes.append(f"  • Line {i}: Added '{line[2:]}'")

            if len(changes) >= max_changes:
                changes.append(f"  ... and {len(diff) - i} more changes")
                break

        return changes

    def log_change(self, old_content, new_content, user_info):
        """Log a detected change to the changelog"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")

        # Calculate change metrics
        chars_added, chars_removed = self.calculate_character_changes(old_content, new_content)
        detailed_changes = self.get_detailed_changes(old_content, new_content)

        # Calculate hashes
        old_hash = self.get_file_hash(old_content)
        new_hash = self.get_file_hash(new_content)

        # Create log entry
        log_entry = f"""
==========================================
CHANGE DETECTED: {timestamp}
==========================================
Entity: {user_info.get('entity', 'unknown')}
Type: {user_info.get('type', 'unknown')}
Commit: {user_info.get('commit', 'pending')}
Timestamp: {user_info.get('timestamp', 'unknown')}

CHARACTER CHANGES:
{chars_added} characters added, {chars_removed} characters removed

DETAILED CHANGES:
{chr(10).join(detailed_changes[:30])}

FILE HASH:
Previous: {old_hash}
Current:  {new_hash}

"""

        # Append to changelog
        with open(self.changelog_path, 'a', encoding='utf-8') as f:
            f.write(log_entry)

        return log_entry

    def check_for_changes(self):
        """Check if CLAUDE.md has changed since last check"""
        if not self.claude_md_path.exists():
            print("⚠️ CLAUDE.md not found")
            return False

        # Read current content
        current_content = self.claude_md_path.read_text(encoding='utf-8')
        current_hash = self.get_file_hash(current_content)

        # Get stored hash
        stored_hash = self.get_stored_hash()

        # If no stored hash, initialize
        if stored_hash is None:
            print("📝 Initializing CLAUDE.md monitoring...")
            self.store_hash(current_hash)
            self.initialize_changelog(current_hash)
            return False

        # Check if changed
        if current_hash != stored_hash:
            print("🔍 Change detected in CLAUDE.md")

            # Try to get old content (for now, we can't retrieve it without versioning)
            # In production, you'd use git or a backup system
            old_content = ""  # Placeholder

            # Get user info
            user_info = self.get_current_user()

            # Log the change
            self.log_change(old_content, current_content, user_info)

            # Update stored hash
            self.store_hash(current_hash)

            # Trigger auto-restore if needed
            from tools.auto_restore_protection import AutoRestoreProtection
            protection = AutoRestoreProtection()
            protection.auto_restore_protected_content(monitor=self)

            return True

        return False

    def initialize_changelog(self, initial_hash):
        """Initialize the changelog file"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")

        initial_entry = f"""This changelog captures every change made to CLAUDE.md
==========================================
MONITORING INITIALIZED: {timestamp}
==========================================
Initial Hash: {initial_hash}
Status: Monitoring active
Protection: Enabled for sections between critical tags

"""

        with open(self.changelog_path, 'w', encoding='utf-8') as f:
            f.write(initial_entry)

    def watch_file(self, interval=5):
        """Continuously watch for changes (blocking)"""
        print(f"👁️ Watching CLAUDE.md for changes (checking every {interval}s)...")
        print("Press Ctrl+C to stop")

        try:
            while True:
                if self.check_for_changes():
                    print("✅ Change processed")
                time.sleep(interval)
        except KeyboardInterrupt:
            print("\n🛑 Monitoring stopped")


def main():
    """Main execution function"""
    import sys

    monitor = ClaudeMdMonitor()

    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == 'check':
            print("🔍 Checking for changes...")
            if monitor.check_for_changes():
                print("✅ Changes detected and logged")
            else:
                print("✅ No changes detected")

        elif command == 'watch':
            monitor.watch_file()

        elif command == 'init':
            print("📝 Initializing monitoring system...")
            content = monitor.claude_md_path.read_text(encoding='utf-8')
            file_hash = monitor.get_file_hash(content)
            monitor.store_hash(file_hash)
            monitor.initialize_changelog(file_hash)
            print("✅ Monitoring initialized")

        elif command == 'restore':
            print("🛡️ Running auto-restore check...")
            from tools.auto_restore_protection import AutoRestoreProtection
            protection = AutoRestoreProtection()
            if protection.auto_restore_protected_content(monitor=monitor):
                print("✅ Protected section restored")
            else:
                print("✅ No unauthorized changes detected")

        else:
            print(f"❌ Unknown command: {command}")
            print("Available commands: check, watch, init, restore")
            sys.exit(1)
    else:
        print("CLAUDE.md Monitor System")
        print("Usage:")
        print("  python tools/monitor_claude_md.py check    # Check for changes once")
        print("  python tools/monitor_claude_md.py watch    # Continuously watch for changes")
        print("  python tools/monitor_claude_md.py init     # Initialize monitoring")
        print("  python tools/monitor_claude_md.py restore  # Run auto-restore check")


if __name__ == "__main__":
    main()
