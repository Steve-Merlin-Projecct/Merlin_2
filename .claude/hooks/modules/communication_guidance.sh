#!/bin/bash
##
## Communication Guidance Module
##
## Detects question patterns in user prompts and reminds agent to:
## - Provide analysis instead of implementation for questions
## - Ask for permission before making changes
## - Follow the Question Detection Protocol from CLAUDE.md
##

set -euo pipefail

# Read hook input from stdin
HOOK_INPUT=$(cat)

# Extract user prompt
USER_PROMPT=$(echo "$HOOK_INPUT" | jq -r '.userPrompt // ""')

# Convert to lowercase for case-insensitive matching
USER_PROMPT_LOWER=$(echo "$USER_PROMPT" | tr '[:upper:]' '[:lower:]')

# Question word patterns (CRITICAL: Question Detection Protocol)
QUESTION_WORDS=(
    "what"
    "how"
    "why"
    "which"
    "should"
    "can you explain"
    "could you explain"
    "would you explain"
    "does"
    "is there"
    "are there"
)

# Recommendation/evaluation patterns
RECOMMENDATION_PATTERNS=(
    "recommend"
    "suggestion"
    "options"
    "best practice"
    "trade-off"
    "pros and cons"
    "compare"
    "evaluate"
    "assessment"
    "review"
    "analyze"
    "understand"
)

# Compound statement patterns (problem + question)
COMPOUND_PATTERNS=(
    "broken.*explain"
    "failed.*why"
    "error.*what"
    "missing.*explain"
    "doesn't work.*why"
    "not working.*how"
)

# Check for question words
FOUND_QUESTION=false
for word in "${QUESTION_WORDS[@]}"; do
    if echo "$USER_PROMPT_LOWER" | grep -qw "$word"; then
        FOUND_QUESTION=true
        break
    fi
done

# Check for recommendation patterns
FOUND_RECOMMENDATION=false
for pattern in "${RECOMMENDATION_PATTERNS[@]}"; do
    if echo "$USER_PROMPT_LOWER" | grep -q "$pattern"; then
        FOUND_RECOMMENDATION=true
        break
    fi
done

# Check for compound statements
FOUND_COMPOUND=false
for pattern in "${COMPOUND_PATTERNS[@]}"; do
    if echo "$USER_PROMPT_LOWER" | grep -E "$pattern"; then
        FOUND_COMPOUND=true
        break
    fi
done

# Check if prompt ends with question mark
HAS_QUESTION_MARK=false
if [[ "$USER_PROMPT" =~ \?$ ]]; then
    HAS_QUESTION_MARK=true
fi

# Generate guidance message if patterns detected
if [[ "$FOUND_QUESTION" == true ]] || [[ "$FOUND_RECOMMENDATION" == true ]] || [[ "$FOUND_COMPOUND" == true ]] || [[ "$HAS_QUESTION_MARK" == true ]]; then
    cat <<'EOF'
📋 ANALYSIS MODE DETECTED: Question/evaluation pattern found

Per CLAUDE.md Communication Guidelines:
✅ REQUIRED ACTIONS:
1. Provide structured analysis (NOT implementation)
2. Offer options with pros/cons if applicable
3. Explain current state without making changes
4. End with: "Would you like me to implement any of these suggestions?"

❌ DO NOT:
- Use tools to make changes
- Implement solutions
- Modify files

⏸️ WAIT for explicit user confirmation before any implementation.
EOF
else
    # No guidance needed
    echo ""
fi
