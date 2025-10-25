---
title: "Action Plan Resource Monitoring"
type: technical_doc
component: general
status: draft
tags: []
---

# Action Plan: Real-Time Worktree Resource Monitoring

**Based on:** PRD v1.0 - Real-Time Worktree Resource Monitoring
**Created:** 2025-10-09
**Status:** In Progress

## Overview
Implement a live resource monitoring system for git worktrees with auto-refresh, adaptive sampling, and multi-view display.

## Requirements Summary (from PRD Open Questions)
- ✅ Historical data: Session-only (no database)
- ✅ Sampling: Adaptive refresh based on activity level
- ✅ Remote monitoring: Local-only
- ❓ Integration: Separate tool (decide during implementation)
- ✅ Notifications: Terminal-only (no desktop notifications)
- ❓ Cloud environments: Standard behavior (no special handling)
- ✅ Battery optimization: Not implemented
- ✅ Multi-user: Single user only

---

## Phase 1: Foundation (Steps 1-3)

### Step 1: Create Core Script Structure
**File:** `monitor-resources.sh`
**Tasks:**
- Create executable bash script with header
- Define color constants and global variables
- Set up signal handlers (SIGINT, SIGTERM)
- Implement basic argument parsing (--help, --interval, --view)
- Add script initialization and cleanup functions

**Deliverable:** Working script skeleton that can be executed

---

### Step 2: Implement Configuration System
**File:** `.worktree-monitor.conf` (template)
**Tasks:**
- Create default configuration file template
- Implement config file parser (bash function)
- Define default thresholds (disk: 1024MB, CPU: 75%, memory: 1024MB)
- Add config override from command-line arguments
- Create config validation function

**Deliverable:** Configuration system that loads defaults and overrides

---

### Step 3: Add Worktree Discovery
**Tasks:**
- Implement function to find all task worktrees
- Filter worktrees by branch pattern (`task/` prefix)
- Store worktree paths and names in array
- Add error handling for missing worktrees
- Validate worktree accessibility

**Deliverable:** Function that returns list of all monitorable worktrees

---

## Phase 2: Data Collection (Steps 4-7)

### Step 4: Implement Disk Usage Monitoring
**Functions:**
- `get_disk_usage()` - Total worktree size
- `get_git_dir_size()` - .git directory size separately
- `calculate_disk_growth()` - Track size changes over time
- Cache disk usage results (expensive operation)
- Format output in human-readable units (MB/GB)

**Commands:**
```bash
du -sb "$worktree_path" --exclude=.git 2>/dev/null
du -sb "$worktree_path/.git" 2>/dev/null
```

**Deliverable:** Accurate disk usage metrics per worktree

---

### Step 5: Implement Git Metrics Collection
**Functions:**
- `get_git_status()` - Uncommitted files count
- `get_diff_stats()` - Lines added/removed
- `get_commits_ahead_behind()` - Compare to develop branch
- `get_last_commit_time()` - Timestamp of last commit
- `count_branches()` - Number of branches in worktree

**Commands:**
```bash
git -C "$path" status --porcelain
git -C "$path" diff --numstat develop/v4.2.0
git -C "$path" rev-list --count HEAD ^develop/v4.2.0
git -C "$path" log -1 --format=%ct
```

**Deliverable:** Complete git repository metrics

---

### Step 6: Implement File Statistics
**Functions:**
- `count_files()` - Total files excluding .git
- `count_by_type()` - File type distribution
- `count_lines_of_code()` - LOC for source files
- Fallback to simple counting if `cloc` unavailable

**Commands:**
```bash
find "$path" -type f -not -path "*/.git/*" | wc -l
find "$path" -type f -name "*.py" | xargs wc -l 2>/dev/null
```

**Deliverable:** File statistics with type breakdown

---

### Step 7: Implement Process Monitoring
**Functions:**
- `find_processes()` - Detect processes in worktree directory
- `get_process_cpu()` - CPU usage per process
- `get_process_memory()` - Memory usage per process
- `aggregate_worktree_resources()` - Sum all processes in worktree

**Commands:**
```bash
lsof +D "$path" 2>/dev/null | awk 'NR>1 {print $2}' | sort -u
ps -p $pid -o %cpu,%mem,comm --no-headers
```

**Deliverable:** Active process monitoring per worktree

---

## Phase 3: Display Layer (Steps 8-10)

### Step 8: Implement Table View
**Function:** `display_table_view()`
**Tasks:**
- Create formatted table header
- Display one row per worktree with key metrics
- Implement column alignment and truncation
- Add color coding based on thresholds
- Display summary row at bottom

**Layout:**
```
WORKTREE             DISK    CPU%   MEM(MB)  FILES  CHANGES  STATUS
──────────────────────────────────────────────────────────────────
claude-refinement    245MB   12.3%   156MB   342    15       🟢 Normal
```

**Deliverable:** Compact table view of all worktrees

---

### Step 9: Implement Detailed View
**Function:** `display_detailed_view()`
**Tasks:**
- Create detailed breakdown for single worktree
- Show disk usage with visual bars
- Display complete git metrics
- List file statistics by type
- Show all active processes with details
- Add navigation controls (next/previous worktree)

