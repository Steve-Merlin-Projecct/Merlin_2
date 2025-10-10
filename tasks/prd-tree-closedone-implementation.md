# Product Requirements Document: /tree closedone Implementation

**Created:** 2025-10-09
**Status:** Draft
**Related PRD:** prd-tree-slash-command.md (Section 7: /tree closedone)

## Introduction/Overview

Implement the `/tree closedone` slash command to automate batch merging and cleanup of completed worktrees. This PRD focuses on the implementation details informed by real-world manual merge experience with the `script-testing` worktree.

The command will detect completed worktrees, merge them back to their base branch, resolve conflicts automatically using AI agents, clean up filesystem and git metadata, and provide comprehensive reporting.

## Goals

1. **Automate worktree completion workflow** - Eliminate manual merge and cleanup steps
2. **Intelligent conflict resolution** - Use AI agents to merge conflicts by combining both changes
3. **Safe and verifiable** - Provide dry-run mode, backups, and verification steps
4. **Comprehensive cleanup** - Remove worktree directories, branches, and close running terminals
5. **Detailed reporting** - Generate merge summaries, conflict resolution logs, and changelog entries
6. **Error resilience** - Handle git locks, dirty working directories, and partial failures gracefully

## User Stories

**As a developer**, I want to merge all completed worktrees with a single command so that I don't have to manually repeat the merge process for each worktree.

**As a developer**, I want conflicts to be automatically resolved by AI so that I don't have to manually merge conflicting changes when both versions should be preserved.

**As a developer**, I want to see a detailed summary of what was merged so that I can verify the changes and update project documentation.

**As a developer**, I want the system to handle git locks and dirty working directories gracefully so that I don't encounter cryptic error messages.

**As a project maintainer**, I want completed worktrees to be fully cleaned up so that the repository stays organized without abandoned branches or directories.

## Functional Requirements

### 1. Completion Detection

**1.1.** Detect completed worktrees by scanning `.trees/.completed/` for synopsis files
**1.2.** Extract worktree metadata from synopsis files:
- Worktree name
- Branch name
- Base branch
- Completion timestamp
**1.3.** Verify worktree still exists in `.trees/` directory
**1.4.** Verify branch still exists in git
**1.5.** Skip worktrees with no unique commits (e.g., `database-viz` scenario)

### 2. Pre-Merge Validation

**2.1.** Check if current working directory is clean
**2.2.** If dirty, prompt user to stash or commit changes
**2.3.** Automatically stash uncommitted changes with descriptive message
**2.4.** Handle git `index.lock` conflicts:
- Detect lock file existence
- Wait up to 5 seconds for lock to clear
- Prompt user if lock persists
**2.5.** Verify base branch exists and is accessible
**2.6.** Check for unique commits: `git log <base>..<worktree> --oneline`
**2.7.** Display summary of worktrees to be merged with commit counts

### 3. User Confirmation

**3.1.** Display interactive prompt: "Merge N completed worktrees? (y/n/review)"
**3.2.** On "review": Show detailed diff statistics for each worktree
**3.3.** On "n": Abort operation, exit cleanly
**3.4.** On "y": Proceed to merge phase
**3.5.** Support `--yes` flag to skip confirmation (automation mode)

### 4. Merge Execution

**4.1.** For each completed worktree:
- Switch to base branch
- Attempt merge with `git merge <worktree-branch> --no-edit`
- Capture merge outcome (fast-forward, merge commit, conflicts, error)

**4.2.** Fast-forward merge handling:
- Verify merge completed
- Log as successful
- Proceed to cleanup

**4.3.** Merge commit handling:
- Verify merge commit created
- Log as successful
- Proceed to cleanup

**4.4.** Conflict handling - transition to automated resolution (Section 5)

**4.5.** Error handling:
- Capture error message
- Roll back merge attempt
- Mark worktree as failed
- Continue with next worktree

### 5. Automated Conflict Resolution

**5.1.** Conflict Detection:
- Capture list of conflicted files from git status
- Create backup directory: `.trees/.conflict-backup/<worktree-name>/`
- Copy conflicted files to backup with version labels (base, incoming)

**5.2.** Agent Invocation:
- Launch general-purpose agent with conflict resolution task
- Provide agent with:
  - List of conflicted file paths
  - Backup file locations
  - Original feature descriptions from both worktrees
  - PURPOSE.md content from both worktrees
  - Explicit instruction: "Combine both changes, don't choose one"

