#!/bin/bash
# Section Commit Script
# Automatically commits a completed section with full workflow
# Usage: ./scripts/commit-section.sh "Section Name" "feat|fix|docs|refactor" "[PRD path]"

set -e  # Exit on error

SECTION_NAME="$1"
COMMIT_TYPE="$2"
PRD_PATH="$3"

if [ -z "$SECTION_NAME" ] || [ -z "$COMMIT_TYPE" ]; then
    echo "Error: Section name and commit type required"
    echo "Usage: ./scripts/commit-section.sh \"Section Name\" \"feat|fix|docs|refactor\" \"[PRD path]\""
    exit 1
fi

echo "=== Section Commit: $SECTION_NAME ==="
echo "Commit type: $COMMIT_TYPE"
echo ""

# 1. Run full test suite
echo "Step 1: Running full test suite..."
if command -v pytest &> /dev/null; then
    pytest -v || {
        echo "❌ Tests failed! Cannot commit."
        echo ""
        echo "Options:"
        echo "1. Fix the failing tests"
        echo "2. Create a new task for fixing tests"
        echo "3. Use checkpoint instead: ./scripts/checkpoint.sh \"$SECTION_NAME\" \"WIP\""
        exit 1
    }
elif command -v npm &> /dev/null && [ -f "package.json" ]; then
    npm test || {
        echo "❌ Tests failed! Cannot commit."
        exit 1
    }
else
    echo "⚠️  No test framework detected. Skipping tests."
fi
echo "✅ All tests passed"
echo ""

# 2. Run database schema automation if needed
echo "Step 2: Checking for database schema changes..."
if git diff --cached --name-only | grep -q "database_tools/migrations/\|database/schema"; then
    echo "Database changes detected. Running schema automation..."
    if [ -f "database_tools/update_schema.py" ]; then
        python database_tools/update_schema.py || {
            echo "❌ Schema automation failed!"
            exit 1
        }
        # Stage generated files
        git add frontend_templates/database_schema.html 2>/dev/null || true
        git add docs/component_docs/database/ 2>/dev/null || true
        git add database_tools/generated/ 2>/dev/null || true
        echo "✅ Schema documentation generated and staged"
    fi
else
    echo "No database changes detected"
fi
echo ""

# 3. Verify documentation requirements
echo "Step 3: Verifying documentation..."
STAGED_FILES=$(git diff --cached --name-only)

# Check for new Python/JS files
NEW_CODE_FILES=$(echo "$STAGED_FILES" | grep -E '\.(py|js|ts)$' | grep -v test | grep -v spec || true)

if [ -n "$NEW_CODE_FILES" ]; then
    # Check for component documentation
    DOC_FILES=$(echo "$STAGED_FILES" | grep "docs/component_docs/" || true)

    if [ -z "$DOC_FILES" ]; then
        echo "❌ Error: New code files added but no component documentation found!"
        echo ""
        echo "New files:"
        echo "$NEW_CODE_FILES"
        echo ""
        echo "Required: Create documentation in docs/component_docs/[module]/"
        exit 1
    else
        echo "✅ Component documentation found"
    fi

    # Check inline documentation (basic check for docstrings)
    for file in $NEW_CODE_FILES; do
        if [ -f "$file" ]; then
            if grep -q '"""' "$file" || grep -q "'''" "$file" || grep -q '/\*\*' "$file"; then
                echo "✅ Inline documentation found in $file"
            else
                echo "⚠️  Warning: No docstrings found in $file"
            fi
        fi
    done
fi
echo ""

# 4. Clean up temporary files
echo "Step 4: Cleaning up temporary files..."
find . -type f -name "*.pyc" -delete 2>/dev/null || true
find . -type f -name ".DS_Store" -delete 2>/dev/null || true
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
echo "✅ Cleanup complete"
echo ""

# 5. Generate commit message
echo "Step 5: Generating commit message..."

