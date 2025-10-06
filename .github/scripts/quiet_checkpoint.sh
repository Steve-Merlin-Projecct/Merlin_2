#!/bin/bash
# Simplified checkpoint script with minimal output

CHECKPOINT_NAME="${1:-checkpoint-$(date +%Y%m%d-%H%M%S)}"
CURRENT_BRANCH=$(git branch --show-current)

echo "Creating checkpoint '$CHECKPOINT_NAME'..."

# Quick schema check (suppress most output)
if ! python database_tools/schema_automation.py --check >/dev/null 2>&1; then
    echo "📊 Updating schema..."
    python database_tools/update_schema.py >/dev/null 2>&1
    echo "✅ Schema updated"
fi

# Commit changes if any
if ! git diff-index --quiet HEAD -- 2>/dev/null; then
    git add . >/dev/null 2>&1
    git commit -m "Checkpoint: $CHECKPOINT_NAME - Auto-save" >/dev/null 2>&1
fi

# Create tag
git tag -a "$CHECKPOINT_NAME" -m "Checkpoint: $CHECKPOINT_NAME" >/dev/null 2>&1

echo "✅ Checkpoint '$CHECKPOINT_NAME' created"
echo "Rollback: git reset --hard $CHECKPOINT_NAME"