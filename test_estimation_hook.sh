#!/bin/bash
# Test script for estimation hook

echo "=== Test 1: Estimation request (how long) ==="
echo '{"userPrompt":"How long will this feature take?"}' | ./.claude/hooks/modules/estimation_guidance.sh
echo ""

echo "=== Test 2: Estimation request (scope) ==="
echo '{"userPrompt":"Can you estimate the scope?"}' | ./.claude/hooks/modules/estimation_guidance.sh
echo ""

echo "=== Test 3: Estimation request (time to) ==="
echo '{"userPrompt":"What is the time to complete this?"}' | ./.claude/hooks/modules/estimation_guidance.sh
echo ""

echo "=== Test 4: Non-estimation request ==="
echo '{"userPrompt":"Implement the authentication feature"}' | ./.claude/hooks/modules/estimation_guidance.sh
echo ""

echo "=== All tests complete ==="