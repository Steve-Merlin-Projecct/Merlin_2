# File Organization Standards

**Purpose:** Define clear standards for file placement, naming, and organization across the project

**Version:** 1.0
**Created:** October 8, 2025

## Directory Structure Guide

### Root Directory (`/workspace`)
**Purpose:** Essential project files only

**Allowed Files:**
- `README.md` - Project overview
- `CLAUDE.md` - AI assistant instructions
- `CHANGELOG.md` - High-level project changelog (redirects to docs/changelogs/)
- `app_modular.py` - Main Flask application
- `main.py` - Alternative entry point
- `requirements.txt` - Python dependencies
- `pyproject.toml` - Python project configuration
- `VERSION` - Version number file
- `docker-compose.yml` - Docker configuration
- `.env` (gitignored) - Environment variables
- `.gitignore` - Git ignore rules

**Prohibited:**
- Test files (→ `/tests`)
- Documentation files (→ `/docs`)
- Temporary files
- Data files (→ `/storage` or `/data`)
- Status/summary files (→ `/docs/git_workflow/branch-status/`)

### Documentation (`/docs`)

#### Active Documentation
- `/docs/api/` - API documentation and specifications
- `/docs/architecture/` - System architecture docs
- `/docs/automation/` - Automation scripts and guides
- `/docs/changelogs/` - Version changelogs
- `/docs/component_docs/` - Component-specific documentation
- `/docs/integrations/` - Third-party integration docs
- `/docs/workflows/` - Development workflows and processes
- `/docs/git_workflow/` - Git-specific workflows

#### Historical/Archive
- `/docs/archived/migrations/` - Completed migration documentation
- `/docs/archived/replit-git-workflow/` - Obsolete Replit-specific git docs
- `/docs/archived/replit-migration/` - Historical Replit migration tasks

### Code Organization

#### Modules (`/modules`)
- One subdirectory per functional module
- Each module should be self-contained
- Module-specific README.md files allowed

#### Database Tools (`/database_tools`)
- Schema management scripts
- Database automation tools
- Generated code (models, CRUD, routes)

#### Tests (`/tests`)
- `/tests/unit/` - Unit tests
- `/tests/integration/` - Integration tests
- `/tests/fixtures/` - Test data and fixtures
- `/tests/e2e/` - End-to-end tests

### Storage & Data

- `/storage/` - Generated documents and files (gitignored)
- `/data/` - Application data files
- `/templates/` - Document templates (.docx files)
- `/frontend_templates/` - HTML templates for web UI

### Configuration & Scripts

- `/.devcontainer/` - VS Code devcontainer configuration
- `/.claude/` - Claude Code settings and commands
- `/scripts/` - Utility scripts and automation tools
- `/.github/` - GitHub-specific files (workflows, templates)

## Naming Conventions

### Documentation Files
**Standard:** `lowercase-with-hyphens.md`

**Examples:**
- ✅ `file-organization-standards.md`
- ✅ `github-connectivity-solution.md`
- ✅ `branch-review-workflow.md`
- ❌ `BRANCH_STATUS.md` (uppercase - legacy style)
- ❌ `FileOrganization.md` (camelCase)
- ❌ `file_organization.md` (underscores - use for code only)

**Exception:** Root-level files may use UPPERCASE (e.g., `README.md`, `CLAUDE.md`, `CHANGELOG.md`)

### Python Files
**Standard:** `snake_case.py`

**Examples:**
- ✅ `app_modular.py`
- ✅ `test_db_connection.py`
- ✅ `schema_automation.py`
- ❌ `AppModular.py` (PascalCase - use for class names only)
- ❌ `app-modular.py` (hyphens - use for docs)

### Branch Status Files
**Location:** `/docs/git_workflow/branch-status/`
**Pattern:** `<branch-name>.md`

**Examples:**
- ✅ `/docs/git_workflow/branch-status/feature-task-guiding-documentation.md`
- ✅ `/docs/git_workflow/branch-status/feature-email-integration.md`

## File Placement Decision Tree

### For Documentation Files

```
Is it a status/summary file?
├─ Yes: Is it branch-specific?
│  ├─ Yes → /docs/git_workflow/branch-status/<branch-name>.md
│  └─ No: Is it migration-related?
│     ├─ Yes → /docs/archived/migrations/<filename>.md
│     └─ No → /docs/<category>/<filename>.md
│
└─ No: Is it current/active documentation?
   ├─ Yes → /docs/<appropriate-category>/<filename>.md
   └─ No → /docs/archived/<category>/<filename>.md
```

### For Code Files

