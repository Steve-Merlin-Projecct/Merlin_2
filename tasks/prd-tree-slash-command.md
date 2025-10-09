# PRD: /tree Slash Command for Worktree Management

## Introduction/Overview

A unified slash command interface (`/tree`) that streamlines the entire worktree workflow from planning to execution. This command provides an interactive, conversational way to stage feature descriptions, analyze conflicts, and build complete worktree environments with Claude instances ready to go.

**Current Workflow Pain Points:**
1. Manual creation of task list files
2. Separate conflict analysis step
3. Multiple commands to run (create, open, start Claude)
4. No staging mechanism for planning multiple features
5. Git operations scattered across workflow

**Proposed Solution:**
A single `/tree` command with intuitive subcommands that guide the user through the entire workflow conversationally.

## Goals

1. **Primary Goal**: Reduce worktree setup from 5+ manual steps to 2 slash commands
2. **Secondary Goal**: Provide interactive staging mechanism for planning multiple features
3. **Tertiary Goal**: Automate git operations and conflict detection in the workflow

## User Stories

1. **As a developer**, I want to stage multiple feature ideas conversationally, so that I can plan my parallel development session interactively.

2. **As a developer**, I want automatic conflict detection during planning, so that I know about potential issues before creating worktrees.

3. **As a developer**, I want a single command to create all worktrees and start Claude, so that I can begin coding immediately.

4. **As a developer**, I want git operations automated (stage, commit, branch), so that I don't have to remember manual steps.

5. **As a developer**, I want to review staged features before building, so that I can make adjustments to the plan.

## Functional Requirements

### 1. /tree stage [description]

**Purpose:** Interactively stage feature descriptions for upcoming worktree build.

**Behavior:**
1.1. Accept natural language feature description
1.2. Parse description to extract:
   - Feature name (slugified for worktree/branch naming)
   - Brief objective
   - Primary scope

1.3. Append to staging file (`/workspace/.trees/.staged-features.txt`)

1.4. Provide feedback:
   - Feature number assigned
   - Extracted worktree name
   - Confirmation message

1.5. Prompt for next action:
   - Stage another feature
   - Review staged features
   - Build staged features

**Example Interaction:**
```
User: /tree stage Add real-time collaboration features with WebSocket support

Claude: ✓ Feature 1 staged: real-time-collaboration
        Objective: Add real-time collaboration features with WebSocket support

        Options:
        - Stage another feature with: /tree stage [description]
        - Review all staged with: /tree list
        - Build worktrees with: /tree build
```

**File Format (`.staged-features.txt`):**
```
# Staged Features for Worktree Build
# Created: 2025-10-09

real-time-collaboration:Add real-time collaboration features with WebSocket support
api-rate-limiting:Implement rate limiting for API endpoints
user-dashboard-redesign:Redesign user dashboard with modern UI components
```

### 2. /tree list

**Purpose:** Display all currently staged features.

**Behavior:**
2.1. Read `.staged-features.txt`
2.2. Display formatted list with:
   - Feature number
   - Worktree name
   - Description
   - Estimated conflicts (if analysis done)

2.3. Show total count

2.4. Provide options:
   - Add more features
   - Remove a feature
   - Edit a feature
   - Build all features

**Example Output:**
```
📋 Staged Features (3)

1. real-time-collaboration
   Add real-time collaboration features with WebSocket support

2. api-rate-limiting
   Implement rate limiting for API endpoints
   ⚠️  May conflict with: Feature 1 (shared middleware)

3. user-dashboard-redesign
   Redesign user dashboard with modern UI components

Actions:
- /tree stage [description] - Add another
- /tree remove [number] - Remove feature
- /tree build - Create all worktrees
```

### 3. /tree remove [number]

**Purpose:** Remove a staged feature by number.

**Behavior:**
3.1. Validate feature number exists
3.2. Remove from staging file
3.3. Renumber remaining features
3.4. Confirm removal
3.5. Show updated list

### 4. /tree clear

**Purpose:** Clear all staged features (start fresh).

**Behavior:**
4.1. Prompt for confirmation
4.2. Delete `.staged-features.txt`
4.3. Confirm cleared

### 5. /tree conflict

**Purpose:** Analyze staged features for conflicts and suggest merging similar features.

**Workflow Steps:**

