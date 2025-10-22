---
title: Automated Job Application System
type: documentation
created: 2024-08-15
modified: 2025-10-21
status: current
related: QUICKSTART.md, CLAUDE.md, docs/DOCUMENTATION_INDEX.md
---

# Automated Job Application System

**Version:** 4.3.3
**Status:** Production Ready
**Last Updated:** 2025-10-21

---

## Quick Links

📖 **[Quick Start Guide](QUICKSTART.md)** - Get up and running fast
📚 **[Documentation Index](docs/DOCUMENTATION_INDEX.md)** - Complete documentation map
🔧 **[System Instructions](CLAUDE.md)** - Development guidelines and policies
🌳 **[Worktree Guide](docs/worktrees/WORKTREE_COMPLETE_GUIDE.md)** - Parallel development workflow

---

## What Is This?

An **AI-driven job application automation system** that:

1. **Scrapes** job postings from multiple sources
2. **Analyzes** them with Google Gemini AI
3. **Generates** personalized resumes and cover letters
4. **Manages** application workflow and tracking

Built with Flask, PostgreSQL, SQLAlchemy, and Google Gemini AI.

---

## Quick Start

### Prerequisites
```bash
# Install dependencies
pip install -r requirements.txt

# Setup database
psql -U postgres -d local_Merlin_3 -f database_migrations/latest.sql

# Configure environment
cp .env.example .env
# Edit .env with your credentials
```

### Run Application
```bash
# Start Flask server
python app_modular.py

# Open dashboard
open http://localhost:5000/
```

**Full setup guide:** See [QUICKSTART.md](QUICKSTART.md)

---

## Core Features

### Job Automation
- **Job Scraping:** Automated scraping via Apify integration
- **AI Analysis:** Google Gemini AI for job description analysis
- **Smart Matching:** ML-based job ranking and recommendations

### Document Generation
- **Resume Generation:** Template-based personalized resumes
- **Cover Letters:** AI-assisted cover letter generation
- **Format Preservation:** Maintains original document formatting

### Workflow Management
- **Application Tracking:** 32-table normalized PostgreSQL database
- **Status Management:** Track applications through entire lifecycle
- **Batch Processing:** Process multiple applications efficiently

### Development Tools
- **Worktree System:** Parallel feature development (NEW in v4.3.3)
- **Error Prevention:** Automated cleanup and recovery
- **Git Orchestration:** Automated commit validation and testing

---

## Architecture

**Tech Stack:**
- **Backend:** Flask, SQLAlchemy, PostgreSQL
- **AI/ML:** Google Gemini AI, scikit-learn
- **Storage:** Local filesystem with cloud provider support
- **Email:** Gmail OAuth 2.0 integration
- **Scraping:** Apify job scraper integration

**Key Systems:**
- Modular Flask microservices
- Template-based document generation
- Automated database schema management
- Comprehensive resilience and error recovery
- Git operations automation

See: [docs/architecture/](docs/architecture/) for details

---

## Documentation

### Getting Started
- [Quick Start Guide](QUICKSTART.md)
- [System Instructions](CLAUDE.md)
- [Documentation Index](docs/DOCUMENTATION_INDEX.md)

### Development
- [Worktree Management](docs/worktrees/WORKTREE_COMPLETE_GUIDE.md)
- [Architecture Overview](docs/architecture/system-overview.md)
- [Code Quality Standards](docs/code-quality-standards.md)

### Operations
- [Database Configuration](docs/database-connection-guide.md)
- [Troubleshooting Guide](docs/troubleshooting/)
- [Testing Strategy](docs/testing/testing-strategy.md)

---

## Project Structure

```
├── .claude/                    # Claude Code configuration
│   ├── commands/              # Slash commands
│   └── scripts/               # Automation scripts
├── docs/                      # Documentation (organized by category)
│   ├── architecture/          # System design
│   ├── implementation/        # Implementation guides
│   ├── testing/               # Test documentation
│   ├── troubleshooting/       # Error resolution
│   └── worktrees/             # Worktree management
├── modules/                   # Core application modules
│   ├── database/              # Database operations
│   ├── document_generation/   # Resume/cover letter generation
│   ├── email_integration/     # Gmail integration
│   ├── scraping/              # Job scraping
│   └── ai_job_description_analysis/  # AI analysis
├── database_tools/            # Schema automation
├── tasks/                     # Task-specific documentation
└── tests/                     # Test suite

**Note:** Documentation reorganized 2025-10-21 for better navigation
```

---

## Recent Updates (v4.3.3)

### Worktree Error Prevention System ✅
- Pre-flight validation with auto-cleanup
- Stale lock detection and removal
- Atomic rollback on failures
- Enhanced error messages
- Idempotent operations (safe retry)

See: [tasks/worktree-error-prevention/](tasks/worktree-error-prevention/)

### Documentation Organization ✅
- 32 loose files organized into logical structure
- Created comprehensive documentation index
- Consolidated worktree documentation
- Updated system instructions

See: [docs/DOCUMENTATION_INDEX.md](docs/DOCUMENTATION_INDEX.md)

---

## Development Workflow

### Using Worktrees (Recommended)
```bash
# Stage features
/tree stage Add user authentication
/tree stage Implement dashboard

# Create worktrees
/tree build

# Work in parallel
cd .trees/add-user-authentication
# ... implement ...
/tree close

# Merge completed work
/tree closedone
```

See: [Worktree Guide](docs/worktrees/WORKTREE_COMPLETE_GUIDE.md)

### Traditional Workflow
```bash
# Create feature branch
git checkout -b feature/new-feature

# Implement changes
# ... code ...

# Run tests
pytest tests/

# Commit with git-orchestrator
# (follows project git policy)
```

---

## Testing

```bash
# Run full test suite
pytest tests/

# Run with coverage
pytest tests/ --cov=modules --cov-report=html

# Run specific module tests
pytest tests/test_document_generation.py
```

**Test Coverage:** 23% (baseline) → 95% (target)

See: [Testing Documentation](docs/testing/)

---

## Status

**Version:** 4.3.3
**Status:** Production Ready
**Last Major Update:** 2025-10-21

**Recent Improvements:**
- ✅ Worktree error prevention system
- ✅ Documentation organization
- ✅ Enhanced error messages
- ✅ Idempotent operations

**Active Development:**
- Testing coverage expansion (Phase 2-5)
- Additional AI integrations
- Cloud storage backends

---

## Support

**Documentation:** [docs/DOCUMENTATION_INDEX.md](docs/DOCUMENTATION_INDEX.md)
**Troubleshooting:** [docs/troubleshooting/](docs/troubleshooting/)
**System Guide:** [CLAUDE.md](CLAUDE.md)

**Issues:**
1. Check documentation index for relevant guides
2. Review troubleshooting documentation
3. Enable verbose mode for debugging
4. Check system status with `/tree status`
