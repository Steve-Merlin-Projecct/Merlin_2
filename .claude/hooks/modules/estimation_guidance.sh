#!/bin/bash
##
## Estimation Guidance Module
##
## Detects when user requests work estimates or when agent attempts to provide estimates.
## Enforces token-based estimation instead of time-based estimates.
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

# Convert to lowercase for case-insensitive matching
USER_PROMPT_LOWER=$(echo "$USER_PROMPT" | tr '[:upper:]' '[:lower:]')

# Estimation request patterns
ESTIMATION_PATTERNS=(
    "how long"
    "how much time"
    "estimate"
    "time to"
    "duration"
    "how many hours"
    "how many days"
    "timeline"
    "timeframe"
    "time estimate"
    "effort"
    "scope"
)

# Check for estimation requests
FOUND_ESTIMATION=false
for pattern in "${ESTIMATION_PATTERNS[@]}"; do
    if echo "$USER_PROMPT_LOWER" | grep -q "$pattern"; then
        FOUND_ESTIMATION=true
        break
    fi
done

# Generate guidance if estimation pattern detected
if [[ "$FOUND_ESTIMATION" == true ]]; then
    cat <<'EOF'
📊 ESTIMATION GUIDANCE ACTIVATED

When estimating work scope (whether requested by user or self-initiated):

REQUIRED FORMAT:
✓ Estimate ONLY in Claude Sonnet 4.5 tokens
✓ Provide a range (e.g., "40,000-60,000 tokens" or "40k-60k tokens")
✓ Wide estimates are acceptable and preferred over false precision

PROHIBITED:
✗ DO NOT estimate in hours, days, or weeks
✗ DO NOT provide time-based estimates
✗ DO NOT convert tokens to time

EXAMPLE RESPONSES:
"This task will require approximately 50,000-75,000 tokens to complete."
"Estimated token usage: 30k-50k tokens for implementation and testing."
"This is a large scope task, expecting 100k-150k tokens."

Remember: Token estimates directly correlate to API costs and work scope without the variability of time-based estimates.
EOF
else
    # No estimation request detected
    echo ""
fi