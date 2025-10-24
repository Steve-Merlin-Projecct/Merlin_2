---
title: "Project Creator Readme"
type: technical_doc
component: general
status: draft
tags: []
---

# Automated Project Creator

Complete automation for creating new development projects with Docker DevContainers, VS Code integration, and Claude Code CLI auto-launch.

## Quick Start

### One Command Setup

```bash
./.github/scripts/create-dev-project.sh <project-name> <language> <project-path>
```

**Example:**
```bash
./.github/scripts/create-dev-project.sh my-js-app javascript ~/projects/my-js-app
```

That's it! The script will:
1. ✅ Create project structure
2. ✅ Generate devcontainer configuration
3. ✅ Allocate unique port (automatic)
4. ✅ Create VS Code workspace
5. ✅ Initialize git repository
6. ✅ Open in VS Code
7. ✅ Build Docker container (when you click "Reopen in Container")
8. ✅ Auto-launch Claude Code CLI

## Supported Languages

| Language | Template | Base Image |
|----------|----------|------------|
| **JavaScript** | `javascript` | Node.js 20 |
| **TypeScript** | `typescript` | Node.js 20 + TypeScript |
| **Python** | `python` | Python 3.11 |

## Port Management

The system automatically manages ports to prevent conflicts:

### Current Port Allocation

| Project | Port | Language |
|---------|------|----------|
| Merlin | 5000 | Python |
| *Next Project* | 5100 | - |
| *Future* | 5200+ | - |

**Port Registry:** `/workspace/.github/port-registry.json`

### How It Works

1. Script checks `port-registry.json` for next available port
2. Verifies port is not in use (`lsof` or `netstat`)
3. Allocates port to new project
4. Updates registry with new project info
5. Increments next available port by 100

## What Gets Created

### Project Structure

```
your-project/
├── .devcontainer/
│   └── devcontainer.json         # Docker container configuration
├── .vscode/                       # VS Code settings (created by you)
├── .git/                          # Git repository
├── .gitignore                     # Language-specific ignores
├── README.md                      # Project documentation
├── project-name.code-workspace    # VS Code workspace file
└── [language-specific files]      # package.json, requirements.txt, etc.
```

### Language-Specific Files

#### JavaScript
- `package.json` - NPM configuration with dev scripts
- `index.js` - Main entry point
- `.gitignore` - Node.js ignores

#### TypeScript
- `package.json` - NPM with TypeScript dependencies
- `tsconfig.json` - TypeScript configuration
- `src/index.ts` - Main entry point
- `.gitignore` - Node.js + TypeScript ignores

#### Python
- `requirements.txt` - Python dependencies (Flask, pytest, black, flake8)
- `app.py` - Main application file
- `.gitignore` - Python ignores

### DevContainer Configuration

Each project gets a fully configured devcontainer with:

- **VS Code Extensions:**
  - Language-specific tools (ESLint, Pylance, etc.)
  - Git integration (GitLens, Git History)
  - Claude Code CLI

- **Port Forwarding:**
  - Automatic port mapping to avoid conflicts
  - Named ports for easy identification

- **Auto-Install:**
  - `postCreateCommand`: Installs dependencies (npm install, pip install)
  - `postStartCommand`: Launches Claude Code CLI automatically

- **Security:**
  - Non-root user (node/vscode)
  - Read-only SSH key mounting
  - Git config mounting

## Usage Examples

### Create JavaScript Project

```bash
./.github/scripts/create-dev-project.sh my-app javascript ~/projects/my-app
```

**Result:**
- Port: 5100 (or next available)
- Node.js 20 environment
- ESLint, Prettier configured
- `npm run dev` ready to use

### Create TypeScript Project

```bash
./.github/scripts/create-dev-project.sh ts-app typescript ~/projects/ts-app
```

**Result:**
- Port: 5100 (or next available)
- TypeScript compiler configured
- Type checking enabled
- `npm run dev` with ts-node

### Create Python Project

```bash
./.github/scripts/create-dev-project.sh py-app python ~/projects/py-app
```

**Result:**
- Port: 5100 (or next available)
- Python 3.11 environment
- Flask, pytest, black, flake8 included
- Virtual environment ready

## Workflow

### Step-by-Step Process

1. **Run Script:**
   ```bash
   ./.github/scripts/create-dev-project.sh my-app javascript ~/projects/my-app
   ```

2. **Script Executes:**
   - Validates inputs
   - Allocates port (e.g., 5100)
   - Creates project directory
   - Generates devcontainer.json from template
   - Creates VS Code workspace file
   - Creates README and project files
   - Initializes git repository
   - Updates port registry
   - Opens in VS Code

3. **VS Code Opens:**
   - You see prompt: "Reopen in Container"
   - Click "Reopen in Container"

4. **Container Builds:**
   - Docker pulls base image (first time)
   - Creates container
   - Installs extensions
   - Runs `postCreateCommand` (npm install / pip install)

5. **Claude Launches:**
   - `postStartCommand` runs automatically
   - Claude Code CLI starts in background
   - Terminal opens (ready to use Claude)

