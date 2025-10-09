---
title: Task Generation Guide (Claude Code Optimized)
created: '2025-10-07'
updated: '2025-10-07'
author: Steve-Merlin-Projecct
type: guide
status: active
tags:
- workflow
- task
- generation
---

# Task Generation Guide (Claude Code Optimized)
**Version:** 1.0
**Date:** October 6, 2025
**Environment:** Claude Code

## Overview

This guide defines how to generate a detailed task list with TodoWrite integration in Claude Code. Task lists are automatically generated as **Phase 2** of the Automated Task Workflow after PRD approval.

## When This Guide Applies

This guide is triggered **automatically** when:
- PRD has been created and approved by user
- Agent begins Phase 2: Task Generation
- PRD exists at `/tasks/[feature-name]/prd.md`

## Goal

Generate a detailed, step-by-step task list that:
1. Maps directly to PRD functional requirements
2. Integrates with Claude Code's TodoWrite API
3. Breaks down complex work into manageable sub-tasks
4. Identifies all relevant files to create/modify
5. Provides clear guidance for implementation

## Process

### Step 1: Acknowledge PRD Approval

```
Phase 2: Task Generation

I'll now analyze the PRD and create a comprehensive task list with TodoWrite integration.
```

### Step 2: Analyze PRD

Read and analyze `/tasks/[feature-name]/prd.md` focusing on:
- **Functional Requirements (FR):** Core functionality to implement
- **User Stories:** User-facing features and workflows
- **Technical Considerations:** Architecture, dependencies, integrations
- **Testing Strategy:** Unit, integration, and acceptance tests
- **Non-Goals:** Scope boundaries to avoid scope creep

### Step 3: Create High-Level Parent Tasks

Generate 4-7 high-level parent tasks that represent major implementation phases.

**Common Parent Task Patterns:**

1. **Setup & Configuration**
   - Environment setup
   - Dependency installation
   - Database schema changes
   - Configuration files

2. **Core Implementation**
   - Primary feature logic
   - Business rules
   - Data models
   - API endpoints

3. **User Interface** (if applicable)
   - UI components
   - Forms and validation
   - User flows
   - Responsive design

4. **Integration**
   - Third-party service integration
   - Internal module connections
   - API client/server connections

5. **Testing**
   - Unit tests
   - Integration tests
   - End-to-end tests
   - Security testing

6. **Documentation** ⚠️ **REQUIRED FOR ALL PROJECTS**
   - Inline code documentation (docstrings, comments)
   - Component documentation in `/docs/component_docs/[module]/`
   - API documentation (if applicable)
   - Update related documentation
   - Archive outdated documentation

7. **Deployment & Validation**
   - Deployment configuration
   - Smoke tests
   - Performance validation
   - Security review

**TodoWrite Creation:**
Create parent tasks in TodoWrite with status `pending`:
```json
{
  "content": "Implement core authentication logic",
  "activeForm": "Implementing core authentication logic",
  "status": "pending"
}
```

### Step 4: Break Down Into Sub-Tasks

For each parent task, create 3-8 specific, actionable sub-tasks.

**Sub-Task Guidelines:**
- Be specific and actionable (start with action verbs)
- Focus on one logical unit of work
- Should be completable in 15-60 minutes
- Include testing as part of implementation
- Reference specific files when known

**Good Sub-Task Examples:**
- ✅ "Create `User` model with email, password_hash, and timestamps fields"
- ✅ "Implement password hashing using bcrypt in `auth_utils.py`"
- ✅ "Add POST `/api/auth/register` endpoint with validation"
- ✅ "Write unit tests for password validation logic"

**Poor Sub-Task Examples:**
- ❌ "Do authentication" (too vague)
- ❌ "Make it work" (not actionable)
- ❌ "Fix bugs" (not specific)

### Step 5: Identify Relevant Files

List all files that will be created or modified, organized by category.

**File Categories:**

1. **Core Implementation Files**
   - Main feature code
   - Business logic
   - Data models

2. **Test Files**
   - Unit tests (always alongside implementation)
   - Integration tests
   - Test utilities

3. **Configuration Files**
   - Environment configs
   - Database migrations
   - Build/deployment configs

4. **Documentation Files**
   - README updates
   - API documentation
   - Architecture diagrams

**Format:**
```markdown
## Relevant Files

### Implementation
- `modules/auth/user_model.py` - SQLAlchemy User model with authentication fields
- `modules/auth/auth_service.py` - Authentication business logic and password handling
- `modules/auth/routes.py` - Flask routes for registration, login, logout

### Tests
- `modules/auth/test_user_model.py` - Unit tests for User model
- `modules/auth/test_auth_service.py` - Unit tests for authentication service
- `modules/auth/test_routes.py` - Integration tests for auth endpoints

### Configuration
- `database_tools/migrations/003_add_users_table.sql` - Database migration for users table
- `.env.example` - Example environment variables for auth configuration

### Documentation
- `docs/component_docs/authentication/auth_system.md` - Authentication system documentation
- `docs/api/auth_endpoints.md` - API documentation for auth endpoints
```

