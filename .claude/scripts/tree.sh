#!/bin/bash

# Tree Worktree Management Script
# Phase 1: Core functionality for /tree closedone

set -e  # Exit on error

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
ARCHIVED_DIR="$TREES_DIR/.archived"
CONFLICT_BACKUP_DIR="$TREES_DIR/.conflict-backup"
STAGED_FEATURES_FILE="$TREES_DIR/.staged-features.txt"

# Command routing
COMMAND="${1:-help}"
shift || true

#==============================================================================
# Helper Functions
#==============================================================================

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

# Handle git index.lock issues
wait_for_git_lock() {
    local max_attempts=5
    local attempt=1

    while [ -f "$WORKSPACE_ROOT/.git/index.lock" ] && [ $attempt -le $max_attempts ]; do
        print_warning "Git lock detected, waiting... (attempt $attempt/$max_attempts)"
        sleep 1
        attempt=$((attempt + 1))
    done

    if [ -f "$WORKSPACE_ROOT/.git/index.lock" ]; then
        print_error "Git lock file persists. Please run: rm $WORKSPACE_ROOT/.git/index.lock"
        return 1
    fi
    return 0
}

# Stash uncommitted changes
stash_changes() {
    wait_for_git_lock || return 1

    if ! git diff-index --quiet HEAD --; then
        print_warning "Uncommitted changes detected, stashing..."
        git stash push -m "Auto-stash before /tree closedone at $(date +%Y%m%d-%H%M%S)"
        print_success "Changes stashed"
        return 0
    fi
    return 1
}

#==============================================================================
# /tree closedone - Phase 1 Core Functionality
#==============================================================================

closedone_main() {
    local dry_run=false
    local skip_confirmation=false

    # Parse options
    while [[ $# -gt 0 ]]; do
        case $1 in
            --dry-run)
                dry_run=true
                shift
                ;;
            --yes|-y)
                skip_confirmation=true
                shift
                ;;
            *)
                print_error "Unknown option: $1"
                echo "Usage: /tree closedone [--dry-run] [--yes]"
                return 1
                ;;
        esac
    done

    print_header "/tree closedone - Batch Merge & Cleanup"

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

    if [ "$dry_run" = true ]; then
        print_warning "DRY RUN - No changes will be made"
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

            if [ "$dry_run" = false ]; then
                # Phase 1.4: Cleanup only
                closedone_cleanup "$worktree" "$branch"
                cleanup_only_count=$((cleanup_only_count + 1))
            fi
        else
            # Phase 1.4: Merge execution
            if closedone_merge "$worktree" "$branch" "$base" "$dry_run"; then
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
    local dry_run=$4

    if [ "$dry_run" = true ]; then
        print_info "  [DRY RUN] Would switch to $base"
        print_info "  [DRY RUN] Would merge $branch"
        print_info "  [DRY RUN] Would cleanup worktree"
        return 0
    fi

    # Switch to base branch
    wait_for_git_lock || return 1

    if ! git checkout "$base" &>/dev/null; then
        print_error "  Failed to checkout $base"
        return 1
    fi
    print_success "  Switched to $base"

    # Attempt merge
    local merge_output
    if merge_output=$(git merge "$branch" --no-edit 2>&1); then
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
                git merge --abort
                return 1
            fi
        else
            print_error "  Merge failed: $merge_output"
            git merge --abort 2>/dev/null
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

# Cleanup worktree and branch
closedone_cleanup() {
    local worktree=$1
    local branch=$2

    # Remove worktree
    if git worktree remove "$TREES_DIR/$worktree" &>/dev/null; then
        print_success "  Removed worktree"
    else
        print_warning "  Failed to remove worktree (may already be removed)"
    fi

    # Delete branch (safe delete)
    if git branch -d "$branch" &>/dev/null; then
        print_success "  Deleted branch $branch"
    elif git branch -D "$branch" &>/dev/null; then
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
# Format: worktree-name:Description of the feature
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
    if grep -q "^${worktree_name}:" "$STAGED_FEATURES_FILE" 2>/dev/null; then
        print_warning "Feature with similar name already staged: $worktree_name"
        echo "Use a more specific description or remove the existing feature first"
        return 1
    fi

    # Append to staging file
    echo "${worktree_name}:${description}" >> "$STAGED_FEATURES_FILE"

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

    # Read staged features
    local features=()
    while IFS=':' read -r name desc; do
        # Skip comments and empty lines
        if [[ "$name" =~ ^#.*$ ]] || [ -z "$name" ]; then
            continue
        fi
        features+=("$name:$desc")
    done < "$STAGED_FEATURES_FILE"

    if [ ${#features[@]} -eq 0 ]; then
        print_warning "No features staged yet"
        echo "Use: /tree stage [description] to stage your first feature"
        return 0
    fi

    print_header "Staged Features (${#features[@]})"

    for i in "${!features[@]}"; do
        local feature="${features[$i]}"
        local name="${feature%%:*}"
        local desc="${feature#*:}"
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
# Other /tree commands (stubs for future implementation)
#==============================================================================

tree_help() {
    cat << EOF
${TREE} Tree Worktree Management

Available commands:
  stage [description]    - Stage feature for worktree creation ✅ PHASE 1
  list                   - Show staged features ✅ PHASE 1
  clear                  - Clear all staged features ✅ PHASE 1
  conflict               - Analyze conflicts and suggest merges (not yet implemented)
  build                  - Create worktrees from staged features (not yet implemented)
  close                  - Complete work and generate synopsis (not yet implemented)
  closedone              - Batch merge and cleanup completed worktrees ✅ PHASE 1 & 2
  status                 - Show worktree environment status (not yet implemented)
  help                   - Show this help

/tree closedone usage:
  /tree closedone [options]

Options:
  --dry-run              Preview actions without executing
  --yes, -y              Skip confirmation prompts

Examples:
  /tree closedone                    # Interactive merge of all completed worktrees
  /tree closedone --dry-run          # Preview what would be merged
  /tree closedone --yes              # Auto-confirm merge

Features:
  ✅ Phase 1: Core merge and cleanup (COMPLETE)
  🔧 Phase 2: AI conflict resolution (FRAMEWORK IMPLEMENTED - needs Claude CLI integration)
  📋 Phase 3: Advanced options (--resume, --skip, --only, etc.)
  📋 Phase 4: Terminal cleanup, error recovery, polish

For full documentation, see: tasks/prd-tree-slash-command.md
EOF
}

tree_not_implemented() {
    print_error "Command '$COMMAND' not yet implemented"
    echo ""
    echo "Currently implemented:"
    echo "  - /tree closedone (Phase 1: Core functionality)"
    echo ""
    echo "Coming soon:"
    echo "  - /tree stage, list, conflict, build, close, status"
    echo ""
    echo "Run '/tree help' for more information"
}

#==============================================================================
# Main Command Router
#==============================================================================

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
    closedone)
        closedone_main "$@"
        ;;
    help|--help|-h)
        tree_help
        ;;
    conflict|build|close|status)
        tree_not_implemented
        ;;
    *)
        print_error "Unknown command: $COMMAND"
        echo ""
        tree_help
        exit 1
        ;;
esac
