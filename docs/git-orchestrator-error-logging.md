---
title: "Git Orchestrator Error Logging"
type: technical_doc
component: general
status: draft
tags: []
---

# Git Orchestrator Error Logging

## Overview
This document defines the comprehensive error logging system for the git-orchestrator agent.

## Logging Strategy

### Log Levels
- `ERROR`: Critical failures that prevent operation completion
- `WARNING`: Non-blocking issues that require attention
- `INFO`: Operational context and successful actions

### Log Entry Structure
\`\`\`json
{
  "timestamp": "ISO8601 timestamp",
  "level": "ERROR|WARNING|INFO",
  "operation": "checkpoint|section_commit|user_commit",
  "context": {
    "branch": "current_branch_name",
    "commit_hash": "previous_commit_hash",
    "files_changed": ["list", "of", "files"]
  },
  "message": "Detailed error description",
  "suggested_action": "Recommended resolution steps"
}
\`\`\`

## Error Handling Guidelines
1. Log all git command failures
2. Capture full error context
3. Provide actionable resolution steps
4. Ensure no sensitive information is logged

## Example Log Entries

### Test Failure Warning
\`\`\`json
{
  "timestamp": "2025-10-12T15:30:45Z",
  "level": "WARNING",
  "operation": "section_commit",
  "context": {
    "branch": "feature/database-schema",
    "failed_tests": 2
  },
  "message": "2 tests failed during section commit",
  "suggested_action": "Review and fix failing tests"
}
\`\`\`

### Commit Creation Error
\`\`\`json
{
  "timestamp": "2025-10-12T15:35:22Z",
  "level": "ERROR",
  "operation": "user_commit",
  "context": {
    "branch": "task/03-git-orchestrator-improvements",
    "files_changed": [".claude/agents/git-orchestrator.md"]
  },
  "message": "Commit creation failed: pre-commit hook rejected",
  "suggested_action": "Review pre-commit hook errors and fix code quality issues"
}
\`\`\`

## Log Management
- Logs rotate daily
- Maximum 30 days of historical logs maintained
- Logs are gitignored to prevent sensitive information tracking