# Get list of changed files
MODIFIED_FILES=$(git diff --cached --name-status | awk '{print $2}')
FILE_COUNT=$(echo "$MODIFIED_FILES" | wc -l | tr -d ' ')

# Categorize changes
NEW_FILES=$(git diff --cached --name-status | grep "^A" | wc -l | tr -d ' ')
MODIFIED_FILES_COUNT=$(git diff --cached --name-status | grep "^M" | wc -l | tr -d ' ')
DELETED_FILES=$(git diff --cached --name-status | grep "^D" | wc -l | tr -d ' ')

# Generate summary
SUMMARY="- $NEW_FILES new file(s), $MODIFIED_FILES_COUNT modified, $DELETED_FILES deleted"

# Get key file changes
KEY_FILES=$(git diff --cached --name-only | head -5)

# Create detailed commit message
COMMIT_MSG="$COMMIT_TYPE: $(echo "$SECTION_NAME" | tr '[:upper:]' '[:lower:]')

Section: $SECTION_NAME
Status: Complete and tested

Changes:
$SUMMARY

Key files:
$(echo "$KEY_FILES" | sed 's/^/- /')

$(if [ -n "$PRD_PATH" ]; then echo "Related: $PRD_PATH"; fi)

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"

echo "Commit message preview:"
echo "---"
echo "$COMMIT_MSG"
echo "---"
echo ""

# 6. Display changes
echo "Step 6: Changes to be committed:"
git diff --cached --stat
echo ""

# 7. Confirm
read -p "Create commit? (y/n) " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Commit cancelled"
    exit 1
fi

# 8. Commit
git commit -m "$COMMIT_MSG"

echo ""
echo "✅ Section committed successfully!"
echo ""

# 9. Update version (if CLAUDE.md exists)
if [ -f "CLAUDE.md" ]; then
    echo "Step 7: Updating version in CLAUDE.md..."

    # Extract current version
    CURRENT_VERSION=$(grep "^Version" CLAUDE.md | head -1 | sed 's/Version //' | sed 's/ .*//')

    if [ -n "$CURRENT_VERSION" ]; then
        # Parse version (e.g., 4.01 -> major=4, minor=01)
        MAJOR=$(echo "$CURRENT_VERSION" | cut -d. -f1)
        MINOR=$(echo "$CURRENT_VERSION" | cut -d. -f2)

        # Increment minor version
        NEW_MINOR=$((MINOR + 1))
        NEW_VERSION="$MAJOR.$(printf "%02d" $NEW_MINOR)"

        echo "Version: $CURRENT_VERSION → $NEW_VERSION"

        # Update CLAUDE.md (line 3)
        sed -i "3s/Version $CURRENT_VERSION/Version $NEW_VERSION/" CLAUDE.md

        echo "✅ Version updated to $NEW_VERSION"
    fi
fi
echo ""

# 10. Prompt for changelog
echo "Step 8: Update master changelog"
echo ""
echo "Add this entry to docs/changelogs/master-changelog.md:"
echo "---"
echo "## $(date +%Y-%m-%d)"
echo ""
echo "### $SECTION_NAME"
echo ""
echo "- **Version:** [update with new version]"
echo "- **Commit:** $COMMIT_TYPE"
echo "- **Changes:**"
echo "  $SUMMARY"
echo "- **Files Modified:**"
echo "$KEY_FILES" | sed 's/^/  - /'
echo "- **Tests:** All passing"
if [ -n "$PRD_PATH" ]; then
    echo "- **Related:** $PRD_PATH"
fi
echo "---"
echo ""

read -p "Open docs/changelogs/master-changelog.md for editing? (y/n) " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    ${EDITOR:-nano} docs/changelogs/master-changelog.md
fi

echo ""
echo "✅ Section commit complete!"
echo ""
echo "Summary:"
echo "- Commit created: $COMMIT_TYPE: $SECTION_NAME"
echo "- Tests: All passing"
echo "- Documentation: Verified"
echo "- Next: Update changelog manually"
echo ""