**5.1. Conflict Detection**
- Analyze all staged features for potential conflicts
- Use semantic analysis of feature descriptions
- Check for keyword overlap (API, database, frontend, etc.)
- Identify shared files/modules from description
- Categorize conflicts: HIGH, MEDIUM, LOW

**5.2. Similarity Analysis**
- Detect features that could be combined
- Look for related scopes (e.g., "API endpoints" + "API rate limiting")
- Suggest merges with explanation

**5.3. Interactive Merging**
- Present merge suggestions
- Allow user to accept/reject each merge
- If accepted, combine descriptions intelligently
- Update staging file with merged features
- Renumber remaining features

**Example Conflict Report:**
```
🔍 Analyzing 5 Staged Features...

MERGE SUGGESTIONS:
┌─────────────────────────────────────────────────────────────┐
│ Features 2 & 4 appear related - consider merging?           │
│                                                              │
│ Feature 2: Implement API rate limiting                      │
│ Feature 4: Add API request throttling                       │
│                                                              │
│ Suggested merge: "Implement API rate limiting and request   │
│                   throttling with token bucket algorithm"   │
│                                                              │
│ Merge these features? (y/n/edit)                           │
└─────────────────────────────────────────────────────────────┘

CONFLICT ANALYSIS:
HIGH RISK:
- Features 1 & 3 both modify: modules/api/middleware.py
  └─ Feature 1: Add authentication middleware
  └─ Feature 3: Add logging middleware
  ⚠️  Recommendation: Coordinate middleware order in shared file

MEDIUM RISK:
- Features 1 & 5 both add routes to: app.py
  └─ Feature 1: User authentication endpoints
  └─ Feature 5: Admin dashboard endpoints
  ℹ️  Note: Should be safe if following REST conventions

LOW RISK:
- All features modify: documentation files
- Features 2 & 5 both update: README.md

FEATURE RELATIONSHIPS:
Feature 1 (auth) ──► Feature 5 (admin) [dependency]
  └─ Feature 5 needs auth from Feature 1

Summary:
- 1 merge suggestion
- 1 HIGH risk conflict
- 1 MEDIUM risk conflict
- 1 dependency relationship

Actions:
- Accept merge suggestions to reduce conflicts
- Note HIGH conflicts in PURPOSE.md for each worktree
- Consider building Feature 1 before Feature 5
```

**5.4. Context Preservation**
- When features are merged, preserve BOTH original descriptions
- Include in PURPOSE.md:
  - Original Feature A description
  - Original Feature B description
  - Combined objective
  - Rationale for merge

**Example Merged PURPOSE.md:**
```markdown
# Purpose: API Rate Limiting and Request Throttling

**Worktree:** api-rate-limiting
**Branch:** task/02-api-rate-limiting
**Created:** 2025-10-09

## Combined Objective
Implement comprehensive API rate limiting and request throttling
with token bucket algorithm to prevent abuse and ensure fair usage.

## Original Features (Merged)

### Feature 2: Implement API rate limiting
Prevent API abuse by limiting requests per user/IP address.
Focus on user-based rate limits with Redis backend.

### Feature 4: Add API request throttling
Add throttling mechanism to smooth out traffic spikes.
Focus on token bucket algorithm for burst handling.

### Merge Rationale
Both features address API traffic control and share the same
middleware layer. Implementing together ensures consistent
rate limiting strategy and avoids duplicate middleware.

## Scope
...
```

### 6. /tree build

**Purpose:** Execute complete worktree creation workflow with all staged features.

**Workflow Steps:**

**6.1. Pre-Build Validation**
- Check that features are staged
- Verify not already on a feature branch
- Confirm current branch is clean (or offer to stash)
- Recommend running `/tree conflict` if not done yet

**6.2. Conflict Reference**
- If `/tree conflict` was run, reference previous analysis
- If not run, offer to run it now
- Display conflict summary
- Prompt for confirmation to proceed

**5.3. Git Operations**
- Stage all current changes: `git add -A`
- Commit with message: "chore: Stage changes before worktree build"
- Create development branch: `git checkout -b develop/v[version]-[timestamp]`
- Push development branch to remote

**5.4. Worktree Creation**
- Generate tasks file from staged features
- Execute `create-worktree-batch.sh`
- Generate VS Code terminal profiles
- Create launch script

**5.5. Terminal Setup**
- Execute `open-terminals.sh` to create tmux session
- Or generate VS Code workspace file
- Provide instructions for both methods