**5.3.** Agent Task Specification:
```
Analyze and resolve merge conflicts by combining both sets of changes.

Conflicted Files:
- <file1>
- <file2>

Context:
- Base feature: <description>
- Incoming feature: <description>

For each file:
1. Read the file with conflict markers
2. Read backup versions from .trees/.conflict-backup/
3. Understand what each version accomplishes
4. Create merged version that includes BOTH changes
5. Write resolved file without conflict markers
6. Document resolution strategy used

Strategies to use:
- Combine Both Changes: Include both functionalities
- Merge Complementary Logic: Merge both modifications into enhanced version
- Preserve Both Variants: Keep both as separate functions
- Structural Merge: Combine imports/config/structure

After resolution:
- Run syntax checks
- Run test suite if available
- Stage resolved files with git add
- Report summary
```

**5.4.** Post-Resolution Verification:
- Verify all conflict markers removed
- Run syntax/linting checks on resolved files
- Run test suite if available
- If tests fail, mark for manual review
- Stage resolved files automatically

**5.5.** Fallback to Manual:
- If agent cannot resolve or verification fails
- Preserve backup files
- Display detailed conflict explanation
- Mark worktree for manual review
- Skip to next worktree

### 6. Cleanup Phase

**6.1.** Worktree Removal:
- Execute `git worktree remove <path>`
- Verify directory no longer exists
- Handle locked worktree errors

**6.2.** Branch Deletion:
- Execute `git branch -d <branch>` (safe delete)
- If fails due to unmerged commits, use `-D` with warning
- Verify branch deleted

**6.3.** Terminal Cleanup:
- Detect Claude processes by worktree path
- For tmux: Find and close tmux pane
- For VS Code: Send SIGTERM to Claude process
- For standalone: Send SIGTERM, log PID if fails
- Report terminals that couldn't be closed automatically

**6.4.** Archive Completion Files:
- Move `.trees/.completed/<name>-*` to `.trees/.archived/<name>/`
- Include conflict resolution logs if applicable
- Preserve for historical record

### 7. Reporting and Summary

**7.1.** Real-time Progress Display:
- Show progress for each worktree: `[1/3] worktree-name`
- Display step-by-step status with checkmarks
- Show conflict resolution progress if applicable
- Update summary statistics live

**7.2.** Per-Worktree Report:
- Merge type (fast-forward, merge commit, conflicts resolved)
- Files changed statistics
- Conflict resolution details if applicable
- Terminal cleanup status
- Final status: SUCCESS, CONFLICTS (manual), FAILED

**7.3.** Final Summary:
- Total worktrees processed
- Success count
- Auto-resolved conflicts count
- Failed count
- List of archived files
- Next steps if any manual resolution needed

**7.4.** Generate Changelog Entry:
- Extract key changes from commit messages
- Format for master changelog
- Save to `.trees/.archived/<name>/<name>-changelog-YYYYMMDD.md`
- Display summary for easy copy-paste

### 8. Advanced Options

**8.1.** `--dry-run`: Preview all actions without executing
**8.2.** `--resume`: Resume from last paused position after manual fix
**8.3.** `--skip <name>`: Skip specific worktree(s)
**8.4.** `--only <name>`: Process only specific worktree(s)
**8.5.** `--exclude <pattern>`: Exclude worktrees matching pattern
**8.6.** `--backup`: Create backup branches before merge
**8.7.** `--force-close`: Force-kill terminals instead of graceful shutdown
**8.8.** `--no-archive`: Delete completion files instead of archiving
**8.9.** `--yes`: Skip confirmation prompts (automation mode)

### 9. Error Handling and Edge Cases

**9.1.** Git Lock Handling:
- Detect `index.lock` file
- Retry after 1-second delay (max 5 attempts)
- If persists, prompt user with instructions
- Log lock detection for debugging

**9.2.** Dirty Working Directory:
- Detect uncommitted changes
- Prompt to stash automatically
- Preserve stash reference for later restoration
- Handle stash conflicts

**9.3.** No Unique Commits:
- Detect worktrees with no commits beyond base
- Skip with informational message: "No work to merge"
- Still perform cleanup (remove worktree/branch)

**9.4.** Missing Base Branch:
- Detect if base branch doesn't exist
- Prompt user to specify correct base
- Skip worktree if unresolvable

**9.5.** Partial Failure Recovery:
- Track which worktrees succeeded/failed
- Allow `--resume` to skip completed ones
- Preserve state file: `.trees/.closedone-state.json`

