#!/bin/bash
##
## Workflow Reminders Module (OPTIONAL)
##
## Provides gentle reminders about project-specific workflows.
## These are already handled by specialized agents but reminders can help.
##
## To disable: Comment out the call in user-prompt-submit.sh
##

set -euo pipefail

# Read hook input from stdin
HOOK_INPUT=$(cat)

# Extract user prompt
USER_PROMPT=$(echo "$HOOK_INPUT" | jq -r '.userPrompt // ""')

# Convert to lowercase for case-insensitive matching
USER_PROMPT_LOWER=$(echo "$USER_PROMPT" | tr '[:upper:]' '[:lower:]')

# Git operation patterns (git-orchestrator handles these)
GIT_PATTERNS=(
    "commit"
    "push"
    "git commit"
    "git push"
    "merge"
    "create pr"
    "pull request"
)

# Database schema patterns (database_tools handles these)
SCHEMA_PATTERNS=(
    "schema"
    "database change"
    "alter table"
    "add column"
    "modify database"
    "update schema"
    "create table"
    "drop table"
)

# Check for git operations
FOUND_GIT=false
for pattern in "${GIT_PATTERNS[@]}"; do
    if echo "$USER_PROMPT_LOWER" | grep -q "$pattern"; then
        FOUND_GIT=true
        break
    fi
done

# Check for schema operations
FOUND_SCHEMA=false
for pattern in "${SCHEMA_PATTERNS[@]}"; do
    if echo "$USER_PROMPT_LOWER" | grep -q "$pattern"; then
        FOUND_SCHEMA=true
        break
    fi
done

# Generate gentle reminders
REMINDERS=""

if [[ "$FOUND_GIT" == true ]]; then
    REMINDERS+="💡 Git Workflow Reminder:
Consider using git-orchestrator agent for commits/pushes
(Handles tests, validation, and remote push automatically)

"
fi

if [[ "$FOUND_SCHEMA" == true ]]; then
    REMINDERS+="💡 Database Schema Reminder:
After PostgreSQL changes, run: python database_tools/update_schema.py
(Generates models, schemas, CRUD ops, and documentation)

"
fi

# Output reminders if any
echo "$REMINDERS"