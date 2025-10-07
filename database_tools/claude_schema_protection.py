#!/usr/bin/env python3
"""
Claude Code hook for database schema file protection.
Intercepts Edit/Write operations on auto-generated files and enforces automation workflow.

Design Note:
This hook blocks Claude (the AI agent) from directly editing protected files using Edit/Write tools.
Automation scripts (update_schema.py, etc.) use Python's file I/O which bypasses Claude Code hooks
entirely, so they don't need whitelisting. The hook only sees Claude's tool calls, not Python's
file operations.
"""

import json
import sys
import os
from pathlib import Path
from typing import Dict

class SchemaProtectionHook:
    """Hook to protect auto-generated database schema files from manual edits"""

    # Protected files that should never be manually edited via Claude's Edit/Write tools
    PROTECTED_FILES = [
        'frontend_templates/database_schema.html',
        'database_tools/docs/database_schema.json',
        'database_tools/docs/database_schema.md',
        'database_tools/generated/models.py',
        'database_tools/generated/schemas.py',
        'database_tools/generated/crud.py',
        'database_tools/generated/routes.py'
    ]

    def __init__(self, hook_input: Dict):
        self.hook_input = hook_input
        self.tool_name = hook_input.get('tool_name', '')
        self.tool_input = hook_input.get('tool_input', {})
        self.cwd = hook_input.get('cwd', '')

    def should_intercept(self) -> bool:
        """Check if this tool use should be intercepted"""
        # Only intercept Edit and Write tools
        if self.tool_name not in ['Edit', 'Write']:
            return False

        # Get the file path being modified
        file_path = self.tool_input.get('file_path', '')
        if not file_path:
            return False

        # Normalize to relative path
        rel_path = self._normalize_path(file_path)

        # Check if it's a protected file
        return any(protected in rel_path for protected in self.PROTECTED_FILES)

    def check_schema_status(self) -> Dict:
        """Check if schema has changed using enforce_automation"""
        try:
            sys.path.insert(0, os.path.join(self.cwd, 'database_tools'))
            from enforce_automation import AutomationEnforcement

            enforcement = AutomationEnforcement()
            return enforcement.check_schema_changes()
        except Exception as e:
            return {'error': str(e), 'schema_changed': False}

    def _normalize_path(self, file_path: str) -> str:
        """Normalize file path to relative path from workspace root"""
        # Handle absolute paths
        if file_path.startswith('//workspace/'):
            file_path = file_path.replace('//workspace/', '')
        elif file_path.startswith('/workspace/'):
            file_path = file_path.replace('/workspace/', '')

        # Remove .trees/claude-config prefix if present
        if '.trees/claude-config/' in file_path:
            file_path = file_path.split('.trees/claude-config/')[-1]

        return file_path

    def generate_response(self) -> Dict:
        """Generate appropriate hook response"""
        if not self.should_intercept():
            # Not a protected file - allow
            return {}

        # Protected file detected - block the edit and provide guidance
        schema_status = self.check_schema_status()
        file_path = self.tool_input.get('file_path', '')
        rel_path = self._normalize_path(file_path)

        # Build informative denial message
        message = f"""🛡️  DATABASE SCHEMA PROTECTION

❌ BLOCKED: Attempt to directly edit auto-generated file
📁 File: {rel_path}
🔧 Tool: {self.tool_name}

⚠️  This file is auto-generated from the PostgreSQL schema.
   Direct edits via Edit/Write tools are not allowed.

✅ CORRECT APPROACH:
   1. Make changes to PostgreSQL database schema
   2. Run: python database_tools/update_schema.py
   3. The automation script will regenerate this file
   4. Review and commit generated files

"""

        if schema_status.get('schema_changed'):
            message += """📊 SCHEMA STATUS: Changed (automation required)
   Your database schema has been modified.
   Run the automation workflow to update all files.

"""
        else:
            message += """📊 SCHEMA STATUS: Up to date
   If you need to make changes, modify the PostgreSQL schema first.

"""

        message += """💡 NOTE: Automation scripts use Python file I/O, not Claude tools,
   so they can modify these files without triggering this protection.

📚 See: docs/development/CLAUDE_CODE_SCHEMA_PROTECTION.md
"""

        return {
            "hookSpecificOutput": {
                "permissionDecision": "deny",
                "permissionDecisionReason": message
            }
        }

def main():
    """Hook entry point"""
    try:
        # Read hook input from stdin
        hook_input = json.loads(sys.stdin.read())

        # Create hook instance and generate response
        hook = SchemaProtectionHook(hook_input)
        response = hook.generate_response()

        # Output response
        print(json.dumps(response))
        sys.exit(0)

    except Exception as e:
        # On error, allow the operation but log
        error_response = {
            "hookSpecificOutput": {
                "permissionDecision": "allow",
                "permissionDecisionReason": f"Schema protection hook error: {e}"
            }
        }
        print(json.dumps(error_response))
        sys.exit(0)

if __name__ == "__main__":
    main()
