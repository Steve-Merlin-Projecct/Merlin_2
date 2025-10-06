#!/bin/bash
#
# Storage Setup Script for Merlin Job Application System
# Version: 1.0
# Date: October 6, 2025
#
# This script initializes the storage directory structure and validates
# the storage configuration for the application.
#

set -e  # Exit on error

echo "=================================================="
echo "Merlin Storage Setup Script"
echo "=================================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
STORAGE_DIR="${LOCAL_STORAGE_PATH:-./storage/generated_documents}"
REQUIRED_PERMISSIONS=755

echo "Configuration:"
echo "  Storage Directory: $STORAGE_DIR"
echo "  Required Permissions: $REQUIRED_PERMISSIONS"
echo ""

# Function to check if directory exists
check_directory() {
    if [ -d "$1" ]; then
        echo -e "${GREEN}✓${NC} Directory exists: $1"
        return 0
    else
        echo -e "${YELLOW}!${NC} Directory does not exist: $1"
        return 1
    fi
}

# Function to create directory
create_directory() {
    echo "  Creating directory: $1"
    if mkdir -p "$1"; then
        echo -e "${GREEN}✓${NC} Directory created successfully"
        return 0
    else
        echo -e "${RED}✗${NC} Failed to create directory"
        return 1
    fi
}

# Function to set permissions
set_permissions() {
    echo "  Setting permissions: $REQUIRED_PERMISSIONS"
    if chmod "$REQUIRED_PERMISSIONS" "$1"; then
        echo -e "${GREEN}✓${NC} Permissions set successfully"
        return 0
    else
        echo -e "${RED}✗${NC} Failed to set permissions"
        return 1
    fi
}

# Function to check if directory is writable
check_writable() {
    if [ -w "$1" ]; then
        echo -e "${GREEN}✓${NC} Directory is writable: $1"
        return 0
    else
        echo -e "${RED}✗${NC} Directory is not writable: $1"
        return 1
    fi
}

# Function to validate environment variables
check_env_vars() {
    echo "Checking environment variables..."

    if [ -z "$STORAGE_BACKEND" ]; then
        echo -e "${YELLOW}!${NC} STORAGE_BACKEND not set, will default to 'local'"
    else
        echo -e "${GREEN}✓${NC} STORAGE_BACKEND=$STORAGE_BACKEND"
    fi

    if [ -z "$LOCAL_STORAGE_PATH" ]; then
        echo -e "${YELLOW}!${NC} LOCAL_STORAGE_PATH not set, will use default: ./storage/generated_documents"
    else
        echo -e "${GREEN}✓${NC} LOCAL_STORAGE_PATH=$LOCAL_STORAGE_PATH"
    fi

    echo ""
}

# Main setup process
echo "Step 1: Validating environment configuration"
echo "--------------------------------------------"
check_env_vars

echo "Step 2: Setting up storage directory"
echo "--------------------------------------------"

if check_directory "$STORAGE_DIR"; then
    echo "  Directory already exists"
else
    if ! create_directory "$STORAGE_DIR"; then
        echo -e "${RED}ERROR:${NC} Failed to create storage directory"
        exit 1
    fi
fi

echo ""
echo "Step 3: Setting directory permissions"
echo "--------------------------------------------"
if ! set_permissions "$STORAGE_DIR"; then
    echo -e "${RED}ERROR:${NC} Failed to set directory permissions"
    exit 1
fi

echo ""
echo "Step 4: Verifying write access"
echo "--------------------------------------------"
if ! check_writable "$STORAGE_DIR"; then
    echo -e "${RED}ERROR:${NC} Storage directory is not writable"
    echo "  Try running: sudo chmod $REQUIRED_PERMISSIONS $STORAGE_DIR"
    exit 1
fi

# Test write by creating a test file
TEST_FILE="$STORAGE_DIR/.write_test"
echo "  Testing write access..."
if echo "test" > "$TEST_FILE" 2>/dev/null; then
    rm -f "$TEST_FILE"
    echo -e "${GREEN}✓${NC} Write test successful"
else
    echo -e "${RED}✗${NC} Write test failed"
    exit 1
fi

echo ""
echo "Step 5: Checking .env file"
echo "--------------------------------------------"
if [ -f ".env" ]; then
    echo -e "${GREEN}✓${NC} .env file exists"
else
    echo -e "${YELLOW}!${NC} .env file not found"
    echo "  Consider copying .env.example to .env"
    echo "  Command: cp .env.example .env"
fi

echo ""
echo "Step 6: Python module verification"
echo "--------------------------------------------"
if command -v python &> /dev/null; then
    echo "  Testing storage module import..."
    if python -c "from modules.storage import get_storage_backend; print('✓ Storage module import successful')" 2>/dev/null; then
        echo -e "${GREEN}✓${NC} Python storage module is working"
    else
        echo -e "${RED}✗${NC} Failed to import storage module"
        echo "  Make sure you're in the project root directory"
        exit 1
    fi
else
    echo -e "${YELLOW}!${NC} Python not found in PATH, skipping module test"
fi

echo ""
echo "=================================================="
echo -e "${GREEN}Storage Setup Complete!${NC}"
echo "=================================================="
echo ""
echo "Directory Structure:"
tree -L 2 "$STORAGE_DIR" 2>/dev/null || ls -la "$STORAGE_DIR"
echo ""
echo "Next Steps:"
echo "  1. Ensure .env file is configured (copy from .env.example)"
echo "  2. Set STORAGE_BACKEND=local in .env"
echo "  3. Set LOCAL_STORAGE_PATH=$STORAGE_DIR in .env (or use default)"
echo "  4. Run your application"
echo ""
echo "For more information, see: docs/storage-architecture.md"
echo ""

exit 0
