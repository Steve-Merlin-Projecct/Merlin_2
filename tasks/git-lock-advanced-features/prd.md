---
title: "Prd"
type: technical_doc
component: general
status: draft
tags: []
---

# PRD: Git Lock Advanced Features

**Version:** 1.0
**Date:** 2025-10-17
**Status:** In Development
**Worktree:** git-lock-advanced-features---per-worktree-locks-lo

## Executive Summary

Enhance the existing git lock management system with 4 advanced features to improve performance, observability, and scalability for multi-worktree development.

## Background

The worktree system currently has robust lock management (95%+ success rate) with:
- Stale lock detection and cleanup
- Exponential backoff retry logic
- flock-based mutex serialization
- 30-second timeouts
- Operation logging

**Current Limitation:** All worktrees compete for a single global lock, causing performance bottlenecks as the system scales.

## Goals

### Feature 1: Per-Worktree Locks
**Problem:** Single global lock serializes all operations, even those on different worktrees
**Solution:** Independent lock files per worktree for truly parallel operations
**Benefit:** 11 worktrees can commit to different branches simultaneously

### Feature 2: Lock Metrics Dashboard
**Problem:** No visibility into lock contention, wait times, or bottlenecks
**Solution:** Real-time metrics collection and HTML dashboard
**Benefit:** Proactive identification of performance issues

### Feature 3: Predictive Lock Management
**Problem:** Reactive lock acquisition causes unnecessary waits
**Solution:** Pre-acquire locks based on operation patterns
**Benefit:** Reduce wait times by anticipating lock needs

### Feature 4: Queue-Based System
**Problem:** Race conditions and thundering herd scenarios
**Solution:** Centralized operation queue with priority scheduling
**Benefit:** Fair scheduling, eliminates races, enables batching

## Technical Specification

### Feature 1: Per-Worktree Locks

**Implementation:**
```bash
# Lock structure
.git/.git-locks/
├── global.lock              # For cross-worktree operations
├── worktree-1.lock          # Per-worktree operations
├── worktree-2.lock
└── ...

# Enhanced safe_git function
safe_git() {
    local git_cmd="$@"
    local lock_scope=$(determine_lock_scope "$git_cmd")

    case $lock_scope in
        "global")   # merge, rebase, pull
            acquire_lock "$GIT_GLOBAL_LOCK"
            ;;
        "worktree") # add, commit, status in specific worktree
            acquire_lock "$WORKTREE_LOCK"
            ;;
    esac
}
```

**Operations requiring global lock:**
- `git merge` - affects shared refs
- `git rebase` - affects shared refs
- `git worktree add/remove` - modifies worktree list
- `git pull` - may affect multiple refs

**Operations requiring only worktree lock:**
- `git add` - modifies worktree index only
- `git commit` - writes to specific ref
- `git status` - reads worktree state
- `git diff` - reads worktree state

### Feature 2: Lock Metrics Dashboard

**Metrics Collection:**
```bash
# Enhanced logging with structured data
log_lock_metric() {
    local metric_type=$1    # acquire|release|wait|timeout|stale
    local lock_file=$2      # which lock
    local duration_ms=$3    # how long
    local operation=$4      # what command

    echo "$(date +%s),$metric_type,$lock_file,$duration_ms,$operation" \
        >> "$WORKSPACE_ROOT/.git/.lock-metrics.csv"
}
```

**Dashboard Features:**
- Real-time lock status (who holds which lock)
- Wait time distribution (p50, p95, p99)
- Lock contention heatmap (time of day)
- Top 10 slowest operations
- Stale lock frequency
- Auto-refresh every 5 seconds

**Dashboard Implementation:**
- HTML + JavaScript (no dependencies)
- Parses `.lock-metrics.csv` on page load
- Chart.js for visualizations
- Accessible via: `file://.git/lock-dashboard.html`

### Feature 3: Predictive Lock Management

**Pattern Detection:**
```bash
# Learn common operation sequences
# Example: /tree build always does:
#   1. git checkout -b develop/...
#   2. git worktree add (x11)
#   3. git status (x11)

# Prediction engine
predict_next_locks() {
    local current_op=$1
    local history_file="$WORKSPACE_ROOT/.git/.lock-patterns"

    # Analyze recent history
    tail -100 "$GIT_OPERATION_LOG" | \
        grep -A 1 "$current_op" | \
        grep -v "$current_op" | \
        sort | uniq -c | sort -rn | head -3
}

# Pre-acquisition
preacquire_locks() {
    local predicted_ops=$(predict_next_locks "$CURRENT_OP")

    for op in $predicted_ops; do
        local lock=$(determine_lock_for_op "$op")
        acquire_lock_async "$lock"  # Non-blocking
    done
}
```

**Patterns to Learn:**
- `/tree build` sequence
- `/tree closedone` sequence
- git-orchestrator commit flow
- Restore terminal flow

**Implementation Strategy:**
- Background process learns patterns
- 80% confidence threshold to predict
- Non-blocking pre-acquisition
- Falls back to normal acquisition if wrong

### Feature 4: Queue-Based System

**Architecture:**
```bash
# Queue manager (background process)
.git/.git-lock-queue/
├── queue.fifo           # Operation queue
├── manager.pid          # Queue manager PID
└── status.json          # Current state

# Queue operations
enqueue_git_operation() {
    local priority=$1      # 1-10 (10=highest)
    local operation=$2
    local worktree=$3

    echo "$priority|$operation|$worktree|$$" >> "$QUEUE_FILE"
    signal_queue_manager
}

# Worker process
queue_worker() {
    while true; do
        local next_op=$(dequeue_highest_priority)

        if [ -n "$next_op" ]; then
            execute_operation "$next_op"
            notify_completion "$next_op"
        else
            sleep 0.1
        fi
    done
}
```

