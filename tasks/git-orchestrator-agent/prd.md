# Product Requirements Document: Git Orchestrator Agent

**Version:** 1.0
**Date:** October 9, 2025
**Status:** Draft
**Feature Directory:** `/tasks/git-orchestrator-agent/`

---

## 1. Executive Summary

### Problem Statement
Current development workflow requires manual context switching between coding and git operations. Primary agents must interrupt their flow to run git commands, leading to:
- Context loss during development
- Inconsistent checkpoint/commit patterns
- Manual validation of schema automation
- Cognitive overhead deciding when to commit vs checkpoint

### Proposed Solution
Create a specialized `git-orchestrator` agent that handles all git operations autonomously when invoked by the primary agent. The primary agent makes explicit handoff decisions based on task completion state, and git-orchestrator executes operations with full validation, error handling, and recovery.

### Success Criteria
- Primary agent can complete multi-task sections with minimal git-related interruptions
- 90%+ of checkpoints created with proper validation (tests, schema automation)
- 100% of section commits include documentation verification
- Average handoff overhead: <200 tokens per invocation
- Zero manual git command execution during normal development flow

---

## 2. User Personas & Use Cases

### Persona 1: Development Agent (Primary User)
**Need:** Autonomous git operations without breaking development flow
**Interaction:** Explicit handoff at logical boundaries (task completion, section completion)
**Expectation:** git-orchestrator handles all validation, returns simple status

### Persona 2: Human Developer (Indirect User)
**Need:** Visibility into git operations and control over commits
**Interaction:** Receives notifications, confirms section commits, reviews error reports
**Expectation:** Clear status updates, ability to intervene when needed

### Use Case 1: Routine Checkpoint During Multi-Task Section
```
Context: Primary agent completes task 1.3 of 5 in "Database Schema" section
Flow:
  1. Primary agent marks task 1.3 complete in TodoWrite
  2. Primary agent thinks: "3 tasks done, checkpoint recommended"
  3. Primary agent invokes: git-orchestrator "checkpoint_check:Database Schema"
  4. git-orchestrator: Reads context, runs tests, creates checkpoint
  5. git-orchestrator returns: {status: "success", action: "checkpoint", hash: "abc1234"}
  6. Primary agent continues to task 1.4
Time: <10 seconds, <150 tokens overhead
```

### Use Case 2: Section Commit After All Tasks Complete
```
Context: Primary agent completes final task (1.5 of 5) in section
Flow:
  1. Primary agent marks task 1.5 complete
  2. Primary agent thinks: "All tasks done, section commit needed"
  3. Primary agent invokes: git-orchestrator "commit_section:Database Schema Setup"
  4. git-orchestrator: Runs full validation (tests, schema, docs)
  5. git-orchestrator: Generates commit message, requests confirmation
  6. User confirms
  7. git-orchestrator: Creates commit, updates version, generates changelog
  8. git-orchestrator returns: {status: "success", action: "section_commit", hash: "def5678"}
  9. Primary agent moves to next section
Time: <30 seconds, <250 tokens overhead
```

### Use Case 3: Validation Failure Recovery
```
Context: Section complete but tests failing
Flow:
  1. Primary agent invokes section commit
  2. git-orchestrator: Detects test failures
  3. git-orchestrator: Creates checkpoint instead (preserves progress)
  4. git-orchestrator returns: {status: "failed", blocking_issues: ["2 test failures"], checkpoint: "ghi9012"}
  5. Primary agent surfaces error to user
  6. Primary agent continues with other work while user fixes tests
Result: Development flow not blocked by test failures
```

### Use Case 4: Worktree Status Check
```
Context: User wants to see repository state across worktrees
Flow:
  1. User requests: "Show me worktree status"
  2. Primary agent invokes: git-orchestrator "worktree_status"
  3. git-orchestrator: Runs status check, formats output
  4. git-orchestrator returns: {status: "success", summary: {...}}
  5. Primary agent presents formatted summary to user
```

### Use Case 5: Automated Worktree Merge
```
Context: Feature branch ready to merge to main
Flow:
  1. User requests: "Merge this worktree to main"
  2. Primary agent invokes: git-orchestrator "merge_worktree:feature/email-validation"
  3. git-orchestrator: Validates branch state, performs merge
  4. git-orchestrator: Detects conflicts, aborts merge, reports
  5. git-orchestrator returns: {status: "conflict", details: [...]}
  6. Primary agent guides user through manual conflict resolution
```