**5.6. Claude Launch (Optional)**
- Prompt: "Start Claude in all worktrees now? (y/n)"
- If yes: Execute `launch-all-claude.sh`
- If no: Provide command to run later

**5.7. Cleanup & Summary**
- Archive `.staged-features.txt` to `.trees/.build-history/YYYYMMDD-HHMMSS.txt`
- Display summary:
  - Development branch created
  - Number of worktrees created
  - Conflict warnings
  - Next steps

**Example Build Output:**
```
🚀 Building Worktrees from 3 Staged Features

✓ Pre-build validation passed
✓ Staged current changes
✓ Created branch: develop/v4.2.0-20251009
✓ Pushed to remote

Creating worktrees...
  [1/3] ✓ real-time-collaboration
  [2/3] ✓ api-rate-limiting
  [3/3] ✓ user-dashboard-redesign

✓ Generated VS Code terminal profiles
✓ Created tmux session: worktrees-12345

📊 Build Summary:
- Branch: develop/v4.2.0-20251009
- Worktrees: 3 created in .trees/
- Conflicts: 2 HIGH, 1 MEDIUM, 1 LOW (see notes in each PURPOSE.md)

🎯 Next Steps:
1. Switch to tmux session: tmux attach -t worktrees-12345
2. Or use VS Code terminal profiles
3. Start Claude in worktrees: /workspace/.trees/launch-all-claude.sh
4. Each worktree has conflict warnings in PURPOSE.md

Happy coding! 🌳
```

### 6. /tree close

**Purpose:** Complete work in current worktree, generate synopsis, and prepare for terminal closure.

**Prerequisites:**
- Must be run from within a worktree (not main workspace)
- Detects current worktree automatically

**Workflow Steps:**

**6.1. Work Analysis**
- Analyze all changes made in the worktree
- Read git diff and git log for this branch
- Identify files created, modified, deleted
- Extract key functionality added
- Detect any TODO comments or incomplete work

**6.2. Generate Long-Form Synopsis**
- Create comprehensive summary of work completed
- Include:
  - Purpose statement (from PURPOSE.md)
  - Files changed with descriptions
  - Key features implemented
  - Technical decisions made
  - Known issues or limitations
  - Testing status
  - Dependencies added/modified

**Example Long-Form Synopsis:**
```markdown
# Work Completed: API Rate Limiting and Request Throttling

## Purpose
Implemented comprehensive API rate limiting and request throttling
with token bucket algorithm to prevent abuse and ensure fair usage.

## Files Changed

### Created Files
1. `modules/middleware/rate_limiter.py` (234 lines)
   - Token bucket rate limiting implementation
   - Redis-backed counter storage
   - Configurable rate limits per endpoint
   - Support for user-based and IP-based limiting

2. `modules/middleware/throttle.py` (156 lines)
   - Request throttling middleware
   - Burst handling with token bucket
   - Integration with rate_limiter

3. `tests/test_rate_limiter.py` (189 lines)
   - Unit tests for rate limiting
   - Integration tests with Redis
   - Performance benchmarks

### Modified Files
1. `app_modular.py` (+12 lines)
   - Registered rate limiting middleware
   - Added configuration for rate limits

2. `requirements.txt` (+2 lines)
   - Added redis dependency (v4.5.0)
   - Added python-redis-lock (v4.0.0)

3. `docs/api/README.md` (+45 lines)
   - Documented rate limiting behavior
   - Added examples of rate limit headers

## Key Features Implemented

✓ Token bucket rate limiting algorithm
✓ Per-user rate limits (100 req/min default)
✓ Per-IP rate limits (1000 req/min default)
✓ Burst handling (up to 2x limit for 10 seconds)
✓ Redis-backed distributed rate limiting
✓ Configurable rate limits per endpoint
✓ Rate limit headers in responses (X-RateLimit-*)
✓ Graceful degradation if Redis unavailable

## Technical Decisions

1. **Redis for State Storage**
   Chose Redis over in-memory storage for distributed rate
   limiting across multiple application instances.

2. **Token Bucket Algorithm**
   Selected over leaky bucket for better burst handling
   and simpler implementation.

3. **Middleware Approach**
   Implemented as Flask middleware for easy integration
   and minimal code changes to existing endpoints.

## Known Issues / Limitations

- Rate limits are per-instance if Redis unavailable (fallback)
- No admin UI for adjusting limits (configured via env vars)
- TODO: Add rate limit bypass for admin users (see line 45)

## Testing Status

✓ Unit tests passing (23/23)
✓ Integration tests passing (8/8)
⚠️  Load testing pending (requires staging environment)
⚠️  Redis failover testing incomplete

## Dependencies Added

- redis==4.5.0
- python-redis-lock==4.0.0

## Related Worktrees

- Feature 3 (logging middleware) may conflict on middleware
  registration order - coordinate before merging
```

