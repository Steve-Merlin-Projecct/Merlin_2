---
title: System Instructions (CLAUDE.md)
type: reference
created: 2024-08-15
modified: 2025-10-24
status: current
related: README.md, docs/DOCUMENTATION_INDEX.md
---

# Automated Job Application System
Version 4.5.1
Python 3.11 | Flask | PostgreSQL | Docker
Last Updated: 2025-10-24

## Project Overview

AI-driven job application automation system that scrapes job postings, analyzes them with Google Gemini AI, and generates personalized resumes and cover letters from templates.

**For detailed documentation, see:**
- Architecture & Components: `docs/architecture/`
- Database Configuration: `docs/database-connection-guide.md`
- Environment Setup: `docs/setup/`
- API Documentation: `docs/api/`


### Context Priming

Use dedicated context files for domain-specific knowledge rather than loading everything:
- Load relevant architecture docs when working on system design
- Load database schema docs when working on data models
- Load API docs when working on integrations
- Use `/task` templates to automatically load appropriate context

**Philosophy:** Prime the context window specifically for the task at hand, not with static universal knowledge.

**Database Schema Management Policy:**
Always use automated database tools instead of manual changes.
Required Workflow:
1. Make schema changes to PostgreSQL database.
2. Run: `python database_tools/update_schema.py`.
3. Commit generated files to version control.

Prohibited Actions:
- Never manually edit `frontend_templates/database_schema.html`.
- Never manually edit files in `docs/component_docs/database/`.
- Never manually edit files in `database_tools/generated/`.
- Never skip running automation after schema changes.

**Git Operations Policy:**
Always delegate git operations to the git-orchestrator agent instead of using Bash directly.

Required Workflow:
1. When user requests git actions ("commit", "push", "merge", "git commit", etc.)
2. Use Task tool to invoke git-orchestrator agent with appropriate pattern:
   - `git-orchestrator "user_commit:Description"` - For user-requested commits/pushes
   - `git-orchestrator "checkpoint_check:Section Name"` - For checkpoints during work
   - `git-orchestrator "commit_section:Section Name"` - For completed section milestones

Agent Benefits:
- Automated test suite execution before commits
- Schema change detection and automation
- Documentation validation
- Conventional commit message formatting
- Automatic remote push with error recovery
- Structured response generation

Prohibited Actions:
- Never use Bash tool for: `git add`, `git commit`, `git push`, `git merge`
- Never manually create commits without validation
- Never skip test runs before committing

**Work Estimation Policy:**
Always provide work estimates in tokens, not traditional time units (hours/days).

Context:
- AI agent execution is near-instantaneous (seconds, not hours)
- Token consumption is the actual resource constraint for agent work
- Traditional time estimates are misleading and create false expectations
- User effort (manual review, decision-making) should still use time estimates

Estimation Guidelines:
- **Small tasks:** 5,000-15,000 tokens
  - Simple file edits, single-file refactoring, basic documentation updates
  - Examples: Updating configuration, adding docstrings, simple bug fixes
- **Medium tasks:** 15,000-50,000 tokens
  - Multi-file changes, moderate refactoring, feature additions
  - Examples: Adding new endpoints, updating related components, comprehensive testing
- **Large tasks:** 50,000-100,000+ tokens
  - System-wide changes, architectural updates, complex feature implementations
  - Examples: Database migrations, security overhauls, major feature rollouts

Work Type Distinction:
- **Agent work:** Estimate in tokens (code changes, analysis, generation)
- **User work:** Estimate in time (reviews, testing, manual configurations)
- **Combined work:** Provide separate estimates for each component

Examples:
```
Correct:
"This refactoring will consume approximately 25,000 tokens for code changes,
plus 15 minutes for you to review and test the changes."

Incorrect:
"This will take about 2 hours to complete."
(Misleading - agent completes work in seconds)
```

Prohibited Actions:
- Never estimate agent work in hours, days, or other time units
- Never use vague estimates like "quickly" or "soon" without token counts
- Never omit estimates for substantial work (>5,000 tokens)
- Never combine agent token estimates with user time estimates into single number

**Worktree Error Prevention System (NEW - v4.3.3):**
The `/tree build` command now includes comprehensive error prevention:
- Pre-flight validation detects and removes orphaned directories/branches
- Automatic `git worktree prune` on every build
- Stale lock detection and auto-removal (>60s old, 0 bytes)
- Atomic rollback on build failures
- Enhanced error messages showing actual git output
- Verbose mode via `--verbose` flag or `TREE_VERBOSE=true`
- Idempotent operations (safe to retry builds)
- Uncommitted changes protection

