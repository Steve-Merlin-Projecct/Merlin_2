#!/bin/bash
# Pre-commit Security Check
# Prevents committing sensitive files and detects potential secrets

set -e

echo "🔒 Running security pre-commit checks..."

# Colors for output
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

FAILED=0

# Check 1: Prevent committing .env files
echo "📁 Checking for .env files..."
if git diff --cached --name-only | grep -qE "^\.env$|^\.env\.|\.env\.production|\.env\.local"; then
    echo -e "${RED}❌ ERROR: Attempting to commit .env file!${NC}"
    echo "   Found: $(git diff --cached --name-only | grep -E '\.env')"
    echo "   These files contain secrets and should NEVER be committed."
    echo "   Use .env.example instead for templates."
    FAILED=1
fi

# Check 2: Prevent committing credentials/token files
echo "🔑 Checking for credential files..."
if git diff --cached --name-only | grep -qE "credentials.*\.json|token.*\.json|.*\.pem|.*\.key$"; then
    echo -e "${RED}❌ ERROR: Attempting to commit credentials/tokens!${NC}"
    echo "   Found: $(git diff --cached --name-only | grep -E 'credentials|token|\.pem|\.key')"
    echo "   OAuth credentials should be base64-encoded in environment variables."
    FAILED=1
fi

# Check 3: Scan for potential secrets in staged content
echo "🔍 Scanning for potential secrets in code..."

# Patterns to detect
PATTERNS=(
    "AVNS_[a-zA-Z0-9_-]{20,}"                           # Digital Ocean managed database passwords
    "AIzaSy[a-zA-Z0-9_-]{33}"                          # Google API keys
    "sk_live_[a-zA-Z0-9]{24,}"                         # Stripe keys
    "password\s*=\s*['\"][^'\"]{8,}['\"]"             # Hardcoded passwords
    "api_key\s*=\s*['\"][^'\"]{20,}['\"]"             # Hardcoded API keys
    "secret_key\s*=\s*['\"][^'\"]{20,}['\"]"          # Hardcoded secret keys
    "postgresql://[^:]+:[^@]{8,}@"                     # Database URLs with passwords
)

for pattern in "${PATTERNS[@]}"; do
    if git diff --cached | grep -qE "$pattern"; then
        echo -e "${YELLOW}⚠️  WARNING: Potential secret detected!${NC}"
        echo "   Pattern: $pattern"
        echo "   Review your changes carefully:"
        git diff --cached | grep -E "$pattern" --color=always | head -5
        echo ""
        echo -e "${YELLOW}   If this is a real secret, abort commit and use environment variables.${NC}"
        FAILED=1
    fi
done

# Check 4: Verify .gitignore exists and includes sensitive patterns
echo "📋 Verifying .gitignore configuration..."
if [ ! -f .gitignore ]; then
    echo -e "${RED}❌ ERROR: .gitignore file missing!${NC}"
    FAILED=1
else
    required_patterns=(".env" "credentials*.json" "token*.json" "*.pem" "*.key")
    for pattern in "${required_patterns[@]}"; do
        if ! grep -q "^${pattern}$" .gitignore; then
            echo -e "${YELLOW}⚠️  WARNING: .gitignore missing pattern: $pattern${NC}"
        fi
    done
fi

# Check 5: Warn about large files (potential binary secrets)
echo "📦 Checking for large files..."
LARGE_FILES=$(git diff --cached --name-only | xargs -I {} sh -c 'if [ -f "{}" ]; then stat -f%z "{}" 2>/dev/null || stat -c%s "{}"; fi' | awk '$1 > 1048576 {print $0}')
if [ -n "$LARGE_FILES" ]; then
    echo -e "${YELLOW}⚠️  WARNING: Large files detected (>1MB)${NC}"
    echo "   Verify these don't contain sensitive data or credentials."
fi

# Results
echo ""
if [ $FAILED -eq 1 ]; then
    echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${RED}❌ COMMIT BLOCKED - Security issues detected${NC}"
    echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo "To fix:"
    echo "  1. Remove sensitive files: git reset HEAD <file>"
    echo "  2. Use environment variables instead"
    echo "  3. Update .gitignore if needed"
    echo "  4. Review docs/deployment/SECURITY_PRACTICES.md"
    echo ""
    exit 1
else
    echo -e "${GREEN}✅ Security checks passed!${NC}"
    echo ""
    exit 0
fi
