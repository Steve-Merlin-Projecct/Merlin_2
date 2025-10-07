#!/bin/bash
# Claude Code Statusline Script
# Displays project context information in the Claude Code statusline

# Change to workspace directory
cd /workspace/.trees/claude-config 2>/dev/null || cd /workspace

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

# Get Python version
if command -v python &> /dev/null; then
    PYTHON_VERSION=$(python --version 2>&1 | cut -d' ' -f2)
    PYTHON_INFO="🐍 ${PYTHON_VERSION}"
else
    PYTHON_INFO="No Python"
fi

# Check if virtual environment is active
if [ -n "$VIRTUAL_ENV" ]; then
    VENV_NAME=$(basename "$VIRTUAL_ENV")
    VENV_INFO="📦 ${VENV_NAME}"
else
    VENV_INFO=""
fi

# Check database connection (quick check)
# Check both .env and .env.example for DATABASE_URL
if [ -f ".env" ] && grep -q "DATABASE_URL" .env 2>/dev/null; then
    DB_INFO="db:connected"
elif [ -f ".env.example" ]; then
    # .env.example exists but no .env - that's normal for worktrees
    DB_INFO="db:template"
else
    DB_INFO="db:none"
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
# Format: Project | Git | Python | VEnv | DB
OUTPUT="${PROJECT_NAME} ${VERSION} | ${GIT_INFO} | ${PYTHON_INFO}"

if [ -n "$VENV_INFO" ]; then
    OUTPUT="${OUTPUT} | ${VENV_INFO}"
fi

OUTPUT="${OUTPUT} | ${DB_INFO}"

echo "$OUTPUT"
