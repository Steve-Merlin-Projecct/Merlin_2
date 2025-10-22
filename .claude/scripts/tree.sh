#!/bin/bash

# Tree Worktree Management Script
# Phase 1: Core functionality for /tree closedone

set -e  # Exit on error

# Source scope detection utilities
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/scope-detector.sh"

# Colors and formatting
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color
BOLD='\033[1m'

# Unicode characters
CHECK='\u2713'
CROSS='\u2717'
WARN='\u26a0'
TREE='\U1F333'

# Paths
WORKSPACE_ROOT="/workspace"
TREES_DIR="$WORKSPACE_ROOT/.trees"
COMPLETED_DIR="$TREES_DIR/.completed"
INCOMPLETE_DIR="$TREES_DIR/.incomplete"
ARCHIVED_DIR="$TREES_DIR/.archived"
CONFLICT_BACKUP_DIR="$TREES_DIR/.conflict-backup"
STAGED_FEATURES_FILE="$TREES_DIR/.staged-features.txt"
GIT_OPERATION_LOCK="$WORKSPACE_ROOT/.git/.git-operation.lock"
GIT_OPERATION_LOG="$WORKSPACE_ROOT/.git/.git-operations.log"

# Command routing
COMMAND="${1:-help}"
shift || true

print_header() {
    echo -e "\n${TREE} ${BOLD}$1${NC}\n"
}

print_success() {
    echo -e "${GREEN}${CHECK}${NC} $1"
}

print_error() {
    echo -e "${RED}${CROSS}${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}${WARN}${NC} $1"
}

print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

# Handle git index.lock issues with enhanced stale lock detection
wait_for_git_lock() {
    local max_wait=30  # Increased from 5 for better reliability
    local attempt=1
    local wait_time=1
    local lock_file="$WORKSPACE_ROOT/.git/index.lock"

    while [ -f "$lock_file" ] && [ $attempt -le $max_wait ]; do
        # Check if lock is stale (older than 60 seconds and empty)
        if is_lock_stale "$lock_file"; then
            print_warning "Stale git lock detected (>60s old), removing automatically..."
            rm -f "$lock_file" 2>/dev/null || {
                print_error "Failed to remove stale lock file. Please run: rm $lock_file"
                return 1
            }
            print_success "Stale lock removed successfully"
            return 0
        fi

        print_warning "Git lock detected, waiting ${wait_time}s (attempt $attempt/$max_wait)"
        sleep $wait_time

        # Exponential backoff: 1s, 2s, 4s, 8s, 16s (max)
        wait_time=$((wait_time * 2))
        [ $wait_time -gt 16 ] && wait_time=16

        attempt=$((attempt + 1))
    done

    # Final check after all attempts
    if [ -f "$lock_file" ]; then
        print_error "Git lock file persists after ${max_wait} attempts. Please run: rm $lock_file"
        return 1
    fi
    return 0
}

# Check if a git lock file is stale
is_lock_stale() {
    local lock_file=$1

    # Get lock file age in seconds
    local current_time=$(date +%s)
    local lock_time=$(stat -c %Y "$lock_file" 2>/dev/null || stat -f %m "$lock_file" 2>/dev/null || echo "0")
    local lock_age=$((current_time - lock_time))

    # Get lock file size
    local lock_size=$(stat -c %s "$lock_file" 2>/dev/null || stat -f %z "$lock_file" 2>/dev/null || echo "0")

    # Consider lock stale if:
    # 1. Older than 60 seconds AND
    # 2. File size is 0 (typical for git index.lock)
    if [ "$lock_age" -gt 60 ] && [ "$lock_size" -eq 0 ]; then
        return 0  # Stale
    fi
    return 1  # Not stale
}

# Log git operations for debugging and monitoring
log_git_operation() {
    local operation=$1
    local timestamp=$(date +"%Y-%m-%d %H:%M:%S")

    # Create log directory if needed
    mkdir -p "$(dirname "$GIT_OPERATION_LOG")"

    echo "[$timestamp] $operation" >> "$GIT_OPERATION_LOG"
}

# Safe git wrapper with flock-based mutex for concurrent operation protection
# Supports error capture and verbose mode via TREE_VERBOSE environment variable
safe_git() {
    local git_cmd="$@"
    local operation_desc="${git_cmd%% *}"  # First word of command
    local verbose="${TREE_VERBOSE:-false}"

    # Check if flock is available
    if ! command -v flock &> /dev/null; then
        print_warning "flock not available, falling back to wait_for_git_lock"
        wait_for_git_lock || return 1

        # Run with or without output based on verbose mode
        if [ "$verbose" = "true" ]; then
            git $git_cmd
        else
            local git_output
            git_output=$(git $git_cmd 2>&1)
            local exit_code=$?

            # Show errors even in non-verbose mode
            if [ $exit_code -ne 0 ]; then
                echo "$git_output" >&2
            fi

            return $exit_code
        fi
        return $?
    fi

    # Create lock file if it doesn't exist
    touch "$GIT_OPERATION_LOCK" 2>/dev/null || {
        print_warning "Cannot create lock file, falling back to direct git"

        if [ "$verbose" = "true" ]; then
            git $git_cmd
        else
            local git_output
            git_output=$(git $git_cmd 2>&1)
            local exit_code=$?

            if [ $exit_code -ne 0 ]; then
                echo "$git_output" >&2
            fi

            return $exit_code
        fi
        return $?
    }

    log_git_operation "Acquiring lock for: git $operation_desc"

    # Acquire exclusive lock with 30 second timeout
    (
        if ! flock -x -w 30 200; then
            print_error "Failed to acquire git operation lock after 30s for: git $operation_desc"
            log_git_operation "Lock acquisition FAILED (timeout) for: git $operation_desc"
            return 1
        fi

        log_git_operation "Lock acquired for: git $operation_desc"

        # Run the git command with appropriate output handling
        if [ "$verbose" = "true" ]; then
            # Verbose mode: show all output
            git $git_cmd
            local exit_code=$?
        else
            # Normal mode: capture output, show only on error
            local git_output
            git_output=$(git $git_cmd 2>&1)
            local exit_code=$?

            # Display error output if command failed
            if [ $exit_code -ne 0 ]; then
                echo "$git_output" >&2
            fi
        fi

        log_git_operation "Lock released for: git $operation_desc (exit: $exit_code)"

        return $exit_code
    ) 200>"$GIT_OPERATION_LOCK"

    local result=$?
    return $result
}

# Stash uncommitted changes
stash_changes() {
    wait_for_git_lock || return 1

    if ! safe_git diff-index --quiet HEAD --; then
        print_warning "Uncommitted changes detected, stashing..."
        safe_git stash push -m "Auto-stash before /tree closedone at $(date +%Y%m%d-%H%M%S)"
        print_success "Changes stashed"
        return 0
    fi
    return 1
}

