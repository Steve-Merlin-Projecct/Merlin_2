#!/bin/bash
# Deployment wrapper for SSH setup script
# This script calls the actual SSH setup script from the tools directory

# Check if the tools directory script exists
if [ -f "tools/setup_ssh.sh" ]; then
    echo "Calling SSH setup script from tools/ directory..."
    bash tools/setup_ssh.sh
else
    echo "SSH setup script not found in tools/ directory"
    exit 1
fi