### Step 6: Create Markdown Task File

Save the complete task list to `/tasks/[feature-name]/tasklist_1.md`.

**File Structure:**
```markdown
# Tasks: [Feature Name]

**PRD:** ./prd.md
**Task List:** tasklist_1.md
**Status:** Not Started
**Created:** 2025-10-06
**Last Updated:** 2025-10-06

## Overview

[1-2 sentences describing what this task list covers]

## Relevant Files

[File list from Step 5]

## Tasks

- [ ] 1.0 Parent Task Title
  - [ ] 1.1 Sub-task description
  - [ ] 1.2 Sub-task description
  - [ ] 1.3 Sub-task description
- [ ] 2.0 Parent Task Title
  - [ ] 2.1 Sub-task description
  - [ ] 2.2 Sub-task description
- [ ] 3.0 Parent Task Title
  - [ ] 3.1 Sub-task description
  - [ ] 3.2 Sub-task description
  - [ ] 3.3 Sub-task description

## Notes

[Optional section for implementation notes, warnings, or considerations]
```

### Step 7: Synchronize with TodoWrite

Create TodoWrite entries for all parent tasks and sub-tasks:

```json
[
  {
    "content": "Set up authentication infrastructure",
    "activeForm": "Setting up authentication infrastructure",
    "status": "pending"
  },
  {
    "content": "Implement core authentication logic",
    "activeForm": "Implementing core authentication logic",
    "status": "pending"
  },
  {
    "content": "Create authentication tests",
    "activeForm": "Creating authentication tests",
    "status": "pending"
  }
]
```

### Step 8: Present Task List to User

```
I've created a comprehensive task list with [X] parent tasks and [Y] sub-tasks.

The task list is saved to /tasks/[feature-name]/tasklist_1.md and synchronized
with TodoWrite for real-time progress tracking.

Would you like me to proceed with Phase 3: Task Execution?
```

Wait for explicit approval before proceeding.

## TodoWrite Integration

### Dual Tracking System

The system maintains **two synchronized** task representations:

1. **Markdown File** (`tasklist_1.md`)
   - Human-readable format
   - Persisted to disk
   - Version controlled
   - Shows complete task hierarchy

2. **TodoWrite API**
   - Real-time progress tracking
   - Enforces one task `in_progress` at a time
   - Visible in Claude Code interface
   - Supports automation and hooks

### Synchronization Rules

**When creating tasks:**
- Create both markdown checkboxes AND TodoWrite entries
- Initial status: `pending` for all tasks

**When starting a task:**
- Mark markdown checkbox as in-progress (optional notation)
- Update TodoWrite status to `in_progress`
- Only ONE task can be `in_progress` globally

**When completing a task:**
- Mark markdown checkbox as checked `[x]`
- Update TodoWrite status to `completed`
- Do this **immediately** upon finishing (no batching)

**When adding new tasks:**
- Add to markdown file
- Create TodoWrite entry
- Insert in logical position in task hierarchy

### TodoWrite Field Requirements

```json
{
  "content": "Imperative form: what needs to be done",
  "activeForm": "Present continuous: what is being done",
  "status": "pending | in_progress | completed"
}
```

**Examples:**
```json
{
  "content": "Create User model with authentication fields",
  "activeForm": "Creating User model with authentication fields",
  "status": "pending"
}

{
  "content": "Write unit tests for password validation",
  "activeForm": "Writing unit tests for password validation",
  "status": "in_progress"
}

{
  "content": "Add POST /api/auth/login endpoint",
  "activeForm": "Adding POST /api/auth/login endpoint",
  "status": "completed"
}
```

## Task Numbering System

Use hierarchical numbering for clear task organization:

```
1.0 Parent Task
  1.1 Sub-task
  1.2 Sub-task
  1.3 Sub-task
2.0 Parent Task
  2.1 Sub-task
  2.2 Sub-task
  2.3 Sub-task
3.0 Parent Task
  3.1 Sub-task
```

**Benefits:**
- Easy to reference in discussions ("Let's work on task 2.3")
- Shows clear hierarchy
- Allows insertion of new tasks (e.g., 2.4, 2.5)
- Maps to commit messages ("Completed task 1.0")

## Quality Checklist

Before presenting the task list:

- [ ] All PRD functional requirements are covered
- [ ] Tasks are broken into manageable sub-tasks (15-60 min each)
- [ ] Each sub-task is specific and actionable
- [ ] Test files are identified for all implementation files
- [ ] Configuration and migration files are listed
- [ ] **Documentation parent task is included (REQUIRED)**
- [ ] Documentation task includes: inline docs, component docs, API docs, archival
- [ ] Tasks are numbered hierarchically
- [ ] TodoWrite entries are created for all tasks
- [ ] Markdown file is saved to `/tasks/[feature-name]/tasklist_1.md`
- [ ] Task descriptions use imperative form (content) and continuous form (activeForm)