**6.3. Generate Changelog Summary**
- Create concise changelog entry
- Follow project changelog format
- Include version, date, type of change

**Example Changelog Summary:**
```markdown
### Added
- API rate limiting with token bucket algorithm (100 req/min per user)
- Request throttling middleware with burst handling
- Redis-backed distributed rate limiting
- Rate limit headers in API responses (X-RateLimit-Limit, X-RateLimit-Remaining, X-RateLimit-Reset)
- Configurable rate limits per endpoint via environment variables

### Changed
- Updated API documentation with rate limiting behavior
- Modified middleware registration order in app_modular.py

### Dependencies
- Added redis==4.5.0
- Added python-redis-lock==4.0.0

### Testing
- Added 23 unit tests for rate limiting
- Added 8 integration tests with Redis backend
```

**6.4. Save Documentation**
- Save long-form synopsis to: `.trees/.completed/<worktree-name>-synopsis-YYYYMMDD.md`
- Save changelog summary to: `.trees/.completed/<worktree-name>-changelog-YYYYMMDD.md`
- Update worktree's PURPOSE.md with completion timestamp

**6.5. Git Operations**
- Stage all changes: `git add -A`
- Commit with comprehensive message
- Push to remote branch

**Example Commit Message:**
```
feat: Implement API rate limiting and request throttling

Adds comprehensive rate limiting with token bucket algorithm
and request throttling to prevent API abuse and ensure fair usage.

Features:
- Per-user rate limits (100 req/min)
- Per-IP rate limits (1000 req/min)
- Redis-backed distributed limiting
- Burst handling (2x limit for 10s)
- Rate limit headers in responses
- Graceful Redis failover

Files changed:
- Created: modules/middleware/rate_limiter.py (234 lines)
- Created: modules/middleware/throttle.py (156 lines)
- Created: tests/test_rate_limiter.py (189 lines)
- Modified: app_modular.py, requirements.txt, docs/api/README.md

Testing: 31/31 tests passing
Load testing: Pending staging environment

Related worktrees: logging-middleware (coordinate merge order)

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

**6.6. Display Summary and Exit Instructions**

**Example Output:**
```
✓ Work analysis complete
✓ Synopsis generated: .trees/.completed/api-rate-limiting-synopsis-20251009.md
✓ Changelog generated: .trees/.completed/api-rate-limiting-changelog-20251009.md
✓ All changes staged and committed
✓ Pushed to: origin/task/02-api-rate-limiting

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 Work Summary: API Rate Limiting and Request Throttling
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Files Changed:
  • Created: 3 files (579 total lines)
  • Modified: 3 files (+59 lines)
  • Dependencies: 2 added

Key Features:
  ✓ Token bucket rate limiting (100 req/min per user)
  ✓ Request throttling with burst handling
  ✓ Redis-backed distributed limiting
  ✓ Rate limit headers in responses

Testing:
  ✓ 31/31 tests passing
  ⚠️  Load testing pending

Known Issues:
  • TODO: Admin bypass functionality (line 45)
  • Load testing requires staging environment

Conflicts to Watch:
  ⚠️  Feature 3 (logging) may conflict on middleware order

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📝 Documentation Saved:
  • Long-form synopsis: .trees/.completed/api-rate-limiting-synopsis-20251009.md
  • Changelog entry: .trees/.completed/api-rate-limiting-changelog-20251009.md

🎯 Next Steps:
  1. Review synopsis and changelog before merging
  2. Copy changelog entry to docs/changelogs/master-changelog.md
  3. Coordinate with Feature 3 team on middleware merge order
  4. Schedule load testing on staging environment

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ This terminal is safe to close.

To merge this work:
  1. Switch to develop branch: git checkout develop/v4.2.0-20251009
  2. Merge: git merge task/02-api-rate-limiting
  3. Resolve any conflicts
  4. Push: git push origin develop/v4.2.0-20251009