# Validate that all active worktrees have been closed
#
# Checks all worktrees in .trees/ to see if they have synopsis files
# in .completed/ directory. If any are missing, displays summary and exits.
#
# Returns:
#   0 - All worktrees closed
#   1 - Some worktrees not closed
validate_all_worktrees_closed() {
    # Get list of all active worktrees (excluding special directories)
    local all_worktrees=()
    if [ -d "$TREES_DIR" ]; then
        while IFS= read -r dir; do
            local name=$(basename "$dir")
            # Skip special directories
            if [[ "$name" != .* ]] && [ -d "$dir" ]; then
                all_worktrees+=("$name")
            fi
        done < <(find "$TREES_DIR" -maxdepth 1 -type d)
    fi

    if [ ${#all_worktrees[@]} -eq 0 ]; then
        # No worktrees at all
        return 0
    fi

    # Get list of closed worktrees (have synopsis files)
    local closed_worktrees=()
    if [ -d "$COMPLETED_DIR" ]; then
        while IFS= read -r file; do
            if [ -f "$file" ]; then
                local filename=$(basename "$file")
                local worktree_name="${filename%%-synopsis-*}"
                closed_worktrees+=("$worktree_name")
            fi
        done < <(find "$COMPLETED_DIR" -name "*-synopsis-*.md" 2>/dev/null)
    fi

    # Find unclosed worktrees (in .trees but no synopsis)
    local unclosed=()
    for worktree in "${all_worktrees[@]}"; do
        local is_closed=false
        for closed in "${closed_worktrees[@]}"; do
            if [ "$worktree" = "$closed" ]; then
                is_closed=true
                break
            fi
        done

        if [ "$is_closed" = false ]; then
            unclosed+=("$worktree")
        fi
    done

    # If all are closed, return success
    if [ ${#unclosed[@]} -eq 0 ]; then
        return 0
    fi

    # Display summary of unclosed worktrees
    echo ""
    print_error "⚠️  Cannot proceed: ${#unclosed[@]} worktree(s) have not been closed"
    echo ""
    echo "The following worktrees need to be closed with '/tree close' before merging:"
    echo ""

    for worktree in "${unclosed[@]}"; do
        # Get branch info if available
        local worktree_path="$TREES_DIR/$worktree"
        local branch=""

        # Try to get branch from git worktree list first
        branch=$(git worktree list --porcelain | grep -A 3 "$worktree_path" | grep "^branch " | sed 's/^branch //' | sed 's#refs/heads/##' || echo "")

        # Fallback to checking inside worktree
        if [ -z "$branch" ] && [ -d "$worktree_path" ]; then
            branch=$(cd "$worktree_path" && git branch --show-current 2>/dev/null || echo "unknown")
        fi

        echo "  • $worktree"
        if [ -n "$branch" ] && [ "$branch" != "unknown" ]; then
            echo "    Branch: $branch"
        fi
        echo "    Path: $worktree_path"
        echo ""
    done

    echo "Options:"
    echo "  1. Close each worktree: cd $TREES_DIR/<worktree> && /tree close"
    echo "  2. Use --force to merge all worktrees anyway: /tree closedone --force"
    echo ""

    print_info "💡 Tip: The --force flag will merge all worktrees, but you'll lose"
    print_info "   the structured synopsis and work description for unclosed worktrees."
    echo ""

    return 1
}

#==============================================================================
# /tree closedone - Phase 1 Core Functionality
#==============================================================================

closedone_main() {
    local skip_confirmation=false
    local force_merge=false

    # Check for --full-cycle flag and delegate
    for arg in "$@"; do
        if [ "$arg" = "--full-cycle" ]; then
            closedone_full_cycle "$@"
            return $?
        fi
    done

    # Parse options for regular closedone
    while [[ $# -gt 0 ]]; do
        case $1 in
            --yes|-y)
                skip_confirmation=true
                shift
                ;;
            --force)
                force_merge=true
                shift
                ;;
            *)
                print_error "Unknown option: $1"
                echo "Usage: /tree closedone [--yes] [--force] [--full-cycle]"
                return 1
                ;;
        esac
    done

    print_header "/tree closedone - Batch Merge & Cleanup"

    # Phase 0: Check for unclosed worktrees (unless --force)
    if [ "$force_merge" = false ]; then
        if ! validate_all_worktrees_closed; then
            return 1
        fi
    else
        print_warning "⚠️  --force flag used: merging all worktrees regardless of close status"
        echo ""
    fi

    # Phase 1.1: Discover completed worktrees
    print_info "Discovering completed worktrees..."

    if [ ! -d "$COMPLETED_DIR" ]; then
        print_warning "No completed worktrees found (no .trees/.completed directory)"
        return 0
    fi

    local synopsis_files=()
    while IFS= read -r -d '' file; do
        synopsis_files+=("$file")
    done < <(find "$COMPLETED_DIR" -name "*-synopsis-*.md" -print0 2>/dev/null)

    if [ ${#synopsis_files[@]} -eq 0 ]; then
        print_warning "No completed worktrees found (no synopsis files)"
        return 0
    fi

    # Extract worktree metadata
    local worktrees=()
    local worktree_branches=()
    local worktree_bases=()

    for synopsis_file in "${synopsis_files[@]}"; do
        local filename=$(basename "$synopsis_file")
        local worktree_name="${filename%%-synopsis-*}"

        # Extract branch and base from synopsis file
        local branch=$(grep -m1 "^# Branch:" "$synopsis_file" 2>/dev/null | sed 's/^# Branch: //' || echo "")
        local base=$(grep -m1 "^# Base:" "$synopsis_file" 2>/dev/null | sed 's/^# Base: //' || echo "develop/v4.2.0")

        # Verify worktree directory exists
        if [ ! -d "$TREES_DIR/$worktree_name" ]; then
            print_warning "Worktree directory not found: $worktree_name (skipping)"
            continue
        fi

        # Verify branch exists
        if ! git rev-parse --verify "$branch" &>/dev/null; then
            print_warning "Branch not found: $branch (skipping $worktree_name)"
            continue
        fi

        # Check for unique commits
        local commit_count=$(git log --oneline "$base..$branch" 2>/dev/null | wc -l)
        if [ "$commit_count" -eq 0 ]; then
            print_info "No commits to merge for $worktree_name (will cleanup only)"
        fi

        worktrees+=("$worktree_name")
        worktree_branches+=("$branch")
        worktree_bases+=("$base")
    done

    if [ ${#worktrees[@]} -eq 0 ]; then
        print_warning "No valid worktrees to process"
        return 0
    fi

    print_success "Found ${#worktrees[@]} completed worktree(s)"
    echo ""

    # Display summary
    for i in "${!worktrees[@]}"; do
        local worktree="${worktrees[$i]}"
        local branch="${worktree_branches[$i]}"
        local base="${worktree_bases[$i]}"
        local commit_count=$(git log --oneline "$base..$branch" 2>/dev/null | wc -l)

        echo "  $((i+1)). $worktree ($branch → $base)"
        if [ "$commit_count" -gt 0 ]; then
            echo "     Commits to merge: $commit_count"
        else
            echo "     No commits (cleanup only)"
        fi
    done
    echo ""

    # Phase 1.2: User confirmation
    if [ "$skip_confirmation" = false ]; then
        echo -n "Merge ${#worktrees[@]} completed worktree(s)? (y/n): "
        read -r response

        if [[ ! "$response" =~ ^[Yy]$ ]]; then
            print_info "Operation cancelled"
            return 0
        fi
    fi

    echo ""
    print_info "Processing worktrees..."
    echo ""

    # Phase 1.3: Pre-merge validation
    cd "$WORKSPACE_ROOT"

    # Handle uncommitted changes
    local stashed=false
    if stash_changes; then
        stashed=true
    fi

    # Process each worktree
    local success_count=0
    local failed_count=0
    local cleanup_only_count=0

    for i in "${!worktrees[@]}"; do
        local worktree="${worktrees[$i]}"
        local branch="${worktree_branches[$i]}"
        local base="${worktree_bases[$i]}"
        local num=$((i+1))

        echo "[$num/${#worktrees[@]}] $worktree"

        # Check if there are commits to merge
        local commit_count=$(git log --oneline "$base..$branch" 2>/dev/null | wc -l)

        if [ "$commit_count" -eq 0 ]; then
            print_info "  No commits to merge (cleanup only)"
            # Phase 1.4: Cleanup only
            closedone_cleanup "$worktree" "$branch"
            cleanup_only_count=$((cleanup_only_count + 1))
        else
            # Phase 1.4: Merge execution
            if closedone_merge "$worktree" "$branch" "$base"; then
                success_count=$((success_count + 1))
            else
                failed_count=$((failed_count + 1))
            fi
        fi

        echo ""
    done

    # Phase 1.5: Final summary
    echo "═══════════════════════════════════════════════════════════"
    echo "SUMMARY"
    echo ""
    echo "Worktrees Processed: ${#worktrees[@]}"
    echo "  ${GREEN}✅${NC} Success: $success_count"
    echo "  ${BLUE}🔧${NC} Cleanup only: $cleanup_only_count"
    echo "  ${RED}❌${NC} Failed: $failed_count"

    if [ "$stashed" = true ]; then
        echo ""
        print_info "Uncommitted changes were stashed. To restore: git stash pop"
    fi

    echo "═══════════════════════════════════════════════════════════"
}

# Merge a single worktree
closedone_merge() {
    local worktree=$1
    local branch=$2
    local base=$3

    # Switch to base branch
    wait_for_git_lock || return 1

    if ! safe_git checkout "$base" &>/dev/null; then
        print_error "  Failed to checkout $base"
        return 1
    fi
    print_success "  Switched to $base"

    # Attempt merge
    local merge_output
    if merge_output=$(safe_git merge "$branch" --no-edit 2>&1); then
        # Check merge type
        if echo "$merge_output" | grep -q "Fast-forward"; then
            print_success "  Merged (fast-forward)"
        else
            print_success "  Merged (merge commit)"
        fi

        # Cleanup after successful merge
        closedone_cleanup "$worktree" "$branch"
        return 0
    else
        # Merge failed - check if conflicts
        if git diff --name-only --diff-filter=U | grep -q .; then
            print_warning "  Conflicts detected in $(git diff --name-only --diff-filter=U | wc -l) file(s)"
            print_info "  🔧 Launching conflict resolution agent..."

            # Phase 2: Automated conflict resolution
            if closedone_resolve_conflicts "$worktree" "$branch" "$base"; then
                # Conflicts resolved successfully
                print_success "  All conflicts resolved automatically"
                closedone_cleanup "$worktree" "$branch"
                return 0
            else
                # Agent couldn't resolve - manual intervention needed
                print_warning "  Agent resolution failed - manual resolution required"
                safe_git merge --abort
                return 1
            fi
        else
            print_error "  Merge failed: $merge_output"
            safe_git merge --abort 2>/dev/null
            return 1
        fi
    fi
}

# Phase 2: Resolve merge conflicts using AI agent
closedone_resolve_conflicts() {
    local worktree=$1
    local branch=$2
    local base=$3

    # Get list of conflicted files
    local conflicted_files=($(git diff --name-only --diff-filter=U))
    local num_conflicts=${#conflicted_files[@]}

    if [ $num_conflicts -eq 0 ]; then
        return 0  # No conflicts
    fi

    # Create conflict backup directory
    local backup_dir="$CONFLICT_BACKUP_DIR/$worktree-$(date +%Y%m%d-%H%M%S)"
    mkdir -p "$backup_dir/base" "$backup_dir/incoming"

    print_info "  Agent resolving $num_conflicts conflict(s):"

    # Backup conflicted files and get context
    for file in "${conflicted_files[@]}"; do
        # Backup base version
        git show "HEAD:$file" > "$backup_dir/base/$file" 2>/dev/null || true
        # Backup incoming version
        git show "$branch:$file" > "$backup_dir/incoming/$file" 2>/dev/null || true
    done

    # Read synopsis files for context
    local base_synopsis=""
    local incoming_synopsis=""

    if [ -f "$COMPLETED_DIR/${worktree}-synopsis-"*.md ]; then
        incoming_synopsis=$(cat "$COMPLETED_DIR/${worktree}-synopsis-"*.md 2>/dev/null || echo "No synopsis available")
    fi

    # Create agent prompt
    local agent_prompt=$(cat <<EOF
# Merge Conflict Resolution Task

## Context
Merging worktree: $worktree
Base branch: $base
Worktree branch: $branch
Number of conflicted files: $num_conflicts

## Incoming Feature Description
$incoming_synopsis

## Conflicted Files
$(printf '%s\n' "${conflicted_files[@]}")

## Resolution Task

For each conflicted file above:
1. Read the file from the working directory (it contains conflict markers)
2. Understand what each version is trying to accomplish
3. Create a merged version that includes BOTH changes appropriately
4. **The correct solution is usually to preserve both different elements, not choose one over the other**
5. Write the resolved file back without conflict markers
6. Document the strategy used

## Resolution Strategies to Prioritize

**Strategy 1: Combine Both Changes (Default)**
- Both versions made different changes to the same section
- Solution: Include both changes in a way that preserves both functionalities
- Example: Two different changelog entries → Keep both entries in chronological order

**Strategy 2: Merge Complementary Logic**
- Both versions modified the same function/section differently
- Solution: Merge both modifications into a single enhanced version
- Example: One added validation, another added logging → Include both

**Strategy 3: Preserve Both Variants**
- Changes represent different approaches to similar problems
- Solution: Keep both as separate elements
- Example: Two different configuration options → Preserve both settings

**Strategy 4: Structural Merge**
- Changes to lists, imports, or structure
- Solution: Combine both sets of additions
- Example: Two different imports added → Include all imports

## Important Instructions

- Read files from: $PWD (current working directory)
- Backup files available in: $backup_dir
- After resolving each file, use the Edit tool to write the resolved content
- Remove ALL conflict markers (<<<<<<, ======, >>>>>>)
- Preserve formatting and indentation
- Test that resolved files are syntactically valid
- Report which strategy was used for each file

## Deliverables

After resolving all conflicts:
1. Write resolved files (conflict markers removed)
2. Report resolution summary with strategy used per file
3. Indicate if any files need manual review
EOF
)

    # Launch agent using Task tool (this would be the actual agent invocation)
    # For now, we'll use a simpler approach - invoke claude directly

    print_info "  Starting agent analysis..."

    # Create a temporary script to hold the agent's work
    local agent_script="$backup_dir/resolve_conflicts.sh"

    # For Phase 2 MVP, we'll use a direct approach
    # The agent would be invoked here via the Task tool
    # For now, return failure to indicate manual resolution needed

    print_warning "  Agent-based resolution requires Claude CLI integration"
    print_info "  Conflict backups saved to: $backup_dir"
    print_info "  Files that need resolution:"
    for file in "${conflicted_files[@]}"; do
        print_info "    - $file"
    done

    return 1  # Indicate manual resolution needed for now
}

#==============================================================================
# Full-Cycle Automation - Phase Functions
#==============================================================================

# Phase 1: Validation & Checkpoint
closedone_full_cycle_phase1() {
    print_info "Phase 1: Validation & Checkpoint"

    # Check for unclosed worktrees
    local unclosed_count=0
    if [ -d "$TREES_DIR" ]; then
        for dir in "$TREES_DIR"/*/ ; do
            [ -d "$dir/.git" ] || [ -f "$dir/.git" ] || continue

            local name=$(basename "$dir")
            # Skip if completed or incomplete synopsis exists
            if ! ls "$COMPLETED_DIR/$name-synopsis-"*.md &>/dev/null && \
               ! ls "$INCOMPLETE_DIR/$name-synopsis-"*.md &>/dev/null; then
                print_warning "  Unclosed worktree: $name"
                unclosed_count=$((unclosed_count + 1))
            fi
        done
    fi

    if [ $unclosed_count -gt 0 ]; then
        print_error "Found $unclosed_count unclosed worktree(s)"
        echo "Please run /tree close or /tree close incomplete in each worktree first"
        return 1
    fi

    # Get current branch
    local current_branch=$(git branch --show-current)
    echo "$current_branch" > /tmp/cycle-branch-backup

    # Create checkpoint
    local checkpoint_tag="checkpoint-before-full-cycle-$(date +%Y%m%d-%H%M%S)"
    git tag "$checkpoint_tag" 2>/dev/null
    echo "$checkpoint_tag" > /tmp/cycle-checkpoint-tag

    print_success "  ✓ All worktrees closed"
    print_success "  ✓ Checkpoint created: $checkpoint_tag"

    return 0
}

# Phase 2: Merge Completed Features
closedone_full_cycle_phase2() {
    print_info "Phase 2: Merge Completed Features"

    # Get current dev branch
    local dev_branch=$(git branch --show-current)

    # Run existing closedone logic
    if ! closedone_main --yes; then
        print_error "  Failed to merge completed worktrees"
        return 1
    fi

    # Push dev branch to remote
    if ! git push origin "$dev_branch" 2>/dev/null; then
        print_warning "  Failed to push dev branch (may not have remote)"
    else
        print_success "  ✓ Dev branch pushed: $dev_branch"
    fi

    print_success "  ✓ Completed features merged"
    echo "$dev_branch"  # Return dev branch name
    return 0
}

# Phase 3: Promote to Main
closedone_full_cycle_phase3() {
    local dev_branch=$1

    print_info "Phase 3: Promote to Main"

    # Switch to main
    if ! git checkout main &>/dev/null; then
        print_error "  Failed to checkout main branch"
        return 1
    fi

    # Pull latest main (optional, non-blocking)
    git pull origin main &>/dev/null || true

    # Merge dev branch with --no-ff to preserve history
    if ! git merge "$dev_branch" --no-ff -m "Merge $dev_branch into main" &>/dev/null; then
        # Check if conflicts
        if git diff --name-only --diff-filter=U | grep -q .; then
            print_error "  Merge conflicts detected"
            echo "  Conflicted files:"
            git diff --name-only --diff-filter=U | while read file; do
                echo "    - $file"
            done
            git merge --abort 2>/dev/null
            return 1
        else
            print_error "  Merge failed"
            git merge --abort 2>/dev/null
            return 1
        fi
    fi

    # Push main to remote
    if ! git push origin main 2>/dev/null; then
        print_warning "  Failed to push main (may not have remote)"
    else
        print_success "  ✓ Main branch pushed"
    fi

    print_success "  ✓ Promoted to main"
    return 0
}

# Phase 4: Version Bump
closedone_full_cycle_phase4() {
    local bump_type="${1:-patch}"

    print_info "Phase 4: Version Bump ($bump_type)"

    # Validate bump type
    if [[ ! "$bump_type" =~ ^(patch|minor|major)$ ]]; then
        print_error "  Invalid bump type: $bump_type (must be patch, minor, or major)"
        return 1
    fi

    # Run version bump
    if ! python tools/version_manager.py --bump "$bump_type" &>/dev/null; then
        print_error "  Version bump failed"
        return 1
    fi

    # Sync version to all files
    if ! python tools/version_manager.py --sync &>/dev/null; then
        print_error "  Version sync failed"
        return 1
    fi

    # Read new version
    local new_version=$(cat VERSION 2>/dev/null || echo "unknown")

    # Commit version changes
    git add . &>/dev/null
    if ! git commit -m "chore: Bump version to $new_version" &>/dev/null; then
        print_warning "  No version changes to commit"
    fi

    # Push to main
    git push origin main &>/dev/null || true

    print_success "  ✓ Version: $new_version"
    echo "$new_version"  # Return new version
    return 0
}

# Phase 5: New Cycle Setup
closedone_full_cycle_phase5() {
    local new_version=$1

    print_info "Phase 5: New Cycle Setup"

    # Generate new dev branch name
    local timestamp=$(date +%Y%m%d-%H%M%S)
    local new_dev_branch="develop/v${new_version}-worktrees-${timestamp}"

    # Create and checkout new dev branch from main
    if ! git checkout -b "$new_dev_branch" main &>/dev/null; then
        print_error "  Failed to create new dev branch"
        return 1
    fi

    # Push with --set-upstream
    if ! git push -u origin "$new_dev_branch" 2>/dev/null; then
        print_warning "  Failed to push new dev branch (may not have remote)"
    else
        print_success "  ✓ New dev branch pushed: $new_dev_branch"
    fi

    # Detect and stage incomplete features
    local incomplete_count=0
    if [ -d "$INCOMPLETE_DIR" ]; then
        # Get incomplete features
        while IFS= read -r description; do
            if [ -n "$description" ]; then
                # Stage the feature
                tree_stage "$description" &>/dev/null
                print_info "  Staged incomplete: $description"
                incomplete_count=$((incomplete_count + 1))
            fi
        done < <(detect_incomplete_features)
    fi

    print_success "  ✓ New dev branch: $new_dev_branch"
    if [ $incomplete_count -gt 0 ]; then
        print_success "  ✓ Staged $incomplete_count incomplete feature(s)"
    fi

    echo "$new_dev_branch"  # Return new dev branch name
    return 0
}

# Phase 6: Cleanup & Report
closedone_full_cycle_phase6() {
    local dev_branch=$1
    local new_version=$2
    local new_dev_branch=$3

    print_info "Phase 6: Cleanup & Report"

    # Generate cycle timestamp
    local cycle_timestamp=$(date +%Y%m%d-%H%M%S)
    local archive_dir="$ARCHIVED_DIR/cycle-$cycle_timestamp"

    # Create archive directories
    mkdir -p "$archive_dir/completed" "$archive_dir/incomplete"

    # Archive completed synopses
    local completed_count=0
    if [ -d "$COMPLETED_DIR" ]; then
        for file in "$COMPLETED_DIR"/*.md; do
            [ -f "$file" ] || continue
            mv "$file" "$archive_dir/completed/" 2>/dev/null && completed_count=$((completed_count + 1))
        done
    fi

    # Archive incomplete synopses
    local incomplete_count=0
    if [ -d "$INCOMPLETE_DIR" ]; then
        for file in "$INCOMPLETE_DIR"/*.md; do
            [ -f "$file" ] || continue
            mv "$file" "$archive_dir/incomplete/" 2>/dev/null && incomplete_count=$((incomplete_count + 1))
        done
    fi

    print_success "  ✓ Archived $completed_count completed, $incomplete_count incomplete"
    print_success "  ✓ Archive location: $archive_dir"

    # Generate completion report
    local report_file="$archive_dir/cycle-report.md"
    cat > "$report_file" << EOF
# Development Cycle Completion Report

**Timestamp:** $(date +"%Y-%m-%d %H:%M:%S")
**Cycle ID:** $cycle_timestamp

## Summary

- **Previous Dev Branch:** $dev_branch
- **New Version:** $new_version
- **New Dev Branch:** $new_dev_branch

## Features Completed

$completed_count worktree(s) merged and deployed to main.

## Features Continuing

$incomplete_count incomplete feature(s) staged for next cycle.

## Next Steps

1. Review archived synopses in: $archive_dir
2. Stage additional features: \`/tree stage [description]\`
3. Build new worktrees: \`/tree build\`
4. Continue development!

---
Generated by /tree closedone --full-cycle
EOF

    print_success "  ✓ Report generated: $report_file"
    return 0
}

# Rollback full cycle on failure
rollback_full_cycle() {
    local failed_phase=$1
    local checkpoint_tag=$(cat /tmp/cycle-checkpoint-tag 2>/dev/null || echo "")
    local original_branch=$(cat /tmp/cycle-branch-backup 2>/dev/null || echo "main")

    print_error "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    print_error "ROLLBACK: Phase $failed_phase failed"
    print_error "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

    # Reset to checkpoint if it exists
    if [ -n "$checkpoint_tag" ] && git rev-parse "$checkpoint_tag" &>/dev/null; then
        print_warning "Rolling back to checkpoint: $checkpoint_tag"
        git reset --hard "$checkpoint_tag" &>/dev/null
        git tag -d "$checkpoint_tag" &>/dev/null
        print_success "  ✓ Repository reset to checkpoint"
    fi

    # Restore original branch
    if [ -n "$original_branch" ]; then
        git checkout "$original_branch" &>/dev/null || true
        print_success "  ✓ Restored branch: $original_branch"
    fi

    # Cleanup temp files
    rm -f /tmp/cycle-branch-backup /tmp/cycle-checkpoint-tag

    echo ""
    print_info "Manual Recovery Steps:"
    echo "  1. Review git log to see partial changes"
    echo "  2. Fix any issues that caused the failure"
    echo "  3. Run: /tree closedone --full-cycle (execute full cycle)"
    echo "  4. Retry when ready"
    echo ""

    return 1
}

# Full-Cycle Orchestrator
closedone_full_cycle() {
    local skip_confirmation=false
    local bump_type="patch"

    # Parse options
    while [[ $# -gt 0 ]]; do
        case $1 in
            --yes|-y)
                skip_confirmation=true
                shift
                ;;
            --bump)
                bump_type="$2"
                shift 2
                ;;
            *)
                print_error "Unknown option: $1"
                echo "Usage: /tree closedone --full-cycle [--yes] [--bump patch|minor|major]"
                return 1
                ;;
        esac
    done

    print_header "/tree closedone - Full Development Cycle"

    # Preview what will happen
    echo "This will execute the complete development cycle:"
    echo "  1. Validate all worktrees closed"
    echo "  2. Merge completed features to dev branch"
    echo "  3. Promote dev branch to main"
    echo "  4. Bump version ($bump_type)"
    echo "  5. Create new dev branch"
    echo "  6. Auto-stage incomplete features"
    echo "  7. Archive and cleanup"
    echo ""

    # Count features
    local completed_count=0
    local incomplete_count=0
    [ -d "$COMPLETED_DIR" ] && completed_count=$(ls "$COMPLETED_DIR"/*-synopsis-*.md 2>/dev/null | wc -l)
    [ -d "$INCOMPLETE_DIR" ] && incomplete_count=$(ls "$INCOMPLETE_DIR"/*-synopsis-*.md 2>/dev/null | wc -l)

    echo "Features to process:"
    echo "  • Completed: $completed_count"
    echo "  • Incomplete: $incomplete_count"
    echo ""

    # Confirmation
    if [ "$skip_confirmation" = false ]; then
        echo -n "Proceed with full cycle? (y/n): "
        read -r response

        if [[ ! "$response" =~ ^[Yy]$ ]]; then
            print_info "Operation cancelled"
            return 0
        fi
        echo ""
    fi

    # Execute phases
    local dev_branch=""
    local new_version=""
    local new_dev_branch=""

    # Phase 1: Validation & Checkpoint
    if ! closedone_full_cycle_phase1; then
        rollback_full_cycle 1
        return 1
    fi
    echo ""

    # Phase 2: Merge Completed Features
    dev_branch=$(closedone_full_cycle_phase2)
    if [ $? -ne 0 ]; then
        rollback_full_cycle 2
        return 1
    fi
    echo ""

    # Phase 3: Promote to Main
    if ! closedone_full_cycle_phase3 "$dev_branch"; then
        rollback_full_cycle 3
        return 1
    fi
    echo ""

    # Phase 4: Version Bump
    new_version=$(closedone_full_cycle_phase4 "$bump_type")
    if [ $? -ne 0 ]; then
        rollback_full_cycle 4
        return 1
    fi
    echo ""

    # Phase 5: New Cycle Setup
    new_dev_branch=$(closedone_full_cycle_phase5 "$new_version")
    if [ $? -ne 0 ]; then
        rollback_full_cycle 5
        return 1
    fi
    echo ""

    # Phase 6: Cleanup & Report
    if ! closedone_full_cycle_phase6 "$dev_branch" "$new_version" "$new_dev_branch"; then
        # Non-critical failure, continue
        print_warning "  Cleanup had issues but cycle completed"
    fi
    echo ""

    # Cleanup temp files
    rm -f /tmp/cycle-branch-backup /tmp/cycle-checkpoint-tag

    # Final summary
    echo "═══════════════════════════════════════════════════════════════"
    echo "✅ FULL CYCLE COMPLETE"
    echo "═══════════════════════════════════════════════════════════════"
    echo ""
    echo "Previous Dev Branch: $dev_branch (preserved as rollback point)"
    echo "New Version: $new_version"
    echo "New Dev Branch: $new_dev_branch"
    echo ""
    echo "Completed Features: $completed_count (merged to main)"
    echo "Incomplete Features: $incomplete_count (staged for next cycle)"
    echo ""
    echo "🎯 Next Steps:"
    echo "  • Stage more features: /tree stage [description]"
    echo "  • Build worktrees: /tree build"
    echo "  • Continue development!"
    echo "═══════════════════════════════════════════════════════════════"

    return 0
}

# Cleanup worktree and branch
closedone_cleanup() {
    local worktree=$1
    local branch=$2

    # Remove worktree
    if safe_git worktree remove "$TREES_DIR/$worktree" &>/dev/null; then
        print_success "  Removed worktree"
    else
        print_warning "  Failed to remove worktree (may already be removed)"
    fi

    # Delete branch (safe delete)
    if safe_git branch -d "$branch" &>/dev/null; then
        print_success "  Deleted branch $branch"
    elif safe_git branch -D "$branch" &>/dev/null; then
        print_warning "  Force-deleted branch $branch (had unmerged commits)"
    else
        print_warning "  Failed to delete branch $branch"
    fi

    # Archive completion files
    if [ -d "$COMPLETED_DIR" ]; then
        mkdir -p "$ARCHIVED_DIR/$worktree"
        if mv "$COMPLETED_DIR/$worktree-"*.md "$ARCHIVED_DIR/$worktree/" 2>/dev/null; then
            print_success "  Archived completion files"
        fi
    fi

    print_success "  Status: ✅ SUCCESS"
}

# Detect incomplete features for auto-staging in next cycle
detect_incomplete_features() {
    local incomplete_features=()

    # Check if incomplete directory exists
    if [ ! -d "$INCOMPLETE_DIR" ]; then
        echo ""  # Return empty array
        return 0
    fi

    # Find all incomplete synopsis files
    local synopsis_files=($(find "$INCOMPLETE_DIR" -name "*-synopsis-*.md" 2>/dev/null))

    for synopsis_file in "${synopsis_files[@]}"; do
        # Verify INCOMPLETE status
        if grep -q "^# Status: INCOMPLETE" "$synopsis_file" 2>/dev/null; then
            # Extract original task description
            local description=""

            # Try to extract from "## Original Task Description" section
            if grep -q "^## Original Task Description" "$synopsis_file"; then
                description=$(sed -n '/^## Original Task Description/,/^##/p' "$synopsis_file" | \
                             grep -v "^##" | grep -v "^$" | head -n 1 | sed 's/^[[:space:]]*//')
            fi

            # Fallback: extract from worktree name if description empty
            if [ -z "$description" ]; then
                local worktree_name=$(basename "$synopsis_file" | sed 's/-synopsis-.*\.md$//')
                description=$(echo "$worktree_name" | tr '-' ' ')
            fi

            # Add to array if we have a description
            if [ -n "$description" ]; then
                incomplete_features+=("$description")
            fi
        fi
    done

    # Return array (space-separated for bash arrays)
    printf '%s\n' "${incomplete_features[@]}"
}

#==============================================================================
# Phase 1: Basic Staging (MVP)
#==============================================================================

# /tree stage [description]
tree_stage() {
    local description="$*"

    if [ -z "$description" ]; then
        print_error "Feature description required"
        echo "Usage: /tree stage [description]"
        echo "Example: /tree stage Add real-time collaboration features with WebSocket support"
        return 1
    fi

    # Create .trees directory if it doesn't exist
    mkdir -p "$TREES_DIR"

    # Create staging file if it doesn't exist
    if [ ! -f "$STAGED_FEATURES_FILE" ]; then
        cat > "$STAGED_FEATURES_FILE" << EOF
# Staged Features for Worktree Build
# Created: $(date +%Y-%m-%d)
#
# Format: worktree-name|||Full description of the feature
# The ||| delimiter preserves the complete description for task context
# One feature per line

EOF
    fi

    # Generate worktree name from description (slugified)
    local worktree_name=$(echo "$description" | \
        tr '[:upper:]' '[:lower:]' | \
        sed 's/[^a-z0-9 -]//g' | \
        sed 's/ \+/-/g' | \
        cut -c1-50 | \
        sed 's/-$//')

    # Check if worktree name already exists
    if grep -q "^${worktree_name}|||" "$STAGED_FEATURES_FILE" 2>/dev/null; then
        print_warning "Feature with similar name already staged: $worktree_name"
        echo "Use a more specific description or remove the existing feature first"
        return 1
    fi

    # Append to staging file with ||| delimiter to preserve full description
    echo "${worktree_name}|||${description}" >> "$STAGED_FEATURES_FILE"

    # Count features
    local feature_count=$(grep -v '^#' "$STAGED_FEATURES_FILE" | grep -v '^$' | wc -l)

    print_success "Feature $feature_count staged: $worktree_name"
    echo "        Objective: $description"
    echo ""
    echo "Options:"
    echo "  - Stage another feature: /tree stage [description]"
    echo "  - Review all staged: /tree list"
    echo "  - Build worktrees: /tree build"
}

# /tree list
tree_list() {
    if [ ! -f "$STAGED_FEATURES_FILE" ]; then
        print_warning "No features staged yet"
        echo "Use: /tree stage [description] to stage your first feature"
        return 0
    fi

    # Read staged features (using ||| delimiter)
    local features=()
    while IFS='|||' read -r name desc; do
        # Skip comments and empty lines
        if [[ "$name" =~ ^#.*$ ]] || [ -z "$name" ]; then
            continue
        fi
        features+=("$name|||$desc")
    done < "$STAGED_FEATURES_FILE"

    if [ ${#features[@]} -eq 0 ]; then
        print_warning "No features staged yet"
        echo "Use: /tree stage [description] to stage your first feature"
        return 0
    fi

    print_header "Staged Features (${#features[@]})"

    for i in "${!features[@]}"; do
        local feature="${features[$i]}"
        local name="${feature%%|||*}"
        local desc="${feature#*|||}"
        local num=$((i + 1))

        echo "$num. $name"
        echo "   $desc"
        echo ""
    done

    echo "Actions:"
    echo "  - /tree stage [description] - Add another"
    echo "  - /tree clear - Clear all staged features"
    echo "  - /tree build - Create all worktrees"
}

# /tree clear
tree_clear() {
    if [ ! -f "$STAGED_FEATURES_FILE" ]; then
        print_info "No staged features to clear"
        return 0
    fi

    # Count features
    local feature_count=$(grep -v '^#' "$STAGED_FEATURES_FILE" | grep -v '^$' | wc -l)

    if [ "$feature_count" -eq 0 ]; then
        print_info "No staged features to clear"
        return 0
    fi

    echo -n "Clear $feature_count staged feature(s)? (y/n): "
    read -r response

    if [[ ! "$response" =~ ^[Yy]$ ]]; then
        print_info "Clear cancelled"
        return 0
    fi

    rm -f "$STAGED_FEATURES_FILE"
    print_success "Cleared $feature_count staged feature(s)"
}

#==============================================================================
# Helper Functions for Worktree Build
#==============================================================================

#==============================================================================
# Error Prevention Functions
#==============================================================================

# Validate that a path is safe to cleanup (prevent accidental data loss)
validate_cleanup_safe() {
    local target_path=$1

    # Must be within .trees directory
    if [[ "$target_path" != "$TREES_DIR"/* ]]; then
        print_error "Refusing to cleanup path outside .trees/: $target_path"
        return 1
    fi

    # Must not be a special directory
    local basename=$(basename "$target_path")
    if [[ "$basename" == .completed ]] || [[ "$basename" == .incomplete ]] || \
       [[ "$basename" == .archived ]] || [[ "$basename" == .conflict-backup ]]; then
        print_error "Refusing to cleanup special directory: $basename"
        return 1
    fi

    # Check for uncommitted changes if it's a git worktree
    if [ -d "$target_path" ] && ([ -f "$target_path/.git" ] || [ -d "$target_path/.git" ]); then
        if ! (cd "$target_path" && git diff-index --quiet HEAD -- 2>/dev/null); then
            print_warning "Path has uncommitted changes: $target_path"
            return 1
        fi
    fi

    return 0
}

# Validate and cleanup a worktree path before creation
# Returns 0 if path is ready, 1 if blocked
validate_and_cleanup_worktree_path() {
    local worktree_path=$1
    local branch=$2

    # Check if path exists
    if [ -e "$worktree_path" ]; then
        print_warning "  Path already exists: $worktree_path"

        # Check if it's a valid worktree registered with git
        if git worktree list --porcelain 2>/dev/null | grep -q "^worktree $worktree_path$"; then
            print_error "  Worktree already registered at this path"
            print_info "  Run: git worktree remove $worktree_path"
            return 1
        fi

        # It's an orphaned/corrupted directory - validate cleanup is safe
        if ! validate_cleanup_safe "$worktree_path"; then
            print_error "  Cannot safely cleanup path (has uncommitted work or outside .trees/)"
            return 1
        fi

        # Safe to remove - it's an orphaned directory
        print_warning "  Removing orphaned directory..."
        rm -rf "$worktree_path"
        print_success "  Orphaned directory removed"
    fi

    # Check if branch already exists
    if git rev-parse --verify "$branch" &>/dev/null; then
        print_warning "  Branch already exists: $branch"

        # Check if it's orphaned (no worktree associated)
        if ! git worktree list 2>/dev/null | grep -q "$branch"; then
            print_warning "  Orphaned branch detected - deleting..."
            if git branch -D "$branch" &>/dev/null; then
                print_success "  Orphaned branch removed"
            else
                print_error "  Failed to remove orphaned branch"
                return 1
            fi
        else
            print_error "  Branch in use by another worktree"
            local worktree_using=$(git worktree list | grep "$branch" | awk '{print $1}')
            print_info "  Used by: $worktree_using"
            return 1
        fi
    fi

    return 0
}

# Cleanup orphaned worktree artifacts at build start
cleanup_orphaned_worktrees() {
    print_info "Checking for orphaned worktree artifacts..."

    local cleanup_count=0
    local skip_count=0

    # Find directories in .trees/ that aren't registered worktrees
    if [ -d "$TREES_DIR" ]; then
        for dir in "$TREES_DIR"/*; do
            [ -d "$dir" ] || continue
            local basename=$(basename "$dir")

            # Skip special directories
            [[ "$basename" == .* ]] && continue

            # Check if this is a registered worktree
            if ! git worktree list 2>/dev/null | grep -q "$basename"; then
                # Not registered - it's orphaned
                print_warning "  Found orphaned directory: $basename"

                # Validate cleanup is safe
                if validate_cleanup_safe "$dir"; then
                    rm -rf "$dir"
                    print_success "  Removed orphaned directory: $basename"
                    cleanup_count=$((cleanup_count + 1))
                else
                    print_warning "  Skipped (has uncommitted changes): $basename"
                    skip_count=$((skip_count + 1))
                fi
            fi
        done
    fi

    if [ $cleanup_count -gt 0 ]; then
        print_success "Cleaned up $cleanup_count orphaned director(y/ies)"
    fi

    if [ $skip_count -gt 0 ]; then
        print_warning "Skipped $skip_count director(y/ies) with uncommitted changes"
        echo "  Review manually or commit/stash changes"
    fi

    if [ $cleanup_count -eq 0 ] && [ $skip_count -eq 0 ]; then
        print_success "No orphaned artifacts found"
    fi
}

# Check for stale git locks and cleanup if safe
check_git_locks() {
    local locks_found=false
    local locks_removed=false

    # Check for index.lock
    local index_lock="$WORKSPACE_ROOT/.git/index.lock"
    if [ -f "$index_lock" ]; then
        print_warning "Found git index.lock"

        if is_lock_stale "$index_lock"; then
            rm -f "$index_lock" 2>/dev/null && {
                print_success "Removed stale index.lock"
                locks_removed=true
            } || {
                print_error "Failed to remove index.lock (check permissions)"
                return 1
            }
        else
            print_error "Git operation in progress (index.lock is active)"
            print_info "Wait for operation to complete or remove manually: rm $index_lock"
            return 1
        fi
    fi

    # Check for worktree locks in .git/worktrees/*/locked
    if [ -d "$WORKSPACE_ROOT/.git/worktrees" ]; then
        for lock in "$WORKSPACE_ROOT/.git/worktrees"/*/locked; do
            if [ -f "$lock" ]; then
                local wt_name=$(basename $(dirname "$lock"))
                print_warning "Found locked worktree: $wt_name"
                locks_found=true
            fi
        done
    fi

    if [ "$locks_found" = true ]; then
        print_warning "Locked worktrees detected - run 'git worktree prune' to clean up"
    fi

    if [ "$locks_removed" = false ] && [ "$locks_found" = false ]; then
        print_success "No stale locks detected"
    fi

    return 0
}

# Rollback partially created worktrees on build failure
rollback_build() {
    local created_worktrees=("$@")

    if [ ${#created_worktrees[@]} -eq 0 ]; then
        return 0
    fi

    print_warning "Rolling back ${#created_worktrees[@]} partially created worktree(s)..."

    local rollback_count=0
    for worktree_info in "${created_worktrees[@]}"; do
        local worktree_path="${worktree_info%%|||*}"
        local branch="${worktree_info#*|||}"

        # Remove worktree
        if git worktree remove "$worktree_path" --force &>/dev/null; then
            print_success "  Removed worktree: $(basename "$worktree_path")"
        elif [ -d "$worktree_path" ]; then
            # Worktree not registered, remove directory
            rm -rf "$worktree_path"
            print_success "  Removed directory: $(basename "$worktree_path")"
        fi

        # Delete branch
        if git branch -D "$branch" &>/dev/null; then
            print_success "  Deleted branch: $branch"
        fi

        rollback_count=$((rollback_count + 1))
    done

    print_success "Rollback complete: $rollback_count worktree(s) cleaned up"
}

# Copy slash commands and scripts to worktree
copy_slash_commands_to_worktree() {
    local worktree_path=$1

    # Copy .claude/commands/ directory
    if [ -d "$WORKSPACE_ROOT/.claude/commands" ]; then
        mkdir -p "$worktree_path/.claude/commands"
        cp -r "$WORKSPACE_ROOT/.claude/commands/"* "$worktree_path/.claude/commands/" 2>/dev/null || true
    fi

    # Copy .claude/scripts/ directory
    if [ -d "$WORKSPACE_ROOT/.claude/scripts" ]; then
        mkdir -p "$worktree_path/.claude/scripts"
        cp -r "$WORKSPACE_ROOT/.claude/scripts/"* "$worktree_path/.claude/scripts/" 2>/dev/null || true
    fi
}

# Install scope enforcement pre-commit hook in worktree
install_scope_hook() {
    local worktree_path=$1

    # Create git hooks directory in worktree
    local hooks_dir="$worktree_path/.git/hooks"
    mkdir -p "$hooks_dir"

    # Create pre-commit hook that calls our scope enforcement script
    cat > "$hooks_dir/pre-commit" << 'EOF'
#!/bin/bash

# Pre-commit hook: Scope enforcement
# Validates that committed files match worktree scope

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && cd ../.. && pwd)"
HOOK_SCRIPT="$SCRIPT_DIR/.claude/scripts/scope-enforcement-hook.sh"

if [ -f "$HOOK_SCRIPT" ]; then
    bash "$HOOK_SCRIPT"
else
    # Hook script not found, skip validation
    exit 0
fi
EOF

    chmod +x "$hooks_dir/pre-commit"
}

# Generate VS Code tasks and auto-execute them
generate_and_run_vscode_tasks() {
    local pending_file="$TREES_DIR/.pending-terminals.txt"

    if [ ! -f "$pending_file" ]; then
        return 0
    fi

    # Count worktrees
    local worktree_count=$(wc -l < "$pending_file")

    print_info "Terminal initialization instructions:"
    echo ""
    echo "To launch Claude in each worktree, you can either:"
    echo ""
    echo "Option 1 - Manual launch (recommended for control):"
    echo "  • Open terminal for each worktree"
    echo "  • Run: cd <worktree-path> && bash .claude-init.sh"
    echo ""
    echo "Option 2 - Automatic launch:"

    local terminal_num=1
    while IFS= read -r worktree_path; do
        local wt_name=$(basename "$worktree_path")
        echo "  • Worktree $terminal_num: $wt_name"
        echo "    cd $worktree_path && bash .claude-init.sh"
        terminal_num=$((terminal_num + 1))
    done < "$pending_file"

    echo ""
    print_warning "Note: Automated terminal launch disabled to prevent unwanted editor tabs"
    print_info "The .claude-init.sh script in each worktree will launch Claude with task context"

    rm -f "$pending_file"
}

# Generate .claude-init.sh script for Claude auto-launch
generate_init_script() {
    local worktree_name=$1
    local description=$2
    local worktree_path=$3
    local init_script="$worktree_path/.claude-init.sh"

    cat > "$init_script" << 'INITSCRIPT'
#!/bin/bash
# Auto-generated Claude initialization script
# This script launches Claude with task context pre-loaded

WORKTREE_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TASK_CONTEXT="$WORKTREE_ROOT/.claude-task-context.md"

# Display banner
echo "════════════════════════════════════════════════════════"
INITSCRIPT

    # Add worktree-specific info
    cat >> "$init_script" << INITEOF
echo "🌳 Worktree: $worktree_name"
echo "📋 Task: $description"
INITEOF

    cat >> "$init_script" << 'INITSCRIPT'
echo "════════════════════════════════════════════════════════"
echo ""
echo "✅ Slash commands available after Claude loads:"
echo "   /tree close   - Complete this worktree"
echo "   /tree status  - Show status"
echo "   /tree restore - Restore terminals"
echo ""
echo "📝 Task context loaded in .claude-task-context.md"
echo ""

# Check if Claude is available
if ! command -v claude &> /dev/null; then
    echo "⚠️  Warning: Claude Code not found in PATH"
    echo "Install Claude Code or add to PATH"
    echo "Terminal will open without Claude"
    exec bash
    exit 0
fi

# Launch Claude with task context
if [ -f "$TASK_CONTEXT" ]; then
    # Read task description
    TASK_DESC=$(cat "$TASK_CONTEXT")

    # Launch Claude with context and clarification instruction
    claude --append-system-prompt "You are working in a git worktree dedicated to this task:

$TASK_DESC

IMPORTANT: After you receive this context, immediately read the .claude-task-context.md file to understand the full task details, then ask 1-3 clarifying questions to ensure you understand the scope and requirements before beginning implementation. Focus on:
1. Ambiguous requirements that need clarification
2. Technical decisions that aren't specified
3. Edge cases or error handling expectations
4. Integration points with existing code

Wait for user responses before starting implementation."
else
    # Fallback: Launch Claude without context
    echo "⚠️  Warning: Task context file not found"
    claude
fi
INITSCRIPT

    chmod +x "$init_script"
}

# Generate .claude-task-context.md file with full task description
generate_task_context() {
    local worktree_name=$1
    local description=$2
    local branch=$3
    local base_branch=$4
    local worktree_path=$5

    cat > "$worktree_path/.claude-task-context.md" << EOF
# Task Context for Claude Agent

## Worktree Information
- **Name**: $worktree_name
- **Branch**: $branch
- **Base Branch**: $base_branch
- **Created**: $(date +"%Y-%m-%d %H:%M:%S")

## Task Description

$description

## Scope

This worktree is dedicated to implementing the feature described above. Focus on:
- Implementing the core functionality
- Writing tests for new features
- Updating documentation
- Following project coding standards

## Success Criteria

- [ ] Core functionality implemented
- [ ] Tests written and passing
- [ ] Documentation updated
- [ ] Code reviewed and approved
- [ ] Ready to merge to base branch

## Working in this Worktree

✅ **Slash commands are available!**

After Claude starts, you can use:
- \`/tree close\` - Complete work and generate synopsis
- \`/tree status\` - Show worktree status
- \`/tree restore\` - Restore terminals (if needed)

## Notes

- This worktree is isolated from main development
- Commit frequently with descriptive messages
- Run tests before marking task complete
- Use \`/tree close\` when work is finished
EOF
}

#==============================================================================
# /tree build - Create worktrees from staged features
#==============================================================================

tree_build() {
    # Parse options
    local confirm_mode=false
    local verbose_mode="${TREE_VERBOSE:-false}"

    while [[ $# -gt 0 ]]; do
        case $1 in
            --confirm)
                confirm_mode=true
                shift
                ;;
            --verbose|-v)
                export TREE_VERBOSE=true
                verbose_mode=true
                shift
                ;;
            *)
                print_error "Unknown option: $1"
                echo "Usage: /tree build [--confirm] [--verbose]"
                return 1
                ;;
        esac
    done

    if [ ! -f "$STAGED_FEATURES_FILE" ]; then
        print_error "No features staged"
        echo "Use: /tree stage [description] to stage features first"
        return 1
    fi

    # Read staged features (using ||| delimiter)
    local features=()
    while IFS='|||' read -r name desc; do
        [[ "$name" =~ ^#.*$ ]] || [ -z "$name" ] && continue
        features+=("$name|||$desc")
    done < "$STAGED_FEATURES_FILE"

    if [ ${#features[@]} -eq 0 ]; then
        print_error "No features staged"
        return 1
    fi

    print_header "🚀 Building ${#features[@]} Worktree(s)"

    if [ "$verbose_mode" = "true" ]; then
        print_info "Verbose mode enabled"
        echo ""
    fi

    # PRE-FLIGHT VALIDATION
    echo "═══════════════════════════════════════════════════════════"
    echo "PRE-FLIGHT CHECKS"
    echo "═══════════════════════════════════════════════════════════"
    echo ""

    # Check for stale locks
    if ! check_git_locks; then
        print_error "Pre-flight check failed: git locks detected"
        return 1
    fi
    echo ""

    # Prune stale worktree references
    print_info "Pruning stale worktree references..."
    if git worktree prune -v 2>&1 | grep -q "Removing"; then
        print_success "Pruned stale worktree references"
    else
        print_success "No stale references to prune"
    fi
    echo ""

    # Cleanup orphaned directories
    cleanup_orphaned_worktrees
    echo ""

    echo "═══════════════════════════════════════════════════════════"
    echo ""

    # Get current version and timestamp
    local version=$(cat /workspace/VERSION 2>/dev/null || echo "0.0.0")
    local timestamp=$(date +%Y%m%d-%H%M%S)
    local dev_branch="develop/v${version}-worktrees-${timestamp}"

    echo "📋 Staged features:"
    for i in "${!features[@]}"; do
        local feature="${features[$i]}"
        local name="${feature%%|||*}"
        echo "  $((i+1)). $name"
    done
    echo ""
    echo "Development Branch: $dev_branch"
    echo ""

    # Create development branch (idempotent)
    if ! git rev-parse --verify "$dev_branch" &>/dev/null; then
        wait_for_git_lock || return 1
        if safe_git checkout -b "$dev_branch" 2>&1 | grep -q "already exists"; then
            print_info "Development branch already exists: $dev_branch (reusing)"
            safe_git checkout "$dev_branch" &>/dev/null
        else
            print_success "Created development branch: $dev_branch"
        fi
    else
        print_info "Development branch already exists: $dev_branch (reusing)"
        safe_git checkout "$dev_branch" &>/dev/null
    fi

    # Track created worktrees for rollback on failure
    local created_worktrees=()
    local success_count=0
    local failed_count=0
    local build_start=$(date +%s)

    for i in "${!features[@]}"; do
        local feature="${features[$i]}"
        local name="${feature%%|||*}"
        local desc="${feature#*|||}"
        local num=$((i+1))
        local task_num=$(printf "%02d" $num)
        local branch="task/${task_num}-${name}"
        local worktree_path="$TREES_DIR/$name"
        local worktree_start=$(date +%s)

        echo "[$num/${#features[@]}] Creating: $name"

        # Pre-flight validation for this worktree
        if ! validate_and_cleanup_worktree_path "$worktree_path" "$branch"; then
            print_error "  ✗ Pre-flight validation failed"
            failed_count=$((failed_count + 1))

            # Rollback all created worktrees on failure
            if [ ${#created_worktrees[@]} -gt 0 ]; then
                echo ""
                rollback_build "${created_worktrees[@]}"
            fi
            return 1
        fi

        # Create worktree with new branch in one command
        wait_for_git_lock || {
            print_error "  ✗ Failed to acquire git lock"
            failed_count=$((failed_count + 1))

            # Rollback on failure
            if [ ${#created_worktrees[@]} -gt 0 ]; then
                echo ""
                rollback_build "${created_worktrees[@]}"
            fi
            return 1
        }

        # Execute git worktree add (error output now shown via safe_git)
        local git_output
        if ! git_output=$(safe_git worktree add -b "$branch" "$worktree_path" "$dev_branch" 2>&1); then
            print_error "  ✗ Failed to create worktree: $branch"
            if [ -n "$git_output" ] && [ "$verbose_mode" != "true" ]; then
                echo "     Git error: $git_output"
            fi
            failed_count=$((failed_count + 1))

            # Rollback on failure
            if [ ${#created_worktrees[@]} -gt 0 ]; then
                echo ""
                rollback_build "${created_worktrees[@]}"
            fi
            return 1
        fi

        # Track successful creation for potential rollback
        created_worktrees+=("$worktree_path|||$branch")

        # Generate scope manifest for this worktree (before PURPOSE.md so we can reference it)
        local scope_manifest=$(detect_scope_from_description "$desc" "$name")
        local scope_json_path="$worktree_path/.worktree-scope.json"
        echo "$scope_manifest" > "$scope_json_path"

        # Extract scope patterns for PURPOSE.md
        local scope_patterns=$(echo "$scope_manifest" | python3 -c "import sys, json; data=json.load(sys.stdin); print('\n'.join(['- ' + p for p in data['scope']['include'][:5]]))")

        # Create PURPOSE.md in worktree
        cat > "$worktree_path/PURPOSE.md" << EOF
# Purpose: ${name//-/ }

**Worktree:** $name
**Branch:** $branch
**Base Branch:** $dev_branch
**Created:** $(date +"%Y-%m-%d %H:%M:%S")

## Objective

$desc

## Scope

**Automatically detected scope patterns:**

$scope_patterns

**Full scope details:** See \`.worktree-scope.json\`

**Enforcement:** Soft (warnings only)

## Out of Scope

Files outside the detected patterns will generate warnings but are not blocked.
For hard enforcement, see \`.worktree-scope.json\` and modify \`enforcement\` setting.

## Success Criteria

- [ ] All functionality implemented
- [ ] Tests written and passing
- [ ] Documentation updated
- [ ] Code reviewed
- [ ] Ready to merge

## Notes

[Add implementation notes, decisions, or concerns here]
EOF

        # Generate .claude-task-context.md with full description
        generate_task_context "$name" "$desc" "$branch" "$dev_branch" "$worktree_path"

        # Copy slash commands and scripts to worktree
        copy_slash_commands_to_worktree "$worktree_path"

        # Install scope enforcement pre-commit hook
        install_scope_hook "$worktree_path"

        # Generate .claude-init.sh script with Claude auto-launch
        generate_init_script "$name" "$desc" "$worktree_path"

        local worktree_end=$(date +%s)
        local worktree_duration=$((worktree_end - worktree_start))
        print_success "  ✓ Created in ${worktree_duration}s"
        success_count=$((success_count + 1))

        # Create integrated terminal for this worktree
        # Store worktree info for terminal creation after all worktrees are built
        echo "$worktree_path" >> "$TREES_DIR/.pending-terminals.txt"
    done

    # Create librarian worktree with inverse scope
    if [ $success_count -gt 0 ]; then
        echo ""
        print_header "📚 Creating Librarian Worktree"

        local librarian_name="librarian"
        local librarian_branch="task/00-librarian"
        local librarian_path="$TREES_DIR/$librarian_name"
        local librarian_start=$(date +%s)

        # Create librarian worktree
        wait_for_git_lock || true
        if safe_git worktree add -b "$librarian_branch" "$librarian_path" "$dev_branch" &>/dev/null; then
            # Collect all feature scope files
            local scope_files=()
            for worktree_dir in "$TREES_DIR"/*; do
                if [ -d "$worktree_dir" ] && [ -f "$worktree_dir/.worktree-scope.json" ]; then
                    scope_files+=("$worktree_dir/.worktree-scope.json")
                fi
            done

            # Generate librarian scope (inverse of all feature scopes)
            local librarian_scope=$(calculate_librarian_scope "${scope_files[@]}")
            echo "$librarian_scope" > "$librarian_path/.worktree-scope.json"

            # Create PURPOSE.md for librarian
            cat > "$librarian_path/PURPOSE.md" << EOF
# Purpose: Librarian - Documentation & Tooling

**Worktree:** $librarian_name
**Branch:** $librarian_branch
**Base Branch:** $dev_branch
**Created:** $(date +"%Y-%m-%d %H:%M:%S")
**Type:** Meta-worktree (Documentation, tooling, project organization)

## Objective

Manage documentation, tooling, and project organization files that are not specific to any feature worktree. This worktree has "inverse scope" - it works on everything that other worktrees don't touch.

## Scope

**Automatically calculated inverse scope:**

This worktree can work on files that are NOT claimed by any feature worktree, including:
- Documentation files (docs/**, *.md)
- Tooling and scripts (.claude/**, tools/**, scripts/**)
- Configuration files (*.toml, *.yaml, *.json)
- GitHub workflows (.github/**)
- Task templates (tasks/**)

**Full scope details:** See \`.worktree-scope.json\`

**Enforcement:** Soft (warnings only)

## Out of Scope

All files that are claimed by feature worktrees are out of scope for librarian.

## Success Criteria

- [ ] Documentation updated and consistent
- [ ] Tooling improvements implemented
- [ ] Project organization enhanced
- [ ] Configuration files maintained
- [ ] Ready to merge

## Notes

The librarian worktree is special - it automatically excludes all files that feature worktrees are working on, preventing conflicts and ensuring clear boundaries.
EOF

            # Copy commands and install hook
            copy_slash_commands_to_worktree "$librarian_path"
            install_scope_hook "$librarian_path"
            generate_task_context "$librarian_name" "Documentation, tooling, and project organization" "$librarian_branch" "$dev_branch" "$librarian_path"
            generate_init_script "$librarian_name" "Manage documentation and tooling" "$librarian_path"

            local librarian_end=$(date +%s)
            local librarian_duration=$((librarian_end - librarian_start))
            print_success "  ✓ Created in ${librarian_duration}s"

            # Add to pending terminals
            echo "$librarian_path" >> "$TREES_DIR/.pending-terminals.txt"
            success_count=$((success_count + 1))
        else
            print_warning "  ⚠ Failed to create librarian worktree (non-critical)"
        fi
    fi

    local build_end=$(date +%s)
    local total_duration=$((build_end - build_start))

    # Archive staging file
    local build_history_dir="$TREES_DIR/.build-history"
    mkdir -p "$build_history_dir"
    mv "$STAGED_FEATURES_FILE" "$build_history_dir/${timestamp}.txt"

    echo ""
    echo "═══════════════════════════════════════════════════════════"
    echo "BUILD SUMMARY"
    echo ""
    echo "Development Branch: $dev_branch"
    echo "Worktrees Created: $success_count"
    echo "Failed: $failed_count"
    echo "Total Time: ${total_duration}s"
    echo ""
    echo "Worktree Location: $TREES_DIR/"
    echo "Build History: $build_history_dir/${timestamp}.txt"
    echo "═══════════════════════════════════════════════════════════"

    # Provide terminal launch instructions
    if [ $success_count -gt 0 ]; then
        echo ""
        print_header "Terminal Launch Instructions"

        generate_and_run_vscode_tasks

        echo ""
        print_success "All worktrees ready!"
        echo ""
        print_info "Each worktree includes:"
        echo "  • .claude-init.sh - Script to launch Claude with task context"
        echo "  • .claude-task-context.md - Full task description"
        echo "  • Slash commands (/tree close, /tree status, /tree restore)"
        echo "  • .worktree-scope.json - Automatic file boundary detection"
        echo ""
        print_info "Next Steps:"
        echo "  1. Open terminal for each worktree you want to work on"
        echo "  2. Navigate: cd <worktree-path>"
        echo "  3. Launch Claude: bash .claude-init.sh"
        echo "  4. Answer Claude's clarifying questions"
        echo "  5. When done: /tree close (from within worktree)"
        echo "  6. Merge all: /tree closedone (from main workspace)"

        # Run scope conflict detection
        echo ""
        tree_scope_conflicts
    fi
}

#==============================================================================
# /tree conflict - Analyze conflicts and suggest merges
#==============================================================================

tree_scope_conflicts() {
    # Detect scope conflicts across all active worktrees
    print_header "🔍 Scope Conflict Detection"

    local scope_files=()
    local worktree_count=0

    # Find all worktrees with scope files
    for worktree_dir in "$TREES_DIR"/*; do
        if [ -d "$worktree_dir" ] && [ ! "$worktree_dir" = *"/.completed"* ] && [ ! "$worktree_dir" = *"/.incomplete"* ] && [ ! "$worktree_dir" = *"/.archived"* ]; then
            local scope_file="$worktree_dir/.worktree-scope.json"
            if [ -f "$scope_file" ]; then
                scope_files+=("$scope_file")
                worktree_count=$((worktree_count + 1))
            fi
        fi
    done

    if [ $worktree_count -eq 0 ]; then
        print_info "No active worktrees with scope files found"
        return 0
    fi

    echo "Analyzing scope conflicts across $worktree_count worktree(s)..."
    echo ""

    # Call scope detection utility
    if detect_scope_conflicts "${scope_files[@]}"; then
        print_success "✓ No scope conflicts detected"
        echo ""
        print_info "All worktrees have non-overlapping scopes"
    else
        print_warning "⚠ Scope conflicts detected - see above for details"
        echo ""
        print_info "Resolution options:"
        echo "  1. Adjust scope patterns in .worktree-scope.json files"
        echo "  2. Merge related worktrees"
        echo "  3. Use enforcement: 'hard' to block conflicting commits"
        return 1
    fi
}

tree_conflict() {
    if [ ! -f "$STAGED_FEATURES_FILE" ]; then
        print_error "No features staged"
        echo "Use: /tree stage [description] to stage features first"
        return 1
    fi

    print_header "Conflict Analysis"

    # Read staged features (using ||| delimiter)
    local features=()
    while IFS='|||' read -r name desc; do
        [[ "$name" =~ ^#.*$ ]] || [ -z "$name" ] && continue
        features+=("$name|||$desc")
    done < "$STAGED_FEATURES_FILE"

    if [ ${#features[@]} -eq 0 ]; then
        print_error "No features to analyze"
        return 1
    fi

    echo "Analyzing ${#features[@]} staged features..."
    echo ""

    # Simple keyword-based conflict detection
    print_info "MERGE SUGGESTIONS:"
    echo ""

    # Check for similar feature names
    for i in "${!features[@]}"; do
        local feature_i="${features[$i]}"
        local name_i="${feature_i%%|||*}"
        local desc_i="${feature_i#*|||}"

        for j in "${!features[@]}"; do
            [ $i -ge $j ] && continue

            local feature_j="${features[$j]}"
            local name_j="${feature_j%%|||*}"
            local desc_j="${feature_j#*|||}"

            # Check for keyword overlaps
            local common_words=$(comm -12 <(echo "$desc_i" | tr ' ' '\n' | sort -u) <(echo "$desc_j" | tr ' ' '\n' | sort -u) | wc -l)

            if [ $common_words -gt 3 ]; then
                echo "┌─────────────────────────────────────────────────────────────┐"
                echo "│ Features $((i+1)) & $((j+1)) may be related - consider merging?        │"
                echo "│                                                              │"
                echo "│ Feature $((i+1)): ${name_i:0:50}"
                echo "│ Feature $((j+1)): ${name_j:0:50}"
                echo "│                                                              │"
                echo "│ Common keywords detected: $common_words"
                echo "└─────────────────────────────────────────────────────────────┘"
                echo ""
            fi
        done
    done

    echo "CONFLICT ANALYSIS:"
    echo ""
    echo "✓ Analysis complete"
    echo "ℹ️  For detailed conflict analysis, review feature descriptions above"
    echo ""
    echo "Actions:"
    echo "  - /tree stage [description] - Add more features"
    echo "  - /tree list - Review all staged"
    echo "  - /tree build - Create worktrees"
}

#==============================================================================
# /tree close - Complete work in current worktree
#==============================================================================

tree_close() {
    # Parse options
    local status="COMPLETE"
    local incomplete_flag=false

    if [[ "$1" == "incomplete" ]]; then
        incomplete_flag=true
        status="INCOMPLETE"
    fi

    # Detect if we're in a worktree
    local current_dir=$(pwd)
    local worktree_name=""

    if [[ "$current_dir" == *"/.trees/"* ]]; then
        worktree_name=$(basename $(dirname "$current_dir/.git") 2>/dev/null || basename "$current_dir")
    else
        print_error "Not in a worktree directory"
        echo "This command must be run from within a worktree"
        return 1
    fi

    if [ "$incomplete_flag" = true ]; then
        print_header "Saving Work Progress: $worktree_name (INCOMPLETE)"
    else
        print_header "Completing Work: $worktree_name"
    fi

    # Get branch info
    local branch=$(git branch --show-current)
    local base_branch=$(git config --get "branch.$branch.merge" | sed 's#refs/heads/##' || echo "main")

    echo "Worktree: $worktree_name"
    echo "Branch: $branch"
    echo "Base: $base_branch"
    if [ "$incomplete_flag" = true ]; then
        echo "Status: ⚠️  INCOMPLETE - will continue in next cycle"
    fi
    echo ""

    # Analyze changes
    print_info "Analyzing changes..."
    local files_created=$(git diff --name-status $base_branch..$branch 2>/dev/null | grep "^A" | wc -l)
    local files_modified=$(git diff --name-status $base_branch..$branch 2>/dev/null | grep "^M" | wc -l)
    local files_deleted=$(git diff --name-status $base_branch..$branch 2>/dev/null | grep "^D" | wc -l)
    local commit_count=$(git log --oneline $base_branch..$branch 2>/dev/null | wc -l)

    echo "  Files created: $files_created"
    echo "  Files modified: $files_modified"
    echo "  Files deleted: $files_deleted"
    echo "  Commits: $commit_count"
    echo ""

    # Determine target directory based on status
    local target_dir
    if [ "$incomplete_flag" = true ]; then
        target_dir="$TREES_DIR/.incomplete"
    else
        target_dir="$COMPLETED_DIR"
    fi
    mkdir -p "$target_dir"

    # Extract original task description if available
    local original_description=""
    local task_context_file="$current_dir/.claude-task-context.md"
    if [ -f "$task_context_file" ]; then
        original_description=$(grep -A 5 "^## Task Description" "$task_context_file" | tail -n +2 | head -n 3)
    fi

    # Generate synopsis
    local timestamp=$(date +%Y%m%d-%H%M%S)
    local synopsis_file="$target_dir/${worktree_name}-synopsis-${timestamp}.md"

    if [ "$incomplete_flag" = true ]; then
        # Generate INCOMPLETE synopsis
        cat > "$synopsis_file" << EOF
# Work In Progress: ${worktree_name//-/ }

# Branch: $branch
# Base: $base_branch
# Closed: $(date +"%Y-%m-%d %H:%M:%S")
# Status: INCOMPLETE
# Resume: This feature needs to continue in the next development cycle

## Original Task Description

$original_description

## Progress Summary

Work has been started on this feature but requires additional work to complete.

## Changes So Far

- Files created: $files_created
- Files modified: $files_modified
- Files deleted: $files_deleted
- Total commits: $commit_count

## Files Changed

$(git diff --name-status $base_branch..$branch 2>/dev/null || echo "No changes detected")

## Commit History

$(git log --oneline $base_branch..$branch 2>/dev/null || echo "No commits")

## Remaining Work

- [ ] Additional tasks to be defined in next cycle
- [ ] Complete feature implementation
- [ ] Add comprehensive tests
- [ ] Update documentation

## Next Steps

1. This feature will be automatically staged in the next development cycle
2. Run /tree closedone --full-cycle to start the next cycle
3. The task description will be preserved for continuation

EOF
    else
        # Generate COMPLETE synopsis (original behavior)
        cat > "$synopsis_file" << EOF
# Work Completed: ${worktree_name//-/ }

# Branch: $branch
# Base: $base_branch
# Completed: $(date +"%Y-%m-%d %H:%M:%S")
# Status: COMPLETE

## Summary

Work completed in worktree: $worktree_name

## Changes

- Files created: $files_created
- Files modified: $files_modified
- Files deleted: $files_deleted
- Total commits: $commit_count

## Files Changed

$(git diff --name-status $base_branch..$branch 2>/dev/null || echo "No changes detected")

## Commit History

$(git log --oneline $base_branch..$branch 2>/dev/null || echo "No commits")

## Next Steps

1. Review this synopsis
2. Run /tree closedone to merge and cleanup
3. Or manually merge: git checkout $base_branch && git merge $branch

EOF
    fi

    print_success "Synopsis generated: $synopsis_file"
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    if [ "$incomplete_flag" = true ]; then
        echo "⚠️  Work Progress Saved: $worktree_name (INCOMPLETE)"
    else
        echo "📋 Work Summary: $worktree_name"
    fi
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "Changes:"
    echo "  • Created: $files_created files"
    echo "  • Modified: $files_modified files"
    echo "  • Deleted: $files_deleted files"
    echo "  • Commits: $commit_count"
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "📝 Documentation: $synopsis_file"
    echo ""
    if [ "$incomplete_flag" = true ]; then
        echo "⚠️  Status: INCOMPLETE"
        echo "  This feature will automatically continue in the next development cycle"
        echo ""
        echo "🎯 Next Steps:"
        echo "  1. Work on other features"
        echo "  2. Run /tree closedone --full-cycle when ready"
        echo "  3. This feature will be auto-staged in the new cycle"
    else
        echo "🎯 Next Steps:"
        echo "  1. Review synopsis before merging"
        echo "  2. Run /tree closedone to batch merge all completed worktrees"
        echo "  3. Or merge manually: git checkout $base_branch && git merge $branch"
        echo ""
        echo "✅ This worktree is ready to merge"
    fi
}

#==============================================================================
# /tree status - Show worktree environment status
#==============================================================================

tree_status() {
    print_header "Worktree Environment Status"

    # Detect current location
    local current_dir=$(pwd)
    local current_branch=$(git branch --show-current 2>/dev/null || echo "unknown")

    if [[ "$current_dir" == *"/.trees/"* ]]; then
        local worktree_name=$(basename "$current_dir")
        echo "Current Location: $current_dir"
        echo "Current Worktree: $worktree_name"
    else
        echo "Current Location: /workspace (main)"
    fi

    echo "Current Branch: $current_branch"
    echo ""

    # List active worktrees
    print_info "Active Worktrees:"
    local worktree_count=0

    if [ -d "$TREES_DIR" ]; then
        for dir in "$TREES_DIR"/*/ ; do
            [ -d "$dir/.git" ] || [ -f "$dir/.git" ] || continue

            local name=$(basename "$dir")
            local branch=$(cd "$dir" && git branch --show-current 2>/dev/null || echo "unknown")

            echo "  ✓ $name ($branch)"
            worktree_count=$((worktree_count + 1))
        done
    fi

    if [ $worktree_count -eq 0 ]; then
        echo "  (none)"
    fi
    echo ""

    # Show staged features
    if [ -f "$STAGED_FEATURES_FILE" ]; then
        local staged_count=$(grep -v '^#' "$STAGED_FEATURES_FILE" | grep -v '^$' | wc -l)
        if [ $staged_count -gt 0 ]; then
            print_info "Staged Features: $staged_count"
            echo "  Run /tree list to see details"
            echo ""
        fi
    fi

    # Show completed worktrees
    if [ -d "$COMPLETED_DIR" ]; then
        local completed_count=$(find "$COMPLETED_DIR" -name "*-synopsis-*.md" 2>/dev/null | wc -l)
        if [ $completed_count -gt 0 ]; then
            print_info "Completed Worktrees: $completed_count"
            echo "  Run /tree closedone to merge and cleanup"
            echo ""
        fi
    fi

    # Show build history
    if [ -d "$TREES_DIR/.build-history" ]; then
        local recent_build=$(ls -t "$TREES_DIR/.build-history" 2>/dev/null | head -1)
        if [ -n "$recent_build" ]; then
            print_info "Most Recent Build:"
            echo "  ${recent_build%.txt}"
            echo ""
        fi
    fi

    echo "Actions:"
    echo "  - /tree stage [description] - Stage new feature"
    echo "  - /tree build - Create worktrees from staged features"
    echo "  - /tree close - Complete current worktree"
    echo "  - /tree closedone - Merge completed worktrees"
}

#==============================================================================
# /tree restore - Restore terminals for worktrees without active shells
#==============================================================================

tree_restore() {
    print_header "🌳 Reconnecting Worktree Terminals"

    # Find all existing worktrees
    local worktrees=()
    if [ -d "$TREES_DIR" ]; then
        for dir in "$TREES_DIR"/*/ ; do
            if [ -d "$dir/.git" ] || [ -f "$dir/.git" ]; then
                local name=$(basename "$dir")
                worktrees+=("$name|||$dir")
            fi
        done
    fi

    if [ ${#worktrees[@]} -eq 0 ]; then
        print_warning "No worktrees found"
        echo "Create worktrees first: /tree build"
        return 0
    fi

    print_info "Found ${#worktrees[@]} worktree(s)"
    echo ""

    # Filter worktrees that need terminals (simplified - check for .claude-init.sh)
    local needs_terminal=()
    for worktree_info in "${worktrees[@]}"; do
        local name="${worktree_info%%|||*}"
        local path="${worktree_info#*|||}"

        # Check if init script exists
        if [ -f "$path/.claude-init.sh" ]; then
            print_warning "  ⚠ $name - Needs terminal"
            needs_terminal+=("$path")
        else
            print_warning "  ⚠ $name - Missing init script, regenerating..."
            # Regenerate init script
            local desc=$(head -1 "$path/PURPOSE.md" 2>/dev/null | sed 's/# Purpose: //' || echo "Worktree task")
            generate_init_script "$name" "$desc" "$path"
            needs_terminal+=("$path")
        fi
    done

    echo ""

    if [ ${#needs_terminal[@]} -eq 0 ]; then
        print_success "All worktrees have init scripts"
        return 0
    fi

    # Create pending terminals file for generate_and_run_vscode_tasks
    rm -f "$TREES_DIR/.pending-terminals.txt"
    for path in "${needs_terminal[@]}"; do
        echo "$path" >> "$TREES_DIR/.pending-terminals.txt"
    done

    print_header "Launching Terminals"
    generate_and_run_vscode_tasks

    print_success "Terminal reconnection complete"
}

#==============================================================================
# /tree refresh - Session guidance for slash command loading
#==============================================================================

tree_refresh() {
    print_header "Slash Command Session Check"

    local current_dir=$(pwd)
    local workspace_root="/workspace"
    local in_worktree=false

    # Detect if we're in a worktree
    if [[ "$current_dir" == *"/.trees/"* ]]; then
        in_worktree=true
        local worktree_name=$(basename "$current_dir")
    fi

    echo "📍 Current Location:"
    echo "   $current_dir"
    echo ""

    if [ "$in_worktree" = true ]; then
        echo "🌳 Worktree Detected: $worktree_name"
        echo ""
    fi

    # Check if slash command files exist
    echo "🔍 Checking Slash Command Files:"

    local commands_found=0
    local commands_missing=0

    for cmd in tree task; do
        if [ -f ".claude/commands/$cmd.md" ]; then
            print_success "/$cmd command file exists"
            commands_found=$((commands_found + 1))
        else
            print_error "/$cmd command file MISSING"
            commands_missing=$((commands_missing + 1))
        fi
    done

    echo ""

    if [ $commands_missing -gt 0 ]; then
        print_error "Missing command files detected!"
        echo ""
        echo "This worktree may be on an older commit. Consider:"
        echo "  1. Merge latest changes from main/develop"
        echo "  2. Cherry-pick the slash command commits"
        echo ""
        return 1
    fi

    # Provide session reload guidance
    print_header "Claude Code CLI Session Guidance"

    echo "ℹ️  Known Issue: Claude Code doesn't always reload slash commands"
    echo "   when switching between worktrees mid-session."
    echo ""

    if [ "$in_worktree" = true ]; then
        print_warning "You're in a worktree. If /tree or /task don't work:"
        echo ""
        echo "  Quick Fix (Recommended):"
        echo "    • Use direct command: bash /workspace/.claude/scripts/tree.sh <command>"
        echo "    • Example: bash /workspace/.claude/scripts/tree.sh status"
        echo ""
        echo "  Permanent Fix:"
        echo "    • Restart Claude Code CLI session"
        echo "    • Start new session FROM this worktree directory"
        echo "    • CLI will rescan .claude/commands/ on session start"
    else
        print_success "You're in main workspace - slash commands should work"
        echo ""
        echo "  If commands still don't work:"
        echo "    • Restart Claude Code CLI session"
        echo "    • Check .claude/commands/ directory exists"
    fi

    echo ""
    print_header "Workaround Commands"
    echo ""
    echo "Instead of /tree commands, use:"
    echo "  bash /workspace/.claude/scripts/tree.sh stage [description]"
    echo "  bash /workspace/.claude/scripts/tree.sh list"
    echo "  bash /workspace/.claude/scripts/tree.sh build"
    echo "  bash /workspace/.claude/scripts/tree.sh close"
    echo "  bash /workspace/.claude/scripts/tree.sh closedone"
    echo "  bash /workspace/.claude/scripts/tree.sh status"
    echo ""

    print_info "All functionality works identically via direct script calls"
}

#==============================================================================
# /tree help
#==============================================================================

tree_help() {
    cat << EOF
${TREE} Tree Worktree Management

Available commands:
  stage [description]    - Stage feature for worktree creation ✅
  list                   - Show staged features ✅
  clear                  - Clear all staged features ✅
  conflict               - Analyze conflicts and suggest merges ✅
  scope-conflicts        - Detect scope conflicts across worktrees ✅
  build [options]        - Create worktrees from staged features (auto-launches Claude) ✅
  restore                - Restore terminals for existing worktrees ✅
  close [incomplete]     - Complete work and generate synopsis ✅
  closedone              - Batch merge and cleanup completed worktrees ✅
  status                 - Show worktree environment status ✅
  refresh                - Check slash command availability & session guidance ✅
  help                   - Show this help ✅

/tree build options:
  --verbose, -v          Show detailed git command output
  --confirm              Prompt before each worktree creation

/tree close usage:
  /tree close              Complete feature and mark ready to merge
  /tree close incomplete   Save progress for continuation in next cycle

/tree closedone usage:
  /tree closedone [options]

Options:
  --yes, -y              Skip confirmation prompts
  --force                Merge all worktrees even if not closed
  --full-cycle           Complete entire development cycle
  --bump [type]          Version bump type: patch|minor|major (default: patch)

⚠️  Important: /tree closedone now requires all worktrees to be closed with
   '/tree close' before merging. Use --force to bypass this check.

🛡️  Error Prevention Features (NEW):
   • Pre-flight validation detects and cleans orphaned directories
   • Automatic git worktree prune on build start
   • Stale lock detection and removal
   • Atomic rollback on build failures
   • Idempotent operations (safe to retry)
   • Enhanced error messages with git output

Environment Variables:
  TREE_VERBOSE=true      Enable verbose mode globally (same as --verbose)

Typical Workflow:
  1. /tree stage [description]  # Stage multiple features
  2. /tree list                 # Review staged features
  3. /tree conflict             # Analyze conflicts (optional)
  4. /tree build                # Create all worktrees (with auto-cleanup)
  5. [work in worktrees]        # Implement features
  6. /tree close                # Complete work (or 'close incomplete')
  7. /tree closedone            # Merge all completed worktrees
  8. /tree closedone --full-cycle  # Full automation (optional)

Examples:
  /tree stage Add user preferences backend
  /tree stage Dashboard analytics view
  /tree list
  /tree conflict
  /tree build                    # Standard build with auto-cleanup
  /tree build --verbose          # Show all git commands
  TREE_VERBOSE=true /tree build  # Same as --verbose
  # ... work in worktrees ...
  /tree close                    # Feature complete
  /tree close incomplete         # Need more work later
  /tree closedone                # Merge completed only
  /tree closedone --full-cycle   # Full cycle: merge → main → version bump → new cycle
  /tree status                   # Check environment status

Troubleshooting:
  • Build fails with "path exists": Run '/tree build' again (auto-cleanup)
  • Build fails with "branch exists": Run '/tree build' again (auto-cleanup)
  • Build fails with stale lock: Run '/tree build' again (auto-removed)
  • See detailed errors: Use '/tree build --verbose'

For full documentation, see: tasks/prd-tree-slash-command.md
EOF
}

#==============================================================================
# Main Command Router
#==============================================================================

# Main command routing with both restore and refresh
case "$COMMAND" in
    stage)
        tree_stage "$@"
        ;;
    list)
        tree_list "$@"
        ;;
    clear)
        tree_clear "$@"
        ;;
    conflict)
        tree_conflict "$@"
        ;;
    scope-conflicts)
        tree_scope_conflicts "$@"
        ;;
    build)
        tree_build "$@"
        ;;
    close)
        tree_close "$@"
        ;;
    status)
        tree_status "$@"
        ;;
    restore)
        tree_restore "$@"
        ;;
    refresh)
        tree_refresh "$@"
        ;;
    closedone)
        closedone_main "$@"
        ;;
    help|--help|-h)
        tree_help
        ;;
    *)
        print_error "Unknown command: $COMMAND"
        echo ""
        tree_help
        exit 1
        ;;
esac