**Usage:**
```bash
/tree build                    # Standard with auto-cleanup
/tree build --verbose          # Debug mode
TREE_VERBOSE=true /tree build  # Verbose via env var
```

See: `tasks/worktree-error-prevention/` for full documentation

**Slash Command Loading in Worktrees (Known Limitation - v4.5.1):**
Claude Code CLI only scans `.claude/commands/` on session initialization, not when changing directories with `cd`.

**Symptoms:**
- `/tree` or `/task` show "Unknown slash command" error in worktrees
- Command files exist and are copied correctly to worktrees
- Only affects mid-session directory changes

**Workarounds:**
1. **Quick Fix:** Use direct script execution
   ```bash
   bash /workspace/.claude/scripts/tree.sh <command>
   ```
2. **Permanent Fix:** Restart CLI session from worktree directory
   ```bash
   exit
   cd /workspace/.trees/<worktree-name>
   claude code
   ```

**Diagnostics:** Run `/tree refresh` or `bash /workspace/.claude/scripts/tree.sh refresh`

**Auto-Documentation:** All new worktrees automatically include workaround instructions in PURPOSE.md

See: `tasks/slash-command-worktree-loading/` for full investigation report



### Documentation Standards

**Inline Documentation:**
- Add comprehensive docstrings to all functions and classes
- Explain relationships between components
- Document expected behaviors and edge cases
- Use comments to explain "why" not just "what"

**Knowledge Capture:**
- When gaining new project understanding, document it appropriately
- Update relevant context files (not always CLAUDE.md)
- Keep documentation close to the code it describes

**Research Preferences:**
- Always check for the latest versions of dependencies before suggesting updates.
- Research current best practices for security implementations.

**External Research Guidelines:**
- When suggesting new libraries, ensure compatibility with our existing stack.
- Adapt external examples to match our coding standards and project structure.

**Librarian System:**
The project uses automated documentation management and validation tools:
- **Validation**: Pre-commit hooks and CI/CD workflows enforce YAML frontmatter and file organization standards
- **Search**: Searchable catalog (SQLite FTS5) with 511+ indexed documents
- **Archival**: Automated stale documentation detection and lifecycle management
- **Metrics**: Track documentation coverage, quality, and health

**Quick Commands:**
```bash
python tools/validate_metadata.py --all --fix  # Add/fix YAML frontmatter
python tools/build_index.py --incremental      # Update search catalog
python tools/query_catalog.py --keywords "api" # Search documentation
python tools/collect_metrics.py --report       # Generate health report
```

**See:** `docs/librarian-tools-reference.md` for complete documentation

### Code Quality Standards

**Style:**
- Use consistent naming patterns and code organization
- Group related functions together
- Use clear, descriptive names that convey intent
- Follow PEP 8 for Python code

**Quality Tools:**
- Black: Code formatting
- Flake8: Linting and style checking
- Vulture: Dead code detection
- pytest: Testing framework

**Standards:**
- Write testable code with clear separation of concerns
- Prefer explicit over implicit
- Handle errors gracefully with proper logging
- Use type hints where they add clarity

**See:** `docs/code-quality-standards.md` for detailed guidelines
<!-- critical: do not change anything above this line -->

## Technical Stack & Architecture

**Core Technologies:** Flask, PostgreSQL, SQLAlchemy, Docker, Google Gemini AI

**Key Architectural Patterns:**
- Modular Flask microservices with Blueprint pattern
- Security-first design (authentication, input validation, rate limiting)
- Template-based document generation with storage abstraction layer
- Automated database schema management with code generation
- Git operations automation via git-orchestrator agent

**For detailed architecture documentation, see:** `docs/architecture/system-overview.md`

## Project-Specific Workflows

### Database Schema Changes
Always use automated tools (never manual edits):
1. Make schema changes to PostgreSQL database
2. Run: `python database_tools/update_schema.py`
3. Commit generated files to version control

**See:** `docs/database-schema-workflow.md`

### Task Workflows
Use the `/task` command with appropriate templates:
- `/task go [description]` - Autonomous implementation (minimize user time)
- `/task slow [description]` - Collaborative with user checkpoints
- `/task analyze [description]` - Analysis without implementation
- `/task research [description]` - Technology evaluation
- `/task communicate [description]` - Human-friendly documentation