```

**6.7. Optional: Auto-Exit**
- If run with `--exit` flag: automatically exit terminal after displaying summary
- Otherwise: wait for user to close terminal manually

### 7. /tree closedone

**Purpose:** Batch merge and cleanup of all completed worktrees that have received `/tree close`.

**Prerequisites:**
- One or more worktrees must have been closed with `/tree close`
- Completed worktrees are identified by presence of `.trees/.completed/<name>-synopsis-*.md` files

**Behavior:**

**7.1. Discovery Phase**
- Scan `.trees/.completed/` directory for synopsis files
- Extract worktree names and branches from synopsis metadata
- Verify worktree still exists in `.trees/` directory
- Display list of completed worktrees found

**7.2. User Confirmation**
- Show summary of worktrees to be merged
- Display target branch for each merge
- Prompt: "Merge N completed worktrees? (y/n/review)"
- If "review": show detailed file changes for each worktree
- If "n": abort operation
- If "y": proceed to merge phase

**7.3. Merge Phase (for each completed worktree)**
- Switch to base/develop branch
- Attempt merge: `git merge <worktree-branch>`
- Handle merge outcomes:
  - **Clean merge**: Continue to cleanup
  - **Conflicts detected**: Pause and display conflict resolution instructions
  - **Merge error**: Skip worktree, log error, continue with next

**7.4. Cleanup Phase (only if merge succeeded)**
- Remove worktree files: `git worktree remove .trees/<worktree-name>`
- Close Claude terminal if still running:
  - Find process by worktree path
  - Send graceful shutdown (SIGTERM)
  - If tmux: close tmux window/pane
  - If VS Code: send terminal close command
- Archive completion files:
  - Move `.trees/.completed/<name>-*` to `.trees/.archived/<name>/`
  - Preserve synopsis and changelog for historical record

**7.5. Summary Report**
- Display results for each worktree:
  - ✅ Successfully merged and cleaned up
  - ⚠️  Merged with conflicts (manual resolution needed)
  - ❌ Failed to merge (error details)
- Show overall statistics
- List any terminals that couldn't be closed automatically

**Example Output:**

```
🌳 /tree closedone - Batch Merge & Cleanup

Discovering completed worktrees...
Found 3 completed worktrees:
  1. real-time-collaboration (task/01-real-time-collaboration → develop/v4.2.0-20251009)
  2. api-rate-limiting (task/02-api-rate-limiting → develop/v4.2.0-20251009)
  3. user-dashboard-redesign (task/03-user-dashboard-redesign → develop/v4.2.0-20251009)

Merge these 3 worktrees? (y/n/review): y

Processing worktrees...

[1/3] real-time-collaboration
  ✓ Switched to develop/v4.2.0-20251009
  ✓ Merged task/01-real-time-collaboration (fast-forward)
  ✓ Removed worktree files
  ✓ Closed Claude terminal (PID 12345)
  ✓ Archived completion files
  Status: ✅ SUCCESS

[2/3] api-rate-limiting
  ✓ Switched to develop/v4.2.0-20251009
  ⚠  Conflicts detected in 2 files
  🔧 Launching conflict resolution agent...

  Agent resolving conflicts:
    ✓ modules/api/middleware.py (Combined both middleware functions)
    ✓ tests/test_rate_limiting.py (Merged both test suites)
  ✓ All conflicts resolved automatically
  ✓ Tests passed
  ✓ Changes staged
  ✓ Removed worktree files
  ✓ Closed Claude terminal (PID 12346)
  ✓ Archived completion files
  Status: ✅ SUCCESS (auto-resolved conflicts)

[3/3] user-dashboard-redesign
  ✓ Switched to develop/v4.2.0-20251009
  ✓ Merged task/03-user-dashboard-redesign (merge commit)
  ✓ Removed worktree files
  ⚠  Claude terminal not found (already closed)
  ✓ Archived completion files
  Status: ✅ SUCCESS

═══════════════════════════════════════════════════════════
SUMMARY

Worktrees Processed: 3
  ✅ Success: 3
  🔧 Auto-resolved conflicts: 1
  ❌ Failed: 0

Conflict Resolution Details:
  - api-rate-limiting: 2 files auto-resolved by agent
    Strategy: Combined both changes to preserve all functionality

Archived Files:
  - .trees/.archived/real-time-collaboration/
  - .trees/.archived/api-rate-limiting/
  - .trees/.archived/user-dashboard-redesign/

