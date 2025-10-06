#!/bin/bash
# Merge Conflict Resolver - Fix failed merge from noxml to main
# Addresses the incomplete merge that left conflicts unresolved

echo "Merge Conflict Resolver - noxml → main Integration"
echo "================================================="

# Function to analyze current git state
analyze_git_state() {
    echo "Analyzing current git state..."
    
    local current_branch=$(git branch --show-current 2>/dev/null || echo "unknown")
    local git_status=$(git status --porcelain 2>/dev/null || echo "Git status unavailable")
    
    echo "Current branch: $current_branch"
    echo "Git status: $([ -z "$git_status" ] && echo "Clean" || echo "Has changes")"
    
    # Check if we're in a merge state
    if [ -f ".git/MERGE_HEAD" ]; then
        echo "⚠️  Repository is in an incomplete merge state"
        return 1
    else
        echo "✅ Repository is not in merge state"
        return 0
    fi
}

# Function to safely switch to main branch
safe_switch_to_main() {
    echo "Switching to main branch safely..."
    
    # Use branch management script for safety
    if ./.github/scripts/branch_management.sh switch main 2>/dev/null; then
        echo "✅ Successfully switched to main"
        return 0
    else
        echo "❌ Could not switch using branch management script"
        
        # Alternative approach - check current location first
        local current=$(git branch --show-current 2>/dev/null)
        if [ "$current" = "main" ]; then
            echo "✅ Already on main branch"
            return 0
        else
            echo "⚠️  Will need manual branch switching"
            return 1
        fi
    fi
}

# Function to create integration strategy
create_integration_strategy() {
    echo "Creating integration strategy for noxml commits..."
    echo ""
    
    echo "Commits from noxml that need integration:"
    echo "========================================"
    echo "ec220eb - Implement safe branching strategy that allows code experimentation"
    echo "31d3fe0 - Implement strategy to prevent conflicts between local and remote Git repos"
    echo "ca31edb - Clarify troubleshooting steps and confirm successful GitHub connection"
    echo "8ce4d7f - Archive outdated documentation for document generation and GitHub connection"
    echo "c1b87c5 - Provide a detailed plan to restore the connection with the GitHub repository"
    echo ""
    
    echo "Integration Strategy:"
    echo "===================="
    echo "1. Switch to main branch"
    echo "2. Create pre-integration checkpoint"
    echo "3. Cherry-pick commits from noxml in order"
    echo "4. Resolve any conflicts manually"
    echo "5. Commit resolved changes"
    echo "6. Push to GitHub"
    echo ""
}

# Function to perform cherry-pick integration
perform_integration() {
    echo "Performing cherry-pick integration..."
    
    # List of commits to cherry-pick (in reverse chronological order for proper application)
    local commits=(
        "c1b87c5" 
        "8ce4d7f"
        "ca31edb"
        "31d3fe0"
        "ec220eb"
    )
    
    # Create checkpoint before integration
    echo "Creating pre-integration checkpoint..."
    if ./.github/scripts/branch_management.sh checkpoint "pre-noxml-integration"; then
        echo "✅ Checkpoint created"
    else
        echo "⚠️  Could not create checkpoint - proceeding with caution"
    fi
    
    echo "Beginning cherry-pick integration..."
    
    for commit in "${commits[@]}"; do
        echo "Cherry-picking commit: $commit"
        
        if git cherry-pick "$commit" 2>/dev/null; then
            echo "✅ Successfully integrated: $commit"
        else
            echo "⚠️  Conflict in commit: $commit"
            echo "Manual resolution required for this commit"
            
            # Show conflicted files
            echo "Conflicted files:"
            git status --porcelain | grep "^UU\|^AA\|^DD" || echo "No obvious conflicts detected"
            
            return 1
        fi
    done
    
    echo "✅ All commits integrated successfully"
    return 0
}

# Function to provide manual resolution guidance
provide_manual_guidance() {
    echo "Manual Resolution Required"
    echo "========================="
    echo ""
    echo "The automatic integration encountered conflicts. Here's how to resolve:"
    echo ""
    echo "1. Check current status:"
    echo "   git status"
    echo ""
    echo "2. For each conflicted file, edit manually to resolve conflicts"
    echo "   Look for conflict markers: <<<<<<< HEAD, =======, >>>>>>> [commit]"
    echo ""
    echo "3. After resolving conflicts in each file:"
    echo "   git add <resolved-file>"
    echo ""
    echo "4. Continue the cherry-pick:"
    echo "   git cherry-pick --continue"
    echo ""
    echo "5. Repeat for remaining commits"
    echo ""
    echo "6. When all commits are integrated:"
    echo "   git push origin main"
    echo ""
    echo "Alternative: Use Replit's git interface (sidebar) for visual conflict resolution"
}

# Main execution
main() {
    echo "Starting merge conflict resolution process..."
    echo ""
    
    # Step 1: Analyze current state
    if ! analyze_git_state; then
        echo "Repository is in an incomplete merge state - manual cleanup required"
        provide_manual_guidance
        return 1
    fi
    
    # Step 2: Show integration strategy
    create_integration_strategy
    
    # Step 3: Switch to main branch
    if ! safe_switch_to_main; then
        echo "Could not switch to main branch safely"
        echo "Please use: ./.github/scripts/branch_management.sh switch main"
        return 1
    fi
    
    # Step 4: Wait for git lock to clear
    echo "Waiting for git operations to stabilize..."
    sleep 3
    
    # Step 5: Attempt integration
    if perform_integration; then
        echo ""
        echo "🎉 SUCCESS: noxml branch successfully integrated into main"
        echo ""
        echo "Next steps:"
        echo "- Verify changes: ./.github/scripts/branch_management.sh status"
        echo "- Check integration: ./.github/scripts/branch_management.sh check-merged main"
        echo "- Push to GitHub: git push origin main"
    else
        echo ""
        echo "⚠️  Integration requires manual conflict resolution"
        provide_manual_guidance
    fi
}

# Execute main function
main "$@"