---
title: "Investigation Report"
type: status_report
component: general
status: draft
tags: []
---

# Investigation Report: Repeated "Dashboard is Live" Notifications

**Issue:** VS Code repeatedly shows "dashboard is live" notifications during development
**Status:** ✅ ROOT CAUSE IDENTIFIED
**Date:** 2025-10-22
**Investigator:** Claude Code

---

## Summary

**Root Cause:** VS Code's automatic port forwarding system combined with stale task configurations causing repeated port scan/forward notifications.

**Primary Issues:**
1. **Port auto-forward notifications** - Dev container configured to notify on port 5001 forward
2. **Stale VS Code tasks** - 17 tasks configured but only 11 worktrees exist
3. **No active dashboard process** - Dashboard isn't actually running

---

## Investigation Findings

### 1. Port Forwarding Configuration

**File:** `.devcontainer/devcontainer.json`
```json
"forwardPorts": [5001, 5432],
"portsAttributes": {
  "5001": {
    "label": "Flask App (port 5001 - avoids macOS AirPlay conflict)",
    "onAutoForward": "notify"  // ← TRIGGERS NOTIFICATION
  }
}
```

**Issue:** `"onAutoForward": "notify"` causes VS Code to show notification whenever:
- Port 5001 is detected as in use
- Port forwarding is auto-enabled
- Container starts/restarts
- File operations trigger port scan

**Why it repeats:**
- Port scan runs periodically
- Any development activity can trigger re-scan
- Even if dashboard isn't running, port check happens

---

### 2. VS Code Tasks Configuration

**File:** `/workspace/.vscode/tasks.json`
**Tasks configured:** 17
**Actual worktrees:** 11

**Problem:** Stale task definitions reference deleted worktrees:
```json
{
  "label": "🌳 7: dashbaord-completion-the-dashboard-needs-to-integr",
  "command": "cd /workspace/.trees/dashbaord-completion-the-dashboard-needs-to-integr/ && bash .claude-init.sh",
  "runOptions": {
    "runOn": "default"  // ← Runs automatically
  }
}
```

**Worktrees in tasks.json but don't exist:**
1. `api-rate-limiting-and-request-throttling-protect-e`
2. `automated-backup-and-disaster-recovery-system-data`
3. `centralized-logging-and-observability-system-struc`
4. `comprehensive-system-testing-framework-end-to-end`
5. `copywriter-i-need-claude-to-act-as-copywriter-and`
6. `dashbaord-completion-the-dashboard-needs-to-integr` ← Dashboard related!
7. ... and 10 more

**Impact:**
- VS Code tries to execute non-existent tasks
- Can trigger port scans
- Adds confusion to terminal/task output

---

### 3. Dashboard Process Status

**Command:** `ps aux | grep -E 'dashboard|flask|gunicorn'`
**Result:** No dashboard processes running

**Conclusion:** Dashboard is **NOT** actually running. Notifications are from port detection, not active service.

---

### 4. Initialization Scripts

**File:** `.claude-init.sh` (in worktrees)
**Purpose:** Launch Claude Code CLI with task context
**Does NOT:** Start Flask/dashboard server

**Example from librarian worktree:**
```bash
# Launch Claude with task context
claude --append-system-prompt "..."
```

**No dashboard startup found** in any initialization scripts.

---

## Why You See Repeated Notifications

### Trigger Sequence
1. **You open VS Code** in workspace
2. **Dev container starts** with port forwarding config
3. **VS Code scans ports** 5001 and 5432
4. **Port 5001 detected** (or becomes "available")
5. **Notification fires** due to `"onAutoForward": "notify"`
6. **Stale tasks attempt to run** → trigger more port activity
7. **Cycle repeats** on file saves, terminal opens, etc.

### Why It Seems Related to Development Activity
- File operations can trigger VS Code extensions
- Extensions may probe ports
- Port scan runs after certain operations
- Creates illusion of "dashboard starting" when you work on files

---

## Solutions

### Solution 1: Change Port Notification Behavior (RECOMMENDED)

**File:** `.devcontainer/devcontainer.json`

**Change from:**
```json
"5001": {
  "label": "Flask App (port 5001 - avoids macOS AirPlay conflict)",
  "onAutoForward": "notify"  // ← CHANGE THIS
}
```

**Change to:**
```json
"5001": {
  "label": "Flask App (port 5001 - avoids macOS AirPlay conflict)",
  "onAutoForward": "silent"  // ← Suppresses notifications
}
```

**Effect:** Port still forwards automatically, but no notification spam

---

### Solution 2: Clean Up Stale VS Code Tasks

**File:** `/workspace/.vscode/tasks.json`

**Current:** 17 tasks, 6 non-existent worktrees
**Target:** Keep only tasks for existing worktrees

