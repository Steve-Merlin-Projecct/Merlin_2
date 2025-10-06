# Documentation Automation

This directory contains scripts and tools for automating documentation processes, maintenance, and quality assurance.

## Automation Categories

### Auto-Generated Documentation
Scripts that extract information from code and generate documentation:

| Script | Purpose | Frequency |
|--------|---------|-----------|
| `extract_docstrings.py` | Generate API docs from code docstrings | On demand |
| `generate_api_docs.py` | Create OpenAPI/Swagger documentation | Weekly |
| `update_dependency_docs.py` | Document project dependencies | Monthly |
| `extract_database_schema.py` | Generate database documentation | After schema changes |

### Documentation Testing
Tools for validating documentation quality and accuracy:

| Tool | Purpose | Frequency |
|------|---------|-----------|
| `link_checker.py` | Find and report broken links | Daily |
| `code_sample_tester.py` | Verify code examples still work | Weekly |
| `doc_freshness_checker.py` | Flag outdated documentation | Daily |
| `spelling_checker.py` | Check spelling and grammar | On commit |

### Maintenance Scripts
Automated maintenance and organization tools:

| Script | Purpose | Frequency |
|--------|---------|-----------|
| `update_indexes.py` | Refresh documentation indexes | Daily |
| `check_metadata.py` | Validate document metadata | Daily |
| `archive_old_docs.py` | Archive outdated documents | Monthly |
| `cross_reference_updater.py` | Update cross-references | Weekly |

## Usage

### Running Individual Scripts
```bash
# Check for broken links
python docs/automation/scripts/link_checker.py

# Generate API documentation
python docs/automation/scripts/generate_api_docs.py

# Test code samples
python docs/automation/scripts/code_sample_tester.py
```

### Automated Execution
- **GitHub Actions**: Automated runs on schedule and commits
- **Pre-commit Hooks**: Quality checks before commits
- **Replit Deployment**: Integration with deployment process

### Configuration
Each script uses configuration files in `docs/automation/config/`:
- `link_checker_config.yaml` - URL patterns and exclusions
- `doc_freshness_config.yaml` - Freshness thresholds by document type
- `api_doc_config.yaml` - API documentation generation settings

## Features

### Link Checking
- Validates internal and external links
- Reports broken links with context
- Suggests alternative links where possible
- Configurable timeout and retry settings

### Code Sample Testing
- Extracts code samples from markdown files
- Tests Python code samples for syntax and execution
- Validates API endpoints and responses
- Reports outdated or broken examples

### Documentation Freshness
- Tracks last update dates for all documents
- Flags documents that haven't been reviewed recently
- Considers document type and importance for thresholds
- Integrates with review schedules

### Cross-Reference Management
- Automatically updates internal links when files move
- Maintains consistency in cross-references
- Generates "Related Documents" sections
- Creates topic-based indexes

## Quality Metrics

### Documentation Coverage
- Percentage of code with docstrings
- API endpoint documentation coverage
- Process documentation completeness

### Link Health
- Percentage of working internal links
- External link availability
- Link update frequency

### Content Freshness
- Average age of documentation
- Percentage of recently reviewed docs
- Outdated content identification rate

## Integration Points

### Development Workflow
- Pre-commit hooks for quality checks
- Pull request automation for doc updates
- Integration with code review process

### Deployment Process
- Documentation updates with each release
- Automatic API documentation generation
- Archive management during deployments

### Monitoring & Alerting
- Daily reports on documentation health
- Alerts for critical documentation issues
- Performance metrics and trends

## Future Enhancements

### Planned Features
- AI-powered content generation assistance
- Automated translation support
- Interactive documentation testing
- Real-time collaboration features

### Integration Opportunities
- Enhanced GitHub integration
- Slack/Discord notifications
- Dashboard and reporting improvements
- Advanced analytics and insights