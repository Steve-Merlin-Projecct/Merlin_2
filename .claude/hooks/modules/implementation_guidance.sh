#!/bin/bash
##
## Implementation Guidance Module
##
## Reminds agent of core implementation principles from CLAUDE.md:
## - Explain approach BEFORE implementing
## - Break down complex tasks
## - Add comprehensive inline documentation
## - Use TodoWrite for multi-step tasks
##

set -euo pipefail

# Read hook input from stdin
HOOK_INPUT=$(cat)

# Extract user prompt
USER_PROMPT=$(echo "$HOOK_INPUT" | jq -r '.userPrompt // ""')

# Convert to lowercase for case-insensitive matching
USER_PROMPT_LOWER=$(echo "$USER_PROMPT" | tr '[:upper:]' '[:lower:]')

# Implementation command patterns
IMPLEMENTATION_PATTERNS=(
    "fix"
    "update"
    "create"
    "implement"
    "build"
    "make"
    "add"
    "remove"
    "delete"
    "modify"
    "change"
    "refactor"
    "optimize"
    "debug"
    "solve"
    "set up"
    "configure"
    "install"
    "deploy"
)

# Complex task indicators (likely need TodoWrite)
COMPLEX_INDICATORS=(
    "multiple"
    "several"
    "list of"
    "all of"
    "each"
    "every"
    "complete"
    "full"
    "entire"
    "comprehensive"
    "step by step"
    "and then"
    "after that"
    "finally"
)

# Check for implementation commands
FOUND_IMPLEMENTATION=false
for pattern in "${IMPLEMENTATION_PATTERNS[@]}"; do
    if echo "$USER_PROMPT_LOWER" | grep -qw "$pattern"; then
        FOUND_IMPLEMENTATION=true
        break
    fi
done

# Check for complex task indicators
FOUND_COMPLEX=false
for indicator in "${COMPLEX_INDICATORS[@]}"; do
    if echo "$USER_PROMPT_LOWER" | grep -q "$indicator"; then
        FOUND_COMPLEX=true
        break
    fi
done

# Check if user is giving numbered/bulleted list
HAS_LIST=false
if echo "$USER_PROMPT" | grep -qE '(^|\n)[0-9]+\.|^-\s|^\*\s|^\+\s'; then
    HAS_LIST=true
fi

# Generate appropriate guidance
GUIDANCE=""

if [[ "$FOUND_IMPLEMENTATION" == true ]]; then
    GUIDANCE+="🔨 IMPLEMENTATION MODE: Follow core principles from CLAUDE.md

📝 BEFORE IMPLEMENTING:
1. Explain what you're going to do and why
2. Break down complex tasks into clear, focused steps
3. Ask for clarification if requirements are unclear

"
fi

if [[ "$FOUND_COMPLEX" == true ]] || [[ "$HAS_LIST" == true ]]; then
    GUIDANCE+="📊 COMPLEX TASK DETECTED: Multiple steps/items found

⚡ REQUIRED: Use TodoWrite tool to:
- Track each step/item as a separate todo
- Mark tasks 'in_progress' BEFORE starting
- Mark 'completed' IMMEDIATELY after finishing
- Maintain ONE in_progress task at a time

"
fi

# Always remind about documentation for implementation
if [[ "$FOUND_IMPLEMENTATION" == true ]]; then
    GUIDANCE+="📚 DOCUMENTATION REQUIREMENTS:
- Add comprehensive docstrings to all functions/classes
- Explain relationships between components
- Document expected behaviors and edge cases
- Use comments to explain 'why' not just 'what'
- Update CLAUDE.md if gaining new project understanding

"
fi

# Output guidance if any was generated
if [[ -n "$GUIDANCE" ]]; then
    echo "$GUIDANCE"
else
    echo ""
fi