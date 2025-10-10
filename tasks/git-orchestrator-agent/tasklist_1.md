# Tasks: Git Orchestrator Agent Implementation

**PRD:** ./prd.md
**Task List:** tasklist_1.md
**Status:** Not Started
**Last Updated:** October 9, 2025
**Target Completion:** 5 weeks from approval

---

## Relevant Files

### To Be Created
- `.claude/agents/git-orchestrator.md` - Agent specification and instructions
- `docs/workflows/git-orchestrator-guide.md` - User documentation
- `docs/code_reviews/git-orchestrator-implementation-review.md` - Post-implementation review

### To Be Modified
- `CLAUDE.md` - Update with git-orchestrator integration notes
- `docs/changelogs/master-changelog.md` - Document feature addition
- Primary agent specifications (if separate files exist) - Add git-orchestrator handoff instructions

### Reference Files (Existing)
- `scripts/checkpoint.sh` - Checkpoint automation script (to be called)
- `scripts/commit-section.sh` - Section commit script (to be called)
- `worktree_tools/worktree_status.sh` - Worktree status script
- `worktree_tools/merge_worktrees.sh` - Worktree merge script
- `database_tools/update_schema.py` - Schema automation script
- `database_tools/schema_automation.py` - Schema change detection
- `docs/workflows/automatic-checkpoints-commits.md` - Existing checkpoint workflow
- `docs/workflows/automated-task-workflow.md` - Existing task workflow
- `docs/agent-creation-guidelines.md` - Agent design principles

---

## Phase 1: Core Agent & Checkpoint Management

### 1.1 Agent Specification Foundation
- [ ] 1.1.1 Create `.claude/agents/git-orchestrator.md` with YAML frontmatter
  - name: git-orchestrator
  - description: Autonomous git operations manager
  - model: haiku
  - color: green
  - tools: Bash, Read, Grep, Glob
- [ ] 1.1.2 Write "Core Responsibilities" section
  - Checkpoint management
  - Section commit management
  - Context discovery
  - Error handling and recovery
- [ ] 1.1.3 Write "Invocation Patterns" section
  - checkpoint_check:Section Name
  - commit_section:Section Name
  - worktree_status
  - merge_worktree:branch-name
- [ ] 1.1.4 Document response format structure (JSON schema)
- [ ] 1.1.5 Add project-specific context from CLAUDE.md

### 1.2 Context Discovery Implementation
- [ ] 1.2.1 Write logic for finding active task list
  - Pattern: `/tasks/*/tasklist_*.md`
  - Use most recently modified if multiple exist
  - Handle case where no task list found
- [ ] 1.2.2 Write task list parsing logic
  - Extract section name from markdown headers
  - Count completed vs pending tasks
  - Identify current section being worked on
- [ ] 1.2.3 Write PRD path extraction
  - Parse task file header for PRD reference
  - Validate path exists
  - Handle missing PRD gracefully
- [ ] 1.2.4 Write git status analysis
  - Run `git status --porcelain`
  - Categorize files: new, modified, deleted
  - Detect uncommitted changes
- [ ] 1.2.5 Write last checkpoint detection
  - Search git log for last checkpoint commit
  - Extract commit hash and timestamp
  - Calculate time since last checkpoint

### 1.3 Checkpoint Creation Logic
- [ ] 1.3.1 Implement checkpoint eligibility check
  - Verify uncommitted changes exist
  - Check if duplicate checkpoint (idempotency)
  - Validate section name provided
- [ ] 1.3.2 Implement file staging
  - Stage all changes: `git add .`
  - Verify staging successful
  - Report staged file count
- [ ] 1.3.3 Integrate test execution
  - Detect test framework (pytest, npm test, etc.)
  - Run quick test check: `pytest --tb=short -q`
  - Parse test results (passed/failed/skipped)
  - Warn on failures but proceed (non-blocking for checkpoints)
- [ ] 1.3.4 Implement schema change detection
  - Check patterns: `database_tools/migrations/`, `database/schema`
  - Run: `python database_tools/schema_automation.py --check`
  - Parse exit code (0=no changes, 1=changes detected)
- [ ] 1.3.5 Implement schema automation execution
  - Run: `python database_tools/update_schema.py`
  - Capture output and errors
  - Stage generated files on success
  - Report schema automation status
- [ ] 1.3.6 Implement documentation check (warning only)
  - Detect new code files (*.py, *.js, exclude tests)
  - Search for docs in `docs/component_docs/`
  - Warn if missing but don't block
