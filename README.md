# Worktree Manager

**Task 00: Worktree Management Tools**

This worktree contains tools for creating and managing multiple worktrees for parallel development.

## Scripts

### 1. Create Worktrees in Batch
`./create-worktree-batch.sh <tasks-file> [base-branch]`

Create multiple worktrees from a task list file.

**Example tasks file format:**
```
# tasks.txt
claude-refinement:Claude.md refinement and agent creation
marketing-content:Marketing automation content generation
script-testing:Script testing framework
template-creation:Template sourcing and creation
```

**Usage:**
```bash
./create-worktree-batch.sh tasks.txt develop/v4.2.0
```

### 2. Open All Terminals
`./open-terminals.sh`

Automatically open terminals for all worktrees using tmux/screen, or generate VS Code workspace.

**Features:**
- Creates tmux session with window per worktree
- Falls back to screen if tmux not available
- Generates `worktrees.code-workspace` for VS Code
- Color-coded windows for easy navigation

**Usage:**
```bash
./open-terminals.sh
```

**Tmux navigation:**
- Switch windows: `Ctrl+b` then `0-9`
- List windows: `Ctrl+b` then `w`
- Detach: `Ctrl+b` then `d`
- Reattach: `tmux attach -t worktrees-<session>`

### 3. Check Worktree Status
`./worktree-status.sh`

Display status dashboard for all worktrees.

**Shows:**
- Uncommitted changes
- Commits ahead/behind develop
- Current branch
- Sync status

**Usage:**
```bash
./worktree-status.sh
```

**Output:**
```
WORKTREE                            BRANCH                         STATUS          COMMITS
--------                            ------                         ------          -------
claude-refinement                   task/01-claude-refinement      CLEAN           ↑3
marketing-content                   task/02-marketing-content      MODIFIED        synced
script-testing                      task/03-script-testing         CLEAN           ↓2
```

### 4. Sync All Worktrees
`./sync-all-worktrees.sh`

Pull latest changes from develop/v4.2.0 in all worktrees.

**Features:**
- Auto-stashes uncommitted changes
- Pulls with rebase
- Detects conflicts
- Restores stashed changes

**Usage:**
```bash
./sync-all-worktrees.sh
```

### 5. Real-Time Resource Monitor
`./monitor-resources.sh [OPTIONS]`

Live monitoring of disk usage, CPU, memory, git metrics, and file statistics across all worktrees.

**Features:**
- Real-time auto-refresh display (2-second default)
- Multiple view modes: table, detailed, summary
- Color-coded status indicators (🟢 Normal, 🟡 Warning, 🔴 Critical)
- Disk usage tracking with caching
- Git metrics (uncommitted files, commits ahead, diff stats)
- Process monitoring (CPU & memory per worktree)
- Configurable alert thresholds
- Data export (JSON/CSV)

**Views:**

**Table View** - Compact overview of all worktrees
```
WORKTREE             DISK    CPU%   MEM(MB)  FILES  CHANGES  STATUS
─────────────────────────────────────────────────────────────────
claude-refinement    245MB   12.3%   156MB   342    15       🟢 Normal
marketing-content    1.2GB   45.7%   892MB   1245   127      🟡 High Disk
dashboard-redesign   567MB   78.3%   1.2GB   892    45       🔴 High CPU
```

**Detailed View** - Complete breakdown of single worktree
```
Disk Usage
  Working Tree:  198MB
  .git Directory: 47MB
  Total:         245MB

Git Metrics
  Uncommitted:   15 files
  Diff Size:     +342 / -89 lines
  Commits Ahead: ↑7
  Last Commit:   2 hours ago

Active Processes
  python (PID 12345): 12.3% CPU, 156MB RAM
```

**Summary View** - System-wide statistics and top consumers
```
System-Wide Summary
  Total Worktrees:     14
  Total Disk Usage:    8.4GB
  Total Files:         7426
  Status Distribution:
    ● Normal:   11
    ● Warning:  2
    ● Critical: 1

Top 5 Disk Consumers
  marketing-content     1.2GB ████████████
  dashboard-redesign    567MB ██████
```

**Usage:**
```bash
# Start monitoring (default: table view, 2s refresh)
./monitor-resources.sh

# Start with specific view
./monitor-resources.sh -v summary

# Custom refresh interval
./monitor-resources.sh -i 5

# Create default configuration file
./monitor-resources.sh --create-config

# Export current snapshot
./monitor-resources.sh --export-json metrics.json
./monitor-resources.sh --export-csv metrics.csv
```

**Keyboard Controls:**
- `p` - Pause/resume monitoring
- `q` - Quit
- `v` - Switch view mode (table → detailed → summary)
- `+/-` - Increase/decrease refresh rate
- `↑/↓` - Navigate worktrees in detailed view

