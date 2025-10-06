# Git Commands - Copy/Paste Reference

**Quick command reference for safe git operations**

## Branch Management Commands

### Check Status
```bash
# View current branch and status
./.github/scripts/branch_management.sh status
```

### Create Checkpoints (Recommended before major changes)
```bash
# Create named checkpoint
./.github/scripts/branch_management.sh checkpoint "before-major-changes"

# Create automatic checkpoint
./.github/scripts/branch_management.sh checkpoint
```

### Switch Branches
```bash
# Switch to main branch
./.github/scripts/branch_management.sh switch main

# Switch to development branch
./.github/scripts/branch_management.sh switch noxml

# Switch to any existing branch
./.github/scripts/branch_management.sh switch <branch-name>
```

### Create Feature Branches
```bash
# Create new feature branch from main
./.github/scripts/branch_management.sh create feature/my-new-feature main

# Create new feature branch from current branch
./.github/scripts/branch_management.sh create feature/my-new-feature
```

### Rollback Operations
```bash
# List available checkpoints
./.github/scripts/branch_management.sh list

# Rollback to specific checkpoint
./.github/scripts/branch_management.sh rollback checkpoint-name

# Rollback to previous commit
./.github/scripts/branch_management.sh rollback HEAD~1
```

### Branch Merge Checking
```bash
# Check which remote branches are merged into main
./.github/scripts/branch_management.sh check-merged main

# Check which remote branches are merged into current branch
./.github/scripts/branch_management.sh check-merged

# Check noxml branch merge status specifically
./.github/scripts/branch_management.sh check-merged main
```

### Merge Operations
```bash
# Merge feature branch (with safety checkpoint)
./.github/scripts/branch_management.sh merge feature/my-feature

# Delete feature branch after merge
./.github/scripts/branch_management.sh delete feature/my-feature
```

## Safe Git Commands

### Basic Operations
```bash
# Safe git add
./.github/scripts/git_safe_commands.sh add -A
./.github/scripts/git_safe_commands.sh add file.py

# Safe git commit
./.github/scripts/git_safe_commands.sh commit -m "Your commit message"

# Safe git status
./.github/scripts/git_safe_commands.sh status

# Safe git push
./.github/scripts/git_safe_commands.sh push origin main

# Safe git pull
./.github/scripts/git_safe_commands.sh pull origin main
```

### Automated Commits
```bash
# Auto commit with timestamp
./.github/scripts/auto_commit.sh

# Auto commit with custom message
./.github/scripts/auto_commit.sh -m "Fix git lock prevention system"

# Auto commit (alternative syntax)
./.github/scripts/auto_commit.sh "Your commit message here"
```

## Lock Prevention Commands

### Full Lock Prevention Setup
```bash
# Complete setup (recommended first-time setup)
./.github/scripts/git_lock_prevention.sh --full

# Clean existing locks only
./.github/scripts/git_lock_prevention.sh --clean-only

# Configure git settings only
./.github/scripts/git_lock_prevention.sh --config-only
```

### Safe Git Operations
```bash
# Execute any git command safely
./.github/scripts/git_lock_prevention.sh --safe add -A
./.github/scripts/git_lock_prevention.sh --safe commit -m "message"
./.github/scripts/git_lock_prevention.sh --safe push origin main
```

### Lock Monitoring
```bash
# Start continuous lock monitoring
./.github/scripts/git_lock_prevention.sh --monitor
```

## Conflict Prevention Commands

🛠️ Manual Steps Required:
Since Replit blocks automated Git operations, you need to manually:

Stop Git processes: pkill -f git
```bash
rm -f .git/index.lock .git/config.lock
rm -f .git/refs/remotes/origin/HEAD.lock
rm -f .git/objects/maintenance.lock

```
### GitHub Priority Setup
```bash
# Full conflict prevention setup
./.github/scripts/git_conflict_prevention.sh

# Sync with GitHub only
./.github/scripts/git_conflict_prevention.sh --sync-only

# Setup configuration only
./.github/scripts/git_conflict_prevention.sh --setup-only
```

## Emergency Recovery Commands

### When Git is Stuck
```bash
# Clean environment and try again
./.github/scripts/git_wrapper.sh clean

# Use Replit's git interface (sidebar) as fallback

# Or wait 30-60 seconds for automatic cleanup
sleep 60
```

### Merge Conflict Resolution
```bash
# When merge conflicts occur, resolve manually:
# 1. Edit conflicted files (look for <<<<<<< ======= >>>>>>> markers)
# 2. Add resolved files
git add <resolved-file>

# 3. Complete the merge
git commit

# 4. Or abort the merge
git merge --abort

# 5. Use branch management rollback if needed
./.github/scripts/branch_management.sh rollback pre-merge-checkpoint
```

### If Branch Management Fails
```bash
# Use basic safe commands
./.github/scripts/git_safe_commands.sh status
./.github/scripts/auto_commit.sh -m "emergency commit"
```

## SSH Setup Commands

### Setup GitHub Authentication
```bash
# Setup SSH keys for GitHub
chmod +x setup_ssh.sh
./setup_ssh.sh
```

### Test SSH Connection
```bash
# Test GitHub connection
ssh -T git@github.com
```

## Quick Workflow Examples

### Daily Development Workflow
```bash
# 1. Check current status
./.github/scripts/branch_management.sh status

# 2. Create checkpoint before starting work
./.github/scripts/branch_management.sh checkpoint "before-daily-work"

# 3. Do your development work...

# 4. Commit your changes
./.github/scripts/auto_commit.sh -m "Implement new feature"

# 5. Push to GitHub (if needed)
./.github/scripts/git_safe_commands.sh push origin main
```

### Feature Development Workflow
```bash
# 1. Create feature branch
./.github/scripts/branch_management.sh create feature/new-functionality main

# 2. Develop on feature branch...

# 3. Checkpoint your work
./.github/scripts/branch_management.sh checkpoint "feature-complete"

# 4. Switch back to main
./.github/scripts/branch_management.sh switch main

# 5. Merge feature (when ready)
./.github/scripts/branch_management.sh merge feature/new-functionality
```

### Emergency Recovery Workflow
```bash
# 1. If something goes wrong, check available rollback points
./.github/scripts/branch_management.sh list

# 2. Rollback to last known good state
./.github/scripts/branch_management.sh rollback checkpoint-name

# 3. Or switch to stable branch
./.github/scripts/branch_management.sh switch main
```

## Command Arguments Reference

### Branch Management Options
- `status` - Show current branch and changes
- `checkpoint [name]` - Create rollback point
- `switch <branch>` - Change branches safely
- `create <branch> [base]` - Create new branch
- `rollback <point>` - Rollback to checkpoint/commit
- `merge <branch>` - Merge branch with safety
- `delete <branch>` - Delete branch safely
- `list` - List checkpoints and recent commits
- `check-merged [branch]` - Check which remote branches are merged into main (or specified branch)

### Git Safe Commands Options
- `add <files>` - Stage files
- `commit <options>` - Commit changes  
- `status <options>` - Check status
- `push <options>` - Push to remote
- `pull <options>` - Pull from remote

### Lock Prevention Options
- `--full` - Complete setup
- `--clean-only` - Remove locks only
- `--config-only` - Configure settings only
- `--safe <command>` - Execute git command safely
- `--monitor` - Start continuous monitoring