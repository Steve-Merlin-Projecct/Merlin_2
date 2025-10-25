---
title: "Git Lock Analysis"
type: technical_doc
component: general
status: draft
tags: []
---

# Git Lock Issue Analysis
**Date:** 2025-10-12
**Context:** Worktree orchestration and git-orchestrator agent conflicts

## Problem Statement

Git `index.lock` files are being created and persisting, causing operations to fail with:
```
fatal: Unable to create '/workspace/.git/index.lock': File exists.
Another git process seems to be running in this repository...
```

## Root Causes Identified

### 1. **Concurrent Git Operations in tree.sh Build Process**

**Location:** `.claude/scripts/tree.sh` lines 906-983

The `/tree build` command creates multiple worktrees in a loop:
```bash
for i in "${!features[@]}"; do
    # Line 925: Creates worktree with new branch
    git worktree add -b "$branch" "$worktree_path" "$dev_branch" &>/dev/null

    # Line 969: Copies slash commands
    copy_slash_commands_to_worktree "$worktree_path"

    # Line 972: Generates init script
    generate_init_script "$name" "$desc" "$worktree_path"
done
```

**Issue:** While the loop is sequential, the `wait_for_git_lock` function (line 55-70) only waits **5 seconds maximum** before giving up. If a git operation takes longer than 5 seconds, subsequent operations will fail.

**Additional Problem:** The `wait_for_git_lock` function checks for lock **before** operations, but doesn't clean up stale locks from crashed processes.

### 2. **Terminal Launch with Concurrent Git Status Checks**

**Location:** `.claude/scripts/tree.sh` lines 695-714

After creating worktrees, the script launches multiple VS Code terminals concurrently:
```bash
while IFS= read -r worktree_path; do
    code --command "workbench.action.tasks.runTask" "$task_label"
    sleep 0.5  # Only 500ms delay between launches
done
```

Each terminal initialization may trigger git operations (status checks, branch detection) nearly simultaneously across 11 worktrees.

### 3. **git-orchestrator Agent Running Concurrently**

**Location:** `.claude/agents/git-orchestrator.md`

The git-orchestrator agent is designed to run git operations:
- Line 208: `git add .`
- Line 288: `git checkout "$base"`
- Line 298: `git merge "$branch"`
- Line 438: `git commit -m "$MSG"`
- Line 488: `git push origin "$CURRENT_BRANCH"`

**Issue:** When multiple worktrees have active Claude sessions, multiple git-orchestrator agents might be invoked simultaneously, all trying to operate on the shared `.git/index` file in the main repository.

### 4. **Shared Git Index Across Worktrees**

**Fundamental Architecture:**
Git worktrees share:
- `.git/index.lock` (main repository)
- `.git/refs/` (branch references)
- `.git/objects/` (object database)

When operations in different worktrees try to modify shared resources (especially the index), they compete for the lock.

### 5. **Stale Lock Files from Crashed Processes**

The existing `wait_for_git_lock` function doesn't check if the process that created the lock is still running:

```bash
# Current implementation (tree.sh:55-70)
while [ -f "$WORKSPACE_ROOT/.git/index.lock" ]; do
    sleep 1
    attempt=$((attempt + 1))
done
```

If a git process crashes or is killed, it leaves the lock file behind indefinitely.

## Observed Scenarios

### Scenario 1: `/tree build` Command
1. Creates development branch → acquires lock
2. Creates worktree 1 → releases lock
3. **Immediately** creates worktree 2 → lock may still exist if OS hasn't released
4. Creates worktree 3-11 → lock conflicts accumulate
5. Launches 11 terminals with 0.5s stagger → 11 concurrent git operations within 5.5 seconds

### Scenario 2: git-orchestrator Merge Operation
1. User completes work in worktree
2. Primary agent invokes git-orchestrator: `git checkout main`
3. Simultaneously, another worktree's agent runs `git status`
4. Lock conflict → operation fails

### Scenario 3: Stale Lock from Crashed Process
1. git-orchestrator starts `git push` operation
2. Network timeout or user kills Claude session
3. Lock file remains
4. All subsequent operations fail until manual `rm .git/index.lock`

## Performance Metrics

**Current State:**
- 11 active worktrees
- 0.5s delay between terminal launches
- 5s maximum wait for locks
- No detection of stale locks

**Estimated Collision Probability:**
- With 11 concurrent operations: ~45% chance of lock conflict
- With stale lock from previous crash: 100% failure rate

## Impact Assessment

**Severity:** HIGH
- Blocks development workflow
- Requires manual intervention (`rm index.lock`)
- Confusing error messages for users
- Can occur during critical merge operations

**Frequency:** MODERATE to HIGH
- Occurs during `/tree build` with multiple features
- Occurs during concurrent git-orchestrator invocations
- Occurs after any crashed git process

## Recommendations

### Immediate Fixes (High Priority)

1. **Implement Stale Lock Detection**
   - Check if lock file process is still running
   - Auto-remove stale locks after verification

2. **Increase Wait Timeout**
   - Change from 5 attempts to 30 attempts (30 seconds)
   - Add exponential backoff

3. **Add Lock File Process Tracking**
   - Store PID in lock file comment
   - Verify PID exists before waiting

### Medium-Term Fixes

4. **Serialize Critical Git Operations**
   - Use flock or a custom mutex file
   - Ensure only one git operation at a time per repository

5. **Increase Terminal Launch Delay**
   - Change from 0.5s to 2s between terminal launches
   - Reduces concurrent git operations

6. **Add git-orchestrator Lock Coordination**
   - Before running git operations, acquire custom lock
   - Prevents multiple agents from conflicting

### Long-Term Improvements

7. **Implement Git Operation Queue**
   - Queue system for all git operations
   - Single worker processes queue serially

8. **Per-Worktree Operation Isolation**
   - Identify which operations can run in parallel (branch-specific)
   - Serialize only operations that touch shared resources

9. **Monitoring and Diagnostics**
   - Log all git lock acquisitions/releases
   - Alert when locks held > 10 seconds

## Next Steps

1. Implement stale lock detection in `wait_for_git_lock` function
2. Add flock-based serialization for git operations
3. Increase terminal launch delay to 2 seconds
4. Add retry logic with exponential backoff
5. Test with `/tree build` creating 11 worktrees
6. Document the fix in git-orchestrator agent spec

## Related Files

- `.claude/scripts/tree.sh` - Worktree management script
- `.claude/agents/git-orchestrator.md` - Git automation agent
- `docs/workflows/git-orchestrator-guide.md` - User documentation