**Configuration:**

Edit `.worktree-monitor.conf` to customize thresholds:
```ini
# Refresh interval in seconds
interval_seconds=2

# Resource thresholds for alerts
disk_mb=1024          # Warning at 717MB, Critical at 922MB
cpu_percent=75.0      # Warning at 52.5%, Critical at 67.5%
memory_mb=1024        # Warning at 717MB, Critical at 922MB

# Display settings
default_view=table    # table | detailed | summary
```

**Status Indicators:**
- 🟢 **Normal**: All metrics < 70% of threshold
- 🟡 **Warning**: Any metric 70-90% of threshold
- 🔴 **Critical**: Any metric > 90% of threshold

**Performance:**
- Disk usage cached for 10 seconds (expensive operation)
- Process detection using `lsof` (requires root or same user)
- Adaptive refresh slows down when idle (future enhancement)

## Workflow

### Initial Setup
1. Create task list file
2. Run batch creator:
   ```bash
   ./create-worktree-batch.sh my-tasks.txt
   ```
3. Open all terminals:
   ```bash
   ./open-terminals.sh
   ```

### Daily Development
1. Check status:
   ```bash
   ./worktree-status.sh
   ```
2. Sync with latest:
   ```bash
   ./sync-all-worktrees.sh
   ```
3. Work in your worktrees
4. Commit and push regularly

### VS Code Integration
1. Generate workspace:
   ```bash
   ./open-terminals.sh  # Creates worktrees.code-workspace
   ```
2. Open in VS Code:
   - File → Open Workspace from File...
   - Select `worktrees.code-workspace`
3. All worktrees appear as folders in sidebar

## Task List Template

Create a `tasks.txt` file with this format:

```
# Project v4.2.0 Tasks
# Format: <worktree-name>:<description>

# Foundation
claude-refinement:Claude.md refinement and agent creation
github-streamline:Streamline GitHub connection
librarian:File organization planning

# Content & Templates
marketing-content:Marketing automation content generation
gemini-prompts:Gemini prompt improvements
template-creation:Template sourcing and creation
docx-verification:Word.docx verification metrics

# Delivery
calendly:Calendly integration
email-refinement:Email system refinement

# Monitoring
dashboard-redesign:Dashboard redesign with Node.js
database-viz:Animated database visualization
analytics:Recruiter click tracking

# Quality
script-testing:Script testing framework
```

## Example: v4.2.0 Setup

```bash
# 1. Create task list
cat > v4.2.0-tasks.txt << 'EOF'
claude-refinement:Claude & Agents
marketing-content:Marketing Content
script-testing:Script Testing
template-creation:Templates
docx-verification:Docx Verification
calendly:Calendly
dashboard-redesign:Dashboard
database-viz:Database Viz
gemini-prompts:Gemini Prompts
librarian:Librarian
email-refinement:Email
github-streamline:GitHub
analytics:Analytics
EOF

# 2. Create all worktrees
./create-worktree-batch.sh v4.2.0-tasks.txt develop/v4.2.0

# 3. Open terminals
./open-terminals.sh

# 4. Check status
./worktree-status.sh
```

## Maintenance

### List All Sessions
```bash
tmux ls                    # List tmux sessions
screen -ls                 # List screen sessions
```

### Kill Session
```bash
tmux kill-session -t <session-name>
screen -S <session-name> -X quit
```

### Clean Up Worktrees
```bash
# Remove specific worktree
git worktree remove .trees/<name>

# Remove all (careful!)
git worktree list | grep task/ | awk '{print $1}' | xargs -I {} git worktree remove {}
```

## Tips

1. **Daily sync:** Run `./sync-all-worktrees.sh` at start of day
2. **Status check:** Use `./worktree-status.sh` to see what needs attention
3. **VS Code:** Use generated workspace for multi-folder editing
4. **Tmux:** Keep session running, detach/reattach as needed
5. **Conflicts:** Resolve in individual worktrees, then re-sync

## Troubleshooting

### Tmux not found
```bash
# Install tmux
sudo apt-get install tmux    # Ubuntu/Debian
brew install tmux            # macOS
```

### Workspace won't open in VS Code
- Ensure file path is correct
- Check JSON syntax in `.code-workspace` file
- Try: File → Open Workspace from File...

### Sync conflicts
- Navigate to conflicted worktree
- Resolve conflicts manually
- `git add .` and `git rebase --continue`
- Re-run `./sync-all-worktrees.sh`

### Worktree not appearing
- Check `git worktree list`
- Ensure path exists
- Verify branch wasn't deleted

---

**Created:** 2025-10-08
**Worktree:** `.trees/worktree-manager`
**Branch:** `task/00-worktree-manager`
