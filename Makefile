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

.PHONY: db-update db-check db-force db-monitor test test-deps start dev help

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

# Help Command
help:
	@echo "Job Application Automation System - Available Commands:"
	@echo ""
	@echo "Database Schema Automation:"
	@echo "  db-update  - Update schema documentation"
	@echo "  db-check   - Check for schema changes"
	@echo "  db-force   - Force schema update"
	@echo "  db-monitor - Continuous monitoring"
	@echo ""
	@echo "Testing:"
	@echo "  test       - Run full test suite"
	@echo "  test-deps  - Test on-demand dependency loading"
	@echo ""
	@echo "Development:"
	@echo "  start      - Start application"
	@echo "  dev        - Start development server with auto-reload"
	@echo ""
	@echo "Use 'make <command>' to run any command."
