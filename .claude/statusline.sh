#!/bin/bash
# Claude Code Statusline Script
# Displays project context information in the Claude Code statusline

# Always use workspace directory
cd /workspace

# Get git branch
if git rev-parse --git-dir > /dev/null 2>&1; then
    BRANCH=$(git branch --show-current 2>/dev/null || echo "detached")
    GIT_STATUS=$(git status --porcelain 2>/dev/null | wc -l)
    if [ "$GIT_STATUS" -gt 0 ]; then
        GIT_INFO="git:${BRANCH} (${GIT_STATUS})"
    else
        GIT_INFO="git:${BRANCH}"
    fi
else
    GIT_INFO="No git"
fi

# Project info
PROJECT_NAME="Merlin Job App"
# Read version from VERSION file
if [ -f "VERSION" ]; then
    VERSION="v$(cat VERSION)"
else
    VERSION="v?.?.?"
fi

# Build statusline output
# Format: Project Version | Git
OUTPUT="${PROJECT_NAME} ${VERSION} | ${GIT_INFO}"

echo "$OUTPUT"
