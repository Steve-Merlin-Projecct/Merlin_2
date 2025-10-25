---
title: "Prd Real Time Resource Monitoring"
type: technical_doc
component: general
status: draft
tags: []
---

# PRD: Real-Time Worktree Resource Monitoring

## Introduction/Overview

A live monitoring system for tracking resource consumption across all active worktrees in real-time. This feature addresses the need to understand resource utilization patterns during parallel development, enabling developers to identify resource-intensive worktrees, detect abnormal behavior, and optimize their development workflow.

The system will provide continuous, auto-refreshing metrics for disk usage, file counts, git repository statistics, and active process monitoring across all task worktrees simultaneously.

## Goals

1. **Primary Goal**: Provide real-time visibility into resource consumption across all worktrees with automatic refresh and minimal performance overhead
2. **Secondary Goal**: Enable proactive identification of resource-intensive worktrees before they impact system performance
3. **Tertiary Goal**: Establish baseline metrics for worktree health monitoring and capacity planning

## User Stories

1. **As a developer**, I want to see live disk usage across all worktrees, so that I can identify which tasks are consuming the most storage space.

2. **As a developer**, I want to monitor CPU and memory usage per worktree, so that I can detect runaway processes or resource leaks during development.

3. **As a team lead**, I want to track code growth metrics (files, lines of code) in real-time, so that I can assess development velocity across parallel tasks.

4. **As a developer**, I want automatic alerts when a worktree exceeds resource thresholds, so that I can take corrective action before system performance degrades.

5. **As a developer**, I want historical resource trends, so that I can understand how resource usage evolves over a development session.

## Functional Requirements

### 1. Real-Time Display
1.1. Auto-refresh display at configurable intervals (default: 2 seconds)
1.2. Support for both table view (compact) and detailed view (per-worktree breakdown)
1.3. Color-coded status indicators (green/yellow/red) based on resource thresholds
1.4. Keyboard controls to pause/resume, change refresh rate, switch views
1.5. Display last update timestamp

### 2. Disk Usage Monitoring
2.1. Show total disk usage per worktree in human-readable format (MB/GB)
2.2. Calculate disk usage growth rate (MB/hour)
2.3. Display percentage of total available disk space
2.4. Track `.git` directory size separately from working tree
2.5. Alert when disk usage exceeds configurable threshold (default: 1GB)

### 3. Git Repository Metrics
3.1. Count uncommitted files (staged, unstaged, untracked)
3.2. Calculate size of uncommitted changes (diff size)
3.3. Display commit count ahead/behind develop branch
3.4. Show last commit timestamp
3.5. Track number of branches per worktree

### 4. File Statistics
4.1. Total file count (excluding .git)
4.2. File type distribution (Python, JavaScript, Markdown, etc.)
4.3. Lines of code (LOC) count for source files
4.4. LOC added/removed compared to base branch
4.5. Largest files by size

### 5. Process Monitoring
5.1. Detect active processes running in each worktree directory
5.2. Display CPU usage percentage per worktree
5.3. Display memory (RAM) usage in MB per worktree
5.4. Show process count per worktree
5.5. Identify specific process names (Python, Node.js, etc.)

### 6. Summary Dashboard
6.1. Total resources across all worktrees
6.2. Top 5 resource-consuming worktrees
6.3. System-wide metrics (total disk, CPU, memory available)
6.4. Average resource usage per worktree
6.5. Resource distribution charts (ASCII bar graphs)

### 7. Alerting and Thresholds
7.1. Configurable thresholds for disk, CPU, memory
7.2. Visual alerts (color change, blinking, sound optional)
7.3. Alert history log
7.4. Threshold configuration file (`.worktree-monitor.conf`)

### 8. Data Export
8.1. Export current snapshot to JSON
8.2. Export historical data to CSV
8.3. Log metrics to file for trend analysis
8.4. Integration with existing worktree-status.sh output

## Non-Goals (Out of Scope)