## Common Task Patterns

### Pattern 1: Database Changes
```markdown
- [ ] 1.0 Database Schema Updates
  - [ ] 1.1 Create migration file for new tables
  - [ ] 1.2 Run migration on development database
  - [ ] 1.3 Update SQLAlchemy models
  - [ ] 1.4 Run `database_tools/update_schema.py` to generate docs
  - [ ] 1.5 Commit generated schema documentation
```

### Pattern 2: API Endpoint
```markdown
- [ ] 2.0 Create User Registration Endpoint
  - [ ] 2.1 Define Pydantic request/response schemas
  - [ ] 2.2 Implement POST `/api/auth/register` route
  - [ ] 2.3 Add input validation (email format, password strength)
  - [ ] 2.4 Implement user creation logic with password hashing
  - [ ] 2.5 Add error handling for duplicate emails
  - [ ] 2.6 Write unit tests for validation logic
  - [ ] 2.7 Write integration tests for endpoint
```

### Pattern 3: UI Component
```markdown
- [ ] 3.0 Build Login Form Component
  - [ ] 3.1 Create LoginForm component structure
  - [ ] 3.2 Add email and password input fields
  - [ ] 3.3 Implement client-side validation
  - [ ] 3.4 Add loading and error states
  - [ ] 3.5 Connect to authentication API
  - [ ] 3.6 Add accessibility attributes (ARIA labels)
  - [ ] 3.7 Write component tests
```

### Pattern 4: Integration
```markdown
- [ ] 4.0 Gmail API Integration
  - [ ] 4.1 Set up Google Cloud project and credentials
  - [ ] 4.2 Implement OAuth 2.0 flow
  - [ ] 4.3 Create email sending service
  - [ ] 4.4 Add attachment handling
  - [ ] 4.5 Implement error handling and retries
  - [ ] 4.6 Write integration tests with mocked API
  - [ ] 4.7 Update environment variable documentation
```

### Pattern 5: Documentation (REQUIRED)
```markdown
- [ ] 5.0 Documentation
  - [ ] 5.1 Add comprehensive inline documentation to all new files
  - [ ] 5.2 Create component documentation in /docs/component_docs/[module]/
  - [ ] 5.3 Document data flow and integration points
  - [ ] 5.4 Add API documentation (if applicable)
  - [ ] 5.5 Update related documentation for modified files
  - [ ] 5.6 Archive outdated documentation with deprecation notices
  - [ ] 5.7 Update master changelog with documentation changes
```

**Note:** Documentation is a **required parent task** for all projects, not optional.

## Multiple Task Lists

For large features, create multiple task lists:

```
/tasks/[feature-name]/
├── prd.md
├── tasklist_1.md    # Phase 1: Core implementation
├── tasklist_2.md    # Phase 2: Advanced features
└── tasklist_3.md    # Phase 3: Optimization & polish
```

**When to use multiple lists:**
- Feature spans 20+ parent tasks
- Distinct implementation phases
- Iterative development approach
- Parallel work streams

**Reference between lists:**
```markdown
# Tasks: User Authentication (Phase 1)

**PRD:** ./prd.md
**Task List:** tasklist_1.md
**Next Phase:** tasklist_2.md (Advanced features)
**Status:** In Progress
```

## Integration with Automated Workflow

After task list approval:
1. **Automatic progression to Phase 3:** Task Execution
2. First sub-task marked as `in_progress` in TodoWrite
3. Agent begins implementation following task order
4. Updates both markdown and TodoWrite on completion
5. Commits after each parent task completion (if tests pass)

## Examples

### Example 1: Simple Feature
See: `/tasks/password-reset/tasklist_1.md` (example)

### Example 2: Complex Feature with Multiple Lists
See: `/tasks/user-dashboard/tasklist_1.md` (example)
See: `/tasks/user-dashboard/tasklist_2.md` (example)

## Incremental Improvements

After generating several task lists, consider:

- **Pattern documentation:** Document common task patterns for your project (see Common Task Patterns section)
- **Time estimates:** Add estimated durations to tasks after completing a few features
- **Task templates:** Create reusable sub-task lists for common operations (API endpoint, database migration, etc.)
- **Dependencies:** Note which tasks frequently block others

**Evaluate after:** 3-5 task lists to identify helpful patterns

---

**Document Owner:** Development Team
**Related Guides:**
- [Automated Task Workflow](./automated-task-workflow.md)
- [PRD Generation Guide](./prd-generation-guide.md)
- [Task Execution Guide](./task-execution-guide.md)

**Last Reviewed:** October 6, 2025
