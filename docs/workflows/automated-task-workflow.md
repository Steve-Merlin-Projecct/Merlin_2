# Automated Task Workflow System
**Version:** 1.0
**Date:** October 6, 2025
**Environment:** Claude Code

## Purpose

This document defines the automatic workflow triggered when a user provides a task-oriented request. The system automatically creates a PRD, generates a task list with TodoWrite integration, and executes tasks using Claude Code's built-in automation features.

## Workflow Overview

```
User Request → Intent Detection → PRD Creation → Task Generation → Task Execution
```

## 1. Intent Detection: Task vs Question

The agent must classify user requests as either **Tasks** (implementation required) or **Questions** (analysis/information only).

### Task Indicators (Trigger Workflow)

**Direct Command Patterns:**
- Action verbs: "Create...", "Build...", "Implement...", "Fix...", "Update...", "Add...", "Refactor...", "Migrate..."
- Explicit requests: "Please make...", "Can you code...", "I need you to develop..."
- Feature requests: "I want a feature that...", "We need functionality for..."
- Bug reports with implied fixes: "This is broken", "Not working correctly", "Getting an error in..."

**Examples:**
- ✅ "Create a user authentication system"
- ✅ "Fix the database connection timeout issue"
- ✅ "Add email validation to the registration form"
- ✅ "Refactor the document generation module"
- ✅ "I need a feature to export reports to PDF"
- ✅ "Build an API endpoint for user profile updates"

### Question Indicators (Skip Workflow - Analysis Only)

**Question Patterns:**
- Question words: "How do we...", "What are...", "Why does...", "Can you explain...", "Where is..."
- Comparison requests: "What's the difference between...", "Which approach is better..."
- Recommendations: "What would you suggest...", "What are best practices for..."
- Understanding: "How does this work...", "What is the purpose of..."
- Review requests: "Can you review...", "What do you think of..."

**Examples:**
- ❌ "How does the authentication system work?"
- ❌ "What are the best practices for error handling?"
- ❌ "Can you explain the database schema?"
- ❌ "Why is the build failing?"
- ❌ "What would you recommend for caching?"

### Edge Cases

**Compound Statements:** Problem + explanation request
- "This is broken. Can you explain why?" → **Question** (focuses on "explain")
- "The system failed. What happened?" → **Question** (focuses on "What")

**Mixed Requests:** Information + action
- Default to **Question** first
- After providing analysis, ask: "Would you like me to implement any of these suggestions?"
- Wait for explicit confirmation before triggering workflow

**Qualifier Phrases:** User explicitly states intent
- "Just analyze..." → **Question**
- "Don't implement, but..." → **Question**
- "I need information about..." → **Question**
- "Go ahead and..." → **Task**
- "Let's implement..." → **Task**

## 2. Automatic Workflow Trigger

When a **Task** is detected, the agent **automatically** executes this three-phase workflow:

### Phase 1: PRD Creation
1. Acknowledge the request as a task
2. Create feature directory: `/tasks/[feature-name]/`
3. Ask clarifying questions (provide options in lettered/numbered lists)
4. Wait for user responses
5. Generate comprehensive PRD
6. Save as `/tasks/[feature-name]/prd.md`
7. Present PRD to user for approval
8. If approved, proceed to Phase 2

### Phase 2: Task Generation
1. Analyze PRD functional requirements from `/tasks/[feature-name]/prd.md`
2. Create TodoWrite entries for high-level tasks (both markdown file AND TodoWrite API)
3. Save task list as `/tasks/[feature-name]/tasklist_1.md`
4. Break down each parent task into sub-tasks
5. Identify relevant files to create/modify
6. Present task structure to user
7. If approved, proceed to Phase 3
8. If additional task lists needed, create `tasklist_2.md`, etc.

### Phase 3: Task Execution
1. Mark first sub-task as `in_progress` in TodoWrite
2. Execute the sub-task
3. Mark sub-task as `completed` immediately upon finishing
4. When all sub-tasks in a parent task are completed:
   - Run full test suite
   - If tests pass, stage changes (`git add .`)
   - Create commit with conventional format
   - Mark parent task as `completed`
5. Proceed to next sub-task
6. Repeat until all tasks completed

## 3. TodoWrite Integration

All task tracking uses Claude Code's built-in TodoWrite tool.

### Required Fields
```json
{
  "content": "Fix authentication bug",
  "activeForm": "Fixing authentication bug",
  "status": "pending|in_progress|completed"
}
```

### Status Management Rules
- **Only ONE task** can be `in_progress` at a time
- Mark tasks `completed` **immediately** after finishing (no batching)
- Keep todo list synchronized with markdown task file
- Update both on every status change

### Example TodoWrite Workflow
```
1. Create todos for parent tasks
2. Mark first sub-task as in_progress
3. Execute work
4. Mark sub-task completed
5. If all sub-tasks done → run tests → commit → mark parent completed
6. Move to next sub-task
```

## 4. Agent Behavior Guidelines

### DO:
- ✅ Automatically trigger workflow when task detected
- ✅ Use TodoWrite for ALL task tracking
- ✅ Ask clarifying questions before PRD creation
- ✅ Break complex tasks into manageable sub-tasks
- ✅ Update todo status in real-time
- ✅ Run tests before committing parent tasks
- ✅ Use conventional commit format
- ✅ Keep markdown and TodoWrite synchronized

