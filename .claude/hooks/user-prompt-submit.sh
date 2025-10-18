#!/bin/bash
##
## User Prompt Submit Hook
##
## This hook runs when the user submits a prompt to Claude.
## It orchestrates validation checks by calling specialized hook modules.
##
## Hook Event: UserPromptSubmit
## Trigger: Before agent processes user input
## Purpose: Guide agent behavior and enforce project standards
##

set -euo pipefail

# Get the directory where this script is located
HOOKS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Read the hook input (JSON) from stdin
HOOK_INPUT=$(cat)

# Extract user prompt from JSON
USER_PROMPT=$(echo "$HOOK_INPUT" | jq -r '.userPrompt // ""')

# Prepare response components
COMMUNICATION_GUIDANCE=""
IMPLEMENTATION_GUIDANCE=""

# Call communication guidance hook
if [[ -f "$HOOKS_DIR/modules/communication_guidance.sh" ]]; then
    COMMUNICATION_GUIDANCE=$(echo "$HOOK_INPUT" | "$HOOKS_DIR/modules/communication_guidance.sh")
fi

# Call implementation guidance hook
if [[ -f "$HOOKS_DIR/modules/implementation_guidance.sh" ]]; then
    IMPLEMENTATION_GUIDANCE=$(echo "$HOOK_INPUT" | "$HOOKS_DIR/modules/implementation_guidance.sh")
fi

# Call workflow reminders hook (optional - comment out to disable)
if [[ -f "$HOOKS_DIR/modules/workflow_reminders.sh" ]]; then
    WORKFLOW_REMINDERS=$(echo "$HOOK_INPUT" | "$HOOKS_DIR/modules/workflow_reminders.sh")
fi

# Combine guidance messages
COMBINED_MESSAGE=""

if [[ -n "$COMMUNICATION_GUIDANCE" ]]; then
    COMBINED_MESSAGE="$COMMUNICATION_GUIDANCE"
fi

if [[ -n "$IMPLEMENTATION_GUIDANCE" ]]; then
    if [[ -n "$COMBINED_MESSAGE" ]]; then
        COMBINED_MESSAGE="$COMBINED_MESSAGE

$IMPLEMENTATION_GUIDANCE"
    else
        COMBINED_MESSAGE="$IMPLEMENTATION_GUIDANCE"
    fi
fi

if [[ -n "${WORKFLOW_REMINDERS:-}" ]]; then
    if [[ -n "$COMBINED_MESSAGE" ]]; then
        COMBINED_MESSAGE="$COMBINED_MESSAGE

$WORKFLOW_REMINDERS"
    else
        COMBINED_MESSAGE="$WORKFLOW_REMINDERS"
    fi
fi

# Output JSON response
if [[ -n "$COMBINED_MESSAGE" ]]; then
    jq -n --arg msg "$COMBINED_MESSAGE" '{
        hookSpecificOutput: {
            message: $msg
        }
    }'
else
    # No guidance needed
    echo '{}'
fi

exit 0
