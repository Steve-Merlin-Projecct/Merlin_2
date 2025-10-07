#!/bin/bash
# Checkpoint Script
# Automatically saves progress when a section of tasks is complete
# Usage: ./scripts/checkpoint.sh "Section Name" "Brief description"

set -e  # Exit on error

SECTION_NAME="$1"
DESCRIPTION="$2"

if [ -z "$SECTION_NAME" ]; then
    echo "Error: Section name required"
    echo "Usage: ./scripts/checkpoint.sh \"Section Name\" \"Brief description\""
    exit 1
fi

echo "=== Checkpoint: $SECTION_NAME ==="
echo ""

# 1. Run tests
echo "Step 1: Running test suite..."
if command -v pytest &> /dev/null; then
    pytest --tb=short -q || {
        echo "❌ Tests failed! Cannot checkpoint."
        echo "Fix failing tests before checkpointing."
        exit 1
    }
elif command -v npm &> /dev/null && [ -f "package.json" ]; then
    npm test || {
        echo "❌ Tests failed! Cannot checkpoint."
        exit 1
    }
else
    echo "⚠️  No test framework detected. Skipping tests."
fi
echo "✅ Tests passed"
echo ""

# 2. Run database schema automation if database files changed
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
    else
        echo "⚠️  No schema automation script found"
    fi
else
    echo "No database changes detected"
fi
echo ""

# 3. Verify documentation exists
echo "Step 3: Checking for documentation..."
STAGED_FILES=$(git diff --cached --name-only)
NEW_CODE_FILES=$(echo "$STAGED_FILES" | grep -E '\.(py|js|ts|go|java|rb)$' | grep -v test | grep -v spec || true)

if [ -n "$NEW_CODE_FILES" ]; then
    echo "New code files detected. Checking for documentation..."

    # Check if any .md files are staged in docs/component_docs/
    DOC_FILES=$(echo "$STAGED_FILES" | grep "docs/component_docs/" || true)

    if [ -z "$DOC_FILES" ]; then
        echo "⚠️  Warning: New code added but no component documentation found"
        echo "Consider adding documentation to docs/component_docs/"
    else
        echo "✅ Documentation found: $DOC_FILES"
    fi
fi
echo ""

# 4. Display what will be committed
echo "Step 4: Files to be committed:"
git diff --cached --name-status
echo ""

# 5. Ask for confirmation
echo "Ready to create checkpoint for: $SECTION_NAME"
echo "Description: $DESCRIPTION"
echo ""
read -p "Proceed with checkpoint? (y/n) " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Checkpoint cancelled"
    exit 1
fi

# 6. Create checkpoint commit (not pushed)
echo "Creating checkpoint commit..."
git commit -m "checkpoint: $SECTION_NAME

$DESCRIPTION

This is a checkpoint commit marking completion of section tasks.
All tests passing. Not yet ready for final commit.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"

echo ""
echo "✅ Checkpoint created successfully!"
echo ""
echo "To view: git log -1"
echo "To amend: git commit --amend"
echo ""
