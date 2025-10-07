# Task Execution Guide (Claude Code Optimized)
**Version:** 1.0
**Date:** October 6, 2025
**Environment:** Claude Code

## Overview

This guide defines how to execute tasks with TodoWrite integration and automated testing in Claude Code. Task execution is automatically triggered as **Phase 3** of the Automated Task Workflow after task list approval.

## When This Guide Applies

This guide is triggered **automatically** when:
- PRD exists at `/tasks/[feature-name]/prd.md`
- Task list exists at `/tasks/[feature-name]/tasklist_1.md`
- TodoWrite entries are created for all tasks
- User approves proceeding with implementation

## Goal

Execute tasks systematically with:
1. Real-time TodoWrite progress tracking
2. Automated test execution before commits
3. Conventional commit format with proper attribution
4. Changelog and version updates
5. Clean, maintainable code

## Execution Flow

### Phase 3: Task Execution

```
Phase 3: Task Execution

I'll now begin implementing the tasks in order, updating TodoWrite progress
in real-time.

Starting with Task 1.1: [Sub-task description]
```

## Core Execution Protocol

### Step 1: Mark Task as In Progress

Before starting any sub-task, **sync both TodoWrite and Markdown in the same action**:

**Use the sync pattern below:**

```markdown
STEP 1A: Update TodoWrite
  ↓
STEP 1B: Update Markdown
  ↓
STEP 1C: Verify ONE Task In-Progress
```

**STEP 1A: Update TodoWrite**
```json
{
  "content": "Create User model with authentication fields",
  "activeForm": "Creating User model with authentication fields",
  "status": "in_progress"
}
```

**STEP 1B: Update Markdown** (immediately after TodoWrite)
```markdown
- [ ] 1.0 Set up authentication infrastructure
  - [→] 1.1 Create User model with authentication fields  ← Currently working
  - [ ] 1.2 Create migration file for users table
```

**STEP 1C: Verify ONE Task In-Progress**
- Check TodoWrite: Only ONE task has `status: "in_progress"`
- If multiple tasks show in-progress, fix immediately
- Both systems updated in **same response**

**CRITICAL RULE:** Only ONE task can be `in_progress` at a time.

### Step 2: Execute the Sub-Task

Perform the work described in the sub-task:
- Write code following project standards
- Add comprehensive inline documentation
- Follow naming conventions
- Implement error handling
- Consider edge cases

**Example:**
```python
# modules/auth/user_model.py

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from modules.database.base import Base

class User(Base):
    """
    User model for authentication and authorization.

    This model stores user credentials and metadata for the authentication
    system. Passwords are stored as bcrypt hashes, never in plaintext.

    Attributes:
        id (int): Primary key, auto-incrementing
        email (str): Unique email address for user identification
        password_hash (str): Bcrypt hash of user password
        created_at (datetime): Timestamp of user registration
        updated_at (datetime): Timestamp of last profile update
    """
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}')>"
```

### Step 3: Mark Sub-Task as Completed

**IMMEDIATELY** after finishing the sub-task, sync both TodoWrite and Markdown:

**Use the sync pattern below** to keep them in perfect alignment:

```markdown
STEP 3A: Update TodoWrite
  ↓
STEP 3B: Update Markdown
  ↓
STEP 3C: Verify Sync
```

**STEP 3A: Update TodoWrite**
```json
{
  "content": "Create User model with authentication fields",
  "activeForm": "Creating User model with authentication fields",
  "status": "completed"
}
```

**STEP 3B: Update Markdown** (immediately after TodoWrite)
```markdown
- [ ] 1.0 Set up authentication infrastructure
  - [x] 1.1 Create User model with authentication fields
  - [ ] 1.2 Create migration file for users table
```

**STEP 3C: Verify Sync**
- TodoWrite shows: `status: "completed"`
- Markdown shows: `[x]` checkbox
- Both updated in **same response** (no delay)

