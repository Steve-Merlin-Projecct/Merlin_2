# System Architecture Memory

## Technology Stack
- **Framework**: Flask (Python 3.11+)
- **Database**: PostgreSQL
- **AI**: Google Gemini
- **Scraping**: Apify (Indeed scraper)
- **Storage**: Local filesystem (abstracted for cloud)

## Project Structure
```
/workspace/.trees/claude-config/
├── app_modular.py          # Main Flask application
├── modules/                # Core application modules
│   ├── content/           # Document generation
│   ├── database/          # Database layer
│   ├── email_integration/ # Gmail OAuth
│   ├── scraping/          # Job scraping
│   └── storage/           # File storage abstraction
├── database_tools/        # Schema automation
├── .claude/              # Claude Code config
├── docs/                 # Documentation
└── tests/                # Test suite
```

## Key Design Patterns

### Modular Flask Architecture
- Blueprint pattern for route organization
- Each module is self-contained
- Clear separation of concerns

### Template-Based Document Generation
- Uses `.docx` templates
- Variable substitution preserves formatting
- CSV mapping for dynamic content

### Automated Schema Management
- Database tools generate models, schemas, CRUD
- PreToolUse hook prevents manual edits
- SHA-256 hash-based change detection

### Storage Abstraction
- Backend-agnostic interface
- Local filesystem by default
- Ready for cloud providers (S3, GCS)

## Security
- API key authentication (WEBHOOK_API_KEY)
- Input validation and sanitization
- Rate limiting
- Audit logging
- LLM injection protection
