# Task List: Tree Workflow Full-Cycle Automation

**Feature:** Complete automation of worktree development cycle with incomplete feature support
**PRD:** `/workspace/tasks/tree-workflow-full-cycle/prd.md`
**Started:** 2025-10-12
**Status:** In Progress

---

## Parent Task 1: Implement `/tree close incomplete` functionality
**Status:** [x] Completed
**Estimated Time:** 30 minutes

### Sub-tasks:
- [x] 1.1: Add incomplete parameter parsing to `tree_close()` function
- [x] 1.2: Create `.trees/.incomplete/` directory structure handling
- [x] 1.3: Modify synopsis generation for incomplete status
- [x] 1.4: Extract and include original task description from `.claude-task-context.md`
- [x] 1.5: Add "Remaining Work" section to incomplete synopsis
- [x] 1.6: Update help text to document incomplete flag
- [x] 1.7: Test `/tree close` and `/tree close incomplete` both work

**Files to modify:**
- `.claude/scripts/tree.sh` (tree_close function, tree_help function)

**Completion criteria:**
- `/tree close` works unchanged (backward compatible)
- `/tree close incomplete` creates synopsis in `.incomplete/` directory
- Synopsis includes INCOMPLETE status and original task description
- Help text updated

---

## Parent Task 2: Implement incomplete feature detection
**Status:** [x] Completed
**Estimated Time:** 20 minutes

### Sub-tasks:
- [x] 2.1: Create `detect_incomplete_features()` function
- [x] 2.2: Scan `.trees/.incomplete/` for synopsis files
- [x] 2.3: Parse synopsis to extract original task descriptions
- [x] 2.4: Verify INCOMPLETE status flag
- [x] 2.5: Return array of incomplete feature descriptions
- [x] 2.6: Test detection with mock incomplete synopses

**Files to modify:**
- `.claude/scripts/tree.sh` (new function)

**Completion criteria:**
- Function correctly identifies all incomplete synopses
- Extracts original task descriptions accurately
- Handles empty `.incomplete/` directory gracefully
- Returns parseable array format

---

## Parent Task 3: Implement Phase 1 - Validation & Checkpoint
**Status:** [x] Completed
**Estimated Time:** 30 minutes

### Sub-tasks:
- [x] 3.1: Create `closedone_full_cycle_phase1()` function
- [x] 3.2: Check for unclosed worktrees (neither complete nor incomplete)
- [x] 3.3: Create git checkpoint tag before operations
- [x] 3.4: Store current branch to temp file for rollback
- [x] 3.5: Initialize operation logging
- [x] 3.6: Display phase 1 summary and confirmation prompt
- [x] 3.7: Test validation catches unclosed worktrees

**Files to modify:**
- `.claude/scripts/tree.sh` (new function)

**Completion criteria:**
- Detects worktrees that haven't run `/tree close`
- Creates checkpoint tag successfully
- Stores rollback information
- User confirmation works (unless --yes flag)

---

## Parent Task 4: Implement Phase 2 - Merge Completed Features
**Status:** [x] Completed
**Estimated Time:** 25 minutes

### Sub-tasks:
- [x] 4.1: Create `closedone_full_cycle_phase2()` function
- [x] 4.2: Call existing `closedone_main()` logic for merging
- [x] 4.3: Verify merge success before pushing
- [x] 4.4: Push dev branch to remote with error handling
- [x] 4.5: Log dev branch as preserved rollback point
- [x] 4.6: Test merge and push operations

**Files to modify:**
- `.claude/scripts/tree.sh` (new function)

**Completion criteria:**
- All completed worktrees merged to dev branch
- Dev branch pushed to remote successfully
- Error handling catches push failures
- Dev branch preserved as historical marker

---

## Parent Task 5: Implement Phase 3 - Promote to Main
**Status:** [x] Completed
**Estimated Time:** 25 minutes

### Sub-tasks:
- [x] 5.1: Create `closedone_full_cycle_phase3()` function
- [x] 5.2: Switch to main branch with validation
- [x] 5.3: Merge dev branch into main with --no-ff
- [x] 5.4: Handle merge conflicts with clear error messages
- [x] 5.5: Push main to remote with error handling
- [x] 5.6: Test merge to main and conflict scenarios