6. **Start Coding:**
   - All tools configured
   - Dependencies installed
   - Claude ready to help
   - No conflicts with other projects

## Claude Code Auto-Launch

Claude Code CLI is configured to launch automatically when the container starts.

### How It Works

In `devcontainer.json`:
```json
{
  "postStartCommand": "echo '🚀 Starting Claude Code CLI...' && nohup claude > /tmp/claude.log 2>&1 &"
}
```

- Runs after container is fully started
- Launches `claude` command in background
- Logs output to `/tmp/claude.log`
- Doesn't block terminal

### Manual Launch

If needed, you can also run manually:
```bash
claude
```

### Check Claude Status

```bash
# View Claude logs
cat /tmp/claude.log

# Check if Claude is running
ps aux | grep claude
```

## Port Registry Management

### View Current Ports

```bash
cat /workspace/.github/port-registry.json
```

### Example Registry

```json
{
  "projects": [
    {
      "name": "merlin",
      "path": "/workspace",
      "ports": {
        "app": 5000,
        "db": 5432
      },
      "language": "python",
      "container_name": "merlin_app",
      "created": "2025-10-11"
    },
    {
      "name": "my-js-app",
      "path": "~/projects/my-js-app",
      "ports": {
        "app": 5100
      },
      "language": "javascript",
      "container_name": "my-js-app_app",
      "created": "2025-10-11"
    }
  ],
  "next_available_port": 5200,
  "port_increment": 100
}
```

### Manual Port Allocation

If you need to manually add a project to the registry:

1. Edit `/workspace/.github/port-registry.json`
2. Add project entry to `projects` array
3. Update `next_available_port`

## Multi-Project Setup

### Running Multiple Projects Simultaneously

Each project runs in its own isolated container:

```bash
# Terminal 1: Create JavaScript app
./.github/scripts/create-dev-project.sh app1 javascript ~/projects/app1
# Port: 5100

# Terminal 2: Create Python app
./.github/scripts/create-dev-project.sh app2 python ~/projects/app2
# Port: 5200

# Terminal 3: Create TypeScript app
./.github/scripts/create-dev-project.sh app3 typescript ~/projects/app3
# Port: 5300
```

**All projects run simultaneously:**
- Separate containers
- Unique ports
- No interference
- Independent Claude instances

### Access Multiple Projects

```bash
# Open each project in separate VS Code window
code ~/projects/app1/app1.code-workspace
code ~/projects/app2/app2.code-workspace
code ~/projects/app3/app3.code-workspace
```

Each window:
- Connects to its own container
- Has its own Claude instance
- Uses its own port
- Completely isolated

## Customization

### Modify Templates

Templates are located in:
```
/workspace/.github/templates/devcontainer/
├── javascript-devcontainer.json
├── python-devcontainer.json
└── typescript-devcontainer.json
```

**Template Variables:**
- `{{PROJECT_NAME}}` - Project name
- `{{APP_PORT}}` - Host port
- `{{CONTAINER_PORT}}` - Internal container port

### Add New Language Template

1. Create template file:
   ```bash
   cp /workspace/.github/templates/devcontainer/javascript-devcontainer.json \
      /workspace/.github/templates/devcontainer/golang-devcontainer.json
   ```

2. Modify template for Go:
   - Change base image to `golang:1.21`
   - Update extensions
   - Adjust settings

3. Update script to support `golang`:
   Edit `/workspace/.github/scripts/create-dev-project.sh`
   - Add `golang` to language validation
   - Add Go-specific file creation

### Modify Script Behavior

Edit `/workspace/.github/scripts/create-dev-project.sh`:

- **Change port increment:** Modify `port_increment` in registry
- **Add more validation:** Update `validate_inputs()` function
- **Change default files:** Modify `create_language_files()` function
- **Customize git init:** Update `init_git_repo()` function

## Troubleshooting

### Port Already in Use

**Issue:** Script says port is in use

**Solution:**
```bash
# Check what's using the port
lsof -i :5100

# Kill the process if needed
kill -9 <PID>

# Or let script auto-increment
# It will try next available port (5200, 5300, etc.)
```

### VS Code Not Opening

**Issue:** `code` command not found

**Solution:**
```bash
# Install VS Code CLI
# Open VS Code → Command Palette (Cmd+Shift+P)
# Type: "Shell Command: Install 'code' command in PATH"

# Or open manually
code ~/projects/my-app/my-app.code-workspace
```

### Container Build Fails

**Issue:** Docker container won't build

**Solution:**
```bash
# Check Docker is running
docker ps

# Check disk space
df -h

# Rebuild without cache
# VS Code → Command Palette → "Dev Containers: Rebuild Container Without Cache"
```

### Claude Not Launching

**Issue:** Claude Code CLI doesn't start automatically

**Solution:**
```bash
# Check logs
cat /tmp/claude.log

# Launch manually
claude

# Check if Claude CLI is installed
which claude

# If not installed, install it
npm install -g @anthropic-ai/claude-code
```

