#!/bin/bash

###############################################################################
# Docker DevContainer Project Creator
#
# Creates a new development project with:
# - Docker devcontainer configuration
# - VS Code workspace setup
# - Automatic port allocation
# - Claude Code CLI auto-launch
# - Complete isolation from other projects
#
# Usage: ./create-dev-project.sh <project-name> <language> <project-path>
# Example: ./create-dev-project.sh my-js-app javascript ~/projects/my-js-app
###############################################################################

set -e  # Exit on error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
GITHUB_DIR="$(dirname "$SCRIPT_DIR")"
PORT_REGISTRY="$GITHUB_DIR/port-registry.json"
TEMPLATES_DIR="$GITHUB_DIR/templates/devcontainer"

# Function to print colored output
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Function to validate inputs
validate_inputs() {
    if [ -z "$PROJECT_NAME" ]; then
        print_error "Project name is required"
        echo "Usage: $0 <project-name> <language> <project-path>"
        exit 1
    fi

    if [ -z "$LANGUAGE" ]; then
        print_error "Language is required"
        echo "Supported languages: javascript, python, typescript"
        exit 1
    fi

    if [ -z "$PROJECT_PATH" ]; then
        print_error "Project path is required"
        echo "Usage: $0 <project-name> <language> <project-path>"
        exit 1
    fi

    # Validate language
    case "$LANGUAGE" in
        javascript|python|typescript)
            print_success "Language: $LANGUAGE"
            ;;
        *)
            print_error "Unsupported language: $LANGUAGE"
            echo "Supported languages: javascript, python, typescript"
            exit 1
            ;;
    esac
}

