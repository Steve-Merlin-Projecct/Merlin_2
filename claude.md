# Automated Job Application System
Version 4.2.0
Python 3.11 | Flask | PostgreSQL | Docker

## Project Overview

AI-driven job application automation system that scrapes job postings, analyzes them with Google Gemini AI, and generates personalized resumes and cover letters from templates.

**For detailed documentation, see:**
- Architecture & Components: `docs/architecture/`
- Database Configuration: `docs/database-connection-guide.md`
- Environment Setup: `docs/setup/`
- API Documentation: `docs/api/`
<!-- critical: do not change anything below this line -->
## Communication & Implementation Guide

### Core Principles

Before implementing changes, explain what you're going to do and why.
Break down complex tasks into clear, focused steps.
Ask for clarification if requirements are unclear.
Provide explanations for technical decisions.
Create inline documentation for sensemaking of codebase.

### Context Priming

Use dedicated context files for domain-specific knowledge rather than loading everything:
- Load relevant architecture docs when working on system design
- Load database schema docs when working on data models
- Load API docs when working on integrations
- Use `/task` templates to automatically load appropriate context

**Philosophy:** Prime the context window specifically for the task at hand, not with static universal knowledge.


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

### Task Tracking with TodoWrite

Use TodoWrite for multi-step tasks to track progress and provide visibility:

**When to use:**
- Tasks with 3+ distinct steps
- Complex, non-trivial implementations
- User explicitly requests task list
- Multiple related tasks

**Best practices:**
- Create todos at task start
- ONE task `in_progress` at a time
- Mark completed immediately after finishing
- Keep descriptions clear and actionable

**See:** Tool documentation for TodoWrite usage patterns

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
