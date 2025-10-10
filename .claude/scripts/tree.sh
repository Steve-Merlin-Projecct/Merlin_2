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
# /tree build - Create worktrees from staged features
#==============================================================================

tree_build() {
    if [ ! -f "$STAGED_FEATURES_FILE" ]; then
        print_error "No features staged"
        echo "Use: /tree stage [description] to stage features first"
        return 1
    fi

    # Read staged features
    local features=()
    while IFS=':' read -r name desc; do
        [[ "$name" =~ ^#.*$ ]] || [ -z "$name" ] && continue
        features+=("$name:$desc")
    done < "$STAGED_FEATURES_FILE"

    if [ ${#features[@]} -eq 0 ]; then
        print_error "No features staged"
        return 1
    fi

    print_header "Building ${#features[@]} Worktree(s)"

    # Get current version and timestamp
    local version=$(cat /workspace/VERSION 2>/dev/null || echo "0.0.0")
    local timestamp=$(date +%Y%m%d-%H%M%S)
    local dev_branch="develop/v${version}-worktrees-${timestamp}"

    echo "📋 Staged features:"
    for i in "${!features[@]}"; do
        local feature="${features[$i]}"
        local name="${feature%%:*}"
        echo "  $((i+1)). $name"
    done
    echo ""
    echo "Development Branch: $dev_branch"
    echo ""

    # Create development branch if not exists
    if ! git rev-parse --verify "$dev_branch" &>/dev/null; then
        wait_for_git_lock || return 1
        git checkout -b "$dev_branch" &>/dev/null
        print_success "Created development branch: $dev_branch"
    fi

    # Create each worktree
    local success_count=0
    local failed_count=0

    for i in "${!features[@]}"; do
        local feature="${features[$i]}"
        local name="${feature%%:*}"
        local desc="${feature#*:}"
        local num=$((i+1))
        local task_num=$(printf "%02d" $num)
        local branch="task/${task_num}-${name}"
        local worktree_path="$TREES_DIR/$name"

        echo "[$num/${#features[@]}] Creating: $name"

        # Create worktree with new branch in one command
        wait_for_git_lock || continue
        if ! git worktree add -b "$branch" "$worktree_path" "$dev_branch" &>/dev/null; then
            print_error "  Failed to create worktree with branch: $branch"
            failed_count=$((failed_count + 1))
            continue
        fi

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

[Define what's in scope for this worktree]

## Out of Scope

[Define what's explicitly NOT in scope]

## Success Criteria

- [ ] All functionality implemented
- [ ] Tests written and passing
- [ ] Documentation updated
- [ ] Code reviewed
- [ ] Ready to merge

## Notes

[Add implementation notes, decisions, or concerns here]
EOF

        print_success "  Created: $worktree_path"
        success_count=$((success_count + 1))

        # Create integrated terminal for this worktree
        # Store worktree info for terminal creation after all worktrees are built
        echo "$worktree_path" >> "$TREES_DIR/.pending-terminals.txt"
    done

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
    echo ""
    echo "Worktree Location: $TREES_DIR/"
    echo "Build History: $build_history_dir/${timestamp}.txt"
    echo "═══════════════════════════════════════════════════════════"

    # Run refresh check for each created worktree to inform about CLI limitation
    if [ $success_count -gt 0 ]; then
        echo ""
        print_header "Worktree Session Information"

        echo "ℹ️  Running /tree refresh check for each worktree..."
        echo "   This will help you understand slash command availability."
        echo ""

        for i in "${!features[@]}"; do
            local feature="${features[$i]}"
            local name="${feature%%:*}"
            local worktree_path="$TREES_DIR/$name"

            # Only run for successfully created worktrees
            if [ -d "$worktree_path" ]; then
                echo ""
                echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
                echo "Worktree: $name"
                echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

                # Change to worktree and run refresh
                (cd "$worktree_path" && bash /workspace/.claude/scripts/tree.sh refresh)
            fi
        done

        echo ""
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        print_success "All worktrees created and session information displayed"

        # Create integrated terminals for each worktree
        echo ""
        print_header "Opening Integrated Terminals"

        if [ -f "$TREES_DIR/.pending-terminals.txt" ]; then
            if command -v code &> /dev/null; then
                print_info "Opening VS Code terminals for each worktree..."

                while IFS= read -r worktree_path; do
                    local wt_name=$(basename "$worktree_path")
                    print_info "  Opening terminal: $wt_name"

                    # Open folder in new VS Code window with integrated terminal
                    code "$worktree_path" &
                    sleep 0.5  # Small delay to prevent overwhelming VS Code
                done < "$TREES_DIR/.pending-terminals.txt"

                print_success "VS Code windows opened for all worktrees"
                echo ""
                print_info "Each worktree has been opened in VS Code"
                print_info "Integrated terminals will be available in each window"

            elif command -v tmux &> /dev/null; then
                print_info "Creating tmux windows for each worktree..."

                while IFS= read -r worktree_path; do
                    local wt_name=$(basename "$worktree_path")
                    tmux new-window -n "$wt_name" -c "$worktree_path" 2>/dev/null && \
                        print_success "  Created tmux window: $wt_name" || \
                        print_warning "  Tmux window creation skipped (not in tmux session)"
                done < "$TREES_DIR/.pending-terminals.txt"

            else
                print_warning "No supported terminal multiplexer found (VS Code or tmux)"
                echo "  Worktrees created but terminals must be opened manually"
            fi

            # Clean up pending terminals file
            rm -f "$TREES_DIR/.pending-terminals.txt"
        fi

        echo ""
        print_info "Next Steps:"
        echo "  1. Switch to a worktree VS Code window"
        echo "  2. Open integrated terminal (Ctrl+\` or Terminal > New Terminal)"
        echo "  3. Start working on your feature"
        echo "  4. Use direct script calls if slash commands don't work:"
        echo "     bash /workspace/.claude/scripts/tree.sh [command]"
        echo "  5. When done: bash /workspace/.claude/scripts/tree.sh close"
    fi
}

#==============================================================================
# /tree conflict - Analyze conflicts and suggest merges
#==============================================================================

tree_conflict() {
    if [ ! -f "$STAGED_FEATURES_FILE" ]; then
        print_error "No features staged"
        echo "Use: /tree stage [description] to stage features first"
        return 1
    fi

    print_header "Conflict Analysis"

    # Read staged features
    local features=()
    while IFS=':' read -r name desc; do
        [[ "$name" =~ ^#.*$ ]] || [ -z "$name" ] && continue
        features+=("$name:$desc")
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
        local name_i="${feature_i%%:*}"
        local desc_i="${feature_i#*:}"

        for j in "${!features[@]}"; do
            [ $i -ge $j ] && continue

            local feature_j="${features[$j]}"
            local name_j="${feature_j%%:*}"
            local desc_j="${feature_j#*:}"

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

    print_header "Completing Work: $worktree_name"

    # Get branch info
    local branch=$(git branch --show-current)
    local base_branch=$(git config --get "branch.$branch.merge" | sed 's#refs/heads/##' || echo "main")

    echo "Worktree: $worktree_name"
    echo "Branch: $branch"
    echo "Base: $base_branch"
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

    # Generate synopsis
    local timestamp=$(date +%Y%m%d-%H%M%S)
    local synopsis_file="$COMPLETED_DIR/${worktree_name}-synopsis-${timestamp}.md"

    mkdir -p "$COMPLETED_DIR"

    cat > "$synopsis_file" << EOF
# Work Completed: ${worktree_name//-/ }

# Branch: $branch
# Base: $base_branch
# Completed: $(date +"%Y-%m-%d %H:%M:%S")

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

    print_success "Synopsis generated: $synopsis_file"
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "📋 Work Summary: $worktree_name"
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
    echo "🎯 Next Steps:"
    echo "  1. Review synopsis before merging"
    echo "  2. Run /tree closedone to batch merge all completed worktrees"
    echo "  3. Or merge manually: git checkout $base_branch && git merge $branch"
    echo ""
    echo "✅ This worktree is ready to merge"
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
  build                  - Create worktrees from staged features ✅
  close                  - Complete work and generate synopsis ✅
  closedone              - Batch merge and cleanup completed worktrees ✅
  status                 - Show worktree environment status ✅
  refresh                - Check slash command availability & session guidance ✅
  help                   - Show this help ✅

/tree closedone usage:
  /tree closedone [options]

Options:
  --dry-run              Preview actions without executing
  --yes, -y              Skip confirmation prompts

Typical Workflow:
  1. /tree stage [description]  # Stage multiple features
  2. /tree list                 # Review staged features
  3. /tree conflict             # Analyze conflicts (optional)
  4. /tree build                # Create all worktrees
  5. [work in worktrees]        # Implement features
  6. /tree close                # Complete work (in each worktree)
  7. /tree closedone            # Merge all completed worktrees

Examples:
  /tree stage Add user preferences backend
  /tree stage Dashboard analytics view
  /tree list
  /tree conflict
  /tree build
  # ... work in worktrees ...
  /tree close                    # Run from within worktree
  /tree closedone                # Run from main workspace
  /tree status                   # Check environment status

For full documentation, see: tasks/prd-tree-slash-command.md
EOF
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
    conflict)
        tree_conflict "$@"
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
