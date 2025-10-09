#!/bin/bash
# List all worktrees with their paths for easy navigation

echo "📁 v4.2.0 Worktrees"
echo "=================="
echo ""

cat << 'EOF'
To open terminals in VS Code:
1. Open integrated terminal (Ctrl+`)
2. Click '+' dropdown → Select shell
3. Type: cd /workspace/.trees/<worktree>

Quick Commands:
EOF

echo ""
echo "cd /workspace/.trees/claude-refinement     # Task 1: Claude & Agents"
echo "cd /workspace/.trees/marketing-content     # Task 2: Marketing Content"
echo "cd /workspace/.trees/script-testing        # Task 3: Script Testing"
echo "cd /workspace/.trees/template-creation     # Task 4: Templates"
echo "cd /workspace/.trees/docx-verification     # Task 5: Docx Verification"
echo "cd /workspace/.trees/calendly              # Task 6: Calendly"
echo "cd /workspace/.trees/dashboard-redesign    # Task 7: Dashboard"
echo "cd /workspace/.trees/database-viz          # Task 8: Database Viz"
echo "cd /workspace/.trees/gemini-prompts        # Task 9: Gemini Prompts"
echo "cd /workspace/.trees/librarian             # Task 10: Librarian"
echo "cd /workspace/.trees/email-refinement      # Task 11: Email"
echo "cd /workspace/.trees/github-streamline     # Task 12: GitHub"
echo "cd /workspace/.trees/analytics             # Task 13: Analytics"
echo ""

echo "Current worktree status:"
git worktree list | grep -E "task/|develop/v4.2.0"