### Dependencies Not Installing

**Issue:** npm install or pip install fails

**Solution:**

**For JavaScript/TypeScript:**
```bash
# Clear npm cache
npm cache clean --force

# Reinstall
rm -rf node_modules package-lock.json
npm install
```

**For Python:**
```bash
# Upgrade pip
pip install --upgrade pip

# Reinstall
pip install --no-cache-dir -r requirements.txt
```

### Git Init Fails

**Issue:** Git repository initialization fails

**Solution:**
```bash
# Configure git (if not done)
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"

# Reinitialize
cd ~/projects/my-app
rm -rf .git
git init
git add .
git commit -m "Initial commit"
```

## Advanced Usage

### Custom DevContainer Configuration

After creating a project, you can customize the devcontainer:

1. Edit `.devcontainer/devcontainer.json`
2. Add more extensions
3. Modify settings
4. Add features
5. Rebuild container

**Example: Add PostgreSQL feature**
```json
{
  "features": {
    "ghcr.io/devcontainers/features/git:1": {},
    "ghcr.io/devcontainers/features/postgres:1": {
      "version": "15"
    }
  }
}
```

### Using with Docker Compose

For complex setups with multiple services:

1. Create `docker-compose.yml` in `.devcontainer/`
2. Update `devcontainer.json`:
   ```json
   {
     "dockerComposeFile": "docker-compose.yml",
     "service": "app",
     "workspaceFolder": "/workspace"
   }
   ```

### Sharing Configurations

To share your setup with team:

1. Commit `.devcontainer/` directory
2. Push to GitHub
3. Team members clone and:
   ```bash
   code project-name.code-workspace
   # Click "Reopen in Container"
   ```

## Benefits

### Time Savings
- **Manual Setup:** 30-60 minutes per project
- **Automated Setup:** 30 seconds
- **Savings:** ~95% time reduction

### Consistency
- Same structure every time
- Same tools installed
- Same port allocation strategy
- No configuration drift

### Isolation
- Each project in separate container
- No version conflicts
- No port conflicts
- Easy cleanup (delete container)

### Claude Integration
- Automatically launches in every project
- Consistent AI assistance
- No manual setup needed

### Team Collaboration
- Reproducible environments
- Version-controlled configuration
- Easy onboarding for new developers

## Examples

### Example 1: Create a REST API (JavaScript)

```bash
# Create project
./.github/scripts/create-dev-project.sh my-api javascript ~/projects/my-api

# Opens in VS Code → Reopen in Container
# Then in terminal:
npm install express
# Edit index.js to create API
npm run dev

# API runs on http://localhost:5100
```

### Example 2: Create a Python Data Science Project

```bash
# Create project
./.github/scripts/create-dev-project.sh data-analysis python ~/projects/data-analysis

# Opens in VS Code → Reopen in Container
# Edit requirements.txt:
# pandas==2.0.0
# jupyter==1.0.0
# matplotlib==3.7.0

# Install
pip install -r requirements.txt

# Launch Jupyter
jupyter notebook --ip=0.0.0.0 --port=5100
```

### Example 3: Full-Stack TypeScript App

```bash
# Create backend
./.github/scripts/create-dev-project.sh api typescript ~/projects/fullstack/api
# Port: 5100

# Create frontend
./.github/scripts/create-dev-project.sh frontend typescript ~/projects/fullstack/frontend
# Port: 5200

# Both running simultaneously, isolated containers
```

## FAQ

**Q: Can I use this with existing projects?**
A: Yes, but you'll need to manually create `.devcontainer/` directory and copy configuration from a template.

**Q: What if I need a different port range?**
A: Edit `port-registry.json` and change `next_available_port` and `port_increment`.

**Q: Can I remove a project from the registry?**
A: Yes, edit `port-registry.json` and remove the project entry. Port will be reused.

**Q: Does this work on Windows?**
A: The bash script requires bash shell. On Windows, use Git Bash or WSL 2.

**Q: Can I use custom Docker images?**
A: Yes, modify the template to use `"build": {"dockerfile": "Dockerfile"}` instead of `"image"`.

**Q: How do I update Claude Code CLI?**
A: In container terminal: `npm install -g @anthropic-ai/claude-code@latest`

**Q: Can I use this without VS Code?**
A: The devcontainer is VS Code-specific, but you can use the generated Dockerfile with regular Docker.

## Contributing

To add features or fix bugs:

1. Edit script: `/workspace/.github/scripts/create-dev-project.sh`
2. Test with: `./create-dev-project.sh test-project javascript /tmp/test`
3. Update documentation
4. Commit changes

## Support

For issues or questions:
1. Check troubleshooting section above
2. Review logs in `/tmp/claude.log`
3. Verify Docker and VS Code are up to date
4. Check [VS Code Dev Containers docs](https://code.visualstudio.com/docs/devcontainers/containers)

---

**Last Updated:** 2025-10-11
**Version:** 1.0
**Maintainer:** Claude Code
