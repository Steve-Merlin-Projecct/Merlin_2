#!/bin/bash

# Git Lock Advanced Features - Test Suite
# Comprehensive tests for all 4 advanced features

set -e

WORKSPACE_ROOT="/workspace"
cd "$WORKSPACE_ROOT"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Test counters
TESTS_RUN=0
TESTS_PASSED=0
TESTS_FAILED=0

# ==============================================================================
# Test Framework
# ==============================================================================

test_start() {
    echo -e "\n${YELLOW}▶${NC} Testing: $1"
    TESTS_RUN=$((TESTS_RUN + 1))
}

test_pass() {
    echo -e "${GREEN}✓${NC} $1"
    TESTS_PASSED=$((TESTS_PASSED + 1))
}

test_fail() {
    echo -e "${RED}✗${NC} $1"
    TESTS_FAILED=$((TESTS_FAILED + 1))
}

# ==============================================================================
# Feature 1: Per-Worktree Locks Tests
# ==============================================================================

test_per_worktree_locks() {
    echo -e "\n${YELLOW}═══ Feature 1: Per-Worktree Locks ═══${NC}"

    # Test 1: Lock manager exists
    test_start "Lock manager script exists"
    if [ -f ".claude/scripts/git-lock-manager.sh" ]; then
        test_pass "Lock manager found"
    else
        test_fail "Lock manager not found"
        return
    fi

    # Test 2: Source lock manager
    test_start "Lock manager can be sourced"
    if source ".claude/scripts/git-lock-manager.sh" 2>/dev/null; then
        test_pass "Lock manager sourced successfully"
    else
        test_fail "Failed to source lock manager"
        return
    fi

    # Test 3: Lock directory created
    test_start "Lock directory structure"
    if [ -d ".git/.git-locks" ]; then
        test_pass "Lock directory exists"
    else
        test_fail "Lock directory not created"
    fi

    # Test 4: Scope determination
    test_start "Lock scope determination"
    local scope=$(determine_lock_scope "merge")
    if [ "$scope" = "global" ]; then
        test_pass "Merge correctly identified as global scope"
    else
        test_fail "Scope determination failed (expected global, got: $scope)"
    fi

    # Test 5: Worktree lock path
    test_start "Worktree lock path generation"
    local lock_path=$(get_worktree_lock)
    if [[ "$lock_path" =~ \.git-locks/.*\.lock$ ]]; then
        test_pass "Worktree lock path generated: $lock_path"
    else
        test_fail "Invalid worktree lock path: $lock_path"
    fi

    # Test 6: safe_git_advanced function exists
    test_start "safe_git_advanced function"
    if type safe_git_advanced &>/dev/null; then
        test_pass "safe_git_advanced function available"
    else
        test_fail "safe_git_advanced function not found"
    fi
}

# ==============================================================================
# Feature 2: Lock Metrics Dashboard Tests
# ==============================================================================

test_metrics_dashboard() {
    echo -e "\n${YELLOW}═══ Feature 2: Lock Metrics Dashboard ═══${NC}"

    # Test 1: Metrics script exists
    test_start "Metrics collection script"
    if [ -f ".claude/scripts/git-lock-metrics.sh" ]; then
        test_pass "Metrics script found"
    else
        test_fail "Metrics script not found"
        return
    fi

    # Test 2: Initialize metrics
    test_start "Metrics initialization"
    if bash ".claude/scripts/git-lock-metrics.sh" init; then
        test_pass "Metrics initialized"
    else
        test_fail "Failed to initialize metrics"
    fi

    # Test 3: Metrics file created
    test_start "Metrics CSV file"
    if [ -f ".git/.lock-metrics.csv" ]; then
        test_pass "Metrics CSV created"
    else
        test_fail "Metrics CSV not found"
    fi

    # Test 4: Dashboard HTML exists
    test_start "Dashboard HTML"
    if [ -f "frontend_templates/lock-dashboard.html" ]; then
        test_pass "Dashboard HTML found"
    else
        test_fail "Dashboard HTML not found"
    fi

    # Test 5: Dashboard JavaScript exists
    test_start "Dashboard JavaScript"
    if [ -f "frontend_templates/lock-dashboard.js" ]; then
        test_pass "Dashboard JS found"
    else
        test_fail "Dashboard JS not found"
    fi

    # Test 6: Generate metrics report
    test_start "Metrics report generation"
    if bash ".claude/scripts/git-lock-metrics.sh" analyze 2>/dev/null; then
        test_pass "Metrics report generated"
    else
        test_fail "Failed to generate metrics report"
    fi
}

# ==============================================================================
# Feature 3: Predictive Lock Management Tests
# ==============================================================================

test_predictive_management() {
    echo -e "\n${YELLOW}═══ Feature 3: Predictive Lock Management ═══${NC}"

    # Test 1: Predictor script exists
    test_start "Predictor script"
    if [ -f ".claude/scripts/git-lock-predictor.sh" ]; then
        test_pass "Predictor script found"
    else
        test_fail "Predictor script not found"
        return
    fi

    # Test 2: Initialize predictor
    test_start "Predictor initialization"
    if bash ".claude/scripts/git-lock-predictor.sh" init; then
        test_pass "Predictor initialized"
    else
        test_fail "Failed to initialize predictor"
    fi

    # Test 3: Pattern database created
    test_start "Pattern database"
    if [ -f ".git/.lock-patterns.db" ]; then
        test_pass "Pattern database created"
    else
        test_fail "Pattern database not found"
    fi

    # Test 4: Learn patterns (may have no data)
    test_start "Pattern learning"
    if bash ".claude/scripts/git-lock-predictor.sh" learn 2>/dev/null; then
        test_pass "Pattern learning executed"
    else
        test_fail "Pattern learning failed"
    fi

    # Test 5: Show patterns (may be empty)
    test_start "Pattern display"
    if bash ".claude/scripts/git-lock-predictor.sh" patterns &>/dev/null; then
        test_pass "Pattern display works"
    else
        test_fail "Pattern display failed"
    fi

    # Test 6: Predict function exists
    test_start "Prediction function"
    source ".claude/scripts/git-lock-predictor.sh"
    if type predict_next_operations &>/dev/null; then
        test_pass "Prediction function available"
    else
        test_fail "Prediction function not found"
    fi
}