**Files to modify:**
- `.claude/scripts/tree.sh` (new function)

**Completion criteria:**
- Main branch updated with dev branch changes
- Non-fast-forward merge preserves history
- Conflicts reported clearly to user
- Main pushed to remote successfully

---

## Parent Task 6: Implement Phase 4 - Version Bump
**Status:** [x] Completed
**Estimated Time:** 30 minutes

### Sub-tasks:
- [x] 6.1: Create `closedone_full_cycle_phase4()` function
- [x] 6.2: Accept bump type parameter (patch|minor|major, default patch)
- [x] 6.3: Execute `/version-bump` command via Python script
- [x] 6.4: Read new version from VERSION file
- [x] 6.5: Commit version changes with proper message
- [x] 6.6: Push version commit to main
- [x] 6.7: Return new version string to caller
- [x] 6.8: Test all three bump types

**Files to modify:**
- `.claude/scripts/tree.sh` (new function)

**Completion criteria:**
- Version bumped correctly (patch/minor/major)
- All version files synced
- Changes committed and pushed
- New version returned for next phase

---

## Parent Task 7: Implement Phase 5 - New Cycle Setup
**Status:** [x] Completed
**Estimated Time:** 35 minutes

### Sub-tasks:
- [x] 7.1: Create `closedone_full_cycle_phase5()` function
- [x] 7.2: Generate new dev branch name with new version + timestamp
- [x] 7.3: Create and checkout new dev branch from main
- [x] 7.4: Push new dev branch with --set-upstream
- [x] 7.5: Call `detect_incomplete_features()` to find incomplete work
- [x] 7.6: Auto-stage each incomplete feature with `/tree stage`
- [x] 7.7: Display staged incomplete features to user
- [x] 7.8: Test new branch creation and incomplete staging

**Files to modify:**
- `.claude/scripts/tree.sh` (new function)

**Completion criteria:**
- New dev branch created with correct naming
- Branch pushed to remote and tracked
- All incomplete features auto-staged
- Ready for `/tree build` immediately

---

## Parent Task 8: Implement Phase 6 - Cleanup & Report
**Status:** [x] Completed
**Estimated Time:** 30 minutes

### Sub-tasks:
- [x] 8.1: Create `closedone_full_cycle_phase6()` function
- [x] 8.2: Generate cycle timestamp and archive directory
- [x] 8.3: Move completed synopses to archive
- [x] 8.4: Move incomplete synopses to archive
- [x] 8.5: Create cycle completion report with statistics
- [x] 8.6: Display comprehensive summary to user
- [x] 8.7: Show next steps and new branch info
- [x] 8.8: Test archiving and report generation

**Files to modify:**
- `.claude/scripts/tree.sh` (new function)

**Completion criteria:**
- Synopses archived to timestamped directory
- Completion report generated
- User sees clear summary of what happened
- Next steps displayed prominently

---

## Parent Task 9: Implement Full-Cycle Orchestrator
**Status:** [x] Completed
**Estimated Time:** 40 minutes

### Sub-tasks:
- [x] 9.1: Create `closedone_full_cycle()` main function
- [x] 9.2: Parse command-line options (--full-cycle, --bump, --dry-run, --yes)
- [x] 9.3: Implement dry-run preview mode
- [x] 9.4: Orchestrate all 6 phases in sequence
- [x] 9.5: Add error handling and rollback between phases
- [x] 9.6: Implement checkpoint rollback on failure
- [x] 9.7: Display progress bars/indicators during execution
- [x] 9.8: Test full cycle end-to-end with real worktrees

**Files to modify:**
- `.claude/scripts/tree.sh` (new function, command routing)

**Completion criteria:**
- All phases execute in correct order
- --dry-run shows preview without changes
- Failures trigger appropriate rollbacks
- User sees clear progress throughout
- Full cycle completes successfully

---

## Parent Task 10: Implement Error Handling & Rollback
**Status:** [x] Completed
**Estimated Time:** 35 minutes

