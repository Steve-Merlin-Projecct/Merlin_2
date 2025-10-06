#!/usr/bin/env python3
"""
Test script for auto-restore protection system
Demonstrates automatic restoration of protected content
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path

# Add parent directory to path to import monitor
sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.monitor_replit_md import ReplitMdMonitor
from tools.auto_restore_protection import AutoRestoreProtection

def test_auto_restore_protection():
    """Test the auto-restore protection system"""
    print("🧪 Testing Auto-Restore Protection System")
    print("=" * 50)
    
    monitor = ReplitMdMonitor()
    auto_restore = AutoRestoreProtection()
    
    # Backup original replit.md
    original_content = monitor.replit_md_path.read_text(encoding='utf-8')
    backup_path = monitor.replit_md_path.with_suffix('.backup')
    
    try:
        # Create backup
        shutil.copy2(monitor.replit_md_path, backup_path)
        print(f"✅ Created backup: {backup_path}")
        
        # Test 1: Simulate agent modification of protected section
        print("\\n📝 Test 1: Simulating agent modification of protected section...")
        
        # Modify the protected section
        modified_content = original_content.replace(
            "Before implementing changes, explain what you're going to do and why.",
            "AGENT MODIFIED: This content should be restored by auto-restore!"
        )
        
        # Write modified content
        monitor.replit_md_path.write_text(modified_content, encoding='utf-8')
        print("   Agent simulation: Modified protected content")
        
        # Run auto-restore
        print("   Running auto-restore check...")
        if auto_restore.auto_restore_protected_content(monitor):
            print("   ✅ Auto-restore successfully detected and restored protected content")
        else:
            print("   ❌ Auto-restore failed to detect/restore protected content")
        
        # Verify restoration
        restored_content = monitor.replit_md_path.read_text(encoding='utf-8')
        if "AGENT MODIFIED" not in restored_content:
            print("   ✅ Protected content successfully restored")
        else:
            print("   ❌ Protected content was not restored")
        
        # Test 2: Test with non-protected section modification
        print("\\n📝 Test 2: Testing modification outside protected section...")
        
        # Modify non-protected section (after the end tag)
        non_protected_mod = restored_content.replace(
            "## System Architecture",
            "## System Architecture (Modified by Agent)"
        )
        
        monitor.replit_md_path.write_text(non_protected_mod, encoding='utf-8')
        print("   Agent simulation: Modified non-protected content")
        
        # Run auto-restore
        print("   Running auto-restore check...")
        restore_result = auto_restore.auto_restore_protected_content(monitor)
        if not restore_result:
            print("   ✅ Auto-restore correctly ignored non-protected modifications")
        else:
            print("   ❌ Auto-restore incorrectly acted on non-protected content")
        
        # Test 3: Test change detection
        print("\\n📝 Test 3: Testing change detection system...")
        
        # Run full change check
        if monitor.check_for_changes():
            print("   ✅ Change detection working")
        else:
            print("   ⚠️ No changes detected (may be expected)")
        
    except Exception as e:
        print(f"❌ Test error: {e}")
    
    finally:
        # Restore original content
        if backup_path.exists():
            shutil.copy2(backup_path, monitor.replit_md_path)
            backup_path.unlink()  # Remove backup
            print(f"\\n🔄 Restored original replit.md content")
        
    print("\\n🏁 Test completed!")

def demonstrate_usage():
    """Demonstrate how to use the auto-restore system"""
    print("\\n📚 Auto-Restore Protection System Usage:")
    print("=" * 40)
    print("Manual commands:")
    print("  python tools/monitor_replit_md.py restore  # Run protection check")
    print("  python tools/monitor_replit_md.py check   # Check for changes (includes auto-restore)")
    print("  python tools/monitor_replit_md.py watch   # Continuous monitoring")
    print("")
    print("Automatic protection:")
    print("  - Auto-restore automatically runs when agent changes are detected")
    print("  - Protected section is between the critical comment tags")
    print("  - Reference content stored in: tools/protected_replit_content.md")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == 'demo':
        demonstrate_usage()
    else:
        test_auto_restore_protection()
        demonstrate_usage()