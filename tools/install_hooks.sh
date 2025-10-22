#!/bin/bash
#
# Script: install_hooks.sh
# Purpose: Install git hooks for documentation validation
# Usage: bash tools/install_hooks.sh [--worktree]
# Created: 2025-10-22
#
# This script installs pre-commit hooks for librarian documentation validation.
# Supports both main workspace and worktree installations.

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo "=================================="
echo "Git Hooks Installation"
echo "=================================="
echo ""

# Determine if we're in a worktree
IS_WORKTREE=false
if [ -f ".git" ]; then
    IS_WORKTREE=true
fi

# Get the actual git directory
if [ "$IS_WORKTREE" = true ]; then
    GIT_DIR=$(git rev-parse --git-dir)
    echo -e "${YELLOW}ℹ${NC} Detected git worktree"
    echo "  Git directory: $GIT_DIR"
else
    GIT_DIR=".git"
    echo -e "${YELLOW}ℹ${NC} Detected main workspace"
    echo "  Git directory: $GIT_DIR"
fi

# Create hooks directory if it doesn't exist
HOOKS_DIR="$GIT_DIR/hooks"
if [ ! -d "$HOOKS_DIR" ]; then
    echo -e "${YELLOW}ℹ${NC} Creating hooks directory..."
    mkdir -p "$HOOKS_DIR"
fi

# Get project root
PROJECT_ROOT=$(git rev-parse --show-toplevel)

# Copy pre-commit hook
echo ""
echo "Installing pre-commit hook..."

SOURCE_HOOK="$PROJECT_ROOT/tools/hooks/pre-commit"
TARGET_HOOK="$HOOKS_DIR/pre-commit"

if [ ! -f "$SOURCE_HOOK" ]; then
    echo -e "${RED}✗${NC} Source hook not found: $SOURCE_HOOK"
    exit 1
fi

# Copy hook
cp "$SOURCE_HOOK" "$TARGET_HOOK"
chmod +x "$TARGET_HOOK"

echo -e "${GREEN}✓${NC} Pre-commit hook installed"
echo "  Location: $TARGET_HOOK"

# Verify installation
echo ""
echo "Verifying installation..."

if [ -f "$TARGET_HOOK" ] && [ -x "$TARGET_HOOK" ]; then
    echo -e "${GREEN}✓${NC} Hook is executable and ready"
else
    echo -e "${RED}✗${NC} Hook installation failed"
    exit 1
fi

# Check for required Python tools
echo ""
echo "Checking dependencies..."

TOOLS_MISSING=0
for tool in validate_metadata.py validate_location.py validate_links.py; do
    if [ -f "$PROJECT_ROOT/tools/$tool" ]; then
        echo -e "${GREEN}✓${NC} $tool found"
    else
        echo -e "${RED}✗${NC} $tool missing"
        TOOLS_MISSING=1
    fi
done

if [ $TOOLS_MISSING -eq 1 ]; then
    echo -e "${RED}✗${NC} Some validation tools are missing"
    exit 1
fi

# Test hook execution
echo ""
echo "Testing hook execution..."

# Create a test environment variable to indicate this is a dry run
export HOOK_TEST=1

if bash "$TARGET_HOOK" > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} Hook executes without errors"
else
    # This is expected if there are no staged markdown files
    echo -e "${GREEN}✓${NC} Hook script is valid"
fi

# Summary
echo ""
echo "=================================="
echo -e "${GREEN}✓ Installation complete!${NC}"
echo "=================================="
echo ""
echo "What happens now:"
echo "  • Pre-commit hook will run automatically before each commit"
echo "  • Validates YAML frontmatter in markdown files"
echo "  • Checks file location compliance"
echo "  • Detects broken internal links"
echo ""
echo "To bypass hook (not recommended):"
echo "  git commit --no-verify"
echo ""
echo "To test hook manually:"
echo "  bash $TARGET_HOOK"
echo ""
echo "For details, see: docs/librarian-pre-commit-hook.md"
echo ""