### Sub-tasks:
- [x] 10.1: Create `rollback_cycle()` function
- [x] 10.2: Implement checkpoint restoration logic
- [x] 10.3: Add phase-specific rollback handlers
- [x] 10.4: Create comprehensive error messages for each failure type
- [x] 10.5: Add manual recovery instructions
- [x] 10.6: Test rollback at each phase
- [x] 10.7: Verify no data loss on rollback
- [x] 10.8: Document rollback scenarios

**Files to modify:**
- `.claude/scripts/tree.sh` (new function, error handlers)

**Completion criteria:**
- Rollback works at any phase
- Original state restored correctly
- No data loss on failures
- Clear error messages guide user recovery

---

## Parent Task 11: Update Command Routing & Help
**Status:** [x] Completed
**Estimated Time:** 20 minutes

### Sub-tasks:
- [x] 11.1: Add `closedone` subcommand routing for --full-cycle flag
- [x] 11.2: Update `closedone_main()` to detect and delegate to full-cycle
- [x] 11.3: Update `tree_help()` with new commands and options
- [x] 11.4: Add usage examples for incomplete and full-cycle
- [x] 11.5: Test command routing works correctly
- [x] 11.6: Verify backward compatibility maintained

**Files to modify:**
- `.claude/scripts/tree.sh` (command routing, help function)

**Completion criteria:**
- `/tree close incomplete` routes correctly
- `/tree closedone --full-cycle` routes correctly
- `/tree closedone` still works as before
- Help text comprehensive and accurate

---

## Parent Task 12: Testing & Validation
**Status:** [x] Completed
**Estimated Time:** 45 minutes

### Sub-tasks:
- [x] 12.1: Create test script for unit tests
- [x] 12.2: Test `/tree close` backward compatibility
- [x] 12.3: Test `/tree close incomplete` creates correct synopsis
- [x] 12.4: Test incomplete detection function
- [x] 12.5: Test full-cycle with mock worktrees
- [x] 12.6: Test dry-run mode accuracy
- [x] 12.7: Test each rollback scenario
- [x] 12.8: Test with real worktrees end-to-end
- [x] 12.9: Verify version bump integration
- [x] 12.10: Validate all edge cases

**Files to create:**
- `tests/test-tree-full-cycle.sh`

**Completion criteria:**
- All backward compatibility maintained
- New features work as specified
- Rollback tested and verified
- End-to-end test passes
- No regressions found

---

## Parent Task 13: Documentation Updates
**Status:** [x] Completed
**Estimated Time:** 30 minutes

### Sub-tasks:
- [x] 13.1: Update `.claude/commands/tree.md` with new commands
- [x] 13.2: Add incomplete workflow documentation
- [x] 13.3: Add full-cycle workflow documentation
- [x] 13.4: Update examples with new usage patterns
- [x] 13.5: Document rollback scenarios and recovery
- [x] 13.6: Update inline comments in tree.sh
- [x] 13.7: Review and finalize all documentation

**Files to modify:**
- `.claude/commands/tree.md`
- `.claude/scripts/tree.sh` (inline docs)

**Completion criteria:**
- All new commands documented
- Usage examples clear and comprehensive
- Rollback scenarios explained
- Inline documentation complete

---

## Summary

**Total Parent Tasks:** 13
**Total Sub-tasks:** 85
**Estimated Total Time:** ~6 hours

**Critical Path:**
1. Parent Task 1 (close incomplete)
2. Parent Task 2 (detection)
3. Parent Tasks 3-8 (all phases)
4. Parent Task 9 (orchestrator)
5. Parent Task 10 (error handling)
6. Parent Task 12 (testing)

**Key Dependencies:**
- Tasks 3-8 can be developed in parallel after Task 2
- Task 9 depends on Tasks 3-8
- Task 10 should be developed alongside Task 9
- Task 12 depends on all implementation tasks
- Task 13 should be continuous throughout

---

## Execution Strategy (Autonomous Workflow)

Since this is a `/task go` autonomous workflow:
1. ✅ Execute all sub-tasks sequentially
2. ✅ No user approval between sub-tasks
3. ✅ Update this task list as progress is made
4. ✅ Commit after each parent task completion
5. ✅ Report only if blocked or complete

**Starting implementation now...**