```
Is it a test file?
├─ Yes: What type?
│  ├─ Unit test → /tests/unit/test_<name>.py
│  ├─ Integration → /tests/integration/test_<name>.py
│  └─ E2E → /tests/e2e/test_<name>.py
│
└─ No: Is it a module?
   ├─ Yes → /modules/<module-name>/<filename>.py
   └─ No: Is it a database tool?
      ├─ Yes → /database_tools/<filename>.py
      └─ No: Is it a script?
         ├─ Yes → /scripts/<filename>.py
         └─ No → Reconsider if it belongs in root
```

### For Configuration Files

```
Is it environment-specific?
├─ Yes: Is it sensitive?
│  ├─ Yes → .env (gitignored)
│  └─ No → .env.example or config/<name>.yaml
│
└─ No: What type of config?
   ├─ Docker → docker-compose.yml or .devcontainer/
   ├─ Claude → .claude/
   ├─ Python → pyproject.toml
   └─ GitHub → .github/
```

## Archive Guidelines

### When to Archive

Archive documentation when:
- Project has moved to different infrastructure (e.g., Replit → Docker)
- Feature/branch has been merged and reviewed
- Documentation is historical but valuable for reference
- Documentation is obsolete but shouldn't be deleted

### Archive Directory Structure

```
/docs/archived/
├─ migrations/          # Completed migration docs
├─ replit-git-workflow/ # Obsolete Replit-specific workflows
├─ replit-migration/    # Historical migration tasks
└─ <category>/          # Other archived categories
```

### Archive README Requirements

Each archive directory MUST include a `README.md` with:
- Purpose of archived files
- Date range of relevance
- Reason for archival
- Related active documentation (if any)

## Git Workflow File Organization

### Branch Status Files
- **Location:** `/docs/git_workflow/branch-status/`
- **Naming:** `<branch-name>.md`
- **When to create:** When a feature branch is ready for review/archival
- **When to update:** After merge, after review, before branch deletion

### Workflow Documentation
- **Location:** `/docs/workflows/`
- **Purpose:** Reusable workflow guides (not branch-specific)
- **Examples:**
  - `branch-review-workflow.md`
  - `task-execution-workflow.md`
  - `deployment-workflow.md`

### Git-Specific Technical Docs
- **Location:** `/docs/git_workflow/`
- **Purpose:** Technical git procedures and configuration
- **Examples:**
  - `MANUAL_MERGE_RESOLUTION.md`
  - `SMART_SCHEMA_ENFORCEMENT.md`

## Examples of Correct Placement

### ✅ Good Examples

**Branch status for feature:**
```
/docs/git_workflow/branch-status/feature-task-guiding-documentation.md
```

**Migration completion summary:**
```
/docs/archived/migrations/migration-complete.md
```

**Integration documentation:**
```
/docs/integrations/google-drive-implementation.md
```

**Test file:**
```
/tests/integration/test_db_connection.py
```

**Workflow guide:**
```
/docs/workflows/branch-review-workflow.md
```

### ❌ Bad Examples (and corrections)

**Branch status in root:**
```
❌ /workspace/BRANCH_STATUS.md
✅ /docs/git_workflow/branch-status/feature-name.md
```

**Test file in root:**
```
❌ /workspace/test_db_connection.py
✅ /tests/integration/test_db_connection.py
```

**Summary file in root:**
```
❌ /workspace/MIGRATION_COMPLETE.md
✅ /docs/archived/migrations/migration-complete.md
```

## Special Cases

### Sensitive Files
Always add to `.gitignore`:
- `cookies.txt`
- `*.pem`, `*.key`
- `credentials*.json`
- `token*.json`
- `.env.local`, `.env.production`

### Generated Files
- Database schema HTML → `frontend_templates/database_schema.html`
- Generated SQLAlchemy models → `database_tools/generated/`
- Generated documents → `storage/` (gitignored)

### Temporary Files
Always gitignore, never commit:
- `/tmp/`, `/temp/`
- `*.log` files
- `.cache/`, `.local/`
- Backup files (`*.backup`, `*.bak`)

## Maintenance

### Regular Reviews
- Monthly: Review root directory for file accumulation
- Per feature: Ensure new files follow standards
- Post-merge: Move branch status to appropriate location
- Quarterly: Review archive structure

### Enforcement
- Pre-commit hooks (future enhancement)
- PR review checklist item
- Documentation in CLAUDE.md
- This standards document

## Questions & Decisions

### "Where should this file go?"
1. Consult decision tree above
2. Check examples in this document
3. Look for similar existing files
4. When in doubt, ask in PR review

### "Should I archive or delete?"
**Archive if:**
- Historical value exists
- Context needed for future decisions
- Documentation effort was significant

**Delete if:**
- Truly obsolete with no historical value
- Duplicates better documentation
- Contains sensitive data (gitignore first)

## Version History

- **v1.0** (2025-10-08): Initial standards document created during file organization cleanup
