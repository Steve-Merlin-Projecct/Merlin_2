# Job Application Automation System - Project Commands
# 
# This Makefile serves as the central command interface for the entire project.
# It provides convenient shortcuts for common development, testing, and database tasks.
#
# LOCATION RATIONALE:
# - Located in project root following industry standard conventions
# - Provides easy access from anywhere in the project (make commands work from root)
# - Serves as project-wide command interface, not just database-specific
# - Developers expect 'make help' to work from project root
#
# USAGE:
# - Run 'make help' to see all available commands
# - All commands are designed to be run from the project root directory
# - Database commands handle schema automation and documentation
# - Testing commands validate system functionality and dependency loading
# - Development commands provide convenient server startup options
#
# ARCHITECTURE:
# - Database tools are in database_tools/ but controlled from root Makefile
# - Testing infrastructure spans multiple directories (tests/, modules/)
# - Development commands use both direct Python and Gunicorn approaches
# - All paths are relative to project root for consistency

.PHONY: db-update db-check db-force db-monitor test test-deps start dev help install setup-env lint format clean logs shell ci serve version version-bump

# Database Schema Automation Commands
# These commands manage PostgreSQL schema documentation and code generation
# All database tools are located in database_tools/ but controlled from root
db-update:
	@echo "🔄 Updating database schema..."
	@echo "   - Reads live PostgreSQL schema from DATABASE_URL"
	@echo "   - Generates HTML visualization and documentation"
	@echo "   - Updates models, schemas, and API code"
	python database_tools/update_schema.py

db-check:
	@echo "🔍 Checking for schema changes..."
	@echo "   - Compares current schema with previous version"
	@echo "   - Uses SHA-256 hashing for change detection"
	python database_tools/schema_automation.py --check

db-force:
	@echo "🔧 Forcing schema update..."
	@echo "   - Bypasses change detection and forces regeneration"
	@echo "   - Useful when documentation is out of sync"
	python database_tools/schema_automation.py --force

db-monitor:
	@echo "👁️  Starting continuous monitoring..."
	@echo "   - Watches for schema changes in real-time"
	@echo "   - Automatically updates documentation when changes detected"
	python database_tools/schema_automation.py --monitor

# Testing Commands
# Comprehensive testing infrastructure for system validation
test:
	@echo "🧪 Running test suite..."
	@echo "   - Executes all tests in tests/ directory"
	@echo "   - Validates system functionality and integration"
	python -m pytest tests/ -v

test-deps:
	@echo "🔍 Testing on-demand dependency loading..."
	@echo "   - Validates smart dependency loading system"
	@echo "   - Tests numpy, bleach, docx, genai, trafilatura loading"
	@echo "   - Verifies mock interfaces and fallback mechanisms"
	python tests/test_dependency_optimization.py

# Development Commands
# Server startup options for development and testing
start:
	@echo "🚀 Starting application..."
	@echo "   - Uses direct Python execution via main.py"
	@echo "   - Suitable for development and debugging"
	python main.py

dev:
	@echo "🔧 Starting development server with auto-reload..."
	@echo "   - Uses Gunicorn with auto-reload enabled"
	@echo "   - Automatically restarts on file changes"
	@echo "   - Binds to 0.0.0.0:5000 for external access"
	gunicorn --bind 0.0.0.0:5000 --reuse-port --reload main:app

# Installation & Setup
install:
	@echo "📦 Installing dependencies..."
	pip install -r requirements.txt
	@echo "✅ Dependencies installed"

setup-env:
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo "✅ Created .env from template"; \
		echo "⚠️  Please edit .env with your credentials"; \
	else \
		echo "⚠️  .env already exists, skipping"; \
	fi

# Code Quality
lint:
	@echo "🔍 Running code quality checks..."
	@echo "1/3 Black (formatting)..."
	@black --check .
	@echo "2/3 Flake8 (linting)..."
	@flake8
	@echo "3/3 Vulture (dead code)..."
	@vulture --min-confidence 80
	@echo "✅ All quality checks passed"

format:
	@echo "🎨 Formatting code with Black..."
	@black .
	@echo "✅ Code formatted"

# Additional Development Commands
serve:
	@echo "🚀 Starting Flask development server..."
	python -m flask --app app_modular run --debug --port 5000

clean:
	@echo "🧹 Cleaning temporary files..."
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete
	@find . -type f -name "*.pyo" -delete
	@find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@rm -rf htmlcov/ .coverage tmp/ temp/ 2>/dev/null || true
	@echo "✅ Cleaned temporary files"

logs:
	@if [ -f logs/application.log ]; then \
		tail -f logs/application.log; \
	else \
		echo "No log file found at logs/application.log"; \
	fi

shell:
	@echo "🐍 Starting Python shell with Flask app context..."
	@python -c "from app_modular import app; app.app_context().push(); import code; code.interact(local=globals())"

# Version Management
version:
	@python tools/version_manager.py

version-bump:
	@echo "📦 Version Bump Tool"
	@echo "Usage: make version-bump-patch | make version-bump-minor | make version-bump-major"

version-bump-patch:
	@python tools/version_manager.py --bump patch
	@python tools/version_manager.py --sync

version-bump-minor:
	@python tools/version_manager.py --bump minor
	@python tools/version_manager.py --sync

version-bump-major:
	@python tools/version_manager.py --bump major
	@python tools/version_manager.py --sync

# Workflow Shortcuts
ci: lint test
	@echo "✅ CI checks passed"

# Help Command
help:
	@echo "Job Application Automation System - Available Commands:"
	@echo ""
	@echo "Setup & Installation:"
	@echo "  install    - Install Python dependencies"
	@echo "  setup-env  - Create .env from template"
	@echo ""
	@echo "Development:"
	@echo "  serve      - Start Flask development server"
	@echo "  start      - Start application (direct Python)"
	@echo "  dev        - Start development server with auto-reload (Gunicorn)"
	@echo "  shell      - Python shell with app context"
	@echo ""
	@echo "Testing & Quality:"
	@echo "  test       - Run full test suite"
	@echo "  test-deps  - Test on-demand dependency loading"
	@echo "  lint       - Run code quality checks"
	@echo "  format     - Auto-format code with Black"
	@echo "  ci         - Run CI checks (lint + test)"
	@echo ""
	@echo "Database Schema Automation:"
	@echo "  db-update  - Update schema documentation"
	@echo "  db-check   - Check for schema changes"
	@echo "  db-force   - Force schema update"
	@echo "  db-monitor - Continuous monitoring"
	@echo ""
	@echo "Version Management:"
	@echo "  version             - Show current version"
	@echo "  version-bump-patch  - Bump patch version (4.0.1 -> 4.0.2)"
	@echo "  version-bump-minor  - Bump minor version (4.0.1 -> 4.1.0)"
	@echo "  version-bump-major  - Bump major version (4.0.1 -> 5.0.0)"
	@echo ""
	@echo "Utilities:"
	@echo "  clean      - Remove temporary files and caches"
	@echo "  logs       - View application logs"
	@echo ""
	@echo "Use 'make <command>' to run any command."
