# WORKTREE STATUS: IMPLEMENTATION COMPLETE - READY FOR COMMIT

Branch: task/06-calendly
Status: Implementation Complete - All 10 Phases Done
Completion Date: October 9, 2025
Ready for: Git commit and PR to main

# Automated Job Application System
Version 4.2.0 - Calendly Integration Complete
October 2025
Modern Docker-based development environment with comprehensive automation and URL tracking analytics.
This project is written in Python 3.11

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
- `ENABLE_URL_TRACKING`: Enable automatic URL tracking for Calendly/LinkedIn/Portfolio (default: `true`)
- `BASE_REDIRECT_URL`: Base URL for tracked redirect links (default: `http://localhost:5000/track`)

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

**Key Components & Features:**

- **Main Application (`app_modular.py`):** Flask application initialization and configuration, proxy middleware setup, health check endpoint, blueprint registration.
- **Document Generation (`modules/document_generation/`):** Template-based generation from `.docx` files, preserving formatting, professional metadata, and storage backend integration.
- **Storage Layer (`modules/storage/`):** Abstraction layer for file storage with local filesystem implementation and future cloud provider support.
- **Gmail Integration (`modules/email_integration/`):** Official Gmail OAuth 2.0, robust email sending with attachments, enhanced error handling, and RFC-compliant validation.
- **AI Job Description Analysis (`modules/ai_job_description_analysis/`):** Google Gemini integration for job analysis, secure REST API, LLM injection protection, usage tracking, and batch processing.
- **Job Scraping (`modules/scraping/`):** Core scraping logic, context-aware scraping, data processing pipeline for cleaning and deduplication, and cost-effective usage tracking.
- **Database Layer (`modules/database/`):** PostgreSQL connection management with SQLAlchemy, 32 normalized tables, comprehensive read/write operations, RESTful API, session handling, and API key authentication.
- **Database Schema Automation (`database_tools/`):** Generates HTML visualizations, extracts schema information, auto-generates SQLAlchemy models, Pydantic schemas, CRUD operations, and Flask API routes from the live schema with change detection.
- **Code Quality & Security Systems:** Security-first architecture, parameterized queries, automated code quality tools (Black, Flake8, Vulture), comprehensive inline documentation, and LSP diagnostic monitoring.

## External Dependencies

- **Flask:** Web framework.
- **python-docx:** Library for creating and manipulating Word documents.
- **Werkzeug:** WSGI utilities.
- **Flask-SQLAlchemy:** ORM for database operations.
- **psycopg2-binary:** PostgreSQL adapter for Python.
- **Apify:** Third-party service for job scraping (specifically misceres/indeed-scraper).
- **Google Gemini AI:** AI model for job analysis and content generation.
- **PostgreSQL:** Primary database for job tracking and application history.


# Changelog
input changes in docs/changelogs/master-changelog.md
Use this formating:
```
Historical Changelog:
- June 30, 2025. Initial setup
- July 01, 2025. Fixed empty attachment issue in email integration
  * Updated download endpoint to use direct Response mechanism instead of send_file with BytesIO
  * Added explicit Content-Length header to ensure proper file transfer
  * Reinstated API authentication with WEBHOOK_API_KEY
  * Optimized cloud-first storage approach with no local file retention
- July 01, 2025. **MILESTONE**: Service fully operational for production use
