---
title: "Git Lock Fix Design"
type: architecture
component: general
status: draft
tags: []
---

# Git Lock Fix Design Specification
**Date:** 2025-10-12
**Version:** 1.0

## Overview

This document specifies the design for fixing git lock conflicts in the worktree orchestration and git-orchestrator agent system.

## Design Principles

1. **Defense in Depth:** Multiple layers of protection against lock conflicts
2. **Graceful Degradation:** Operations should retry with exponential backoff
3. **Automatic Recovery:** Detect and recover from stale locks without user intervention
4. **Minimal Performance Impact:** Lock coordination should add <1s overhead per operation
5. **Backward Compatibility:** Existing workflows continue to work

## Solution Architecture

### Layer 1: Stale Lock Detection and Cleanup

**Implementation:** Enhanced `wait_for_git_lock` function

**Mechanism:**
1. Check if `.git/index.lock` exists
2. If yes, attempt to identify the process that created it
3. Check if that process is still running
4. If not running, remove the stale lock automatically
5. If running, wait with exponential backoff

**Code Location:** `.claude/scripts/tree.sh` function `wait_for_git_lock`

**Benefits:**
- Automatically recovers from crashed processes
- No manual intervention needed
- Minimal code changes

**Pseudocode:**
```bash
wait_for_git_lock() {
    local max_wait=30  # Increased from 5
    local attempt=1
    local wait_time=1

    while [ -f "$LOCK_FILE" ] && [ $attempt -le $max_wait ]; do
        # Try to determine if lock is stale
        if is_lock_stale "$LOCK_FILE"; then
            print_warning "Stale lock detected, removing..."
            rm -f "$LOCK_FILE"
            return 0
        fi

        print_warning "Git lock detected, waiting ${wait_time}s (attempt $attempt/$max_wait)"
        sleep $wait_time

        # Exponential backoff (1s, 2s, 4s, 8s, 16s, max 16s)
        wait_time=$((wait_time * 2))
        [ $wait_time -gt 16 ] && wait_time=16

        attempt=$((attempt + 1))
    done

    # Final check
    if [ -f "$LOCK_FILE" ]; then
        return 1
    fi
    return 0
}

is_lock_stale() {
    local lock_file=$1
    local lock_age_seconds=$(( $(date +%s) - $(stat -f %m "$lock_file" 2>/dev/null || stat -c %Y "$lock_file") ))

    # If lock is older than 60 seconds and file size is 0, likely stale
    if [ $lock_age_seconds -gt 60 ] && [ ! -s "$lock_file" ]; then
        return 0  # Stale
    fi
    return 1  # Not stale
}
```

### Layer 2: Filesystem-Based Mutex (flock)

**Implementation:** Custom git operation wrapper with flock

**Mechanism:**
1. Create a `.git/.git-operation.lock` file
2. Use `flock` to acquire exclusive lock
3. Run git operation
4. Release lock automatically when operation completes

**Code Location:** New function in `.claude/scripts/tree.sh`

**Benefits:**
- Operating system handles lock coordination
- Works across processes and terminals
- Automatic cleanup on process termination

**Pseudocode:**
```bash
# Global lock file for serializing git operations
GIT_OPERATION_LOCK="$WORKSPACE_ROOT/.git/.git-operation.lock"

# Wrapper for all git operations that modify state
safe_git() {
    local git_cmd="$@"

    # Create lock file if it doesn't exist
    touch "$GIT_OPERATION_LOCK"

    # Acquire exclusive lock (wait up to 30 seconds)
    (
        flock -x -w 30 200 || {
            print_error "Failed to acquire git operation lock after 30s"
            return 1
        }

        # Run the git command
        git $git_cmd
        local exit_code=$?

        return $exit_code
    ) 200>"$GIT_OPERATION_LOCK"

    return $?
}
```

**Usage:**
```bash
# Replace:
git worktree add -b "$branch" "$path" "$base"

# With:
safe_git worktree add -b "$branch" "$path" "$base"

# Replace:
git checkout "$branch"

# With:
safe_git checkout "$branch"
```

### Layer 3: Increased Delays in Concurrent Operations

**Implementation:** Modify terminal launch timing

**Changes:**
1. Increase delay from 0.5s to 2s between terminal launches
2. Add random jitter (0-500ms) to prevent thundering herd

**Code Location:** `.claude/scripts/tree.sh` lines 695-714

**Before:**
```bash
sleep 0.5
```

**After:**
```bash
# Staggered launch with jitter to prevent concurrent git operations
local jitter=$(( RANDOM % 500 ))
sleep 2.$jitter
```

**Benefits:**
- Reduces likelihood of concurrent operations
- Simple change with high impact

### Layer 4: git-orchestrator Lock Coordination

**Implementation:** Add lock acquisition to git-orchestrator agent

**Mechanism:**
1. Before any git operation, invoke `safe_git` wrapper
2. Agent waits for lock availability
3. Performs operation
4. Lock released automatically

**Code Location:** `.claude/agents/git-orchestrator.md` - add to all git operations

**Example Integration:**
```bash
# In git-orchestrator agent prompt
# Before running any git command, use the safe_git wrapper:

# Instead of:
git add .
git commit -m "$MESSAGE"
git push origin $BRANCH

# Use:
safe_git add .
safe_git commit -m "$MESSAGE"
safe_git push origin $BRANCH
```