**Action:** Remove tasks for deleted worktrees

**Script to identify stale tasks:**
```bash
# List existing worktrees
git worktree list

# Compare with tasks.json
# Manually remove tasks for non-existent worktrees
```

---

### Solution 3: Disable Auto-Task Execution

**File:** `/workspace/.vscode/tasks.json`

**Change from:**
```json
"runOptions": {
  "runOn": "default"  // ← Runs automatically
}
```

**Change to:**
```json
"runOptions": {
  "runOn": "folderOpen"  // ← Only runs when folder opened
}
```

**Or remove** `runOptions` entirely (manual execution only)

---

### Solution 4: Remove Port Forwarding Entirely

**If you don't need automatic port forwarding:**

**File:** `.devcontainer/devcontainer.json`

**Remove or comment out:**
```json
// "forwardPorts": [5001, 5432],
// "portsAttributes": { ... }
```

**Manually forward** ports when needed via VS Code UI

---

## Recommended Fix (Combination Approach)

### Step 1: Fix Port Notifications (Immediate)
```bash
# Edit .devcontainer/devcontainer.json
# Change "notify" → "silent" for port 5001
```

### Step 2: Clean Up Tasks (Maintenance)
```bash
# Edit /workspace/.vscode/tasks.json
# Remove tasks for deleted worktrees
# Keep only 11 tasks matching current worktrees
```

### Step 3: Rebuild Container (Optional)
```bash
# Rebuild dev container to apply changes
# VS Code: Command Palette → "Dev Containers: Rebuild Container"
```

---

## Testing the Fix

### Before Fix
- ⚠️ Notifications appear repeatedly during development
- 📝 Tasks.json has 17 entries (6 stale)
- 🔔 Port 5001 shows notifications

### After Fix
- ✅ No notifications unless manually triggered
- ✅ Tasks.json matches actual worktrees
- ✅ Port forwarding still works silently

### Verification
```bash
# 1. Check tasks match worktrees
git worktree list | wc -l
grep "label.*🌳" /workspace/.vscode/tasks.json | wc -l
# Should be equal

# 2. Verify no dashboard running
ps aux | grep -E 'flask|dashboard|gunicorn' | grep -v grep
# Should be empty

# 3. Check port notification setting
cat .devcontainer/devcontainer.json | grep -A 2 "5001"
# Should show "silent" not "notify"
```

---

## Additional Notes

### Port 5001 vs 5000
**Why port 5001?**
- macOS AirPlay Receiver uses port 5000
- Conflict on macOS systems
- Port 5001 avoids collision

**Dashboard URL when running:**
```
http://localhost:5001/dashboard
```

### How to Actually Start Dashboard
If you **want** to run the dashboard:

```bash
# Option 1: Using startup script
bash scripts/start_dashboard.sh

# Option 2: Direct Python
export PGPASSWORD=goldmember
python app_modular.py

# Option 3: With gunicorn (production)
gunicorn -c gunicorn_config.py app_modular:app
```

---

## Files to Modify

### Priority 1 (Immediate Fix)
1. **.devcontainer/devcontainer.json**
   - Line 59: Change `"onAutoForward": "notify"` → `"silent"`

### Priority 2 (Cleanup)
2. **/workspace/.vscode/tasks.json**
   - Remove tasks for non-existent worktrees
   - Keep only 11 tasks

### Optional
3. **.devcontainer/devcontainer.json**
   - Consider removing `runOptions.runOn` from tasks

---

## Root Cause Analysis

### Why This Happened
1. **Worktree lifecycle** - Worktrees created and deleted over time
2. **Tasks auto-generated** - `/tree build` creates tasks for all worktrees
3. **Tasks not cleaned up** - No automatic cleanup when worktrees removed
4. **Port notifications enabled** - Default setting for Flask app
5. **Confusion from notifications** - Appeared related to dashboard

### Prevention
1. **Auto-cleanup tasks** - Add to `/tree closedone` workflow
2. **Silent port forwarding** - Use "silent" by default
3. **Task generation review** - Periodically audit tasks.json

---

## Conclusion

**Problem:** Port forwarding notifications, not actual dashboard startup
**Cause:** VS Code configuration + stale tasks
**Solution:** Change `"onAutoForward": "silent"` + clean up tasks
**Impact:** Immediate relief from notification spam

**The dashboard is NOT auto-starting.** You're seeing port detection notifications from VS Code's dev container port forwarding feature.

---

## Implementation

To implement the fix, would you like me to:
1. **Update `.devcontainer/devcontainer.json`** (change notify → silent)
2. **Clean up `/workspace/.vscode/tasks.json`** (remove stale tasks)
3. **Both of the above**

Let me know and I'll make the changes!