All worktrees merged successfully! 🎉
═══════════════════════════════════════════════════════════
```

**7.6. Automated Conflict Resolution Workflow**

When conflicts are detected, use the general-purpose agent to automatically analyze and resolve:

**7.6.1. Conflict Detection**
- Merge attempt fails with conflict markers
- Capture list of conflicted files
- Create backup copies in `.trees/.conflict-backup/<worktree-name>/`

**7.6.2. Agent-Based Resolution**
- Launch general-purpose agent with conflict analysis task
- Agent receives:
  - Conflicted file paths
  - Backup copies of both versions (base, incoming)
  - Original feature descriptions from both worktrees
  - Context from PURPOSE.md files

**Agent Task:**
```
Analyze and resolve merge conflicts in the following files from merging worktrees:

Conflicted Files:
{list of files with conflicts}

Context:
- Base worktree: {name} - {original purpose description}
- Incoming worktree: {name} - {original purpose description}

For each conflicted file:
1. Read the file with conflict markers
2. Read backup copies: .trees/.conflict-backup/{worktree}/base/{file} and .trees/.conflict-backup/{worktree}/incoming/{file}
3. Understand what each version is trying to accomplish
4. Create a merged version that includes BOTH sets of changes appropriately
5. The correct solution is usually to include both different elements, not choose one over the other
6. Write the resolved file without conflict markers
7. Explain the resolution strategy used

After resolving all conflicts:
- Stage resolved files with git add
- Report resolution summary
```

**7.6.3. Resolution Strategies**

The agent should prioritize these strategies:

**Strategy 1: Combine Both Changes (Default)**
- Both worktrees made different changes to the same area
- Solution: Include both changes in a way that preserves both functionalities
- Example: Two different API endpoints added → Keep both endpoints

**Strategy 2: Merge Complementary Logic**
- Both worktrees modified the same function differently
- Solution: Merge both modifications into a single enhanced function
- Example: One added validation, another added error handling → Include both

**Strategy 3: Preserve Both Variants**
- Changes represent different approaches to similar problems
- Solution: Keep both as separate functions/methods
- Example: Two different rate limiting algorithms → Keep both with different names

**Strategy 4: Structural Merge**
- Changes to imports, configuration, or structure
- Solution: Combine both sets of imports/config entries
- Example: Two different imports added → Include both import statements

**7.6.4. Post-Resolution Verification**
- Agent runs syntax checks on resolved files
- Agent runs test suite if available
- Agent reports:
  - Number of conflicts resolved
  - Strategy used for each file
  - Any issues that require human review
  - Test results

**7.6.5. Fallback to Manual Resolution**

If agent cannot resolve (rare cases):
- Mark conflict as requiring human intervention
- Preserve backup files
- Provide detailed explanation of the issue
- Support `--resume` flag to continue after manual fix
- Support `--skip <worktree-name>` to skip specific worktree

**Example Agent Resolution Output:**
```
🔧 Resolving conflicts with AI agent...

[1/3] modules/api/middleware.py
  Strategy: Combine Both Changes
  - Base added: rate limiting middleware
  - Incoming added: authentication middleware
  ✓ Resolution: Merged both middleware functions into pipeline
  ✓ Syntax check passed

[2/3] tests/test_middleware.py
  Strategy: Merge Complementary Logic
  - Base added: rate limit tests
  - Incoming added: auth tests
  ✓ Resolution: Combined both test suites
  ✓ Syntax check passed

[3/3] config/settings.py
  Strategy: Structural Merge
  - Base added: RATE_LIMIT_WINDOW config
  - Incoming added: AUTH_TIMEOUT config
  ✓ Resolution: Included both configuration entries
  ✓ Syntax check passed

Running test suite...
✓ All tests passed (42 tests, 0 failures)

Conflict Resolution Summary:
  Files resolved: 3/3
  Strategy breakdown:
    - Combine Both Changes: 1
    - Merge Complementary Logic: 1
    - Structural Merge: 1
  Test results: ✓ PASSED

Staging resolved files...
✓ git add modules/api/middleware.py
✓ git add tests/test_middleware.py
✓ git add config/settings.py

✅ Conflicts resolved automatically. Ready to commit.
```

**7.7. Safety Features**

- **Confirmation prompt**: Prevents accidental batch merges
- **Dry-run mode**: `--dry-run` flag to preview without executing
- **Backup branches**: Create backup branch before merge (optional)
- **Rollback support**: If merge fails, restore to pre-merge state
- **Selective processing**: `--only <worktree-name>` to merge specific worktree
- **Exclude pattern**: `--exclude <pattern>` to skip certain worktrees

**7.8. Advanced Options**

```
/tree closedone [options]

