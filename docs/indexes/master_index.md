---
title: "Master Index"
type: technical_doc
component: general
status: draft
tags: []
---

# Master Documentation Index

**Last Updated**: 2025-08-07  
**Total Documents**: 50+  
**Coverage**: All system components and processes

## Quick Navigation

| Category | Documents | Description |
|----------|-----------|-------------|
| [🏗️ Architecture](#architecture) | 5 | System design and decisions |
| [👩‍💻 Development](#development) | 15 | Developer guides and standards |
| [🔧 Processes](#processes) | 8 | Operational procedures |
| [🔌 Integrations](#integrations) | 6 | External service connections |
| [🛡️ Security](#security) | 4 | Security guides and assessments |
| [📊 API](#api) | 10 | API documentation and examples |
| [🤖 Automation](#automation) | 5 | Documentation automation tools |
| [📁 Archived](#archived) | 20+ | Historical documentation |

---

## Architecture

### System Design
- **[Project Architecture](../architecture/PROJECT_ARCHITECTURE.md)** - Complete system overview and component relationships
- **[Decision Records](../decisions/README.md)** - Architecture Decision Records (ADRs)
  - [ADR-001: Database Choice](../decisions/001-database-choice.md) - PostgreSQL selection rationale
  - [ADR-002: Document Generation Strategy](../decisions/002-document-generation-strategy.md) - Template-based approach
  - [ADR-003: AI Integration Approach](../decisions/003-ai-integration-approach.md) - Google Gemini selection
  - [ADR-004: Authentication Strategy](../decisions/004-authentication-strategy.md) - OAuth 2.0 implementation

---

## Development

### Standards & Guidelines
- **[Coding Standards](../development/standards/CODING_STANDARDS.md)** - Python coding conventions and best practices
- **[Automated Tooling Guide](../development/standards/AUTOMATED_TOOLING_GUIDE.md)** - Black, Flake8, Vulture configuration
- **[Development Guide](../development/DEVELOPMENT_GUIDE.md)** - Development workflow and patterns

### Code Quality
- **[Code Review Decision Guide](../development/code_quality/CODE_REVIEW_DECISION_GUIDE.md)** - Review criteria and decision matrix
- **[Code Review History](../development/code_quality/CODE_REVIEW_HISTORY.md)** - Historical review results and metrics
- **[Code Review Comprehensive Report](../development/code_quality/code_review_comprehensive.md)** - Latest comprehensive review results

### API Documentation
- **[API Overview](../development/API_DOCUMENTATION.md)** - Complete API reference
- **[API Endpoints](../api/README.md)** - REST API documentation

### Component Documentation
- **[Database Schema](../component_docs/database/database_schema.md)** - Complete 32-table schema documentation
- **[Database Automation](../component_docs/database/database_schema_automation.md)** - Schema management philosophy
- **[Document Generation Architecture](../component_docs/document_generation/document_generation_architecture.md)** - Template-based generation system
- **[Gmail OAuth Integration](../component_docs/gmail_oauth_integration.md)** - Email integration implementation
- **[Security Overview](../component_docs/security/security_overview.md)** - Comprehensive security controls

---

## Processes

### Deployment & Operations
- **[Production Deployment](../processes/deployment/production_deployment.md)** - Complete deployment procedure
- **[Incident Response Plan](../processes/incident_response/incident_response_plan.md)** - Emergency response procedures

### Team Management
- **[Developer Onboarding](../processes/onboarding/developer_onboarding.md)** - New team member setup
- **[Environment Setup](../processes/onboarding/environment_setup.md)** - Development environment configuration

### Release Management
- **[Release Process](../processes/release_management/release_process.md)** - Standard release procedures
- **[Version Management](../processes/release_management/version_management.md)** - Version control and tracking

---

## Integrations

### External Services
- **[Apify Integration](../integrations/external/apify_integration.md)** - Web scraping service integration
- **[Google Gemini Integration](../integrations/external/google_gemini_integration.md)** - AI analysis service
- **[Gmail API Integration](../integrations/external/gmail_integration.md)** - Email automation service
- **[Replit Storage Integration](../integrations/external/replit_storage_integration.md)** - Cloud storage service

### Internal Services
- **[Database Integration](../integrations/internal/database_integration.md)** - Internal data layer
- **[Security Integration](../integrations/internal/security_integration.md)** - Authentication and authorization

---

## Security

### Implementation & Assessment
- **[Security Implementation Guide](../component_docs/security/security_implementation_guide.md)** - Security controls implementation
- **[Security Assessment Report](../security_assessments/security_assessment_report.md)** - Comprehensive security testing results
- **[Link Tracking Security](../component_docs/link_tracking/security_implementation.md)** - URL security implementation

---

## API

### Reference Documentation
- **[API Overview](../api/README.md)** - Complete API documentation system
- **[Endpoint Documentation](../api/endpoints/)** - Individual endpoint details
- **[API Schemas](../api/schemas/)** - Data models and structures
- **[API Examples](../api/examples/)** - Request/response examples

---

## Automation

### Documentation Tools
- **[Automation Overview](../automation/README.md)** - Documentation automation system
- **[Link Checker](../automation/scripts/link_checker.py)** - Automated link validation
- **[API Documentation Generator](../automation/scripts/generate_api_docs.py)** - Auto-generate API docs
- **[Documentation Testing](../automation/tests/)** - Quality assurance tools

---

## Project Overview

### Getting Started
- **[README](../project_overview/README.md)** - Project introduction and setup
- **[System Requirements](../project_overview/SYSTEM_REQUIREMENTS.md)** - Technical requirements

---

## Git Workflow

### Version Control
- **[Git Commands](../git_workflow/GIT_COMMANDS.md)** - Common Git operations
- **[GitHub Connectivity](../git_workflow/GITHUB_CONNECTIVITY_SOLUTION.md)** - GitHub integration setup
- **[Manual Merge Resolution](../git_workflow/MANUAL_MERGE_RESOLUTION.md)** - Conflict resolution procedures

---

## Templates

### Documentation Templates
- **[Template Overview](../templates/README.md)** - Available documentation templates
- **[ADR Template](../templates/adr_template.md)** - Architecture Decision Record template
- **[Feature Specification Template](../templates/feature_spec_template.md)** - Feature documentation template
- **[Process Template](../templates/process_template.md)** - Process documentation template

---

## Archived Documentation

### Historical Materials
- **[Code Review Session 2025-07-30](../archived/code_review_session_2025_07_30/)** - Historical code review documentation
- **[Component Documentation Archive](../archived/component_docs/)** - Archived component-specific docs
- **[Standalone Documentation Archive](../archived/standalone_docs/)** - Individual archived documents

---

## Special Collections

### Recent Updates (Last 30 Days)
- Documentation Organization Summary
- Code Review Comprehensive Report
- Master Documentation Index (this document)
- Template System Implementation

### Most Referenced Documents
1. System Architecture Overview
2. Coding Standards
3. API Documentation
4. Security Implementation Guide
5. Developer Onboarding Guide

---

## How to Use This Index

### For New Team Members
1. Start with [Project Overview](../project_overview/README.md)
2. Read [System Architecture](../architecture/PROJECT_ARCHITECTURE.md)
3. Follow [Developer Onboarding](../processes/onboarding/developer_onboarding.md)
4. Review [Coding Standards](../development/standards/CODING_STANDARDS.md)

### For Existing Developers
- Check [Recent Updates](#recent-updates-last-30-days) for latest changes
- Use [API Documentation](../api/README.md) for implementation reference
- Refer to [Decision Records](../decisions/README.md) for architectural context

### For Operations Teams
- Focus on [Processes](#processes) section
- Review [Security](#security) documentation
- Check [Integrations](#integrations) for service dependencies

---

**Navigation**: [🏠 Documentation Home](../README.md) | [🔍 Topic Search](topic_search.md) | [📈 Documentation Stats](doc_stats.md)