### DON'T:
- ❌ Implement without creating PRD first
- ❌ Skip task list generation
- ❌ Use manual markdown checkboxes instead of TodoWrite
- ❌ Have multiple tasks in `in_progress` simultaneously
- ❌ Batch todo completions
- ❌ Commit without running tests
- ❌ Skip clarifying questions

## 5. Commit Protocol

When all sub-tasks in a parent task are completed:

1. **Run Tests:** Execute full test suite (`pytest`, `npm test`, etc.)
2. **Stage Changes:** `git add .` (only if tests pass)
3. **Clean Up:** Remove temporary files/code
4. **Commit:** Use conventional commit format with descriptive message
5. **Mark Parent Completed:** Update TodoWrite status

### Commit Message Format
```bash
git commit -m "$(cat <<'EOF'
feat: add user authentication validation

- Validates email format and password strength
- Adds unit tests for edge cases
- Updates API documentation

Related to Task 1.0 in PRD: User Authentication System

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"
```

## 6. File Structure

### Generated Files
```
/tasks/
└── [feature-name]/
    ├── prd.md                     # Product Requirements Document
    ├── tasklist_1.md              # Primary task list (markdown format)
    ├── tasklist_2.md              # Additional task lists if needed
    └── notes.md                   # Optional: Implementation notes
```

**Naming Convention:**
- Feature directory: Use kebab-case (e.g., `user-authentication`, `password-reset`)
- PRD: Always named `prd.md` within feature directory
- Task lists: Numbered sequentially (`tasklist_1.md`, `tasklist_2.md`, etc.)
- Additional files: As needed for documentation

### Task File Format
```markdown
# Tasks: [Feature Name]

**PRD:** ./prd.md
**Task List:** tasklist_1.md
**Status:** In Progress
**Last Updated:** 2025-10-06

## Relevant Files

- `path/to/file.py` - Description of file's role
- `path/to/file.test.py` - Unit tests for file.py

## Tasks

- [ ] 1.0 Parent Task Title
  - [ ] 1.1 Sub-task description
  - [ ] 1.2 Sub-task description
- [ ] 2.0 Parent Task Title
  - [ ] 2.1 Sub-task description
```

## 7. Version Control Integration

### Changelog Updates
After completing a **full parent task** (all sub-tasks done):
1. Update `docs/changelogs/master-changelog.md`
2. Increment version number in `CLAUDE.md` (line 3)
   - Major changes: increment `x.0`
   - Minor changes: increment `0.xx`

### Archival Process
After **complete project completion** and verification:
1. Move entire feature directory to `docs/archived/[appropriate-subdirectory]/[feature-name]/`
2. Preserve all files within the feature directory (prd.md, tasklist_*.md, notes.md)
3. Update `docs/changelogs/master-changelog.md` with new locations
4. Update project status in `CLAUDE.md`

## 8. Potential Improvements

After using this workflow, consider these incremental enhancements:

**Small Improvements:**
- Add a `.template` file for common PRD sections to reduce repetition
- Create bash aliases for frequently used commands (`run-tests`, `update-schema`)
- Document common task patterns as you discover them

**Hooks Integration:**
- Add a pre-commit hook to run tests automatically
- Add a hook to check for TODOs before marking tasks complete
- Add a hook to validate commit message format

**Documentation Updates:**
- Capture lessons learned after each feature completion
- Add real examples from completed projects
- Document edge cases as you encounter them

**Evaluate After:** 5-10 completed features to identify which improvements would be most valuable

## 9. Examples

### Example 1: Task Request
**User:** "Create a password reset feature for users"

**Agent Response:**
```
I've detected this as a task request. I'll automatically create a PRD, generate a task list,
and execute the implementation.

Phase 1: PRD Creation

Before I create the PRD, I have some clarifying questions:

1. Password reset method:
   a) Email-based reset link
   b) SMS-based verification code
   c) Security questions
   d) Multiple methods

2. Token expiration time:
   a) 15 minutes
   b) 1 hour
   c) 24 hours
   d) Custom duration

3. Should users be forced to change password after reset?
   a) Yes, must change on first login
   b) No, reset sets permanent password

...
```

### Example 2: Question Request
**User:** "How does the current authentication system work?"

**Agent Response:**
```
I've detected this as an informational question. I'll provide analysis without
implementing changes.

The current authentication system works as follows:

1. User Authentication Flow:
   - User submits credentials via POST /api/auth/login
   - System validates against database (modules/database/auth.py:45)
   - JWT token generated (modules/auth/token_manager.py:78)
   ...

Would you like me to implement any improvements to this system?
```

## 10. Troubleshooting

### Workflow Not Triggering
- Verify request contains task indicators (action verbs)
- Check if request is phrased as a question
- Use explicit language: "Please implement..." or "Create..."

### TodoWrite Not Updating
- Ensure only ONE task is `in_progress`
- Check TodoWrite API calls are made after each change
- Verify todo list structure matches required format

### Commits Failing
- Ensure tests pass before commit attempt
- Check for unstaged changes
- Verify conventional commit format
- Review pre-commit hooks (if configured)

---

**Document Owner:** Development Team
**Review Cycle:** After every 5 completed projects
**Last Reviewed:** October 6, 2025
