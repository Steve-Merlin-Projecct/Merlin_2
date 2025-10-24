---
title: "Prd"
type: technical_doc
component: general
status: draft
tags: []
---

# PRD: Worktree System Error Prevention

## Introduction/Overview

The `/tree build` command currently fails with cryptic errors when encountering corrupted worktree state, orphaned directories, or stale git locks. The error `mkdir: cannot create directory '.git': Not a directory` was encountered but the script's aggressive error suppression (`&>/dev/null`) hid the actual cause, making debugging impossible.

This feature implements comprehensive error prevention strategies to:
1. **Prevent errors before they occur** through pre-flight validation and cleanup
2. **Provide clear diagnostics** when errors do happen
3. **Enable safe recovery** through atomic operations and rollback

**Goal:** Make the worktree system resilient to corrupted state, capable of self-healing, and provide actionable error messages when failures occur.

## Goals

1. **Prevent 95% of worktree build failures** through automated cleanup
2. **Eliminate cryptic error messages** by capturing and displaying git output
3. **Enable safe retry** through idempotent operations
4. **Provide atomic rollback** on partial failures
5. **Detect and auto-fix** common corruption scenarios

## User Stories

1. **As a developer**, when I run `/tree build`, I want orphaned directories automatically cleaned up so the build succeeds without manual intervention.

2. **As a developer**, when a worktree build fails, I want to see the actual git error message so I can diagnose the problem.

3. **As a developer**, when a build partially completes then fails, I want the system to rollback automatically so I'm not left in an inconsistent state.

4. **As a developer**, when I accidentally delete worktree directories manually, I want the system to detect and fix this on the next build.

5. **As a developer**, I want to safely re-run `/tree build` if it fails, without worrying about conflicts with partially-created worktrees.

## Functional Requirements

### Prevention Layer

1. **Pre-flight validation function** that runs before any worktree creation:
   - Detects existing directories at target paths
   - Identifies orphaned git worktree registrations
   - Detects orphaned branches (no associated worktree)
   - Validates git repository is not locked
   - Returns actionable errors or auto-fixes issues

2. **Git worktree prune** executed at build start:
   - Cleans up orphaned worktree references in `.git/worktrees/`
   - Synchronizes git's internal state with filesystem
   - Logs what was pruned

3. **Orphaned directory cleanup**:
   - Detects directories in `.trees/` not registered with git
   - Prompts user for removal or auto-removes with `--force` flag
   - Validates before deletion (confirms no uncommitted work)

4. **Stale lock detection**:
   - Checks for `index.lock` before operations
   - Uses existing `is_lock_stale()` function
   - Auto-removes locks older than 60s with size 0
   - Warns about active locks

5. **Idempotent dev branch creation**:
   - Reuses existing dev branch if present
   - Validates branch state before reuse
   - Prevents duplicate branch creation errors

### Diagnostic Layer

6. **Error capture in safe_git wrapper**:
   - Capture stderr from git commands to variable
   - Display errors when commands fail
   - Preserve exit codes

7. **Verbose mode support**:
   - Environment variable `TREE_VERBOSE=true`
   - Command flag `--verbose` or `-v`
   - Shows all git command output when enabled

8. **Enhanced error messages**:
   - Show actual git error output
   - Provide context about what operation failed
   - Suggest remediation steps

### Recovery Layer

9. **Atomic rollback on build failure**:
   - Track all created worktrees during build
   - On failure, remove all partially-created worktrees
   - Clean up branches associated with failed worktrees
   - Restore to pre-build state

10. **Cleanup validation function**:
    - Before removing paths, verify they're safe to delete
    - Check for uncommitted changes
    - Confirm paths are within `.trees/` directory
    - Prevent accidental data loss

## Non-Goals (Out of Scope)

- Fixing network-related git failures (authentication, remote connection)
- Recovering from disk full errors
- Handling OS-level permission issues
- Preventing user-initiated force operations
- Migrating existing corrupted worktrees (manual cleanup required)

## Technical Considerations

### Implementation Strategy

**Phase 1: Prevention Functions (Core)**
- `validate_and_cleanup_worktree_path()` - Pre-flight path validation
- `cleanup_orphaned_worktrees()` - Orphaned artifact detection
- `check_git_locks()` - Stale lock detection
- Integrate prune into `tree_build()` start

**Phase 2: Diagnostic Improvements**
- Update `safe_git()` to capture stderr
- Add `TREE_VERBOSE` support
- Enhance error messages with git output

**Phase 3: Recovery Mechanisms**
- Implement rollback tracking in `tree_build()`
- Add `rollback_build()` function
- Cleanup validation helpers

### Integration Points

**Existing Functions to Modify:**
- `tree_build()` - Add pre-flight checks, rollback tracking
- `safe_git()` - Add error capture, verbose mode
- `tree_help()` - Document new flags and behavior

**Existing Functions to Leverage:**
- `is_lock_stale()` - Already exists, reuse for lock detection
- `wait_for_git_lock()` - Already exists, enhance with cleanup
- `print_*()` - Use existing output functions

### File Changes

**Primary file:** `.claude/scripts/tree.sh`

**New functions to add:**
1. `validate_and_cleanup_worktree_path()` (lines ~1330-1380)
2. `cleanup_orphaned_worktrees()` (lines ~1380-1430)
3. `check_git_locks()` (lines ~1430-1480)
4. `rollback_build()` (lines ~1820-1860)
5. `validate_cleanup_safe()` (lines ~1860-1900)

**Modifications:**
- Line 131-173: Update `safe_git()` function
- Line 1533-1826: Update `tree_build()` function
- Line 2389-2447: Update `tree_help()` function

## Work Estimate

**Estimated tokens:** 35k-45k

**Breakdown:**
- Discovery & code review: 5k tokens
- Core prevention functions: 12k tokens
- Diagnostic layer updates: 8k tokens
- Recovery/rollback implementation: 10k tokens
- Testing & validation: 5k tokens
- Documentation: 3k tokens
- Buffer for edge cases: 7k tokens

**Complexity factors:**
- Bash script complexity (error handling, subshells)
- Need to preserve existing behavior
- Testing requires simulating failure scenarios
- Integration with existing lock/state management

## Success Metrics

1. **Error rate reduction:** 95% of builds succeed on first attempt (vs current unknown failure rate)
2. **Mean time to recovery:** < 5 seconds for auto-fixed errors
3. **Manual intervention rate:** < 5% of failures require manual cleanup
4. **Error clarity:** 100% of errors show actionable git output
5. **Zero data loss:** No accidental deletion of work-in-progress

## Open Questions

None - implementation approach is clear from error analysis.

## Implementation Notes

**Testing approach:**
- Create test scenarios for each error type
- Verify cleanup safety (no data loss)
- Test rollback mechanisms
- Validate idempotency (safe to retry)

**Backward compatibility:**
- All changes maintain existing behavior
- New flags are opt-in
- Auto-cleanup only removes confirmed orphans
- User prompts prevent accidental deletion
