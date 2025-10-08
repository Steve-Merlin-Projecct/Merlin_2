# Database Connection Configuration Guide

## Overview

The Merlin Job Application System now supports automatic environment detection for PostgreSQL database connections. The system intelligently detects whether it's running in a Docker container or locally, and configures the database connection accordingly.

## Architecture

### Components

1. **[database_config.py](../modules/database/database_config.py)** - Environment detection and connection string builder
2. **[database_client.py](../modules/database/database_client.py)** - Database client using environment-aware configuration
3. **[.env](.env)** - Environment variables for local development
4. **[docker-compose.yml](../.devcontainer/docker-compose.yml)** - Docker container environment variables
5. **[devcontainer.json](../.devcontainer/devcontainer.json)** - VS Code devcontainer settings

### Connection Priority

The system uses the following priority order for database configuration:

1. **Explicit DATABASE_URL** (highest priority)
   - If set, uses this connection string directly
   - Bypasses all auto-detection

2. **Individual Components** (recommended)
   - Docker: Uses `DATABASE_HOST`, `DATABASE_PORT`, `DATABASE_NAME`, `DATABASE_USER`, `DATABASE_PASSWORD`
   - Local: Uses `localhost` with `PGPASSWORD` and `DATABASE_NAME`

3. **Fallback Defaults** (lowest priority)
   - Uses sensible defaults if nothing else is configured

## Environment Detection

### Docker Environment

The system detects Docker by checking:

1. `DATABASE_HOST` is set to `host.docker.internal` or `docker.internal`
2. Both `DATABASE_HOST` and `DATABASE_USER` are set (from devcontainer.json)
3. `/.dockerenv` file exists AND database environment variables are present

When Docker is detected, it uses:
```
Host: host.docker.internal (or value from DATABASE_HOST)
Port: 5432 (or value from DATABASE_PORT)
Database: local_Merlin_3 (or value from DATABASE_NAME)
User: postgres (or value from DATABASE_USER)
Password: From DATABASE_PASSWORD or PGPASSWORD
```

### Local Environment

When running locally (not in Docker), it uses:
```
Host: localhost
Port: 5432
Database: local_Merlin_3 (or value from DATABASE_NAME)
User: postgres
Password: From PGPASSWORD
```

## Configuration Files

### .env (Local Development)

```bash
# Database Configuration
PGPASSWORD=your_password
DATABASE_NAME=local_Merlin_3

# Optional: Override auto-detection with explicit URL
# DATABASE_URL=postgresql://postgres:password@localhost:5432/local_Merlin_3
```

### docker-compose.yml (Docker Environment)

```yaml
environment:
  - DATABASE_HOST=localhost
  - DATABASE_PORT=5432
  - DATABASE_NAME=local_Merlin_3
  - DATABASE_USER=postgres
  - PGPASSWORD=your_password
```

### devcontainer.json (VS Code Container)

```json
"containerEnv": {
  "DATABASE_HOST": "host.docker.internal",
  "DATABASE_PORT": "5432",
  "DATABASE_NAME": "local_Merlin_3",
  "DATABASE_USER": "postgres",
  "DATABASE_PASSWORD": "your_password"
}
```

## Testing Connection

Run the connection test script:

```bash
python tests/integration/test_db_connection.py
```

This will:
- Display all environment variables
- Show environment detection results
- Test database connectivity
- List database tables
- Verify PostgreSQL version

Expected output:
```
============================================================
DATABASE CONNECTION TEST
============================================================

1. Environment Variables:
   DATABASE_HOST: host.docker.internal
   DATABASE_PORT: 5432
   ...

2. Environment Detection:
   /.dockerenv exists: True
   Environment type: Docker

3. Database Configuration:
   Connection URL: postgresql://postgres:****@host.docker.internal:5432/local_Merlin_3

4. Connection Test:
   ✓ Database connection successful!

============================================================
✓ ALL TESTS PASSED
============================================================
```

## Troubleshooting

### Connection Fails in Docker

1. **Check PostgreSQL is running on host:**
   ```bash
   psql -h localhost -p 5432 -U postgres -d local_Merlin_3
   ```

2. **Verify network mode in docker-compose.yml:**
   ```yaml
   network_mode: host
   ```

3. **Check environment variables in container:**
   ```bash
   docker exec -it <container_name> env | grep DATABASE
   ```

### Connection Fails Locally

1. **Check .env file exists and is loaded:**
   ```bash
   cat .env
   ```

2. **Verify PGPASSWORD is set:**
   ```bash
   echo $PGPASSWORD
   ```

3. **Test PostgreSQL directly:**
   ```bash
   PGPASSWORD=goldmember psql -h localhost -p 5432 -U postgres -d local_Merlin_3
   ```

### Override Auto-Detection

If auto-detection isn't working, explicitly set DATABASE_URL:

```bash
# In .env or export
DATABASE_URL=postgresql://postgres:password@localhost:5432/local_Merlin_3
```

## Security Considerations

- **Password Logging:** Passwords are automatically masked in logs (shown as `****`)
- **Environment Variables:** Never commit `.env` to version control (it's gitignored)
- **Docker Secrets:** Consider using Docker secrets for production deployments
- **Connection Pooling:** SQLAlchemy connection pooling is enabled with:
  - `pool_pre_ping=True` - Test connections before use
  - `pool_recycle=300` - Recycle connections every 5 minutes

## Migration from Replit

The previous Replit-specific configuration has been replaced with environment-aware configuration:

**Before (Replit):**
```python
DATABASE_URL = os.environ.get("DATABASE_URL")  # Hardcoded
```

**After (Environment-aware):**
```python
db_config = get_database_config()  # Auto-detects environment
database_url = db_config.get_connection_url()
```

## API Reference

### DatabaseConfig Class

```python
from modules.database.database_config import get_database_config

# Get singleton instance
config = get_database_config()

# Get connection URL
url = config.get_connection_url()

# Get individual parameters
params = config.get_connection_params()
# Returns: {'host': '...', 'port': 5432, 'database': '...', 'user': '...', 'password': '...'}

# Check environment
is_docker = config.is_docker
```

### DatabaseClient Class

```python
from modules.database.database_client import DatabaseClient

# Initialize with auto-detection
db_client = DatabaseClient()

# Test connection
db_client.test_connection()

# Check environment
if db_client.is_docker:
    print("Running in Docker")
```

## Best Practices

1. **Use individual environment variables** instead of DATABASE_URL for flexibility
2. **Let auto-detection work** - only override when necessary
3. **Test both environments** when making changes
4. **Check logs** - they show which environment was detected
5. **Use the test script** to verify configuration before deployment

## Changelog

- **October 6, 2025:** Created environment-aware database configuration
  - Added `database_config.py` with Docker/local auto-detection
  - Updated `database_client.py` to use environment-aware config
  - Created `test_db_connection.py` for connection testing
  - Updated `.env` with configuration documentation
  - Migrated from Replit-specific hardcoded DATABASE_URL
