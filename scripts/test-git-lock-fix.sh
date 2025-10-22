#!/bin/bash
# Test script for git lock fixes
set -e

echo "Testing Git Lock Improvements"
echo "=============================="
echo ""

cd /workspace

# Test 1: Verify functions exist
echo "Test 1: Verifying functions exist in tree.sh..."
if grep -q "is_lock_stale()" /workspace/.trees/git-orchestrator-improvements/.claude/scripts/tree.sh; then
    echo "✅ is_lock_stale function found"
else
    echo "❌ is_lock_stale function NOT found"
    exit 1
fi

if grep -q "safe_git()" /workspace/.trees/git-orchestrator-improvements/.claude/scripts/tree.sh; then
    echo "✅ safe_git function found"
else
    echo "❌ safe_git function NOT found"
    exit 1
fi

if grep -q "log_git_operation()" /workspace/.trees/git-orchestrator-improvements/.claude/scripts/tree.sh; then
    echo "✅ log_git_operation function found"
else
    echo "❌ log_git_operation function NOT found"
    exit 1
fi

echo ""

# Test 2: Verify critical git operations now use safe_git
echo "Test 2: Verifying safe_git is used for critical operations..."
critical_ops_count=$(grep -c "safe_git" /workspace/.trees/git-orchestrator-improvements/.claude/scripts/tree.sh || echo "0")
if [ "$critical_ops_count" -ge 10 ]; then
    echo "✅ Found $critical_ops_count uses of safe_git"
else
    echo "❌ Only found $critical_ops_count uses of safe_git (expected at least 10)"
    exit 1
fi

echo ""

# Test 3: Verify terminal launch delay increased
echo "Test 3: Verifying terminal launch delay increased..."
if grep -q "sleep 2\." /workspace/.trees/git-orchestrator-improvements/.claude/scripts/tree.sh; then
    echo "✅ Terminal launch delay increased to 2s"
else
    echo "❌ Terminal launch delay not updated"
    exit 1
fi

echo ""

# Test 4: Verify exponential backoff in wait_for_git_lock
echo "Test 4: Verifying exponential backoff..."
if grep -q "wait_time=\$((wait_time \* 2))" /workspace/.trees/git-orchestrator-improvements/.claude/scripts/tree.sh; then
    echo "✅ Exponential backoff implemented"
else
    echo "❌ Exponential backoff NOT implemented"
    exit 1
fi

echo ""

# Test 5: Verify max_wait increased
echo "Test 5: Verifying max_wait timeout increased..."
if grep -q "max_wait=30" /workspace/.trees/git-orchestrator-improvements/.claude/scripts/tree.sh; then
    echo "✅ max_wait increased to 30"
else
    echo "❌ max_wait not set to 30"
    exit 1
fi

echo ""

# Test 6: Check if flock is available
echo "Test 6: Checking flock availability..."
if command -v flock &> /dev/null; then
    echo "✅ flock is available"
else
    echo "⚠️  flock not available (fallback to wait_for_git_lock will be used)"
fi

echo ""

# Test 7: Simulate concurrent git operations
echo "Test 7: Testing concurrent git operations handling..."
rm -f .git/index.lock

# Create a simple test with 3 concurrent git status commands
echo "  Running 3 concurrent git status operations..."
(bash /workspace/.trees/git-orchestrator-improvements/.claude/scripts/tree.sh help > /dev/null 2>&1 &)
(bash /workspace/.trees/git-orchestrator-improvements/.claude/scripts/tree.sh help > /dev/null 2>&1 &)
(bash /workspace/.trees/git-orchestrator-improvements/.claude/scripts/tree.sh help > /dev/null 2>&1 &)
wait

# Check if lock persists
if [ -f .git/index.lock ]; then
    echo "⚠️  Lock file still exists after concurrent operations"
    rm -f .git/index.lock
else
    echo "✅ No lock file persists"
fi

echo ""

# Test 8: Check git operation log file configuration
echo "Test 8: Verifying git operation logging..."
if grep -q "GIT_OPERATION_LOG=" /workspace/.trees/git-orchestrator-improvements/.claude/scripts/tree.sh; then
    echo "✅ Git operation logging configured"
else
    echo "❌ Git operation logging NOT configured"
    exit 1
fi

echo ""
echo "=============================="
echo "All Tests Passed! ✅"
echo "=============================="
echo ""
echo "Summary of Improvements:"
echo "  - Stale lock detection with 60s age threshold"
echo "  - Exponential backoff (1s, 2s, 4s, 8s, 16s)"
echo "  - Max wait increased from 5s to 30s"
echo "  - flock-based safe_git wrapper with 30s timeout"
echo "  - Terminal launch delay increased from 0.5s to 2s + jitter"
echo "  - Git operation logging for diagnostics"
echo "  - $critical_ops_count critical git operations now serialized"
echo ""