**9.6.** Agent Failure:
- If agent times out or errors
- Preserve conflict state
- Mark for manual resolution
- Continue with next worktree

**9.7.** Test Failure After Resolution:
- If tests fail post-agent-resolution
- Create detailed failure report
- Mark for manual review
- Don't stage resolved files

## Non-Goals (Out of Scope)

1. **Automatic push to remote** - User must manually push merged changes
2. **Multi-repository merges** - Only works within single repository
3. **Cherry-picking commits** - Only full branch merges supported
4. **Rewriting commit history** - Preserves original commit history
5. **Remote worktree cleanup** - Only cleans up local worktrees
6. **Conflict resolution teaching** - Agent uses predefined strategies, no learning

## Design Considerations

### Implementation Language

Implement as a bash script in `.claude/commands/tree.sh` with subcommand routing:
- Easier integration with git commands
- Native process management for terminal cleanup
- Direct file system operations
- Can invoke Claude CLI for agent tasks

### State Management

Use JSON state file during operation:
```json
{
  "operation_id": "closedone-20251009-143022",
  "started_at": "2025-10-09T14:30:22Z",
  "worktrees": [
    {
      "name": "script-testing",
      "status": "completed",
      "merge_type": "fast-forward",
      "conflicts_resolved": 0
    },
    {
      "name": "api-enhancements",
      "status": "in_progress",
      "conflicts_detected": 2,
      "agent_launched": true
    }
  ]
}
```

### Agent Integration

Use Claude CLI Task tool:
```bash
claude --append-system-prompt "$(cat <<EOF
Resolve merge conflicts in the following files by combining both changes...
EOF
)" <<< "Analyze conflicts and resolve"
```

Or invoke via temporary script that launches agent programmatically.

### Terminal Detection

**Tmux:**
```bash
tmux list-panes -a -F "#{pane_id} #{pane_pid} #{pane_current_path}" | \
  grep "$WORKTREE_PATH" | \
  awk '{print $1}' | \
  xargs -I {} tmux kill-pane -t {}
```

**VS Code/General:**
```bash
pgrep -f "claude.*$WORKTREE_PATH" | xargs kill -TERM
```

### Backup Strategy

Create timestamped backups before destructive operations:
```
.trees/.conflict-backup/<worktree-name>-<timestamp>/
  ├── base/
  │   ├── file1.py
  │   └── file2.py
  ├── incoming/
  │   ├── file1.py
  │   └── file2.py
  └── metadata.json
```

### Progress Display

Use Unicode box-drawing characters and ANSI colors:
```
🌳 /tree closedone - Batch Merge & Cleanup

Discovering completed worktrees... ✓
Found 3 worktrees

[1/3] script-testing
  ✓ Switched to develop/v4.2.0
  ✓ Merged (fast-forward)
  ✓ Removed worktree
  ✓ Deleted branch
  ✓ Archived files
  Status: ✅ SUCCESS
```

## Technical Considerations

### Git Operations Safety

- Always verify working directory is clean before operations
- Use `--no-edit` for automated merge commits
- Prefer safe delete (`-d`) over force delete (`-D`)
- Capture all git output for error analysis
- Support rollback via git reflog

### Conflict File Parsing

Parse git conflict markers to extract both versions:
```python
def extract_conflict_versions(content):
    conflicts = []
    current = None
    for line in content.split('\n'):
        if line.startswith('<<<<<<<'):
            current = {'base': [], 'incoming': []}
        elif line.startswith('======='):
            current['marker'] = 'incoming'
        elif line.startswith('>>>>>>>'):
            conflicts.append(current)
            current = None
        elif current:
            current[current.get('marker', 'base')].append(line)
    return conflicts
```

### Agent Prompt Template