Options:
  --dry-run              Preview actions without executing
  --resume               Resume from last paused position
  --skip <name>          Skip specific worktree
  --only <name>          Process only specific worktree
  --exclude <pattern>    Exclude worktrees matching pattern
  --backup               Create backup branches before merge
  --force-close          Force-kill terminals instead of graceful shutdown
  --no-archive           Don't archive completion files (delete instead)
```

**7.9. Terminal Cleanup Strategy**

Detect terminal environment and close appropriately:

**Tmux:**
```bash
# Find tmux window/pane by working directory
tmux list-panes -a -F "#{pane_id} #{pane_current_path}" | grep worktree-name
# Close gracefully
tmux kill-pane -t <pane-id>
```

**VS Code Integrated Terminal:**
```bash
# Find process by working directory
ps aux | grep "claude.*worktree-name"
# Send SIGTERM for graceful shutdown
kill -TERM <pid>
# VS Code should auto-close terminal when process ends
```

**Standalone Terminal:**
```bash
# Find Claude process
pgrep -f "claude.*worktree-name"
# Send SIGTERM
kill -TERM <pid>
# Note: Terminal window remains open (manual close required)
```

**7.10. Error Handling**

- **Worktree not found**: Skip with warning
- **Branch already merged**: Skip with informational message
- **Dirty working directory**: Prompt to stash/commit changes
- **Terminal close failure**: Log PID and instructions for manual closure
- **Archive failure**: Warn but don't fail entire operation

### 8. /tree status

**Purpose:** Show status of current worktree environment.

**Behavior:**
8.1. Detect if in worktree or main workspace
8.2. Show current branch
8.3. List all active worktrees
8.4. Show which worktrees have running processes
8.5. Display recent build history
8.6. Show completed worktrees (from /tree close)

**Example Output:**
```
🌳 Worktree Environment Status

Current Location: /workspace/.trees/worktree-manager
Current Branch: task/00-worktree-manager
Base Branch: develop/v4.2.0-20251009

Active Worktrees (3):
✓ real-time-collaboration (task/01-real-time-collaboration)
  └─ Claude running (PID 12345)
✓ api-rate-limiting (task/02-api-rate-limiting)
  └─ No active processes
✓ user-dashboard-redesign (task/03-user-dashboard-redesign)
  └─ Claude running (PID 12346)

Recent Builds:
- 2025-10-09 14:23 - 3 worktrees (develop/v4.2.0-20251009)

Actions:
- /tree list - Show staged features (if any)
- Monitor resources: cd /workspace/.trees/worktree-manager && ./monitor-resources.sh
```

### 9. /tree help

**Purpose:** Display comprehensive help for all /tree commands.

**Behavior:**
9.1. Show command summary
9.2. Provide usage examples
9.3. Link to full documentation

## Non-Goals (Out of Scope)

1. CI/CD integration (future enhancement)
2. Cross-repository worktrees
3. Remote worktree creation (local only)
4. Automatic deployment (manual deployment workflow required)

## Design Considerations

### Command Structure
```
/tree <subcommand> [args]

Planning Phase:
  stage [description]    - Add feature to staging
  list                   - Show staged features
  remove [number]        - Remove staged feature
  clear                  - Clear all staged features
  conflict               - Analyze conflicts and suggest merges

Build Phase:
  build                  - Create worktrees from staged features

Active Development:
  status                 - Show worktree environment status
  close                  - Complete work, generate synopsis, prepare for terminal closure
  closedone              - Batch merge and cleanup all completed worktrees

Utilities:
  help                   - Show detailed help

Typical Workflow:
  1. /tree stage [description]  (repeat for each feature)
  2. /tree conflict             (analyze and merge if needed)
  3. /tree build                (create all worktrees)
  4. [work in worktrees]
  5. /tree close                (in each worktree when done)
  6. /tree closedone            (merge all completed worktrees back to develop)