**DO NOT:**
- ❌ Update TodoWrite now, markdown later
- ❌ Batch multiple completions
- ❌ Skip either update
- ❌ Update only one system

### Step 4: Check Parent Task Completion

After completing a sub-task, check if **all sub-tasks** under the parent task are completed.

**If YES (all sub-tasks done):**
1. Proceed to Step 5 (Test & Commit)

**If NO (more sub-tasks remain):**
1. Move to next sub-task
2. Return to Step 1

### Step 5: Test & Commit (Parent Task Complete)

When all sub-tasks in a parent task are completed:

#### 5.1 Run Full Test Suite

```bash
# Python projects
pytest

# Node.js projects
npm test

# Ruby projects
bin/rails test

# Go projects
go test ./...
```

**If tests FAIL:**
- Keep parent task status as `in_progress`
- Create new sub-task: "Fix failing tests in [component]"
- Mark new sub-task as `in_progress`
- Debug and fix issues
- Re-run tests
- Mark sub-task as `completed` when passing

**If tests PASS:**
- Proceed to 5.2

#### 5.2 Stage Changes

```bash
git add .
```

**Verify staged changes:**
```bash
git status
git diff --staged
```

#### 5.3 Clean Up

Before committing:
- Remove temporary files
- Remove debug print statements
- Remove commented-out code (unless intentionally kept)
- Ensure no secrets or credentials in code
- Verify all new files are staged

#### 5.4 Create Commit

Use **conventional commit format** with heredoc for proper formatting:

```bash
git commit -m "$(cat <<'EOF'
feat: implement user authentication model

- Created SQLAlchemy User model with email and password fields
- Added timestamps (created_at, updated_at) for audit trail
- Implemented unique constraint on email with index
- Added comprehensive docstrings explaining model purpose
- Password stored as bcrypt hash (not plaintext)

Completed: Task 1.0 - Set up authentication infrastructure
Related: /tasks/user-authentication/prd.md

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"
```

**Conventional Commit Prefixes:**
- `feat:` - New feature
- `fix:` - Bug fix
- `refactor:` - Code refactoring (no functional change)
- `docs:` - Documentation updates
- `test:` - Adding or updating tests
- `chore:` - Maintenance tasks (dependencies, config)
- `perf:` - Performance improvements
- `style:` - Code style changes (formatting, no logic change)

#### 5.5 Mark Parent Task Completed

**Sync both systems immediately:**

**Update TodoWrite:**
```json
{
  "content": "Set up authentication infrastructure",
  "activeForm": "Setting up authentication infrastructure",
  "status": "completed"
}
```

**Update Markdown:** (in same response)
```markdown
- [x] 1.0 Set up authentication infrastructure
  - [x] 1.1 Create User model with authentication fields
  - [x] 1.2 Create migration file for users table
  - [x] 1.3 Run database migration
```

**Verify Sync:**
- TodoWrite parent task: `status: "completed"`
- Markdown parent task: `[x]`
- All sub-tasks also marked complete in both systems

#### 5.6 Update Documentation

After completing a **full parent task**, update documentation:

**1. Create/Update Component Documentation**

If this is a new feature or significant change, create component documentation:

```bash
# Create documentation in appropriate module directory
/docs/component_docs/[module-name]/[feature-name].md
```

Follow the [Documentation Requirements Guide](./documentation-requirements.md) template.

**Required sections:**
- Overview (purpose, key functionality)
- Architecture (dependencies, system context)
- Implementation Files (core files, supporting files, tests)
- Data Flow (input, processing, output)
- Database Interactions (tables used, query patterns)
- Configuration (environment variables, settings)
- Error Handling
- Security Considerations
- Usage Examples
- Related Documentation

**2. Update Master Changelog**

```bash
# Edit docs/changelogs/master-changelog.md
```

