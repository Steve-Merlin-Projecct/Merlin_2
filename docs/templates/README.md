---
title: Documentation Templates
created: '2025-10-06'
updated: '2025-10-06'
author: Steve-Merlin-Projecct
type: template
status: active
tags: []
---

# Documentation Templates

This directory contains standardized templates for creating consistent documentation across the project.

## Available Templates

| Template | Purpose | Usage |
|----------|---------|--------|
| `adr_template.md` | Architecture Decision Records | Document major architectural choices |
| `feature_spec_template.md` | Feature Specifications | Define new features and requirements |
| `troubleshooting_template.md` | Troubleshooting Guides | Standardize problem-solving documentation |
| `integration_template.md` | Integration Documentation | Document external service integrations |
| `process_template.md` | Process Documentation | Document operational procedures |
| `api_endpoint_template.md` | API Endpoint Documentation | Document individual API endpoints |

## Using Templates

1. Copy the appropriate template file
2. Rename it to match your documentation topic
3. Fill in the template sections
4. Add appropriate metadata tags
5. Place in the correct directory structure

## Metadata Standards

All documentation should include frontmatter with:
```yaml
---
title: "Document Title"
tags: [relevant, tags, here]
audience: [developers, ops, business]
last_updated: YYYY-MM-DD
next_review: YYYY-MM-DD
owner: team_or_person
status: [draft, active, deprecated]
---
```