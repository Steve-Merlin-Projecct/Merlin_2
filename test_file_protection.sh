#!/bin/bash
# Test script for file protection hook

echo "=== Test 1: Edit protected file (user-prompt-submit-unified.sh) ==="
echo '{"userPrompt":"Edit the user-prompt-submit-unified.sh file to add a new feature"}' | ./.claude/hooks/modules/file_protection.sh
echo ""

echo "=== Test 2: Modify protected module (behavioral_guidance.sh) ==="
echo '{"userPrompt":"Can you modify the behavioral_guidance.sh module?"}' | ./.claude/hooks/modules/file_protection.sh
echo ""

echo "=== Test 3: Update estimation module ==="
echo '{"userPrompt":"Update the estimation_guidance.sh to change the format"}' | ./.claude/hooks/modules/file_protection.sh
echo ""

echo "=== Test 4: Generic hook mention with edit intent ==="
echo '{"userPrompt":"I want to change the hook system behavior"}' | ./.claude/hooks/modules/file_protection.sh
echo ""

echo "=== Test 5: Safe operation (not editing hooks) ==="
echo '{"userPrompt":"Create a new feature in my application"}' | ./.claude/hooks/modules/file_protection.sh
echo ""

echo "=== Test 6: Mention hook without edit intent ==="
echo '{"userPrompt":"How does the behavioral_guidance.sh module work?"}' | ./.claude/hooks/modules/file_protection.sh
echo ""

echo "=== All tests complete ==="