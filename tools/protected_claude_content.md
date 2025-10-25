---
title: "Protected Claude Content"
type: technical_doc
component: general
status: draft
tags: []
---

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
- When new understanding of the project is gained, document the changes in replit.md.

**Research Preferences:**
- Always check for the latest versions of dependencies before suggesting updates.
- Research current best practices for security implementations.

**External Research Guidelines:**
- When suggesting new libraries, ensure compatibility with our existing stack.
- Adapt external examples to match our coding standards and project structure.

**Style:**
- Use consistent naming patterns and code organization. Group related functions together and use clear, descriptive names.
