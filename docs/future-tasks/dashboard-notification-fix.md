---
title: Fix VS Code Dashboard Notification Spam
type: task
status: deferred
priority: medium
created: 2025-10-22
scheduled_for: after-worktree-cycle
workspace: main
branch: feature/v4.5.1-development
---

# Task: Fix VS Code Dashboard Notification Spam

**Status:** Deferred until after worktree development cycle
**Priority:** Medium
**Estimated Time:** 15-30 minutes
**Target Location:** Main workspace (not worktree)
**Target Branch:** Feature branch (e.g., `feature/v4.5.1-development`)

---

## Issue Summary

VS Code repeatedly shows "dashboard is live" notifications during development activity. This is caused by port forwarding configuration, not an actually running dashboard.

**Investigation:** See `tasks/dashboard-notification-investigation/INVESTIGATION_REPORT.md`

---

## Root Cause

**File:** `.devcontainer/devcontainer.json`
```json
"5001": {
  "label": "Flask App (port 5001)",
  "onAutoForward": "notify"  // ← Triggers notification on every port scan
}
```

**Contributing Factor:** Stale VS Code tasks (17 tasks, 11 worktrees = 6 stale)

---

## Changes Required

### Change 1: Silence Port Notifications
**File:** `/workspace/.devcontainer/devcontainer.json`
**Line:** ~59

**From:**
```json
"5001": {
  "label": "Flask App (port 5001 - avoids macOS AirPlay conflict)",
  "onAutoForward": "notify"
},
```

**To:**
```json
"5001": {
  "label": "Flask App (port 5001 - avoids macOS AirPlay conflict)",
  "onAutoForward": "silent"
},
```

### Change 2: Clean Up Stale VS Code Tasks
**File:** `/workspace/.vscode/tasks.json`

**Remove tasks for these deleted worktrees:**
1. `api-rate-limiting-and-request-throttling-protect-e`
2. `automated-backup-and-disaster-recovery-system-data`
3. `centralized-logging-and-observability-system-struc`
4. `comprehensive-system-testing-framework-end-to-end`
5. `copywriter-i-need-claude-to-act-as-copywriter-and`
6. `dashbaord-completion-the-dashboard-needs-to-integr`
7. And ~11 more (compare with `git worktree list`)

**Keep only tasks for existing worktrees.**

---

## Implementation Steps

### Step 1: Verify Current State
```bash
cd /workspace

# Count current worktrees
git worktree list | wc -l

# Count tasks in tasks.json
grep '"label": "🌳' .vscode/tasks.json | wc -l

# Should be: 11 worktrees, but more tasks
```

### Step 2: Apply Changes

#### Edit devcontainer.json
```bash
vi .devcontainer/devcontainer.json

# Line 59: Change "notify" to "silent"
```

#### Clean up tasks.json
```bash
# Get list of existing worktrees
git worktree list | awk '{print $1}' | sed 's|/workspace/.trees/||' > /tmp/existing-worktrees.txt

# Manually edit tasks.json
vi .vscode/tasks.json

# Remove tasks where worktree directory doesn't exist
# Keep only 11 tasks matching existing worktrees
```

### Step 3: Test
```bash
# Verify no dashboard running
ps aux | grep -E 'flask|dashboard|gunicorn' | grep -v grep

# Verify notification setting
grep -A 2 '"5001"' .devcontainer/devcontainer.json

# Verify task count
grep '"label": "🌳' .vscode/tasks.json | wc -l
# Should equal: git worktree list | wc -l
```

### Step 4: Commit
```bash
git add .devcontainer/devcontainer.json .vscode/tasks.json
git commit -m "fix(vscode): Silence port notifications and clean up stale worktree tasks

- Changed port 5001 notification from 'notify' to 'silent'
- Removed 6 stale VS Code tasks for deleted worktrees
- Tasks now match actual worktrees (11 total)

Resolves repeated 'dashboard is live' notification spam during development.

🤖 Generated with Claude Code
Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Validation

### Before Fix
- ⚠️ Notifications appear repeatedly during development
- 📝 Tasks.json has 17+ entries (6+ stale)
- 🔔 Port 5001 shows notifications on port scan

### After Fix
- ✅ No notifications unless manually triggered
- ✅ Tasks.json matches actual worktrees (11 tasks = 11 worktrees)
- ✅ Port forwarding still works silently
- ✅ No dashboard processes running (as expected)

### Verification Commands
```bash
# 1. Check notification setting
cat .devcontainer/devcontainer.json | grep -A 2 "5001"
# Should show: "onAutoForward": "silent"

# 2. Verify task count matches worktrees
git worktree list | wc -l
grep "label.*🌳" .vscode/tasks.json | wc -l
# Should be equal (11 and 11)

# 3. Confirm no dashboard running
ps aux | grep -E 'flask|dashboard' | grep -v grep
# Should be empty
```

---

## Dependencies

**None** - This is a standalone configuration fix

---

## Risks

**Low risk:**
- Configuration changes only
- No code changes
- Port forwarding still works (just silent)
- Tasks can be manually triggered if needed
- Reversible (change "silent" back to "notify")

---

## Notes

### Why Port 5001?
- macOS AirPlay Receiver uses port 5000
- Port 5001 avoids collision on macOS systems

### Dashboard URLs (When Actually Running)
```
http://localhost:5001/dashboard
http://localhost:5001/dashboard/jobs
```

### How to Actually Start Dashboard
```bash
bash scripts/start_dashboard.sh
# or
python app_modular.py
```

---

## Related Documentation

- Investigation Report: `tasks/dashboard-notification-investigation/INVESTIGATION_REPORT.md`
- Dev Container Docs: `.devcontainer/README.md`
- VS Code Tasks Docs: `.vscode/README.md` (if exists)

---

## Checklist

Before implementation:
- [ ] Complete current worktree development cycle
- [ ] Merge/close all active worktrees
- [ ] Switch to main workspace
- [ ] Checkout feature branch

During implementation:
- [ ] Edit `.devcontainer/devcontainer.json` (line 59)
- [ ] Edit `.vscode/tasks.json` (remove 6+ stale tasks)
- [ ] Verify task count matches worktree count
- [ ] Test: no notifications on file save
- [ ] Commit changes with conventional message

After implementation:
- [ ] Rebuild dev container (optional)
- [ ] Verify notifications stopped
- [ ] Verify port forwarding still works
- [ ] Close this task

---

**Scheduled for:** After worktree development cycle completes
**Target workspace:** `/workspace` (main workspace)
**Target branch:** Feature branch (not main)