1. Network bandwidth monitoring (not typically relevant to worktree operations)
2. GPU usage monitoring (most development tasks don't use GPU)
3. Detailed profiling of individual processes (use dedicated profilers instead)
4. Distributed monitoring across multiple machines
5. Database query performance monitoring
6. Browser-based GUI (terminal-only interface)
7. Historical data storage beyond current session (future enhancement)
8. Integration with external monitoring systems (Prometheus, Grafana, etc.)

## Design Considerations

### Terminal UI Layout

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ 📊 Worktree Resource Monitor                      Last Update: 10:23:45 AM  │
│ Refresh: 2s | Press 'p' to pause, 'q' to quit, 'v' to change view          │
├─────────────────────────────────────────────────────────────────────────────┤
│ WORKTREE             DISK    CPU%   MEM(MB)  FILES  CHANGES  STATUS         │
│ ────────────────────────────────────────────────────────────────────────    │
│ claude-refinement    245MB   12.3%   156MB   342    15 📝    🟢 Normal      │
│ marketing-content    1.2GB   45.7%   892MB   1,245  127 📝   🟡 High Disk   │
│ script-testing       89MB    2.1%    45MB    156    3 📝     🟢 Normal      │
│ dashboard-redesign   567MB   78.3%   1.2GB   892    45 📝    🔴 High CPU    │
│ ...                                                                          │
├─────────────────────────────────────────────────────────────────────────────┤
│ SUMMARY: 14 worktrees | Total Disk: 8.4GB | Avg CPU: 23.4% | Avg Mem: 345MB│
│ 🔴 ALERT: dashboard-redesign exceeds CPU threshold (78.3% > 75%)            │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Detailed View (Single Worktree)
```
┌─ claude-refinement (.trees/claude-refinement) ──────────────────────────────┐
│ Disk Usage                                                                   │
│   Working Tree:  198MB  ████████████░░░░░░░░ 65%                           │
│   .git Directory: 47MB  ████░░░░░░░░░░░░░░░░ 35%                           │
│   Total:         245MB  Growth: +12MB/hour                                  │
│                                                                              │
│ Git Metrics                                                                  │
│   Uncommitted:   15 files (8 staged, 7 unstaged)                           │
│   Diff Size:     +342 lines / -89 lines                                    │
│   Commits:       ↑7 ahead of develop                                       │
│   Last Commit:   2 hours ago                                               │
│                                                                              │
│ File Statistics                                                             │
│   Total Files:   342                                                        │
│   Python:        156 files (12,345 LOC)                                    │
│   Markdown:      45 files                                                   │
│   JSON:          12 files                                                   │
│                                                                              │
│ Active Processes                                                            │
│   python (PID 12345):  12.3% CPU, 156MB RAM                               │
│   No other processes detected                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Color Coding
- 🟢 Green: Normal (< 70% of threshold)
- 🟡 Yellow: Warning (70-90% of threshold)
- 🔴 Red: Critical (> 90% of threshold)

## Technical Considerations

### Implementation Approach
- **Language**: Bash script with optional Python fallback for complex calculations
- **Display Library**: `tput` for terminal control, or `ncurses` for advanced UI
- **Refresh Mechanism**: `watch` command or custom loop with `sleep`
- **Process Detection**: `ps`, `lsof`, `pgrep` to identify processes by working directory

### Performance Optimization
- Cache expensive operations (disk usage) with shorter refresh intervals
- Use `git diff --numstat` for fast line count calculations
- Implement lazy loading for detailed views
- Sample processes rather than scanning all if count is high
- Use `git ls-files` instead of `find` for file counting

### Data Collection Commands
```bash
# Disk usage
du -sh "$worktree_path" --exclude=.git
du -sh "$worktree_path/.git"

# Git metrics
git status --porcelain | wc -l
git diff --stat develop/v4.2.0
git rev-list --count HEAD ^develop/v4.2.0

# File statistics
find "$worktree_path" -type f -not -path "*/.git/*" | wc -l
cloc "$worktree_path" --quiet --json

# Process monitoring
lsof +D "$worktree_path" | awk 'NR>1 {print $2}' | sort -u
ps -p $pid -o %cpu,%mem,comm --no-headers
```

### Dependencies
- Standard Unix tools: `du`, `ps`, `lsof`, `git`
- Optional: `cloc` (count lines of code) - fallback to basic `wc -l` if not available
- Optional: `jq` for JSON export
- Terminal: 80x24 minimum, 120x40 recommended

### Configuration File Format
```ini
# .worktree-monitor.conf
[refresh]
interval_seconds=2

[thresholds]
disk_mb=1024
cpu_percent=75.0
memory_mb=1024
uncommitted_files=50

[display]
default_view=table
show_alerts=true
color_enabled=true

[monitoring]
track_processes=true
log_to_file=false
log_path=./worktree-monitor.log
```

## Success Metrics

1. **Performance**: Monitor runs with < 5% CPU overhead on host system
2. **Accuracy**: Resource measurements within 5% of actual values
3. **Responsiveness**: Display updates within 100ms of refresh trigger
4. **Usability**: Developers can identify resource issues within 10 seconds of opening monitor
5. **Adoption**: 80% of developers using monitor during parallel development sessions
6. **Early Detection**: 90% of resource issues identified before system impact

## Open Questions

1. **Historical Data**: Should we store historical metrics in a local database (SQLite) for trend analysis, or keep it session-only?
no
2. **Sampling Frequency**: What's the optimal balance between refresh rate and system overhead? Should we implement adaptive refresh based on activity level?
adaptive refresh sounds good.
3. **Remote Monitoring**: Should we support monitoring worktrees on remote machines via SSH, or keep it local-only?
no
4. **Integration**: Should resource metrics be integrated into existing `worktree-status.sh` or remain a separate tool?
I don't know
5. **Notification System**: Should we implement desktop notifications (via `notify-send`) for critical alerts, or terminal-only?
no
6. **Cloud Environments**: How should monitoring behave in containerized environments (Docker, Kubernetes) where resource limits are different?
I don't know.
7. **Battery Optimization**: On laptops, should refresh rate automatically slow down when on battery power?
no
8. **Multi-User**: How should the monitor handle worktrees owned by different users (permission issues)?
I'm the only user.
---

**Document Version:** 1.0
**Created:** 2025-10-09
**Type:** feature
**Status:** Draft
**Branch:** task/00-worktree-manager
**Worktree:** .trees/worktree-manager
