# Testing Plan: Worktree Error Prevention

## Test Scenarios

### 1. Pre-Flight Validation Tests

#### Test 1.1: Orphaned Directory Cleanup
**Setup:**
```bash
# Create orphaned directory
mkdir -p /workspace/.trees/test-orphan
echo "test" > /workspace/.trees/test-orphan/file.txt
```

**Expected behavior:**
- `/tree build` detects orphaned directory
- Prompts for removal or auto-removes
- Build proceeds successfully

**Validation:**
```bash
/tree build --verbose
# Should show: "Found orphaned directory: test-orphan"
# Should show: "Removed orphaned directory: test-orphan"
```

#### Test 1.2: Orphaned Branch Cleanup
**Setup:**
```bash
# Create orphaned branch
git checkout -b task/99-orphaned-test
git checkout main
```

**Expected behavior:**
- `/tree build` detects orphaned branch
- Auto-removes branch if no worktree associated
- Build proceeds successfully

**Validation:**
```bash
/tree build
# Should show: "Orphaned branch detected - deleting..."
# Should show: "Orphaned branch removed"
```

#### Test 1.3: Uncommitted Changes Protection
**Setup:**
```bash
# Create directory with uncommitted changes
mkdir -p /workspace/.trees/test-uncommitted
cd /workspace/.trees/test-uncommitted
git init
echo "uncommitted" > file.txt
git add file.txt
```

**Expected behavior:**
- `/tree build` detects uncommitted changes
- Refuses to delete directory
- Provides clear warning

**Validation:**
```bash
/tree build
# Should show: "Skipped (has uncommitted changes): test-uncommitted"
# Should NOT delete directory
```

---

### 2. Stale Lock Detection Tests

#### Test 2.1: Stale index.lock Removal
**Setup:**
```bash
# Create stale lock (old timestamp, empty)
touch /workspace/.git/index.lock
# Make it old (use touch with timestamp)
touch -t 202501010000 /workspace/.git/index.lock
```

**Expected behavior:**
- `/tree build` detects stale lock
- Auto-removes lock
- Build proceeds

**Validation:**
```bash
/tree build
# Should show: "Found git index.lock"
# Should show: "Removed stale index.lock"
```

#### Test 2.2: Active Lock Detection
**Setup:**
```bash
# Create recent lock
touch /workspace/.git/index.lock
```

**Expected behavior:**
- `/tree build` detects active lock
- Refuses to proceed
- Provides clear error message

**Validation:**
```bash
/tree build
# Should show: "Git operation in progress (index.lock is active)"
# Should exit with error
```

---

### 3. Git Worktree Prune Tests

#### Test 3.1: Automatic Prune on Build
**Setup:**
```bash
# Manually remove a worktree directory without git
rm -rf /workspace/.trees/some-worktree
```

**Expected behavior:**
- `/tree build` runs `git worktree prune`
- Cleans up stale references
- Shows pruned items

**Validation:**
```bash
/tree build --verbose
# Should show: "Pruning stale worktree references..."
# Should show: "Pruned stale worktree references" or "No stale references"
```

---

### 4. Error Capture and Verbose Mode Tests

#### Test 4.1: Verbose Mode via Flag
**Setup:**
```bash
# Stage a feature
/tree stage Test error capture feature
```

**Expected behavior:**
- Shows all git command output
- Displays detailed progress

**Validation:**
```bash
/tree build --verbose
# Should show: "Verbose mode enabled"
# Should show detailed git output
```

#### Test 4.2: Verbose Mode via Environment Variable
**Setup:**
```bash
export TREE_VERBOSE=true
```

**Expected behavior:**
- Same as --verbose flag
- Shows all git operations

**Validation:**
```bash
TREE_VERBOSE=true /tree build
# Should show detailed git output
```

#### Test 4.3: Error Output Capture
**Setup:**
```bash
# Force an error by creating conflicting state
mkdir -p /workspace/.trees/test-error
# Create a file where git expects a directory
touch /workspace/.trees/test-error/.git
```

**Expected behavior:**
- Git error is captured and displayed
- User sees actual error message
- Clear indication of what failed

**Validation:**
```bash
/tree build
# Should show actual git error message
# Should NOT show just "Failed to create worktree"
```

---

### 5. Atomic Rollback Tests

#### Test 5.1: Rollback on Validation Failure
**Setup:**
```bash
# Stage multiple features
/tree stage Feature one
/tree stage Feature two
/tree stage Feature three

# Create conflicting state for second feature
# (Create after build starts but before it gets to feature 2)
```

**Expected behavior:**
- First worktree creates successfully
- Second worktree fails validation
- First worktree is rolled back
- No partial state remains

**Validation:**
```bash
/tree build
# Should show: "Rolling back X partially created worktree(s)"
# Verify: git worktree list shows no new worktrees
# Verify: .trees/ is clean
```

