#!/bin/bash

# Worktree Scope Detection System
# Automatically detects and manages file boundaries for worktrees

set -e

# ==============================================================================
# Configuration
# ==============================================================================

WORKSPACE_ROOT="${WORKSPACE_ROOT:-/workspace}"

# Scope detection patterns
# Maps keywords in feature descriptions to file patterns
declare -A SCOPE_PATTERNS=(
    # Email/Communication
    ["email"]="modules/email_integration/**"
    ["gmail"]="modules/email_integration/gmail*.py"
    ["oauth"]="modules/email_integration/*oauth*.py"
    ["smtp"]="modules/email_integration/smtp*.py"

    # Document Generation
    ["document"]="modules/document_generation/**"
    ["docx"]="modules/document_generation/**"
    ["template"]="modules/document_generation/templates/**"
    ["resume"]="modules/document_generation/*resume*.py"
    ["cover"]="modules/document_generation/*cover*.py"

    # Database
    ["database"]="modules/database/**"
    ["schema"]="modules/database/schema*.py"
    ["migration"]="modules/database/migrations/**"
    ["model"]="modules/database/models*.py"

    # API/Web
    ["api"]="modules/api/**"
    ["endpoint"]="modules/api/endpoints/**"
    ["route"]="modules/api/routes/**"
    ["webhook"]="modules/webhooks/**"

    # Frontend/Dashboard
    ["dashboard"]="frontend_templates/**"
    ["frontend"]="frontend_templates/**"
    ["ui"]="frontend_templates/**"
    ["template"]="frontend_templates/**"

    # AI/ML
    ["ai"]="modules/ai_job_description_analysis/**"
    ["gemini"]="modules/ai_job_description_analysis/**"
    ["llm"]="modules/ai_job_description_analysis/**"

    # Scraping
    ["scraping"]="modules/scraping/**"
    ["scrape"]="modules/scraping/**"
    ["spider"]="modules/scraping/**"

    # Storage
    ["storage"]="modules/storage/**"
    ["s3"]="modules/storage/cloud/**"
    ["gcs"]="modules/storage/cloud/**"

    # Testing
    ["test"]="tests/**"
    ["pytest"]="tests/**"

    # Documentation
    ["doc"]="docs/**"
    ["documentation"]="docs/**"
    ["readme"]="*.md"
)

# ==============================================================================
# Scope Detection Functions
# ==============================================================================

