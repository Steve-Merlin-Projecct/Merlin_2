#!/bin/bash
# Test script for PreToolUse file protection hook

echo "=== Testing PreToolUse File Protection Hook ==="
echo ""

echo "Test 1: Edit protected file (user-prompt-submit-unified.sh)"
echo '{"tool_name":"Edit","tool_input":{"file_path":".claude/hooks/user-prompt-submit-unified.sh"},"cwd":"/workspace"}' | \
    ./.claude/hooks/pre-tool-use-file-protection.py
echo "Exit code: $?"
echo ""

echo "Test 2: Write to protected module (behavioral_guidance.sh)"
echo '{"tool_name":"Write","tool_input":{"file_path":".claude/hooks/modules/behavioral_guidance.sh"},"cwd":"/workspace"}' | \
    ./.claude/hooks/pre-tool-use-file-protection.py
echo "Exit code: $?"
echo ""

echo "Test 3: Edit protected file with worktree path"
echo '{"tool_name":"Edit","tool_input":{"file_path":"/workspace/.trees/hooks-hooks/.claude/hooks/modules/estimation_guidance.sh"},"cwd":"/workspace"}' | \
    ./.claude/hooks/pre-tool-use-file-protection.py
echo "Exit code: $?"
echo ""

echo "Test 4: Edit non-protected file (should allow)"
echo '{"tool_name":"Edit","tool_input":{"file_path":"app.py"},"cwd":"/workspace"}' | \
    ./.claude/hooks/pre-tool-use-file-protection.py
echo "Exit code: $?"
echo ""

echo "Test 5: Read tool (should allow - not Edit/Write)"
echo '{"tool_name":"Read","tool_input":{"file_path":".claude/hooks/user-prompt-submit-unified.sh"},"cwd":"/workspace"}' | \
    ./.claude/hooks/pre-tool-use-file-protection.py
echo "Exit code: $?"
echo ""

echo "=== All tests complete ==="
echo ""
echo "Expected exit codes:"
echo "  0 = Operation allowed"
echo "  1 = Operation blocked"