**See:** `.claude/README-WORKFLOWS.md`

## Environment Variables

All sensitive credentials are stored in the `.env` file (which is gitignored). The system now uses **environment-aware database configuration** that automatically detects Docker vs local environments.

### Database Configuration
The system automatically detects the runtime environment:
- **Docker Container**: Uses `DATABASE_HOST=host.docker.internal` with container environment variables
- **Local Development**: Uses `localhost` with `.env` file settings

Key environment variables:
- `PGPASSWORD`: PostgreSQL database password (required for both environments)
- `DATABASE_NAME`: Database name (default: `local_Merlin_3`)
- `DATABASE_URL`: Full PostgreSQL connection string (optional override)
- `WEBHOOK_API_KEY`: API authentication key
- `STORAGE_BACKEND`: Storage backend type (default: `local`)
- `LOCAL_STORAGE_PATH`: Path for local filesystem storage (default: `./storage/generated_documents`)

**Connection Priority:**
1. Explicit `DATABASE_URL` (highest priority - bypasses auto-detection)
2. Individual components (`DATABASE_HOST`, `DATABASE_PORT`, etc.)
3. Fallback defaults (`localhost` for local, container settings for Docker)

**Configuration Files:**
- `.env`: Local development settings
- `docker-compose.yml`: Docker container environment variables
- `.devcontainer/devcontainer.json`: VS Code devcontainer settings

See [Database Connection Guide](docs/database-connection-guide.md) for detailed configuration instructions.

The `.claude/settings.local.json` file references these environment variables (e.g., `$PGPASSWORD`) instead of hardcoding credentials.

## Overview

This AI-driven job application ecosystem automates and enhances the job search experience. It scrapes job postings, uses Google Gemini AI for sophisticated analysis and ranking, and generates personalized resumes and cover letters from variable-based templates. The system boasts a normalized PostgreSQL database across 32 tables, ensuring an optimal relational structure for comprehensive data management. The project's vision is to transform job searching through intelligent technology, offering a significant advantage in the job market.
<!-- critical: do not change anything below this line -->
## Communication & Implementation Guide

Before implementing changes, explain what you're going to do and why.
Break down complex tasks into clear, focused steps.
Ask for clarification if requirements are unclear.
Provide explanations for technical decisions.
Create inline documentation for sensemaking of codebase.


**Analysis vs Implementation Guidelines:**
When to Provide Analysis Only:
  - Questions starting with "How do we...", "What are...", "Why does...", "Can you explain..."
  - Requests for recommendations, comparisons, or evaluations
  - Asking about best practices, trade-offs, or architectural decisions
  - Seeking understanding of current state or problem diagnosis
  - Request to review or understand documents or data
  - Explicit question words ALWAYS trigger analysis mode, regardless of context
  - Compound statements: Problem + explanation request (e.g., "This is broken. Can you explain why?") and Mixed requests: When both informational and actionable elements are present, treat as analysis first
  - "X is missing. Can you explain?" → Analysis (focuses on "explain")
  - "This doesn't work. Why?" → Analysis (focuses on "Why")
  - "The system failed. What happened?" → Analysis (focuses on "What")
    
When to Implement:
  - Direct commands: "Fix...", "Update...", "Create...", "Implement..."
  - "Please make these changes...", "Can you code..."
  - Following up analysis with "Let's do that" or "Go ahead with option X"
  - Specific bug reports with implied fix request

Default Behavior:
  - When intent is unclear, always default to analysis first.
  - After providing analysis, ask "Would you like me to implement any of these suggestions?"
  - Wait for explicit confirmation before making code changes.

User Can Use Qualifier Phrases:
  - "Just analyze..." or "Don't implement, but..."
  - "I need information about..."
  - "What's your assessment of..."

**Proposed Communication Patterns:**
For Analysis Requests The Agent should:
  1. Provide clear, structured analysis.
  2. Offer options with pros/cons.
  3. Explain current state without changing it.
  4. Ask "Would you like me to implement any of these suggestions?" at the end.

For Implementation Requests the Agent should:
  1. Briefly confirm understanding.
  2. Outline the implementation plan.
  3. Execute the changes.
  4. Report results.

