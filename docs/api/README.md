---
title: API Documentation
created: '2025-10-06'
updated: '2025-10-06'
author: Steve-Merlin-Projecct
type: api
status: active
tags:
- api
---

# API Documentation

This directory contains comprehensive API documentation for the Automated Job Application System's REST API endpoints.

## API Overview
The system provides a RESTful API for accessing job data, AI analysis, document generation, and system management functionality.

- **Base URL**: `https://your-app.replit.app/api/v1`
- **Authentication**: API Key (Header: `X-API-Key`)
- **Content Type**: `application/json`
- **Rate Limiting**: 100 requests per minute per API key

## API Structure

### Endpoints by Category

#### Job Management
- `GET /api/v1/jobs` - List all jobs with filtering and pagination
- `GET /api/v1/jobs/{id}` - Get specific job details
- `POST /api/v1/jobs` - Create new job entry
- `PUT /api/v1/jobs/{id}` - Update job information
- `DELETE /api/v1/jobs/{id}` - Delete job entry

#### AI Analysis
- `POST /api/v1/analysis/job` - Analyze job description
- `POST /api/v1/analysis/batch` - Batch analyze multiple jobs
- `GET /api/v1/analysis/{job_id}` - Get analysis results

#### Document Generation  
- `POST /api/v1/documents/generate` - Generate resume/cover letter
- `GET /api/v1/documents/{id}` - Download generated document
- `GET /api/v1/documents/templates` - List available templates

#### Email Integration
- `POST /api/v1/email/send` - Send job application email
- `GET /api/v1/email/oauth/status` - Check OAuth status
- `POST /api/v1/email/oauth/authorize` - Start OAuth flow

#### System Management
- `GET /api/health` - System health check
- `GET /api/v1/system/stats` - System statistics
- `GET /api/v1/system/status` - Detailed system status

## Documentation Structure

```
api/
├── endpoints/              # Individual endpoint documentation
│   ├── jobs.md            # Job management endpoints
│   ├── analysis.md        # AI analysis endpoints  
│   ├── documents.md       # Document generation endpoints
│   ├── email.md           # Email integration endpoints
│   └── system.md          # System management endpoints
├── schemas/               # Data schemas and models
│   ├── job_schema.md      # Job data model
│   ├── analysis_schema.md # Analysis result model
│   └── error_schema.md    # Error response model
└── examples/              # Request/response examples
    ├── job_examples.md    # Job API examples
    ├── analysis_examples.md # Analysis API examples
    └── error_examples.md  # Error handling examples
```

## Quick Start

### Authentication
```bash
# All API requests require authentication
curl -H "X-API-Key: your_api_key_here" https://your-app.replit.app/api/v1/jobs
```

### Basic Job Retrieval
```bash
# Get all jobs
curl -H "X-API-Key: your_api_key" https://your-app.replit.app/api/v1/jobs

# Get specific job
curl -H "X-API-Key: your_api_key" https://your-app.replit.app/api/v1/jobs/123
```

### AI Analysis
```bash
# Analyze job description
curl -X POST \
  -H "X-API-Key: your_api_key" \
  -H "Content-Type: application/json" \
  -d '{"job_description": "Software Engineer position..."}' \
  https://your-app.replit.app/api/v1/analysis/job
```

## Error Handling
All endpoints return consistent error responses:

```json
{
  "status": "error",
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": ["Additional error details"]
  }
}
```

## Rate Limiting
- **Limit**: 100 requests per minute per API key
- **Headers**: Response includes rate limiting headers
- **Exceeded**: Returns 429 status with retry information

## Versioning
- Current version: `v1`
- Backward compatibility maintained within major versions
- Deprecation notices provided 6 months before removal

## Support
- Documentation issues: Create GitHub issue with `documentation` label  
- API bugs: Create GitHub issue with `api` label
- Feature requests: Create GitHub issue with `enhancement` label