```

### File Locations
- Staging file: `/workspace/.trees/.staged-features.txt`
- Build history: `/workspace/.trees/.build-history/`
- Generated tasks file: `/workspace/.trees/.current-build-tasks.txt` (temporary)
- Completed worktrees: `/workspace/.trees/.completed/`
  - Synopsis files: `<worktree-name>-synopsis-YYYYMMDD.md`
  - Changelog files: `<worktree-name>-changelog-YYYYMMDD.md`
- Conflict backups: `/workspace/.trees/.conflict-backup/<worktree-name>/`
  - Backup copies of conflicted files before agent resolution
  - Preserved for rollback if needed
- Archived worktrees: `/workspace/.trees/.archived/`
  - Files moved here after successful merge with `/tree closedone`
  - Includes conflict resolution logs if applicable

### Conflict Detection Algorithm
```python
def detect_conflicts(features):
    conflicts = []
    for i, feature_a in enumerate(features):
        for feature_b in features[i+1:]:
            # Check for overlapping files based on feature description keywords
            shared_files = analyze_shared_scope(feature_a, feature_b)
            if shared_files:
                severity = calculate_severity(shared_files)
                conflicts.append({
                    'features': [feature_a, feature_b],
                    'files': shared_files,
                    'severity': severity
                })
    return conflicts
```

### Git Branch Naming
```
develop/v[major.minor.patch]-[YYYYMMDD]

Examples:
- develop/v4.2.0-20251009
- develop/v5.0.0-20251015
```

### Safety Checks
- Never build if there are uncommitted changes on main/master
- Always confirm before destructive operations (clear, build with conflicts)
- Preserve staged features in build history
- Never auto-push to main branch

## Technical Considerations

### Slash Command Implementation
- File: `/workspace/.claude/commands/tree.md`
- Format: Standard Claude Code slash command
- Should handle multiple invocations in sequence
- State persisted in file system (staging file)

### Integration Points
- Uses existing `create-worktree-batch.sh`
- Uses existing `open-terminals.sh`
- Uses existing `launch-all-claude.sh`
- Adds git workflow automation

### Error Handling
- Invalid feature number: Show valid range
- No staged features: Prompt to stage first
- Git conflicts during commit: Offer to stash or abort
- Worktree creation failures: Continue with remaining, report failures
- Missing dependencies: Check for tmux, git, etc.

### Performance
- Staging is instant (append to file)
- Conflict analysis runs in < 5 seconds for typical feature count
- Build time depends on feature count (~10s per worktree)
- No performance impact when not actively using /tree

## Success Metrics

1. **Setup Time Reduction**: Worktree setup time reduced from 5+ minutes to < 2 minutes
2. **Error Rate**: < 5% of builds fail due to git conflicts or validation errors
3. **Adoption**: 80% of worktree builds use `/tree build` instead of manual scripts
4. **User Satisfaction**: "This is way easier" feedback from developers
5. **Conflict Prevention**: 90% of HIGH conflicts identified before worktree creation

## Open Questions

1. **Interactive vs Batch**: Should `/tree stage` accept multiple features at once, or one at a time?
   - **Recommendation**: One at a time for simplicity, but support `/tree stage -f file.txt` for batch

2. **Version Numbering**: Should `/tree build` auto-increment version, or require user input?
   - **Recommendation**: Read from VERSION file, prompt for major/minor/patch increment

3. **Conflict Analysis Depth**: How deep should conflict analysis go?
   - **Recommendation**: Start with keyword-based file analysis, enhance with AST analysis later

4. **Tmux vs VS Code**: Which should be the default terminal method?
   - **Recommendation**: Detect if in VS Code, use appropriate method

5. **Claude Auto-Launch**: Should Claude auto-launch by default?
   - **Recommendation**: Prompt user during build, remember preference

6. **State Management**: Should staging persist across Claude sessions?
   - **Recommendation**: Yes, staging file persists until built or cleared

## Implementation Phases

### Phase 1: Basic Staging (MVP)
- `/tree stage [description]`
- `/tree list`
- `/tree clear`
- Basic file-based staging

### Phase 2: Build Automation
- `/tree build` with git operations
- Conflict analysis (basic keyword matching)
- Integration with existing scripts

### Phase 3: Enhanced Features
- `/tree remove [number]`
- `/tree status`
- Build history tracking
- Improved conflict detection

### Phase 4: Polish & Optimization
- Interactive editing of staged features
- Template-based feature staging
- Performance optimization
- Enhanced error messages

---

**Document Version:** 1.0
**Created:** 2025-10-09
**Type:** feature
**Status:** Draft
**Branch:** task/00-worktree-manager
**Worktree:** .trees/worktree-manager
**Priority:** High
**Estimated Effort:** 8-12 hours