### Layer 5: Enhanced Logging and Diagnostics

**Implementation:** Log all git lock events

**Mechanism:**
1. Log when lock is acquired
2. Log when lock is released
3. Log when waiting for lock
4. Log when stale lock is removed

**Code Location:** New function in `.claude/scripts/tree.sh`

**Pseudocode:**
```bash
log_git_operation() {
    local operation=$1
    local timestamp=$(date +"%Y-%m-%d %H:%M:%S")
    local log_file="$WORKSPACE_ROOT/.git/.git-operations.log"

    echo "[$timestamp] $operation" >> "$log_file"
}

# Usage:
log_git_operation "Lock acquired for: git worktree add"
log_git_operation "Lock released after: git worktree add"
log_git_operation "Stale lock removed (age: 120s)"
log_git_operation "Waiting for lock (attempt 3/30)"
```

## Implementation Plan

### Phase 1: Enhanced Lock Detection (Immediate)
- [ ] Modify `wait_for_git_lock` function
- [ ] Add stale lock detection with age check
- [ ] Increase timeout from 5s to 30s
- [ ] Add exponential backoff

### Phase 2: flock Integration (High Priority)
- [ ] Create `safe_git` wrapper function
- [ ] Add flock-based mutex
- [ ] Replace critical git operations in tree.sh
- [ ] Add logging for lock events

### Phase 3: Timing Adjustments (Medium Priority)
- [ ] Increase terminal launch delay to 2s
- [ ] Add random jitter to prevent synchronization
- [ ] Increase `wait_for_git_lock` max attempts to 30

### Phase 4: git-orchestrator Integration (Medium Priority)
- [ ] Update git-orchestrator.md specification
- [ ] Add safe_git wrapper to agent tools
- [ ] Document lock coordination in agent guide

### Phase 5: Testing and Validation (Required)
- [ ] Test with `/tree build` creating 11 worktrees
- [ ] Test with concurrent git-orchestrator operations
- [ ] Simulate stale lock scenarios
- [ ] Measure performance impact

## Rollback Plan

If the changes cause issues:

1. **Immediate Rollback:** Revert `wait_for_git_lock` function to original
2. **Partial Rollback:** Keep stale lock detection, remove flock
3. **Timing Rollback:** Revert terminal delays to 0.5s

**Rollback Triggers:**
- Operations slower than 5s baseline
- New lock conflicts introduced
- User reports of hangs or timeouts

## Performance Targets

| Metric | Current | Target | Maximum Acceptable |
|--------|---------|--------|-------------------|
| Lock wait time | 0-5s | 0-2s | 10s |
| Stale lock cleanup | Manual | Automatic (<1s) | N/A |
| Concurrent operation success rate | ~55% | >95% | >90% |
| Terminal launch total time | 5.5s (11 * 0.5s) | 22s (11 * 2s) | 30s |

## Success Criteria

1. **No manual lock removal needed** for at least 100 worktree operations
2. **Zero lock conflicts** during `/tree build` with 11 worktrees
3. **Automatic recovery** from stale locks in <5 seconds
4. **<1% performance overhead** for single git operations

## Testing Strategy

### Unit Tests
- `test_wait_for_git_lock_timeout`
- `test_stale_lock_detection`
- `test_safe_git_wrapper`
- `test_exponential_backoff`

### Integration Tests
- `/tree build` with 11 features
- Concurrent git-orchestrator invocations
- Simulated crashed git process
- Thundering herd scenario (20 concurrent operations)

### Stress Tests
- Create 50 worktrees sequentially
- 100 concurrent git status operations
- Lock held for 60 seconds (manual simulation)

## Monitoring and Alerts

**Metrics to Track:**
- Lock wait time (p50, p95, p99)
- Stale lock removals per day
- Lock acquisition failures
- Git operation duration

**Alert Conditions:**
- Lock wait time >10s
- Stale lock removal >5 times/hour
- Lock acquisition failure
- Git operation timeout

## Documentation Updates

1. **git-orchestrator-guide.md** - Add lock coordination section
2. **git-orchestrator.md** - Update with safe_git usage
3. **tree.sh** - Inline comments for lock functions
4. **CLAUDE.md** - Update troubleshooting section

## Dependencies

**Required:**
- `flock` command (part of util-linux, available on Linux)
- `stat` command (for file age detection)

**Optional:**
- Enhanced logging (can proceed without)

## Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| flock not available | Low | High | Check for flock, fallback to wait_for_git_lock only |
| Increased latency | Medium | Low | Performance testing, adjust timeouts |
| False positive stale detection | Low | Medium | Conservative age threshold (60s) |
| Deadlock in flock | Low | High | 30s timeout on flock acquisition |

## Future Enhancements

1. **Git Operation Queue** - Centralized queue for all git operations
2. **Per-Worktree Locks** - Allow concurrent operations on different worktrees
3. **Lock Metrics Dashboard** - Real-time monitoring of lock state
4. **Predictive Lock Management** - Pre-acquire locks based on operation patterns

---

**Next Step:** Begin Phase 1 implementation with enhanced `wait_for_git_lock` function.
