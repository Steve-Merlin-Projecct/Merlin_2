---
title: Architecture Decision Records (ADRs)
status: current
created: '2025-10-06'
updated: '2025-10-06'
author: Steve-Merlin-Projecct
type: decision
tags: []
---

# Architecture Decision Records (ADRs)

This directory contains Architecture Decision Records (ADRs) that document significant architectural and design decisions made for the Automated Job Application System.

## What are ADRs?
Architecture Decision Records capture important architectural decisions along with their context and consequences. They help teams understand why decisions were made and provide a historical record for future reference.

## ADR Format
All ADRs follow a consistent format:
- **Status**: Current status (Proposed, Accepted, Deprecated, Superseded)
- **Context**: The situation that led to the decision
- **Decision**: The actual decision made
- **Consequences**: Positive and negative outcomes
- **Alternatives**: Other options considered and why they were rejected

## Current ADRs

| ADR | Title | Status | Date |
|-----|-------|--------|------|
| [ADR-001](001-database-choice.md) | PostgreSQL as Primary Database | Accepted | 2025-08-07 |
| [ADR-002](002-document-generation-strategy.md) | Template-Based Document Generation | Accepted | 2025-08-07 |
| [ADR-003](003-ai-integration-approach.md) | Google Gemini for AI Analysis | Accepted | 2025-08-07 |
| [ADR-004](004-authentication-strategy.md) | OAuth 2.0 for Gmail Integration | Accepted | 2025-08-07 |
| [ADR-005](005-storage-strategy.md) | Replit Object Storage for Documents | Accepted | 2025-08-07 |

## Creating New ADRs
1. Copy the [ADR template](../templates/adr_template.md)
2. Use the next sequential number (ADR-XXX)
3. Fill in all sections thoroughly
4. Get team review before marking as "Accepted"
5. Update this README with the new ADR

## ADR Lifecycle
- **Proposed**: Under consideration, seeking feedback
- **Accepted**: Approved and being implemented
- **Deprecated**: No longer relevant but kept for historical context
- **Superseded**: Replaced by a newer decision (link to replacement)