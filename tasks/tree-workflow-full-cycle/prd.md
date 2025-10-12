# PRD: Tree Workflow Full-Cycle Automation

**Version:** 1.0
**Date:** 2025-10-12
**Status:** Approved
**Feature Branch:** task/02-worktree-improvements

---

## Executive Summary

Implement comprehensive automation for the complete worktree development cycle, from feature staging through version bump and next-cycle preparation. This includes support for incomplete/partial features that need to continue across development cycles.

### Key Additions
1. **`/tree close incomplete`** - Mark worktrees as partial/incomplete for continuation
2. **`/tree closedone --full-cycle`** - Full automation from merge → version bump → new cycle
3. **Incomplete worktree detection** - Automatically stage incomplete work for next cycle

---

## Problem Statement

### Current Workflow Gaps

**Manual Steps Required:**
1. After `/tree closedone` merges to dev branch, user must manually:
   - Checkpoint dev branch
   - Push dev branch to remote
   - Merge dev branch to main
   - Push main to remote
   - Run `/version-bump`
   - Create new dev branch
   - Re-stage incomplete features

**No Support for Partial Work:**
- No way to mark worktrees as "incomplete but needs to continue"
- All closed worktrees are treated as "complete"
- User must manually remember which features need more work

### User Pain Points

1. **Repetitive Manual Operations** - 8+ steps after every closedone
2. **Context Loss** - Incomplete features forgotten between cycles
3. **Error-Prone** - Easy to forget steps in the workflow
4. **No Rollback Point** - Dev branch not preserved as historical marker

---

## Goals & Success Criteria

### Goals

1. **Automate Complete Cycle** - Single command from worktree completion → next cycle ready
2. **Support Partial Work** - Track and continue incomplete features across cycles
3. **Preserve History** - Keep dev branches as rollback points
4. **Zero Manual Steps** - Fully automated workflow with safety checks

### Success Criteria

✅ `/tree close incomplete` marks features for continuation
✅ `/tree closedone --full-cycle` completes entire cycle
✅ Incomplete features automatically staged in new cycle
✅ Dev branch preserved and pushed to remote
✅ Version bumped and new dev branch created
✅ Main branch updated and pushed
✅ Comprehensive logging and error handling
✅ Dry-run mode available
✅ Rollback capability on failure

---

## User Stories

### Story 1: Developer Marks Incomplete Feature
**As a** developer
**I want to** mark a feature as incomplete when running `/tree close`
**So that** the system remembers to continue this work in the next cycle

**Acceptance Criteria:**
- `/tree close incomplete` generates synopsis with INCOMPLETE status
- Synopsis saved to `.trees/.incomplete/` directory
- Synopsis includes original task description and progress notes
- Branch preserved for potential reference

### Story 2: Developer Completes Full Cycle
**As a** developer
**I want to** run one command to complete the entire development cycle
**So that** I don't have to manually execute 8+ steps

**Acceptance Criteria:**
- `/tree closedone --full-cycle` executes all steps automatically
- Checkpoints created before major operations
- Dev branch pushed as historical marker
- Main branch updated and pushed
- Version bumped (patch by default)
- New dev branch created with new version
- Incomplete features automatically staged

### Story 3: Developer Recovers from Failure
**As a** developer
**I want to** rollback if something fails during the cycle
**So that** I don't lose work or corrupt the repository

**Acceptance Criteria:**
- Failures detected at each step
- Automatic rollback to last checkpoint
- Clear error messages explaining what failed
- Manual recovery instructions provided

---

## Technical Design

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    /tree close [incomplete]                  │
│                                                               │
│  ┌─────────────┐         ┌──────────────┐                   │
│  │  Complete   │         │  Incomplete  │                   │
│  │  Synopsis   │         │   Synopsis   │                   │
│  │   .completed/│         │  .incomplete/│                   │
│  └──────┬──────┘         └──────┬───────┘                   │
│         │                       │                            │
└─────────┼───────────────────────┼────────────────────────────┘
          │                       │
          ▼                       ▼