**Deliverable:** Comprehensive per-worktree detailed view

---

### Step 10: Implement Summary Dashboard
**Function:** `display_summary_view()`
**Tasks:**
- Calculate totals across all worktrees
- Show top 5 resource consumers
- Display system-wide available resources
- Create ASCII bar graphs for distribution
- Add average metrics per worktree

**Deliverable:** High-level summary dashboard

---

## Phase 4: Real-Time Features (Steps 11-13)

### Step 11: Implement Auto-Refresh Loop
**Function:** `monitor_loop()`
**Tasks:**
- Create infinite loop with sleep interval
- Clear screen and redraw on each iteration
- Implement adaptive refresh rate (slow down when idle)
- Add timestamp to display ("Last Update: HH:MM:SS")
- Handle terminal resize events

**Deliverable:** Continuously updating display

---

### Step 12: Add Keyboard Controls
**Function:** `handle_input()`
**Tasks:**
- Non-blocking input reading
- 'p' - Pause/resume monitoring
- 'q' - Quit
- 'v' - Switch view mode (table/detailed/summary)
- '+'/'-' - Increase/decrease refresh rate
- Arrow keys - Navigate in detailed view
- Display help bar at top

**Deliverable:** Interactive keyboard controls

---

### Step 13: Implement Adaptive Refresh
**Function:** `calculate_refresh_interval()`
**Tasks:**
- Detect activity level (git status changes, new processes)
- Fast refresh (1s) when activity detected
- Slow refresh (5s) when idle for > 30 seconds
- Very slow refresh (10s) when idle for > 5 minutes
- Cache expensive operations longer during slow periods

**Deliverable:** Intelligent adaptive refresh rate

---

## Phase 5: Alert System (Steps 14-15)

### Step 14: Implement Threshold Checking
**Function:** `check_thresholds()`
**Tasks:**
- Compare metrics against configured thresholds
- Classify alerts: Normal (green), Warning (yellow), Critical (red)
- Track alert history (session-only)
- Generate alert messages with context
- Return status code for each worktree

**Deliverable:** Threshold-based status classification

---

### Step 15: Add Alert Display
**Function:** `display_alerts()`
**Tasks:**
- Show active alerts at bottom of screen
- Color-code alert severity
- Include specific metric that triggered alert
- Add alert count to summary
- Optional: Terminal bell for new critical alerts

**Deliverable:** Visual alert notifications

---

## Phase 6: Data Export (Step 16)

### Step 16: Implement Export Functionality
**Functions:**
- `export_json()` - Current snapshot to JSON
- `export_csv()` - Metrics to CSV format
- Command-line flags: `--export-json`, `--export-csv`
- Add timestamp to export filenames
- Validate export before writing

**Files:**
- `worktree-metrics-YYYYMMDD-HHMMSS.json`
- `worktree-metrics-YYYYMMDD-HHMMSS.csv`

**Deliverable:** Data export in multiple formats

---

## Phase 7: Testing & Documentation (Steps 17-18)

### Step 17: Testing
**Test Cases:**
- Single worktree monitoring
- Multiple worktrees (13+)
- High CPU worktree detection
- Large disk usage detection
- Process detection accuracy
- Adaptive refresh behavior
- Keyboard controls responsiveness
- Configuration file loading
- Export functionality
- Edge cases: deleted worktrees, permission errors

**Deliverable:** Validated monitoring system

---

### Step 18: Documentation
**Files to Update:**
- `README.md` - Add monitoring section
- `monitor-resources.sh` - Inline documentation
- `.worktree-monitor.conf` - Comment all options

**Content:**
- Usage instructions
- Configuration options
- Keyboard shortcuts
- Threshold customization
- Troubleshooting guide
- Performance considerations

**Deliverable:** Complete user documentation

---

## Step 19: Integration & Finalization

### Tasks:
- Add `monitor-resources.sh` to worktree manager toolkit
- Create default `.worktree-monitor.conf`
- Update main README with monitoring workflow
- Add monitoring to recommended daily workflow
- Stage and commit all changes
- Push to task/00-worktree-manager branch

**Deliverable:** Production-ready monitoring tool

---

## Success Criteria

- ✅ Real-time display updates smoothly (< 100ms lag)
- ✅ Adaptive refresh reduces overhead during idle periods
- ✅ All metrics accurate within 5% margin
- ✅ Keyboard controls responsive and intuitive
- ✅ Alerts trigger correctly based on thresholds
- ✅ Export generates valid JSON/CSV
- ✅ Documentation complete and clear
- ✅ Script handles errors gracefully (no crashes)

---

## Timeline Estimate

- Phase 1 (Foundation): ~30 minutes
- Phase 2 (Data Collection): ~45 minutes
- Phase 3 (Display Layer): ~45 minutes
- Phase 4 (Real-Time): ~30 minutes
- Phase 5 (Alerts): ~20 minutes
- Phase 6 (Export): ~20 minutes
- Phase 7 (Testing & Docs): ~30 minutes
- **Total: ~3.5 hours**

---

**Document Version:** 1.0
**Created:** 2025-10-09
**Type:** action-plan
**Status:** In Progress
**Next Step:** Step 1 - Create Core Script Structure