- [ ] 1.3.7 Implement checkpoint commit creation
  - Generate commit message with conventional format
  - Call: `git commit -m "checkpoint: ..."`
  - Capture commit hash
  - Verify commit successful
- [ ] 1.3.8 Implement structured response generation
  - Format JSON response
  - Include status, action, hash, tests, schema_automation
  - Generate human-readable message

### 1.4 Error Handling for Checkpoints
- [ ] 1.4.1 Handle "no changes" scenario
  - Detect: `git status --porcelain` returns empty
  - Return status: "no_changes"
  - Skip commit creation
- [ ] 1.4.2 Handle test framework not found
  - Detect missing pytest/npm/etc
  - Log warning
  - Proceed without tests (non-critical for checkpoints)
- [ ] 1.4.3 Handle schema automation failure
  - Catch automation errors
  - Create checkpoint without schema files
  - Report error details
  - Suggest manual run
- [ ] 1.4.4 Handle git commit failure
  - Catch commit errors (e.g., pre-commit hook failure)
  - Report specific error
  - Suggest remediation
  - Return failed status

### 1.5 Testing & Validation (Phase 1)
- [ ] 1.5.1 Test checkpoint with file changes and passing tests
  - Expected: Checkpoint created successfully
- [ ] 1.5.2 Test checkpoint with failing tests
  - Expected: Warning shown, checkpoint still created
- [ ] 1.5.3 Test checkpoint with schema changes
  - Expected: Schema automation runs, files staged
- [ ] 1.5.4 Test checkpoint with no changes
  - Expected: "no_changes" status returned
- [ ] 1.5.5 Test idempotent checkpoint (invoke twice)
  - Expected: Second invocation returns "skipped"

---

## Phase 2: Section Commit Management

### 2.1 Section Validation Logic
- [ ] 2.1.1 Implement section completion check
  - Parse task list for current section
  - Verify all sub-tasks marked complete
  - Return validation result
- [ ] 2.1.2 Implement full test suite execution
  - Run: `pytest` (full suite, not quick check)
  - Parse complete test results
  - **Block commit if any tests fail**
  - Generate detailed failure report
- [ ] 2.1.3 Implement strict documentation validation
  - Detect new code files in staged changes
  - Search for corresponding documentation
  - **Block commit if documentation missing**
  - Report which files need docs
  - Suggest documentation locations

### 2.2 Commit Message Generation
- [ ] 2.2.1 Implement commit type inference
  - Analyze changed files and patterns
  - Detect: feat, fix, docs, refactor, test, chore
  - Default to "feat" if ambiguous
- [ ] 2.2.2 Implement commit title generation
  - Extract section name
  - Create descriptive title (50 chars max)
  - Follow conventional commit format
- [ ] 2.2.3 Implement commit body generation
  - Analyze git diff for changes
  - Generate bullet points of key changes
  - Include file count summary
- [ ] 2.2.4 Add PRD reference and attribution
  - Extract PRD path from task list
  - Add Claude Code co-authorship
  - Format with heredoc for proper structure

### 2.3 Section Commit Execution
- [ ] 2.3.1 Implement temporary file cleanup
  - Remove: *.pyc, __pycache__, .DS_Store, etc.
  - Log cleaned files
  - Re-stage after cleanup
- [ ] 2.3.2 Implement commit preview and confirmation
  - Show generated commit message
  - Display files to be committed
  - Request user confirmation (y/n)
  - Handle user rejection gracefully
- [ ] 2.3.3 Implement commit creation
  - Call: `git commit -m "$(cat <<'EOF'...)"`
  - Capture commit hash
  - Verify commit successful
- [ ] 2.3.4 Implement CLAUDE.md version update
  - Read current version from line 3
  - Increment minor version (4.00 → 4.01)
  - Write updated version
  - Stage CLAUDE.md
- [ ] 2.3.5 Implement changelog template generation
  - Extract commit details
  - Generate markdown template
  - Include date, version, changes, files
  - Prompt user to complete changelog

### 2.4 Fallback to Checkpoint on Failure
- [ ] 2.4.1 Implement test failure recovery
  - Detect test failures during section commit
  - Automatically create checkpoint instead
  - Report failed tests with details
  - Suggest fixes and re-invocation
