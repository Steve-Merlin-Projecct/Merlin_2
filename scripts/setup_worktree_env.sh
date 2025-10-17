#!/bin/bash
#
# Git Worktree Environment Setup Script
#
# This script handles .env file accessibility in git worktrees.
# Git worktrees create separate working directories, but the .env file
# typically resides in the main workspace.
#
# This script provides two options:
# 1. Create a symlink from worktree to parent .env (recommended)
# 2. Copy .env to worktree with warning comment
#
# Usage:
#   ./scripts/setup_worktree_env.sh [--copy]
#
# Options:
#   --copy    Copy .env instead of creating symlink (less recommended)
#
# Author: Automated Job Application System
# Version: 4.3.2

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
RESET='\033[0m'

# Parse arguments
USE_COPY=false
if [[ "$1" == "--copy" ]]; then
    USE_COPY=true
fi

# Function to print colored output
print_header() {
    echo -e "\n${BOLD}${BLUE}======================================================================${RESET}"
    echo -e "${BOLD}${BLUE}$1${RESET}"
    echo -e "${BOLD}${BLUE}======================================================================${RESET}\n"
}

print_success() {
    echo -e "${GREEN}✓${RESET} $1"
}

print_error() {
    echo -e "${RED}✗${RESET} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${RESET}  $1"
}

print_info() {
    echo -e "${BLUE}ℹ${RESET}  $1"
}

# Find project root (current directory or parent with app_modular.py)
find_project_root() {
    local current_dir="$PWD"

    # Check current directory
    if [[ -f "$current_dir/app_modular.py" ]]; then
        echo "$current_dir"
        return 0
    fi

    # Check parent directories
    while [[ "$current_dir" != "/" ]]; do
        if [[ -f "$current_dir/app_modular.py" ]]; then
            echo "$current_dir"
            return 0
        fi
        current_dir="$(dirname "$current_dir")"
    done

    return 1
}

# Main script
print_header "Git Worktree Environment Setup"

# Find project root
PROJECT_ROOT=$(find_project_root)
if [[ $? -ne 0 ]]; then
    print_error "Could not find project root (app_modular.py not found)"
    print_info "Make sure you're running this script from the project directory or a worktree"
    exit 1
fi

print_success "Found project root: $PROJECT_ROOT"

# Check if we're in a git worktree
GIT_COMMON_DIR=$(git rev-parse --git-common-dir 2>/dev/null || echo "")
GIT_DIR=$(git rev-parse --git-dir 2>/dev/null || echo "")

if [[ -z "$GIT_COMMON_DIR" ]]; then
    print_error "Not a git repository"
    exit 1
fi

IS_WORKTREE=false
if [[ "$GIT_COMMON_DIR" != "$GIT_DIR" ]]; then
    IS_WORKTREE=true
    print_info "Detected git worktree environment"
else
    print_info "Running in main workspace (not a worktree)"
fi

# Check if .env exists in current directory
LOCAL_ENV="$PROJECT_ROOT/.env"

if [[ -f "$LOCAL_ENV" ]] && [[ ! -L "$LOCAL_ENV" ]]; then
    print_success ".env file already exists in current directory"
    print_info "Path: $LOCAL_ENV"
    exit 0
fi

# If .env is a symlink, verify it's valid
if [[ -L "$LOCAL_ENV" ]]; then
    if [[ -f "$LOCAL_ENV" ]]; then
        print_success ".env symlink already exists and is valid"
        LINK_TARGET=$(readlink -f "$LOCAL_ENV")
        print_info "Points to: $LINK_TARGET"
        exit 0
    else
        print_warning ".env symlink exists but is broken"
        print_info "Removing broken symlink..."
        rm "$LOCAL_ENV"
    fi
fi

# Find parent workspace .env
PARENT_WORKSPACE=""
if $IS_WORKTREE; then
    # For worktrees, look for .env in parent directories
    CURRENT_DIR="$(dirname "$PROJECT_ROOT")"
    while [[ "$CURRENT_DIR" != "/" ]]; do
        if [[ -f "$CURRENT_DIR/.env" ]]; then
            PARENT_WORKSPACE="$CURRENT_DIR"
            break
        fi
        CURRENT_DIR="$(dirname "$CURRENT_DIR")"
    done

    if [[ -z "$PARENT_WORKSPACE" ]]; then
        print_error "Could not find .env file in parent workspace"
        print_info "Expected location: $(dirname $(dirname $PROJECT_ROOT))/.env"
        print_info ""
        print_info "Please create a .env file in the main workspace with:"
        print_info "  PGPASSWORD=your_database_password"
        print_info "  DATABASE_NAME=local_Merlin_3"
        exit 1
    fi

    PARENT_ENV="$PARENT_WORKSPACE/.env"
    print_success "Found .env in parent workspace: $PARENT_ENV"
else
    print_error ".env file not found in main workspace"
    print_info "Please create .env file with required environment variables:"
    print_info "  PGPASSWORD=your_database_password"
    print_info "  DATABASE_NAME=local_Merlin_3"
    exit 1
fi

# Create symlink or copy
print_header "Setting up .env in worktree"

if $USE_COPY; then
    print_info "Copying .env to worktree (--copy mode)..."
    cp "$PARENT_ENV" "$LOCAL_ENV"

    # Add warning comment to top of copied file
    TEMP_FILE=$(mktemp)
    echo "# WARNING: This is a COPY of the .env file from the parent workspace" > "$TEMP_FILE"
    echo "# Original location: $PARENT_ENV" >> "$TEMP_FILE"
    echo "# Changes here will NOT affect other worktrees" >> "$TEMP_FILE"
    echo "# Consider using symlink instead: ./scripts/setup_worktree_env.sh" >> "$TEMP_FILE"
    echo "" >> "$TEMP_FILE"
    cat "$LOCAL_ENV" >> "$TEMP_FILE"
    mv "$TEMP_FILE" "$LOCAL_ENV"

    print_success ".env copied to: $LOCAL_ENV"
    print_warning "This is a COPY. Changes here won't affect other worktrees"
    print_info "To use symlink instead, run: ./scripts/setup_worktree_env.sh"
else
    print_info "Creating symlink to parent .env..."
    ln -s "$PARENT_ENV" "$LOCAL_ENV"

    print_success ".env symlink created: $LOCAL_ENV"
    print_success "Points to: $PARENT_ENV"
    print_info "All worktrees will share the same environment configuration"
fi

# Verify setup
print_header "Verification"

if [[ -f "$LOCAL_ENV" ]]; then
    print_success ".env is accessible in worktree"

    # Check for required variables
    if grep -q "PGPASSWORD" "$LOCAL_ENV"; then
        print_success "PGPASSWORD found in .env"
    else
        print_warning "PGPASSWORD not found in .env"
    fi

    if grep -q "DATABASE_NAME" "$LOCAL_ENV"; then
        print_success "DATABASE_NAME found in .env"
    else
        print_info "DATABASE_NAME not found (will use default: local_Merlin_3)"
    fi
else
    print_error "Setup verification failed - .env not accessible"
    exit 1
fi

print_header "Setup Complete"
print_success "Environment is ready for Flask dashboard"
print_info "You can now run: python scripts/start_dashboard.py"
echo ""
