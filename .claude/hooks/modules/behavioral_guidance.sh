#!/bin/bash
##
## Behavioral Guidance Module - SINGLE SOURCE OF TRUTH
##
## This hook contains ALL behavioral instructions that were previously
## scattered throughout CLAUDE.md. It provides just-in-time guidance
## based on the user's actual request.
##

set -euo pipefail

# Read hook input from stdin
HOOK_INPUT=$(cat)

# Extract user prompt
USER_PROMPT=$(echo "$HOOK_INPUT" | jq -r '.userPrompt // ""' 2>/dev/null || echo "")

# If jq fails, try Python fallback
if [[ -z "$USER_PROMPT" ]]; then
    USER_PROMPT=$(echo "$HOOK_INPUT" | python3 -c "import json,sys; print(json.load(sys.stdin).get('userPrompt',''))" 2>/dev/null || echo "")
fi

# Convert to lowercase for pattern matching
USER_PROMPT_LOWER=$(echo "$USER_PROMPT" | tr '[:upper:]' '[:lower:]')

# Initialize guidance components
ANALYSIS_MODE=""
IMPLEMENTATION_MODE=""
TASK_COMPLEXITY=""
DOCUMENTATION_REMINDER=""

# ============================================================================
# ANALYSIS VS IMPLEMENTATION DETECTION
# ============================================================================

# Question patterns that trigger analysis mode
if echo "$USER_PROMPT_LOWER" | grep -qE "(what|how|why|which|should|can you explain|could you explain|does|is there|are there)"; then
    ANALYSIS_MODE="DETECTED"
fi

# Evaluation/recommendation patterns
if echo "$USER_PROMPT_LOWER" | grep -qE "(recommend|suggestion|option|best practice|trade-off|pros and cons|compare|evaluate|assess|review|analyze|understand)"; then
    ANALYSIS_MODE="DETECTED"
fi

# Compound statements (problem + question)
if echo "$USER_PROMPT_LOWER" | grep -qE "(broken.*explain|failed.*why|error.*what|missing.*explain|doesn't work.*why|not working.*how)"; then
    ANALYSIS_MODE="DETECTED"
fi

# Question mark at end
if [[ "$USER_PROMPT" =~ \?$ ]]; then
    ANALYSIS_MODE="DETECTED"
fi

# Implementation command patterns
if echo "$USER_PROMPT_LOWER" | grep -qE "(fix|update|create|implement|build|make|add|remove|delete|modify|change|refactor|optimize|debug|solve|set up|configure|install|deploy|code|write)"; then
    IMPLEMENTATION_MODE="DETECTED"
fi

# ============================================================================
# COMPLEXITY DETECTION
# ============================================================================

# Multiple items/steps
if echo "$USER_PROMPT_LOWER" | grep -qE "(multiple|several|list of|all of|each|every|complete|full|entire|comprehensive|step by step|and then|after that|finally)"; then
    TASK_COMPLEXITY="COMPLEX"
fi

# Numbered or bulleted lists
if echo "$USER_PROMPT" | grep -qE '(^|\n)[0-9]+\.|^-\s|^\*\s|^\+\s'; then
    TASK_COMPLEXITY="COMPLEX"
fi

# More than 3 "and" conjunctions suggest multiple tasks
AND_COUNT=$(echo "$USER_PROMPT_LOWER" | grep -o " and " | wc -l)
if [[ $AND_COUNT -ge 3 ]]; then
    TASK_COMPLEXITY="COMPLEX"
fi

# ============================================================================
# DOCUMENTATION DETECTION
# ============================================================================

# Any code modification should trigger documentation reminder
if [[ "$IMPLEMENTATION_MODE" == "DETECTED" ]]; then
    DOCUMENTATION_REMINDER="REQUIRED"
fi

# ============================================================================
# GENERATE CONTEXTUAL GUIDANCE
# ============================================================================

OUTPUT=""

# Analysis mode takes precedence
if [[ "$ANALYSIS_MODE" == "DETECTED" ]] && [[ "$IMPLEMENTATION_MODE" != "DETECTED" ]]; then
    OUTPUT="🔍 ANALYSIS MODE ACTIVATED

REQUIRED BEHAVIOR:
✓ Provide structured analysis without implementation
✓ Explain current state and available options
✓ Include pros/cons for each option if applicable
✓ End with: \"Would you like me to implement any of these suggestions?\"

DO NOT:
✗ Use tools to make changes
✗ Modify any files
✗ Proceed with implementation

⏸️ Wait for explicit user permission before implementing."

elif [[ "$IMPLEMENTATION_MODE" == "DETECTED" ]]; then
    OUTPUT="🛠️ IMPLEMENTATION MODE ACTIVATED

REQUIRED SEQUENCE:
1️⃣ EXPLAIN your approach before starting
2️⃣ BREAK DOWN the task into clear steps
3️⃣ ASK for clarification if anything is unclear"

    if [[ "$TASK_COMPLEXITY" == "COMPLEX" ]]; then
        OUTPUT="$OUTPUT
4️⃣ USE TodoWrite to track each step:
   - Create todos for each distinct task
   - Mark 'in_progress' BEFORE starting work
   - Mark 'completed' IMMEDIATELY after finishing
   - Maintain ONE in_progress task at a time"
    fi

    if [[ "$DOCUMENTATION_REMINDER" == "REQUIRED" ]]; then
        OUTPUT="$OUTPUT

📚 DOCUMENTATION REQUIREMENTS:
- Add docstrings to all new functions/classes
- Explain component relationships in comments
- Document edge cases and assumptions
- Use comments for 'why' not just 'what'"
    fi
fi

# Output the guidance
echo "$OUTPUT"