---

## 3. Functional Requirements

### FR-1: Checkpoint Management
**Priority:** P0 (Critical)

**FR-1.1:** Autonomous checkpoint creation when invoked by primary agent
**FR-1.2:** Stage all uncommitted changes (`git add .`)
**FR-1.3:** Run test suite (quick check, skip if tests don't exist)
**FR-1.4:** Detect database schema changes via file patterns
**FR-1.5:** Auto-run `database_tools/update_schema.py` if schema changes detected
**FR-1.6:** Stage generated schema files automatically
**FR-1.7:** Warn if documentation missing for new code (non-blocking)
**FR-1.8:** Create checkpoint commit with conventional format
**FR-1.9:** Return structured status to primary agent

**Acceptance Criteria:**
- Checkpoint created in <10 seconds
- Test failures reported but don't block checkpoint creation
- Schema automation runs automatically without manual intervention
- Primary agent receives actionable status response

---

### FR-2: Section Commit Management
**Priority:** P0 (Critical)

**FR-2.1:** Validate section completion before committing
**FR-2.2:** Stage all changes
**FR-2.3:** Run **full test suite** (fail commit if tests fail)
**FR-2.4:** Detect and auto-run schema automation if needed
**FR-2.5:** **Verify documentation exists** for new code (fail if missing)
**FR-2.6:** Clean temporary files (*.pyc, __pycache__, .DS_Store, etc.)
**FR-2.7:** Generate conventional commit message based on changes
**FR-2.8:** Show preview, request user confirmation
**FR-2.9:** Create commit after confirmation
**FR-2.10:** Update version number in CLAUDE.md (line 3)
**FR-2.11:** Generate changelog template entry
**FR-2.12:** Prompt user to update master changelog
**FR-2.13:** Return structured status with commit details

**Acceptance Criteria:**
- Section commits only created when all validation passes
- Documentation requirement strictly enforced
- Commit messages follow conventional format
- Version automatically incremented
- Changelog template generated for user to complete
- Blocking issues clearly reported with remediation steps

---

### FR-3: Context Discovery
**Priority:** P0 (Critical)

**FR-3.1:** Discover active task list from `/tasks/*/tasklist_*.md`
**FR-3.2:** Parse task list to identify current section
**FR-3.3:** Count completed vs pending tasks in section
**FR-3.4:** Extract PRD path from task file header
**FR-3.5:** Determine last checkpoint from git log
**FR-3.6:** Analyze git status and diff for change summary
**FR-3.7:** Identify changed files and categorize (new, modified, deleted)

**Acceptance Criteria:**
- Agent can operate with minimal handoff context (section name only)
- Accurate task completion state detection
- Correct PRD reference extraction
- Efficient context gathering (<5 seconds)

---

### FR-4: Commit Message Generation
**Priority:** P0 (Critical)

**FR-4.1:** Infer commit type from changed files:
  - New features → "feat"
  - Bug fixes → "fix"
  - Documentation only → "docs"
  - Refactoring → "refactor"
  - Tests only → "test"
  - Configuration/tooling → "chore"

**FR-4.2:** Generate descriptive commit title (50 chars max)
**FR-4.3:** Generate detailed body with bullet points of changes
**FR-4.4:** Include reference to PRD and task section
**FR-4.5:** Add Claude Code co-authorship attribution
**FR-4.6:** Follow conventional commit format exactly

**Template:**
```
<type>: <brief description>

<detailed description>
- Change 1
- Change 2
- Change 3

Related to Task <section> in PRD: <path>

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

**Acceptance Criteria:**
- Commit type correctly inferred 90%+ of time
- Commit messages are descriptive and accurate
- All required sections present
- Passes conventional commit linting

---

### FR-5: Schema Automation Integration
**Priority:** P0 (Critical)

**FR-5.1:** Detect schema changes via file patterns:
  - `database_tools/migrations/*.sql`
  - `database/schema/*`
  - Any file with "migration" or "schema" in path

**FR-5.2:** Run smart schema check: `python database_tools/schema_automation.py --check`
**FR-5.3:** If changes detected (exit code 1), auto-run: `python database_tools/update_schema.py`
**FR-5.4:** Stage generated files:
  - `frontend_templates/database_schema.html`
  - `docs/component_docs/database/*`
  - `database_tools/generated/*`

**FR-5.5:** Report schema automation status in operation summary
**FR-5.6:** Handle automation failures gracefully (report, create checkpoint without generated files)

**Acceptance Criteria:**
- Schema automation runs automatically for 100% of schema changes
- Generated files always included in commits
- Automation failures don't block progress (checkpoint created instead)
- Clear error messages when automation fails

---

### FR-6: Test Execution & Validation
**Priority:** P0 (Critical)

**FR-6.1:** Detect test framework (pytest, npm test, etc.)
**FR-6.2:** Run quick test check for checkpoints (skip if no tests)
**FR-6.3:** Run full test suite for section commits
**FR-6.4:** Parse test results (passed, failed, skipped counts)
**FR-6.5:** For checkpoints: Warn on failures but proceed
**FR-6.6:** For section commits: Block commit on any test failure
**FR-6.7:** Report failing tests with file:line references
**FR-6.8:** Suggest "create checkpoint instead" when tests fail

**Acceptance Criteria:**
- Test detection works for pytest, npm, and common frameworks
- Test results accurately parsed and reported
- Section commits NEVER created with failing tests
- Clear guidance provided when tests fail

---

### FR-7: Documentation Validation
**Priority:** P0 (Critical)

**FR-7.1:** Detect new code files in commit:
  - Patterns: `*.py`, `*.js`, `*.ts`, `*.go`, `*.java` (exclude tests)

**FR-7.2:** Check for corresponding documentation:
  - Search `docs/component_docs/` for related documentation
  - Look for module-level docstrings in new files

**FR-7.3:** For checkpoints: Warn if documentation missing
**FR-7.4:** For section commits: **Block** if documentation missing
**FR-7.5:** Report which files need documentation
**FR-7.6:** Suggest documentation location following project structure

**Acceptance Criteria:**
- New code files accurately detected
- Documentation presence correctly validated
- Section commits blocked when documentation missing
- Clear guidance on where to add documentation

---

### FR-8: Error Handling & Recovery
**Priority:** P0 (Critical)

**FR-8.1:** Test failures: Create checkpoint, report details, suggest fixes
**FR-8.2:** Documentation missing: Block section commit, report files, suggest locations
**FR-8.3:** Schema automation fails: Report error, create checkpoint without schema files
**FR-8.4:** Database connection fails: Report error, suggest .env verification
**FR-8.5:** No changes to commit: Skip operation, return "no_changes" status
**FR-8.6:** User cancels confirmation: Abort operation, preserve staged changes

**FR-8.7:** Provide structured error responses:
```json
{
  "status": "failed",
  "reason": "tests_failed",
  "blocking_issues": [
    "modules/database/operations.py::test_insert_job FAILED",
    "modules/database/models.py::test_relationship FAILED"
  ],
  "remediation": [
    "Fix failing tests",
    "Create checkpoint instead to save progress",
    "Show test details for debugging"
  ],
  "fallback_action": "checkpoint_created",
  "fallback_hash": "ghi9012"
}
```

**Acceptance Criteria:**
- All error conditions handled gracefully
- Fallback actions always available (checkpoint when commit fails)
- Clear, actionable error messages
- Structured error responses for programmatic handling
- Development flow never permanently blocked

---

### FR-9: Worktree Management
**Priority:** P1 (High)

**FR-9.1:** Worktree status dashboard:
  - List all active worktrees and locations
  - Show merged vs unmerged branches
  - Display commit counts ahead of main
  - Report uncommitted changes per worktree
  - Check upstream tracking configuration

**FR-9.2:** Worktree merge automation:
  - Switch to main branch
  - Pull latest remote changes
  - Identify unmerged branches
  - Show merge preview, request confirmation
  - Merge branches sequentially
  - Auto-configure upstream tracking if missing
  - Detect conflicts, abort problematic merges
  - Push to remote after successful merges
  - Report summary with any conflicts

**FR-9.3:** Delegate to existing scripts:
  - `./worktree_tools/worktree_status.sh` for status
  - `./worktree_tools/merge_worktrees.sh` for merging

**Acceptance Criteria:**
- Status dashboard provides comprehensive view
- Merge process handles conflicts gracefully
- Upstream tracking auto-configured
- Clear reporting of merge results

---

### FR-10: Response Format & Primary Agent Integration
**Priority:** P0 (Critical)

**FR-10.1:** Return structured JSON responses:
```json
{
  "status": "success|skipped|failed|conflict|no_changes",
  "action": "checkpoint|section_commit|worktree_status|merge|none",
  "commit_hash": "abc1234",
  "version_updated": "4.00 → 4.01",
  "message": "Human-readable summary",
  "blocking_issues": [],
  "remediation": [],
  "files_changed": {
    "new": 3,
    "modified": 5,
    "deleted": 0
  },
  "tests": {
    "passed": 12,
    "failed": 0,
    "skipped": 1
  },
  "schema_automation": "run|skipped|failed",
  "documentation": "present|missing|warned"
}
```

**FR-10.2:** Support invocation patterns:
  - `"checkpoint_check:Section Name"`
  - `"commit_section:Section Name"`
  - `"worktree_status"`
  - `"merge_worktree:branch-name"`

**FR-10.3:** Concise confirmation messages for users:
  - Checkpoints: `✅ Checkpoint: "Section Name" [abc1234]`
  - Commits: `✅ Section commit: "feat: description" [def5678]`
  - Errors: `❌ Cannot commit: 2 tests failing (checkpoint created instead)`

**Acceptance Criteria:**
- Primary agent can parse response with <10 tokens of logic
- Status field is always present and accurate
- Human-readable messages suitable for user display
- Structured data available for programmatic decisions

---

## 4. Non-Functional Requirements

### NFR-1: Performance
- Checkpoint creation: <10 seconds (including tests)
- Section commit: <30 seconds (including full validation)
- Context discovery: <5 seconds
- Response generation: <2 seconds
- **Total handoff overhead: <200 tokens per invocation**

### NFR-2: Reliability
- 100% idempotent operations (can invoke multiple times safely)
- Zero data loss (always create checkpoint before risky operations)
- Graceful degradation (if tests fail, create checkpoint instead)
- Atomic operations (commit succeeds completely or not at all)

### NFR-3: Token Efficiency
- Agent specification: <2,000 tokens
- Average invocation: ~3,500-5,000 tokens total
- Context gathering: <500 tokens
- Response formatting: <200 tokens
- No redundant file reads or command executions

### NFR-4: Maintainability
- Agent logic clearly documented
- Error messages reference CLAUDE.md sections
- Logging for debugging and auditing
- Version controlled agent specification

### NFR-5: Security
- Never commit sensitive files (.env, credentials)
- Validate all paths to prevent directory traversal
- Sanitize user input in commit messages
- Verify git operations complete successfully before reporting success

---

## 5. Technical Architecture

### Agent Specification Location
`/.claude/agents/git-orchestrator.md`

### Agent Configuration
```yaml
---
name: git-orchestrator
description: Autonomous git operations manager for development workflows. Handles checkpoints, section commits, and worktree management. Invoked explicitly by primary agent at task boundaries.
model: haiku
color: green
tools: Bash, Read, Grep, Glob
---
```

### Command Patterns

#### Checkpoint Check
```bash
# Invoked by primary agent
git-orchestrator "checkpoint_check:Database Schema"

# Agent actions
1. Find active task list
2. Parse section status
3. Check git status
4. Run tests (quick)
5. Detect schema changes
6. Run schema automation if needed
7. Create checkpoint commit
8. Return structured response
```

#### Section Commit
```bash
# Invoked by primary agent
git-orchestrator "commit_section:Database Schema Setup"

# Agent actions
1. Find active task list
2. Validate all tasks complete
3. Check git status
4. Run full test suite (block if fail)
5. Detect schema changes
6. Run schema automation if needed
7. Validate documentation (block if missing)
8. Clean temp files
9. Generate commit message
10. Show preview, request confirmation
11. Create commit
12. Update CLAUDE.md version
13. Generate changelog template
14. Return structured response
```

#### Worktree Status
```bash
# Invoked by primary agent
git-orchestrator "worktree_status"

# Agent actions
1. Run ./worktree_tools/worktree_status.sh
2. Parse output
3. Format summary
4. Return structured response
```

#### Worktree Merge
```bash
# Invoked by primary agent
git-orchestrator "merge_worktree:feature/email-validation"

# Agent actions
1. Validate branch exists
2. Run ./worktree_tools/merge_worktrees.sh
3. Monitor for conflicts
4. Report results
5. Return structured response
```

### Integration with Existing Scripts

**Leverage existing automation:**
- `scripts/checkpoint.sh` - Called via Bash tool
- `scripts/commit-section.sh` - Called via Bash tool
- `worktree_tools/worktree_status.sh` - Called via Bash tool
- `worktree_tools/merge_worktrees.sh` - Called via Bash tool
- `database_tools/update_schema.py` - Called via Bash tool

**Agent adds value through:**
- Context discovery and parsing
- Intelligent decision-making
- Error handling and recovery
- Structured response formatting
- Integration with primary agent workflow

---

## 6. Workflow Integration

### Primary Agent Instructions Update

Add to primary agent's system prompt:

```markdown
## Git Operations Delegation

You have access to git-orchestrator agent for version control operations.

### Decision Logic: When to Invoke

**After completing any sub-task:**
1. Check: How many sub-tasks completed in current section?
2. If 3+ tasks completed since last checkpoint:
   - Invoke: git-orchestrator "checkpoint_check:{{section_name}}"
   - Summarize what you did since last checkpoint
   - Identify key files changed
   - Wait for response
   - Check status field in response:
     * "success": Continue to next task
     * "skipped": Continue (no changes to commit)
     * "failed": Surface error to user, continue with other work

**After completing all sub-tasks in a section:**
1. Verify: All checkboxes marked complete in section
2. Invoke: git-orchestrator "commit_section:{{section_name}}"
3. Summarize section accomplishments
4. Identify all files modified in section
5. Wait for response (may require user confirmation)
6. Check status field:
   * "success": Proceed to next section
   * "failed": Surface blocking issues, wait for user to resolve

**Note:** Worktree operations will be added in future phase after worktree management branch is merged.

### Handoff Context Requirements

When invoking git-orchestrator, provide:
1. **Operation type**: checkpoint_check | commit_section
2. **Section name**: Current section being worked on
3. **Summary**: Brief description of work completed
4. **Files changed**: List of key files modified (git-orchestrator will verify)

Example invocation:
```
Invoking git-orchestrator for checkpoint...

Operation: checkpoint_check:Database Schema
Summary: Completed tasks 1.1-1.3: created email_validations table, added validation fields to users table, ran migrations
Files: database_tools/migrations/004_add_email_validations.sql, database_tools/migrations/005_update_users_validation.sql
```

### Response Handling

git-orchestrator returns structured JSON. Check only the "status" field:
- **"success"**: Operation completed, continue immediately
- **"skipped"**: No action needed (e.g., no changes), continue
- **"failed"**: Blocking issues exist, surface to user with remediation options

DO NOT parse detailed fields unless status is "failed" (then read blocking_issues).

The response message field is formatted for user display - you can show it directly.

### What NOT to Do

- ❌ Do NOT run git commands directly (git add, git commit, git push, etc.)
- ❌ Do NOT bypass git-orchestrator for any git operations
- ❌ Do NOT continue to next section if section commit failed
- ❌ Do NOT ignore "failed" status responses
- ❌ Do NOT provide minimal context (git-orchestrator needs full picture)
```

### TodoWrite Integration

```markdown
After calling TodoWrite to mark task complete:
1. Count completed tasks in section
2. If 3+ completed: Invoke git-orchestrator for checkpoint
3. If all complete: Invoke git-orchestrator for section commit

This ensures git operations happen immediately after task state changes.
```

---

## 7. User Experience Requirements

### UX-1: Visibility
- Show git operations in progress (status line or brief message)
- Display commit hashes for reference
- Show version number changes
- Report test results summary

### UX-2: Control
- Request confirmation before section commits (show preview, allow abort)
- Automatic push to remote after successful section commit
- Provide "skip" options for non-critical validations
- Enable user to override decisions with clear reasoning

### UX-3: Feedback
- Concise success messages: `✅ Checkpoint created [abc1234]`
- Clear error messages with specific file:line references
- Actionable remediation steps for all failures
- Progress indicators for long operations (tests, schema automation)

### UX-4: Recovery
- Always offer fallback option (checkpoint when commit fails)
- Preserve work-in-progress via checkpoints
- Guide user through conflict resolution
- Never leave repository in broken state

---

## 8. Testing & Validation

### Test Scenarios

**TS-1: Routine Checkpoint Creation**
- Given: 3 tasks completed in a section with file changes
- When: Primary agent invokes checkpoint_check
- Then: Checkpoint created successfully with tests run and schema automation

**TS-2: Section Commit with All Validations Passing**
- Given: All tasks in section complete, tests pass, documentation exists
- When: Primary agent invokes commit_section
- Then: Section commit created, version updated, changelog template generated

**TS-3: Section Commit Blocked by Test Failures**
- Given: All tasks complete but 2 tests failing
- When: Primary agent invokes commit_section
- Then: Operation fails, checkpoint created instead, test failures reported

**TS-4: Section Commit Blocked by Missing Documentation**
- Given: All tasks complete, tests pass, but new code lacks documentation
- When: Primary agent invokes commit_section
- Then: Operation blocked, missing documentation reported with suggestions

**TS-5: Schema Automation Triggered Automatically**
- Given: Database migration files changed
- When: Any checkpoint or commit operation
- Then: Schema automation runs automatically, generated files staged

**TS-6: Idempotent Operations**
- Given: Checkpoint already created for current state
- When: Primary agent invokes checkpoint_check again
- Then: Returns "skipped" status, no duplicate commit

**TS-7: Worktree Merge with Conflicts**
- Given: Feature branch diverged from main with conflicts
- When: Invoke merge_worktree
- Then: Conflict detected, merge aborted, manual resolution required

**TS-8: No Changes to Commit**
- Given: No uncommitted changes exist
- When: Invoke checkpoint_check
- Then: Returns "no_changes" status, no commit created

---

## 9. Success Metrics

### Quantitative Metrics
- **Checkpoint success rate**: >95% of checkpoints created without errors
- **Section commit validation rate**: 100% of commits include required validations
- **Schema automation trigger rate**: 100% of schema changes trigger automation
- **Token efficiency**: <200 tokens average handoff overhead
- **Operation speed**: <10s for checkpoints, <30s for section commits
- **Error recovery rate**: 100% of failures result in checkpoint fallback

### Qualitative Metrics
- Primary agent developers report reduced git-related interruptions
- Human developers report consistent, high-quality commit history
- Changelog entries are comprehensive and accurate
- Version numbers correctly incremented
- Documentation coverage improves over time

---

## 10. Implementation Phases

### Phase 1: Core Agent & Checkpoint Management (Week 1)
**Deliverables:**
- Agent specification file created
- Checkpoint detection and creation working
- Test execution integrated
- Schema automation detection working
- Basic error handling implemented

**Definition of Done:**
- Primary agent can invoke checkpoint_check successfully
- Checkpoints created with proper validation
- Structured responses returned
- Tests pass for checkpoint scenarios

---

### Phase 2: Section Commit Management (Week 2)
**Deliverables:**
- Section commit validation logic
- Documentation verification
- Commit message generation
- Version update automation
- Changelog template generation
- User confirmation flow

**Definition of Done:**
- Primary agent can invoke commit_section successfully
- All validations enforced (tests, docs, schema)
- Commit messages follow conventional format
- Version numbers update automatically
- Tests pass for section commit scenarios

---

### Phase 3: Context Discovery & Intelligence (Week 3)
**Deliverables:**
- Task list parsing
- Section status detection
- Completion state validation
- PRD path extraction
- Commit type inference
- Smart change analysis

**Definition of Done:**
- Agent operates with minimal handoff context
- Accurate task completion detection
- Correct commit type inference 90%+ of time
- Efficient context gathering (<5s)

---

### Phase 4: Error Handling & Polish (Week 4)
**Deliverables:**
- Comprehensive error handling for all scenarios
- Fallback operations (checkpoint when commit fails)
- Enhanced error messages with remediation
- Idempotency guarantees
- Performance optimization

**Definition of Done:**
- All error scenarios handled gracefully
- No operation leaves repository in broken state
- Error messages clear and actionable
- Performance targets met
- All acceptance criteria satisfied

---

## 11. Dependencies & Constraints

### Dependencies
- Existing shell scripts must remain functional:
  - `scripts/checkpoint.sh`
  - `scripts/commit-section.sh`
  - `database_tools/update_schema.py`
- Worktree scripts deferred (will integrate post-merge with worktree management branch)
- Task list format in `/tasks/*/tasklist_*.md`
- TodoWrite tool availability in primary agent
- Git repository initialized and configured
- Test framework installed (pytest or npm test)
- Database tools functional

### Constraints
- Must work within Claude Code agent framework
- Token budget: <5,000 tokens per invocation (including context)
- Must integrate with existing workflows without breaking changes
- Cannot modify core git behavior (only orchestrate existing tools)
- Must respect CLAUDE.md policies (schema automation, documentation)

---

## 12. Resolved Design Decisions

1. **Q:** Should git-orchestrator ever push to remote automatically?
   **A:** ✅ DECIDED - YES, automatically push after section commits. No push for checkpoints (local only).

2. **Q:** How to handle multi-file task lists (tasklist_1.md, tasklist_2.md)?
   **A:** ✅ DECIDED - Read all tasklist_*.md files in feature directory, parse all, merge completion state across all files.

3. **Q:** Should changelog updates be automated or require user input?
   **A:** ✅ DECIDED - Generate markdown template with facts, prompt user to complete with narrative context.

4. **Q:** What if user doesn't have pre-commit hooks installed?
   **A:** ✅ DECIDED - Agent validates independently, doesn't rely on hooks (defense in depth).

5. **Q:** How to handle git operations in sub-directories (not root)?
   **A:** ✅ DECIDED - Detect git root using `git rev-parse --show-toplevel`, operate from there.

6. **Q:** Should agent support custom commit message templates?
   **A:** ✅ DECIDED - Use conventional commit format by default. Custom templates are Phase 2+ enhancement.

7. **Q:** Should worktree management be in initial implementation?
   **A:** ✅ DECIDED - NO, defer to post-merge. User is working on worktree management in another branch. Will integrate after merge.

---

## 13. Risks & Mitigations

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Agent token overhead too high | High | Medium | Optimize context gathering, minimize file reads |
| Test execution takes too long | Medium | Low | Use quick tests for checkpoints, full suite for commits |
| Schema automation fails frequently | High | Low | Comprehensive error handling, fallback to checkpoint |
| Primary agent forgets to invoke | High | Medium | Clear instructions, TodoWrite integration reminders |
| Git operations corrupt repository | Critical | Very Low | Idempotent operations, validate before executing |
| Commit messages lack context | Medium | Medium | Improve message generation, allow user editing |
| Documentation validation too strict | Medium | Medium | Warn for checkpoints, block only for section commits |

---

## 14. Future Enhancements (Post-V1)

### Phase 5: Documentation & Integration (Week 5)
**Deliverables:**
- Complete agent specification
- Primary agent integration guide
- User documentation
- CLAUDE.md updates
- Changelog entries
- Implementation review document

**Definition of Done:**
- Agent specification complete and tested
- Primary agents know how to invoke git-orchestrator
- User guide published
- All documentation updated
- Tests pass
- Ready for production use

---

### Worktree Management (Post-Merge)
- Worktree status dashboard
- Worktree merge automation
- Conflict detection and reporting
- Integration with worktree management branch work

### Advanced Intelligence
- Auto-detect commit type from git diff content (not just files)
- Suggest section names from task list context
- Pre-emptive validation before task completion
- Smart checkpoint timing (before risky operations)

### Advanced Automation
- Automatic changelog generation from commit history
- Semantic version bump suggestions (major/minor/patch)
- PR description generation from section commits
- Release note compilation

### Enhanced Worktree Support (After Initial Worktree Integration)
- Parallel worktree status checks
- Bulk merge operations with dry-run mode
- Worktree creation wizard
- Automatic branch cleanup after merge

### Integration Enhancements
- Pre-commit hook generation
- CI/CD pipeline integration
- GitHub Actions workflow suggestions
- Slack/Discord notifications for commits

---

## 15. Appendices

### Appendix A: Example Agent Invocations

**Checkpoint Check:**
```
Primary Agent: Invoking git-orchestrator for checkpoint...

Operation: checkpoint_check:Database Schema
Summary: Completed tasks 1.1-1.3
- Created email_validations table migration
- Added validation fields to users table
- Ran migrations on development database

Files changed:
- database_tools/migrations/004_add_email_validations.sql (new)
- database_tools/migrations/005_update_users_validation.sql (new)

git-orchestrator:
✅ Checkpoint created
Tests: 12 passed
Schema automation: run
Commit: checkpoint: Database Schema (tasks 1.1-1.3) [abc1234]

Primary Agent: Continuing to task 1.4...
```

**Section Commit:**
```
Primary Agent: Invoking git-orchestrator for section commit...

Operation: commit_section:Database Schema Setup
Summary: All tasks complete (1.1-1.5)
- Created database migrations
- Updated schema documentation
- Added validation indexes
- Ran schema automation
- Verified all tests passing

Files changed:
- database_tools/migrations/004_*.sql (2 new)
- docs/component_docs/validation/email_system.md (new)
- frontend_templates/database_schema.html (generated)
- database_tools/generated/models.py (generated)

git-orchestrator:
Running validation...
✅ Tests: 12 passed
✅ Schema automation: run
✅ Documentation: present

Commit message preview:
---
feat: database schema setup for email validation

- Created email_validations table for audit trail
- Added validation fields to users table
- Implemented performance indexes
- Generated schema documentation

Related to Task 1: Database Schema in PRD: /tasks/email-validation/prd.md

🤖 Generated with [Claude Code](https://claude.com/claude-code)
Co-Authored-By: Claude <noreply@anthropic.com>
---

Confirm commit? (y/n): y

✅ Section committed: feat: database schema setup [def5678]
📊 Version updated: 4.00 → 4.01
📝 Changelog template generated

Primary Agent: Moving to next section: Core Validation Service
```

### Appendix B: Error Response Examples

**Test Failures:**
```json
{
  "status": "failed",
  "reason": "tests_failed",
  "action": "checkpoint",
  "fallback_hash": "ghi9012",
  "message": "Cannot commit section: 2 tests failing. Checkpoint created instead.",
  "blocking_issues": [
    "modules/database/operations.py::test_insert_job FAILED",
    "modules/database/models.py::test_relationship FAILED"
  ],
  "remediation": [
    "Fix failing tests in database module",
    "Run tests locally: pytest modules/database/",
    "Review test output for details",
    "Re-invoke commit_section after fixing"
  ],
  "tests": {
    "passed": 10,
    "failed": 2,
    "skipped": 0
  }
}
```

**Documentation Missing:**
```json
{
  "status": "failed",
  "reason": "documentation_missing",
  "action": "none",
  "message": "Cannot commit section: Documentation required for new code.",
  "blocking_issues": [
    "modules/validation/email_validator.py (new file, no documentation)"
  ],
  "remediation": [
    "Create component documentation in docs/component_docs/validation/",
    "Add comprehensive docstrings to email_validator.py",
    "Document public API and usage examples",
    "Re-invoke commit_section after documenting"
  ],
  "documentation": "missing"
}
```

### Appendix C: Configuration Examples

**.claude/agents/git-orchestrator.md Header:**
```yaml
---
name: git-orchestrator
description: Autonomous git operations manager for development workflows. Handles checkpoints, section commits, and worktree management. Invoked explicitly by primary agent at task boundaries. Performs full validation, error handling, and recovery.
model: haiku
color: green
tools: Bash, Read, Grep, Glob
---
```

**Invocation from Primary Agent:**
```python
# Pseudo-code for primary agent logic

def on_task_complete(task, section):
    completed_count = count_completed_tasks(section)

    if completed_count >= 3:
        response = invoke_agent(
            "git-orchestrator",
            f"checkpoint_check:{section.name}",
            context={
                "summary": task.summary,
                "files_changed": get_changed_files()
            }
        )

        if response.status == "failed":
            report_error_to_user(response.blocking_issues)

    if all_tasks_complete(section):
        response = invoke_agent(
            "git-orchestrator",
            f"commit_section:{section.name}",
            context={
                "summary": section.summary,
                "files_changed": get_changed_files()
            }
        )

        if response.status == "success":
            move_to_next_section()
        else:
            report_blockers_to_user(response.blocking_issues)
```

---

## 16. Approval & Sign-off

**Product Owner:** [User]
**Development Lead:** Claude Code
**Target Start Date:** Upon approval
**Target Completion Date:** 5 weeks from start (reduced from 6 weeks - worktree management deferred)

**Approval Status:** Pending Review

---

**End of PRD**