#### Test 5.2: Rollback on Git Failure
**Setup:**
```bash
# Stage features
/tree stage Feature test

# Simulate git failure by corrupting git state
```

**Expected behavior:**
- Build fails with git error
- All created worktrees are removed
- Branches are deleted
- Clean state restored

**Validation:**
```bash
/tree build
# Should show: "Rollback complete: X worktree(s) cleaned up"
# Verify clean state
```

---

### 6. Idempotent Operations Tests

#### Test 6.1: Safe Build Retry
**Setup:**
```bash
# Run build once
/tree stage Test feature
/tree build

# Immediately run again
/tree build
```

**Expected behavior:**
- Second build detects existing worktrees
- Either skips or reuses
- No errors about "already exists"

**Validation:**
```bash
/tree build
/tree build
# Second run should not fail
```

#### Test 6.2: Dev Branch Reuse
**Setup:**
```bash
# Create dev branch manually
git checkout -b develop/v4.3.0-worktrees-20250101-000000
git checkout main
```

**Expected behavior:**
- Build detects existing branch
- Reuses instead of erroring
- Shows "reusing" message

**Validation:**
```bash
/tree build
# Should show: "Development branch already exists (reusing)"
```

---

### 7. Integration Tests

#### Test 7.1: Full Build Cycle with Cleanup
**Setup:**
```bash
# Create multiple types of issues
mkdir -p /workspace/.trees/orphan-dir
git checkout -b task/99-orphan-branch
git checkout main
touch /workspace/.git/index.lock
touch -t 202501010000 /workspace/.git/index.lock

# Stage real features
/tree stage Integration test feature one
/tree stage Integration test feature two
```

**Expected behavior:**
- Pre-flight cleans all issues
- Build succeeds completely
- All worktrees created

**Validation:**
```bash
/tree build --verbose
# Should show all cleanup steps
# Should create all worktrees
# Should show "BUILD SUMMARY" with success
```

#### Test 7.2: Error Recovery Flow
**Setup:**
```bash
# Intentionally create failure scenario
/tree stage Recovery test
# Create conflict manually
mkdir -p /workspace/.trees/recovery-test
git worktree add /workspace/.trees/recovery-test
```

**Expected behavior:**
- Build detects conflict
- Shows clear error
- User can fix and retry
- Retry succeeds

**Validation:**
```bash
/tree build  # Should fail with clear message
# User fixes issue
/tree build  # Should succeed
```

---

## Test Results Template

### Test Run: [Date]

| Test ID | Description | Status | Notes |
|---------|-------------|--------|-------|
| 1.1 | Orphaned Directory Cleanup | ⬜ Pass ⬜ Fail | |
| 1.2 | Orphaned Branch Cleanup | ⬜ Pass ⬜ Fail | |
| 1.3 | Uncommitted Changes Protection | ⬜ Pass ⬜ Fail | |
| 2.1 | Stale Lock Removal | ⬜ Pass ⬜ Fail | |
| 2.2 | Active Lock Detection | ⬜ Pass ⬜ Fail | |
| 3.1 | Automatic Prune | ⬜ Pass ⬜ Fail | |
| 4.1 | Verbose Mode Flag | ⬜ Pass ⬜ Fail | |
| 4.2 | Verbose Mode Env Var | ⬜ Pass ⬜ Fail | |
| 4.3 | Error Output Capture | ⬜ Pass ⬜ Fail | |
| 5.1 | Rollback on Validation Failure | ⬜ Pass ⬜ Fail | |
| 5.2 | Rollback on Git Failure | ⬜ Pass ⬜ Fail | |
| 6.1 | Safe Build Retry | ⬜ Pass ⬜ Fail | |
| 6.2 | Dev Branch Reuse | ⬜ Pass ⬜ Fail | |
| 7.1 | Full Build Cycle | ⬜ Pass ⬜ Fail | |
| 7.2 | Error Recovery Flow | ⬜ Pass ⬜ Fail | |

---

## Manual Testing Checklist

- [ ] Run syntax validation: `bash -n .claude/scripts/tree.sh`
- [ ] Test help command: `/tree help`
- [ ] Test each prevention function individually
- [ ] Test rollback mechanism
- [ ] Test verbose mode
- [ ] Test error capture
- [ ] Test full build cycle
- [ ] Verify no data loss scenarios
- [ ] Test on clean repository
- [ ] Test with existing worktrees
- [ ] Test concurrent operations (if applicable)

---

## Success Criteria

✅ All test scenarios pass
✅ No data loss in any scenario
✅ Error messages are clear and actionable
✅ Rollback leaves clean state
✅ Idempotent operations work correctly
✅ Verbose mode shows detailed output
✅ Auto-cleanup works safely
