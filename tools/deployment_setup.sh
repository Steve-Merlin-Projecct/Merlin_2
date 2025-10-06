#!/bin/bash
# Deployment setup wrapper script
# Ensures setup_ssh.sh is executable and runs it safely

set -e  # Exit on any error

echo "🚀 Starting deployment setup..."

# Ensure setup_ssh.sh is executable
if [ -f "setup_ssh.sh" ]; then
    echo "📝 Making setup_ssh.sh executable..."
    chmod +x setup_ssh.sh
    
    echo "🔧 Running SSH setup..."
    bash setup_ssh.sh || {
        echo "⚠️  SSH setup failed, but continuing with deployment..."
        # Don't exit here - SSH setup failure shouldn't stop deployment
    }
else
    echo "⚠️  setup_ssh.sh not found, skipping SSH setup"
fi

echo "✅ Deployment setup completed successfully"