**Format:**
```markdown
## 2025-10-06

### User Authentication Feature

- **Version:** 4.01 (minor increment)
- **Task:** 1.0 - Set up authentication infrastructure
- **Changes:**
  - Created SQLAlchemy User model with authentication fields
  - Added database migration for users table
  - Implemented bcrypt password hashing
  - Added comprehensive inline and component documentation
- **Files Modified:**
  - `modules/auth/user_model.py` (new)
  - `database_tools/migrations/003_add_users_table.sql` (new)
  - `modules/database/models.py` (updated imports)
- **Documentation:**
  - Created `/docs/component_docs/authentication/auth_system.md`
  - Added inline docstrings to all functions and classes
- **Tests:** All passing (3 new unit tests added)
- **Related:** `/tasks/user-authentication/prd.md`
```

**3. Archive Outdated Documentation**

If this task replaces or significantly modifies existing functionality:

```bash
# Move outdated documentation to archived location
mv /docs/component_docs/[module]/old_doc.md \
   /docs/archived/component_docs/[module]/old_doc_deprecated_YYYY-MM-DD.md
```

**Add deprecation notice** to archived file:
```markdown
# [Original Title]

> **DEPRECATED:** 2025-10-06
> **Replaced By:** /docs/component_docs/[module]/new_doc.md
> **Reason:** [Brief explanation of why this was replaced]
>
> This documentation is archived for historical reference only.

[Original content follows...]
```

**Update changelog** with archival info:
```markdown
- **Documentation Archived:**
  - `docs/component_docs/auth/old_oauth_flow.md` → `docs/archived/component_docs/auth/old_oauth_flow_deprecated_2025-10-06.md`
  - Reason: Replaced by new OAuth 2.0 implementation
```

#### 5.7 Update Version Number

Update `CLAUDE.md` line 3:

```markdown
# Automated Job Application System
Version 4.01 (Update the version number during development...)
```

**Version Increment Rules:**
- **Major changes (x.0):** New major features, breaking changes, significant refactors
- **Minor changes (0.xx):** Small features, bug fixes, incremental improvements

### Step 6: Move to Next Section

After completing a section (including commit and changelog):
1. Mark next section's first task as `in_progress`
2. Return to Step 2 (Execute)
3. Repeat until all sections completed

## Automatic Checkpoints and Commits

**Instead of manual commit workflow, use automated scripts:**

See [Automatic Checkpoints & Commits Guide](./automatic-checkpoints-commits.md) for details.

**Checkpoint (after 3+ tasks):**
```bash
git add .
./scripts/checkpoint.sh "Section Name" "Completed tasks 1.1-1.3"
```

**Section Commit (all tasks complete):**
```bash
git add .
./scripts/commit-section.sh "Section Name" "feat|fix|docs" "/tasks/feature/prd.md"
```

**Scripts automatically handle:**
- ✅ Running tests
- ✅ Database schema automation
- ✅ Documentation verification
- ✅ Commit message generation
- ✅ Version updates
- ✅ Changelog template generation

**Agent just needs to:**
1. Stage files
2. Run appropriate script
3. Answer confirmations
4. Update changelog when prompted

## TodoWrite Status Management

### The One-In-Progress Rule

**CRITICAL:** Only ONE task can have status `in_progress` at any time.

**Valid State:**
```json
[
  {"content": "Set up auth infrastructure", "status": "completed"},
  {"content": "Implement auth logic", "status": "in_progress"},  ← Only one
  {"content": "Create auth tests", "status": "pending"},
  {"content": "Write documentation", "status": "pending"}
]
```

**INVALID State:**
```json
[
  {"content": "Set up auth infrastructure", "status": "in_progress"},  ← Two!
  {"content": "Implement auth logic", "status": "in_progress"},        ← Two!
  {"content": "Create auth tests", "status": "pending"}
]
```

### Status Transitions

**Valid transitions:**
```
pending → in_progress → completed
pending → in_progress → pending (if need to defer)
```

**Invalid transitions:**
```
pending → completed (must go through in_progress)
completed → in_progress (don't re-open, create new task)
```

### Real-Time Updates