┌─────────────────────────────────────────────────────────────┐
│              /tree closedone --full-cycle                    │
│                                                               │
│  Phase 1: Validate & Checkpoint                              │
│    ✓ Check all worktrees closed                             │
│    ✓ Checkpoint current dev branch                          │
│                                                               │
│  Phase 2: Merge Completed Features                           │
│    ✓ Merge .completed/ worktrees to dev branch              │
│    ✓ Push dev branch (preserved as rollback)                │
│                                                               │
│  Phase 3: Promote to Main                                    │
│    ✓ Merge dev branch → main                                │
│    ✓ Push main to remote                                    │
│                                                               │
│  Phase 4: Version Bump                                       │
│    ✓ Run /version-bump [patch|minor|major]                  │
│    ✓ Read new version from VERSION file                     │
│                                                               │
│  Phase 5: New Cycle Setup                                    │
│    ✓ Create develop/v{new-version}-worktrees-{timestamp}    │
│    ✓ Detect incomplete features in .incomplete/             │
│    ✓ Auto-stage with /tree stage                            │
│                                                               │
│  Phase 6: Cleanup & Report                                   │
│    ✓ Archive completed/incomplete synopses                   │
│    ✓ Generate cycle completion report                       │
│    ✓ Display next steps                                     │
└─────────────────────────────────────────────────────────────┘
```

### Directory Structure

```
.trees/
├── .completed/              # Complete features (existing)
│   ├── feature-1-synopsis-20251012-120000.md
│   └── feature-2-synopsis-20251012-123000.md
├── .incomplete/             # Incomplete/partial features (NEW)
│   ├── feature-3-synopsis-20251012-130000.md
│   └── feature-4-synopsis-20251012-140000.md
├── .archived/               # Archived after merge (existing)
│   ├── cycle-20251012-044136/
│   │   ├── completed/
│   │   └── incomplete/
├── .build-history/          # Build history (existing)
└── [worktree-dirs]/         # Active worktrees
```

### Synopsis File Format

#### Complete Synopsis (`.completed/`)
```markdown
# Work Completed: feature-name

# Branch: task/01-feature-name
# Base: develop/v4.3.2-worktrees-20251012-044136
# Completed: 2025-10-12 12:00:00
# Status: COMPLETE

## Summary
[Description of completed work]

## Changes
- Files created: 5
- Files modified: 10
- Total commits: 3

[... rest of synopsis ...]
```

#### Incomplete Synopsis (`.incomplete/`)
```markdown
# Work In Progress: feature-name

# Branch: task/01-feature-name
# Base: develop/v4.3.2-worktrees-20251012-044136
# Closed: 2025-10-12 13:00:00
# Status: INCOMPLETE
# Resume: This feature needs to continue in the next development cycle

## Original Task Description
[Full description from .claude-task-context.md]

## Progress Summary
[What was accomplished]

## Remaining Work
- [ ] Task 1 still needed
- [ ] Task 2 still needed

## Changes So Far
- Files created: 2
- Files modified: 5
- Total commits: 2

