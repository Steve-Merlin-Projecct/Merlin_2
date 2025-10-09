#!/bin/bash
# Open terminal for each worktree using tmux or screen

echo "🚀 Opening terminals for all 13 worktrees..."
echo ""

# Check if tmux is available
if command -v tmux &> /dev/null; then
    echo "Using tmux..."

    # Create tmux session
    tmux new-session -d -s v4.2.0-dev -n "Main" -c /workspace

    # Create windows for each worktree
    tmux new-window -t v4.2.0-dev -n "Task-01-Claude" -c /workspace/.trees/claude-refinement
    tmux new-window -t v4.2.0-dev -n "Task-02-Content" -c /workspace/.trees/marketing-content
    tmux new-window -t v4.2.0-dev -n "Task-03-Testing" -c /workspace/.trees/script-testing
    tmux new-window -t v4.2.0-dev -n "Task-04-Templates" -c /workspace/.trees/template-creation
    tmux new-window -t v4.2.0-dev -n "Task-05-Docx" -c /workspace/.trees/docx-verification
    tmux new-window -t v4.2.0-dev -n "Task-06-Calendly" -c /workspace/.trees/calendly
    tmux new-window -t v4.2.0-dev -n "Task-07-Dashboard" -c /workspace/.trees/dashboard-redesign
    tmux new-window -t v4.2.0-dev -n "Task-08-DbViz" -c /workspace/.trees/database-viz
    tmux new-window -t v4.2.0-dev -n "Task-09-Gemini" -c /workspace/.trees/gemini-prompts
    tmux new-window -t v4.2.0-dev -n "Task-10-Librarian" -c /workspace/.trees/librarian
    tmux new-window -t v4.2.0-dev -n "Task-11-Email" -c /workspace/.trees/email-refinement
    tmux new-window -t v4.2.0-dev -n "Task-12-GitHub" -c /workspace/.trees/github-streamline
    tmux new-window -t v4.2.0-dev -n "Task-13-Analytics" -c /workspace/.trees/analytics

    # Select first window
    tmux select-window -t v4.2.0-dev:1

    echo "✅ Tmux session 'v4.2.0-dev' created with 14 windows"
    echo ""
    echo "To attach: tmux attach -t v4.2.0-dev"
    echo "To navigate: Ctrl+b then window number (0-13)"
    echo "To detach: Ctrl+b then d"
    echo ""

    # Attach to session
    tmux attach -t v4.2.0-dev

elif command -v screen &> /dev/null; then
    echo "Using screen..."

    # Create screen session
    screen -dmS v4.2.0-dev

    # Create screens for each worktree
    screen -S v4.2.0-dev -X screen -t "Task-01-Claude" bash -c "cd /workspace/.trees/claude-refinement; bash"
    screen -S v4.2.0-dev -X screen -t "Task-02-Content" bash -c "cd /workspace/.trees/marketing-content; bash"
    screen -S v4.2.0-dev -X screen -t "Task-03-Testing" bash -c "cd /workspace/.trees/script-testing; bash"
    screen -S v4.2.0-dev -X screen -t "Task-04-Templates" bash -c "cd /workspace/.trees/template-creation; bash"
    screen -S v4.2.0-dev -X screen -t "Task-05-Docx" bash -c "cd /workspace/.trees/docx-verification; bash"
    screen -S v4.2.0-dev -X screen -t "Task-06-Calendly" bash -c "cd /workspace/.trees/calendly; bash"
    screen -S v4.2.0-dev -X screen -t "Task-07-Dashboard" bash -c "cd /workspace/.trees/dashboard-redesign; bash"
    screen -S v4.2.0-dev -X screen -t "Task-08-DbViz" bash -c "cd /workspace/.trees/database-viz; bash"
    screen -S v4.2.0-dev -X screen -t "Task-09-Gemini" bash -c "cd /workspace/.trees/gemini-prompts; bash"
    screen -S v4.2.0-dev -X screen -t "Task-10-Librarian" bash -c "cd /workspace/.trees/librarian; bash"
    screen -S v4.2.0-dev -X screen -t "Task-11-Email" bash -c "cd /workspace/.trees/email-refinement; bash"
    screen -S v4.2.0-dev -X screen -t "Task-12-GitHub" bash -c "cd /workspace/.trees/github-streamline; bash"
    screen -S v4.2.0-dev -X screen -t "Task-13-Analytics" bash -c "cd /workspace/.trees/analytics; bash"

    echo "✅ Screen session 'v4.2.0-dev' created"
    echo ""
    echo "To attach: screen -r v4.2.0-dev"
    echo "To navigate: Ctrl+a then window number"
    echo "To detach: Ctrl+a then d"
    echo ""

    # Attach to session
    screen -r v4.2.0-dev

else
    echo "❌ Neither tmux nor screen is installed"
    echo ""
    echo "Manual option - Open terminals individually:"
    echo ""
    echo "cd /workspace/.trees/claude-refinement     # Task 1"
    echo "cd /workspace/.trees/marketing-content     # Task 2"
    echo "cd /workspace/.trees/script-testing        # Task 3"
    echo "cd /workspace/.trees/template-creation     # Task 4"
    echo "cd /workspace/.trees/docx-verification     # Task 5"
    echo "cd /workspace/.trees/calendly              # Task 6"
    echo "cd /workspace/.trees/dashboard-redesign    # Task 7"
    echo "cd /workspace/.trees/database-viz          # Task 8"
    echo "cd /workspace/.trees/gemini-prompts        # Task 9"
    echo "cd /workspace/.trees/librarian             # Task 10"
    echo "cd /workspace/.trees/email-refinement      # Task 11"
    echo "cd /workspace/.trees/github-streamline     # Task 12"
    echo "cd /workspace/.trees/analytics             # Task 13"
    echo ""
    echo "Or use VS Code integrated terminals (see .vscode/terminals.json)"
fi
