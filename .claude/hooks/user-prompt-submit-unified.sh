#!/bin/bash
##
## Unified User Prompt Submit Hook
##
## Single orchestrator that calls the behavioral guidance module
## which is now the SINGLE SOURCE OF TRUTH for all behavioral instructions
##

set -euo pipefail

# Get the directory where this script is located
HOOKS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Read the hook input (JSON) from stdin
HOOK_INPUT=$(cat)

# Call the unified behavioral guidance module
GUIDANCE=""
if [[ -f "$HOOKS_DIR/modules/behavioral_guidance.sh" ]]; then
    GUIDANCE=$(echo "$HOOK_INPUT" | "$HOOKS_DIR/modules/behavioral_guidance.sh")
fi

# Optional: Call workflow reminders (gentle nudges about git/database)
WORKFLOW=""
if [[ -f "$HOOKS_DIR/modules/workflow_reminders.sh" ]]; then
    WORKFLOW=$(echo "$HOOK_INPUT" | "$HOOKS_DIR/modules/workflow_reminders.sh" 2>/dev/null || echo "")
fi

# Combine messages
COMBINED=""
if [[ -n "$GUIDANCE" ]]; then
    COMBINED="$GUIDANCE"
fi

if [[ -n "$WORKFLOW" ]]; then
    if [[ -n "$COMBINED" ]]; then
        COMBINED="$COMBINED

$WORKFLOW"
    else
        COMBINED="$WORKFLOW"
    fi
fi

# Output JSON response
if [[ -n "$COMBINED" ]]; then
    # Use Python for reliable JSON encoding
    echo "$COMBINED" | python3 -c "
import json
import sys
message = sys.stdin.read()
print(json.dumps({'hookSpecificOutput': {'message': message}}))
" 2>/dev/null || echo '{}'
else
    echo '{}'
fi

exit 0