[... rest of synopsis ...]
```

---

## Implementation Details

### Component 1: `/tree close incomplete`

**Location:** `.claude/scripts/tree.sh`
**Function:** `tree_close()`

**Changes:**
1. Accept optional `incomplete` parameter
2. Modify synopsis header with status flag
3. Save to `.incomplete/` instead of `.completed/`
4. Extract original task description from `.claude-task-context.md`
5. Include "Remaining Work" section

**Pseudocode:**
```bash
tree_close() {
    local status="COMPLETE"
    local target_dir="$COMPLETED_DIR"

    # Check for incomplete flag
    if [[ "$1" == "incomplete" ]]; then
        status="INCOMPLETE"
        target_dir="$TREES_DIR/.incomplete"
        mkdir -p "$target_dir"
    fi

    # Generate synopsis with status
    cat > "$synopsis_file" << EOF
# Work $([ "$status" = "COMPLETE" ] && echo "Completed" || echo "In Progress"): $worktree_name

# Branch: $branch
# Base: $base_branch
# $([ "$status" = "COMPLETE" ] && echo "Completed" || echo "Closed"): $(date)
# Status: $status
$([ "$status" = "INCOMPLETE" ] && echo "# Resume: This feature needs to continue in the next development cycle")

[... rest of synopsis ...]
EOF

    # Move to appropriate directory
    mv "$synopsis_file" "$target_dir/"
}
```

### Component 2: `/tree closedone --full-cycle`

**Location:** `.claude/scripts/tree.sh`
**Function:** `closedone_full_cycle()`

**Options:**
- `--full-cycle` - Execute complete cycle
- `--bump [patch|minor|major]` - Version bump type (default: patch)
- `--dry-run` - Preview without executing
- `--yes` - Skip confirmations

**Phases:**

#### Phase 1: Validate & Checkpoint
```bash
closedone_full_cycle_phase1() {
    # Verify all worktrees are closed
    check_for_unclosed_worktrees

    # Create checkpoint
    git checkout "$dev_branch"
    git tag "checkpoint-before-closedone-$(date +%Y%m%d-%H%M%S)"

    print_success "Phase 1: Validation complete"
}
```

#### Phase 2: Merge Completed Features
```bash
closedone_full_cycle_phase2() {
    # Merge all completed worktrees (existing logic)
    closedone_main

    # Push dev branch to remote
    git push origin "$dev_branch"

    print_success "Phase 2: Features merged and pushed"
}
```

#### Phase 3: Promote to Main
```bash
closedone_full_cycle_phase3() {
    # Switch to main
    git checkout main

    # Merge dev branch
    git merge "$dev_branch" --no-ff -m "Merge $dev_branch into main"

    # Push to remote
    git push origin main

    print_success "Phase 3: Promoted to main"
}
```

#### Phase 4: Version Bump
```bash
closedone_full_cycle_phase4() {
    local bump_type="${1:-patch}"

    # Run version bump
    python tools/version_manager.py --bump "$bump_type"
    python tools/version_manager.py --sync

    # Read new version
    local new_version=$(cat VERSION)

    # Commit version bump
    git add .
    git commit -m "chore: Bump version to $new_version"
    git push origin main

    print_success "Phase 4: Version bumped to $new_version"
    echo "$new_version"
}
```

#### Phase 5: New Cycle Setup
```bash
closedone_full_cycle_phase5() {
    local new_version=$1
    local timestamp=$(date +%Y%m%d-%H%M%S)
    local new_dev_branch="develop/v${new_version}-worktrees-${timestamp}"

    # Create new dev branch from main
    git checkout -b "$new_dev_branch" main
    git push -u origin "$new_dev_branch"

    # Detect and stage incomplete features
    if [ -d "$TREES_DIR/.incomplete" ]; then
        local incomplete_files=($(find "$TREES_DIR/.incomplete" -name "*-synopsis-*.md"))

        for synopsis_file in "${incomplete_files[@]}"; do
            # Extract original description
            local description=$(grep "^## Original Task Description" -A 10 "$synopsis_file" | tail -n +2 | head -n 1)

            # Stage for next cycle
            /workspace/.claude/scripts/tree.sh stage "$description"

            print_info "Staged incomplete feature: $description"
        done
    fi

    print_success "Phase 5: New cycle ready ($new_dev_branch)"
}
```

#### Phase 6: Cleanup & Report
```bash
closedone_full_cycle_phase6() {
    local cycle_timestamp=$(date +%Y%m%d-%H%M%S)
    local archive_dir="$TREES_DIR/.archived/cycle-$cycle_timestamp"

    # Archive synopses
    mkdir -p "$archive_dir/completed" "$archive_dir/incomplete"
    mv "$COMPLETED_DIR"/*.md "$archive_dir/completed/" 2>/dev/null || true
    mv "$TREES_DIR/.incomplete"/*.md "$archive_dir/incomplete/" 2>/dev/null || true

    # Generate completion report
    generate_cycle_report "$archive_dir"

    print_success "Phase 6: Cleanup complete"
}
```

### Component 3: Incomplete Feature Detection

**Function:** `detect_incomplete_features()`

```bash
detect_incomplete_features() {
    local incomplete_dir="$TREES_DIR/.incomplete"
    local features=()

    if [ ! -d "$incomplete_dir" ]; then
        return 0
    fi

    # Find all incomplete synopses
    while IFS= read -r synopsis_file; do
        # Verify it's marked incomplete
        if grep -q "^# Status: INCOMPLETE" "$synopsis_file"; then
            # Extract description
            local desc=$(sed -n '/^## Original Task Description/,/^##/p' "$synopsis_file" | \
                        grep -v "^##" | head -n 1)

            features+=("$desc")
        fi
    done < <(find "$incomplete_dir" -name "*-synopsis-*.md")

    echo "${features[@]}"
}
```

---

## Error Handling & Rollback

### Checkpoint System

**Before each major operation:**
1. Create git tag: `checkpoint-[operation]-[timestamp]`
2. Store current branch in temp file
3. Log operation to `.git/.cycle-operations.log`

### Rollback Strategy

```bash
rollback_cycle() {
    local failed_phase=$1
    local checkpoint_tag=$2

    print_error "Phase $failed_phase failed - rolling back"

    # Find last checkpoint
    if [ -n "$checkpoint_tag" ]; then
        git reset --hard "$checkpoint_tag"
        git tag -d "$checkpoint_tag"
    fi

    # Restore branch state
    if [ -f "/tmp/cycle-branch-backup" ]; then
        local original_branch=$(cat /tmp/cycle-branch-backup)
        git checkout "$original_branch"
    fi

    print_warning "Rolled back to checkpoint: $checkpoint_tag"
    print_info "Manual recovery instructions:"
    echo "  1. Review git log for partial changes"
    echo "  2. Run: /tree closedone --dry-run to preview"
    echo "  3. Fix issues and retry"
}
```

### Failure Scenarios

| Phase | Failure | Rollback Action |
|-------|---------|----------------|
| 1 | Unclosed worktrees | Stop, report which worktrees need closing |
| 2 | Merge conflicts | Abort merge, preserve dev branch, manual resolution |
| 3 | Main merge fails | Reset main to pre-merge, preserve dev branch |
| 4 | Version bump fails | Reset main, restore previous version |
| 5 | New branch creation fails | Delete partial branch, restore dev branch |
| 6 | Archive fails | Continue, report failure (non-critical) |

---

## Testing Strategy

### Unit Tests

1. **Test `/tree close incomplete`**
   - Verify synopsis saved to `.incomplete/`
   - Check status flag set correctly
   - Confirm task description extracted

2. **Test incomplete detection**
   - Create mock incomplete synopses
   - Verify detection function finds them
   - Check description extraction

3. **Test phase execution**
   - Each phase isolated
   - Mock git operations
   - Verify state changes

### Integration Tests

1. **End-to-end cycle test**
   - Stage 2 features (1 complete, 1 incomplete)
   - Build worktrees
   - Close both (one normal, one incomplete)
   - Run full cycle
   - Verify: main updated, version bumped, incomplete re-staged

2. **Rollback test**
   - Inject failure at each phase
   - Verify rollback executes
   - Check state restored correctly

3. **Dry-run test**
   - Run `--dry-run` mode
   - Verify no actual changes made
   - Check preview output accurate

### Manual Testing Checklist

- [ ] `/tree close` still works (backward compatibility)
- [ ] `/tree close incomplete` creates correct synopsis
- [ ] `/tree closedone` still works (backward compatibility)
- [ ] `/tree closedone --full-cycle` completes all phases
- [ ] Incomplete features auto-staged in new cycle
- [ ] Dev branch preserved and pushed
- [ ] Main branch updated correctly
- [ ] Version bumped and synced
- [ ] Error handling works at each phase
- [ ] `--dry-run` mode accurate
- [ ] `--yes` mode skips confirmations

---

## Documentation Updates

### Files to Update

1. **`.claude/commands/tree.md`**
   - Add `/tree close incomplete` usage
   - Add `/tree closedone --full-cycle` usage
   - Update workflow examples

2. **`tasks/prd-tree-slash-command.md`**
   - Add full-cycle workflow section
   - Update directory structure diagrams
   - Add incomplete feature documentation

3. **`.claude/scripts/tree.sh`** (inline docs)
   - Function docstrings
   - Usage examples in help text

4. **`CLAUDE.md`** (if applicable)
   - Update worktree workflow section
   - Add full-cycle automation notes

---

## Migration & Backward Compatibility

### Backward Compatibility

✅ Existing `/tree close` behavior unchanged
✅ Existing `/tree closedone` behavior unchanged
✅ New features opt-in only
✅ No breaking changes to file formats

### Migration

**For users with existing completed worktrees:**
1. No action required
2. System continues working as before
3. New features available immediately

**For incomplete features:**
1. Manually run `/tree close incomplete` for partial work
2. Or continue using existing workflow

---

## Success Metrics

### Performance Metrics

- Full cycle execution time: < 5 minutes (excluding test suite)
- Rollback time: < 30 seconds
- Incomplete detection: < 1 second

### Reliability Metrics

- Success rate: > 95% (with proper git state)
- Rollback success: 100%
- Zero data loss on failures

### User Experience Metrics

- Manual steps reduced: 8 → 1 (87.5% reduction)
- Context loss prevention: 100% (incomplete features tracked)
- Error recovery: Automated (vs manual)

---

## Future Enhancements (Out of Scope)

1. **Interactive conflict resolution** during merge
2. **Automated testing** during full-cycle
3. **Slack/email notifications** on cycle completion
4. **Web dashboard** for cycle history
5. **AI-powered** incomplete feature prioritization
6. **Multi-repository** cycle coordination

---

## Appendix

### Example Usage

#### Example 1: Mark Feature Incomplete
```bash
# In worktree
cd /workspace/.trees/my-feature
/tree close incomplete

# Output:
# 🌳 Completing Work: my-feature
# Worktree: my-feature
# Branch: task/01-my-feature
# Base: develop/v4.3.2-worktrees-20251012-044136
#
# ⚠ INCOMPLETE - This feature will continue in next cycle
# ✓ Synopsis generated: .trees/.incomplete/my-feature-synopsis-20251012-150000.md
```

#### Example 2: Run Full Cycle
```bash
# In main workspace
cd /workspace
/tree closedone --full-cycle --bump minor

# Output:
# 🌳 /tree closedone - Full Development Cycle
#
# Phase 1: Validate & Checkpoint
# ✓ All worktrees closed (2 complete, 1 incomplete)
# ✓ Checkpoint created
#
# Phase 2: Merge Completed Features
# ✓ Merged 2 worktrees into develop/v4.3.2-worktrees-20251012-044136
# ✓ Pushed develop branch
#
# Phase 3: Promote to Main
# ✓ Merged to main
# ✓ Pushed main
#
# Phase 4: Version Bump
# ✓ Version: 4.3.2 → 4.4.0 (minor)
# ✓ Committed and pushed
#
# Phase 5: New Cycle Setup
# ✓ Created develop/v4.4.0-worktrees-20251012-151000
# ✓ Staged 1 incomplete feature
#
# Phase 6: Cleanup & Report
# ✓ Archived synopses to .archived/cycle-20251012-151000
#
# ═══════════════════════════════════════════════
# CYCLE COMPLETE
#
# New Dev Branch: develop/v4.4.0-worktrees-20251012-151000
# Version: 4.4.0
# Staged Features: 1 (from incomplete)
#
# Next Steps:
#   • /tree stage [description] - Add more features
#   • /tree build - Create new worktrees
# ═══════════════════════════════════════════════
```

#### Example 3: Dry Run
```bash
/tree closedone --full-cycle --dry-run

# Output:
# 🌳 /tree closedone - Full Development Cycle (DRY RUN)
#
# [DRY RUN] Phase 1: Would validate and checkpoint
# [DRY RUN] Phase 2: Would merge 2 completed worktrees
# [DRY RUN] Phase 3: Would merge to main and push
# [DRY RUN] Phase 4: Would bump version (patch)
# [DRY RUN] Phase 5: Would create new dev branch
# [DRY RUN] Phase 6: Would stage 1 incomplete feature
# [DRY RUN] Phase 7: Would archive and cleanup
#
# No changes made (dry run mode)
```

---

## Approval & Sign-off

**Approved by:** AI Agent (Autonomous Workflow)
**Date:** 2025-10-12
**Next Step:** Generate task list and begin implementation

---