# ==============================================================================
# Feature 4: Queue-Based System Tests
# ==============================================================================

test_queue_system() {
    echo -e "\n${YELLOW}═══ Feature 4: Queue-Based System ═══${NC}"

    # Test 1: Queue manager script exists
    test_start "Queue manager script"
    if [ -f ".claude/scripts/git-queue-manager.sh" ]; then
        test_pass "Queue manager script found"
    else
        test_fail "Queue manager script not found"
        return
    fi

    # Test 2: Queue client exists
    test_start "Queue client library"
    if [ -f ".claude/scripts/git-queue-client.sh" ]; then
        test_pass "Queue client found"
    else
        test_fail "Queue client not found"
    fi

    # Test 3: Start queue manager
    test_start "Queue manager start"
    if bash ".claude/scripts/git-queue-manager.sh" start 2>/dev/null; then
        test_pass "Queue manager started"
    else
        test_fail "Failed to start queue manager"
        return
    fi

    # Wait for manager to initialize
    sleep 1

    # Test 4: Check queue status
    test_start "Queue status check"
    if bash ".claude/scripts/git-queue-manager.sh" status | grep -q "Running"; then
        test_pass "Queue manager is running"
    else
        test_fail "Queue manager not running"
    fi

    # Test 5: Queue directory structure
    test_start "Queue directory structure"
    if [ -d ".git/.git-lock-queue" ] && [ -p ".git/.git-lock-queue/queue.fifo" ]; then
        test_pass "Queue directory and FIFO created"
    else
        test_fail "Queue directory structure incomplete"
    fi

    # Test 6: Stop queue manager
    test_start "Queue manager stop"
    if bash ".claude/scripts/git-queue-manager.sh" stop 2>/dev/null; then
        test_pass "Queue manager stopped gracefully"
    else
        test_fail "Failed to stop queue manager"
    fi
}

# ==============================================================================
# Integration Tests
# ==============================================================================

test_integration() {
    echo -e "\n${YELLOW}═══ Integration Tests ═══${NC}"

    # Test 1: All scripts executable
    test_start "All scripts are executable"
    local all_executable=true
    for script in \
        ".claude/scripts/git-lock-manager.sh" \
        ".claude/scripts/git-lock-metrics.sh" \
        ".claude/scripts/git-lock-predictor.sh" \
        ".claude/scripts/git-queue-manager.sh" \
        ".claude/scripts/git-queue-client.sh"; do

        if [ ! -x "$script" ]; then
            all_executable=false
            break
        fi
    done

    if $all_executable; then
        test_pass "All scripts executable"
    else
        test_fail "Some scripts not executable"
    fi

    # Test 2: No syntax errors
    test_start "Scripts have no syntax errors"
    local all_valid=true
    for script in \
        ".claude/scripts/git-lock-manager.sh" \
        ".claude/scripts/git-lock-metrics.sh" \
        ".claude/scripts/git-lock-predictor.sh" \
        ".claude/scripts/git-queue-manager.sh" \
        ".claude/scripts/git-queue-client.sh"; do

        if ! bash -n "$script" 2>/dev/null; then
            all_valid=false
            break
        fi
    done

    if $all_valid; then
        test_pass "No syntax errors detected"
    else
        test_fail "Syntax errors found"
    fi

    # Test 3: Dashboard files valid HTML/JS
    test_start "Dashboard files valid"
    if [ -f "frontend_templates/lock-dashboard.html" ] && \
       [ -f "frontend_templates/lock-dashboard.js" ]; then
        test_pass "Dashboard files present"
    else
        test_fail "Dashboard files missing"
    fi
}

# ==============================================================================
# Main Test Runner
# ==============================================================================

echo -e "${YELLOW}═══════════════════════════════════════════════════════${NC}"
echo -e "${YELLOW}Git Lock Advanced Features - Test Suite${NC}"
echo -e "${YELLOW}═══════════════════════════════════════════════════════${NC}"

# Run all test suites
test_per_worktree_locks
test_metrics_dashboard
test_predictive_management
test_queue_system
test_integration

# Summary
echo -e "\n${YELLOW}═══════════════════════════════════════════════════════${NC}"
echo -e "${YELLOW}Test Summary${NC}"
echo -e "${YELLOW}═══════════════════════════════════════════════════════${NC}"
echo -e "Tests Run:    $TESTS_RUN"
echo -e "${GREEN}Tests Passed: $TESTS_PASSED${NC}"
if [ $TESTS_FAILED -gt 0 ]; then
    echo -e "${RED}Tests Failed: $TESTS_FAILED${NC}"
else
    echo -e "${GREEN}Tests Failed: $TESTS_FAILED${NC}"
fi

# Exit code
if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "\n${GREEN}✓ All tests passed!${NC}"
    exit 0
else
    echo -e "\n${RED}✗ Some tests failed${NC}"
    exit 1
fi