- Before implementing changes, agent will explain what the agent is going to do and why.
- Break down complex tasks into clear, focused steps.
- Ask for clarification if requirements are unclear.
- Provide brief explanations for technical decisions.

**Database Schema Management Policy:**
Always use automated database tools instead of manual changes.
Required Workflow:
1. Make schema changes to PostgreSQL database.
2. Run: `python database_tools/update_schema.py`.
3. Commit generated files to version control.

Prohibited Actions:
- Never manually edit `frontend_templates/database_schema.html`.
- Never manually edit files in `docs/component_docs/database/`.
- Never manually edit files in `database_tools/generated/`.
- Never skip running automation after schema changes.

**Documentation:**
- Add detailed inline documentation on all new or changed code. Add comprehensive docstrings and comments directly in your code that explain relationships between functions and expected behaviors.
- When new understanding of the project is gained, document the changes in CLAUDE.md.

**Agent Usage Documentation:**
- Document all significant agent usage decisions and patterns in `docs/agent-usage-guide.md`.
- When choosing to use (or not use) a specialized agent, add the reasoning as a teachable moment in the guide.
- Include context, decision rationale, metrics (tool calls, tokens), and lessons learned.
- Update best practices section when new usage patterns emerge.
- Focus on documenting border cases where the choice between direct tools vs. agents is not obvious.

**Research Preferences:**
- Always check for the latest versions of dependencies before suggesting updates.
- Research current best practices for security implementations.

**External Research Guidelines:**
- When suggesting new libraries, ensure compatibility with our existing stack.
- Adapt external examples to match our coding standards and project structure.

**Style:**
- Use consistent naming patterns and code organization. Group related functions together and use clear, descriptive names.
<!-- critical: do not change anything above this line -->
## System Architecture

The application employs a modular Flask microservice architecture with a strong emphasis on security.

**Core Architectural Decisions:**
- **Flask Framework:** Chosen for its lightweight nature, ideal for focused webhook processing with enterprise-grade security.
- **Modular Design:** Code is organized into separate modules (`/modules`) for clear separation of concerns, scalability, and security isolation.
- **Blueprint Pattern:** Flask blueprints organize routes, separating webhook logic from the main application.
- **Security-First:** All components implement comprehensive security controls including authentication, input validation, rate limiting, and audit logging.
- **Template-Based Document Generation:** Utilizes a `BaseGenerator Class` and specialized generators to create personalized documents from `.docx` templates, preserving original formatting and structure.
- **Storage Abstraction Layer:** Documents are stored using a pluggable storage backend system supporting local filesystem (default) with future support for cloud providers (AWS S3, Google Cloud Storage).
- **Automated Database Schema Management:** Uses a suite of tools (`database_tools/`) to generate SQLAlchemy models, Pydantic schemas, CRUD operations, and Flask API routes directly from the live PostgreSQL schema, ensuring documentation and code consistency. Pre-commit hooks prevent manual schema changes.
- **Resilience System:** Includes a comprehensive failure recovery mechanism with intelligent retry logic, circuit breaker patterns, workflow checkpoints, and automatic data correction.
- **Git Operations Automation:** git-orchestrator agent handles all version control operations (checkpoints, section commits) with automatic validation (tests, schema automation, documentation checks), error recovery, and remote push integration.

**Key Components & Features:**

- **Main Application (`app_modular.py`):** Flask application initialization and configuration, proxy middleware setup, health check endpoint, blueprint registration.
- **Document Generation (`modules/document_generation/`):** Template-based generation from `.docx` files, preserving formatting, professional metadata, and storage backend integration.
- **Storage Layer (`modules/storage/`):** Abstraction layer for file storage with local filesystem implementation and future cloud provider support.
- **Gmail Integration (`modules/email_integration/`):** Official Gmail OAuth 2.0, robust email sending with attachments, enhanced error handling, and RFC-compliant validation.
- **AI Job Description Analysis (`modules/ai_job_description_analysis/`):** Google Gemini integration for job analysis, secure REST API, LLM injection protection, usage tracking, and batch processing.
- **Job Scraping (`modules/scraping/`):** Core scraping logic, context-aware scraping, data processing pipeline for cleaning and deduplication, and cost-effective usage tracking.
- **Database Layer (`modules/database/`):** PostgreSQL connection management with SQLAlchemy, 32 normalized tables, comprehensive read/write operations, RESTful API, session handling, and API key authenticatio