# Detect scope from feature description
#
# Args:
#   $1 - Feature description (e.g., "Email OAuth refresh tokens")
#   $2 - Worktree name
# Returns:
#   JSON scope manifest on stdout
detect_scope_from_description() {
    local description="$1"
    local worktree_name="$2"

    # Convert to lowercase for matching
    local desc_lower=$(echo "$description" | tr '[:upper:]' '[:lower:]')

    # Collect matched patterns
    local patterns=()

    # Check each keyword
    for keyword in "${!SCOPE_PATTERNS[@]}"; do
        if echo "$desc_lower" | grep -q "$keyword"; then
            patterns+=("${SCOPE_PATTERNS[$keyword]}")
        fi
    done

    # If no patterns matched, try to infer from worktree name
    if [ ${#patterns[@]} -eq 0 ]; then
        patterns=$(infer_from_worktree_name "$worktree_name")
    fi

    # Generate JSON
    generate_scope_json "$worktree_name" "$description" "${patterns[@]}"
}

# Infer scope from worktree directory name
#
# Args:
#   $1 - Worktree name (e.g., "email-integration")
# Returns:
#   Array of patterns
infer_from_worktree_name() {
    local worktree_name="$1"
    local patterns=()

    # Extract first meaningful word from name
    local primary_word=$(echo "$worktree_name" | sed 's/[-_]/ /g' | awk '{print $1}' | tr '[:upper:]' '[:lower:]')

    # Check if primary word matches a known pattern
    if [ -n "${SCOPE_PATTERNS[$primary_word]}" ]; then
        patterns+=("${SCOPE_PATTERNS[$primary_word]}")
    else
        # Default: create module-specific scope
        local module_name=$(echo "$worktree_name" | sed 's/-/_/g')
        patterns+=("modules/${module_name}/**")
        patterns+=("tests/test_${module_name}*.py")
    fi

    echo "${patterns[@]}"
}

# Generate scope JSON manifest
#
# Args:
#   $1 - Worktree name
#   $2 - Description
#   $@ - Patterns (remaining args)
generate_scope_json() {
    local worktree_name="$1"
    local description="$2"
    shift 2
    local patterns=("$@")

    # Start JSON
    cat <<EOF
{
  "worktree": "$worktree_name",
  "description": "$description",
  "scope": {
    "include": [
EOF

    # Add patterns
    local first=true
    for pattern in "${patterns[@]}"; do
        if [ "$first" = true ]; then
            first=false
        else
            echo ","
        fi
        echo -n "      \"$pattern\""
    done

    # Add related test files
    echo ","
    echo "      \"tests/test_*${worktree_name//-/_}*.py\","
    echo "      \"docs/*${worktree_name}*.md\""

    # Close JSON
    cat <<EOF

    ],
    "exclude": [
      "**/__pycache__/**",
      "**/*.pyc",
      ".git/**",
      "**/.DS_Store"
    ]
  },
  "enforcement": "soft",
  "created": "$(date -Iseconds)",
  "out_of_scope_policy": "warn"
}
EOF
}

# ==============================================================================
# Librarian Scope Calculation
# ==============================================================================

# Calculate librarian scope (inverse of all feature scopes)
#
# Args:
#   $@ - Paths to all feature scope JSON files
# Returns:
#   JSON scope manifest for librarian
calculate_librarian_scope() {
    local scope_files=("$@")

    # Collect all feature patterns
    local all_patterns=()
    for scope_file in "${scope_files[@]}"; do
        if [ -f "$scope_file" ]; then
            # Extract include patterns from JSON
            local patterns=$(python3 -c "
import json, sys
with open('$scope_file') as f:
    data = json.load(f)
    for pattern in data['scope']['include']:
        print(pattern)
" 2>/dev/null || echo "")

            while IFS= read -r pattern; do
                [ -n "$pattern" ] && all_patterns+=("$pattern")
            done <<< "$patterns"
        fi
    done

    # Generate librarian scope
    cat <<EOF
{
  "worktree": "librarian",
  "description": "Documentation, tooling, and project organization",
  "scope": {
    "include": [
      "docs/**",
      ".claude/**",
      "tools/**",
      "tasks/**",
      "*.md",
      "*.txt",
      "*.toml",
      "*.yaml",
      "*.json",
      ".github/**",
      "scripts/**"
    ],
    "exclude": [
EOF

    # Add all feature patterns as exclusions
    local first=true
    for pattern in "${all_patterns[@]}"; do
        if [ "$first" = true ]; then
            first=false
        else
            echo ","
        fi
        echo -n "      \"$pattern\""
    done

    cat <<EOF
,
      "**/__pycache__/**",
      "**/*.pyc",
      ".git/**"
    ]
  },
  "enforcement": "soft",
  "created": "$(date -Iseconds)",
  "type": "librarian",
  "out_of_scope_policy": "warn"
}
EOF
}

# ==============================================================================
# Scope Validation
# ==============================================================================

# Check if a file matches scope patterns
#
# Args:
#   $1 - File path
#   $2 - Scope JSON file path
# Returns:
#   0 if matches, 1 if not
file_matches_scope() {
    local file_path="$1"
    local scope_json="$2"

    if [ ! -f "$scope_json" ]; then
        # No scope file = full access
        return 0
    fi

    # Use Python for glob matching
    python3 <<PYTHON
import json
import fnmatch
import sys

file_path = "$file_path"
scope_file = "$scope_json"

try:
    with open(scope_file) as f:
        scope = json.load(f)

    # Check excludes first
    for pattern in scope['scope'].get('exclude', []):
        if fnmatch.fnmatch(file_path, pattern):
            sys.exit(1)  # Excluded

    # Check includes
    for pattern in scope['scope'].get('include', []):
        if fnmatch.fnmatch(file_path, pattern):
            sys.exit(0)  # Included

    # Not in scope
    sys.exit(1)
except Exception as e:
    print(f"Error: {e}", file=sys.stderr)
    sys.exit(1)
PYTHON

    return $?
}

# ==============================================================================
# Conflict Detection
# ==============================================================================

# Detect scope conflicts across worktrees
#
# Args:
#   $@ - Paths to all scope JSON files
# Returns:
#   List of conflicting files
detect_scope_conflicts() {
    local scope_files=("$@")

    python3 <<PYTHON
import json
import sys
from collections import defaultdict

scope_files = [$(printf '"%s",' "${scope_files[@]}" | sed 's/,$//')
]

# Build file -> worktrees mapping
file_owners = defaultdict(list)

for scope_file in scope_files:
    try:
        with open(scope_file) as f:
            scope = json.load(f)

        worktree = scope['worktree']

        # For each include pattern, note which worktree owns it
        for pattern in scope['scope'].get('include', []):
            file_owners[pattern].append(worktree)
    except Exception as e:
        print(f"Error reading {scope_file}: {e}", file=sys.stderr)
        continue

# Find conflicts (patterns owned by multiple worktrees)
conflicts = {pattern: owners for pattern, owners in file_owners.items() if len(owners) > 1}

if conflicts:
    print("CONFLICTS DETECTED:")
    for pattern, owners in conflicts.items():
        print(f"  Pattern: {pattern}")
        print(f"    Owned by: {', '.join(owners)}")
    sys.exit(1)
else:
    print("No conflicts detected")
    sys.exit(0)
PYTHON
}

# ==============================================================================
# Export Functions
# ==============================================================================

# Export functions for use in other scripts
export -f detect_scope_from_description
export -f infer_from_worktree_name
export -f generate_scope_json
export -f calculate_librarian_scope
export -f file_matches_scope
export -f detect_scope_conflicts
