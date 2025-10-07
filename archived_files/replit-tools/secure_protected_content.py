#!/usr/bin/env python3
"""
Secure the protected content reference file
Makes it read-only to provide additional protection
"""

import os
import stat
from pathlib import Path

def secure_protected_file():
    """Make the protected content file read-only"""
    project_root = Path(__file__).parent.parent
    protected_file = project_root / "tools/protected_replit_content.md"
    
    if not protected_file.exists():
        print(f"❌ Protected content file not found: {protected_file}")
        return False
    
    try:
        # Get current permissions
        current_permissions = protected_file.stat().st_mode
        
        # Make read-only (remove write permissions for owner, group, others)
        read_only_permissions = current_permissions & ~stat.S_IWUSR & ~stat.S_IWGRP & ~stat.S_IWOTH
        
        # Apply new permissions
        protected_file.chmod(read_only_permissions)
        
        print(f"🔒 Protected content file secured (read-only): {protected_file}")
        print(f"   Permissions: {oct(protected_file.stat().st_mode)}")
        return True
        
    except Exception as e:
        print(f"❌ Error securing file: {e}")
        return False

def unsecure_protected_file():
    """Make the protected content file writable again"""
    project_root = Path(__file__).parent.parent
    protected_file = project_root / "tools/protected_replit_content.md"
    
    if not protected_file.exists():
        print(f"❌ Protected content file not found: {protected_file}")
        return False
    
    try:
        # Make writable (add write permission for owner)
        protected_file.chmod(0o644)  # rw-r--r--
        
        print(f"🔓 Protected content file made writable: {protected_file}")
        print(f"   Permissions: {oct(protected_file.stat().st_mode)}")
        return True
        
    except Exception as e:
        print(f"❌ Error unsecuring file: {e}")
        return False

def check_file_status():
    """Check the current status of the protected content file"""
    project_root = Path(__file__).parent.parent
    protected_file = project_root / "tools/protected_replit_content.md"
    
    if not protected_file.exists():
        print(f"❌ Protected content file not found: {protected_file}")
        return
    
    stat_info = protected_file.stat()
    permissions = oct(stat_info.st_mode)
    is_writable = os.access(protected_file, os.W_OK)
    
    print(f"📄 Protected content file: {protected_file}")
    print(f"   Permissions: {permissions}")
    print(f"   Writable: {'Yes' if is_writable else 'No'}")
    print(f"   Size: {stat_info.st_size} bytes")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == 'secure':
            secure_protected_file()
        elif command == 'unsecure':
            unsecure_protected_file()
        elif command == 'status':
            check_file_status()
        else:
            print(f"❌ Unknown command: {command}")
            print("Available commands: secure, unsecure, status")
    else:
        print("Protected Content Security Tool")
        print("Usage:")
        print("  python tools/secure_protected_content.py secure   # Make file read-only")
        print("  python tools/secure_protected_content.py unsecure # Make file writable")
        print("  python tools/secure_protected_content.py status   # Check file status")
        print("")
        print("Current status:")
        check_file_status()