- [ ] 2.4.2 Implement documentation failure recovery
  - Detect missing documentation
  - Block commit (don't create checkpoint)
  - Report missing files
  - Suggest documentation creation
- [ ] 2.4.3 Implement user cancellation handling
  - Detect user rejection of commit preview
  - Preserve staged changes
  - Return "cancelled" status
  - Allow user to modify and retry

### 2.5 Testing & Validation (Phase 2)
- [ ] 2.5.1 Test section commit with all validations passing
  - Expected: Commit created, version updated, changelog generated
- [ ] 2.5.2 Test section commit blocked by test failures
  - Expected: Checkpoint created instead, failures reported
- [ ] 2.5.3 Test section commit blocked by missing documentation
  - Expected: Commit blocked, missing files reported
- [ ] 2.5.4 Test commit type inference for different change types
  - Expected: Correct type inferred 90%+ of time
- [ ] 2.5.5 Test user cancellation flow
  - Expected: Operation aborted, changes preserved

---

## Phase 3: Context Discovery & Intelligence

### 3.1 Enhanced Task List Parsing
- [ ] 3.1.1 Implement multi-file task list support
  - Find all tasklist_*.md files
  - Read and merge task states
  - Handle tasklist_1.md, tasklist_2.md, etc.
- [ ] 3.1.2 Implement section boundary detection
  - Identify section headers (## headings)
  - Map tasks to sections
  - Track section completion state
- [ ] 3.1.3 Implement task counting by section
  - Count total tasks per section
  - Count completed tasks per section
  - Calculate completion percentage

### 3.2 Smart Change Analysis
- [ ] 3.2.1 Implement file categorization
  - Categorize by type: code, tests, docs, config
  - Categorize by module: database, API, frontend, etc.
  - Report distribution of changes
- [ ] 3.2.2 Implement change impact analysis
  - Identify critical files (migrations, schema, core logic)
  - Flag high-risk changes
  - Suggest extra validation
- [ ] 3.2.3 Implement commit type inference enhancement
  - Analyze diff content, not just filenames
  - Detect bug fix patterns in code
  - Identify refactoring patterns
  - Improve accuracy to 95%+

### 3.3 Context Caching & Efficiency
- [ ] 3.3.1 Implement context caching within session
  - Cache parsed task list
  - Cache git status results
  - Invalidate cache on operations
- [ ] 3.3.2 Minimize redundant file reads
  - Track which files already read
  - Only re-read if modified
  - Reduce token usage
- [ ] 3.3.3 Optimize git command usage
  - Combine git operations where possible
  - Use efficient git flags
  - Minimize shell invocations

### 3.4 Testing & Validation (Phase 3)
- [ ] 3.4.1 Test multi-file task list parsing
  - Expected: All tasks correctly merged and tracked
- [ ] 3.4.2 Test context caching reduces token usage
  - Expected: <500 tokens for context gathering
- [ ] 3.4.3 Test enhanced commit type inference accuracy
  - Expected: 95%+ accuracy on diverse change types

---

## Phase 4: Error Handling & Polish

### 4.1 Comprehensive Error Scenarios
- [ ] 4.1.1 Handle database connection failures
  - Detect connection errors
  - Report .env configuration issue
  - Suggest verification steps
  - Create checkpoint without schema files
- [ ] 4.1.2 Handle git repository not initialized
  - Detect missing .git directory
  - Report clear error
  - Suggest repository initialization
- [ ] 4.1.3 Handle pre-commit hook failures
  - Detect hook errors
  - Report specific hook failure
  - Suggest hook bypass or fix
- [ ] 4.1.4 Handle disk space issues
  - Detect disk full errors
  - Report storage issue
  - Suggest cleanup

### 4.2 Idempotency Guarantees
- [ ] 4.2.1 Implement duplicate checkpoint detection
  - Check if HEAD is already checkpoint for section
  - Compare timestamps and content
  - Return "skipped" if duplicate
- [ ] 4.2.2 Implement duplicate section commit detection
  - Search git log for existing section commit
  - Check if section already committed
  - Return "skipped" if duplicate
- [ ] 4.2.3 Test multiple invocations with same state
  - Expected: First succeeds, subsequent return "skipped"

### 4.3 Response Format Standardization
- [ ] 4.3.1 Define complete JSON schema
  - Document all fields
  - Define valid values for status
  - Document optional vs required fields
- [ ] 4.3.2 Implement response validation
  - Verify all required fields present
  - Validate field types
  - Catch malformed responses
- [ ] 4.3.3 Implement human-readable message generation
  - Concise success messages
  - Detailed error messages
  - Actionable remediation steps

### 4.4 Performance Optimization
- [ ] 4.4.1 Optimize test execution
  - Use pytest markers for quick tests
  - Skip slow tests for checkpoints
  - Run full suite only for section commits
- [ ] 4.4.2 Optimize schema automation
  - Cache schema hash between operations
  - Only run if database files changed
  - Minimize database queries
- [ ] 4.4.3 Optimize git operations
  - Use git plumbing commands where faster
  - Batch git operations
  - Minimize repository scans
- [ ] 4.4.4 Measure and document performance
  - Checkpoint: <10s target
  - Section commit: <30s target
  - Token usage: <200 tokens handoff overhead

### 4.5 Final Testing & Validation
- [ ] 4.5.1 End-to-end test: Complete feature workflow
  - Simulate full task execution with checkpoints and commit
  - Expected: All operations successful, proper commit history
- [ ] 4.5.2 Stress test: 10 consecutive checkpoints
  - Expected: All successful, no performance degradation
- [ ] 4.5.3 Error recovery test: Multiple failure scenarios
  - Expected: Graceful handling, clear messages, fallback actions
- [ ] 4.5.4 Integration test: Primary agent handoff
  - Expected: Seamless handoff, minimal context loss
- [ ] 4.5.5 Token usage test: Measure actual overhead
  - Expected: <200 tokens average per invocation

---

## Phase 5: Documentation & Integration

### 5.1 Agent Documentation
- [ ] 5.1.1 Complete agent specification in git-orchestrator.md
  - All sections documented
  - Examples included
  - Error scenarios covered
- [ ] 5.1.2 Create user guide: `docs/workflows/git-orchestrator-guide.md`
  - How to invoke from primary agent
  - Response handling
  - Common scenarios and examples
  - Troubleshooting guide
- [ ] 5.1.3 Update CLAUDE.md with integration notes
  - Add git-orchestrator to agent list
  - Document when to use
  - Link to detailed guide

### 5.2 Primary Agent Integration Instructions
- [ ] 5.2.1 Create primary agent integration guide: `docs/workflows/primary-agent-git-integration.md`
  - When to invoke git-orchestrator
  - Required context in handoff
  - Response handling logic
  - Error handling patterns
- [ ] 5.2.2 Create handoff examples
  - Checkpoint invocation example
  - Section commit invocation example
- [ ] 5.2.3 Update agent-usage-guide.md
  - Add git-orchestrator entry
  - Decision framework for when to use
  - Integration with TodoWrite
- [ ] 5.2.4 Document TodoWrite integration
  - After marking task complete
  - Count tasks, decide on checkpoint
  - Invoke git-orchestrator as needed

### 5.3 Changelog & Version Updates
- [ ] 5.3.1 Update master changelog
  - Document git-orchestrator feature addition
  - List all capabilities
  - Note integration points
  - Add version bump
- [ ] 5.3.2 Update CLAUDE.md version
  - Increment to next version
  - Document milestone

### 5.4 Code Review & Final Validation
- [ ] 5.4.1 Create implementation review document
  - Path: `docs/code_reviews/git-orchestrator-implementation-review.md`
  - Review all components
  - Validate against PRD requirements
  - Document any deviations
- [ ] 5.4.2 Verify all acceptance criteria met
  - Check PRD Section 3 (Functional Requirements)
  - Check PRD Section 4 (Non-Functional Requirements)
  - Document pass/fail for each criterion
- [ ] 5.4.3 Performance validation
  - Measure checkpoint time
  - Measure section commit time
  - Measure token usage
  - Compare against targets

---

## Success Criteria Summary

### Must-Have (P0)
- ✅ Checkpoint creation working with validation
- ✅ Section commit working with full validation suite
- ✅ Test execution integrated
- ✅ Schema automation integrated
- ✅ Documentation validation working
- ✅ Error handling and recovery functional
- ✅ Structured responses for primary agent
- ✅ Context discovery autonomous
- ✅ Commit message generation accurate

### Should-Have (P1)
- ✅ Performance targets met (<10s checkpoint, <30s commit)
- ✅ Token efficiency (<200 tokens handoff)

### Nice-to-Have (P2)
- Enhanced commit type inference (95%+ accuracy)
- Context caching optimization
- Advanced error scenarios covered
- Comprehensive user documentation

---

## Notes

- All phases should be completed sequentially (don't skip ahead)
- After each phase, run tests before proceeding to next phase
- Create checkpoints after completing 3+ tasks in any phase
- Create section commit after completing entire phase
- Update this task list as requirements evolve
- Document any deviations from PRD in notes

---

**Total Tasks:** 84 tasks across 5 phases (worktree management deferred)
**Estimated Effort:** 5 weeks (Phases 1-3: 3 weeks, Phase 4: 1 week, Phase 5: 1 week)
**Status:** Ready for approval and implementation
