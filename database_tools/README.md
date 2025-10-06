# Database Schema Automation Tools

This directory contains automated tools for maintaining database schema documentation and generating code from the database structure.

## Tools Overview

### 1. Database Schema Generator (`database_schema_generator.py`)
Extracts complete schema information from PostgreSQL and generates comprehensive documentation.

**Features:**
- Extracts tables, columns, constraints, and indexes from `information_schema`
- Generates detailed Markdown documentation with business rules
- Creates JSON schema files for API integration
- Includes relationship diagrams and sample data

**Usage:**
```bash
python database_schema_generator.py
```

**Outputs:**
- `docs/database_schema.md` - Comprehensive documentation
- `docs/database_schema.json` - JSON schema for APIs
- `docs/schema_raw_data.json` - Raw extracted data

### 2. Code Generator (`code_generator.py`)
Automatically generates Python code from database schema changes.

**Features:**
- SQLAlchemy models with relationships and utility methods
- Pydantic schemas for API validation (Create/Update/Response)
- CRUD operations with custom methods based on table purpose
- Flask API routes with full REST endpoints
- Database migration scripts for schema changes

**Usage:**
```bash
python code_generator.py
```

**Outputs:**
- `generated/models.py` - SQLAlchemy models
- `generated/schemas.py` - Pydantic validation schemas
- `generated/crud.py` - CRUD operations
- `generated/routes.py` - Flask API routes
- `generated/migration_*.py` - Migration scripts

### 3. Schema Automation (`schema_automation.py`)
Orchestrates the entire automation process with change detection and monitoring.

**Features:**
- Detects schema changes via hash comparison
- Automatically updates documentation and code when changes occur
- Continuous monitoring mode
- Git integration for automatic commits
- Configurable automation settings

**Usage:**
```bash
# Check for changes and update if needed
python schema_automation.py --check

# Force update all documentation and code
python schema_automation.py --force

# Monitor for changes continuously
python schema_automation.py --monitor
```

## Configuration

The automation system uses `database_tools/schema_config.json` for configuration. Default settings are created automatically on first run.

### Example Configuration
```json
{
  "documentation": {
    "enabled": true,
    "output_dir": "docs",
    "formats": ["markdown", "json"]
  },
  "code_generation": {
    "enabled": true,
    "output_dir": "generated",
    "generate_models": true,
    "generate_schemas": true,
    "generate_crud": true,
    "generate_routes": true,
    "generate_migrations": true
  },
  "monitoring": {
    "check_interval_minutes": 60,
    "auto_commit": false,
    "notify_on_changes": true
  },
  "git_integration": {
    "enabled": false,
    "auto_commit": false,
    "commit_message_template": "Auto-update: Database schema changes detected on {date}"
  }
}
```

## Generated File Structure

```
docs/
├── database_schema.md          # Comprehensive documentation
├── database_schema.json        # JSON schema for APIs
├── schema_raw_data.json        # Raw extracted data
└── schema_raw_data_previous.json  # Previous schema for migrations

generated/
├── models.py                   # SQLAlchemy models
├── schemas.py                  # Pydantic schemas
├── crud.py                     # CRUD operations
├── routes.py                   # Flask API routes
└── migration_20250706_232809.py  # Migration scripts

database_tools/
├── .schema_hash               # Current schema hash for change detection
└── schema_config.json         # Automation configuration
```

## Key Features

### Change Detection
- Uses SHA-256 hash of schema structure to detect changes
- Compares current schema with previously stored hash
- Only regenerates documentation/code when actual changes occur

### Documentation Quality
- Business rules and constraints clearly documented
- Table relationships with foreign key mappings
- Column descriptions with data types and constraints
- Sample data and usage examples
- Performance optimization recommendations

### Code Generation Quality
- Type-safe SQLAlchemy models with proper relationships
- Pydantic schemas for API validation (Create/Update/Response variants)
- CRUD operations with custom methods based on table purpose
- RESTful API routes with proper error handling
- Database migrations that preserve data integrity

### Automation Benefits
- **Consistency**: Documentation always matches actual database structure
- **Efficiency**: Eliminates manual documentation maintenance
- **Accuracy**: Reduces human error in code generation
- **Productivity**: Developers focus on business logic instead of boilerplate
- **Change Tracking**: Clear history of schema evolution

## Integration with Existing Project

The tools are designed to integrate seamlessly with the existing job application system:

1. **Database Models**: Generated models can replace or supplement existing `modules/database_models.py`
2. **API Routes**: Generated routes can be integrated with existing Flask blueprints
3. **Documentation**: Updates `docs/database_schema.md` to stay current with schema changes
4. **Migration Scripts**: Provides safe database evolution with rollback capabilities

## Recommended Workflow

1. **Development**: Make schema changes in PostgreSQL
2. **Detection**: Run `python schema_automation.py --check` to detect changes
3. **Review**: Examine generated documentation and code
4. **Integration**: Incorporate generated code into existing modules
5. **Testing**: Validate that generated code works with existing system
6. **Deployment**: Apply migration scripts to production database

## Monitoring and Maintenance

- Set up automated runs via cron job: `0 */6 * * * cd /path/to/project/database_tools && python schema_automation.py --check`
- Enable Git integration for automatic documentation commits
- Use continuous monitoring mode during active development
- Regular review of generated migration scripts before production deployment

## Dependencies

- SQLAlchemy and psycopg2-binary for database access
- Existing `modules/database_client.py` for database connections
- PostgreSQL database with proper permissions for information_schema access