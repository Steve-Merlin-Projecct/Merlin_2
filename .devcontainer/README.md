# Docker Dev Container Setup

This configuration creates a secure, isolated development environment for the Merlin Job Application System with restricted filesystem access.

## Features

- **Python 3.11** environment
- **Restricted Access**: Container can only read/write to the project directory
- **PostgreSQL Connection**: Direct access to local_Merlin_3 database
- **GitHub Integration**: SSH and Git configured for version control
- **Claude Code Support**: Extension enabled with workspace restrictions
- **Security Hardened**: Non-root user, capability restrictions, no new privileges

## Prerequisites

1. **Docker Desktop** installed and running
2. **VS Code** with "Dev Containers" extension installed
3. **PostgreSQL** running locally with database `local_Merlin_3`
4. **SSH Keys** configured for GitHub access at `~/.ssh/`

## Quick Start

1. Open the project folder in VS Code:
   ```
   /Volumes/Programming_Seagate_2022/Merlin_Project_Files/Code/project files/Merlin_2/
   ```

2. When prompted, click **"Reopen in Container"** or:
   - Press `Cmd+Shift+P` (Mac) or `Ctrl+Shift+P` (Windows/Linux)
   - Type "Dev Containers: Reopen in Container"
   - Press Enter

3. VS Code will:
   - Build the Docker image (first time only, takes 2-5 minutes)
   - Start the container
   - Install Python dependencies
   - Configure extensions

4. Verify database connection:
   ```bash
   psql -h localhost -p 5432 -U postgres -d local_Merlin_3
   ```
   Password: `goldmember`

## Security Features

### Filesystem Isolation
- **Only Mounted Path**: `/Volumes/Programming_Seagate_2022/Merlin_Project_Files/Code/project files/Merlin_2`
- Container cannot access any other directories on your host system
- Claude Code workspace is explicitly restricted to `/workspace`

### Database Connection
- Connects to host PostgreSQL via `host.docker.internal` (or `localhost` with host network)
- Credentials configured via environment variables
- No database containers - uses your existing local database

### GitHub Access
- SSH keys mounted read-only from `~/.ssh/`
- Git config mounted read-only from `~/.gitconfig`
- No credential modifications possible from container

### Container Hardening
- Runs as non-root user `vscode` (UID 1000)
- All capabilities dropped except `NET_BIND_SERVICE`
- Security option: `no-new-privileges`
- Resource limits: 2-4GB RAM, 1-2 CPU cores

## Installed Tools & Extensions

### Python Tools
- Black (formatter)
- Flake8 (linter)
- Vulture (dead code detection)
- pytest (testing)
- ipython (interactive shell)

### VS Code Extensions
- Python (ms-python.python)
- Pylance (ms-python.vscode-pylance)
- Black Formatter (ms-python.black-formatter)
- Flake8 (ms-python.flake8)
- Debugpy (ms-python.debugpy)
- Git History (donjayamanne.githistory)
- GitLens (eamodio.gitlens)
- GitHub Pull Requests (github.vscode-pull-request-github)
- **Claude Code (anthropics.claude-code)**

## Configuration Files

### devcontainer.json
Main configuration file defining:
- Docker Compose integration
- VS Code extensions and settings
- Port forwarding
- Environment variables
- Mount points
- Security options

### Dockerfile
Defines the container image:
- Base: Python 3.11 slim
- PostgreSQL development libraries
- Non-root user setup
- Python development tools

### docker-compose.yml
Container orchestration:
- Volume mounting (project directory only)
- Network configuration (host mode for PostgreSQL)
- Environment variables
- Resource limits
- Security constraints

## Workflow

### Daily Use
1. Open VS Code
2. Open project folder - container starts automatically
3. All terminal commands run inside container
4. All file operations restricted to project directory
5. Database queries connect to host PostgreSQL
6. Git operations use your SSH keys

### Testing Database Connection
```bash
# From container terminal
python -c "import psycopg2; conn = psycopg2.connect(host='localhost', port=5432, dbname='local_Merlin_3', user='postgres', password='goldmember'); print('Connected!'); conn.close()"
```

### Running the Application
```bash
# Install dependencies (first time)
pip install -r requirements.txt

# Run Flask app
python app_modular.py
```

### Git Operations
```bash
# All standard git commands work
git status
git add .
git commit -m "message"
git push origin main
```

## Troubleshooting

### Container Won't Start
- Ensure Docker Desktop is running
- Check Docker has access to the project folder
- Verify disk space available

### Database Connection Fails
- Verify PostgreSQL is running: `pg_isready`
- Check database exists: `psql -l | grep local_Merlin_3`
- Confirm port 5432 is not blocked by firewall
- For Mac: Ensure `host.docker.internal` resolves

### GitHub Authentication Fails
- Verify SSH keys exist at `~/.ssh/`
- Test SSH: `ssh -T git@github.com`
- Check permissions on SSH keys (should be 600)

### Claude Code Not Working
- Verify extension installed in container
- Check workspace path in settings
- Reload window: `Cmd+Shift+P` → "Developer: Reload Window"

### Permission Errors
- Container runs as UID 1000 - ensure project files are readable
- If needed, adjust ownership: `sudo chown -R 1000:1000 /path/to/project`

## Rebuilding Container

If you modify Dockerfile or add dependencies:

1. `Cmd+Shift+P` → "Dev Containers: Rebuild Container"
2. Or from terminal: `docker-compose -f .devcontainer/docker-compose.yml build --no-cache`

## Environment Variables

Set in `.devcontainer/devcontainer.json`:

```json
"containerEnv": {
  "PYTHONUNBUFFERED": "1",
  "FLASK_ENV": "development",
  "DATABASE_HOST": "host.docker.internal",
  "DATABASE_PORT": "5432",
  "DATABASE_NAME": "local_Merlin_3",
  "DATABASE_USER": "postgres",
  "DATABASE_PASSWORD": "goldmember",
  "TZ": "America/Denver"
}
```

**Timezone Configuration:**
- `TZ="America/Denver"` sets the container timezone to Mountain Time (MDT/MST)
- This affects all date/time displays including the `/usage` command in Claude Code
- Claude Code will now show reset times in your local timezone instead of UTC

To add secrets (API keys, etc.), create `.env` file in project root and add to `.gitignore`.

## Benefits

✅ **Isolated Environment**: No conflicts with system Python
✅ **Consistent Setup**: Same environment across machines
✅ **Security**: Restricted filesystem access
✅ **Database Access**: Direct connection to local PostgreSQL
✅ **GitHub Ready**: SSH configured automatically
✅ **Claude Code Enabled**: AI assistance within secure bounds
✅ **Reproducible**: Identical setup via version-controlled config

## Notes

- Container uses host networking for PostgreSQL access
- SSH keys are mounted read-only (cannot be modified)
- Project directory is the ONLY writable location
- All changes persist on host filesystem
- Container can be deleted/rebuilt without data loss