Update TodoWrite **immediately** when:
- ✅ Starting a sub-task (mark `in_progress`)
- ✅ Completing a sub-task (mark `completed`)
- ✅ Completing a parent task (mark `completed`)
- ✅ Discovering a new task (add with `pending`)

**DO NOT:**
- ❌ Wait to batch multiple updates
- ❌ Update at end of work session
- ❌ Skip TodoWrite and only update markdown

## Code Quality Standards

### Inline Documentation

**Always add comprehensive docstrings and comments:**

```python
def validate_password(password: str) -> tuple[bool, str]:
    """
    Validate password strength according to security requirements.

    Password must meet the following criteria:
    - Minimum 12 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one number
    - At least one special character (!@#$%^&*)

    Args:
        password (str): The password to validate

    Returns:
        tuple[bool, str]: (is_valid, error_message)
            - is_valid: True if password meets all requirements
            - error_message: Empty string if valid, error description if invalid

    Examples:
        >>> validate_password("short")
        (False, "Password must be at least 12 characters")

        >>> validate_password("SecureP@ssw0rd!")
        (True, "")
    """
    if len(password) < 12:
        return False, "Password must be at least 12 characters"

    # ... implementation
```

### Error Handling

**Implement comprehensive error handling:**

```python
def create_user(email: str, password: str) -> User:
    """
    Create a new user with email and hashed password.

    Raises:
        ValueError: If email format is invalid
        ValueError: If password doesn't meet strength requirements
        IntegrityError: If email already exists in database
    """
    # Validate email format
    if not is_valid_email(email):
        raise ValueError(f"Invalid email format: {email}")

    # Validate password strength
    is_valid, error = validate_password(password)
    if not is_valid:
        raise ValueError(f"Password validation failed: {error}")

    try:
        # Hash password and create user
        password_hash = hash_password(password)
        user = User(email=email, password_hash=password_hash)
        db.session.add(user)
        db.session.commit()
        return user

    except IntegrityError as e:
        db.session.rollback()
        logger.error(f"Failed to create user {email}: {e}")
        raise ValueError(f"User with email {email} already exists")
```

### Testing

**Write tests as part of implementation:**

```python
# modules/auth/test_user_model.py

import pytest
from modules.auth.user_model import User
from modules.database import db

class TestUserModel:
    """Test suite for User model."""

    def test_user_creation(self):
        """Test creating a user with valid email and password."""
        user = User(
            email="test@example.com",
            password_hash="$2b$12$hashed_password"
        )
        db.session.add(user)
        db.session.commit()

        assert user.id is not None
        assert user.email == "test@example.com"
        assert user.created_at is not None

    def test_duplicate_email_constraint(self):
        """Test that duplicate emails are rejected."""
        user1 = User(email="dup@example.com", password_hash="hash1")
        db.session.add(user1)
        db.session.commit()

        user2 = User(email="dup@example.com", password_hash="hash2")
        db.session.add(user2)

        with pytest.raises(IntegrityError):
            db.session.commit()
```

## Database Schema Changes

When tasks involve database changes, **ALWAYS** use automated tools:

### Required Workflow

1. **Make schema changes** to PostgreSQL database
2. **Run automation:** `python database_tools/update_schema.py`
3. **Commit generated files** to version control

### Prohibited Actions

- ❌ Manually edit `frontend_templates/database_schema.html`
- ❌ Manually edit files in `docs/component_docs/database/`
- ❌ Manually edit files in `database_tools/generated/`
- ❌ Skip running automation after schema changes

### Example Task Execution with Database Changes

```markdown
- [ ] 1.0 Database Schema Updates
  - [x] 1.1 Create migration file for users table
  - [x] 1.2 Run migration on development database
  - [x] 1.3 Run database_tools/update_schema.py to generate docs
  - [x] 1.4 Verify generated documentation is accurate
  - [x] 1.5 Stage and commit all changes including generated files
```

## Hooks Integration (Future)

Claude Code supports hooks for automation. Consider implementing:

### Pre-Commit Hook Example

```json
{
  "hooks": {
    "PreToolUse": {
      "Bash": {
        "command": "if [[ \"$TOOL_NAME\" == \"Bash\" ]] && [[ \"$COMMAND\" =~ ^git\\ commit ]]; then pytest; fi",
        "description": "Run tests before allowing commits"
      }
    }
  }
}
```

**This would automatically:**
- Run test suite before every commit
- Block commit if tests fail
- Provide immediate feedback

### Post-Completion Hook Example

```json
{
  "hooks": {
    "PostToolUse": {
      "TodoWrite": {
        "command": "if [[ \"$STATUS\" == \"completed\" ]]; then echo '✅ Task completed!' >> progress.log; fi",
        "description": "Log task completions"
      }
    }
  }
}
```

## Troubleshooting

### Problem: Tests Failing After Implementation

**Solution:**
1. Keep parent task as `in_progress`
2. Create new sub-task: "Debug and fix failing tests"
3. Mark as `in_progress`
4. Investigate failures
5. Fix issues
6. Re-run tests
7. Mark sub-task `completed` when passing
8. Then mark parent task `completed`

### Problem: Multiple Tasks Show In Progress

**Solution:**
1. Review TodoWrite entries
2. Identify which task is actually being worked on
3. Mark others as `pending` or `completed` as appropriate
4. Only keep current task as `in_progress`

### Problem: Forgot to Update TodoWrite

**Solution:**
1. Review markdown task file
2. Identify completed tasks
3. Bulk update TodoWrite to match reality
4. Establish habit of immediate updates going forward

### Problem: Commit Blocked by Pre-Commit Hook

**Solution:**
1. Review hook error message
2. Fix identified issues (formatting, linting, tests)
3. Re-stage changes: `git add .`
4. Retry commit
5. If hook is incorrect, discuss with user before modifying

## Complete Project Archival

After **all tasks completed** and **user verification:**

### Archival Process

1. **Move feature directory:**
   ```bash
   mv /tasks/[feature-name]/ /docs/archived/[subdirectory]/[feature-name]/
   ```

2. **Preserve all files:**
   - `prd.md`
   - `tasklist_1.md`, `tasklist_2.md`, etc.
   - `notes.md` (if exists)
   - Any other related documentation

3. **Update master changelog:**
   ```markdown
   ## Project Archived: [Feature Name]

   - **Date:** 2025-10-06
   - **Location:** `/docs/archived/[subdirectory]/[feature-name]/`
   - **Status:** Completed and verified
   - **Version:** 4.1
   ```

4. **Update CLAUDE.md:**
   - Document project completion
   - Update system overview if feature changes architecture
   - Increment major version if significant

## Examples

### Example 1: Simple Sub-Task Execution
See task execution for: `/tasks/password-reset/tasklist_1.md` Task 1.1

### Example 2: Parent Task with Testing
See task execution for: `/tasks/user-authentication/tasklist_1.md` Task 2.0

### Example 3: Database Schema Change Task
See task execution for: `/tasks/job-scraping/tasklist_1.md` Task 1.0

## Incremental Improvements

After completing several features, consider:

**Immediate Additions:**
- Add pre-commit hook to run tests automatically (prevents committing broken code)
- Create shell aliases for common commands (`alias run-schema='python database_tools/update_schema.py'`)
- Document common error patterns and solutions as you encounter them

**Quality Improvements:**
- Track how long tasks actually take vs estimates
- Note which types of tasks consistently need more sub-tasks
- Keep a list of frequently forgotten steps (e.g., running schema automation)

**Evaluate after:** 2-3 completed features to see what would help most

---

**Document Owner:** Development Team
**Related Guides:**
- [Automated Task Workflow](./automated-task-workflow.md)
- [PRD Generation Guide](./prd-generation-guide.md)
- [Task Generation Guide](./task-generation-guide.md)

**Last Reviewed:** October 6, 2025
