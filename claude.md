# Automated Job Application System
Version 4.3.2 | Python 3.11 | Flask | PostgreSQL | Docker

## Project Overview

AI-driven job application automation system that scrapes job postings, analyzes them with Google Gemini AI, and generates personalized resumes and cover letters from templates.

## Technical Architecture

### Core Stack
- **Framework**: Flask with Blueprint pattern for modular microservices
- **Database**: PostgreSQL with SQLAlchemy ORM (32 normalized tables)
- **AI Integration**: Google Gemini for job analysis and content generation
- **Container**: Docker with environment-aware configuration
- **Storage**: Abstraction layer supporting local filesystem and cloud providers

### Key Components
- **Document Generation** (`modules/document_generation/`): Template-based `.docx` generation preserving formatting
- **Gmail Integration** (`modules/email_integration/`): OAuth 2.0 authenticated email with attachments
- **Job Scraping** (`modules/scraping/`): Apify-based Indeed scraper with deduplication
- **Database Tools** (`database_tools/`): Auto-generates models, schemas, CRUD, and API routes from live schema

## Critical Workflows

### Database Schema Changes
```bash
# After PostgreSQL modifications:
python database_tools/update_schema.py
# This auto-generates all dependent code and documentation
```

### Git Operations
Use git-orchestrator agent via Task tool:
- `git-orchestrator "user_commit:Description"` for commits
- Handles tests, validation, and remote push automatically

### Task Management
Use `/task` command with templates:
- `/task go` - Autonomous implementation
- `/task analyze` - Analysis without implementation
- `/task research` - Technology evaluation

## Environment Configuration

### Database Connection (Auto-detected)
- **Docker**: Uses `host.docker.internal`
- **Local**: Uses `localhost`
- **Override**: Set `DATABASE_URL` explicitly

### Key Variables
- `PGPASSWORD`: Database password (required)
- `DATABASE_NAME`: Default `local_Merlin_3`
- `WEBHOOK_API_KEY`: API authentication
- `STORAGE_BACKEND`: Storage type (default: local)

## Project Standards

### Code Quality
- **Formatter**: Black
- **Linter**: Flake8
- **Dead Code**: Vulture
- **Testing**: pytest

### Security
- Parameterized queries only
- Input validation on all endpoints
- Rate limiting implemented
- API key authentication required

## Documentation Locations
- Architecture: `docs/architecture/`
- Database Guide: `docs/database-connection-guide.md`
- API Reference: `docs/api/`
- Setup Guide: `docs/setup/`