```markdown
# Merge Conflict Resolution Task

## Context
Merging worktree: {worktree_name}
Base branch: {base_branch}
Worktree branch: {worktree_branch}

## Features Being Merged

### Base Feature
{base_feature_description}

### Incoming Feature
{incoming_feature_description}

## Conflicted Files

{for file in conflicted_files}
### {file.path}

**Conflict Preview:**
{file.conflict_snippet}

**Backup Locations:**
- Base version: .trees/.conflict-backup/{worktree}/base/{file.path}
- Incoming version: .trees/.conflict-backup/{worktree}/incoming/{file.path}
{endfor}

## Resolution Task

For each conflicted file:
1. Read the file with conflict markers
2. Read both backup versions to understand intent
3. Create a merged version that includes BOTH changes
4. The correct solution is usually to preserve both different elements
5. Write the resolved file without conflict markers
6. Document the strategy used

## Resolution Strategies

**Strategy 1: Combine Both Changes (Default)**
- Example: Two different API endpoints → Keep both
- Example: Different middleware added → Chain both in pipeline

**Strategy 2: Merge Complementary Logic**
- Example: One added validation, other added logging → Include both in function
- Example: Different error handling approaches → Combine into comprehensive handler

**Strategy 3: Preserve Both Variants**
- Example: Two different algorithms → Keep both with descriptive names
- Example: Different configuration options → Preserve both settings

**Strategy 4: Structural Merge**
- Example: Different imports → Include all imports
- Example: Different dependencies → Add both to requirements

## Deliverables

After resolving all conflicts:
1. Write resolved files
2. Run syntax check: `python -m py_compile <file>` (for Python files)
3. Stage resolved files: `git add <files>`
4. Report resolution summary with strategy used per file
```

### Performance Considerations

- Batch git operations where possible
- Run agent resolution in parallel if multiple worktrees have conflicts
- Cache git log/diff results to avoid repeated queries
- Stream output for long-running operations
- Timeout agent tasks after 10 minutes

## Success Metrics

1. **Automation Rate**: >95% of merges complete without manual intervention
2. **Conflict Resolution Accuracy**: >90% of agent resolutions pass tests
3. **Time Savings**: 80% reduction in time vs manual merge process
4. **User Satisfaction**: Positive feedback on ease of use
5. **Error Rate**: <5% of operations require manual recovery

## Open Questions

1. **Should we support partial conflict resolution?** - If agent resolves 2 of 3 conflicts, proceed or fail?
2. **How to handle merge conflicts in binary files?** - Always fail or provide special handling?
3. **Should we create merge commit messages automatically?** - Or use git default merge messages?
4. **How long to retain conflict backups?** - Delete after successful merge or keep in archive?
5. **Should we support interactive conflict resolution?** - Present agent suggestions and ask user to approve?

## Implementation Phases

### Phase 1: Core Functionality (MVP)
- Completion detection
- Pre-merge validation
- Merge execution (fast-forward and merge commits)
- Basic cleanup (worktree and branch removal)
- Summary reporting

### Phase 2: Conflict Resolution
- Conflict detection and backup
- Agent integration
- Post-resolution verification
- Conflict resolution reporting

### Phase 3: Advanced Features
- All command-line options
- State management and resume
- Terminal cleanup
- Archive management

### Phase 4: Polish and Error Handling
- Comprehensive error handling
- Edge case coverage
- Performance optimization
- User experience refinement

## Testing Strategy

### Unit Tests
- Completion detection logic
- Conflict file parsing
- Backup creation
- State management

### Integration Tests
- End-to-end merge workflow
- Agent resolution simulation
- Cleanup verification
- Error recovery

### Manual Testing Scenarios
1. Clean fast-forward merge (like script-testing)
2. Merge with conflicts requiring agent
3. Merge with dirty working directory
4. Merge with git lock present
5. Merge with no unique commits
6. Multiple worktrees with mixed outcomes
7. Resume after manual conflict fix
8. Dry-run mode verification

## Documentation Requirements

1. **Command Reference** - Full documentation of all options
2. **Usage Examples** - Common scenarios with example commands
3. **Troubleshooting Guide** - Common errors and solutions
4. **Agent Resolution Guide** - How the AI resolves conflicts
5. **Architecture Document** - Implementation details for maintainers

## Security Considerations

1. **No automatic push** - Prevents accidental publication of merged code
2. **Backup preservation** - Can roll back if merge was incorrect
3. **Verification steps** - Tests must pass before considering resolution successful
4. **User confirmation** - Requires explicit approval before destructive operations
5. **Audit trail** - All operations logged with timestamps

## Migration Path

For existing worktrees not created with `/tree` system:
1. Manually create `.trees/.completed/<name>-synopsis-*.md` file
2. Use template format with required metadata
3. Run `/tree closedone` normally
4. System validates and proceeds with merge

Example manual synopsis:
```markdown
# Worktree: script-testing
# Branch: task/03-script-testing
# Base: develop/v4.2.0
# Created: 2025-10-09
# Completed: 2025-10-09

## Work Summary
Comprehensive system testing implementation...
```
