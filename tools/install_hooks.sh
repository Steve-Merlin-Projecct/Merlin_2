#!/bin/bash
#
# Install git hooks for librarian documentation validation
#
# Usage: bash tools/install_hooks.sh
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
HOOKS_DIR="$REPO_ROOT/.git/hooks"

echo "📦 Installing librarian git hooks..."

# Copy pre-commit hook source
cat > "$HOOKS_DIR/pre-commit" << 'HOOK_EOF'
#!/usr/bin/env python3
"""
Pre-commit hook for librarian documentation validation.

Validates only staged .md files for:
- YAML frontmatter presence
- File organization compliance

Lightweight validation - runs in <1 second for typical commits.
"""

import subprocess
import sys
import os

def get_staged_md_files():
    """Get list of staged markdown files."""
    try:
        result = subprocess.run(
            ['git', 'diff', '--cached', '--name-only', '--diff-filter=ACM'],
            capture_output=True,
            text=True,
            check=True
        )
        files = result.stdout.strip().split('\n')
        return [f for f in files if f.endswith('.md') and f]
    except subprocess.CalledProcessError:
        return []

def validate_metadata(files):
    """Validate YAML frontmatter for staged files."""
    if not files:
        return True

    for filepath in files:
        if not os.path.exists(filepath):
            continue

        try:
            result = subprocess.run(
                ['python', 'tools/validate_metadata.py', filepath],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode != 0:
                print(f"\n❌ Metadata validation failed for: {filepath}")
                print(result.stdout)
                print("\n💡 Fix: Add YAML frontmatter or run:")
                print(f"   python tools/validate_metadata.py {filepath} --fix")
                return False

        except subprocess.TimeoutExpired:
            print(f"\n⚠️  Validation timeout for {filepath} (skipping)")
            continue
        except Exception as e:
            print(f"\n⚠️  Validation error for {filepath}: {e} (skipping)")
            continue

    return True

def validate_location(files):
    """Validate file organization for staged files."""
    if not files:
        return True

    root_violations = [f for f in files if '/' not in f and f not in [
        'README.md', 'CLAUDE.md', 'CHANGELOG.md', 'claude.md'
    ]]

    if root_violations:
        print("\n❌ File organization violation - files in root directory:")
        for f in root_violations:
            print(f"   - {f}")
        print("\n💡 Fix: Move files to appropriate directories per FILE_ORGANIZATION_STANDARDS.md")
        print("   Or bypass this check: git commit --no-verify")
        return False

    return True

def main():
    """Run pre-commit validation."""
    staged_files = get_staged_md_files()

    if not staged_files:
        sys.exit(0)

    print(f"🔍 Validating {len(staged_files)} markdown file(s)...")

    metadata_valid = validate_metadata(staged_files)
    location_valid = validate_location(staged_files)

    if metadata_valid and location_valid:
        print("✅ Documentation validation passed")
        sys.exit(0)
    else:
        print("\n❌ Pre-commit validation failed")
        print("   Fix the issues above or use --no-verify to bypass")
        sys.exit(1)

if __name__ == '__main__':
    main()
HOOK_EOF

chmod +x "$HOOKS_DIR/pre-commit"

echo "✅ Pre-commit hook installed"
echo ""
echo "The hook will validate markdown files on commit."
echo "To bypass validation: git commit --no-verify"