**Priority Levels:**
- 10: User-initiated commands
- 8: git-orchestrator operations
- 5: Background status checks
- 3: Metric collection
- 1: Cleanup operations

**Queue Manager Features:**
- Fair scheduling (prevent starvation)
- Batch compatible operations
- Dead letter queue for failures
- Graceful shutdown on SIGTERM

## User Stories

### US1: Parallel Worktree Commits
**As a** developer with 11 active worktrees
**I want** to commit changes in multiple worktrees simultaneously
**So that** I don't wait for serial lock acquisition

**Acceptance Criteria:**
- 5 concurrent commits to different branches complete in <10s
- No lock conflicts
- All commits succeed

### US2: Lock Performance Monitoring
**As a** system administrator
**I want** to see lock wait times and contention
**So that** I can identify performance bottlenecks

**Acceptance Criteria:**
- Dashboard shows real-time lock status
- Historical metrics available for 7 days
- Alerts when p95 wait time >5s

### US3: Faster /tree build
**As a** developer
**I want** `/tree build` to pre-acquire locks for known operations
**So that** worktree creation is faster

**Acceptance Criteria:**
- Reduce `/tree build` time by 20%
- No increase in failed operations
- Prediction accuracy >70%

### US4: Fair Operation Scheduling
**As a** developer with multiple Claude sessions
**I want** git operations to execute fairly
**So that** no session starves waiting for locks

**Acceptance Criteria:**
- No operation waits >30s
- Priority-based execution
- User commands take precedence over background tasks

## Implementation Plan

### Phase 1: Per-Worktree Locks
**Files:**
- `.claude/scripts/tree.sh` - Enhanced `safe_git()`
- `.claude/scripts/git-lock-manager.sh` - Lock manager library

**Tasks:**
1. Create lock directory structure
2. Implement `determine_lock_scope()`
3. Add worktree-specific lock acquisition
4. Update all git operations
5. Test with 11 concurrent commits

### Phase 2: Metrics Dashboard
**Files:**
- `.claude/scripts/git-lock-metrics.sh` - Metrics collection
- `frontend_templates/lock-dashboard.html` - Dashboard UI
- `frontend_templates/lock-dashboard.js` - Dashboard logic

**Tasks:**
1. Implement structured logging
2. Create CSV metrics file
3. Build HTML dashboard
4. Add Chart.js visualizations
5. Test with 1000+ operations

### Phase 3: Predictive Management
**Files:**
- `.claude/scripts/git-lock-predictor.sh` - Pattern learning
- `.git/.lock-patterns` - Pattern database

**Tasks:**
1. Implement history analysis
2. Build prediction engine
3. Add pre-acquisition logic
4. Train on `/tree build` pattern
5. Measure prediction accuracy

### Phase 4: Queue System
**Files:**
- `.claude/scripts/git-queue-manager.sh` - Queue worker
- `.claude/scripts/git-queue-client.sh` - Client library

**Tasks:**
1. Implement queue data structure
2. Build priority scheduler
3. Create worker process
4. Add client integration
5. Test with 50 concurrent operations

## Testing Strategy

### Unit Tests
- `test_lock_scope_determination.sh`
- `test_metrics_collection.sh`
- `test_pattern_prediction.sh`
- `test_queue_scheduling.sh`

### Integration Tests
- Concurrent commits to different worktrees
- Dashboard accuracy under load
- Prediction during `/tree build`
- Queue fairness with mixed priorities

### Performance Tests
- Baseline: 11 worktrees, serial operations
- Test: 11 worktrees, parallel operations
- Target: >50% improvement in total time

## Success Metrics

| Metric | Baseline | Target |
|--------|----------|--------|
| /tree build time (11 worktrees) | 22-27s | <15s |
| Concurrent commit success rate | 95% | 99% |
| Lock wait time p95 | 5s | <2s |
| Prediction accuracy | N/A | >70% |
| Dashboard load time | N/A | <1s |

## Risks & Mitigations

| Risk | Mitigation |
|------|-----------|
| Per-worktree locks introduce deadlocks | Implement lock acquisition ordering |
| Metrics collection impacts performance | Use buffered writes, async collection |
| Prediction causes false acquisitions | Conservative confidence threshold |
| Queue manager crashes | Auto-restart, graceful degradation |

## Documentation

**Updates Required:**
- `docs/git-lock-improvements-summary.md` - Add advanced features
- `docs/tree-command-guide.md` - Update performance characteristics
- `.claude/scripts/tree.sh` - Inline documentation
- `tasks/git-lock-advanced-features/README.md` - Usage guide

## Future Enhancements

- Distributed lock coordination (multiple devcontainers)
- Machine learning for pattern prediction
- Real-time dashboard via WebSocket
- Lock profiling per git command
- Auto-tuning of timeout values

## References

- [Git Lock Analysis](../docs/git-lock-analysis.md)
- [Git Lock Fix Design](../docs/git-lock-fix-design.md)
- [Git Lock Improvements Summary](../docs/git-lock-improvements-summary.md)
- [Tree Command Guide](../docs/tree-command-guide.md)