# Function to get next available port
get_next_port() {
    if [ ! -f "$PORT_REGISTRY" ]; then
        print_error "Port registry not found: $PORT_REGISTRY"
        exit 1
    fi

    # Use python to parse JSON (more reliable than jq)
    NEXT_PORT=$(python3 -c "
import json
import sys

try:
    with open('$PORT_REGISTRY', 'r') as f:
        data = json.load(f)
    print(data.get('next_available_port', 5100))
except Exception as e:
    print('5100', file=sys.stderr)
    sys.exit(1)
")

    echo "$NEXT_PORT"
}

# Function to update port registry
update_port_registry() {
    local project_name="$1"
    local project_path="$2"
    local app_port="$3"
    local language="$4"

    python3 -c "
import json
import sys
from datetime import datetime

try:
    with open('$PORT_REGISTRY', 'r') as f:
        data = json.load(f)

    # Add new project
    new_project = {
        'name': '$project_name',
        'path': '$project_path',
        'ports': {
            'app': int($app_port)
        },
        'language': '$language',
        'container_name': '${project_name}_app',
        'created': datetime.now().strftime('%Y-%m-%d')
    }

    data['projects'].append(new_project)
    data['next_available_port'] = int($app_port) + data.get('port_increment', 100)

    with open('$PORT_REGISTRY', 'w') as f:
        json.dump(data, f, indent=2)

    print('Port registry updated successfully')
except Exception as e:
    print(f'Error updating port registry: {e}', file=sys.stderr)
    sys.exit(1)
"
}

# Function to check port availability
check_port_available() {
    local port="$1"

    # Check if port is in use (works on macOS and Linux)
    if command -v lsof &> /dev/null; then
        if lsof -i ":$port" -sTCP:LISTEN -t >/dev/null 2>&1; then
            return 1  # Port in use
        fi
    elif command -v netstat &> /dev/null; then
        if netstat -tuln 2>/dev/null | grep -q ":$port "; then
            return 1  # Port in use
        fi
    fi

    return 0  # Port available
}

# Function to create project directory structure
create_project_structure() {
    local project_path="$1"

    print_info "Creating project structure at: $project_path"

    # Create main project directory
    mkdir -p "$project_path"

    # Create .devcontainer directory
    mkdir -p "$project_path/.devcontainer"

    # Create .vscode directory
    mkdir -p "$project_path/.vscode"

    print_success "Project structure created"
}

# Function to generate devcontainer.json from template
generate_devcontainer() {
    local project_name="$1"
    local language="$2"
    local project_path="$3"
    local app_port="$4"
    local container_port="$5"

    local template_file="$TEMPLATES_DIR/${language}-devcontainer.json"
    local output_file="$project_path/.devcontainer/devcontainer.json"

    if [ ! -f "$template_file" ]; then
        print_error "Template not found: $template_file"
        exit 1
    fi

    print_info "Generating devcontainer.json from template"

    # Replace placeholders in template
    sed -e "s|{{PROJECT_NAME}}|$project_name|g" \
        -e "s|{{APP_PORT}}|$app_port|g" \
        -e "s|{{CONTAINER_PORT}}|$container_port|g" \
        "$template_file" > "$output_file"

    print_success "devcontainer.json generated"
}

# Function to create VS Code workspace file
create_vscode_workspace() {
    local project_name="$1"
    local project_path="$2"

    local workspace_file="$project_path/${project_name}.code-workspace"

    print_info "Creating VS Code workspace file"

    cat > "$workspace_file" <<EOF
{
  "folders": [
    {
      "name": "$project_name",
      "path": "."
    }
  ],
  "settings": {
    "claude-code.workspacePath": "\${workspaceFolder}"
  },
  "extensions": {
    "recommendations": [
      "anthropics.claude-code",
      "ms-vscode-remote.remote-containers"
    ]
  }
}
EOF

    print_success "VS Code workspace file created"
}

# Function to create README
create_readme() {
    local project_name="$1"
    local language="$2"
    local project_path="$3"
    local app_port="$4"

    print_info "Creating README.md"

    cat > "$project_path/README.md" <<EOF
# $project_name

A $language project with Docker DevContainer setup.

## Getting Started

### Prerequisites
- Docker Desktop
- VS Code with Dev Containers extension
- Git

### Quick Start

1. Open in VS Code:
   \`\`\`bash
   code $project_name.code-workspace
   \`\`\`

2. When prompted, click **"Reopen in Container"**

3. Wait for container to build and dependencies to install

4. Claude Code CLI will start automatically

5. Start developing!

### Development

- **App Port:** $app_port
- **Language:** $language
- **Container:** Isolated Docker environment

### Scripts

EOF

    # Add language-specific scripts
    case "$language" in
        javascript|typescript)
            cat >> "$project_path/README.md" <<EOF
- \`npm run dev\` - Start development server
- \`npm test\` - Run tests
- \`npm run lint\` - Lint code
EOF
            ;;
        python)
            cat >> "$project_path/README.md" <<EOF
- \`python app.py\` - Start application
- \`pytest\` - Run tests
- \`black .\` - Format code
EOF
            ;;
    esac

    cat >> "$project_path/README.md" <<EOF

### Claude Code

Claude Code CLI is automatically launched when the container starts. You can also run:
\`\`\`bash
claude
\`\`\`

## Project Info

- Created: $(date +"%Y-%m-%d")
- Port: $app_port
- Language: $language
EOF

    print_success "README.md created"
}

# Function to create language-specific files
create_language_files() {
    local language="$1"
    local project_path="$2"

    print_info "Creating $language project files"

    case "$language" in
        javascript)
            # Create package.json
            cat > "$project_path/package.json" <<EOF
{
  "name": "$(basename "$project_path")",
  "version": "1.0.0",
  "description": "A JavaScript project",
  "main": "index.js",
  "scripts": {
    "dev": "nodemon index.js",
    "start": "node index.js",
    "test": "echo \"Error: no test specified\" && exit 1",
    "lint": "eslint ."
  },
  "keywords": [],
  "author": "",
  "license": "ISC",
  "devDependencies": {
    "nodemon": "^3.0.1",
    "eslint": "^8.50.0"
  }
}
EOF
            # Create index.js
            cat > "$project_path/index.js" <<EOF
console.log('Hello from JavaScript!');

// Your code here
EOF
            # Create .gitignore
            cat > "$project_path/.gitignore" <<EOF
node_modules/
.env
.DS_Store
*.log
dist/
build/
EOF
            ;;

        typescript)
            # Create package.json
            cat > "$project_path/package.json" <<EOF
{
  "name": "$(basename "$project_path")",
  "version": "1.0.0",
  "description": "A TypeScript project",
  "main": "dist/index.js",
  "scripts": {
    "dev": "ts-node src/index.ts",
    "build": "tsc",
    "start": "node dist/index.js",
    "test": "echo \"Error: no test specified\" && exit 1",
    "lint": "eslint src"
  },
  "keywords": [],
  "author": "",
  "license": "ISC",
  "devDependencies": {
    "typescript": "^5.2.2",
    "ts-node": "^10.9.1",
    "@types/node": "^20.8.0",
    "eslint": "^8.50.0",
    "@typescript-eslint/parser": "^6.7.4",
    "@typescript-eslint/eslint-plugin": "^6.7.4"
  }
}
EOF
            # Create tsconfig.json
            cat > "$project_path/tsconfig.json" <<EOF
{
  "compilerOptions": {
    "target": "ES2020",
    "module": "commonjs",
    "outDir": "./dist",
    "rootDir": "./src",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules", "dist"]
}
EOF
            # Create src directory and index.ts
            mkdir -p "$project_path/src"
            cat > "$project_path/src/index.ts" <<EOF
console.log('Hello from TypeScript!');

// Your code here
EOF
            # Create .gitignore
            cat > "$project_path/.gitignore" <<EOF
node_modules/
dist/
.env
.DS_Store
*.log
EOF
            ;;

        python)
            # Create requirements.txt
            cat > "$project_path/requirements.txt" <<EOF
flask==3.0.0
pytest==7.4.3
black==23.11.0
flake8==6.1.0
EOF
            # Create app.py
            cat > "$project_path/app.py" <<EOF
#!/usr/bin/env python3
"""
Main application file
"""

def main():
    print("Hello from Python!")
    # Your code here

if __name__ == "__main__":
    main()
EOF
            # Create .gitignore
            cat > "$project_path/.gitignore" <<EOF
__pycache__/
*.py[cod]
*$py.class
.env
.venv
venv/
*.log
.pytest_cache/
.coverage
htmlcov/
dist/
build/
*.egg-info/
EOF
            ;;
    esac

    print_success "$language project files created"
}

# Function to initialize git repository
init_git_repo() {
    local project_path="$1"

    print_info "Initializing git repository"

    cd "$project_path"
    git init
    git add .
    git commit -m "Initial commit: Project setup with Docker DevContainer" || true

    print_success "Git repository initialized"
}

# Function to open in VS Code
open_in_vscode() {
    local project_path="$1"
    local workspace_file="$2"

    print_info "Opening project in VS Code"

    if command -v code &> /dev/null; then
        code "$workspace_file"
        print_success "Opened in VS Code"
        print_info "Click 'Reopen in Container' when prompted"
    else
        print_warning "VS Code 'code' command not found"
        print_info "Please open manually: code $workspace_file"
    fi
}

###############################################################################
# Main Script
###############################################################################

# Parse arguments
PROJECT_NAME="$1"
LANGUAGE="$2"
PROJECT_PATH="$3"

# Print header
echo ""
echo "╔════════════════════════════════════════════════════════╗"
echo "║     Docker DevContainer Project Creator               ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""

# Validate inputs
print_info "Validating inputs..."
validate_inputs

# Get next available port
print_info "Allocating ports..."
APP_PORT=$(get_next_port)
CONTAINER_PORT="3000"  # Internal container port (mapped to APP_PORT)

# Check if port is available
if ! check_port_available "$APP_PORT"; then
    print_warning "Port $APP_PORT is in use, trying next port..."
    APP_PORT=$((APP_PORT + 100))
fi

print_success "Allocated port: $APP_PORT"

# Create project structure
create_project_structure "$PROJECT_PATH"

# Generate devcontainer configuration
generate_devcontainer "$PROJECT_NAME" "$LANGUAGE" "$PROJECT_PATH" "$APP_PORT" "$CONTAINER_PORT"

# Create VS Code workspace
create_vscode_workspace "$PROJECT_NAME" "$PROJECT_PATH"

# Create README
create_readme "$PROJECT_NAME" "$LANGUAGE" "$PROJECT_PATH" "$APP_PORT"

# Create language-specific files
create_language_files "$LANGUAGE" "$PROJECT_PATH"

# Initialize git repository
init_git_repo "$PROJECT_PATH"

# Update port registry
print_info "Updating port registry..."
update_port_registry "$PROJECT_NAME" "$PROJECT_PATH" "$APP_PORT" "$LANGUAGE"
print_success "Port registry updated"

# Print summary
echo ""
echo "╔════════════════════════════════════════════════════════╗"
echo "║                    Setup Complete!                     ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""
print_success "Project: $PROJECT_NAME"
print_success "Language: $LANGUAGE"
print_success "Path: $PROJECT_PATH"
print_success "Port: $APP_PORT"
echo ""
print_info "Next steps:"
echo "  1. Open in VS Code: code $PROJECT_PATH/${PROJECT_NAME}.code-workspace"
echo "  2. Click 'Reopen in Container' when prompted"
echo "  3. Wait for container to build"
echo "  4. Claude Code will launch automatically"
echo "  5. Start coding!"
echo ""

# Open in VS Code
WORKSPACE_FILE="$PROJECT_PATH/${PROJECT_NAME}.code-workspace"
open_in_vscode "$PROJECT_PATH" "$WORKSPACE_FILE"

print_success "All done! 🚀"
echo ""
